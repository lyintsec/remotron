############################################################################
##
## Copyright 2024 lyint
##
## Лицензия Apache версии 2.0 («Лицензия»);
## вы не можете использовать этот файл, кроме как в соответствии с Лицензией.
## Вы можете получить копию Лицензии по адресу
##
## https://www.apache.org/licenses/LICENSE-2.0
##
## Если это не требуется действующим законодательством или не согласовано 
## в письменной форме, программное обеспечение распространяется по Лицензии,
## распространяется на условиях «КАК ЕСТЬ»,
## БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ ИЛИ УСЛОВИЙ, явных или подразумеваемых.
## См. лицензию для конкретного языка, регулирующего разрешения и
## ограничения по Лицензии.
##
############################################################################

import os
import sys
import datetime
import json
import tempfile
import subprocess

import configparser
from PyQt5 import QtCore, QtGui, QtWidgets
from notifypy import Notify

from settings import CONFIG_PATH, WINDOWS, DATA_PATH, \
    ICON_PATH, ICO_PATH, APP_TITLE
from ui import ui, main_window

# Служебные функции
def db_switch(test=False):
    """
    Функция переключения между основной
    и альтернативной БД
    Аргумент test позволяет посмотреть текущую БД 
    без ее переключения
    """
    global current_db

    if not test:
        if current_db == config_values.get('ips_path'):
            current_db = config_values.get('ips_accessorius_path')
        else:
            current_db = config_values.get('ips_path')

        machines_ip_array, machines_mirror = db_open(current_db)

        ui.comboBoxAdresses.clear() # Очищаем поле ComboBox (выпадающий список адресов)
        ui.comboBoxAdresses.addItems(machines_mirror) # Добавляем в выпадающий список другую БД
    else:
        return current_db
        

def db_open(current_db):
    """
    Открытие текстовой базы данных
    в которой хроанятся созраненные
    адреса подключения и их имена
    """

    def read_and_sort_db():
        """
        Загружает файл db.json и сортирует по ключу name
        """
        with open(current_db, "r", encoding='utf-8') as f:
            return sorted(json.load(f)["machines"], key=lambda s: s['name'])

    try:
        machines_ip_array = read_and_sort_db()
    except:
        db_error = popup_message(
            'error', 
            'Ошибка', 
            (
                f'Файл {current_db} пуст, не найден или содержит ошибки!<br>'
                'Пожалуй создам пустой файл и наполню его каркасом за вас.'
            )
        
        )

        if not db_error:
            exit()

        if os.path.exists(current_db) == False or os.stat(current_db).st_size == 0:
            with open(current_db, "w", encoding='utf-8') as jfw:
                jfw.write(
                    (
                        '{\n    "machines": [\n        '
                        '{\n            "name": "",'
                        '\n            "ip": ""'
                        '\n        }\n    ]\n}'
                    )
                )

        
        machines_ip_array = read_and_sort_db()


    # Создание списка для более удобного отображения
    machines_mirror = []
    for i in machines_ip_array:
        if i['name']:
            machines_mirror.append(f"{machines_ip_array.index(i)}     {i['name']}     [ {i['ip']} ]")

    return machines_ip_array, machines_mirror

def checking_folders():
    """ 
    Создание/проверка директорий
    """
    if os.path.isdir(DATA_PATH) == False:
        os.mkdir(DATA_PATH)

    if os.path.isdir(DATA_PATH + "/vnc") == False:
        os.mkdir(DATA_PATH + "/vnc")

    if not os.path.exists(DATA_PATH + '/recent.txt'):
    	with open(DATA_PATH + '/recent.txt', 'w', encoding='utf-8') as file:
    		file.write('')

