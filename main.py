############################################################################
#
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

"""
Проект: Remotron
Автор: lyintSec
Github: https://github.com/lyintsec/remotron
Версия: 2.2
Дата обновления: 06 июля 2024
Описание: Программа удаленного подключения, многофункциональный командный центр сочетающий в себе
удобное окно с полем ввода ip или hostname и кнопками подключения по vnc, ssh, rdp и др.

Зависимости:
PyQt5==5.15.10
paramiko==3.4.0
pythonping==1.1.4
pyperclip==1.9.0
notify-py==0.3.43
pyinstaller==6.8.0

Структура:
main.py - главный файл для запуска приложения
settings.py - настройки приложения
gui.py - GUI из PyQt5, содержащий графический интерфейс
ui.py - инициализация UI прилоежния
utils.py - служебные функции используемые приложением
connect.py - функции подключения к удаленной машине и валидации введенного адреса
resource_rc.py - Ресурсы PyQt5 (фоновое изображение)

Автоустановка:
Windows - install.bat/install.ps1
Linux - install.sh

Упаковонное исполняемое приложение после установки будет находиться в папке dist.
"""

# Импорт стандартных библиотек
import os
import sys
import subprocess

# Импорт сторонних пакетов
from PyQt5 import QtGui, QtWidgets

# Импорт локальных модулей
from ui import app, main_window, ui
from settings import APP_NAME, VERSION, NEWS, \
    CONFIG_PATH, RELEASE_DATE, DEVELOPER_FULL
from utils import popup_message, db_switch, hot_buttons, \
    transform_menuline_to_ip
from utils import config_values, ui, machines_mirror
from connect import ping_cmd, general_validation, add_new_record

