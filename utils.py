import pandas as pd
import os
import tempfile
import random
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import STAGES, VARIANTS, get_default_profile, get_image_size, get_greeting, get_cta_text


def load_users(csv_path: str) -> pd.DataFrame:
    """
    Загружает пользователей из CSV файла.
    Проверяет наличие необходимых полей и конвертирует telegram_id в int.
    Добавляет поле variant если отсутствует.
    """
    try:
        df = pd.read_csv(csv_path)
        
        # Проверяем наличие необходимых полей
        required_fields = ['name', 'role', 'company', 'telegram_id']
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            raise ValueError(f"Отсутствуют обязательные поля: {missing_fields}")
        
        # Добавляем поле variant если отсутствует
        if 'variant' not in df.columns:
            df['variant'] = 'a'
            print("⚠️  Поле 'variant' отсутствует, установлено значение 'a' по умолчанию")
        
        # Конвертируем telegram_id в int
        df['telegram_id'] = df['telegram_id'].astype(int)
        
        # Проверяем корректность вариантов
        invalid_variants = df[~df['variant'].isin(VARIANTS)]
        if not invalid_variants.empty:
            print(f"⚠️  Найдены некорректные варианты: {invalid_variants['variant'].tolist()}")
            df.loc[~df['variant'].isin(VARIANTS), 'variant'] = 'a'
        
        print(f"✅ Загружено {len(df)} пользователей из {csv_path}")
        print(f"   Варианты: {df['variant'].value_counts().to_dict()}")
        return df
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {csv_path} не найден")
    except Exception as e:
        raise Exception(f"Ошибка при загрузке CSV: {e}")


