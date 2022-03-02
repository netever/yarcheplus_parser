import logging
import traceback
from bs4 import BeautifulSoup
import json
import time
import random
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

config = json.loads(open('config.json', 'r').read())
logging.basicConfig(filename=config['logs_dir']+"yarche_parser.log", level=logging.INFO)
log = logging.getLogger("parser")

def get(driver, site, tt_name):
    rand = random.randrange(1, config['delay_range_s'], 1) if config['delay_range_s'] > 0 else 0
    time.sleep(rand)

    try:
        driver.get(site)
        WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, '/html/body/main/div/div/div[2]/div/div[1]/div[1]/a'))) #ждём когда появится элемент
        page = driver.page_source
        log.info('Successfully specified delivery address and starting to get categories')
        return __get_Categories(__get_json(page))

    except Exception as e:
        log.error('Something didnt work, attach error\n'+traceback.format_exc()+'\n\n')

def __get_Categories(site, parent_url = None, parent_name = ''):
    dictData = json.loads(site)
    CatName = []
    try:
        dictData = dictData['api']['categoryList']['list']
    except:
        pass #чтобы кучу if'ок не делать решил обернуть в try-except
    for category in dictData:
        result = {}
        result['id'] = category['treeId']
        result['parent_id'] = category['parentTreeId']
        result['name'] = parent_name + category['name']
        result['url'] = "-".join(['/' + category['code'], str(category['id'])])
        result['parent_url'] = parent_url
        if len(category['children']) > 0: #если у категории есть подкатегории,
            # то рекурсивно вызываем функцию и передаём информацию об их отце, чтобы построить дерево
            result['url'] = config['base_url'] + '/category' + result['url']
            CatName = CatName + __get_Categories(json.dumps(category['children']), parent_url=result['url'], parent_name=result['name']+' | ')
        else:
            result['url'] = config['base_url'] + '/catalog' + result['url']
        CatName.append(result)
    del_bad_symbols(CatName)#малоли тут тоже могут оказаться символы, которые нужно удалить
    log.info('Categories retrieved successfully!')
    return CatName

def __get_json(site):#вытаскиваем всю инфу из статики, приделываем скобочки {} и json готов!
    soup = BeautifulSoup(site, "html.parser")
    pagejson = str(soup.find('script', charset="UTF-8"))
    pagejson = pagejson[pagejson.find('{'):pagejson.rfind('}')+1]
    return pagejson


def del_bad_symbols(categories):
    bad_symbols = [';', '«', '»', '”', '“', '\\', '"', '(', ')', '\n', '\t', '\r', '\xc2', '\xa0']
    if len(categories) > 0:
        for category in categories:
            for key in list(category.keys()):
                if type(category[key]) == type(''):
                    for bad_symbol in bad_symbols:
                        category[key] = category[key].replace(bad_symbol, '')