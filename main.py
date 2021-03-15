import os
import io
import time
import json
import asyncio
import random
import requests
import subprocess
from threading import Thread
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import colorama
from colorama import Fore, Back, Style

API_TOKEN = '1601993948:AAEVIc8vlA5hkaM8Uxs_lrm1I70CH_jmbz8'

colorama.init(autoreset=True)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


##    JSON    ##
def jsonread(file):
    '''
    Чтение JSON файла file
    
    file - имя JSON файла, может содержать полный или относительный путь
    '''
    with open(file, "r", encoding='utf-8') as read_file:
        data = json.load(read_file)
    return data


def jsonwrite(file, data):
    '''
    Запись в JSON файл file данные data
    
    file - имя JSON файла, может содержать полный или относительный путь
    data - данные, может быть словарем/списком/кортежем/строкой/числом
    '''
    with open(file, 'w', encoding='utf-8') as write_file:
        write_file.write(json.dumps(data))


##    СООБЩЕНИЯ   ##
async def send(chat_id, message):
    '''
    Отправляет сообщение определенному человеку/чату. Если сообщение слишком 
    длинное, то разделяет его
    chat_id - целое число, id чата или пользователя Telegram
    message - строка, само сообщение
    '''
    if len(message) > 3000:
        for x in range(0, len(message), 3000):
            await bot.send_message(chat_id, message[x:x+3000])
    else:
        await bot.send_message(chat_id, message)


async def send_to_admin(message):
    '''
    Отправляет сообщение всем пользователям у кого есть тег 'a' (Всем админам Толи)
    
    message - сообщение для админов
    '''
    for admin in USERS_LIST:
        if 'a' in USERS_LIST[admin]:
            try:
                await send(admin, message)
            except:
                pass


async def anon_send(chat_id, msg):
    '''
    Функция анонимной отправки сообщения.
    Отправляет сообщение от имени толи и сообщает, что 
    это писал другой пользователь
    
    chat_id - целое число, id чата или пользователя Telegram
    message - строка, само сообщение
    '''
    await send(chat_id, 'Меня попросили тебе передать:')
    await send(chat_id, msg)


async def tolya_say(chat_id, msg):
    '''
    Функция отправки сообщения от имени Толи.
    Отправляет сообщение от имени толи
    
    chat_id - целое число, id чата или пользователя Telegram
    message - строка, само сообщение
    '''
    print(f'{chat_id}: {msg}')
    await send(chat_id, msg)


##    РАБОТА С ФАЙЛАМИ    ##
async def download(chat_id, msg):
    '''
    Функция скачивания файла из интернета.
    Скачивает файл по ссылки данной в сообщении после слова 'скачать'
    
    chat_id - целое число, id чата или пользователя Telegram
    msg - строка, команда
    '''
    msg = msg.split(' ')
    if len(msg) > 2:
        file = requests.get(msg[1])
        if file.status_code == 200:
            await send(chat_id, f'Скачиваю {os.path.split(msg[1])[1]}...')
            with open(os.path.join(FILES_PATH, msg[2]), 'wb') as f:
                f.write(file.content)
            await send(chat_id, 'Файл скачан!')
            if len(msg) > 3:
                if msg[3] == 'мне':
                    await send(chat_id, 'Отправляю...')
                    bot.send_document(chat_id, open(os.path.join(FILES_PATH, msg[2]), 'rb'))
        elif file.status_code == 404:
            await send(chat_id, 'Файл не найден!')
        else:
            await send(chat_id, f'Ошибка запроса! {file}')
    else:
        await send(chat_id, 'Пример использования комманды\n"скачай http://site.ru//file.zip название.файла мне"')


async def upload(chat_id, msg):
    '''
    Функция загрузки.
    Загружает файл в чат запросившего пользователя. Запрос должен включать:
    слово 'загрузи', имя файла или номер файла в категории
    
    chat_id - целое число, id чата или пользователя Telegram
    msg - строка, команда
    '''
    msg = msg.split(' ')
    if len(msg) > 1:
        if msg[1].isdigit:
            try:
                file = os.path.join(FILES_PATH, os.listdir(FILES_PATH)[int(msg[1])-1])
                await send(chat_id, 'Загружаю файл...')
                bot.send_document(chat_id, open(file, 'rb'))
            except Exception as e:
                print(e)
        elif os.path.exists(os.path.join('files', msg[1])):
            file = os.path.join('files', msg[1])
            await send(chat_id, 'Загружаю файл...')
            await bot.send_document(chat_id, open(file, 'rb'))
        elif os.path.exists(msg[1]):
            file = os.path.split(msg[1])[1]
            await send(chat_id, 'Загружаю файл...')
            await bot.send_document(chat_id, open(file, 'rb'))
        else:
            await send(chat_id, 'Файл не найден!')
    else:
        await send(chat_id, 'Пример использования комманды\nзагрузи путь/к/файлу.файл')


