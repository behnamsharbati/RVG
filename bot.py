import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import telebot
from telebot import types


TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)


# ==========================================
# Web Server for Render
# ==========================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Bot is running!".encode("utf-8"))

    def log_message(self, format, *args):
        return


def run_web_server():
    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(f"Web server running on port {port}")

    server.serve_forever()


# ==========================================
# Main Menu
# ==========================================

def main_menu():

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

    return markup


# ==========================================
# START
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(
        message.chat.id,

        "سلام 👋 بهنام هستم.\n\n"
        "🌐 به فروشگاه V2ray Valac خوش آمدید.\n\n"
        "برای شروع، گزینه موردنظر خود را از منوی زیر انتخاب کنید:",

        reply_markup=main_menu()
    )


# ==========================================
# BUY CONFIG
# ==========================================

@bot.message_handler(
    func=lambda message: message.text == "🛒 خرید کانفیگ"
)
def buy_config(message):

    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(

        types.InlineKeyboardButton(
            "⚡ اشتراک بر سرعت ولک شاپ",
            callback_data="veloc_shop"
        ),

        types.InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="back_main"
        )

    )

    bot.send_message(
        message.chat.id,

        "🛒 خرید کانفیگ\n\n"
        "در این بخش اشتراک خود را انتخاب کنید:",

        reply_markup=markup
    )


# ==========================================
# VELOC SHOP
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data == "veloc_shop"
)
def veloc_shop(call):

    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(

        types.InlineKeyboardButton(
            "📱 همراه اول",
            callback_data="internet_mci"
        ),

        types.InlineKeyboardButton(
            "📶 Wi-Fi",
            callback_data="internet_wifi"
        ),

        types.InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="back_subscription"
        )

    )

    bot.edit_message_text(

        "⚡ اشتراک بر سرعت ولک شاپ\n\n"
        "نوع اینترنت خود را انتخاب کنید:",

        call.message.chat.id,
        call.message.message_id,

        reply_markup=markup
    )


# ==========================================
# INTERNET TYPE
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data in [
        "internet_mci",
        "internet_wifi"
    ]
)
def select_internet(call):

    bot.answer_callback_query(call.id)

    if call.data == "internet_mci":

        internet_name = "📱 همراه اول"
        prefix = "mci"

    else:

        internet_name = "📶 Wi-Fi"
        prefix = "wifi"


    markup = types.InlineKeyboardMarkup(row_width=2)


    prices = [

        ("۱۰ گیگ — ۷۰,۰۰۰ تومان", f"{prefix}_10"),
        ("۲۰ گیگ — ۱۳۸,۰۰۰ تومان", f"{prefix}_20"),

        ("۳۰ گیگ — ۲۰۴,۰۰۰ تومان", f"{prefix}_30"),
        ("۴۰ گیگ — ۲۶۸,۰۰۰ تومان", f"{prefix}_40"),

        ("۵۰ گیگ — ۳۳۰,۰۰۰ تومان", f"{prefix}_50"),
        ("۶۰ گیگ — ۳۹۰,۰۰۰ تومان", f"{prefix}_60"),

        ("۷۰ گیگ — ۴۴۸,۰۰۰ تومان", f"{prefix}_70"),
        ("۸۰ گیگ — ۵۰۴,۰۰۰ تومان", f"{prefix}_80"),

        ("۹۰ گیگ — ۵۵۸,۰۰۰ تومان", f"{prefix}_90"),
        ("۱۰۰ گیگ — ۵۹۹,۰۰۰ تومان", f"{prefix}_100")

    ]


    for text, callback in prices:

        markup.add(
            types.InlineKeyboardButton(
                text,
                callback_data=callback
            )
        )


    markup.add(
        types.InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="back_internet"
        )
    )


    bot.edit_message_text(

        f"{internet_name}\n\n"
        "📦 لطفاً حجم اشتراک خود را انتخاب کنید:",

        call.message.chat.id,
        call.message.message_id,

        reply_markup=markup
    )


# ==========================================
# SELECT CONFIG
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith(
        ("mci_", "wifi_")
    )
)
def selected_config(call):

    bot.answer_callback_query(call.id)


    parts = call.data.split("_")

    internet_type = parts[0]
    volume = parts[1]


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


    if internet_type == "mci":

        internet_name = "📱 همراه اول"

    else:

        internet_name = "📶 Wi-Fi"


    price = prices[volume]


    text = (

        "✅ سفارش شما\n\n"

        "⚡ اشتراک بر سرعت ولک شاپ\n\n"

        f"{internet_name}\n"

        f"📦 حجم اشتراک: {volume} گیگ\n"

        f"💰 مبلغ
