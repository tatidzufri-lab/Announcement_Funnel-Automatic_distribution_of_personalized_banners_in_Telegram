#!/usr/bin/env python3
"""
Базовый тест системы без внешних зависимостей
"""

import os
import sys
from pathlib import Path


def test_file_structure():
    """Проверяет структуру файлов"""
    print("🧪 Проверяем структуру файлов...")
    
    required_files = [
        'bot_funnel.py',
        'config.py', 
        'utils.py',
        'users.csv',
        'requirements.txt',
        'env.example',
        'templates/interest_a.html',
        'templates/solution_a.html',
        'templates/deadline_a.html',
        'templates/styles.css'
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - файл не найден")
            all_good = False
    
    return all_good


def test_csv_content():
    """Проверяет содержимое CSV файла с поддержкой вариантов"""
    print("\n🧪 Проверяем CSV файл...")
    
    try:
        with open('users.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            print("❌ CSV файл пуст или содержит только заголовки")
            return False
        
        # Проверяем заголовки
        headers = lines[0].strip().split(',')
        required_headers = ['name', 'role', 'company', 'telegram_id', 'variant']
        
        for header in required_headers:
            if header not in headers:
                print(f"❌ Отсутствует обязательное поле: {header}")
                return False
        
        print(f"✅ CSV файл корректен: {len(lines)-1} пользователей")
        print(f"   Поля: {', '.join(headers)}")
        
        # Проверяем варианты
        variants = []
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 5:
                variants.append(parts[4])
        
        variant_counts = {}
        for variant in variants:
            variant_counts[variant] = variant_counts.get(variant, 0) + 1
        
        print(f"   Варианты: {variant_counts}")
        
        # Показываем первые несколько записей
        print("   Примеры записей:")
        for i, line in enumerate(lines[1:4], 1):
            print(f"   {i}. {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка чтения CSV: {e}")
        return False


def test_html_templates():
    """Проверяет HTML шаблоны с A/B-тестированием"""
    print("\n🧪 Проверяем HTML шаблоны...")
    
    stages = ['interest', 'solution', 'deadline']
    variants = ['a', 'b', 'c']
    all_good = True
    
    for stage in stages:
        for variant in variants:
            template_name = f"{stage}_{variant}.html"
            template_path = f"templates/{template_name}"
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Проверяем наличие основных плейсхолдеров
                # Новый формат: brand.logo.text вместо brand.logo
                placeholders = ['{{ greeting }}', '{{ cta_text', 'brand.logo']
                missing_placeholders = [p for p in placeholders if p not in content]
                
                if missing_placeholders:
                    print(f"⚠️  {template_name}: не найдены {missing_placeholders}")
                else:
                    print(f"✅ {template_name}: структура корректна")
                    
            except Exception as e:
                print(f"❌ {template_name}: ошибка чтения - {e}")
                all_good = False
    
    return all_good


def test_css_file():
    """Проверяет CSS файл"""
    print("\n🧪 Проверяем CSS файл...")
    
    try:
        with open('templates/styles.css', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие основных стилей (новый формат)
        required_styles = ['body', '.banner', '.logo', '.cta-button']
        missing_styles = [style for style in required_styles if style not in content]
        
        if missing_styles:
            print(f"❌ CSS: отсутствуют стили {missing_styles}")
            return False
        else:
            print("✅ CSS файл корректен")
            return True
            
    except Exception as e:
        print(f"❌ CSS: ошибка чтения - {e}")
        return False


def test_python_syntax():
    """Проверяет синтаксис Python файлов"""
    print("\n🧪 Проверяем синтаксис Python файлов...")
    
    python_files = ['bot_funnel.py', 'config.py', 'utils.py']
    all_good = True
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Простая проверка синтаксиса
            compile(content, file_path, 'exec')
            print(f"✅ {file_path}: синтаксис корректен")
            
        except SyntaxError as e:
            print(f"❌ {file_path}: синтаксическая ошибка - {e}")
            all_good = False
        except Exception as e:
            print(f"❌ {file_path}: ошибка - {e}")
            all_good = False
    
    return all_good


def main():
    """Основная функция тестирования"""
    print("🚀 Базовое тестирование системы воронки\n")
    
    tests = [
        test_file_structure,
        test_csv_content,
        test_html_templates,
        test_css_file,
        test_python_syntax
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("="*50)
    print(f"📊 Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Система готова к работе.")
        print("\nСледующие шаги:")
        print("1. Установите зависимости: pip install -r requirements.txt")
        print("2. Настройте .env файл с BOT_TOKEN")
        print("3. Запустите: python3 bot_funnel.py --test")
    else:
        print("❌ Некоторые тесты не пройдены. Исправьте ошибки.")
    
    return passed == total


if __name__ == "__main__":
    main()