##    УЧАСТНИКИ    ##
async def add_member(chat_id, msg):
    '''
    Функция добавления участника.
    Добавляет участника и приписывает ему привелегии, или изменяет 
    привелегии существующего участника. Привелегии создателя может изменить только создатель.
    
    chat_id - целое число, id чата или пользователя Telegram
    msg - строка, команда
    '''
    msg = msg.split(' ')
    if len(msg) > 1:
        member = msg[1].split(':')
        if len(member) > 1:
            if member[0].lower() in ['мне', 'меня']:
                member[0] = chat_id
            try:
                if member[0] == '768602428' and chat_id == 768602428:
                    USERS_LIST.update({int(member[0]):member[1]})
                elif member[0] == '768602428' and chat_id != 768602428:
                    await send(chat_id, 'Вы не можете изменять привелегии этого пользователя')
                else:
                    USERS_LIST.update({int(member[0]):member[1]})
            except ValueError:
                await send(chat_id, 'ID должен быть числом!')
            except Exception as e:
                await send(chat_id, f'Произошла ошибка!\n{e}')
            else:
                data = {'members': USERS_LIST,
                        'games': GAMES}
                jsonwrite(JSON_PATH, data)
                await send(chat_id, f'Участник добавлен!\n ID - {member[0]}; ПРАВА - {member[1]}')
            finally:
                return 0
    await send(chat_id, 'Пример использования комманды\nдобавить ID_ПОЛЬЗОВАТЕЛЯ:ПРАВА')


async def del_member(chat_id, msg):
    '''
    Функция удаления участника.
    Удаляет участника, но не создателя.
    
    chat_id - целое число, id чата или пользователя Telegram
    msg - строка, команда
    '''
    msg = msg.split(' ')
    if len(msg) > 1:
        if msg[1] != '768602428':
            try:
                del USERS_LIST[int(msg[1])]
            except KeyError:
                await send(chat_id, 'Участник не найден!')
            except ValueError:
                await send(chat_id, 'ID должен быть числом!')
            except Exception as e:
                await send(chat_id, f'Произошла ошибка!\n{e}')
            else:
                data = {'members': USERS_LIST,
                        'games': GAMES}
                jsonwrite(JSON_PATH, data)
                await send(chat_id, f'Участник {msg[1]} удален!')
        else:
            await send(chat_id, 'Нельзя удалить создателя!')
    else:
        await send(chat_id, 'Пример использования комманды\nудали ID_ПОЛЬЗОВАТЕЛЯ')


##    СТОРОННИЕ ПРОГРАММЫ    ##
async def run(chat_id, msg, user_name, now, message):
    if msg.split(' ')[0] != 'main':
        app = f'{os.path.join(APP_PATH, msg)} {chat_id}'
        try:
            stdout = subprocess.Popen(app.split(' '), shell=True, stdout=subprocess.PIPE).communicate()[0]
            stdout = stdout.decode(encoding='utf-8', errors='ignore')
            if stdout not in ['', '\n', None]:
                print(f'{stdout}')
                await send(chat_id, stdout)
        except Exception as e:
            await send(chat_id, f'Произошла ошибка! вымени\n{e}')
    return


