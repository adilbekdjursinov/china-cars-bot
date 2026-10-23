import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import ai
import keyboards as kb
from config import ADMIN_CHAT_ID, SHOP_NAME
from db import save_order
from faq import FAQ

log = logging.getLogger(__name__)
router = Router()


class Order(StatesGroup):
    car = State()
    vin = State()
    part = State()
    name = State()
    phone = State()
    city = State()
    comment = State()
    confirm = State()


# ---------- Общие команды ----------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Здравствуйте! 👋 Я бот магазина <b>{SHOP_NAME}</b>.\n\n"
        "Мы продаём <b>автооптику</b> и <b>кузовные детали</b> для китайских автомобилей: "
        "Chery, Haval, Geely, Changan, JAC, Exeed, Tank, Omoda и др.\n\n"
        "Я могу:\n"
        "• ответить на частые вопросы\n"
        "• проконсультировать — просто напишите вопрос\n"
        "• принять заказ на деталь",
        reply_markup=kb.main_menu,
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "/start — главное меню\n/order — оформить заказ\n/faq — частые вопросы\n/cancel — отменить",
        reply_markup=kb.main_menu,
    )


@router.message(Command("id"))
async def cmd_id(message: Message):
    # Помогает узнать ADMIN_CHAT_ID (отправьте /id в нужном чате или группе)
    await message.answer(f"ID этого чата: <code>{message.chat.id}</code>")


@router.message(StateFilter("*"), Command("cancel"))
@router.message(StateFilter("*"), F.text == kb.BTN_CANCEL)
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=kb.main_menu)


# ---------- FAQ ----------

@router.message(Command("faq"))
@router.message(F.text == kb.BTN_FAQ)
async def faq_list(message: Message):
    await message.answer("Выберите вопрос:", reply_markup=kb.faq_list_kb())


@router.callback_query(F.data == "faq:list")
async def faq_list_cb(callback: CallbackQuery):
    await callback.message.edit_text("Выберите вопрос:", reply_markup=kb.faq_list_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("faq:"))
async def faq_answer(callback: CallbackQuery):
    item = FAQ[int(callback.data.split(":")[1])]
    await callback.message.edit_text(
        f"<b>{escape(item['q'])}</b>\n\n{escape(item['a'])}", reply_markup=kb.faq_back_kb
    )
    await callback.answer()


@router.message(F.text == kb.BTN_CONTACTS)
async def contacts(message: Message):
    await message.answer(escape(FAQ[-1]["a"]), reply_markup=kb.main_menu)


@router.message(F.text == kb.BTN_ASK)
async def ask_prompt(message: Message):
    await message.answer(
        "Напишите ваш вопрос — например: «Есть ли передняя фара на Haval Jolion 2022?»"
    )


# ---------- Оформление заказа ----------

async def start_order(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Order.car)
    await message.answer(
        "Оформим заказ 🛒\n\n<b>Шаг 1/7.</b> Укажите марку, модель и год авто.\n"
        "Например: <i>Chery Tiggo 7 Pro 2021</i>",
        reply_markup=kb.cancel_kb,
    )


@router.message(Command("order"))
@router.message(F.text == kb.BTN_ORDER)
async def order_cmd(message: Message, state: FSMContext):
    await start_order(message, state)


@router.callback_query(F.data.in_({"order:start", "order:restart"}))
async def order_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_order(callback.message, state)


@router.message(Order.car, F.text)
async def order_car(message: Message, state: FSMContext):
    await state.update_data(car=message.text)
    await state.set_state(Order.vin)
    await message.answer(
        "<b>Шаг 2/7.</b> Отправьте VIN-код (17 символов) — так мы точно подберём деталь.\n"
        "Если нет под рукой — нажмите «Пропустить».",
        reply_markup=kb.skip_kb,
    )


@router.message(Order.vin, F.text)
async def order_vin(message: Message, state: FSMContext):
    vin = "" if message.text == kb.BTN_SKIP else message.text.strip().upper()
    if vin and len(vin) != 17:
        await message.answer("VIN должен содержать 17 символов. Проверьте или нажмите «Пропустить».")
        return
    await state.update_data(vin=vin)
    await state.set_state(Order.part)
    await message.answer(
        "<b>Шаг 3/7.</b> Какая деталь нужна? Можно текстом или фото с подписью.\n"
        "Например: <i>левая передняя фара LED, передний бампер</i>",
        reply_markup=kb.cancel_kb,
    )


