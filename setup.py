#!/usr/bin/env python3
"""
Скрипт для быстрой настройки проекта воронки
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ошибка:")
        print(f"   {e.stderr}")
        return False


def check_python_version():
    """Проверяет версию Python"""
    print("🐍 Проверяем версию Python...")
    if sys.version_info < (3, 7):
        print("❌ Требуется Python 3.7 или выше")
        print(f"   Текущая версия: {sys.version}")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]} - подходит")
        return True


def install_requirements():
    """Устанавливает зависимости"""
    if not Path("requirements.txt").exists():
        print("❌ Файл requirements.txt не найден")
        return False
    
    return run_command("pip install -r requirements.txt", "Установка зависимостей")


def create_env_file():
    """Создает файл .env"""
    if Path(".env").exists():
        print("✅ Файл .env уже существует")
        return True
    
    if not Path("env.example").exists():
        print("❌ Файл env.example не найден")
        return False
    
    try:
        with open("env.example", "r") as src:
            content = src.read()
        
        with open(".env", "w") as dst:
            dst.write(content)
        
        print("✅ Файл .env создан из env.example")
        print("⚠️  Не забудьте добавить ваш BOT_TOKEN в файл .env")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания .env: {e}")
        return False


def create_directories():
    """Создает необходимые директории"""
    print("📁 Создаем директории...")
    directories = ["output", "test_output"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ {directory}/")
    
    return True


def check_weasyprint():
    """Проверяет установку WeasyPrint"""
    print("🖼️  Проверяем WeasyPrint...")
    try:
        import weasyprint
        print("✅ WeasyPrint установлен")
        return True
    except ImportError:
        print("❌ WeasyPrint не установлен")
        print("   Установите системные зависимости:")
        print("   macOS: brew install cairo pango gdk-pixbuf libffi")
        print("   Ubuntu: sudo apt-get install libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev")
        return False


def main():
    """Основная функция настройки"""
    print("🚀 Настройка проекта воронки анонсов\n")
    
    success = True
    
    # Проверяем Python
    if not check_python_version():
        success = False
    
    # Создаем директории
    if not create_directories():
        success = False
    
    # Создаем .env файл
    if not create_env_file():
        success = False
    
    # Устанавливаем зависимости
    if not install_requirements():
        success = False
    
    # Проверяем WeasyPrint
    if not check_weasyprint():
        success = False
    
    print("\n" + "="*50)
    
    if success:
        print("🎉 Настройка завершена успешно!")
        print("\nСледующие шаги:")
        print("1. Добавьте ваш BOT_TOKEN в файл .env")
        print("2. Запустите тест: python test_system.py")
        print("3. Запустите генерацию PNG: python bot_funnel.py --test")
        print("4. Запустите рассылку: python bot_funnel.py --send")
    else:
        print("❌ Настройка завершена с ошибками")
        print("Исправьте ошибки и запустите setup.py снова")
    
    return success


if __name__ == "__main__":
    main()