def _resolve_asset_paths(data: dict, base_dir: Path) -> dict:
    """
    Рекурсивно преобразует относительные пути к assets в абсолютные.
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = _resolve_asset_paths(value, base_dir)
        elif isinstance(value, str) and value.startswith('assets/'):
            # Преобразуем относительный путь в абсолютный
            abs_path = base_dir / value
            if abs_path.exists():
                result[key] = f"file://{abs_path.resolve()}"
            else:
                result[key] = value  # Оставляем как есть если файл не найден
        else:
            result[key] = value
    
    return result


def render_html(stage: str, variant: str, user_data: dict, profile: dict = None) -> str:
    """
    Рендерит HTML шаблон с данными пользователя, брендингом и профилем.
    
    Args:
        stage: Этап воронки (interest, solution, deadline)
        variant: Вариант A/B-теста (a, b, c)
        user_data: Данные пользователя (name, role, company)
        profile: Профиль брендинга (если None, используется default)
    
    Returns:
        str: Отрендеренный HTML
    """
    if profile is None:
        profile = get_default_profile()
    
    try:
        # Базовая директория проекта
        base_dir = Path(__file__).parent
        
        # Создаем Jinja2 окружение
        template_dir = base_dir / 'templates'
        env = Environment(loader=FileSystemLoader(template_dir))
        
        # Формируем имя шаблона
        template_name = f"{stage}_{variant}.html"
        template_path = template_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Шаблон {template_name} не найден")
        
        # Загружаем шаблон
        template = env.get_template(template_name)
        
        # Получаем приветствие и CTA на основе профиля
        greeting = get_greeting(profile, user_data.get('name', 'User'))
        cta_text = get_cta_text(profile, stage)
        
        # Преобразуем пути к assets в абсолютные для html2image
        brand_data = _resolve_asset_paths(profile.get('brand', {}), base_dir)
        
        # Подготавливаем данные для рендеринга
        render_data = {
            # Данные пользователя
            **user_data,
            
            # Брендинг (с абсолютными путями)
            'brand': brand_data,
            'colors': profile.get('colors', {}),
            'fonts': profile.get('fonts', {}),
            'social': profile.get('social', {}),
            
            # Дизайн
            'card': profile.get('card', {}),
            'cta': profile.get('cta', {}),
            'image': profile.get('image', {}),
            'banner': profile.get('banner', {}),
            'icons': profile.get('icons', {}),
            
            # Контент
            'content': profile.get('content', {}).get(stage, {}),
            'tone': profile.get('tone', {}),
            
            # Вспомогательные
            'greeting': greeting,
            'cta_text': cta_text,
            'stage': stage,
            'variant': variant
        }
        
        # Рендерим с данными пользователя и брендингом
        html_content = template.render(**render_data)
        
        return html_content
        
    except Exception as e:
        raise Exception(f"Ошибка при рендеринге HTML {stage}_{variant}: {e}")


def html_to_png(html_str: str, stage: str, user_id: int, output_dir: str, 
                user_data: dict = None, profile: dict = None) -> str:
    """
    Конвертирует HTML в PNG изображение через браузерный рендеринг.
    
    Args:
        html_str: HTML-контент (полностью отрендеренный)
        stage: Этап воронки
        user_id: ID пользователя Telegram
        output_dir: Директория для сохранения
        user_data: Данные пользователя
        profile: Профиль брендинга
    
    Returns:
        str: Путь к сгенерированному PNG
    """
    if profile is None:
        profile = get_default_profile()
    
    if user_data is None:
        user_data = {}
    
    try:
        # Создаем директорию для вывода если её нет
        os.makedirs(output_dir, exist_ok=True)
        
        # Получаем размеры изображения из профиля
        width, height = get_image_size(profile)
        
        # Имя файла
        png_filename = f"{stage}_{user_id}.png"
        png_path = os.path.join(output_dir, png_filename)
        
        # Пробуем html2image (браузерный рендеринг)
        try:
            from html2image import Html2Image
            
            # Создаём временную директорию для html2image
            temp_output = tempfile.mkdtemp()
            
            hti = Html2Image(
                output_path=temp_output,
                size=(width, height),
                custom_flags=['--no-sandbox', '--disable-gpu', '--hide-scrollbars']
            )
            
            # Рендерим HTML в PNG
            hti.screenshot(
                html_str=html_str,
                save_as=png_filename
            )
            
            # Перемещаем файл в output_dir
            temp_png = os.path.join(temp_output, png_filename)
            if os.path.exists(temp_png):
                import shutil
                shutil.move(temp_png, png_path)
                
                # Очищаем временную директорию
                shutil.rmtree(temp_output, ignore_errors=True)
                
                print(f"   📸 Сгенерировано: {png_filename} ({width}x{height})")
                return png_path
            else:
                raise Exception("html2image не создал файл")
                
        except ImportError:
            print("   ⚠️  html2image не установлен, используем Pillow fallback")
            return _pillow_fallback(html_str, stage, user_id, output_dir, user_data, profile)
        except Exception as e:
            print(f"   ⚠️  html2image ошибка: {e}, используем Pillow fallback")
            return _pillow_fallback(html_str, stage, user_id, output_dir, user_data, profile)
            
    except Exception as e:
        raise Exception(f"Ошибка при конвертации HTML в PNG: {e}")


def _pillow_fallback(html_str: str, stage: str, user_id: int, output_dir: str,
                     user_data: dict, profile: dict) -> str:
    """
    Fallback генерация через Pillow если html2image недоступен.
    """
    from PIL import Image, ImageDraw, ImageFont
    
    width, height = get_image_size(profile)
    colors = profile.get('colors', {})
    fonts_config = profile.get('fonts', {})
    
    # Цвета
    bg_color = colors.get('background', '#F5F3EF')
    text_color = colors.get('text_primary', '#4A4F46')
    accent_color = colors.get('secondary', '#A38DA2')
    
    # Создаём изображение с градиентом
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Простой вертикальный градиент
    bg1 = _hex_to_rgb(colors.get('background', '#F5F3EF'))
    bg2 = _hex_to_rgb(colors.get('background_alt', '#E3D6C4'))
    
    for y in range(height):
        ratio = y / height
        r = int(bg1[0] * (1 - ratio) + bg2[0] * ratio)
        g = int(bg1[1] * (1 - ratio) + bg2[1] * ratio)
        b = int(bg1[2] * (1 - ratio) + bg2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Загружаем шрифты
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 
                                        fonts_config.get('size_title', 42))
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 
                                         fonts_config.get('size_subtitle', 26))
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 
                                        fonts_config.get('size_body', 18))
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
    
    padding = profile.get('card', {}).get('padding', 48)
    stage_base = stage.split('_')[0] if '_' in stage else stage
    
    # Рисуем контент
    y_pos = padding
    
    # Логотип
    brand = profile.get('brand', {})
    logo = brand.get('logo', {})
    logo_text = logo.get('text', 'BRAND') if isinstance(logo, dict) else str(logo)
    draw.text((padding, y_pos), logo_text, fill=text_color, font=font_large)
    y_pos += fonts_config.get('size_title', 42) + 20
    
    # Приветствие
    greeting = get_greeting(profile, user_data.get('name', 'User'))
    draw.text((padding, y_pos), greeting, fill=text_color, font=font_medium)
    y_pos += fonts_config.get('size_subtitle', 26) + 30
    
    # Контент этапа
    content = profile.get('content', {}).get(stage_base, {})
    headline = content.get('headline', '')
    if headline:
        draw.text((padding, y_pos), headline, fill=accent_color, font=font_medium)
        y_pos += fonts_config.get('size_subtitle', 26) + 15
    
    subheadline = content.get('subheadline', '')
    if subheadline:
        draw.text((padding, y_pos), subheadline, fill=text_color, font=font_small)
        y_pos += fonts_config.get('size_body', 18) + 25
    
    # Features
    features = content.get('features', [])
    for feature in features[:3]:
        if isinstance(feature, dict):
            icon = feature.get('icon', '•')
            text = feature.get('text', '')
        else:
            icon = '•'
            text = str(feature)
        draw.text((padding, y_pos), f"{icon} {text}", fill=text_color, font=font_small)
        y_pos += fonts_config.get('size_body', 18) + 12
    
    # CTA
    cta_text = get_cta_text(profile, stage_base)
    cta_y = height - padding - 70
    
    # Кнопка CTA (прямоугольник)
    button_color = _hex_to_rgb(colors.get('button_bg', '#8CA29B'))
    button_width = len(cta_text) * 12 + 60
    draw.rounded_rectangle(
        [(padding, cta_y), (padding + button_width, cta_y + 50)],
        radius=25,
        fill=button_color
    )
    draw.text((padding + 30, cta_y + 12), cta_text, fill='white', font=font_small)
    
    # Tagline
    tagline = brand.get('tagline', '')
    draw.text((padding, height - padding - 10), tagline, fill=text_color, font=font_small)
    
    # Сохраняем
    png_filename = f"{stage}_{user_id}.png"
    png_path = os.path.join(output_dir, png_filename)
    
    quality = profile.get('image', {}).get('quality', 95)
    img.save(png_path, quality=quality)
    
    print(f"   📸 Сгенерировано (Pillow): {png_filename}")
    return png_path


def _hex_to_rgb(hex_color: str) -> tuple:
    """Конвертирует HEX цвет в RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_keyboard(stage: str, user_id: int, user_name: str = None, profile: dict = None) -> InlineKeyboardMarkup:
    """
    Создает inline клавиатуру для этапа воронки с персонализацией.
    
    Args:
        stage: Этап воронки
        user_id: ID пользователя
        user_name: Имя пользователя
        profile: Профиль брендинга
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой
    """
    if profile is None:
        profile = get_default_profile()
    
    # Получаем текст кнопки из профиля
    stage_base = stage.split('_')[0] if '_' in stage else stage
    button_text = get_cta_text(profile, stage_base)
    
    # Добавляем имя пользователя если есть
    if user_name:
        button_text = f"{button_text} для {user_name}"
    
    # URL из профиля
    base_url = profile.get('brand', {}).get('website', 'https://example.com')
    button_url = f"{base_url}/{stage}?user={user_id}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, url=button_url)]
    ])
    
    return keyboard


