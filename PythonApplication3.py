import netmiko
from netmiko import ConnectHandler
import getpass
import telebot
from collections import Counter
import sqlite3
import time
import os
import subprocess

#  msg = bot.send_message(message.chat.id, '*текст пользователю*', reply_markup = *Имя клавиатуры*)
#  bot.register_next_step_handler(msg, *название следующей функции*)



token = 'ваш токен бота'
bot = telebot.TeleBot(token)
keyboard_menu = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
keyboard_menu.row('Мои устройства', 'Добавить новое устройство')
keyboard_menu.row('Добавить нового пользователя', 'Терминал сервера')
keyboard_type_device = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
keyboard_type_device.row('Cisco', 'MikroTik', 'Keenetic')
keyboard_type_device.row('Huawei', 'TP-Link', 'Eltex')
keyboard_new_yes_or_no = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
keyboard_new_yes_or_no.row('Добавить', 'В меню')
keyboard_action = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
keyboard_action.row('Подключиться', 'Скрипты')
keyboard_action.row('Получить последние записи log-файла')
keyboard_action.row('Удалить устройство')
keyboard_action.row('Назад')
keyboard_yes_or_no = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
keyboard_yes_or_no.row('Да', 'Нет')
keyboard_exit = telebot.types.ReplyKeyboardMarkup(True)
keyboard_exit.row('Назад')
keyboard_confirm_or_exit = telebot.types.ReplyKeyboardMarkup(True)
keyboard_confirm_or_exit.row('Готово')
keyboard_script_choise = telebot.types.ReplyKeyboardMarkup(True)
keyboard_script_choise.row('Выполнить', 'Удалить')
keyboard_script_choise.row('Назад')

def make_keyboard():
    global keyboard_devices
    keyboard_devices = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
    db = sqlite3.connect('database.db', check_same_thread=False)
    cur = db.cursor()
    cur.execute('SELECT name FROM devices')
    devices = cur.fetchall()
    for i in devices:
        keyboard_devices.row(str(i[0]))
    keyboard_devices.row('Назад')

def make_keyboard_script(name):
    global keyboard_scripts
    keyboard_scripts = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
    db = sqlite3.connect('database.db', check_same_thread=False)
    cur = db.cursor()
    cur.execute("SELECT DISTINCT name_script FROM scripts WHERE name_device = '{0}'".format(name))
    scripts = cur.fetchall()
    for i in scripts:
        keyboard_scripts.row(str(i[0]))
    keyboard_scripts.row('Добавить')
    keyboard_scripts.row('Назад')

@bot.message_handler(commands = ['start', 'menu'])
def startanswer(message):
    id = message.chat.id
    msg = message.text
    check = False
    db = sqlite3.connect('database.db', check_same_thread=False)
    cur = db.cursor()
    cur.execute('SELECT id_user FROM users')
    check_user = str(cur.fetchall())
    if str(message.chat.id) in check_user:
        check = True

    if check == True or msg == '584806':
        msg = bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup = keyboard_menu)
        bot.register_next_step_handler(msg, main)
    else:
        bot.send_message(message.chat.id, 'Доступ запрещен')
        bot.send_message(message.chat.id, 'Ваш chat_id: {0}'.format(id))

def main(message):
    msg = message.text
    if msg == 'Мои устройства':
        make_keyboard()
        msg = bot.send_message(message.chat.id, 'Выберите устройство: ', reply_markup = keyboard_devices)
        bot.register_next_step_handler(msg, my_devices)
    elif msg == 'Добавить новое устройство':
        msg = bot.send_message(message.chat.id, 'Назовите устройство: ')
        bot.register_next_step_handler(msg, add_new_device)
    elif msg == 'Добавить нового пользователя':
        msg = bot.send_message(message.chat.id, 'Введите chat_id: ', reply_markup = keyboard_exit)
        bot.register_next_step_handler(msg, add_new_user)
    elif msg == 'Терминал сервера':
        msg = bot.send_message(message.chat.id, 'Введите команду: ', reply_markup = keyboard_exit)
        os.system("chcp 866")
        bot.register_next_step_handler(msg, server_terminal)
    else:
         msg = bot.send_message(message.chat.id, 'Не могу распознать ответ', reply_markup = keyboard_menu)
         bot.register_next_step_handler(msg, main)

