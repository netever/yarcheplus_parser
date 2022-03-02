# yarcheplus_parser
Парсер сайта https://yarcheplus.ru/
Парсинг товаров, категорий, их сортировка, отправка результатов 

main.py - основной файл, в котором осуществляется работа. 

get_categories.py - модуль получения списка категорий.

run.py - модуль получения списка товаров с их подробной информацией.

save.py - модуль сохранения результата в файлы, сжатия и отправки по почте.

config.json - файл конфигурации
Так как был подключен selenium в данный момент не используется max_retries, backoff_factor и headers. 
Так как tt_id может быть несколько, а также необходимо подставлять значения этому tt_id, было решено сделать это поле словарём. Не получилось найти где-либо способ достать адреса ориентируюясь только на tt_id.
Так как требуется сделать categories для отдельного tt_id, то был сделан словарь, где ключ это tt_id, а значение - массив из категорий.
email_sender - данные отправителя.
email_recipient - данные получателя.
work_email_recipient - слежубная почта, куда отправляются категории, которые были как либо отсечены фильтром.

Так как в репозитории отсутствуют и никак не используются parser_date и models_date, то и эти пункты никак не выполнялись. Если их также требуется выполнить, то прошу обсудить это.
