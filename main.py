import json
from datetime import datetime
import get_categories
import run
import save

config = json.loads(open('config.json', 'r').read())

def main():
    
    for tt_id in list(config['tt_id'].keys()):

        time = datetime.now()

        file = ''
        file2 = ''

        categories = (get_categories.get(config['base_url'] + '/category/'))
        if len(categories) > 0:
            save.header_categories(categories[0])
            for category in categories:
                save.categories(category)
        
        if len(config['categories'][tt_id]) == 0 and len(categories) > 0:
            for category in categories:
                products = run.get(category['url'], tt_id)
                if (len(products[0]) > 0): #https://yarcheplus.ru/catalog/tsvety-455 тут нет товаров
                    file = save_products(products[0], tt_id, time)
                    file2 = save_products(products[1], tt_id, time)
            save.archive(file)
            save.archive(file2)

        file = ''
        file2 = ''

        if len(config['categories'][tt_id]) > 0:
            for category in config['categories'][tt_id]:
                
                if category in get_keys(categories, 'url'):
                    products = run.get(category, tt_id)
                    if (len(products[0]) > 0):
                        file = save_products(products[0], tt_id, time)
                    if (len(products[1]) > 0):
                        file2 = save_products(products[1], tt_id, time)

                    if len(check_subcategory(category, categories)) > 0:
                        for subcategory in check_subcategory(category, categories):
                            products = run.get(subcategory, tt_id)
                            if (len(products[0]) > 0):
                                file = save_products(products[0], tt_id, time)
                            if (len(products[1]) > 0):
                                file2 = save_products(products[1], tt_id, time)
                else: print('Ошибка!')
            save.archive(file)
            save.archive(file2)
    
        save.send_mail(file + '.zip', config['tt_id'][tt_id], time.strftime("%Y-%m-%d %H:%M:%S"))
        save.send_mail(file2 + '.zip', config['tt_id'][tt_id], time.strftime("%Y-%m-%d %H:%M:%S"), recipient='work_email_recipient')


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

def check_subcategory(category, categories):
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