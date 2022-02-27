import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
import random



config = json.loads(open('config.json', 'r').read())

def pers(url):
    retries = Retry(total=config['max_retries'], backoff_factor=config['backoff_factor'], status_forcelist=[ 500, 502, 503, 504 ])
    req = requests.Session()
    req.mount('https://', HTTPAdapter(max_retries=retries))
    site = req.get(url, headers=json.loads(config['headers'].replace("'",'"')))
    if site.status_code == 200:

        return site.text

    return site.status_code


def get(url, tt_id):
    rand = 0
    if config['delay_range_s'] > 0:
        rand = random.randrange(1, config['delay_range_s'], 1)
    time.sleep(rand)

    retries = Retry(total=config['max_retries'], backoff_factor=config['backoff_factor'], status_forcelist=[ 500, 502, 503, 504 ])
    req = requests.Session()
    req.mount('https://', HTTPAdapter(max_retries=retries))
    site = req.get(url, headers=json.loads(config['headers'].replace("'",'"')))
    if site.status_code == 200:

        return __get_json_info(site.text, tt_id)

    return site.status_code


def __get_json_info(site, tt_id):
    dictData = json.loads(__get_json(site))
    try:
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
        if product['quant']['type'] == 'piece':
            result['sku_package'] = 2
        if product['quant']['type'] == 'weight':
            result['sku_package'] = 0
        result['sku_packed'] = ""
        result['sku_weight_min'] = ""
        result['sku_volume_min'] = ""
        result['sku_quantity_min'] = ""
        result['sku_fat_min'] = ""
        result['sku_alcohol_min'] = ""
        result['sku_link'] = config['base_url'] + "/product/" + product['code'] + '-' + str(product['id'])
        result['api_link'] = "" + get_api_url(site)
        result['sku_parameters_json'] = ""
        result['sku_images'] = ""
        result['server_ip'] = '127.0.0.1'
        result['dev_info'] = ''
        result['promodata'] = 'promodata'

        if config['sku_images_enable'] == True:
            result['sku_images'] = result['api_link'] + '/thumbnail/740x740/{}/{}/{}.webp'.format(str(product['image']['id'])[0:2], str(product['image']['id'])[2:], product['image']['id'])
        if config['sku_parameters_enable'] == True:
            result['sku_brand'] = ""
            result['sku_country'] = ""
            result['sku_manufacturer'] = ""
            if product['quant']['type'] == 'piece':
                result['sku_package'] = 2
            if product['quant']['type'] == 'weight':
                result['sku_package'] = 0
            result['sku_packed'] = ""
            result['sku_weight_min'] = ""
            result['sku_volume_min'] = ""
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
    del_bad_symbols(products)
    del_bad_symbols(notsend)
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

def __get_product_description(site):
    rand = 0
    if config['delay_range_s'] > 0:
        rand = random.randrange(1, config['delay_range_s'], 1)
    time.sleep(rand)
    
    retries = Retry(total=config['max_retries'], backoff_factor=config['backoff_factor'], status_forcelist=[ 500, 502, 503, 504 ])
    req = requests.Session()
    req.mount('https://', HTTPAdapter(max_retries=retries))
    site = req.get(site, headers=json.loads(config['headers'].replace("'",'"')))
    if site.status_code == 200:
        site = site.text
    
    soup = BeautifulSoup(site, "html.parser")
    pagejson = soup.find('div', attrs={ "class" : "product-props__sub-section"})
    #print(pagejson)
    return ""

def get_api_url(site):
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