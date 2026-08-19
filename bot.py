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


bot = telebot.TeleBot(
    TOKEN,
    parse_mode="HTML"
)


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

DB_FILE = os.getenv(
    "DB_FILE",
    "v2ray_shop.db"
)

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
# DISCOUNT CODES
# =========================================================
# برای اضافه کردن کد تخفیف جدید:
#
# "CODE": درصد تخفیف
#
# مثال:
# "VALAC10": 10
#
# =========================================================

DISCOUNT_CODES = {
    "VALAC10": 10,
    "WELCOME": 5,
}


# =========================================================
# VIP SETTINGS
# =========================================================

VIP_REQUIRED_ORDERS = 5

VIP_DISCOUNT_PERCENT = 5


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(
        DB_FILE,
        check_same_thread=False,
        timeout=30
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_database():

    with DB_LOCK:

        conn = get_db()

        # USERS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                successful_orders INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        # ORDERS
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
                discount_percent INTEGER DEFAULT 0,
                discount_amount INTEGER DEFAULT 0,
                final_price INTEGER,
                server_location TEXT,
                status TEXT,
                receipt_file_id TEXT,
                config TEXT,
                created_at TEXT,
                paid_at TEXT
            )
        """)

        # Add columns to old databases if missing
        columns = {
            "discount_percent": "INTEGER DEFAULT 0",
            "discount_amount": "INTEGER DEFAULT 0",
            "config": "TEXT"
        }

        existing = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(orders)"
            ).fetchall()
        }

        for column, definition in columns.items():

            if column not in existing:

                conn.execute(
                    f"ALTER TABLE orders ADD COLUMN "
                    f"{column} {definition}"
                )

        user_columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(users)"
            ).fetchall()
        }

        if "referral_code" not in user_columns:
            conn.execute(
                "ALTER TABLE users ADD COLUMN "
                "referral_code TEXT"
            )

        if "referred_by" not in user_columns:
            conn.execute(
                "ALTER TABLE users ADD COLUMN "
                "referred_by INTEGER"
            )

        if "successful_orders" not in user_columns:
            conn.execute(
                "ALTER TABLE users ADD COLUMN "
                "successful_orders INTEGER DEFAULT 0"
            )

        conn.commit()
        conn.close()


init_database()


# =========================================================
# BASIC HELPERS
# =========================================================

def now():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def format_money(value):

    return (
        f"{value:,}"
        .replace(",", "٬")
        + " تومان"
    )


def generate_order_code():

    return (
        "VL-"
        + uuid.uuid4().hex[:8].upper()
    )


def generate_referral_code(telegram_id):

    return f"VL{telegram_id}"


def get_discount_code(code):

    if not code:
        return 0

    code = code.strip().upper()

    return DISCOUNT_CODES.get(code, 0)


def calculate_final_price(
   
