import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)


# =========================
# /start
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton("🛒 خرید کانفیگ"),
        types.KeyboardButton("📦 کانفیگ‌های من")
    )

    markup.add(
        types.KeyboardButton("💳 پیگیری سفارش"),
        types.KeyboardButton("🎁 کد تخفیف")
    )

    markup.add(
        types.KeyboardButton("👤 پشتیبانی")
    )

    bot.send_message(
        message.chat.id,
        "سلام 👋\n\n"
        "🌐 به فروشگاه V2ray Valac خوش آمدید.\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=markup
    )


# =========================
# خرید کانفیگ
# =========================

@bot.message_handler(
    func=lambda message: message.text == "🛒 خرید کانفیگ"
)
def buy_config(message):

    markup = types.InlineKeyboardMarkup(row_width=2)

    prices = [
        ("۱۰ گیگ — ۷۰,۰۰۰ تومان", "buy_10"),
        ("۲۰ گیگ — ۱۳۸,۰۰۰ تومان", "buy_20"),
        ("۳۰ گیگ — ۲۰۴,۰۰۰ تومان", "buy_30"),
        ("۴۰ گیگ — ۲۶۸,۰۰۰ تومان", "buy_40"),
        ("۵۰ گیگ — ۳۳۰,۰۰۰ تومان", "buy_50"),
        ("۶۰ گیگ — ۳۹۰,۰۰۰ تومان", "buy_60"),
        ("۷۰ گیگ — ۴۴۸,۰۰۰ تومان", "buy_70"),
        ("۸۰ گیگ — ۵۰۴,۰۰۰ تومان", "buy_80"),
        ("۹۰ گیگ — ۵۵۸,۰۰۰ تومان", "buy_90"),
        ("۱۰۰ گیگ — ۵۹۹,۰۰۰ تومان", "buy_100")
    ]

    for text, callback in prices:
        markup.add(
            types.InlineKeyboardButton(
                text,
                callback_data=callback
            )
        )

    bot.send_message(
        message.chat.id,
        "🛒 لیست قیمت کانفیگ‌ها\n\n"
        "لطفاً حجم موردنظر خود را انتخاب کنید:",
        reply_markup=markup
    )


# =========================
# انتخاب حجم
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_")
)
def selected_config(call):

    volume = call.data.replace("buy_", "")

    prices = {
        "10": "۷۰,۰۰۰ تومان",
        "20": "۱۳۸,۰۰۰ تومان",
        "30": "۲۰۴,۰۰۰ تومان",
        "40": "۲۶۸,۰۰۰ تومان",
        "50": "۳۳۰,۰۰۰ تومان",
        "60": "۳۹۰,۰۰۰ تومان",
        "70": "۴۴۸,۰۰۰ تومان",
        "80": "۵۰۴,۰۰۰ تومان",
        "90": "۵۵۸,۰۰۰ تومان",
        "100": "۵۹۹,۰۰۰ تومان"
    }

    bot.answer_callback_query(call.id)

    price = prices.get(volume)

    text = (
        f"✅ حجم انتخابی: {volume} گیگ\n"
        f"💰 مبلغ: {price}\n\n"
        "💳 اطلاعات پرداخت:\n\n"
        "شماره کارت:\n"
        "۵۰۲۲۲۹۱۵۴۴۵۰۷۴۵۰\n\n"
        "👤 بهنام شربتی نوکنده\n"
        "🏦 بانک پاسارگاد\n\n"
        "📞 پس از پرداخت، رسید و اطلاعات سفارش "
        "را برای پشتیبانی ارسال کنید:\n"
        "@V2rayngvalac"
    )

    bot.send_message(
        call.message.chat.id,
        text
    )


# =========================
# کانفیگ‌های من
# =========================

@bot.message_handler(
    func=lambda message: message.text == "📦 کانفیگ‌های من"
)
def my_configs(message):

    bot.send_message(
        message.chat.id,
        "📦 هنوز کانفیگی برای حساب شما ثبت نشده است."
    )


# =========================
# پیگیری سفارش
# =========================

@bot.message_handler(
    func=lambda message: message.text == "💳 پیگیری سفارش"
)
def orders(message):

    bot.send_message(
        message.chat.id,
        "💳 لطفاً شماره سفارش خود را برای پشتیبانی ارسال کنید:\n\n"
        "@V2rayngvalac"
    )


# =========================
# کد تخفیف
# =========================

@bot.message_handler(
    func=lambda message: message.text == "🎁 کد تخفیف"
)
def discount(message):

    bot.send_message(
        message.chat.id,
        "🎁 اگر کد تخفیف دارید، کد را ارسال کنید."
    )


# =========================
# پشتیبانی
# =========================

@bot.message_handler(
    func=lambda message: message.text == "👤 پشتیبانی"
)
def support(message):

    bot.send_message(
        message.chat.id,
        "👤 پشتیبانی فروشگاه V2ray Valac\n\n"
        "📞 آیدی پشتیبانی:\n"
        "@V2rayngvalac"
    )


# =========================
# Help
# =========================

@bot.message_handler(commands=["help"])
def help_command(message):

    bot.send_message(
        message.chat.id,
        "راهنمای ربات 🌐\n\n"
        "/start - نمایش منوی اصلی\n"
        "/help - نمایش راهنما"
    )


# =========================
# Run Bot
# =========================

print("Bot is running...")

bot.infinity_polling()
