import json
from datetime import datetime
import get_categories
import run
import save

config = json.loads(open('config.json', 'r').read())

def main():
    
    for tt_id in list(config['tt_id'].keys()):

        time = datetime.now()

        categories = (get_categories.get('https://yarcheplus.ru/category/'))
        if len(categories) > 0:
            save.header_categories(categories[0])
            for category in categories:
                save.categories(category)
        
        if len(config['categories']) == 0 and len(categories) > 0:
            for category in categories:
                products = run.get(category['url'], tt_id)
                if (len(products) > 0): #https://yarcheplus.ru/catalog/tsvety-455 тут нет товаров
                    file = save.header_products(products[0])
                    for product in products:
                        save.product(product)


        if len(config['categories']) > 0:
            for category in config['categories']:
                if category in get_keys(categories, 'url'):
                    products = run.get(category, tt_id)
                    if (len(products) > 0): #https://yarcheplus.ru/catalog/tsvety-455 тут нет товаров
                        file = save.header_products(products[0], tt_id, time.strftime("%Y-%m-%d_%H-%M-%S"))
                        for product in products:
                            save.product(product, tt_id, time.strftime("%Y-%m-%d_%H-%M-%S"))
                        save.archive(file)
                else: print('Ошибка!')
    
        save.send_mail(file + '.zip', config['tt_id'][tt_id], time.strftime("%Y-%m-%d %H:%M:%S"))    



def get_keys(list, par):
    result = []
    for dict in list:
        result.append(dict[par])
    return result



if __name__ == '__main__':
    main()