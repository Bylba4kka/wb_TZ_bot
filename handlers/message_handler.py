import asyncio
import schedule
from datetime import datetime

from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandStart

from config import TIME, EXCEL_PATH
from excel_processing.read_excel import read_product_ids_from_excel
from wb_parser import get_root_id, get_product_name, get_feedbacks, get_item_id, unique_values

router = Router()
# Словарь для отслеживания состояния пользователей
user_state = {}


# Функция для сбора и отправки уведомлений о негативных отзывах
async def notify_negative_reviews(message: types.Message):
    # чтение эксель файла с SKU
    product_ids = read_product_ids_from_excel(EXCEL_PATH)
    for product_id in product_ids:
        # Получение нужной информации
        url = f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"
        product_name = get_product_name(url)
        sku = get_item_id(url)
        feedback_list = unique_values(url)

        if not len(feedback_list) == 0:
            await message.answer(f'Товар "{product_name}" новых негативных отзывов {len(feedback_list)}')
            for feedback in feedback_list:
                feedback_rating = feedback["feedback_rating"]
                negative_review_text = feedback["feedback"]
                rating = feedback["product_rating"]

                await message.answer(
                    f'Отзыв на товар "{product_name}" (SKU: {sku})\n\n'
                    f'🌟 Рейтинг отзыва: {feedback_rating}\n\n'
                    'Текст отзыва: '
                    f'{negative_review_text}\n\n'
                    f'Текущий рейтинг товара: {rating}/5.0\n'
                )

                await asyncio.sleep(3)
        else:
            await message.answer(f"Новых негативных отзывов нет на товар {product_name}")


    # Добавляем вывод информации о запуске в консоль
    print("Запуск задачи в", datetime.now())


# Создание корутин задачи
# def run_daily_job(message):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     asyncio.run_coroutine_threadsafe(notify_negative_reviews(message), loop)
async def async_job_wrapper(message):
    await notify_negative_reviews(message)


def async_scheduler(message):
    loop = asyncio.get_event_loop()
    loop.create_task(async_job_wrapper(message))

# Обработчик команды /start
@router.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, отправлял ли пользователь команду /start ранее
    if user_state.get(user_id) is None:
        # Запоминаем, что пользователь отправил команду /start
        user_state[user_id] = True
        # Если не отправлял, то выполняем необходимые действия

        await message.answer(
            "Привет, я бот из ТЗ. В группу Телеграмм я буду отправлять уведомления о негативных отзывах на товары в Wildberries.\n\n"
            f"Я уже запущен и работаю, в это время {TIME} я буду присылать уведомления о наличие новых негативных отзывов"
        )
        # Запускаем задачу ежедневно в заданное время в конфиге
        schedule.every().day.at(TIME).do(async_scheduler, message=message)

        # Бесконечный цикл для проверки запуска задач по расписанию
        while True:
            schedule.run_pending()
            await asyncio.sleep(10)  # Проверка расписания каждую минуту
    else:
        await message.answer(
            f"Я уже запущен и работаю, в это время {TIME} я буду присылать уведомления о наличие новых негативных отзывов"
        )




