import telebot
import sqlite3
import random

TOKEN = "8761896381:AAGotG_C1pC5FqO_1OmDdjFOB2SJPHt4OcA"
ADMIN_ID = 7058954196  # your Telegram ID

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
    status TEXT,
    proof TEXT
)
""")

conn.commit()

# ---------------- DEFAULT PRODUCTS ----------------
default_products = [
    ("rice", "₦1500"),
    ("beans", "₦2000"),
    ("oil", "₦3500"),
    ("sugar", "₦1200")
]

for p in default_products:
    cursor.execute("SELECT * FROM products WHERE name=?", (p[0],))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO products VALUES (?, ?)", p)

conn.commit()

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "🏪 BUSINESS SHOP BOT\n\n"
        "User Commands:\n"
        "- products\n"
        "- order rice 2\n"
        "- pay\n"
        "- send proof (reply to order)\n\n"
        "Admin Commands:\n"
        "- orders\n"
        "- approve 1234\n"
        "- delivered 1234\n"
        "- delete 1234\n"
        "- add rice 1500"
    )

# ---------------- PRODUCTS ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "products")
def products(message):
    cursor.execute("SELECT * FROM products")
    items = cursor.fetchall()

    msg = "🛒 PRODUCTS\n\n"
    for i in items:
        msg += f"- {i[0]} = ₦{i[1]}\n"

    bot.reply_to(message, msg)

# ---------------- PAYMENT INFO ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "pay")
def pay(message):
    bot.reply_to(message,
        "💳 PAYMENT DETAILS\n\n"
        "Bank: Example Bank\n"
        "Account: 0123456789\n"
        "Name: BUSINESS SHOP\n\n"
        "After payment, send proof like:\n"
        'proof 1234 image_link'
    )

# ---------------- ORDER SYSTEM ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("order"))
def order(message):

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "❌ Use: order rice 2")
        return

    product = parts[1]
    qty = parts[2]
    order_id = random.randint(1000, 9999)

    cursor.execute(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
        (order_id, message.from_user.id, product, qty, "pending", "")
    )
    conn.commit()

    bot.reply_to(message,
        f"✅ ORDER CREATED\n\n"
        f"Order ID: {order_id}\n"
        f"Product: {product}\n"
        f"Qty: {qty}\n"
        f"Status: pending\n\n"
        f"Now pay and send proof"
    )

# ---------------- PAYMENT PROOF ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("proof"))
def proof(message):

    parts = message.text.split()

    if len(parts) < 3:
        bot.reply_to(message, "❌ Use: proof 1234 image_link")
        return

    order_id = parts[1]
    proof_link = parts[2]

    cursor.execute(
        "UPDATE orders SET proof=?, status='paid' WHERE order_id=?",
        (proof_link, order_id)
    )
    conn.commit()

    bot.reply_to(message, f"✅ Proof received for order {order_id}. Waiting admin approval.")

# ---------------- ADMIN PANEL ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "orders")
def admin_orders(message):

    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Not allowed")
        return

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    if not orders:
        bot.reply_to(message, "📦 No orders")
        return

    msg = "📦 ALL ORDERS\n\n"

    for o in orders:
        msg += (
            f"ID: {o[0]}\n"
            f"User: {o[1]}\n"
            f"Product: {o[2]}\n"
            f"Qty: {o[3]}\n"
            f"Status: {o[4]}\n"
            f"Proof: {o[5]}\n\n"
        )

    bot.reply_to(message, msg)

# ---------------- APPROVE PAYMENT ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("approve"))
def approve(message):

    if message.from_user.id != ADMIN_ID:
        return

    order_id = message.text.split()[1]

    cursor.execute(
        "UPDATE orders SET status='approved' WHERE order_id=?",
        (order_id,)
    )
    conn.commit()

    bot.reply_to(message, f"✅ Order {order_id} approved")

# ---------------- MARK DELIVERED ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("delivered"))
def delivered(message):

    if message.from_user.id != ADMIN_ID:
        return

    order_id = message.text.split()[1]

    cursor.execute(
        "UPDATE orders SET status='delivered' WHERE order_id=?",
        (order_id,)
    )
    conn.commit()

    bot.reply_to(message, f"🚚 Order {order_id} delivered")

# ---------------- ADD PRODUCT ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("add"))
def add_product(message):

    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()

    if len(parts) < 3:
        bot.reply_to(message, "❌ Use: add rice 1500")
        return

    name = parts[1]
    price = parts[2]

    cursor.execute("INSERT INTO products VALUES (?, ?)", (name, price))
    conn.commit()

    bot.reply_to(message, f"✅ {name} added")

# ---------------- SEARCH PRODUCT ----------------
@bot.message_handler(func=lambda m: True)
def search(message):

    if not message.text:
        return

    text = message.text.lower()

    cursor.execute("SELECT * FROM products WHERE name=?", (text,))
    product = cursor.fetchone()

    if product:
        bot.reply_to(message, f"{product[0]} = ₦{product[1]}")
    elif text == "hello":
        bot.reply_to(message, "👋 Welcome to Business Shop Bot")

# ---------------- RUN BOT ----------------
bot.polling()
