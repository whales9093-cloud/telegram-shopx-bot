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
conn.commit()

# ---------------- DEFAULT PRODUCTS ----------------
default_products = [
    ("rice", "₦1,500 per kg"),
    ("beans", "₦2,000 per kg"),
    ("oil", "₦3,500 per litre"),
    ("sugar", "₦1,200 per kg")
]

for product in default_products:
    cursor.execute("SELECT * FROM products WHERE name=?", (product[0],))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO products VALUES (?, ?)", product)

conn.commit()

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "👋 Welcome to Shop Bot\n\n"
        "Commands:\n"
        "- products\n"
        "- rice\n"
        "- pay\n"
        "- add noodles 2500 (admin only)"
    )

# ---------------- PRODUCTS LIST ----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "products")
def show_products(message):
    cursor.execute("SELECT * FROM products")
    items = cursor.fetchall()

    text = "🛒 Products:\n"
    for item in items:
        text += f"- {item[0]} ({item[1]})\n"

    bot.reply_to(message, text)

# ---------------- MAIN HANDLER ----------------
@bot.message_handler(func=lambda message: True)
def handle(message):
    text = message.text.lower()
    user_id = message.from_user.id

    # ---------- PAYMENT ----------
    if text == "pay":
        bot.reply_to(
            message,
            "💳 PAYMENT DETAILS\n\n"
            "Bank: Example Bank\n"
            "Account Name: Wale Shop\n"
            "Account Number: 0123456789\n\n"
            "After payment, send your reference number."
        )
        return

    # ---------- ADMIN ADD PRODUCT ----------
    if user_id == ADMIN_ID:
        if text.startswith("add"):
            try:
                parts = text.split()
                name = parts[1]
                price = parts[2]

                cursor.execute(
                    "INSERT INTO products VALUES (?, ?)",
                    (name, f"₦{price}")
                )
                conn.commit()

                bot.reply_to(message, f"✅ {name} added successfully!")
                return

            except:
                bot.reply_to(message, "❌ Use format: add noodles 2500")
                return
# ---------- ORDER SYSTEM ----------
    if text.startswith("order"):
        try:
            parts = text.split()

            product_name = parts[1]
            quantity = parts[2]

            order_id = random.randint(1000, 9999)

            bot.reply_to(
                message,
                f"✅ Order received!\n\n"
                f"Product: {product_name}\n"
                f"Quantity: {quantity}\n"
                f"Order ID: {order_id}\n\n"
                f"Type 'pay' for payment details."
            )
            return

        except:
            bot.reply_to(
                message,
                "❌ Use: order rice 2"
            )
            return
    # ---------- PRODUCT SEARCH ----------
    cursor.execute("SELECT * FROM products WHERE name=?", (text,))
    product = cursor.fetchone()

    if product:
        bot.reply_to(message, f"{product[0]} = {product[1]}")
    elif text == "hello":
        bot.reply_to(message, "Hello 👋 Type 'products'")
    else:
        bot.reply_to(message, "❌ Product not found.")

# ---------------- RUN BOT ----------------
bot.polling()