def popup_message(msgtype, title, message, details=''):
    """
    Вывод всплывающего окна с сообщением. 
    Выводит в формате RichText, так что можно использовать
    html разметку
    """
    msg_type_map = {
        'error': QtWidgets.QMessageBox.Critical,
        'info': QtWidgets.QMessageBox.Information,
        'question': QtWidgets.QMessageBox.Question,
        'default': QtWidgets.QMessageBox.NoIcon,
    }
    
    msgBox = QtWidgets.QMessageBox()
    msgBox.setTextFormat(QtCore.Qt.RichText)
    msgBox.setIcon(msg_type_map.get(msgtype, msg_type_map['default']))
    msgBox.setWindowTitle(title)
    msgBox.setWindowIcon(QtGui.QIcon(ICON_PATH))
    msgBox.setText(message)
    
    if details.strip():
        msgBox.setDetailedText(details)
    
    if msgtype == 'question':
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.button(QtWidgets.QMessageBox.Yes).setText('Да')
        msgBox.button(QtWidgets.QMessageBox.No).setText('Нет')
    elif msgtype == 'error':
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBox.button(QtWidgets.QMessageBox.Cancel).setText('Отмена')
    else:
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    
    return msgBox.exec_() in [QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.Ok]

def notify(title, text):
    """
    Вывод уведомления через стандартные пути ОС
    """
    notification = Notify()
    notification.title = title
    notification.message = text
    notification.icon = ICO_PATH
    notification.send()

def recent_connections(ip):
    """
    Добавление в журнал recent.txt ip адреса,
    имени хоста и даты подключения
    """

    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    with open(config_values.get('recent_connections_journal_path'), 'r+', encoding='utf-8') as file:
        f = file.read()
        file.seek(0)

        file.write(f"[{now}] {ip} \n{f}")

