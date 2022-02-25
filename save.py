import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
import smtplib
import json
from transliterate import translit
import zipfile

config = json.loads(open('config.json', 'r').read())

directory = config['output_directory']
if directory == 'out':
    directory = ''
if len(directory) > 0:
    if directory[-1] != '/':
        directory += '/'

def header_categories(category):
    with open(directory + 'categories' + '.csv', 'a', newline='') as csvfile:
        fieldnames = list(category.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                quoting=csv.QUOTE_ALL)
        writer.writeheader()

def categories(category):
    with open(directory + 'categories' + '.csv', 'a', newline='') as csvfile:
        fieldnames = list(category.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                quoting=csv.QUOTE_ALL)
        writer.writerow(category)

def header_products(product, tt_id, time):
    file_name = '_'.join([translite(config['chain_name']), 'app', config['tt_region'], tt_id, config['part_number'], 'pd_all', time])
    file_name = directory + file_name

    with open(file_name + '.csv', 'a', newline='') as csvfile:
        fieldnames = list(product.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                quoting=csv.QUOTE_ALL)
        writer.writeheader()
    return file_name

def product(product, tt_id, time):
    file_name = '_'.join([translite(config['chain_name']), 'app', config['tt_region'], tt_id, config['part_number'], 'pd_all', time])
    file_name = directory + file_name

    with open(file_name + '.csv', 'a', newline='') as csvfile:
        fieldnames = list(product.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                quoting=csv.QUOTE_ALL)
        writer.writerow(product)
    return file_name

def archive(file):
    jungle_zip = zipfile.ZipFile(file + '.zip', 'w')
    jungle_zip.write(file + '.csv', compress_type=zipfile.ZIP_DEFLATED)
    jungle_zip.close()

def send_mail(file, tt_name, time, body = 'Выгрузка успешно завершена'):
    address = tt_name
    if get_city(config['tt_region']) in address:
        address = address.replace(get_city(config['tt_region']) + ',', '')
    head = config['chain_name'] + ' | app | ' + get_city(config['tt_region']) + ' | ' + address + ' | ' + 'pd_all' + ' | ' + time
    from_addr = config['email_sender']['login']
    password = config['email_sender']['password']
    smtp = config['email_sender']['smtp']
    port = config['email_sender']['smtp_port']
    to_addr = config['email_recipient']
    subject = head
    body_text = body

    msg = MIMEText('' + body_text, 'plain', 'utf-8')
    msg = MIMEMultipart()
    msg['Subject'] = Header('' + subject, 'utf-8')
    msg['From'] = from_addr
    msg['To'] = ", ".join(to_addr)

    attach = MIMEApplication(open(file, 'rb').read())
    attach.add_header('Content-Disposition', 'attachment', filename=file)
    msg.attach(attach)

    server = smtplib.SMTP_SSL(smtp, port)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


def translite(text):
    tex = translit(text.lower(), 'ru', reversed=True)
    for ch in '''_'"''':
        tex = tex.replace(ch, '')
    tex = tex.replace(' ', '_')
    return tex

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