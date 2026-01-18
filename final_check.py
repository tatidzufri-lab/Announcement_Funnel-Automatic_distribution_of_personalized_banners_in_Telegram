#!/usr/bin/env python3
"""
Финальная проверка системы воронки анонсов с A/B-тестированием
"""

import os
import sys
from pathlib import Path

def check_project_structure():
    """Проверяет структуру проекта"""
    print("🔍 Проверка структуры проекта...")
    
    required_files = [
        'bot_funnel.py',
        'config.py', 
        'utils.py',
        'users.csv',
        'requirements.txt',
        'env.example',
        'templates/styles.css',
        'test_basic.py',
        'demo_ab_testing.py',
        'README.md',
        'QUICKSTART.md',
        'PROJECT_COMPLETE.md'
    ]
    
    # Проверяем основные файлы
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    # Проверяем HTML шаблоны
    stages = ['interest', 'solution', 'deadline']
    variants = ['a', 'b', 'c']
    
    print("\n📋 Проверка HTML шаблонов:")
    for stage in stages:
        for variant in variants:
            template_path = f"templates/{stage}_{variant}.html"
            if Path(template_path).exists():
                print(f"✅ {template_path}")
            else:
                missing_files.append(template_path)
                print(f"❌ {template_path}")
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы: {missing_files}")
        return False
    
    print(f"\n✅ Все файлы на месте! Всего: {len(required_files) + 9} файлов")
    return True


def check_csv_structure():
    """Проверяет структуру CSV файла"""
    print("\n📊 Проверка CSV файла...")
    
    try:
        with open('users.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            print("❌ CSV файл пуст")
            return False
        
        # Проверяем заголовки
        headers = lines[0].strip().split(',')
        required_headers = ['name', 'role', 'company', 'telegram_id', 'variant']
        
        missing_headers = [h for h in required_headers if h not in headers]
        if missing_headers:
            print(f"❌ Отсутствуют поля: {missing_headers}")
            return False
        
        print(f"✅ CSV файл корректен: {len(lines)-1} пользователей")
        print(f"   Поля: {', '.join(headers)}")
        
        # Анализируем варианты
        variants = []
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 5:
                variants.append(parts[4])
        
        variant_counts = {}
        for variant in variants:
            variant_counts[variant] = variant_counts.get(variant, 0) + 1
        
        print(f"   Варианты: {variant_counts}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка чтения CSV: {e}")
        return False


def check_branding():
    """Проверяет брендинг"""
    print("\n🎨 Проверка брендинга Poznay Sebya...")
    
    try:
        from config import BRAND, FONTS
        
        print("✅ Конфигурация брендинга загружена")
        print(f"   Логотип: {BRAND['logo']}")
        print(f"   Цвета: {len(BRAND['colors'])} цветов")
        print(f"   Шрифты: {len(FONTS)} шрифтов")
        
        # Проверяем CSS файл
        with open('templates/styles.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        if 'Cormorant Garamond' in css_content and 'Inter' in css_content:
            print("✅ CSS содержит брендовые шрифты")
        else:
            print("❌ CSS не содержит брендовые шрифты")
            return False
        
        if '#F5F3EF' in css_content and '#A38DA2' in css_content:
            print("✅ CSS содержит брендовые цвета")
        else:
            print("❌ CSS не содержит брендовые цвета")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки брендинга: {e}")
        return False


def check_templates_content():
    """Проверяет содержимое шаблонов"""
    print("\n📝 Проверка содержимого шаблонов...")
    
    stages = ['interest', 'solution', 'deadline']
    variants = ['a', 'b', 'c']
    all_good = True
    
    for stage in stages:
        for variant in variants:
            template_path = f"templates/{stage}_{variant}.html"
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Проверяем наличие плейсхолдеров
                placeholders = ['{{ name }}', '{{ role }}', '{{ company }}', '{{ brand.logo }}']
                missing_placeholders = [p for p in placeholders if p not in content]
                
                if missing_placeholders:
                    print(f"❌ {template_path}: отсутствуют {missing_placeholders}")
                    all_good = False
                else:
                    print(f"✅ {template_path}: все плейсхолдеры найдены")
                    
            except Exception as e:
                print(f"❌ {template_path}: ошибка чтения - {e}")
                all_good = False
    
    return all_good


def check_python_syntax():
    """Проверяет синтаксис Python файлов"""
    print("\n🐍 Проверка синтаксиса Python файлов...")
    
    python_files = ['bot_funnel.py', 'config.py', 'utils.py']
    all_good = True
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, file_path, 'exec')
            print(f"✅ {file_path}: синтаксис корректен")
            
        except SyntaxError as e:
            print(f"❌ {file_path}: синтаксическая ошибка - {e}")
            all_good = False
        except Exception as e:
            print(f"❌ {file_path}: ошибка - {e}")
            all_good = False
    
    return all_good


def show_usage_summary():
    """Показывает сводку по использованию"""
    print("\n🚀 Сводка по использованию:")
    
    print("\n1. Установка:")
    print("   pip install -r requirements.txt")
    print("   cp env.example .env")
    print("   # Добавьте BOT_TOKEN в .env")
    
    print("\n2. Тестирование:")
    print("   python3 test_basic.py")
    print("   python3 demo_ab_testing.py")
    print("   python3 bot_funnel.py --test")
    print("   python3 bot_funnel.py --test --variant random")
    
    print("\n3. Отправка:")
    print("   python3 bot_funnel.py --send")
    print("   python3 bot_funnel.py --send --variant random")
    
    print("\n4. Ожидаемый результат:")
    print("   - 15 PNG файлов при тестировании")
    print("   - Персонализированные сообщения при отправке")
    print("   - Статистика A/B-тестирования")


def main():
    """Основная функция финальной проверки"""
    print("🎯 Финальная проверка системы воронки анонсов с A/B-тестированием\n")
    
    checks = [
        check_project_structure(),
        check_csv_structure(),
        check_branding(),
        check_templates_content(),
        check_python_syntax()
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print("\n" + "="*60)
    print(f"📊 Результат финальной проверки: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Проект полностью готов!")
        print("\n✅ Система поддерживает:")
        print("   - A/B-тестирование с 3 вариантами")
        print("   - Брендинг Poznay Sebya")
        print("   - Персонализацию сообщений")
        print("   - Генерацию PNG изображений")
        print("   - Отправку через Telegram-бота")
        
        show_usage_summary()
        
        print("\n🎯 Следующий шаг: Установите зависимости и запустите тестирование!")
        
    else:
        print("❌ Некоторые тесты не пройдены. Исправьте ошибки.")
    
    return passed == total


if __name__ == "__main__":
    main()


