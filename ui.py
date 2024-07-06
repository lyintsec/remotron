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

import sys

from PyQt5 import QtGui, QtWidgets

from gui import Ui_MainWindow
from settings import APP_TITLE, ICON_PATH

# Создание QApplication
app = QtWidgets.QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True) # Для завершения приложения при закрытии последнего окна
main_window = QtWidgets.QMainWindow() # Создание QMainWindow

# Инициализация ui
ui = Ui_MainWindow() 
ui.setupUi(main_window)
main_window.setWindowTitle(APP_TITLE)
icon = QtGui.QIcon()
icon.addPixmap(QtGui.QPixmap(ICON_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)
main_window.setWindowIcon(icon)
main_window.show()