def server_terminal(message):
    msg = message.text
    if msg == 'Назад':         
       msg = bot.send_message(message.chat.id, 'Подключение разорвано (2) ', reply_markup = keyboard_menu)
       bot.register_next_step_handler(msg, main)
    else:
       try:
          output = subprocess.check_output(msg, shell=True)
          print(output)
          msg = bot.send_message(message.chat.id, '{0}'.format(output), reply_markup = keyboard_exit)
          bot.register_next_step_handler(msg, server_terminal)
       except:
          msg = bot.send_message(message.chat.id, 'Подключение разорвано (1) ', reply_markup = keyboard_menu)
          bot.register_next_step_handler(msg, main)

### Добавляем пользователя



def user_check(message):
    check = True
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    for i in range(len(message)):
        if message.lower()[i] not in numbers:
            check = False
    return check

def add_new_user(message):
    msg = message.text
    if user_check(msg) == True:
        db = sqlite3.connect('database.db', check_same_thread=False)
        cur = db.cursor()
        id = msg
        cur.execute(f"INSERT INTO users(id_user) VALUES('{id}');") #f"DELETE FROM devices WHERE name = '{name}';"
        db.commit()
        msg = bot.send_message(message.chat.id, 'Пользователь с chat_id: {0} добавлен'.format(msg), reply_markup = keyboard_menu)
        bot.register_next_step_handler(msg, main)
    elif msg == 'Назад':
         msg = bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup = keyboard_menu)
         bot.register_next_step_handler(msg, main)
    else:
        msg = bot.send_message(message.chat.id, 'Не верный формат chat_id', reply_markup = keyboard_menu)
        bot.register_next_step_handler(msg, main)



### Добавляем новое устройство



def add_new_device(message):
    msg = message.text
    name = message.text
    msg = bot.send_message(message.chat.id, 'Выберите тип устройства', reply_markup = keyboard_type_device)
    bot.register_next_step_handler(msg, add_new_device_type, name)

def add_new_device_type(message, name):
    msg = message.text
    if msg == 'Cisco':
        type = 'cisco_ios'
        msg = bot.send_message(message.chat.id, 'Введите IP: ')
        bot.register_next_step_handler(msg, add_new_device_ip, name, type)
    elif msg == 'MikroTik':
        type = 'eltex'
        msg = bot.send_message(message.chat.id, 'Введите IP: ')
        bot.register_next_step_handler(msg, add_new_device_ip, name, type)
    elif msg == 'Keenetic':
        type = 'eltex'
        msg = bot.send_message(message.chat.id, 'Введите IP: ')
        bot.register_next_step_handler(msg, add_new_device_ip, name, type)
    elif msg == 'Huawei':
        type = 'eltex'
        msg = bot.send_message(message.chat.id, 'Введите IP: ')
        bot.register_next_step_handler(msg, add_new_device_ip, name, type)
    elif msg == 'TP-Link':
        type = 'eltex'
        msg = bot.send_message(message.chat.id, 'Введите IP: ')
        bot.register_next_step_handler(msg, add_new_device_ip, name, type)
    elif msg == 'Eltex':
        type = 'eltex'
        msg = bot.send_message(message.chat.id, 'Введите IP: ')
        bot.register_next_step_handler(msg, add_new_device_ip, name, type)
    else:
         msg = bot.send_message(message.chat.id, 'Не могу распознать ответ', reply_markup = keyboard_type_device)
         bot.register_next_step_handler(msg, add_new_device_type, name)

def check_ip_mask(message):
    check = True
    count = Counter(message)
    signes = ["."]
    numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    if count['.'] != 3:
        check = False
    for i in range(len(message)):
        if message[i] not in signes + numbers:
            check = False
    return check

def check_port(message):
    check = True
    numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    for i in range(len(message)):
        if message[i] not in numbers:
            check = False
    return check

def check_username(message):
    check = True
    rus_lang = ['й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х', 'ъ',
                'ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж', 'э',
                'я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю']
    for i in range(len(message)):
        if message.lower()[i] in rus_lang:
            check = False
    return check

