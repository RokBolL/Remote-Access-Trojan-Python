import os
import subprocess
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from PIL import ImageGrab
from io import BytesIO

# Настройки
TOKEN = "7669958438:AAEWPqnyFNfSr4oEBUFKNJ79F2Lrc8cixIE"
AUTHORIZED_USERS = [7244578938]  # Узнать у @userinfobot
ADMIN_PASSWORD = "pidor"  # Для дополнительной защиты

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def is_authorized(update: Update) -> bool:
    """Проверка прав доступа"""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Доступ запрещен!")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /start"""
    if not await is_authorized(update):
        return
    
    help_text = """
🖥 *Удаленный доступ к ПК*

Доступные команды:
/start - это сообщение
/cmd <команда> - выполнить команду
/screenshot - получить скриншот
/password <код> - установить пароль
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def execute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выполнение команд"""
    if not await is_authorized(update):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите команду: /cmd <команда>")
        return
    
    command = " ".join(context.args)
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout or result.stderr or "✅ Команда выполнена"
        await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def send_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка скриншота"""
    if not await is_authorized(update):
        return
    
    try:
        img = ImageGrab.grab()
        bio = BytesIO()
        img.save(bio, "PNG")
        bio.seek(0)
        await update.message.reply_photo(photo=bio)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def set_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка пароля"""
    if not context.args:
        await update.message.reply_text("❌ Укажите пароль: /password <код>")
        return
    
    global ADMIN_PASSWORD
    ADMIN_PASSWORD = " ".join(context.args)
    await update.message.reply_text("✅ Пароль обновлен")

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmd", execute_command))
    app.add_handler(CommandHandler("screenshot", send_screenshot))
    app.add_handler(CommandHandler("password", set_password))
    
    # Фильтр для текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()