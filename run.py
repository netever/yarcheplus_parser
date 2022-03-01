from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
import logging
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import traceback



config = json.loads(open('config.json', 'r').read())
logging.basicConfig(filename=config['logs_dir']+"yarche_parser.log", level=logging.INFO)
log = logging.getLogger("parser")


def get(site, tt_id):
    rand = random.randrange(1, config['delay_range_s'], 1) if config['delay_range_s'] > 0 else 0
    time.sleep(rand)

    log.info('Start and configure browser')
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=opts)
    driver.set_window_size(1440, 900)
    try:
        driver.get(site)
        time.sleep(3)
        butt = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[1]/div/button')
        butt.click()
        time.sleep(1)
        form = driver.find_element_by_xpath('//*[@id="receivedAddress"]')
        form.send_keys(config['tt_id'][tt_id] + Keys.ENTER)
        time.sleep(8)
        form = driver.find_element_by_name('addressConfirmationForm')
        form.submit()
        time.sleep(8)
        page = driver.page_source
        driver.quit()
        log.info('Successfully specified delivery address and starting to get products')
        return __get_json_info(page, tt_id)

    except Exception as e:
        log.error('Something didnt work, attach error\n'+traceback.format_exc()+'\n\n')
        driver.quit()
        return None




def __get_json_info(site, tt_id):
    dictData = json.loads(__get_json(site))
    try: #чтобы кучу if'ок не делать решил обернуть в try-except
        dictData = dictData['api']['productList']['list']
    except:
        pass
    products = []
    notsend = []
    for product in dictData:
        result = {}
        result['parser_id'] = config['parser_id']
        result['chain_id'] = config['chain_id']
        result['tt_id'] = tt_id
        result['tt_region'] = get_city(config['tt_region'])
        result['tt_name'] = "{} ({})".format(config['chain_name'], config['tt_id'][tt_id])
        result['price_datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result['price'] = ""
        result['price_promo '] = ""
        if product['previousPrice'] != None and product['price'] < product['previousPrice']:
            result['price'] = product['previousPrice']
            result['price_promo '] = product['price']
        elif product['previousPrice'] == None:
            result['price'] = product['price']
        result['price_card'] = ""
        result['price_card_promo'] = ""
        result['promo_start_date'] = ""
        result['promo_end_date'] = ""
        result['promo_type'] = ""
        result['in_stock'] = ""
        result['sku_status'] = 0
        if product['isAvailable']:
            result['sku_status'] = 1
        result['sku_article'] = ""
        result['sku_name'] = product['name']
        result['sku_category'] = __get_category(product['categories'])
        result['sku_brand'] = ""
        result['sku_country'] = ""
        result['sku_manufacturer'] = ""
        result['sku_package'] = ""
        result['sku_packed'] = ""
        result['sku_weight_min'] = ""
        result['sku_volume_min'] = ""
        result['sku_quantity_min'] = ""
        result['sku_fat_min'] = ""
        result['sku_alcohol_min'] = ""
        result['sku_link'] = config['base_url'] + "/product/" + product['code'] + '-' + str(product['id'])
        result['api_link'] = "" + get_api_url(site)
        sku_parameters = __get_product_description(result['sku_link'], config['tt_id'][tt_id])
        result['sku_parameters_json'] = json.dumps(sku_parameters)
        result['sku_images'] = ""
        result['server_ip'] = '127.0.0.1'
        result['dev_info'] = ''
        result['promodata'] = 'promodata'

        if config['sku_images_enable'] == True:
            result['sku_images'] = result['api_link'] + '/thumbnail/740x740/{}/{}/{}.webp'.format(str(product['image']['id'])[0:2], str(product['image']['id'])[2:], product['image']['id'])
        if config['sku_parameters_enable'] == True:
            if 'Торговая марка' in list(sku_parameters.keys()):
                result['sku_brand'] = sku_parameters['Торговая марка']
            if 'Страна производства' in list(sku_parameters.keys()):
                result['sku_country'] = sku_parameters['Страна производства']
            if 'Производитель' in list(sku_parameters.keys()):
                result['sku_manufacturer'] = sku_parameters['Производитель']
            if product['quant']['type'] == 'piece':
                result['sku_packed'] = 2
            if product['quant']['type'] == 'weight':
                result['sku_packed'] = 0
            result['sku_package'] = ""
            if 'Вес' in list(sku_parameters.keys()):
                result['sku_weight_min'] = sku_parameters['Вес']
            if 'Объем' in list(sku_parameters.keys()):
                result['sku_volume_min'] = sku_parameters['Объем']
            result['sku_quantity_min'] = ""
            result['sku_fat_min'] = ""
            result['sku_alcohol_min'] = ""
        if config['promo_only'] == True and product['previousPrice'] != None:
            products.append(result)
        elif config['promo_only'] == False:
            products.append(result)
        else: 
            result['notsend'] = 'yes'
            notsend.append(result)
    del_bad_symbols(products)#удаление символов, которые
    del_bad_symbols(notsend)#могут сломать csv таблицы
    return [products, notsend]

def __get_category(categories):
    result = ''
    if categories != None:
        for category in categories:
            result += ' | ' + category['name']
        return result[3:]
    return result


def __get_json(site):
    soup = BeautifulSoup(site, "html.parser")
    pagejson = str(soup.find('script', charset="UTF-8"))
    pagejson = pagejson[pagejson.find('{'):pagejson.rfind('}')+1]
    return pagejson

def __get_product_description(site, tt_name):
    rand = random.randrange(1, config['delay_range_s'], 1) if config['delay_range_s'] > 0 else 0
    time.sleep(rand)
    
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=opts)
    driver.set_window_size(1440, 900)
    try:
        driver.get(site)
        time.sleep(3)
        butt = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[1]/div/button')
        butt.click()
        time.sleep(0)
        form = driver.find_element_by_xpath('//*[@id="receivedAddress"]')
        form.send_keys(tt_name)
        time.sleep(1)
        form.send_keys(Keys.ENTER)#на сайте представляются варианты исходя из того
        time.sleep(8)             # что написано в адрессе, потому жмём enter
        form = driver.find_element_by_name('addressConfirmationForm')
        form.submit()
        time.sleep(8)# если ждать слишком мало, то на медленной машине может не успеть прогрузиться
        try:         #что грозит блокировкой элементов
            form = driver.find_element_by_xpath('/html/body/main/div/div/div[5]/div/div/div[3]/div/div[1]/button[2]')
            driver.execute_script("window.scrollTo(0, {})".format(form.location['y']-90))
            time.sleep(1)
            form.click()
        except Exception as e:
            log.error('Something didnt work, attach error\n'+traceback.format_exc()+'\n\n')
        site = driver.page_source
        driver.quit()

    except Exception as e:
        log.error('Something didnt work, attach error\n'+traceback.format_exc()+'\n\n')
        driver.quit()
    soup = BeautifulSoup(site, "html.parser")
    page = soup.find('div', class_='product-props__sub-section')
    products = []
    result = {}
    for element in page.find_all('div'):
        products.append(element.text)

    for element in enumerate(products):
        #Почему-то достаётся 3 поля "Упаковка", "пленка", "Упаковкапленка"
        #Этот for отсекает третье поле
        if len(products) - element[0] > 2:
            if element[1] == products[element[0]+1] + products[element[0]+2]:
                del products[element[0]]
    
    for element in enumerate(products):
        #Массив превращаем в словарь result[res[0]] = res[1], result[res[2]] = res[3]
        if element[0] % 2 == 0:
            result[element[1]] = ''
        else: result[products[element[0]-1]] = element[1]
    return result

