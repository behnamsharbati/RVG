import os
import sqlite3
import threading
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import telebot
from telebot import types


# =========================================================
# SETTINGS
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID environment variable is not set")

try:
    ADMIN_ID = int(ADMIN_ID)
except ValueError:
    raise RuntimeError("ADMIN_ID must be numeric")


bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# =========================================================
# SHOP SETTINGS
# =========================================================

SHOP_NAME = "V2ray Valac"

SERVER_LOCATION = "🇺🇸 آمریکا"

SUPPORT_USERNAME = "@V2rayngvalac"
SUPPORT_URL = "https://t.me/V2rayngvalac"

CARD_NUMBER = "۵۰۲۲۲۹۱۵۴۴۵۰۷۴۵۰"
CARD_OWNER = "بهنام شربتی نوکنده"
BANK_NAME = "پاسارگاد"

DB_FILE = "v2ray_shop.db"

DB_LOCK = threading.Lock()


# =========================================================
# PRICES
# =========================================================

PRICES = {
    10: 70000,
    20: 138000,
    30: 204000,
    40: 268000,
    50: 330000,
    60: 390000,
    70: 448000,
    80: 504000,
    90: 558000,
    100: 599000,
}


# =========================================================
# DATABASE
# =========================================================

def get_db():

    conn = sqlite3.connect(
        DB_FILE,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_database():

    with DB_LOCK:

        conn = get_db()

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_code TEXT UNIQUE,
                telegram_id INTEGER,
                username TEXT,
                first_name TEXT,
                internet_type TEXT,
                volume INTEGER,
                price INTEGER,
                final_price INTEGER,
                server_location TEXT,
                status TEXT,
                receipt_file_id TEXT,
                created_at TEXT,
                paid_at TEXT
            )
        """)

        conn.commit()
        conn.close()


init_database()


# =========================================================
# HELPERS
# =========================================================

def now():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def format_money(value):

    return f"{value:,}".replace(",", "٬") + " تومان"


def save_user(user):

    with DB_LOCK:

        conn = get_db()

        conn.execute("""
            INSERT INTO users (
                telegram_id,
                username,
                first_name,
                last_name,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(telegram_id)
            DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_name=excluded.last_name
        """, (
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            now()
        ))

        conn.commit()
        conn.close()


def generate_order_code():

    return "VL-" + uuid.uuid4().hex[:8].upper()


def get_order(order_code):

    with DB_LOCK:

        conn = get_db()

        row = conn.execute(
            """
            SELECT *
            FROM orders
            WHERE order_code=?
            """,
            (order_code,)
        ).fetchone()

        conn.close()

    return row


# =========================================================
# HEALTH SERVER - RENDER
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
        f"Health server running on port {port}"
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
        types.KeyboardButton("💳 سفارش‌های من"),
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

    save_user(message.from_user)

    first_name = (
        message.from_user.first_name
        or "دوست عزیز"
    )

    text = (
        f"🌸 <b>سلام {first_name}!</b>\n\n"
        f"به <b>{SHOP_NAME}</b> خوش اومدی 💜\n\n"
        "🚀 فروش کانفیگ V2Ray\n"
        "🇺🇸 سرور آمریکا\n"
        "⚡ تحویل سریع\n"
        "🔐 سرویس مطمئن\n"
        "💎 پشتیبانی آنلاین\n\n"
        "👇 از منوی زیر انتخاب کن:"
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
    func=lambda m: m.text == "🛒 خرید کانفیگ"
)
def buy_config(message):

    markup = types.InlineKeyboardMarkup(
        row_width=1
    )

    markup.add(
        types.InlineKeyboardButton(
            "⚡ اشتراک بر سرعت ولک شاپ",
            callback_data="veloc_shop"
        ),
        types.InlineKeyboardButton(
            "🇺🇸 سرور آمریکا",
            callback_data="veloc_shop"
        ),
        types.InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="back_main"
        )
    )

    bot.send_message(
        message.chat.id,
        "🛒 <b>خرید کانفیگ</b>\n\n"
        "🇺🇸 سرور آمریکا\n\n"
        "سرویس موردنظر را انتخاب کن:",
        reply_markup=markup
    )


# =========================================================
# SERVER / SHOP
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "veloc_shop"
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
        "🇺🇸 سرور آمریکا\n\n"
        "نوع اینترنت خود را انتخاب کن:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )


# =========================================================
# INTERNET
# =========================================================

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

    markup = types.InlineKeyboardMarkup(
        row_width=2
    )

    for volume, price in PRICES.items():

        markup.add(
            types.InlineKeyboardButton(
                f"📦 {volume} گیگ — {format_money(price)}",
                callback_data=f"{prefix}_{volume}"
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="veloc_shop"
        )
    )

    bot.edit_message_text(
        f"{internet_name}\n\n"
        "🇺🇸 <b>سرور آمریکا</b>\n\n"
        "📦 حجم اشتراک را انتخاب کن:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )


# =========================================================
# SELECT VOLUME
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith(
        ("mci_", "wifi_")
    )
)
def selected_volume(call):

    bot.answer_callback_query(call.id)

    parts = call.data.split("_")

    internet_type = parts[0]
    volume = int(parts[1])

    price = PRICES.get(volume)

    if not price:

        bot.answer_callback_query(
            call.id,
            "❌ حجم نامعتبر است.",
            show_alert=True
        )

        return

    if internet_type == "mci":

        internet_name = "📱 همراه اول"

    else:

        internet_name = "📶 Wi-Fi"

    order_code = generate_order_code()

    first_name = (
        call.from_user.first_name
        or "مشتری"
    )

    username = (
        call.from_user.username
        or ""
    )

    with DB_LOCK:

        conn = get_db()

        conn.execute("""
            INSERT INTO orders (
                order_code,
                telegram_id,
                username,
                first_name,
                internet_type,
                volume,
                price,
                final_price,
                server_location,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_code,
            call.from_user.id,
            username,
            first_name,
            internet_name,
            volume,
            price,
            price,
            SERVER_LOCATION,
            "awaiting_payment",
            now()
        ))

        conn.commit()
        conn.close()

    text = (
        "🧾 <b>سفارش شما</b>\n\n"
        f"🔢 شماره سفارش:\n"
        f"<code>{order_code}</code>\n\n"
        f"⚡ سرویس: بر سرعت ولک شاپ\n"
        f"{internet_name}\n"
        f"📦 حجم: <b>{volume} گیگ</b>\n"
        f"🇺🇸 سرور: <b>آمریکا</b>\n"
        f"💰 مبلغ: <b>{format_money(price)}</b>\n\n"
        "━━━━━━━━━━━━━━\n"
        "💳 <b>اطلاعات پرداخت</b>\n"
        "━━━━━━━━━━━━━━\n\n"
        f"💳 شماره کارت:\n"
        f"<code>{CARD_NUMBER}</code>\n\n"
        f"👤 صاحب کارت:\n"
        f"{CARD_OWNER}\n\n"
        f"🏦 بانک:\n"
        f"{BANK_NAME}\n\n"
        "⚠️ لطفاً مبلغ دقیق سفارش را واریز کن.\n\n"
        "بعد از پرداخت، عکس رسید را برای ربات ارسال کن.\n"
        "رسید برای پشتیبانی ارسال می‌شود و بعد از بررسی، "
        "سفارش تأیید خواهد شد.\n\n"
        f"🆘 پشتیبانی: {SUPPORT_USERNAME}"
    )

    markup = types.InlineKeyboardMarkup(
        row_width=1
    )

    markup.add(
        types.InlineKeyboardButton(
            "📸 ارسال رسید پرداخت",
            callback_data=f"receipt_{order_code}"
        ),
        types.InlineKeyboardButton(
            "🆘 پشتیبانی",
            url=SUPPORT_URL
        ),
        types.InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data=f"internet_{internet_type}"
        )
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )


