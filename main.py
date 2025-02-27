import time
import requests
import threading

from waitress import serve
from flask import Flask, request

app = Flask(__name__)


# Функция для получения данных с сайта
def get_data_from_site():
    global data

    login_data = {}
    # Получаем данные для авторизации в Mapix
    with open('credentials.txt', 'r') as file:
        for line in file:
            # Убираем лишние пробелы и проверяем каждую строку
            line = line.strip()
            # AUTH URL
            if line.startswith('auth_url='):
                auth_url = line.split('=')[1]
            elif line.startswith('api_url='):
                api_url = line.split('=')[1]
            # Логин и пароль для базовой авторизации
            elif line.startswith('username='):
                login_data['username'] = line.split('=')[1]
            elif line.startswith('password='):
                login_data['password'] = line.split('=')[1]

    # Создаем сессию
    session = requests.Session()

    # Выполняем запрос на авторизацию
    response = session.post(auth_url, data=login_data)

    # Проверяем, успешно ли выполнена авторизация
    if response.status_code == 200 and 'логин' not in response.text.lower():

        # Теперь выполняем запрос на API
        api_response = session.get(api_url)

        # Проверяем, успешно ли выполнен запрос
        if api_response.status_code == 200:
            try:
                data = api_response.json()  # Сохраняем данные
            except ValueError:
                print('Ответ от сервера не является валидным JSON.')
        else:
            print('Ошибка при запросе к API:', api_response.status_code)
    else:
        print('Ошибка авторизации или редирект на страницу логина. Ответ от сервера:')
        print(response.text)


# Функция для периодического обновления данных каждые 5 минут
def periodic_data_update():
    while True:
        get_data_from_site()
        time.sleep(300)


# Обработчик маршрута /get_coordinates/longitude
@app.route('/get_coordinates/longitude', methods=['GET'])
def get_coordinates_longitude():
    # Получаем параметр 'number' из URL
    number = request.args.get('number')

    if number is None:
        return 'Number parameter is required', 400

    # Проходим по данным и ищем номер
    for key, value in data.items():
        for entry in value:
            if number in entry['number'].replace(' ', ''):
                # Если номер найден, возвращаем значение 'ln' как число
                return str(float(entry['ln']))

    # Если номер не найден
    return 'Number not found', 404


# Обработчик маршрута /get_coordinates/latitude
@app.route('/get_coordinates/latitude', methods=['GET'])
def get_coordinates_latitude():
    # Получаем параметр 'number' из URL
    number = request.args.get('number')

    if number is None:
        return 'Number parameter is required', 400

    # Проходим по данным и ищем номер
    for key, value in data.items():
        for entry in value:
            if number in entry['number'].replace(' ', ''):
                # Если номер найден, возвращаем значение 'la' как число
                return str(float(entry['la']))

    # Если номер не найден
    return 'Number not found', 404


# Обработчик маршрута /get_speed
@app.route('/get_speed', methods=['GET'])
def get_speed():
    # Получаем параметр 'number' из URL
    number = request.args.get('number')

    if number is None:
        return 'Number parameter is required', 400

    # Проходим по данным и ищем номер
    for key, value in data.items():
        for entry in value:
            if number in entry['number'].replace(' ', ''):
                # Если номер найден, возвращаем значение 'la' как число
                return str(float(entry['s']))

    # Если номер не найден
    return 'Number not found', 404


# Обработчик маршрута /get_ignition
@app.route('/get_ignition', methods=['GET'])
def get_ignition():
    # Получаем параметр 'number' из URL
    number = request.args.get('number')

    if number is None:
        return 'Number parameter is required', 400

    # Проходим по данным и ищем номер
    for key, value in data.items():
        for entry in value:
            if number in entry['number'].replace(' ', ''):
                # Если номер найден, возвращаем значение 'la' как число
                return str(float(entry['i']))

    # Если номер не найден
    return 'Number not found', 404


if __name__ == '__main__':
    # Переменная для хранения данных
    data = {}

    # Запуск фоновой задачи для обновления данных
    thread = threading.Thread(target=periodic_data_update)
    thread.daemon = True
    thread.start()

    # Запускаем сервер на всех интерфейсах, на порту 5000
    serve(app, host='0.0.0.0', port=5000)

# docker-compose up -d --build