def add_new_device_ip(message, name, type):
    msg = message.text
    if check_ip_mask(msg) == True:
        ipadr = msg
        msg = bot.send_message(message.chat.id, 'Введите порт: ')
        bot.register_next_step_handler(msg, add_new_device_port, name, type, ipadr)
    else:
        msg = bot.send_message(message.chat.id, 'IP введен не верно')
        bot.register_next_step_handler(msg, add_new_device_ip, name, type)

def add_new_device_port(message, name, type, ipadr):
    msg = message.text
    if check_port(msg) == True:
        port = msg
        msg = bot.send_message(message.chat.id, 'Введите Username: ')
        bot.register_next_step_handler(msg, add_new_device_username, name, type, ipadr, port)
    else:
        msg = bot.send_message(message.chat.id, 'Порт введен не верно')
        bot.register_next_step_handler(msg, add_new_device_port, name, type, ipadr)

def add_new_device_username(message, name, type, ipadr, port):
    msg = message.text
    if check_username(msg) == True:
        username = msg
        msg = bot.send_message(message.chat.id, 'Введите пароль: ')
        bot.register_next_step_handler(msg, add_new_device_password, name, type, ipadr, port, username)
    else:
        msg = bot.send_message(message.chat.id, 'Username введен не верно')
        bot.register_next_step_handler(msg, add_new_device_username, name, type, ipadr, port)

def add_new_device_password(message, name, type, ipadr, port, username):
    msg = message.text
    if check_username(msg) == True:
        password = msg
        msg = bot.send_message(message.chat.id, 'Проверьте правильность введенных данных' + '\n' + 
                               '\n' + 'Device Name:  ' + name +
                               '\n' + 'Type:  ' + type +
                               '\n' + 'IP:  ' + ipadr + 
                               '\n' + 'Port:  ' + port + 
                               '\n' + 'Username:  '+ username + 
                               '\n' + 'Password:  ' + password, reply_markup = keyboard_new_yes_or_no)
        bot.register_next_step_handler(msg, add_or_back, name, type, ipadr, port, username, password)
    else:
        msg = bot.send_message(message.chat.id, 'Пароль введен не верно')
        bot.register_next_step_handler(msg, add_new_device_password, name, type, ipadr, port, username)

def add_or_back(message, name, type, ipadr, port, username, password):
    msg = message.text
    if msg == 'Добавить':
        db = sqlite3.connect('database.db', check_same_thread=False)
        cur = db.cursor()
        cur.execute('INSERT INTO devices(name, type, ip, port, username, password) VALUES(?,?,?,?,?,?);', (name, type, ipadr, port, username, password))
        db.commit()
        del name, type, ipadr, port, username, password
        msg = bot.send_message(message.chat.id, 'Устройство добавлено', reply_markup = keyboard_menu)
        bot.register_next_step_handler(msg, main)
    elif msg == 'В меню':
         del name, type, ipadr, port, username, password
         msg = bot.send_message(message.chat.id, 'Выберите действие:', reply_markup = keyboard_menu)
         bot.register_next_step_handler(msg, main)
    else:
        msg = bot.send_message(message.chat.id, 'Не распознал ответ', reply_markup = keyboard_new_yes_or_no)
        bot.register_next_step_handler(msg, add_or_back, name, type, ipadr, port, username, password)



### Мои устройства



def my_devices(message):
    msg = message.text
    check = False
    db = sqlite3.connect('database.db', check_same_thread=False)
    cur = db.cursor()
    cur.execute('SELECT name FROM devices')
    names = str(cur.fetchall())
    if msg in names:
        check = True
    if check == True:
        name = msg
        msg = bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup = keyboard_action)
        bot.register_next_step_handler(msg, action, name)
    elif msg == 'Назад':
        msg = bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup = keyboard_menu)
        bot.register_next_step_handler(msg, main)
    else:
        msg = bot.send_message(message.chat.id, 'Нет такого устройства', reply_markup = keyboard_devices)
        bot.register_next_step_handler(msg, my_devices)