def config_check(): 
    """
    Проверяет наличие конфигурационного файла
    и создает его при необходимости, 
    наполняя дефолтными значениями
    """

    if not os.path.exists(CONFIG_PATH):
        # Присваивание значений в зависимости от типа ОС
        terminal = 'cmd' if WINDOWS else 'fly-term'
        editor = 'notepad.exe' if WINDOWS else 'kate'
        vnc_path = '/vnc/vnc.exe' if WINDOWS else '/vnc/vnc'
        rdp_connect_cmd = 'start mstsc /console /v:' if WINDOWS else 'remmina --no-tray-icon -c rdp://'
        ssh_connect_string = 'cmd.exe /K ssh' if WINDOWS else 'fly-term -e ssh'
        ping_command_string = 'cmd.exe /K ping -c' if WINDOWS else 'fly-term -e ping -c'
        bemg_web_open = 'start https:/192.168.0.1:8000/bemg/' if WINDOWS else 'firefox https://192.168.0.1:8000/bemg/'

        default_config = (
            '[DEFAULT]\n\n'
            '; Предупреждать об отсутствии программы VNC при запуске\n'
            'vnc_exist_notify=yes\n\n'
            '; Предварительно поднимать VNC сервер (через SSH) перед подключением по VNC\n'
            'vnc_up=yes\n\n'
            '; Спрашивать о сохранении подключения\n'
            'save_connection=no\n\n'
            '; Путь до журнала последних соединений\n'
            'recent_connections_journal_path=/recent.txt\n\n'
            '; Путь до терминала\n'
            f'terminal={terminal}\n\n'
            '; Редактор по умолчанию\n'
            f'editor={editor}\n\n'          
            '; Количество запросов для пинга\n'
            'ping_count=16\n\n'
            '; Путь до приложения VNC\n'
            f'vnc_path={vnc_path}\n\n'
            '; Команда для поднятия VNC\n'
            '; Приложение подключается через ssh к удаленному компьютеру\n'
            '; И запускает скрипт поднятия VNC сервера\n'
            '; Скрипт vncup кастомный, можете написать свой или скопировать из репозитория\n'
            'vncs_up=if test -f /corp/scripts/vncup; then sudo /corp/scripts/vncup; else x11vnc -display :0; fi\n\n'
            '; Логин и порт по умолчанию для paramiko и SSH\n'
            '; Пароль не указан из соображений безопасности\n'
            '; Хотя понимаю, что это может быть удобным, поэтому используйте на свой страх и риск\n'
            'ssh_default_login=admin\n'
            'ssh_default_port=22\n'
            'ssh_default_password=\n\n'
            '; Команда для подключения по RDP\n'
            f'rdp_connect_cmd={rdp_connect_cmd}\n\n'
            '; Путь до файла БД где хранятся сохраненные адреса\n'
            'ips_path=/db.json\n\n'
            '; Альтернативный файл БД\n'
            'ips_accessorius_path=/db2.json\n\n'
            '; Значение по умолчанию для вставки в поле ввода\n'
            'ip_insert_value=192.168.0.\n\n'
            '; Настройка сохраненных подсетей(кнопки над полем ввода ip адреса)\n'
            '; mp_*_name - это название на самой кнопке, mp_*_value - это значение которое будет вставлено в поле ввода\n'
            '; Не используйте имя длиной более 4 символов, иначе текст не поместится\n'
            '; Например: имя ".32" будет отлично отражать суть кнопки. Так вы сможете понять на какую подсеть вы сможете переключиться\n'
            '; Для mp_*_value пропишите, например, "192.168.32."\n\n'
            'mp_1_name=0\n'
            'mp_1_value=192.168.0.\n'
            'mp_2_name=1\n'
            'mp_2_value=192.168.1.\n'
            'mp_3_name=2\n'
            'mp_3_value=192.168.2.\n'
            'mp_4_name=3\n'
            'mp_4_value=192.168.3.\n'
            'mp_5_name=4\n'
            'mp_5_value=192.168.4.\n'
            'mp_6_name=5\n'
            'mp_6_value=192.168.5.\n'
            'mp_7_name=6\n'
            'mp_7_value=192.168.6.\n'
            'mp_8_name=7\n'
            'mp_8_value=192.168.7.\n'
            'mp_9_name=8\n'
            'mp_9_value=192.168.8.\n'
            'mp_10_name=9\n'
            'mp_10_value=192.168.9.\n\n'
            '; Горячие клавиши для отправки команд удаленному компьютеру\n'
            '; Команда вывода на дисплей сообщения о подключении админа\n'
            '; Является кастомной командой, логику указываете исходя из\n'
            '; инраструктуры вашей организации. Пример в дефолтном значении \n'
            'admin_alert=export DISPLAY=:0; if test -f /usr/share/rcapp/admin_connected.jpg; then gwenview -f /usr/share/rcapp/admin_connected.jpg; else ristretto /usr/share/images/admin_connected.jpg -f; fi\n\n'
            '; Параметры для подключения по ssh через терминал\n'
            f'ssh_connect_string={ssh_connect_string}\n\n'
            '; Команда для пинга через указанный терминал\n'
            f'ping_command_string={ping_command_string}\n\n'
            '; Открытие машины в BEMG web\n'
            '; Так как в моем учреждении использовался написанной мной приложение BEMG\n'
            '; Эта кнопка было добавлена для удобства открытия страницы машины в самом BEMG\n'
            '; Подробнее про BEMG на моем гитхаб: https://github.com/lyintsec/bemg\n'
            f'bemg_web_open={bemg_web_open}\n\n'
            '; Кастомные команды\n'
            '; Сюда пишете любые команды которые хотите привязать к этим кнопкам\n'
            '; Например, открытие файловой шары\n'
            'custom_command_1=start explorer.exe\n'
            'custom_command_2=\n'
            'custom_command_3=\n'
            'custom_command_4=\n'
        )

        with open(CONFIG_PATH, 'w', encoding='utf-8') as cfgfile:
            cfgfile.write(default_config)