# =========================================================
# RECEIPT REQUEST
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("receipt_")
)
def request_receipt(call):

    bot.answer_callback_query(call.id)

    order_code = call.data.replace(
        "receipt_",
        ""
    )

    order = get_order(order_code)

    if not order:

        bot.send_message(
            call.message.chat.id,
            "❌ سفارش پیدا نشد."
        )

        return

    if order["telegram_id"] != call.from_user.id:

        bot.answer_callback_query(
            call.id,
            "⛔ این سفارش متعلق به شما نیست.",
            show_alert=True
        )

        return

    bot.send_message(
        call.message.chat.id,
        "📸 <b>ارسال رسید پرداخت</b>\n\n"
        f"🔢 سفارش: <code>{order_code}</code>\n\n"
        "لطفاً عکس واضح رسید پرداخت را همینجا ارسال کن.\n\n"
        "📨 بعد از ارسال، رسید به صورت خودکار برای پشتیبانی "
        "فرستاده می‌شود."
    )

    bot.register_next_step_handler(
        call.message,
        receive_receipt,
        order_code
    )


# =========================================================
# RECEIVE RECEIPT
# =========================================================

def receive_receipt(message, order_code):

    order = get_order(order_code)

    if not order:

        bot.send_message(
            message.chat.id,
            "❌ سفارش پیدا نشد."
        )

        return

    if order["telegram_id"] != message.from_user.id:

        bot.send_message(
            message.chat.id,
            "⛔ این سفارش متعلق به شما نیست."
        )

        return

    if message.content_type != "photo":

        bot.send_message(
            message.chat.id,
            "⚠️ لطفاً فقط عکس رسید پرداخت را ارسال کن."
        )

        bot.register_next_step_handler(
            message,
            receive_receipt,
            order_code
        )

        return

    receipt_file_id = message.photo[-1].file_id

    with DB_LOCK:

        conn = get_db()

        conn.execute("""
            UPDATE orders
            SET receipt_file_id=?,
                status='receipt_submitted'
            WHERE order_code=?
        """, (
            receipt_file_id,
            order_code
        ))

        conn.commit()
        conn.close()

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "ندارد"
    )

    admin_text = (
        "🚨 <b>رسید پرداخت جدید</b>\n\n"
        f"🔢 سفارش: <code>{order_code}</code>\n"
        f"👤 نام مشتری: {message.from_user.first_name or 'نامشخص'}\n"
        f"👤 Username: {username}\n"
        f"🆔 Telegram ID: <code>{message.from_user.id}</code>\n\n"
        f"📦 حجم: {order['volume']} گیگ\n"
        f"🌐 اینترنت: {order['internet_type']}\n"
        f"🇺🇸 سرور: آمریکا\n"
        f"💰 مبلغ: {format_money(order['final_price'])}\n\n"
        "👇 رسید را بررسی کن:"
    )

    markup = types.InlineKeyboardMarkup(
        row_width=2
    )

    markup.add(
        types.InlineKeyboardButton(
            "✅ تأیید پرداخت",
            callback_data=f"approve_{order_code}"
        ),
        types.InlineKeyboardButton(
            "❌ رد پرداخت",
            callback_data=f"reject_{order_code}"
        )
    )

    bot.send_photo(
        ADMIN_ID,
        receipt_file_id,
        caption=admin_text,
        reply_markup=markup
    )

    bot.send_message(
        message.chat.id,
        "✅ <b>رسید با موفقیت دریافت شد.</b>\n\n"
        f"🔢 سفارش: <code>{order_code}</code>\n\n"
        "📨 رسید برای پشتیبانی ارسال شد.\n"
        "⏳ وضعیت: در انتظار بررسی\n\n"
