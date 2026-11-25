# Personalized banners for a Telegram funnel

A tool that turns a subscriber list into a series of personal banners and sends them through a Telegram bot. It suits online schools, courses, coaches and retreats that need image mailings without a designer.

This is a practice project. Case study: [tatidzufri.com/en/case/banner-funnel](https://tatidzufri.com/en/case/banner-funnel).

## About the project

Each person's data (name, role, company) goes into an HTML template, and a headless browser turns the page into an image. That gives the banner real typography, gradients and a logo, which are hard to get by drawing images in code.

The funnel has three touchpoints: interest, decision, deadline. Each stage has three layout variants. The look comes from a brand profile in YAML, while the templates stay the same.

## The task

A mailing with one picture for the whole list reads as an ad and quickly stops getting responses. Making personal banners by hand doesn't work: every subscriber needs their own layout, and three warm-up stages triple that. Paying a designer for each touchpoint eats the whole benefit of personalization.

## How it works

1. **Subscribers in a CSV.** Columns `name`, `role`, `company`, `telegram_id` and `variant` (which layout variant to show).
2. **Nine templates.** Three variants per stage. Interest hooks with emotion, decision shows the offer, deadline nudges to act with limited seats or a personal address by name.
3. **Brand profiles.** Six ready styles (wellness, corporate, creative, luxury, tech, minimal) plus a template for your own. A profile holds the logo, colors, fonts, sizes, button style and message tone.
4. **Rendering to an image.** html2image with Chromium saves each banner as a 1200×900 PNG.
5. **Sending.** An aiogram bot sends each subscriber three banners with a button to the website. If someone blocked the bot, the mailing carries on. At the end it prints statistics: who received what and which variants were shown.
6. **A/B test.** The layout variant comes from the table or is picked at random (`--variant random`) to compare which works better.

## Results

- Every subscriber gets a banner with their own name, role and company.
- In my test run a series of 15 layouts (5 subscribers times 3 stages) was ready in about a minute and a half, no designer involved.
- Six ready brand profiles, from restrained minimalism to a premium style.
- Nine templates cover three funnel stages, three variants each.

## Tech stack

| Technology | What it's for |
|---|---|
| **Python** | Project language, 3.11 in the container |
| **aiogram** | Sends the banners in Telegram with a link button |
| **Jinja2** | Puts subscriber data into the HTML template |
| **html2image + Chromium** | Turns the HTML page into a PNG with full layout |
| **pandas** | Reads the subscriber table |
| **PyYAML** | Brand profiles: colors, fonts, logo, sizes |
| **Pillow** | Processes the finished images |
| **python-dotenv** | The bot token in `.env`, outside the code |
| **Docker** | Runs with Chromium already installed |

## Repository structure

- `bot_funnel.py`: entry point, generation and sending.
- `config.py`: loading brand profiles.
- `utils.py`: rendering templates to images.
- `templates/`: nine HTML templates and shared styles.
- `profiles/`: brand profiles; `custom_sample.yaml` is the sample for your own.
- `assets/`: logos, icons and background patterns. How to add them is in `assets/README.md`.
- `users.csv`: a sample subscriber list.
- `test_basic.py`: a project structure check.

## Running it

You need Python 3 and Chromium (`brew install chromium` on macOS, `apt-get install chromium-browser` on Ubuntu).

```bash
pip install -r requirements.txt
cp env.example .env       # BOT_TOKEN from @BotFather and BASE_URL for the buttons
```

Fill `users.csv` with your subscribers. You can find a person's Telegram ID with the `@userinfobot` bot. For the bot to message someone, that person has to press "Start" in the bot at least once.

```bash
python3 bot_funnel.py --list-profiles              # list profiles
python3 bot_funnel.py --test --brand wellness      # images only, into output/, nothing sent
python3 bot_funnel.py --send --brand wellness      # send the mailing
python3 bot_funnel.py --send --variant random      # random variants for an A/B test
```

Your own style: copy `profiles/custom_sample.yaml` to `profiles/custom.yaml`, change the colors, fonts and logo, and run with `--brand custom`.

With Docker, a test generation runs like this: `docker compose run --rm funnel`. The images appear in `output/`.

## License

MIT: free to use in commercial and personal projects.

## Author

Tetiana Dziubas, AI automation engineer. I build Telegram bots, RAG assistants and LLM agents that take routine work off small teams. Case studies and contact: [tatidzufri.com/en](https://tatidzufri.com/en/).
