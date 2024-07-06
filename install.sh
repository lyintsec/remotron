#!/bin/bash

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

if [ -z "$1" ] || [ -z "$2" ]
then
printf "Если вы хотите установить pip пакеты через прокси, то запускайте так:\n"
printf 'bash ./install.sh --proxy "http://<адресс_прокси>:3128"\n\n'
else
echo "Используется прокси $2 для установки пакетов"
fi

# Проверка установки Python
if ! command -v python3 &> /dev/null
then
    echo "Python не установлен. Пожалуйста, установите Python и попробуйте снова."
    exit 1
fi

# Проверка установки pip
if ! python3 -m pip --version &> /dev/null
then
    echo "pip не установлен. Пожалуйста, установите pip и попробуйте снова."
    exit 1
fi

# Проверка установки модуля venv
if ! python3 -m venv --help &> /dev/null
then
    echo "Модуль venv не установлен. Пожалуйста, установите Python с поддержкой venv и попробуйте снова."
    exit 1
fi

# Создание виртуального окружения
echo "Создание виртуального окружения..."
if ! python3 -m venv env
then
    echo "Произошла ошибка при создании виртуального окружения."
    exit 1
fi

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source env/bin/activate

# Обновление pip
if [ ! -z "$1" ] && [ ! -z "$2" ]
then
    echo "Обновление pip через прокси $2..."
    if ! python3 -m pip install --upgrade pip $2 $3 &> /dev/null
    then
        echo "Ошибка обновления pip через прокси. Пропуск..."
    fi
else
    echo "Обновление pip..."
    if ! python3 -m pip install --upgrade pip &> /dev/null
    then
        echo "Ошибка обновления pip. Пропуск..."
    fi
fi


# Установка зависимостей
if [ ! -z "$1" ] && [ ! -z "$2" ]
then
    echo "Установка зависимостей через прокси $2..."
    if ! python3 -m pip install -r requirements.txt &> /dev/null
    then
        echo "Произошла ошибка при установке зависимостей через прокси."
        exit 1
    fi
else
    echo "Установка зависимостей..."
    if ! python3 -m pip install -r requirements.txt &> /dev/null
    then
        echo "Произошла ошибка при установке зависимостей."
        exit 1
    fi
fi

# Упаковка приложения с помощью pyinstaller
echo "Упаковка приложения с использованием pyinstaller..."
if ! pyinstaller --noconfirm --onedir --windowed --log-level=ERROR --icon "data/remotron.ico" --name "Remotron" --clean --add-data "data:data/" "main.py"
then
    echo "Произошла ошибка при упаковке приложения."
    exit 1
fi

# Удаление папки build и файла .spec
rm -rf "$SCRIPT_DIR/build"
rm -f "$SCRIPT_DIR/Remotron.spec"

echo "Все зависимости установлены, и приложение успешно упаковано."
echo "Упакованное приложение находится в папке dist."

exit 0
