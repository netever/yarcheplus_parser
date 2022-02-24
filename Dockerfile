from python:3.10-buster

copy ./ ./

user root

run pip3 install -r requirements.txt
run sh get_components.sh
run python3 main.py
