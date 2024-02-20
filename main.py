import telebot #pip install TelegramBotAPI
import sqlite3
import time


def command_split(command): #returns deadline in seconds and note text
    deadline, text = command.split()[1], command[len(command.split()[1])+6:]

    if deadline[-1] == 'y':
        deadline = round(time.time()) + 60*60*24*365*int(deadline[:-1])
    elif deadline[-1] == 'm':
        deadline = round(time.time()) + 60*60*24*30*int(deadline[:-1])
    elif deadline[-1] == 'd':
        deadline = round(time.time()) + 60*60*24*int(deadline[:-1])
    elif deadline[-1] == 'h':
        deadline = round(time.time()) + 60*60*int(deadline[:-1])
    else:
        return 1/0
    return deadline, text


def time_translate(n):
    n = n - round(time.time())
    if n<=0:
        flag = False
    else:
        flag = True
    years = n // (365*24*60*60)
    months = (n - years*(365*24*60*60))  // (30*24*60*60)
    days = (n - years*(365*24*60*60) - months*(30*24*60*60))  // (24*60*60)
    hours = (n - years*(365*24*60*60) - months*(30*24*60*60) - days*(24*60*60)) // (60*60)
    return years, months, days, hours, flag


#Token
bot = telebot.TeleBot('')





@bot.message_handler(commands=['start']) #Start command
def start(message):

    #Necessary variables
    table_name = message.chat.id

    #Database connection
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    #Creating a table if not exists
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS id{table_name}(
        note TEXT,
        deadline TEXT
    )""")
    connect.commit()
    text = """Функционал бота
/add [текст] - создать новую заметку
/tadd [время] [текст] - создать временную заметку
(формат времени: число + буква, где y - годы, m - месяцы, d - дни, h - часы)
Пример команды: /tadd 2d сдать проект
/notes - вывести все заметки
/delete [текст] - удалить заметку со значением [текст]
"""
    bot.send_message(message.chat.id, text)





@bot.message_handler(commands=['add']) #Add note command
def add(message):

    #database connection
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    try:

        #Necessary variables
        text = message.text[5:]
        table_name = message.chat.id

        #Creating a table if not exists
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS id{table_name}(
            note TEXT,
            deadline TEXT
        )""")
        connect.commit()

        #Adding a note
        cursor.execute(f"""INSERT INTO id{table_name} VALUES(?, ?);""", (text, ''))
        connect.commit()
        bot.send_message(message.chat.id, 'Заметка "' + text + '" успешно добавлена.')
    except:
        bot.send_message(message.chat.id, 'Проверьте правильность ввода и попробуйте ещё раз.')





@bot.message_handler(commands=['tadd']) #Command to add temporary note
def tadd(message):

    #Database connection
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    try:
        #Necessary variables
        deadline, text = command_split(message.text)
        table_name = message.chat.id

        #Creating a table if not exists
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS id{table_name}(
            note TEXT,
            deadline TEXT
        )""")
        connect.commit()

        #Adding a temporary note
        cursor.execute(f"""INSERT INTO id{table_name} VALUES(?, ?);""", (text, deadline))
        connect.commit()
        bot.send_message(message.chat.id, 'Заметка "' + text + f'" успешно добавлена. Установлено время в {message.text.split()[1]}')
    except:
        bot.send_message(message.chat.id, 'Проверьте правильность ввода и попробуйте ещё раз.')


@bot.message_handler(commands=['notes']) #Note output command
def notes(message):

    #Database connection
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    table_name = message.chat.id

    #Output notes
    try:
        cursor.execute(f"""SELECT note, deadline FROM id{table_name}""")
        data = cursor.fetchall()
        s = """"""
        flag = False
        for number, i in enumerate(data):
            number = f'{number+1}) '
            if str(i[1]) != '':
                years, months, days, hours, flag = time_translate(int(i[1]))
            if str(i[1]) == '':
                s = s + number + i[0] + '\n'
            if flag:
                if years > 0:
                    s = s + number + i[0] + f' ({years}y:{months}m:{days}d:{hours}h)' + '\n'
                elif months > 0:
                    s = s + number + i[0] + f' ({months}m:{days}d:{hours}h)' + '\n'
                elif days > 0:
                    s = s + number + i[0] + f' ({days}d:{hours}h)' + '\n'
                elif hours > 0:
                    s = s + number + i[0] + f' ({hours}h)' + '\n'
                elif hours == 0:
                    s = s + number + i[0] + f' (<1h)' + '\n'
            else:
                cursor.execute(f"DELETE FROM id{table_name} WHERE note = ?", (i[0],))
            
        bot.send_message(message.chat.id, s)
    except:
        #No notes exist or error
        bot.send_message(message.chat.id, 'Заметок пока что нет!')



@bot.message_handler(commands=['delete'])
def delete(message):

    #Database connection
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    #Deleting a note
    table_name = message.chat.id
    try:
        text = message.text[8:]
        cursor.execute(f"DELETE FROM id{table_name} WHERE note = ?", (text,))
        connect.commit()
        bot.send_message(message.chat.id, 'Заметка "' + text + '" успешно удалена.') 
    except:
        bot.send_message(message.chat.id, 'Проверьте правильность ввода и попробуйте ещё раз.') 





bot.polling(non_stop=True) #For non-stop operation of the bot