def action(message, name):
    msg = message.text
    if msg == 'Подключиться':
        connector(message, name)
    elif msg == 'Получить последние записи log-файла':
        last_log(message, name)
    elif msg == 'Скрипты':
        make_keyboard_script(name)
        msg = bot.send_message(message.chat.id, 'Выберите скрипт для {0}'.format(name), reply_markup = keyboard_scripts)
        bot.register_next_step_handler(msg, scripts, name)
    elif msg == 'Удалить устройство':
        msg = bot.send_message(message.chat.id, 'Удалить устройство?', reply_markup = keyboard_yes_or_no)
        bot.register_next_step_handler(msg, delete, name)
    elif msg == 'Назад':
        msg = bot.send_message(message.chat.id, 'Выберите устройство: ', reply_markup = keyboard_devices)
        bot.register_next_step_handler(msg, my_devices)
    else:
        msg = bot.send_message(message.chat.id, 'Не распознал ответ', reply_markup = keyboard_action)
        bot.register_next_step_handler(msg, action, name)

def delete(message, name):
    msg = message.text
    if msg == 'Да':
        db = sqlite3.connect('database.db', check_same_thread=False)
        cur = db.cursor()
        cur.execute(f"DELETE FROM devices WHERE name = '{name}';")
        db.commit()
        make_keyboard()
        msg = bot.send_message(message.chat.id, 'Данные о {0} стерты'.format(name), reply_markup = keyboard_devices)
        bot.register_next_step_handler(msg, my_devices)
    elif msg == 'Нет':
        msg = bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup = keyboard_action)
        bot.register_next_step_handler(msg, action, name)
    else:
        msg = bot.send_message(message.chat.id, 'Не распознал ответ', reply_markup = keyboard_yes_or_no)
        bot.register_next_step_handler(msg, delete, name)


def last_log(message, name):
        msg = message.text
        db = sqlite3.connect('database.db', check_same_thread=False)
        cur = db.cursor()
        cur.execute(f"SELECT type, ip, port, username, password FROM devices WHERE name = '{name}';")
        data = cur.fetchall()
        for i in data:
            type = str(i[0])
            ip = str(i[1])
            port = str(i[2])
            username = str(i[3])
            password = str(i[4])
        connect = {'device_type': type,
                   'host': ip,
                   'port': port,
                   'username': username,
                   'password': password}
        try:
            sshCli = ConnectHandler(**connect)
            if type == 'cisco':
                sshCli.send_command('config terminal')
                output = sshCli.send_command_timing('logging console 7', read_timeout=5)
                answer = sshCli.find_prompt() + 'logging console 7' + output
                msg = bot.send_message(message.chat.id, '{0}'.format(answer), reply_markup = keyboard_action)
                bot.register_next_step_handler(msg, action, name)
            else:
                output = sshCli.send_command_timing('show log 30 once', read_timeout=1)
                answer = sshCli.find_prompt() + 'show log 30 once' + output
                msg = bot.send_message(message.chat.id, '{0}'.format(answer), reply_markup = keyboard_action)
                bot.register_next_step_handler(msg, action, name)
        except:
            msg = bot.send_message(message.chat.id, 'Подключение разорвано', reply_markup = keyboard_action)
            bot.register_next_step_handler(msg, action, name)

def connector(message, name):
    db = sqlite3.connect('database.db', check_same_thread=False)
    cur = db.cursor()
    cur.execute(f"SELECT type, ip, port, username, password FROM devices WHERE name = '{name}';")
    data = cur.fetchall()
    for i in data:
        type = str(i[0])
        ip = str(i[1])
        port = str(i[2])
        username = str(i[3])
        password = str(i[4])
    connect = {'device_type': type,
               'host': ip,
               'port': port,
               'username': username,
               'password': password}
    try:
       sshCli = ConnectHandler(**connect)
       msg = bot.send_message(message.chat.id, 'Подключение установлено\n{0}'.format(sshCli.find_prompt()), reply_markup = keyboard_exit)
       bot.register_next_step_handler(msg, connection, name, sshCli)
    except:
       msg = bot.send_message(message.chat.id, 'Подключение разорвано (0)', reply_markup = keyboard_action)
       bot.register_next_step_handler(msg, action, name)

def connection(message, name, sshCli):
    msg = message.text
    try:
       if msg == 'Назад':
          sshCli.disconnect()
          msg = bot.send_message(message.chat.id, 'Подключение разорвано (1) ', reply_markup = keyboard_action)
          bot.register_next_step_handler(msg, action, name)
       else:
          try:
             command = str(msg)
             output = sshCli.send_command(command)
             answer = sshCli.find_prompt() + command + '\n' + output         
             msg = bot.send_message(message.chat.id, '{0}'.format(answer), reply_markup = keyboard_exit)
             bot.register_next_step_handler(msg, connection, name, sshCli)
          except:
             msg = bot.send_message(message.chat.id, 'Неизвестная команда\n{0}'.format(sshCli.find_prompt()), reply_markup = keyboard_exit)
             bot.register_next_step_handler(msg, connection, name, sshCli)

    except:
       msg = bot.send_message(message.chat.id, 'Подключение разорвано (2)', reply_markup = keyboard_action)
       bot.register_next_step_handler(msg, action, name)

