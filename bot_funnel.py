#!/usr/bin/env python3
"""
Telegram Bot для автоматической персонализированной воронки анонсов
с поддержкой профилей брендинга и A/B-тестирования
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from utils import (
    load_users, render_html, html_to_png, get_keyboard, 
    get_random_variant, list_available_profiles
)
from config import (
    BOT_TOKEN, STAGES, SEND_DELAY, VARIANTS, 
    load_profile, AVAILABLE_PROFILES
)


async def send_funnel(bot: Bot, users_df, output_dir: str, send_real: bool = False, 
                      variant_mode: str = 'fixed', profile: dict = None):
    """
    Отправляет персонализированную воронку пользователям с поддержкой A/B-тестирования
    и кастомного брендинга.
    
    Args:
        bot: Экземпляр Telegram бота
        users_df: DataFrame с пользователями
        output_dir: Директория для сохранения PNG
        send_real: Отправлять ли реальные сообщения
        variant_mode: Режим выбора вариантов (fixed/random)
        profile: Профиль брендинга
    """
    brand_name = profile.get('brand', {}).get('name', 'Unknown') if profile else 'Default'
    
    print(f"\n{'='*60}")
    print(f"🚀 Запуск воронки анонсов")
    print(f"{'='*60}")
    print(f"📊 Пользователей: {len(users_df)}")
    print(f"📝 Режим: {'Отправка' if send_real else 'Тестирование (генерация PNG)'}")
    print(f"🎯 Варианты: {variant_mode}")
    print(f"🎨 Бренд: {brand_name}")
    print(f"{'='*60}\n")
    
    total_messages = len(users_df) * len(STAGES)
    processed = 0
    variant_stats = {'a': 0, 'b': 0, 'c': 0}
    
    for _, row in users_df.iterrows():
        user_data = {
            'name': row['name'],
            'role': row['role'],
            'company': row['company']
        }
        chat_id = row['telegram_id']
        
        # Определяем вариант для пользователя
        if variant_mode == 'random':
            variant = get_random_variant()
        else:
            variant = row.get('variant', 'a')
        
        print(f"\n👤 {user_data['name']} (ID: {chat_id}, вариант: {variant.upper()})")
        
        for stage in STAGES:
            try:
                # Рендерим HTML с учетом варианта и профиля
                html_content = render_html(stage, variant, user_data, profile)
                
                # Конвертируем в PNG с уникальным именем
                png_path = html_to_png(
                    html_content, 
                    f"{stage}_{variant}", 
                    chat_id, 
                    output_dir, 
                    user_data,
                    profile
                )
                
                if send_real:
                    # Отправляем через бота
                    keyboard = get_keyboard(stage, chat_id, user_data['name'], profile)
                    
                    try:
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=FSInputFile(png_path),
                            reply_markup=keyboard
                        )
                        print(f"   ✅ Отправлено: {stage}_{variant}")
                        
                    except TelegramBadRequest as e:
                        print(f"   ❌ Ошибка: {e}")
                    except TelegramForbiddenError as e:
                        print(f"   ❌ Пользователь заблокировал бота")
                    except Exception as e:
                        print(f"   ❌ Неожиданная ошибка: {e}")
                    
                    # Задержка между отправками
                    await asyncio.sleep(SEND_DELAY)
                else:
                    print(f"   📸 Сгенерирован: {Path(png_path).name}")
                
                # Статистика вариантов
                variant_stats[variant] += 1
                processed += 1
                
            except Exception as e:
                print(f"   ❌ Ошибка при обработке {stage}_{variant}: {e}")
                continue
    
    # Итоговая статистика
    print(f"\n{'='*60}")
    print(f"🎉 Обработка завершена!")
    print(f"{'='*60}")
    print(f"📊 Обработано сообщений: {processed}/{total_messages}")
    print(f"📈 Статистика вариантов:")
    for v, count in variant_stats.items():
        if count > 0:
            print(f"   Вариант {v.upper()}: {count} сообщений")
    print(f"📁 PNG сохранены в: {output_dir}/")
    print(f"{'='*60}\n")


async def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description='Telegram Bot для воронки анонсов с A/B-тестированием и кастомным брендингом',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --test                      # Тест с профилем по умолчанию (wellness)
  %(prog)s --test --brand corporate    # Тест с корпоративным стилем
  %(prog)s --test --brand luxury       # Тест с люксовым стилем
  %(prog)s --send --brand creative     # Отправка с креативным стилем
  %(prog)s --test --brand /path/to/custom.yaml  # Тест с кастомным профилем
  %(prog)s --list-profiles             # Показать доступные профили
        """
    )
    parser.add_argument('--test', action='store_true', 
                        help='Тестовый режим (только генерация PNG)')
    parser.add_argument('--send', action='store_true', 
                        help='Режим отправки сообщений')
    parser.add_argument('--variant', choices=['fixed', 'random'], default='fixed', 
                        help='Режим выбора вариантов: fixed (по CSV) или random (случайно)')
    parser.add_argument('--brand', type=str, default='custom',
                        help='Профиль брендинга: custom, wellness, corporate, creative, luxury, tech, minimal или путь к .yaml')
    parser.add_argument('--list-profiles', action='store_true',
                        help='Показать список доступных профилей')
    
    args = parser.parse_args()
    
    # Показать список профилей
    if args.list_profiles:
        print("\n📋 Доступные профили брендинга:\n")
        profiles = list_available_profiles()
        for p in profiles:
            emoji = {
                'wellness': '🌿',
                'corporate': '🏢', 
                'creative': '🎨',
                'luxury': '👑',
                'tech': '💻',
                'minimal': '⬜',
                'custom': '🎨'
            }.get(p, '📄')
            print(f"  {emoji} {p}")
        print(f"\nИспользование: python3 bot_funnel.py --test --brand <профиль>\n")
        return
    
    # Определяем режим работы
    if args.send:
        send_real = True
        mode = "отправки"
    else:
        send_real = False
        mode = "тестирования"
    
    print(f"\n🚀 Запуск в режиме {mode}")
    
    # Загружаем профиль
    profile = load_profile(args.brand)
    
    # Проверяем токен бота
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден в переменных окружения")
        print("   Создайте файл .env и добавьте BOT_TOKEN=your_bot_token")
        sys.exit(1)
    
    # Создаем директорию для вывода
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Загружаем пользователей
        users_df = load_users('users.csv')
        
        if users_df.empty:
            print("❌ Ошибка: CSV файл пуст или не содержит данных")
            sys.exit(1)
        
        # Создаем бота
        bot = Bot(token=BOT_TOKEN)
        
        # Запускаем воронку с профилем
        await send_funnel(bot, users_df, output_dir, send_real, args.variant, profile)
        
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)
    finally:
        # Закрываем сессию бота
        if 'bot' in locals():
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Программа остановлена пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
