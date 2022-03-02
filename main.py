from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import json
import time
from datetime import datetime
import logging
import traceback
import get_categories
import run
import save

config = json.loads(open('config.json', 'r').read())


def main():

    logging.basicConfig(filename=config['logs_dir']+"yarche_parser.log", level=logging.INFO)
    log = logging.getLogger("parser")
    
    log.info('Start and configure browser')
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=opts)
    driver.set_window_size(1440, 900)
    try:
        driver.get(config['base_url'])
        WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, '/html/body/main/div/div/div[2]/div/div[1]/div[1]/a'))) #ждём когда появится элемент
        
        time.sleep(1)
        log.info('Website successfully received')
    except Exception as e:
        log.error('Something didnt work, attach error\n'+traceback.format_exc()+'\n\n')
        #driver.quit()

    for tt_id in list(config['tt_id'].keys()):

        try:
            butt = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[1]/div/button')
            butt.click()
            WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[1]/form/button'))) #ждём когда появится элемент
            form = driver.find_element_by_xpath('//*[@id="receivedAddress"]')
            form.send_keys(config['tt_id'][tt_id] + Keys.ENTER)
            time.sleep(8)#нет идей как оптимизировать. На медленных машинах может тупить отправка форма и нужно немного подождать
            form = driver.find_element_by_name('addressConfirmationForm')
            form.submit()
            WebDriverWait(driver, 10).until(expected_conditions.invisibility_of_element((By.XPATH, '/html/body/div[2]/div/div/div[1]/form/button'))) #ждём когда появится элемент
            log.info('Successfully specified delivery address')
            driver.save_screenshot('screen.png')
        except Exception as e:
            log.error('Something didnt work, attach error\n'+traceback.format_exc()+'\n\n')


        timenow = datetime.now()

        file = ''
        file2 = ''

        log.info('Starting download categories for a {}\n'.format(config['tt_id'][tt_id]))
        categories = (get_categories.get(driver, config['base_url'] + '/category/', config['tt_id'][tt_id]))
        try:
            if len(categories) > 0:
                save.header_categories(categories[0])
                for category in categories:
                    save.categories(category)
        except Exception as e:
            log.error('Something didnt work in save categories, attach error\n'+traceback.format_exc()+'\n\n')
        
        try:
            if len(config['categories']) == 0 and len(categories) > 0:#если в конфиге пусто, то парсим всё что есть
                for category in categories:
                    products = run.get(driver, category['url'], tt_id)
                    file = save_products(products[0], tt_id, timenow) if (len(products[0]) > 0) else '' #https://yarcheplus.ru/catalog/tsvety-455 тут нет товаров
                    file2 = save_products(products[1], tt_id, timenow) if (len(products[1]) > 0) else ''
                print(file)
                save.archive(file)
                save.archive(file2)
        except Exception as e:
            log.error('Something didnt work in save products, attach error\n'+traceback.format_exc()+'\n\n')

        file = ''
        file2 = ''

        try:
            if len(config['categories']) > 0:#если в конфиге не пусто, то бежим по категориям
                for category in config['categories']:
                    
                    if category in get_keys(categories, 'url'):
                        products = run.get(driver, category, tt_id)
                        file = save_products(products[0], tt_id, timenow) if (len(products[0]) > 0) else ''
                        file2 = save_products(products[1], tt_id, timenow) if (len(products[1]) > 0) else ''

                        if len(check_subcategory(category, categories)) > 0:#проверяем наличие подкатегорий
                            for subcategory in check_subcategory(category, categories):
                                products = run.get(driver, subcategory, tt_id)
                                file = save_products(products[0], tt_id, timenow) if (len(products[0]) > 0) else ''
                                file2 = save_products(products[1], tt_id, timenow) if (len(products[1]) > 0) else ''
                    else: log.error('No urls in categories!\n')
                save.archive(file)
                save.archive(file2)
        except Exception as e:
            log.error('Something didnt work in save products, attach error\n'+traceback.format_exc()+'\n\n')
        
        try:
            save.send_mail(file + '.zip', config['tt_id'][tt_id], timenow.strftime("%Y-%m-%d %H:%M:%S"))
            save.send_mail(file2 + '.zip', config['tt_id'][tt_id], timenow.strftime("%Y-%m-%d %H:%M:%S"), recipient='work_email_recipient')
        except Exception as e:
            log.error('Something didnt work in send email, attach error\n'+traceback.format_exc()+'\n\n')
    log.info('Parser completed successfully!')
    driver.quit()


def save_products(products, tt_id, time):
    if 'notsend' in products[0]:
        file = save.header_products(products[0], tt_id, time.strftime("%Y-%m-%d_%H-%M-%S"), suspect=True)
    else: file = save.header_products(products[0], tt_id, time.strftime("%Y-%m-%d_%H-%M-%S"))

    for product in products:
        if 'notsend' in product:
            del product['notsend']
        save.product(product, tt_id, time.strftime("%Y-%m-%d_%H-%M-%S"), file=file)
    return file

def get_keys(list, par):
    result = []
    for dict in list:
        result.append(dict[par])
    return result

def check_subcategory(category, categories): #Проверяем наличие подкатегорий, если есть, то извлекаем
    cat_id = -1
    subcategories = []
    for cat in categories:
        if category == cat['url']:
            cat_id = cat['id']
    if cat_id != -1:
        for cat in categories:
            if cat['parent_id'] == cat_id:
                subcateg = check_subcategory(cat['url'], categories)
                if len(subcateg) == 0:
                    subcategories.append(cat['url'])
                elif len(subcateg) > 0:
                    for subcat in subcateg:
                        subcategories.append(subcat)
    return subcategories


if __name__ == '__main__':
    main()