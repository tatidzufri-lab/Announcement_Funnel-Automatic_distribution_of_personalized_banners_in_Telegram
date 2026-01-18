import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Этапы воронки
STAGES = ['interest', 'solution', 'deadline']

# Варианты для A/B-тестирования
VARIANTS = ['a', 'b', 'c']

# Задержка между отправкой сообщений (секунды)
SEND_DELAY = 1

# Директория с профилями
PROFILES_DIR = Path(__file__).parent / 'profiles'

# Доступные профили
AVAILABLE_PROFILES = ['wellness', 'corporate', 'creative', 'luxury', 'tech', 'minimal', 'custom']

# ═══════════════════════════════════════════════════════════════════════════════
# ФУНКЦИИ ДЛЯ РАБОТЫ С ПРОФИЛЯМИ
# ═══════════════════════════════════════════════════════════════════════════════

def load_profile(profile_name: str = 'wellness') -> dict:
    """
    Загружает профиль брендинга из YAML файла.
    
    Args:
        profile_name: Имя профиля (wellness, corporate, creative, luxury, tech, minimal)
                     или путь к кастомному YAML файлу
    
    Returns:
        dict: Настройки профиля
    """
    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML не установлен. Используем профиль по умолчанию.")
        return get_default_profile()
    
    # Проверяем, является ли profile_name путём к файлу
    if profile_name.endswith('.yaml') or profile_name.endswith('.yml'):
        profile_path = Path(profile_name)
    else:
        profile_path = PROFILES_DIR / f'{profile_name}.yaml'
    
    if not profile_path.exists():
        print(f"⚠️  Профиль '{profile_name}' не найден. Используем 'wellness'.")
        profile_path = PROFILES_DIR / 'wellness.yaml'
    
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = yaml.safe_load(f)
        print(f"✅ Загружен профиль: {profile_path.stem}")
        return profile
    except Exception as e:
        print(f"❌ Ошибка загрузки профиля: {e}")
        return get_default_profile()


def get_default_profile() -> dict:
    """
    Возвращает профиль по умолчанию (wellness/Poznay Sebya).
    Используется если YAML не доступен.
    """
    return {
        'brand': {
            'name': 'Poznay Sebya',
            'logo': 'POZNAY SEBYA / KNOW YOURSELF',
            'tagline': 'Путь к себе начинается здесь',
            'website': 'https://poznaysebya.com',
            'telegram': '@poznaysebya'
        },
        'colors': {
            'primary': '#4A4F46',
            'secondary': '#A38DA2',
            'accent': '#8CA29B',
            'background': '#F5F3EF',
            'background_alt': '#E3D6C4',
            'text_primary': '#4A4F46',
            'text_secondary': '#6B7064',
            'text_light': '#FFFFFF',
            'button_bg': '#8CA29B',
            'button_text': '#FFFFFF',
            'button_hover': '#7A9189',
            'border': '#D4CFC7',
            'shadow': 'rgba(74, 79, 70, 0.1)'
        },
        'fonts': {
            'heading': 'Cormorant Garamond',
            'heading_weight': '600',
            'body': 'Inter',
            'body_weight': '400',
            'size_title': 36,
            'size_subtitle': 24,
            'size_body': 18,
            'size_small': 14,
            'size_button': 16,
            'line_height': 1.6
        },
        'image': {
            'format': 'wide',
            'sizes': {
                'square': [800, 800],
                'wide': [1200, 630],
                'story': [1080, 1920],
                'compact': [800, 600]
            },
            'quality': 95,
            'dpi': 144
        },
        'card': {
            'border_radius': 16,
            'padding': 40,
            'shadow': 'soft',
            'border_width': 0,
            'background_type': 'gradient',
            'gradient_direction': 'to bottom right',
            'gradient_colors': ['#F5F3EF', '#E3D6C4']
        },
        'cta': {
            'style': 'rounded',
            'icon': '→',
            'shadow': True,
            'texts': {
                'interest': 'Узнать больше',
                'solution': 'Получить программу',
                'deadline': 'Записаться сейчас'
            }
        },
        'tone': {
            'style': 'friendly',
            'greetings': {
                'formal': 'Уважаемый(-ая) {{ name }},',
                'friendly': '{{ name }}, добрый день!',
                'dynamic': '{{ name }}, это ваш момент!'
            },
            'calls_to_action': {
                'formal': 'Будем рады видеть Вас на программе',
                'friendly': 'Присоединяйтесь к нам в путешествие к себе',
                'dynamic': 'Действуйте прямо сейчас!'
            }
        },
        'social': {
            'telegram': '@poznaysebya',
            'instagram': '@poznay.sebya',
            'website': 'https://poznaysebya.com',
            'email': 'hello@poznaysebya.com',
            'phone': '+7 (999) 123-45-67'
        },
        'content': {
            'interest': {
                'headline': 'Откройте глубину в себе',
                'subheadline': 'Путь самопознания начинается с первого шага',
                'features': ['Персональный подход', 'Безопасное пространство', 'Глубинные инсайты']
            },
            'solution': {
                'headline': 'Ваша программа трансформации',
                'subheadline': 'Индивидуальные сессии с экспертом',
                'features': ['5-10 персональных встреч', 'PDF-отчёты с инсайтами', 'Поддержка между сессиями']
            },
            'deadline': {
                'headline': 'Осталось ограниченное число мест',
                'subheadline': 'Начните свой путь уже сегодня',
                'urgency': 'Только 10 мест доступно!',
                'price_range': '25 000 — 75 000 ₽'
            }
        }
    }


def get_image_size(profile: dict) -> tuple:
    """
    Возвращает размеры изображения на основе выбранного формата в профиле.
    """
    image_config = profile.get('image', {})
    format_name = image_config.get('format', 'wide')
    sizes = image_config.get('sizes', {})
    
    default_sizes = {
        'square': (800, 800),
        'wide': (1200, 900),  # Увеличено для полного отображения контента
        'story': (1080, 1920),
        'compact': (800, 600)
    }
    
    size = sizes.get(format_name, default_sizes.get(format_name, (800, 600)))
    return tuple(size)


def get_greeting(profile: dict, name: str) -> str:
    """
    Возвращает приветствие на основе тона в профиле.
    """
    tone = profile.get('tone', {})
    style = tone.get('style', 'friendly')
    greetings = tone.get('greetings', {})
    
    template = greetings.get(style, '{{ name }}, добрый день!')
    return template.replace('{{ name }}', name)


def get_cta_text(profile: dict, stage: str) -> str:
    """
    Возвращает текст кнопки CTA для этапа.
    """
    cta = profile.get('cta', {})
    texts = cta.get('texts', {})
    
    text = texts.get(stage, 'Узнать больше →')
    
    # Если текст уже содержит стрелку или иконку — возвращаем как есть
    if '→' in text or '←' in text or text.endswith(('!', '?')):
        return text
    
    # Добавляем иконку если есть
    icon = cta.get('icon', '')
    if icon and icon not in text:
        text = f"{text} {icon}"
    
    return text


# ═══════════════════════════════════════════════════════════════════════════════
# ОБРАТНАЯ СОВМЕСТИМОСТЬ
# ═══════════════════════════════════════════════════════════════════════════════
# Старые переменные для совместимости с существующим кодом

_default_profile = get_default_profile()

BRAND = _default_profile['brand']
FONTS = _default_profile['fonts']
BASE_URL = _default_profile['brand']['website']
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600