@router.message(Order.part, F.text | F.photo)
async def order_part(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id if message.photo else None
    part = message.text or message.caption or "см. фото"
    await state.update_data(part=part, photo_id=photo_id)
    await state.set_state(Order.name)
    await message.answer("<b>Шаг 4/7.</b> Как к вам обращаться?", reply_markup=kb.cancel_kb)


@router.message(Order.name, F.text)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Order.phone)
    await message.answer(
        "<b>Шаг 5/7.</b> Ваш номер телефона — нажмите кнопку ниже или введите вручную.",
        reply_markup=kb.phone_kb,
    )


@router.message(Order.phone, F.contact | F.text)
async def order_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text.strip()
    if sum(c.isdigit() for c in phone) < 10:
        await message.answer("Похоже, номер неполный. Введите телефон ещё раз.")
        return
    await state.update_data(phone=phone)
    await state.set_state(Order.city)
    await message.answer(
        "<b>Шаг 6/7.</b> Город доставки (или «самовывоз»).", reply_markup=kb.cancel_kb
    )


@router.message(Order.city, F.text)
async def order_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(Order.comment)
    await message.answer(
        "<b>Шаг 7/7.</b> Комментарий к заказу (оригинал/аналог, цвет, сроки и т.п.) "
        "или «Пропустить».",
        reply_markup=kb.skip_kb,
    )


def order_summary(data: dict) -> str:
    lines = [
        f"🚗 <b>Авто:</b> {escape(data['car'])}",
        f"🔢 <b>VIN:</b> {escape(data['vin']) or '—'}",
        f"🔧 <b>Деталь:</b> {escape(data['part'])}",
        f"👤 <b>Имя:</b> {escape(data['name'])}",
        f"📞 <b>Телефон:</b> {escape(data['phone'])}",
        f"📍 <b>Город:</b> {escape(data['city'])}",
        f"💬 <b>Комментарий:</b> {escape(data['comment']) or '—'}",
    ]
    return "\n".join(lines)


@router.message(Order.comment, F.text)
async def order_comment(message: Message, state: FSMContext):
    comment = "" if message.text == kb.BTN_SKIP else message.text
    await state.update_data(comment=comment)
    await state.set_state(Order.confirm)
    data = await state.get_data()
    await message.answer("Проверьте заявку:", reply_markup=kb.main_menu)
    await message.answer(order_summary(data), reply_markup=kb.confirm_kb)


@router.callback_query(Order.confirm, F.data == "order:confirm")
async def order_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user = callback.from_user
    order_id = save_order(
        {
            "user_id": user.id,
            "username": user.username or "",
            "photo_id": data.get("photo_id"),
            **{k: data[k] for k in ("car", "vin", "part", "name", "phone", "city", "comment")},
        }
    )
    await state.clear()
    await callback.message.edit_text(
        f"✅ Заявка <b>№{order_id}</b> принята!\n\n{order_summary(data)}\n\n"
        "Менеджер свяжется с вами в рабочее время, чтобы уточнить цену и наличие."
    )
    await callback.answer("Заявка отправлена")

    if ADMIN_CHAT_ID:
        client = f"@{escape(user.username)}" if user.username else f"id {user.id}"
        text = f"🆕 <b>Новая заявка №{order_id}</b>\nКлиент: {client}\n\n{order_summary(data)}"
        try:
            await bot.send_message(ADMIN_CHAT_ID, text)
            if data.get("photo_id"):
                await bot.send_photo(ADMIN_CHAT_ID, data["photo_id"], caption=f"Фото к заявке №{order_id}")
        except Exception:
            log.exception("Не удалось отправить заявку админу")
    else:
        log.warning("ADMIN_CHAT_ID не задан — заявка №%s сохранена только в базе", order_id)


@router.callback_query(F.data == "order:cancel")
async def order_cancel_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Заявка отменена.")
    await callback.answer()


@router.message(StateFilter(Order))
async def order_wrong_input(message: Message):
    await message.answer("Пожалуйста, ответьте текстом на вопрос выше или нажмите «❌ Отмена».")


# ---------- Свободные вопросы → Gemini ----------

@router.message(F.text)
async def free_question(message: Message, bot: Bot):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    answer, wants_order = await ai.ask(message.from_user.id, message.text)
    await message.answer(
        answer,
        parse_mode=None,
        reply_markup=kb.start_order_kb if wants_order else None,
    )
