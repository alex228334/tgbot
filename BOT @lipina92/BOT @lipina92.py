import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ChatMemberUpdated
import asyncio
import sqlite3
from database import get_user_name, init_db, add_user, save_card_data, get_card_data, get_profile_data, \
    save_profile_data
from markups import get_support_keyboard, get_change_card_keyboard

logging.basicConfig(level=logging.INFO)

TOKEN = '7575757667:AAHvxrKDy31-5_qIur_58S1x13x6vae7HVc'
CHANNEL_ID = '-1002346144227'

bot = Bot(token=TOKEN)
dp = Dispatcher()

class CardForm(StatesGroup):
    waiting_for_card_number = State()

def escape_markdown(text):
    special_chars = ['.', '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def get_profile_text(user_id, profile_data):
    user_username = escape_markdown(get_user_name(user_id))
    total_profit = escape_markdown(str(profile_data['total_profit']))
    profit_count = escape_markdown(str(profile_data['profit_count']))
    daily_profit = escape_markdown(str(profile_data['daily_profit']))
    monthly_profit = escape_markdown(str(profile_data['monthly_profit']))

    return (
        f"*🚀 Статистика: {user_username}*\n\n"
        f"_*💸 Сумма профитов: {total_profit} ₽*_\n"
        f"_*🕐 Количество профитов: {profit_count}*_\n"
        f"_*☀️ Сумма профитов за последний день: {daily_profit}₽*_\n"
        f"_*🤑 Сумма профитов за последний месяц: {monthly_profit}₽*_"
    )

@dp.message(Command("start"))
async def handle_start(message: types.Message):
    user_id = message.from_user.id
    user_name = "" + message.from_user.username if message.from_user.username else message.from_user.full_name
    add_user(user_id, user_name)
    commands_description = """
Добро Пожаловать XXNETT TEAM! 🔫Вот список доступных команд:

/mp - профиль пользователя

/tp - узнать, кто на техподдержке

/pin - закрепленное сообщение

/top - топ за всё время

/topm - топ за последний месяц

/mp - профиль пользователя
    """
    await message.reply(commands_description)

@dp.message(Command("tp"))
async def handle_tp(message: types.Message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    add_user(user_id, user_username)
    keyboard = get_support_keyboard()
    await message.reply("ТЕХ.ПОДДЕРЖКА:", reply_markup=keyboard)

@dp.message(Command("pin"))
async def handle_pin(message: types.Message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    add_user(user_id, user_username)

    chat = await bot.get_chat(CHANNEL_ID)
    pinned_message = chat.pinned_message
    if pinned_message:
        await message.reply(pinned_message.text)
    else:
        await message.reply("В канале нет закрепленного сообщения.")

@dp.message(Command("mp"))
async def handle_mp(message: types.Message):
    user_id = message.from_user.id
    user_name = "@" + message.from_user.username if message.from_user.username else message.from_user.full_name
    add_user(user_id, user_name)

    profile_data = get_profile_data(user_id)
    photos = await bot.get_user_profile_photos(user_id=user_id)

    if photos.total_count > 0:
        await message.answer_photo(
            photo=photos.photos[0][0].file_id,
            caption=get_profile_text(user_id, profile_data),
            parse_mode="MarkdownV2"
        )
    else:
        await message.reply(get_profile_text(user_id, profile_data), parse_mode="MarkdownV2")

@dp.message(Command("top"))
async def handle_top(message: types.Message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    add_user(user_id, user_username)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, total_profit FROM profile
        ORDER BY total_profit DESC
        LIMIT 10
    """)
    results = cursor.fetchall()
    conn.close()

    if results:
        top_users = "\n".join(
            [
                f"@{escape_markdown(get_user_name(user_id))}: {escape_markdown(str(total_profit))} ₽"
                for user_id, total_profit in results])

        total_profit_sum = sum(total_profit for _, total_profit in results)
        await message.reply(
            f"*🚀 Топ по сумме профитов:\n\n{top_users}*\n\n*📈Сумма профитов: {escape_markdown(str(total_profit_sum))} ₽*",
            parse_mode="MarkdownV2")
    else:
        await message.reply("📊 Нет данных о профитах.")

@dp.message(Command("topm"))
async def handle_topm(message: types.Message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    add_user(user_id, user_username)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, monthly_profit FROM profile
        ORDER BY monthly_profit DESC
        LIMIT 10
    """)
    results = cursor.fetchall()
    conn.close()

    if results:
        top_users = "\n".join(
            [
                f"@{escape_markdown(get_user_name(user_id))}: {escape_markdown(str(monthly_profit))} ₽"
                for user_id, monthly_profit in results])

        total_monthly_profit_sum = sum(monthly_profit for _, monthly_profit in results)
        await message.reply(
            f"*🚀 Топ за месяц:\n\n{top_users}*\n\n*📈Сумма профитов за месяц: {escape_markdown(str(total_monthly_profit_sum))} ₽*",
            parse_mode="MarkdownV2")
    else:
        await message.reply("📊 Нет данных о профитах.")

# Обработчик вступления нового участника в группу
@dp.chat_member()
async def on_chat_member_updated(update: ChatMemberUpdated):
    if update.new_chat_member.status == 'member':  # Проверяем, что пользователь стал участником
        user_id = update.new_chat_member.user.id
        user_name = "" + update.new_chat_member.user.username if update.new_chat_member.user.username else update.new_chat_member.user.full_name
        add_user(user_id, user_name)

        # Отправляем приветственное сообщение в саму группу
        commands_description = """
Добро Пожаловать XXNETT TEAM! 🔫Вот список доступных команд:

/mp - профиль пользователя

/tp - узнать, кто на техподдержке

/pin - закрепленное сообщение

/top - топ за всё время

/topm - топ за последний месяц

/mp - профиль пользователя
        """
        # Отправляем сообщение в группу
        await bot.send_message(CHANNEL_ID, f"Приветствуем нового участника @{user_name}! {commands_description}")

async def main():
    init_db()  # Инициализация базы данных
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
