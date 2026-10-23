# China Cars — Telegram-бот

Бот магазина автооптики и кузовных деталей для китайских авто: FAQ, ИИ-консультант (Gemini), приём заказов.

## Стек
- Python 3.12, aiogram 3 — Telegram-бот (long polling)
- google-genai — Gemini API
- SQLite — хранение заказов
- Railway — хостинг (worker)

## Файлы
| Файл | Назначение |
|---|---|
| `bot.py` | точка входа |
| `handlers.py` | меню, FAQ, заказ по шагам, ответы ИИ |
| `faq.py` | вопросы и ответы FAQ (редактируйте здесь) |
| `ai.py` | промпт и запросы к Gemini |
| `db.py` | база заказов |
| `config.py` | переменные окружения |

## Локальный запуск
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # впишите токен и ключи
python bot.py
```

## Деплой на Railway
1. Загрузите проект на GitHub (файл `.env` не попадёт — он в `.gitignore`).
2. Railway → New Project → Deploy from GitHub repo.
3. Вкладка **Variables**: добавьте `BOT_TOKEN`, `GEMINI_API_KEY`, `ADMIN_CHAT_ID` и при желании `SHOP_*`.
4. Чтобы заказы не терялись при передеплое: **Add Volume** с путём монтирования `/data`, переменная `DB_PATH=/data/orders.db`.
5. Домен не нужен — бот работает через polling. Держите 1 реплику.

`ADMIN_CHAT_ID`: напишите боту `/id` в личке или в группе менеджеров (бот должен быть добавлен в группу).

> Не запускайте бота локально и на Railway одновременно — Telegram выдаст ошибку Conflict.
