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
import time
import subprocess
import socket

import paramiko
from pythonping import ping
from PyQt5 import QtWidgets

from ui import main_window
from utils import notify, popup_message, recent_connections, \
    add_new_record
from utils import config_values, ui
from settings import WINDOWS, APP_TITLE

# Функции подключения к удаленной машине
def connect(inscribed_ip, view_only_flag_status):
    """
    Функция подключения по VNC. Написана специально для программы RealVNC. Работает только с ней
    потому что с ней удобно передавать флаг "view only" и она бесплатна.

    Принимает 2 аргумента: адрес к которому вы хотите подключиться и view_only_flag_status (подключение в режиме "только просмотр") 

    До подключения по VNC, функция подключается через paramiko SSH
    и запускает на удаленной машине vnc на дисплее :0
    Это сделано, на случай если вы не хотите держать включенными 
    сервера VNC на удаленных машинах, что в целом увеличивает безопасность инфраструктуры.
    Если удаленный хост на винде, то он пропускает подключение по SSH.
    """

    # Проверка присутствия программы vnc
    if not os.path.exists(config_values.get('vnc_path')):
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
        return 1

    def up_vnc_server(inscribed_ip):
        """
        Поднимает на удаленном linux хосте vnc сервер
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=inscribed_ip, username=ui.sshAuthLoginInput.text(), password=ui.sshAuthPasswordInput.text(), port=ui.sshAuthPortInput.text(), timeout=2)
            channel = client.invoke_shell()
            channel.send(f"{config_values.get('vncs_up')}\n") # команда поднятия vnc сервера
            return True
        except Exception as e:
            notify("Ошибка",e)
    
    # Аргументы для подключения по RealVNC в режиме "только просмотр"
    VOA_1 = "SendPointerEvents=false"
    VOA_2 = "SendKeyEvents=false"
    VOA_3 = "SendMediaKeys=false"
    VOA_4 = "SendSpecialKeys=false"
    VOA_5 = "WarnUnencrypted=false"

    view_only_key = view_only_flag_status

    if config_values.get('vnc_up') == 'yes':    
        up_vnc_server(inscribed_ip) # поднимает удаленный vnc сервер, если в конфиге указано vnc_up=yes

    if view_only_key: # Если в режиме "только просмотр"
        if WINDOWS:
            subprocess.Popen([config_values.get('vnc_path'), VOA_1, VOA_2, VOA_3, VOA_4, VOA_5, inscribed_ip])
        else: # На linux синтаксис вызова немного отличается
            time.sleep(2) # Даем немного времени дойти пакетам до машины на linux
            subprocess.Popen([config_values.get('vnc_path'), inscribed_ip, VOA_1, VOA_2, VOA_5])
            time.sleep(2) # Хотелось бы без этого, но тесты показали что это необходимо
    else:
        subprocess.Popen([config_values.get('vnc_path'), VOA_5, inscribed_ip])

def ping_cmd(inscribed_ip):
    """
    Запуск пинга до удаленного хоста в новом терминале
    """
    if inscribed_ip.strip() == '':
        popup_message('info', 'Ошибка', 'Что, забыл ввести ip?')
    elif inscribed_ip == config_values.get('ip_insert_value'):
        error_str = f'Ты ввел такой вот IP: {inscribed_ip}'
        popup_message('info', 'Ошибка',  f'{error_str}<br>Может потрудишься и дополнишь адрес?')
    else:
        try:
            os.system(config_values.get('ping_cmd_app_path') + inscribed_ip)
        except Exception as e:
            popup_message('error', 'Ошибка', e)

def ssh_connect(inscribed_ip):
    """
    Функция подключения к удаленной машине по SSH
    """
    try:
        os.system(f"{config_values.get('start_ssh')} {ui.sshAuthLoginInput.text()}@{inscribed_ip} -p {ui.sshAuthPortInput.text()}")
    except Exception as e:
        popup_message('error', 'Ошибка', e)

def send_admin_notify_cmd(inscribed_ip):
    """
    Отправка команды для открытия картинки
    "Внимание, к вам подключился администратор"
    """
    admin_notify_cmd = config_values.get('admin_alert')
    try:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=inscribed_ip, username=ui.sshAuthLoginInput.text(), password=ui.sshAuthPasswordInput.text(), port=ui.sshAuthPortInput.text(), timeout=1)
            stdin, stdout, stderr = (client.exec_command(admin_notify_cmd))
            notify(APP_TITLE, f'Команда {admin_notify_cmd} успешно отправлена')
        except Exception as e:
            notify("Ошибка", e)
    except Exception as e:
        popup_message(
            'error',
            'Ошибка',
            (
                f'Невозможно подключиться к машине по SSH что бы отправить сообщение.<br>'
                'Возможно на ней ОС Windows или SSH сервер не установлен.<br>'
                'Подробно: {e}'
            )
            
        )    

def send_custom_command(inscribed_ip):
    """
    Отправка команды на удаленный компьютер через ssh
    Например: отправка команды для открытия картинки
    "Внимание, к вам подключился администратор"
    """
    cmd, ok = QtWidgets.QInputDialog.getMultiLineText(
        main_window, 
        'Введите комманду', 
            (
                'Эта фича отправляет вашу команду через SSH и выполняет ее на удаленной машине.\n'
                'Можно отправить любую команду, которую "скушает" машина через SSH.\n'
                'Ответа не ждите'
            )
        )
    if cmd and ok:
        try:
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=inscribed_ip, username=ui.sshAuthLoginInput.text(), password=ui.sshAuthPasswordInput.text(), port=ui.sshAuthPortInput.text(), timeout=1)
                stdin, stdout, stderr = (client.exec_command(cmd))
                notify(APP_TITLE, f'Команда {cmd} успешно отправлена')
            except Exception as e:
                notify(
                    "Неправильный логин/пароль или это винда", 
                    f"Не удалось подключиться по ssh. Неправильно указан логин/пароль в SSH AUTH или хост на винде. Ошибка: {e}"
                )
        except Exception as e:
            popup_message(
                'error',
                'Ошибка',
                (
                    f'Невозможно подключиться к машине по SSH что бы отправить сообщение.<br>'
                    'Возможно на ней ОС Windows или SSH сервер не установлен.<br>'
                    'Подробно: {e}'
                )
                
            )
    elif not cmd and ok:
        user_answer = popup_message(
            'error', 
            'Ошибка', 
            'Напишите свою команду'
        )
        if user_answer:
            send_custom_command(inscribed_ip)
    else:
        pass

# Функции валидации предоставленного адреса
def ip_validation(ip):
    """
    Функция проверки валидности ip адреса
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def general_validation(ip='', cmd='', view_only_flag=False):
    """
    Главная функция валидации содержимого строки ввода адреса
    После проверки валидности, функция вызывает нужную функцию подключения
    Например, ssh или vnc.
    view_only_flag - это view only flag
    mw - это  main_window = QtWidgets.QMainWindow()
    """
    
    no_signal = 'Похоже, что "абонент не абонент"'

    def start_cmd():
        """
        Функция запуска нужного подключения к удаленной машине
        """
        if cmd == 'vnc':
            connect(ip, view_only_flag)
        elif cmd == 'ssh':
            ssh_connect(ip)
        elif cmd == 'rdp':
            os.system(f"{config_values.get('rdp_connect_cmd')}{ip}")
        elif cmd == 'cmd':
            send_custom_command(ip)
        elif cmd == 'send_admin_notify':
            send_admin_notify_cmd(ip)

        recent_connections(ip) # Добавление в журнал недавних подключений

    def connect_to_machine():
        """
        Функция подключения к удаленной машине
        """               
        status_check = ping(ip, verbose=False, timeout=0.2).success() if WINDOWS else True # Проверка доступности до начала подключения только для Windows

        if config_values.get('save_connection') == 'yes': # Если в конфиге указано "спрашивать о сохранении подключения"
            add_new_record(ip)

        if status_check:
            start_cmd()
        else:
            question = popup_message('question', no_signal, 'Все равно попробовать подключиться?')
            if question == True:
                start_cmd()
            else:
                pass
        
    if ip.strip("1234567890. ") == "": # Если представлен ip адрес а не hostname
        ip = ip.strip()
        error_str = f'Ты ввел такой вот IP: {ip}'

        if ip == '':
            popup_message('info', 'Ошибка', 'Что, забыл ввести ip или hostname?')
            return False

        elif ip == config_values.get('ip_insert_value'):
            popup_message('info', 'Ошибка', f'{error_str}<br>Может потрудишься и дополнишь адрес?')
            return False

        elif ip_validation(ip) == False:
            popup_message('info', 'Ошибка', f'{error_str}<br>Ничего не смущает?')
            return False
    
    try:
        connect_to_machine()
    except Exception as e:
        popup_message('info', 'Ошибка', f'Ошибка: {e}')
        return False
    
    return True
