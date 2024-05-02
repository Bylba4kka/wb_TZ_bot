import json
import os
import re

import requests

from config import BACKUPS_PATH


# Мы обращаемся к https://card.wb.ru/cards/detail?nm=154509545 айди берём из ссылки
# Там находим root это айди отзыва и оттуда уже будем распраршивать данные


def get_card_data(url):
    response = requests.get(url=f"https://card.wb.ru/cards/detail?nm={get_item_id(url=url)}")
    if response.status_code == 200:
        data = response.json()
        return data


def get_item_id(url: str):
    regex = "(?<=catalog/).+(?=/detail)"
    item_id = re.search(regex, url)[0]
    return item_id


# Получение SKU товара
def get_root_id(url):
        # response = requests.get(url=f"https://card.wb.ru/cards/detail?nm={get_item_id(url=url)}")
        # data = json.loads(response.text)
        data = get_card_data(url)
        root_value = data["data"]["products"][0]["root"]
        return root_value


# Получение название товара
def get_product_name(url):
    data = get_card_data(url)
    product_name = data["data"]["products"][0]["name"]
    return product_name


# Получение отзывов
def get_feedbacks(url):
    result = []  # Создаем пустой список для хранения информации
    file_name = f"{get_item_id(url)}_backup"

    link = f"https://feedbacks1.wb.ru/feedbacks/v1/{get_root_id(url=url)}"
    print(link)
    res = requests.get(url=link)
    data = res.json()
    
    if data["valuationSum"] == 0:
        url = f"https://feedbacks2.wb.ru/feedbacks/v1/{get_root_id(url=url)}"
        print(url)
        res = requests.get(url=url)

    if res.status_code == 200:
        # Десериализация JSON-объекта
        data = json.loads(res.text)

        feedbacks = data['feedbacks']
        for feedback in feedbacks:
            if feedback['productValuation'] < 4:
                result.append(
                    {
                        "feedback": feedback['text'],
                        "feedback_rating": feedback['productValuation'],
                        "product_rating": data['valuation'],
                    }
                )


        # # Бэкап страницы
        with open(BACKUPS_PATH + f"{file_name}.json", "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    return result  # Возвращаем список с нужной информацией


# Функция, которая проверяет наличие новых отзывов
def unique_values(url):
    file_name = f"{get_item_id(url)}_backup"

    # Получаем файл с бэкапом
    file_path = os.path.join(BACKUPS_PATH, file_name)
    # print("file_path", file_path)

    # Получение json_data_1
    try:
        print("Получение json_data_1")
        with open(file_path + ".json", 'r', encoding="utf-8") as file1:
            # print("json_data_1 открыт")
            json_data_1 = json.load(file1)
            # print("json_data_1", json_data_1)
    except:
        print("Получение json_data_1")
        # Если нет первого бэкапа то делаем его
        json_data_1 = get_feedbacks(url)

        # # Записываем информацию в файл
        # with open(file_path + ".json", 'w') as json_file:
        #     json.dump(data, json_file)

    # Получаем текущую информацию о негативных отзывах
    print("Получение json_data_2")
    json_data_2 = get_feedbacks(url)
    # Создаем пустой список для хранения значений, которые есть в первом файле, но отсутствуют во втором
    unique = []

    # Проходим по каждому элементу из первого файла
    print("Сравнение файлов")
    for item in json_data_2:
        # Получаем значения из текущего элемента
        feedback = item["feedback"]

        # Проверяем, есть ли эти значения во втором файле
        if not any(d["feedback"] == feedback for d in json_data_1):
            # Если значение отсутствует во втором файле, добавляем его в список уникальных значений.
            print("Значение отсутствует")
            unique.append(
                {
                    "feedback": feedback,
                    "feedback_rating": item["feedback_rating"],
                    "product_rating": item['product_rating'],
                }
            )

    print("Дописываем отзывы")
    if unique:
        # # Открываем и дописываем новые негативные отзывы к существующему бэкапу
        # with open(file_path + ".json", 'r', encoding="utf-8") as file:
        #     data = json.load(file)

        # Дописываем уникальные значения к существующим данным
        json_data_1.extend(unique)

        # Записываем измененные данные обратно в файл
        with open(file_path + ".json", 'w', encoding="utf-8") as file:
            json.dump(json_data_1, file, indent=4, ensure_ascii=False)  # indent=4 для красивого форматирования JSON
        print("Отзывы дописаны")
    else:
        print("Нет изменений")
    return unique


print(unique_values("https://www.wildberries.ru/catalog/154509545/detail.aspx"))