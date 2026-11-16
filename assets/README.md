# Логотипы, иконки и паттерны для баннеров

```
assets/
├── logos/
│   ├── poznay_sebya.svg        # для светлого фона
│   └── poznay_sebya_dark.svg   # для темного фона
├── icons/
│   ├── check.svg
│   ├── star.svg
│   └── arrow.svg
└── patterns/
    └── dots.svg                # точечный фон
```

## Как подключить в профиле

Логотип задается в профиле бренда, например в `profiles/wellness.yaml`:

```yaml
brand:
  logo:
    image: "assets/logos/poznay_sebya.svg"
    image_dark: "assets/logos/poznay_sebya_dark.svg"
    image_width: 200
    image_height: 50
    text: "POZNAY SEBYA"        # подпись, если файл логотипа не найден
    subtitle: "KNOW YOURSELF"
```

Иконки для пунктов списка:

```yaml
icons:
  feature_marker: "assets/icons/star.svg"
  check_marker: "assets/icons/check.svg"
```

Пути указываются от корня проекта. При рендере они сами превращаются в абсолютные.

## Какие файлы подходят

| | Логотип | Иконка | Паттерн |
|---|---|---|---|
| Формат | SVG, можно PNG | SVG | SVG с `pattern` |
| Размер | viewBox около 400×80, PNG 400×100 и @2x | viewBox 24×24 | плитка 20–50 px |
| Цвет | светлая и темная версии, PNG с прозрачностью | `currentColor` или цвета профиля | прозрачность 0,05–0,15 |

SVG лучше PNG: он остается четким при любом размере баннера.

## Свой логотип

1. Положите файл в `assets/logos/`.
2. Укажите путь и размеры в профиле.
3. Проверьте результат без рассылки: `python3 bot_funnel.py --test --brand wellness`.
