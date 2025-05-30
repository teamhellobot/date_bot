import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from loguru import logger
from dotenv import load_dotenv
from peewee import fn
import asyncio

from database.models import Idea, User
from database.utils import initialize_db, populate_db

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

idea_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎲 Рандомное свидание")],
        [KeyboardButton(text="🌟 Заказать бота")],
    ],
    resize_keyboard=True,
)


def get_manager_keyboard():
    """Создает inline-клавиатуру с кнопкой для перехода в чат с менеджером."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Пиши нашему менеджеру — @hellobotstudio 👩‍💻",
                    url="https://t.me/hellobotstudio    ",
                )
            ]
        ]
    )


async def get_random_idea():
    """Функция для получения случайной идеи с картинкой"""
    logger.info("Fetching random idea from the database...")
    idea = Idea.select().order_by(fn.Random()).first()
    if idea:
        logger.info(f"Random idea found: {idea.text}")
    else:
        logger.warning("No ideas available in the database.")
    return idea


@dp.message(lambda message: message.text == "🌟 Заказать бота")
async def send_ofer(message: types.Message):
    """Функция для отправки контактов для заказа ботов"""
    logger.info(f"User requested bot order: {message.from_user.id}")
    user, created = User.get_or_create(
        user_id=message.from_user.id,
        defaults={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
        },
    )

    if created:
        logger.info(f"New user created: {user.user_id}")
    else:
        logger.info(f"Existing user interacted: {user.user_id}")

    welcome_text = (
        "🚀 <b>P.S.</b> Мы создаём Telegram-ботов любой сложности:\n"
        "• От лид-магнитов до сложных систем автоматизации\n"
        "• Индивидуальный подход\n"
        "• Профессиональная реализация\n\n"
        "Хочешь такого же крутого бота?"
    )

    await message.reply(
        welcome_text, reply_markup=get_manager_keyboard(), parse_mode="HTML"
    )
    logger.info(f"Bot order information sent to user: {user.user_id}")


@dp.message(Command("start", "help"))
async def send_welcome(message: types.Message):
    """Функция для отправки приветствия пользователя"""
    logger.info(f"User started the bot: {message.from_user.id}")
    user, created = User.get_or_create(
        user_id=message.from_user.id,
        defaults={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
        },
    )

    if created:
        logger.info(f"New user created: {user.user_id}")
    else:
        logger.info(f"Existing user interacted: {user.user_id}")

    welcome_text = (
        "🌟 *Привет!* 🌟\n\n"
        "Я — твой персональный бот для идеальных свиданий! 💖\n"
        "Знаю <b>50+ способов</b> как провести день не на диване "
        "и без бесконечных переписок в стиле «Куда поедем? — Не знаю, а ты?» 😏\n\n"
        "✨ *Просто нажми кнопку — и я мгновенно предложу:\n"
        "▫️ Креативную идею для свидания\n"
        "▫️ Случайную вдохновляющую картинку\n"
        "▫️ Всё в спонтанном и романтичном формате — *без мозгового штурма*! ❤️\n\n"
        "---\n"
        "🚀 <b>P.S.</b> Мы создаём Telegram-ботов любой сложности.\n"
    )

    await message.reply(welcome_text, reply_markup=idea_keyboard, parse_mode="HTML")

    await message.answer(
        "Нужен такой же бот? "
        "Есть вопросы или возникли проблемы?" 
        "Хочешь поговорить по душам?. Нажмите на кнопку ниже 👇",
        reply_markup=get_manager_keyboard(),
    )

    logger.info(f"Welcome message sent to user: {user.user_id}")


@dp.message(lambda message: message.text == "🎲 Рандомное свидание")
async def send_idea(message: types.Message):
    """Функция для отправки рандомной идеи свидания"""
    logger.info(f"User requested random date idea: {message.from_user.id}")
    try:
        await message.reply("🎲 Выбираем идеальное свидание...")

        await asyncio.sleep(2)

        idea = await get_random_idea()
        if not idea:
            logger.warning("No ideas available to send.")
            await message.reply("Идеи закончились 😢", reply_markup=idea_keyboard)
            return

        response = f"✨ Идея для свидания ✨\n\n{idea.text}\n\nХорошего время препровождения! ❤️"

        if idea.image_path and os.path.exists(idea.image_path):
            logger.info(f"Sending idea with image: {idea.text}")
            with open(idea.image_path, "rb") as photo:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=types.BufferedInputFile(photo.read(), filename="idea.jpg"),
                    caption=response,
                    reply_markup=idea_keyboard,
                )
        else:
            logger.info(f"Sending idea without image: {idea.text}")
            await message.reply(response, reply_markup=idea_keyboard)

    except Exception as e:
        logger.error(f"Unexpected error while sending idea: {type(e).__name__} - {e}")
        await message.reply(
            "Что-то пошло не так, попробуйте еще раз", reply_markup=idea_keyboard
        )


async def main():
    logger.add("bot.log", rotation="10 MB", level="INFO")
    logger.info("Starting bot...")
    initialize_db()
    populate_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())