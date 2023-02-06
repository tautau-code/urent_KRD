import json
import logging
import os
from datetime import date

from aiogram import Bot, Dispatcher, types, executor

# Logger initialization and logging level setting
log = logging.getLogger(__name__)
log.setLevel(os.environ.get('LOGGING_LEVEL', 'INFO').upper())

# Vars
count_scooters = 0
count_parking = 0
working_zone = 'Красная'

words_to_process = [
    'тс',
    'ст',
    'scooter',
    'ts',
    'sctr',
    'самокат',
    'поправил',
    'подвёз',
    'подвез',
    'поднял',
    'переместил',
]


# Handlers
async def start(message: types.Message):
    global working_zone
    start_shift_text = f"#смена {date.today().strftime('%d.%m.%Y')}\nначал\n• Зона работы: {working_zone}\n"
    # todo: написать еще одно сообшение-напоминание о том, чтобы скопировал сообщение и отправил в чат скаутов
    # todo: сделать так чтобы оно автоматически копировалось в буфер (если так можно)
    await message.answer(start_shift_text)


async def process_scooters(message: types.Message):
    global count_scooters, count_parking
    pieces = message.text.split()
    if pieces[0].lower() in words_to_process and pieces[1].isdigit():

        count_parking += 1
        count_scooters += int(pieces[1])
        msg = f'✅🛴 {pieces[1]} ТС Обработано.\n✅🅿️  Парковка обработана.'
        # todo: добавить инлайн кновку отменить (когда будешь делать через бд, записывай с вызовом метода уникальный message_id или другой id, чтобы потом по нему удалять из бд определенное количество. Или для начала можно сделать просто: берем это же сообщение, в котором нажата инлайн кнопка отмены, парсим ее текст и делаем запрос в бд на вычитание тс, но тогда бл должна быть не из UNSIGNED TINYINT | INT32)
        await message.answer(msg)

async def instructions(message: types.Message):
    description = 'Описание:\n\tБот для счёта обработанных ТС и парковок.\n\r'
    how_to_shift = 'Как начинать и заканчивать смену:\n\tНачать смену: выбрать в меню "начать смену" или написать команду "/start".\n\tЗакончить смену: выбрать в меню "закончить смену"(команда "/end_shift")\n\r'
    # todo: (выше) тоже сделать в расширеной версии почему это СТОИТ делать в боте, например сколько времени он экономит, пусть сами попробуют посчитать и пройдут опрос тг, создать опросы, хранить их в бд для статистики, написать что мы используем безотказные технологии, если у нас что-то не работает, то скорее всего не работает ни у кого (или @разраб накосячил)
    # todo: (вышех2) написать о том, что нужно копировать сообщение, сгенерированное ботом, написать как это сделать и добавить гифку как это делает тг для своих новых функций
    how_to_write_ts = f'\tКак считать:\n\t\t+🛴🅿️ Напиши "тс <число>". Тогда тебе засчитается это количество тс и одна парковка.\n\t\t🛠Если у тебя самокат🛴 на 🛠ремонт, выбери в меню команду "сбор, ремонт". Тогда тебе засчитается только один тс, без парковки (так и надо)\n\r' #todo: добавить две инструкции: ераткую, где просто примеры с кратким описанием и расширенные, где написано какие слова допустимы и к кому обращаться для добавления новых слов, для багов и вцелом для исправления ошибок
    final_instr = description + how_to_shift + how_to_write_ts
    how_to_get_shift_stats = '' # todo: написать как смотреть статистику во время смены
    await message.answer(text=final_instr)

async def repair(message: types.Message):
    global count_scooters
    count_scooters += 1
    repair_text = f'✅🛠🛴 1 ТС Обработан.'
    await message.answer(repair_text)


async def stats():
    global count_scooters, count_parking
    return f'• Обработано парковок: {count_parking}\n• Количество ТС обработано: {count_scooters}'


async def shift_stats(message: types.Message):
    await message.answer(text=await stats())


async def end_shift(message: types.Message):
    end_shift_text = f"#смена {date.today().strftime('%d.%m.%Y')}\nзавершил\n• Зона работы: {working_zone}\n" + await stats()
    await message.answer(end_shift_text)
    global count_scooters, count_parking
    count_scooters = 0
    count_parking = 0


# Functions for Yandex.Cloud
# async def register_handlers(dp: Dispatcher):
#     """Registration all handlers before processing update."""
#
#     dp.register_message_handler(start, commands=['start'])
#     dp.register_message_handler(process_scooters)
#     dp.register_message_handler(instructions, commands=['help'])
#     dp.register_message_handler(repair, commands='repair')
#     dp.register_message_handler(shift_stats, commands=['stats'])
#     dp.register_message_handler(end_shift, commands=['end_shift'])
#
#     log.debug('Handlers are registered.')


async def process_event(event, dp: Dispatcher):
    """
    Converting an Yandex.Cloud functions event to an update and
    handling tha update.
    """

    update = json.loads(event['body'])
    log.debug('Update: ' + str(update))

    Bot.set_current(dp.bot)
    update = types.Update.to_object(update)
    await dp.process_update(update)


# async def handler(event, context):
#     """Yandex.Cloud functions handler."""
#
#     if event['httpMethod'] == 'POST':
#         # Bot and dispatcher initialization
#         bot = Bot(os.environ.get('TOKEN'))
#         dp = Dispatcher(bot)
#
#         await register_handlers(dp)
#         await process_event(event, dp)
#
#         return {'statusCode': 200, 'body': 'ok'}
#     return {'statusCode': 405}

if __name__ == '__main__':
    bot = Bot("6057374188:AAER_-4JpcIp3w4IbcDUBrMnm0RCen2RKKI")
    dp = Dispatcher(bot)

    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(instructions, commands=['help'])
    dp.register_message_handler(repair, commands='repair')
    dp.register_message_handler(shift_stats, commands=['stats'])
    dp.register_message_handler(end_shift, commands=['end_shift'])
    dp.register_message_handler(process_scooters)

    log.debug('Handlers are registered.')

    executor.start_polling(dp)

