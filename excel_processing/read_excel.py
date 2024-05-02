import pandas as pd
from config import EXCEL_PATH


def read_product_ids_from_excel(file_path):
    try:
        # Чтение файла Excel
        df = pd.read_excel(file_path,
                           header=None)  # Указываем header=None, чтобы pandas не считал первую строку заголовком
        # Получение списка айди товаров
        product_ids = df.iloc[:, 0].tolist()  # Используем iloc для доступа к столбцу по его индексу
        return product_ids
    except Exception as e:
        print(f"Ошибка при чтении файла Excel: {e}")
        return []


# Пример использования
# product_ids = read_product_ids_from_excel(EXCEL_PATH)
# print(product_ids)
