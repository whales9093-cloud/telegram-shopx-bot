import telebot
import sqlite3
import random

TOKEN = "8761896381:AAGotG_C1pC5FqO_1OmDdjFOB2SJPHt4OcA"
ADMIN_ID = 7058954196  # YOUR REAL TELEGRAM ID

bot = telebot.TeleBot(TOKEN)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    name TEXT,
    price TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER,
    user_id INTEGER,
    product TEXT,
    quantity TEXT,
    payment_status TEXT,
    delivery_status TEXT
)
""") 

conn.commit()

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "🏪 SHOP BOT\n\n"
        "Commands:\n"
        "- products\n"
        "- order rice 2\n"
        "- pay\n\n"
        "Admin:\n"
        "- orders\n"
        "- approve 1234\n"
        "- delivered 1234\n"
        "- add rice 1500"
    )

# ---------------- PRODUCTS ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "products")
def products(message):
    cursor.execute("SELECT * FROM products")
    items = cursor.fetchall()

    if not items:
        bot.reply_to(message, "No products")
        return

    msg = "🛒 PRODUCTS\n\n"
    for i in items:
        msg += f"- {i[0]} = {i[1]}\n"

    bot.reply_to(message, msg)

# ---------------- PAY ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "pay")
def pay(message):
    bot.reply_to(message,
        "💳 PAYMENT DETAILS\n\n"
        "Bank: Example Bank\n"
        "Account: 0123456789\n"
        "Name: Shop Bot\n"
    )

# ---------------- ADMIN ORDERS (FIXED) ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "orders")
def orders(message):

    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Not admin")
        return

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    if not orders:
        bot.reply_to(message, "📦 No orders yet")
        return

    msg = "📦 ALL ORDERS\n\n"

    for o in orders:
        msg += (
            f"ID: {o[0]}\n"
            f"User: {o[1]}\n"
            f"Product: {o[2]}\n"
            f"Qty: {o[3]}\n"
            f"Payment: {o[4]}\n"
            f"Delivery: {o[5]}\n\n"
        )

    bot.reply_to(message, msg)

# ---------------- ADD PRODUCT ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("add"))
def add(message):

    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()

    if len(parts) < 3:
        bot.reply_to(message, "Use: add rice 1500")
        return

    name = parts[1]
    price = parts[2]

    cursor.execute("INSERT INTO products VALUES (?, ?)", (name, f"₦{price}"))
    conn.commit()

    bot.reply_to(message, f"✅ {name} added")

# ---------------- ORDER SYSTEM (FIXED) ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("order"))
def order(message):

    parts = message.text.split()

    if len(parts) < 3:
        bot.reply_to(message, "Use: order rice 2")
        return

    product = parts[1]
    qty = parts[2]

    order_id = random.randint(1000, 9999)

    cursor.execute(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
        (
            order_id,
            message.from_user.id,
            product,
            qty,
            "PENDING",
            "NOT_DELIVERED"
        )
    )

    conn.commit()

    bot.reply_to(
        message,
        f"✅ ORDER CREATED\n\n"
        f"ID: {order_id}\n"
        f"Product: {product}\n"
        f"Qty: {qty}\n"
        f"Payment: PENDING\n"
        f"Delivery: NOT_DELIVERED\n\n"
        f"Type 'pay' for payment details."
    )

# ---------------- APPROVE ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("approve"))
def approve(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        order_id = message.text.split()[1]

        cursor.execute(
            "UPDATE orders SET payment_status=? WHERE order_id=?",
            ("PAID", order_id)
        )

        conn.commit()

        bot.reply_to(
            message,
            f"✅ Order {order_id} marked as PAID"
        )

    except:
        bot.reply_to(
            message,
            "Use: approve 1234"
        )

# ---------------- DELIVERED ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("delivered"))
def delivered(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        order_id = message.text.split()[1]

        cursor.execute(
            "UPDATE orders SET delivery_status=? WHERE order_id=?",
            ("DELIVERED", order_id)
        )

        conn.commit()

        bot.reply_to(
            message,
            f"🚚 Order {order_id} marked DELIVERED"
        )

    except:
        bot.reply_to(
            message,
            "Use: delivered 1234"
        )

# ---------------- SEARCH ----------------
@bot.message_handler(func=lambda m: True)
def search(message):

    if not message.text:
        return

    text = message.text.lower()

    # ---------- HELLO FIX ----------
    if text == ["hello","hi","hey"]:
        bot.reply_to(message, "👋 Hello! Welcome to Shop Bot")
        return

    # ---------- PRODUCT SEARCH ----------
    cursor.execute("SELECT * FROM products WHERE name=?", (text,))
    product = cursor.fetchone()

    if product:
        bot.reply_to(message, f"{product[0]} = {product[1]}")
    else:
        bot.reply_to(message, "❌ Not found")

# ---------------- RUN ----------------
bot.polling()