async def cmd(chat_id, msg):
    '''
    Выполняет консольную команду и отправляет ответ.
    
    chat_id - целое число, id чата или пользователя Telegram
    msg - строка, команда
    '''
    com = msg.split(' ')
    
    if len(com) > 1 and com.index('cmd') == 0:
        com = msg.replace('cmd ', '')
        if 'cd ' in com:
            print(f'{Fore.CYAN}Выполняю команду {Fore.YELLOW}{com}')
            try:
                os.chdir(com.split(' ')[1])
            except Exception as e:
                await send(chat_id, f'Произошла ошибка! {Fore.YELLOW}{com}\n{e}')
        elif 'dir' in com:
            print(f'{Fore.CYAN}Выполняю команду {Fore.YELLOW}{com}')
            answer = f'Директория {os.getcwd()}:\n{"-"*29}\n\n'
            num = 1
            for file in os.listdir():
                if os.path.isfile(file):
                    answer += f'<File {num}> {file}\n'
                else:
                    answer += f'<Dir {num}> {file}\n'
                num += 1
            answer += f'\n{"-"*29}'
            await send(chat_id, answer)
        elif com not in ['date']:
            print(f'{Fore.CYAN}Выполняю команду {Fore.YELLOW}{com}')
            try:
                stdout = subprocess.Popen(com.split(' '), shell=True, stdout=subprocess.PIPE).communicate()[0]
                stdout = stdout.decode('utf-8', errors='ignore')
                print(stdout)
            except Exception as e:
                await send(chat_id, f'Произошла ошибка!\n{e}')
            else:
                print(stdout)
                if stdout != '':
                    try:
                        await send(chat_id, stdout)
                    except Exception as e:
                        await send(chat_id, f'Произошла ошибка!\n{e}')
                else:
                    await send(chat_id, f'Команда "{com}" неопознана!')
        else:
            await send(chat_id, f'Команда "{com}" запрещена!')


##    КОМАНДЫ    ##
async def random_choice(chat_id, cat):
    '''
    Функция рандомного выбора.
    Случайно выбирает фотографию из папки и отправляет их
    
    chat_id - целое число, id чата или пользователя Telegram
    cat - категория выбора
    '''
    intro = {'чипсики': 'И твои чипсики на сегодня...',
             'напиток': 'И твой напиток на сегодня...',
             'герой': 'И твой герой на сегодня...'}
    path = {'чипсики': 'chipseki',
            'напиток': 'drinks',
            'герой': 'dota'}
    
    await send(chat_id, intro[cat])
    await asyncio.sleep(2)
    
    RANDOM_PATH = os.path.join(APP_PATH, 'random', path[cat])
    answer = os.path.join(RANDOM_PATH, random.choice(os.listdir(RANDOM_PATH)))
    
    await bot.send_photo(chat_id, open(answer, 'rb'))
    pass


async def issue(chat_id, msg, user_name):
    '''
    Функция приема идей.
    Принимает идею написанную после слова 'идея' в сообщении
    и сохраняет ее в файл, а так же отправляет эту идею админам
    
    chat_id - целое число, id чата или пользователя Telegram
    msg - строка, идея
    user_name - строка, имя пользователя
    '''
    msg = msg.split(' ')
    if len(msg) > 1 and msg[0] == 'идея':
        msg.remove('идея')
        
        msg_ = ''
        for word in msg:
            msg_ += word + ' '
        
        with open('ideas.txt', 'a') as f:
            f.write(f'\nИдея от {user_name}:\n')
            f.write(msg_)
            
        await send(chat_id, 'Я записал твою идею')
        await send_to_admin(f'Новая идея была предложена\n{msg_}')
    else:
        await send(chat_id, f'С помощью этой команды ты можешь предложить разработчику свою идею для расширения моей функциональности\n\nПример использования комманды\nидея мысль которую хочешь предложить')


async def blackjack(message, chat_id, mode):
    BLACKJACK_PATH = os.path.join(APP_PATH, 'blackjack')
    
    if mode == 'start':
        inline_kb = types.InlineKeyboardMarkup(row_width=2)
        single_bt = types.InlineKeyboardButton('Против Толи', callback_data='jack_single')
        multi_bt = types.InlineKeyboardButton('Против кого-то другого', callback_data='jack_multi')
        inline_kb.add(single_bt, multi_bt)

        await message.reply('Ну, сыграем в 21 очко!\nБудешь играть со мной или с кем-то другим?', reply_markup=inline_kb)


##    ОБРАБОТКА ПРИНЯТЫХ СООБЩЕНИЙ    ##
@dp.callback_query_handler(lambda cb: cb.data in ['jack_single', 'jack_multi'])
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    await query.answer()  # send answer to close the rounding circle

    answer_data = query.data
    
    if answer_data == 'jack_single':
        await bot.send_message(query.from_user.id, 'Ну готовься, ща я тебя обыграю и уничтожу!)')
    elif answer_data == 'jack_multi':
        await bot.send_message(query.from_user.id, "Oh no...Why so?")
    else:
        await bot.send_message(query.from_user.id, "Invalid callback data!")


