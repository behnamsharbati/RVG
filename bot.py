import os
import uuid
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import telebot
from telebot import types


# =========================================================
# SETTINGS
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

ADMIN_ID = os.getenv("ADMIN_ID")

if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID environment variable is not set")

ADMIN_ID = int(ADMIN_ID)

SUPPORT_USERNAME = "V2rayngvalac"
CARD_NUMBER = "5022291544507450"
CARD_OWNER = "بهنام شربتی نوکنده"
BANK_NAME = "بانک پاسارگاد"

DATABASE = "valac.db"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# =========================================================
# PRODUCTS
# =========================================================

PRODUCTS = {
    "10": 70000,
    "20": 138000,
    "30": 204000,
    "40": 268000,
    "50": 330000,
    "60": 390000,
    "70": 448000,
    "80": 504000,
    "90": 558000,
    "100": 599000,
}

DISCOUNT_CODES = {
    "VALAC10": 10,
    "VALAC20": 20,
}


# =========================================================
# DATABASE
# =========================================================

def get_db():
    connection = sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            referral_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE,
            telegram_id INTEGER,
            first_name TEXT,
            username TEXT,
            internet_type TEXT,
            volume INTEGER,
            price INTEGER,
            discount INTEGER DEFAULT 0,
            final_price INTEGER,
            server TEXT,
            status TEXT DEFAULT 'waiting_payment',
            config TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.commit()
    db.close()


# =========================================================
# HELPERS
# =========================================================

def format_price(price):
    return f"{price:,} تومان"


def generate_order_code():
    return "VL-" + uuid.uuid4().hex[:8].upper()


def generate_referral_code(telegram_id):
    return f"VL{telegram_id}"


def get_discount_code(code):
    if not code:
        return 0

    code = code.strip().upper()

    return DISCOUNT_CODES.get(code, 0)


def calculate_final_price(price, discount_code=None):
    discount_percent = get_discount_code(discount_code)

    if discount_percent <= 0:
        return price, 0

    discount_amount = int(price * discount_percent / 100)

    final_price = max(
        price - discount_amount,
        0
    )

    return final_price, discount_percent


def get_user_name(message):
    first_name = message.from_user.first_name

    if first_name:
        return first_name

    return "دوست عزیز"


def save_user(message):
    db = get_db()

    telegram_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    username = message.from_user.username or ""
    referral_code = generate_referral_code(telegram_id)

    db.execute("""
        INSERT OR REPLACE INTO users
        (
            telegram_id,
            first_name,
            username,
            referral_code
        )
        VALUES (?, ?, ?, ?)
    """, (
        telegram_id,
        first_name,
        username,
        referral_code
    ))

    db.commit()
    db.close()


def create_order(
    message,
    internet_type,
    volume,
    discount_code=None
):
    volume = str(volume)

    price = PRODUCTS[volume]

    final_price, discount_percent = calculate_final_price(
        price,
        discount_code
    )

    order_code = generate_order_code()

    first_name = message.from_user.first_name or ""
    username = message.from_user.username or ""

    db = get_db()

    db.execute("""
        INSERT INTO orders
        (
            order_code,
            telegram_id,
            first_name,
            username,
            internet_type,
            volume,
            price,
            discount,
            final_price,
            server
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_code,
        message.from_user.id,
        first_name,
        username,
        internet_type,
        int(volume),
        price,
        discount_percent,
        final_price,
        "USA"
    ))

    db.commit()
    db.close()

    return order_code, price, final_price, discount_percent


# =========================================================
# WEB SERVER FOR RENDER
# =========================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )

        self.end_headers()

        self.wfile.write(
            "V2ray Valac Bot is running!".encode("utf-8")
        )

    def log_message(self, format, *args):
        return


def run_web_server():

    port = int(
        os.environ.get(
            "PORT",
            "10000"
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(
        f"Web server running on port {port}"
    )

    server.serve_forever()


# =========================================================
# MAIN MENU
# =========================================================

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


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    save_user(message)

    name = get_user_name(message)

    text = (
        f"سلام <b>{name}</b> 👋🌸\n\n"
        "💜 به فروشگاه <b>V2ray Valac</b> خوش اومدی.\n\n"
        "🇺🇸 سرور سرویس‌ها: <b>آمریکا</b>\n\n"
        "🛒 از منوی زیر می‌تونی سرویس موردنظرت رو انتخاب کنی."
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu()
    )


# =========================================================
# BUY
# =========================================================

@bot.message_handler(
    func=lambda message:
    message.text == "🛒 خرید کانفیگ"
)
def buy_config(message):

    markup = types.InlineKeyboardMarkup(
        row_width=1
    )

    markup.add(
        types.InlineKeyboardButton(
            "⚡ اشتراک بر سرعت ولک شاپ",
            callback_data="veloc_shop"
        )
    )

    bot.send_message(
        message.chat.id,
        "🛒 <b>خرید کانفیگ</b>\n\n"
        "نوع سرویس خود را انتخاب کنید:",
        reply_markup=markup
    )


# =========================================================
# VELOC SHOP
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data == "veloc_shop"
)
def veloc_shop(call):

    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup(
        row_width=1
    )

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
            callback_data="back_main"
        )
    )

    bot.edit_message_text(
        "⚡ <b>اشتراک بر سرعت ولک شاپ</b>\n\n"
        "🇺🇸 سرور: <b>آمریکا</b>\n\n"
        "نوع اینترنت را انتخاب کنید:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )


# =========================================================
# INTERNET TYPE
# =========================================================

def internet_keyboard(prefix):

    markup = types.InlineKeyboardMarkup(
        row_width=2
    )

    for volume, price in PRODUCTS.items():

        text = (
            f"{volume} گیگ — "
            f"{format_price(price)}"
        )

        markup.add(
            types.InlineKeyboardButton(
                text,
                callback_data=f"{prefix}_{volume}"
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="veloc_shop"
        )
    )

    return markup


@bot.callback_query_handler(
    func=lambda call:
    call.data in [
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

    bot.edit_message_text(
        f"{internet_name}\n\n"
        "🇺🇸 سرور: <b>آمریکا</b>\n\n"
        "📦 حجم موردنظر خود را انتخاب کنید:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=internet_keyboard(prefix)
    )


# =========================================================
# SELECT CONFIG
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith(("mci_", "wifi_"))
)
def selected_config(call):

    bot.answer_callback_query(call.id)

    parts = call.data.split("_")

    internet_type = parts[0]
    volume = parts[1]

    if volume not in PRODUCTS:
        return

    if internet_type == "mci":

        internet_name = "📱 همراه اول"

    else:

        internet_name = "📶 Wi-Fi"

    price = PRODUCTS[volume]

    markup = types.InlineKeyboardMarkup(
        row_width=1
    )

    markup.add(
        types.InlineKeyboardButton(
            "🎁 وارد کردن کد تخفیف",
            callback_data=f"discount_{internet_type}_{volume}"
        ),
        types.InlineKeyboardButton(
            "💳 ادامه سفارش",
            callback_data=f"order_{internet_type}_{volume}"
        ),
        types.InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data=f"internet_{internet_type}"
        )
    )

    text = (
        "🛒 <b>جزئیات سرویس</b>\n\n"
        f"{internet_name}\n"
        "🇺🇸 سرور: <b>آمریکا</b>\n"
        f"📦 حجم: <b>{volume} گیگ</b>\n"
        f"💰 قیمت: <b>{format_price(price)}</b>\n\n"
        "برای ادامه،
