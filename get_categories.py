import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import json
import time
import random

config = json.loads(open('config.json', 'r').read())

def get(url):
    rand = 0
    if config['delay_range_s'] > 0:
        rand = random.randrange(1, config['delay_range_s'], 1)
    time.sleep(rand)
    
    retries = Retry(total=config['max_retries'], backoff_factor=config['backoff_factor'], status_forcelist=[ 500, 502, 503, 504 ])
    req = requests.Session()
    req.mount('https://', HTTPAdapter(max_retries=retries))
    site = req.get(url, headers=json.loads(config['headers'].replace("'",'"')))
    if site.status_code == 200:
        return __get_Categories(__get_json(site.text))
    return site.status_code

def __get_Categories(site, parent_url = None, parent_name = ''):
    dictData = json.loads(site)
    CatName = []
    try:
        dictData = dictData['api']['categoryList']['list']
    except:
        pass
    for category in dictData:
        result = {}
        result['id'] = category['treeId']
        result['parent_id'] = category['parentTreeId']
        result['name'] = parent_name + category['name']
        result['url'] = "-".join(['/' + category['code'], str(category['id'])])
        result['parent_url'] = parent_url
        if len(category['children']) > 0:
            result['url'] = config['base_url'] + '/category' + result['url']
            CatName = CatName + __get_Categories(json.dumps(category['children']), parent_url=result['url'], parent_name=result['name']+' | ')
        else:
            result['url'] = config['base_url'] + '/catalog' + result['url']
        CatName.append(result)
    del_bad_symbols(CatName)
    return CatName

def __get_json(site):
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