def get_random_variant() -> str:
    """
    Возвращает случайный вариант для A/B-тестирования.
    """
    return random.choice(VARIANTS)


def list_available_profiles() -> list:
    """
    Возвращает список доступных профилей.
    """
    from config import PROFILES_DIR, AVAILABLE_PROFILES
    
    profiles = []
    if PROFILES_DIR.exists():
        for file in PROFILES_DIR.glob('*.yaml'):
            profiles.append(file.stem)
    
    return sorted(set(profiles))


def validate_profile(profile: dict) -> tuple:
    """
    Проверяет корректность профиля.
    
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    required_sections = ['brand', 'colors', 'fonts', 'image', 'cta', 'tone', 'content']
    
    for section in required_sections:
        if section not in profile:
            errors.append(f"Отсутствует секция: {section}")
    
    # Проверяем brand
    if 'brand' in profile:
        brand = profile['brand']
        if 'name' not in brand:
            errors.append("brand.name обязателен")
        if 'logo' not in brand:
            errors.append("brand.logo обязателен")
    
    # Проверяем colors
    if 'colors' in profile:
        colors = profile['colors']
        required_colors = ['primary', 'background', 'text_primary']
        for color in required_colors:
            if color not in colors:
                errors.append(f"colors.{color} обязателен")
    
    # Проверяем content
    if 'content' in profile:
        content = profile['content']
        for stage in ['interest', 'solution', 'deadline']:
            if stage not in content:
                errors.append(f"content.{stage} обязателен")
    
    return (len(errors) == 0, errors)