# Запуск GUI
if __name__ == "__main__":      
    
    # Установка фокуса на строку ввода адреса
    ui.directInputLine.setFocus()

    # Заполенения левого блока авторизации SSH
    ui.sshAuthLoginInput.setText(config_values.get('ssh_default_login'))
    ui.sshAuthPasswordInput.setText(config_values.get('ssh_default_password'))
    ui.sshAuthPortInput.setText(config_values.get('ssh_default_port'))

    # Чекбокс "только просмотр"
    view_only_flag = False

    def view_only_state_change():
        global view_only_flag

        if view_only_flag == True: # Если было True
            view_only_flag = False # Ставим False
        else: # И наоборот
            view_only_flag = True

    # При клике на чекбокс
    ui.checkboxViewOnly.stateChanged.connect(view_only_state_change)

    # Установка начального значения из конфига
    hot_buttons('subnet_change', config_values.get('ip_insert_value'))

    # Обработка нажатий горячих клавишь на клавиатуре 
    shortcut_returnKey = QtWidgets.QShortcut(QtGui.QKeySequence("Return"), main_window) # VNC при нажатии на главный Return
    shortcut_returnKey.activated.connect(lambda: general_validation(ip=ui.directInputLine.text(), cmd='vnc', view_only_flag=view_only_flag))

    shortcut_enterKey = QtWidgets.QShortcut(QtGui.QKeySequence("Enter"), main_window) # VNC при нажатии на главный Enter
    shortcut_enterKey.activated.connect(lambda: general_validation(ip=ui.directInputLine.text(), cmd='vnc', view_only_flag=view_only_flag))

    shortcut_f5Key = QtWidgets.QShortcut(QtGui.QKeySequence("F5"), main_window) # F5 для перезапуска приложения
    shortcut_f5Key.activated.connect(lambda: os.execl(sys.executable, os.path.abspath(__file__), *sys.argv))

    shortcut_escKey = QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), main_window) # Esc для закрытия приложения
    shortcut_escKey.activated.connect(lambda: sys.exit())

    shortcut_f1Key = QtWidgets.QShortcut(QtGui.QKeySequence("F1"), main_window) # F1 для вызова помощи
    shortcut_f1Key.activated.connect(lambda: popup_message('info', f'{APP_NAME}{VERSION}', f'{NEWS}'))

    shortcut_f2Key = QtWidgets.QShortcut(QtGui.QKeySequence("F2"), main_window) # F2 для отправки команды "К вам подключился администратор"
    shortcut_f2Key.activated.connect(lambda: general_validation(ip=ui.directInputLine.text(), cmd="send_admin_notify"))

    shortcut_ctrl1Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+1"), main_window) # CTRL+1 смена подсети
    shortcut_ctrl1Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_1_value')))

    shortcut_ctrl2Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+2"), main_window) # CTRL+2 смена подсети
    shortcut_ctrl2Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_2_value')))

    shortcut_ctrl3Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+3"), main_window) # CTRL+3 смена подсети
    shortcut_ctrl3Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_3_value')))

    shortcut_ctrl4Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+4"), main_window) # CTRL+4 смена подсети
    shortcut_ctrl4Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_4_value')))

    shortcut_ctrl5Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+5"), main_window) # CTRL+5 смена подсети
    shortcut_ctrl5Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_5_value')))

    shortcut_ctrl6Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+6"), main_window) # CTRL+6 смена подсети
    shortcut_ctrl6Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_6_value')))

    shortcut_ctrl7Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+7"), main_window) # CTRL+7 смена подсети
    shortcut_ctrl7Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_7_value')))

    shortcut_ctrl8Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+8"), main_window) # CTRL+8 смена подсети
    shortcut_ctrl8Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_8_value')))

    shortcut_ctrl9Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+9"), main_window) # CTRL+9 смена подсети
    shortcut_ctrl9Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_9_value')))

    shortcut_ctrl10Key = QtWidgets.QShortcut(QtGui.QKeySequence("CTRL+0"), main_window) # CTRL+0 смена подсети
    shortcut_ctrl10Key.activated.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_10_value')))

    # При клике: сохранение адреса в БД введенного в строку подключения
    ui.saveAdressesButton.clicked.connect(lambda: add_new_record(ip=ui.directInputLine.text()))

    # При клике: смена на альтернативную БД
    ui.switchDatabaseButton.clicked.connect(lambda: db_switch())

    # При клике: изменение текстового файла БД с сохраненными адресами 
    # Что бы получить текущую выбранную БД вызывает db_switch с аргументом test=True
    ui.editAdressesButton.clicked.connect(lambda: subprocess.Popen([config_values.get('editor'), db_switch(test=True)]))

    # Обработка выпадающего меню 
    ui.comboBoxAdresses.clear() # Очистка при запуске
    ui.comboBoxAdresses.addItems(machines_mirror) # Добавление удобочитаемого списка сохраненных адресов machines_mirror из функции db_open

    # При клике: добавление адреса из выпадающего списка в строку введения адреса
    ui.comboBoxAdresses.activated.connect( 
        lambda: ui.directInputLine.setText(
            transform_menuline_to_ip(ui.comboBoxAdresses.currentText())
        )
    )

    # Добавление подписей на кнопки быстрого переключения подсети
    ui.quickSubnetChange1.setText(config_values.get('mp_1_name'))
    ui.quickSubnetChange2.setText(config_values.get('mp_2_name'))
    ui.quickSubnetChange3.setText(config_values.get('mp_3_name'))
    ui.quickSubnetChange4.setText(config_values.get('mp_4_name'))
    ui.quickSubnetChange5.setText(config_values.get('mp_5_name'))
    ui.quickSubnetChange6.setText(config_values.get('mp_6_name'))
    ui.quickSubnetChange7.setText(config_values.get('mp_7_name'))
    ui.quickSubnetChange8.setText(config_values.get('mp_8_name'))
    ui.quickSubnetChange9.setText(config_values.get('mp_9_name'))
    ui.quickSubnetChange10.setText(config_values.get('mp_10_name'))

    # При клике: быстрая смена подсети
    ui.quickSubnetChange1.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_1_value')))
    ui.quickSubnetChange2.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_2_value')))
    ui.quickSubnetChange3.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_3_value')))
    ui.quickSubnetChange4.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_4_value')))
    ui.quickSubnetChange5.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_5_value')))
    ui.quickSubnetChange6.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_6_value')))
    ui.quickSubnetChange7.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_7_value')))
    ui.quickSubnetChange8.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_8_value')))
    ui.quickSubnetChange9.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_9_value')))
    ui.quickSubnetChange10.clicked.connect(lambda: hot_buttons('subnet_change', config_values.get('mp_10_value')))

    # При клике: запуск одной из 4 кастомных фукнций
    ui.customUserCommand1.clicked.connect(lambda: hot_buttons('custom_cmd', config_values.get('custom_command_1')))
    ui.customUserCommand2.clicked.connect(lambda: hot_buttons('custom_cmd', config_values.get('custom_command_2')))
    ui.customUserCommand3.clicked.connect(lambda: hot_buttons('custom_cmd', config_values.get('custom_command_3')))
    ui.customUserCommand4.clicked.connect(lambda: hot_buttons('custom_cmd', config_values.get('custom_command_4')))

    # Главные (большие в центре) кнопки подключения к удаленной машине
    ui.vncButton.clicked.connect(lambda: general_validation(ip=ui.directInputLine.text(), cmd='vnc', view_only_flag=view_only_flag)) # VNC
    ui.sshButton.clicked.connect(lambda: general_validation(ip=ui.directInputLine.text(), cmd='ssh')) # SSH
    ui.rdpButton.clicked.connect(lambda: general_validation(ip=ui.directInputLine.text(), cmd='rdp')) # RDP
    ui.customCommandButton.clicked.connect(lambda: general_validation(ip=ui.directInputLine.text(), cmd='cmd')) # Отправка кастомнок команды
    ui.adminAlertButton.clicked.connect(lambda: general_validation(ip=ui.directInputLine.text(), cmd="send_admin_notify")) # Отправка уведомления от администратора    

    # При клике: редактирование конфигурационного файла
    ui.settingsButton.clicked.connect(lambda: subprocess.Popen([config_values.get('editor'), CONFIG_PATH]))

    # При клике: открытие журнала недавних подключений
    ui.recentButton.clicked.connect(lambda: subprocess.Popen([config_values.get('editor'), config_values.get('recent_connections_journal_path')]))

    ui.notepadButton.clicked.connect(lambda: hot_buttons('ub_txt')) # Открытие блокнота
    ui.terminalButton.clicked.connect(lambda: hot_buttons('terminal')) # Открытие терминала
    ui.pingButton.clicked.connect(lambda: ping_cmd(ui.directInputLine.text())) # Запуск пинга до удаленной машины

    # Кнопка помощи снизу
    ui.bottomInfoButton.setText(f'{VERSION} {RELEASE_DATE} {DEVELOPER_FULL}')
    ui.bottomInfoButton.clicked.connect(lambda: popup_message('info', f'{APP_NAME}{VERSION}', f'{NEWS}'))

    # Запуск приложения
    sys.exit(app.exec_())