def scripts(message, name):
    msg = message.text
    check = False
    db = sqlite3.connect('database.db', check_same_thread=False)
    cur = db.cursor()
    cur.execute("SELECT name_script FROM scripts WHERE name_device = '{0}'".format(name))
    names = str(cur.fetchall())
    if msg in names and msg != 'Добавить' and msg != 'Назад':
        check = True
        name_script = msg
        msg = bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup = keyboard_script_choise)
        bot.register_next_step_handler(msg, script_choise, name, name_script)
    elif msg == 'Добавить':
        msg = bot.send_message(message.chat.id, 'Введите название скрипта: ')
        bot.register_next_step_handler(msg, add_script, name)
    elif msg == 'Назад':
        msg = bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup = keyboard_action)
        bot.register_next_step_handler(msg, action, name)
    else:
        msg = bot.send_message(message.chat.id, 'Не распознал ответ', reply_markup = keyboard_scripts)
        bot.register_next_step_handler(msg, scripts, name)

def script_choise(message, name, name_script):
    msg = message.text
    if msg == 'Выполнить':
        msg = bot.send_message(message.chat.id, 'Успешно выполнено', reply_markup = keyboard_action)
        bot.register_next_step_handler(msg, action, name)
    elif msg == 'Удалить':
        db = sqlite3.connect('database.db', check_same_thread=False)
        cur = db.cursor()
        cur.execute(f"DELETE FROM scripts WHERE name_device = '{0}' and name_script = '{1}'".format(name, name_script)) #f"DELETE FROM devices WHERE name = '{name}';"
        db.commit()
        msg = bot.send_message(message.chat.id, 'Скрипт {0} для устройства {1} удален'.format(name_script, name), reply_markup = keyboard_action)
        bot.register_next_step_handler(msg, action, name)
    elif msg == 'Назад':
        msg = bot.send_message(message.chat.id, 'Выберите действие:', reply_markup = keyboard_action)
        bot.register_next_step_handler(msg, action, name)
    else:
        msg = bot.send_message(message.chat.id, 'Не распознал ответ', reply_markup = keyboard_script_choise)
        bot.register_next_step_handler(msg, script_choise, name_script)

def add_script(message, name):
    name_script = message.text
    bot.send_message(message.chat.id, 'Прежде чем добавлять скрипт, убедитесь что введенные команды не вызовут ошибок')
    msg = bot.send_message(message.chat.id, 'Введите команду:', reply_markup = keyboard_confirm_or_exit)
    bot.register_next_step_handler(msg, add_script_command, name, name_script)

def add_script_command(message, name, name_script):
    msg = message.text
    if msg == 'Готово':
        db = sqlite3.connect('database.db', check_same_thread=False)
        cur = db.cursor()
        cur.execute("SELECT data FROM scripts WHERE name_device = '{0}' and name_script = '{1}'".format(name, name_script))
        data = str(cur.fetchall())
        data = data.replace("[('", "", 1)
        data = data.replace("',), ('", "\n ")
        data = data.replace("',)]", "")
        make_keyboard_script(name)
        msg = bot.send_message(message.chat.id, 'Создан скрипт для {0} с именем {1}: \n {2}'.format(name, name_script, data), reply_markup = keyboard_scripts)
        bot.register_next_step_handler(msg, scripts, name)
    else:
        db = sqlite3.connect('database.db', check_same_thread=False)
        cur = db.cursor()
        cur.execute("INSERT INTO scripts(name_device, name_script, data) VALUES(?,?,?);", (name, name_script, msg))
        db.commit()
        msg = bot.send_message(message.chat.id, 'Введите команду:', reply_markup = keyboard_confirm_or_exit)
        bot.register_next_step_handler(msg, add_script_command, name, name_script)

if __name__ == '__main__':
        bot.infinity_polling()
