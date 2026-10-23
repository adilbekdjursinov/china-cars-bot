from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from faq import FAQ

BTN_ORDER = "🛒 Оформить заказ"
BTN_FAQ = "❓ Частые вопросы"
BTN_ASK = "💬 Задать вопрос"
BTN_CONTACTS = "📞 Контакты"
BTN_CANCEL = "❌ Отмена"
BTN_SKIP = "⏭ Пропустить"

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_ORDER)],
        [KeyboardButton(text=BTN_FAQ), KeyboardButton(text=BTN_ASK)],
        [KeyboardButton(text=BTN_CONTACTS)],
    ],
    resize_keyboard=True,
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BTN_CANCEL)]], resize_keyboard=True
)

skip_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BTN_SKIP)], [KeyboardButton(text=BTN_CANCEL)]],
    resize_keyboard=True,
)

phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить мой номер", request_contact=True)],
        [KeyboardButton(text=BTN_CANCEL)],
    ],
    resize_keyboard=True,
)

confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="order:confirm"),
            InlineKeyboardButton(text="✏️ Заново", callback_data="order:restart"),
        ],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="order:cancel")],
    ]
)

start_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text=BTN_ORDER, callback_data="order:start")]]
)


def faq_list_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=item["q"], callback_data=f"faq:{i}")]
            for i, item in enumerate(FAQ)
        ]
    )


faq_back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Все вопросы", callback_data="faq:list")],
        [InlineKeyboardButton(text=BTN_ORDER, callback_data="order:start")],
    ]
)