@dp.message_handler(commands=['start', 'restart'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or '/restart' command
    """
    kb_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb_main.row('Привет', 'Идея', 'ID', 'Анон')
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id not in USERS_LIST:
        USERS_LIST.update({user_id:'0'})
        jsonwrite(JSON_PATH, USERS_LIST)
        await send_to_admin(f'Новый пользователь только что написал!\n Его ID - {user_id}\nОн уже добавлен в список')
    
    if user_id in USERS_LIST:
        for perm in USERS_LIST[user_id]:
            if perm == 'd':
                kb_main.add('Скачай')
            elif perm == 'u':
                kb_main.add('Загрузи', 'Файлы')
            elif perm == 'a':
                kb_main.add('Участники', 'Добавь', 'Удали', 'CMD')
            elif perm == 'z':
                kb_main.add('Чипсеки', 'Напиток')
    
    await message.reply('Привет!', 
                    reply_markup=kb_main)


@dp.message_handler()
async def main(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.username != None:
        user_name = message.from_user.username
    else:
        user_name = message.from_user.id
    chat_id = message.chat.id
    forw = message.forward_from
    msg = message.text.lower()
    now = time.struct_time(time.localtime(time.time()))
    nepon = True
    
    strs = []
    str_ = ''
    inbound = False
    for word in msg.split(' '):
        if inbound:
            str_ += word+' '
        if word[0] == '"':
            str_ += word+' '
            inbound = True
        if word[-1] == '"':
            strs.append(str_.replace('"', ''))
            inbound = False
            str_ = ''
    
    print(f'{Fore.GREEN}[{now.tm_hour:02d}:{now.tm_min:02d}]    {Fore.YELLOW}{user_name}{Fore.RESET} : {msg}')
    
    if msg.split(' ')[0] in ['толя', 'толь', 'анатолий', 'толян']:
        nepon = False
        if len(msg.split(' ')) == 1:
            await send(chat_id, random.choice([
                'А? Суету навести охота?',
                'Чего шумишь?',
                'Да-да, Я',
                'Шо?'
            ]))
        else:
            msg = msg.replace(msg.split(' ')[0]+' ', '')
    
    if forw != None:
        await send(chat_id, f'ID пользователя: {forw.id}')
    elif msg in ['привет', 'здарова']:
        await send(chat_id, 'Ну привет')
    elif msg == 'id':
        await send(chat_id, f'Ваш ID - {user_id}\nЧтобы получить ID другого пользователя перешлите его любое сообщение сюда')
    elif msg == 'участники':
            if 'm' in USERS_LIST[user_id]:
                num = 1
                answer = ''
                for member in USERS_LIST:
                    answer += f'#{num}\nID - {member}; ПРАВА - {USERS_LIST[member]}\n'
                    num += 1
                await send(chat_id, answer)
            else:
                await send(chat_id, 'Недостаточно прав')
    elif msg == 'файлы':
            if 'u' in USERS_LIST[user_id]:
                answer = f'Файлы доступные для загрузки:\n{"-"*29}\n\n'
                num = 1
                for file in os.listdir(FILES_PATH):
                    if os.path.isfile(os.path.join(FILES_PATH, file)):
                        answer += f'<File {num}> {file}\n'
                        num += 1
                answer += f'\n{"-"*29}'
                await send(chat_id, answer)
            else:
                await send(chat_id, 'Недостаточно прав')
    elif 'непонел' in msg.split(' ')[0]:
        await send(chat_id, random.choice([
            'Ахуив?',
            'Хуль меня пародируешь?',
            'Тебе до моего "непонел..." еще далеко'
        ]))
    elif msg.split(' ')[0] == 'идея':
        await issue(chat_id, msg, user_name)
    elif msg.split(' ')[0] == 'скачай':
            if 'd' in USERS_LIST[user_id]:
                file = await download(chat_id, msg)
            else:
                await send(chat_id, 'Недостаточно прав')
    elif msg.split(' ')[0] == 'загрузи':
            if 'u' in USERS_LIST[user_id]:
                file = await upload(chat_id, msg)
            else:
                await send(chat_id, 'Недостаточно прав')
    elif msg.split(' ')[0] == 'добавь':
            if 'm' in USERS_LIST[user_id]:
                await add_member(chat_id, msg)
            else:
                await send(chat_id, 'Недостаточно прав')
    elif msg.split(' ')[0] == 'удали':
            if 'm' in USERS_LIST[user_id]:
                await del_member(chat_id, msg)
            else:
                await send(chat_id, 'Недостаточно прав')
    elif msg.split(' ')[0] == 'cmd':
        if 'c' in USERS_LIST[user_id]:
            await cmd(chat_id, msg)
        else:
            await send(chat_id, 'Недостаточно прав')
    elif msg.split(' ')[0] == 'чипсеки':
        if 'z' in USERS_LIST[user_id]:
            await random_choice(chat_id, 'чипсеки')
        else:
            await send(chat_id, 'Недостаточно прав')
    elif msg.split(' ')[0] == 'напиток':
        if 'z' in USERS_LIST[user_id]:
            await random_choice(chat_id, 'напиток')
        else:
            await send(chat_id, 'Недостаточно прав')
    elif msg.split(' ')[0] == 'герой':
        await random_choice(chat_id, 'герой')
    elif msg.split(' ')[0] == 'игры':
        if GAMES != None:
            answer = ''
            for game in GAMES:
                answer += f'{game["name"]}\nЖанр: {game["genre"]}    Максимум игроков: {game["players_max"]}\n\n'
            await send(chat_id, answer)
    elif msg.split(' ')[0] in ['anon', 'анон']:
        if len(msg.split(' ')) == 1:
            await send(chat_id, 'Эта функция анонимно отправляет ваше сообщение другому пользователю этого бота\n\n')
            await send(chat_id, 'Пример использования: \nанон ID-получателя "Сообщение"\n - Сообщение обязательно должно быть в двойных скобках')
        else:
            if msg.split(' ')[1] in ['мне', 'меня']:
                to_chat_id = chat_id
            else:
                to_chat_id = msg.split(' ')[1]
            try:
                await anon_send(chat_id=chat_id,
                            msg=strs[0])
            except IndexError:
                await send(chat_id, 'Пример использования: \nанон ID-получателя "Сообщение"\n - Сообщение обязательно должно быть в двойных скобках')
            except Exception as e:
                await send(chat_id, f'Произошла ошибка!\n{e}')
            else:
                await send(chat_id, 'Сообщение отправлено!')
    elif msg.split(' ')[0] in ['say', 'скажи']:
        if len(msg.split(' ')) == 1:
            await send(chat_id, 'Эта функция отправляет ваше сообщение другому пользователю этого бота от имени Толи\n\n')
            await send(chat_id, 'Пример использования: \nскажи ID-получателя "Сообщение"\n - Сообщение обязательно должно быть в двойных скобках')
        else:
            if msg.split(' ')[1] in ['мне', 'меня']:
                to_chat_id = chat_id
            else:
                to_chat_id = msg.split(' ')[1]
            try:
                await tolya_say(chat_id=to_chat_id,
                            msg=strs[0])
            except IndexError:
                await send(chat_id, 'Пример использования: \nскажи ID-получателя "Сообщение"\n - Сообщение обязательно должно быть в двойных скобках')
            except Exception as e:
                await send(chat_id, f'Произошла ошибка!\n{e}')
            else:
                await send(chat_id, 'Я сказал)')
    elif msg.split(' ')[0]+'.py' in os.listdir(APP_PATH):
        await run(chat_id, msg, user_name, now, message)
    else:
        if nepon:
            await send(chat_id, 'непонел...')


@dp.message_handler(content_types=['document'])
async def doc_upload(message):
    document = message.document
    chat_id = message.chat.id
    user_id = message.from_user.id
    if message.from_user.username != None:
        user_name = message.from_user.username
    else:
        user_name = message.from_user.id
    
    if 'a' in USERS_LIST[user_id]:
        try:
            file_name = document.file_name
            file_id_info = await bot.get_file(document.file_id)
            download_file = await bot.download_file(file_id_info.file_path)
        except Exception as e:
            await send(chat_id, f'Произошла ошибка!\n{e}')
        else:
            await send(chat_id, 'Загружаю файл..')
            with open(os.path.join(APP_PATH, file_name), 'wb') as f:
                f.write(download_file.read())
            await send(chat_id, f'Файл загружен!\nЕго имя - "{file_name}"')


if __name__ == '__main__':
    APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    FILES_PATH = os.path.join(APP_PATH, 'files')
    JSON_PATH = os.path.join(APP_PATH, 'tolya_db.json')

    if os.path.exists(JSON_PATH):
        USERS_LIST = {}
        for member in jsonread(JSON_PATH)['members'].items():
            USERS_LIST.update({int(member[0]):member[1]})
        GAMES = jsonread(JSON_PATH)['games']
    else:
        USERS_LIST = {768602428:'smduc'}
        GAMES = ['']

    print(Fore.LIGHTGREEN_EX + 'Бот запущен!')
    
    executor.start_polling(dp, skip_updates=True)
