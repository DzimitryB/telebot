import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from video_processor import download_audio_or_low_res_video, transcribe_audio  # Импортируем наши функции

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f"""
    Привет, {update.effective_user.first_name}!
    Я тестовый бот и пока у меня сииильно урезанная функциональность!!
    """
    await update.message.reply_text(message)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступные команды:\n/start - Начать\n/help - Помощь")

# Обработка обычных сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Вы сказали: {update.message.text}")

# Команда /transcribe
async def transcribe_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        url = context.args[0]
        try:
            await update.message.reply_text("Загружаю аудио...")
            audio_file = download_audio_or_low_res_video(url)
            
            await update.message.reply_text("Аудио загружено. Распознаю текст...")
            result = transcribe_audio(audio_file)
            
            await update.message.reply_text(f"Распознанный текст:\n{result}")
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {e}")
    else:
        await update.message.reply_text("Пожалуйста, отправьте ссылку на видео.")


# Основная функция
def main():
    # Замените 'YOUR_API_TOKEN' на ваш токен
    TOKEN = 'YOUR_API_TOKEN'

    # Создаем приложение
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("transcribe", transcribe_video))
    app.add_handler(MessageHandler(filters.VIDEO, transcribe_video))

    # Обрабатываем текстовые сообщения
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
