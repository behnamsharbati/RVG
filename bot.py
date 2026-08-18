import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "سلام 👋\n"
        "به فروشگاه V2ray Valac خوش آمدید 🌐\n\n"
        "برای شروع، از منوی ربات استفاده کنید."
    )

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(
        message,
        "راهنما:\n"
        "/start - شروع ربات\n"
        "/help - راهنما"
    )

print("Bot is running...")

bot.infinity_polling()
