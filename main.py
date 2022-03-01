import logging

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.webhook import SendMessage
import json
import time
import asyncio

# in seconds
#DELAY = 1814400
DELAY = 5
API_TOKEN = '###'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(content_types=['new_chat_members'])
async def handle_user_join(message: types.Message):
    print(message.new_chat_members[0].id, "joined")
    if message.chat.id not in usertime_dbase:
        usertime_dbase[message.chat.id] = {}
    if message.new_chat_members[0].id not in usertime_dbase[message.chat.id]:
        usertime_dbase[message.chat.id][message.new_chat_members[0].id] = time.time()
        with open("db.txt", 'w') as json_file:
            json.dump(usertime_dbase, json_file)
    return


async def kick_user(chat_id, user_id):
    await bot.ban_chat_member(chat_id, user_id)
    await bot.unban_chat_member(chat_id, user_id)


def scheduler(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(DELAY, scheduler, coro, loop)


async def banchecker():
    current_time = time.time()
    for chat in usertime_dbase:
        banned = []
        for user in usertime_dbase[chat]:
            if current_time - usertime_dbase[chat][user] > 10:
                await ban_user(chat, user)
                banned.append(user)
                print("banned", user)
        for user in banned:
            del usertime_dbase[chat][user]
    with open("db.txt", 'w') as json_file:
        json.dump(usertime_dbase, json_file)


if __name__ == '__main__':
    with open("db.txt") as json_file:
        global usertime_dbase
        usertime_dbase = json.load(json_file)
    loop = asyncio.get_event_loop()
    loop.call_later(DELAY, scheduler, banchecker, loop)
    executor.start_polling(dp, loop=loop)
