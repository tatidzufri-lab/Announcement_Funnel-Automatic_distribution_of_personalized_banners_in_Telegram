# Logos, icons and patterns for the banners

```
assets/
├── logos/
│   ├── poznay_sebya.svg        # for a light background
│   └── poznay_sebya_dark.svg   # for a dark background
├── icons/
│   ├── check.svg
│   ├── star.svg
│   └── arrow.svg
└── patterns/
    └── dots.svg                # dotted background
```

## Adding them to a profile

The logo is set in the brand profile, for example in `profiles/wellness.yaml`:

```yaml
brand:
  logo:
    image: "assets/logos/poznay_sebya.svg"
    image_dark: "assets/logos/poznay_sebya_dark.svg"
    image_width: 200
    image_height: 50
    text: "POZNAY SEBYA"        # caption used if the logo file isn't found
    subtitle: "KNOW YOURSELF"
```

Icons for list items:

```yaml
icons:
  feature_marker: "assets/icons/star.svg"
  check_marker: "assets/icons/check.svg"
```

Paths are relative to the project root. They're turned into absolute paths at render time.

## Which files work

| | Logo | Icon | Pattern |
|---|---|---|---|
| Format | SVG, PNG is fine | SVG | SVG with `pattern` |
| Size | viewBox about 400×80, PNG 400×100 and @2x | viewBox 24×24 | a 20–50 px tile |
| Color | light and dark versions, PNG with transparency | `currentColor` or profile colors | opacity 0.05–0.15 |

SVG is better than PNG: it stays sharp at any banner size.

## Your own logo

1. Put the file in `assets/logos/`.
2. Set the path and size in the profile.
3. Check the result without sending anything: `python3 bot_funnel.py --test --brand wellness`.