def load_config(data_path):
    """
    Загрузка значений из конфигурационного файла
    в глобальный словарь config_values.
    В нем хранятся все переменные использующиеся
    в этом приложении
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf8") # Чтение кофигурационного файла

    try:

        # Автоматический сбор значений из конфигурационного файла
        config_section = config['DEFAULT']
        config_values = {}
        for i in config_section:
            config_values[i] = config_section[i]

        # Правка некоторых значений из конфига
        config_values['recent_connections_journal_path'] = data_path + config['DEFAULT']['recent_connections_journal_path']
        config_values['vnc_path'] = data_path + config['DEFAULT']['vnc_path']
        config_values['ips_path'] = data_path + config['DEFAULT']['ips_path']
        config_values['ips_accessorius_path'] = data_path + config['DEFAULT']['ips_accessorius_path']

        # Собираем в одну строчку всю команду для вызова пинга
        config_values['ping_cmd_app_path'] = (
            f"start {config_values.get('terminal')} /c ping -n {config_values.get('ping_count')} " 
            if WINDOWS else 
            f"{config_values.get('terminal')} {config_values.get('ping_command_string')} {config_values.get('ping_count')} "
        )

        # Собираем в одну строчку всю команду для вызова терминала
        config_values['start_terminal'] = (
            f"start {config_values.get('terminal')}"
            if WINDOWS else
            f"{config_values.get('terminal')}"
        )

        # Собираем в одну строчку всю команду для вызова ssh
        config_values['start_ssh'] = (
            f"start {config_values.get('ssh_connect_string')}"
            if WINDOWS else
            f"{config_values.get('ssh_connect_string')}"
        )

        if not os.path.exists(config_values.get('vnc_path')) and config_values.get('vnc_exist_notify') == 'yes':
            popup_message(
                'info', 
                'Ошибка',
                (
                    'Похоже, отсутсвует программа vnc.<br>'
                    'Скачайте с сайта RealVNC Standalone Viewer<br>'
                    '<a href="https://www.realvnc.com/en/connect/download/viewer/">https://www.realvnc.com/en/connect/download/viewer/</a><br>'
                    'назовите его vnc.exe (или просто vnc для linux) и положите в папку data/vnc'
                )
            )

        if not WINDOWS:
            try:
                os.system(f"chmod +x {config_values.get('vnc_path')}") # Назначаем права на запуск vnc в linux
            except:
                pass                

    except KeyError: # Если есть ошибки в файле конфигурации
        # Переименование сломанного конфигурационного файла с сохранением старых значений
        now = datetime.datetime.now().strftime('%d%m%Y%H%M%S')
        backup_filename = f"config.backup_{now}.cfg"
        backup_path = os.path.join(DATA_PATH, backup_filename)
        os.rename(CONFIG_PATH, backup_path)

        popup_message(
            'info',
            'Внимание',
            (                
                'Ваш файл конфигурации был восстановлен на значения по умолчанию из-за ошибки в синтаксисе.<br><br>'
                'Ваши старые настройки находятся в папке /data/ под названием config.backup_(датавремя).cfg<br><br>'
                'Вы можете исправить ошибку и переименовать файл обратно в config.cfg<br><br>'
                'Примечание: Ошибка скорее всего связана с неправильным названием ключа '
                '(например вместо "mp_1_value" -> "mp_1_valu") или его отсутствием.<br><br>'
                'Для восстановления старых настроек, сравните текущий config.cfg и ваш старый конфиг, '
                'исправьте ошибку и перезапустите приложение.'
            )
        )

        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

    return config_values

def add_new_record(ip):
    """
    Функция добавления в текстовую БД
    ip адрес который вы хотите сохранить
    """
    global machines_mirror
    global machines_ip_array
    global current_db

    # Чтение db.json файла
    with open(current_db, "r", encoding='utf-8') as f:
        ip_array = json.load(f)
        machines_ip_array = ip_array["machines"]

    # Создание списка IP-адресов
        temp_ip_list = [machine['ip'] for machine in machines_ip_array]
    
    # Проверка уникальности IP-адреса
    ip_not_found = ip not in temp_ip_list

    if ip_not_found:
        # Чтение конфига и просмотр состояния save_connection
        if config_values.get('save_connection') == 'no':    
            answer = True # Если стоит "не спрашивать", то идем дальше
        else:
            answer = popup_message(
                'question', 
                'Добавить запись?', 
                'Этого ip нет в списке сохраненных.\nДобавить его в список?'
            )

        if answer == True:
            name, ok = QtWidgets.QInputDialog.getText(main_window, 'Ввод имени', 'Введите имя компьютера (можно по русски для удобства)')

            # Если кликнули ок и ввели имя
            if ok and name:
                try:
                    # Чтение существующих данных в db.json
                    with open(current_db, "r", encoding='utf-8') as file:
                        json_db_file = json.load(file)
                        machines = json_db_file["machines"]

                        # Сбор уникальных значений имен из файла
                        unique_names = [i['name'] for i in machines if i['name']]

                    # Проверка на уникальность имени    
                    if name.upper() not in unique_names:
                        new_record = {'name': name.upper(), 'ip': ip}
                        machines.append(new_record)

                        # Запись новых данных во временный файл
                        with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', dir=DATA_PATH) as temp_file:
                            json.dump(json_db_file, temp_file, indent=4, ensure_ascii=False)
                            temp_file_name = temp_file.name

                        # Замена оригинального файла временным
                        os.replace(temp_file_name, current_db)                        
                    else:
                        name_error = popup_message('info', 'Ошибка', 'Это имя уже занято!')
                        if name_error == True:
                            add_new_record(ip)
                except Exception as e:
                    # Обработка ошибок, если необходимо
                    print(f"Возникла ошибка: {e}")
                    if 'temp_file_name' in locals():
                        os.remove(temp_file_name)
                        
                # Обновляем комбобокс в ui
                machines_ip_array, machines_mirror = db_open(current_db)
                ui.comboBoxAdresses.clear()
                ui.comboBoxAdresses.addItems(machines_mirror)
            elif ok and not name:
                warning = popup_message('info', 'Ошибка', 'Поле не может быть пустым!')
                if warning == True:
                    add_new_record(ip)
            else:
                pass
        else:
            pass       
    else:
        popup_message('warning', 'Ошибка', 'Этот айпи уже есть в списке!')

def transform_menuline_to_ip(menuLine):
    """
    Функция перевода строчки из выпадающего списка
    в адрес для подключения
    """
    machines_ip_array, machines_mirror = db_open(current_db)
    item_index = menuLine[0:3]        
    inscribed_ip = machines_ip_array[int(item_index.strip())]
    menu_ip = inscribed_ip["ip"]

    return menu_ip

def hot_buttons(cmd, mp_value=''):
    """
    Функции обработки горячих клавиш. 
    Аргумент mp_value только для доавбления 
    сохраненных подсетей
    """
    if cmd == 'subnet_change': # Смена подсети через корчие клавиши (кнопки)
        ui.directInputLine.setText(mp_value)
        ui.directInputLine.setFocus() # Установка фокуса на строке ввода адреса
    elif cmd == 'ub_txt': # Открытие блокнота
        subprocess.Popen(config_values.get('editor'))
    elif cmd == 'terminal':
        try:
            os.system(config_values.get('start_terminal'))
        except Exception as e:
            popup_message('error', 'Ошибка', e)
    elif cmd == 'custom_cmd': # Запуск одной из 4 кастомных команд
        if mp_value == "":
            notify(APP_TITLE, "Команда не заполнена в конфиге. Выполнять нечего")
        try:
            os.system(mp_value)
        except Exception as e:
            popup_message('error', 'Ошибка', e)

# Создание/проверка директорий для исключения дальнейших ошибок
checking_folders()

# Проверка конфигурации
config_check() # Проверяет наличие конфигурации и создает, если config.cfg отсутствует

# Чтение файла конфигурации
config_values = load_config(DATA_PATH) # Наполнение глобального словаря значениями из файла конфигурации

# Объявление текущей БД, используется в некоторых функциях
# Например для переключение на альтернативную БД\
global current_db
current_db = config_values.get('ips_path')

# Открытие текстовой БД и создание списка machines_mirror
machines_ip_array, machines_mirror = db_open(current_db)