def get_api_url(site):#не то чтобы это полноценная апишка, но по ней можно доставать картиночки
    soup = BeautifulSoup(site, "html.parser")
    pages = soup.findAll('script', charset="UTF-8")
    for page in pages:
        if 'window.API_URL' in str(page):
            page = str(page)
            return page[page.find("'")+1:page.find("'", page.find("'")+1)]
    return None

def get_city(abbr):
    citys = {
        'ekb': 'Екатеринбург',
        'msk': 'Москва',
        'spb': 'Санкт Петеребург',
        'kzn': 'Казань',
        'rzn': 'Рязань',
        'klg': 'Калуга',
        'rnd': 'Ростов-на-Дону',
        'nsb': 'Новосибирск',
        'kst': 'Кострома',
        'yar': 'Ярославль',
        'nng': 'Нижний Новгород',
        'krd': 'Краснодар',
        'tvr': 'Тверь',
        'tms': 'Томск',
        'kng': 'Калининград'
    }

    if abbr in list(citys.keys()):
        return citys[abbr]
    return abbr


def del_bad_symbols(products):
    bad_symbols = [';', '«', '»', '”', '“', '\\', '"', '(', ')', '\n', '\t', '\r', '\xc2', '\xa0']
    if len(products) > 0:
        for product in products:
            for key in list(product.keys()):
                if type(product[key]) == type(''):
                    for bad_symbol in bad_symbols:
                        product[key] = product[key].replace(bad_symbol, '')