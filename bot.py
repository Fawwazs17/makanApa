from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ConversationHandler
)
from typing import Final
from datetime import datetime
import json
import sqlite3
import os
import logging


# Configure logging
class NoHttpRequestFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith("HTTP Request:")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__) # Get logger instance
logger.setLevel(logging.DEBUG) # Set logger level to DEBUG to capture debug logs as well
logger.addFilter(NoHttpRequestFilter()) # Add filter to logger

from dotenv import load_dotenv

load_dotenv()

# Define states for the conversation
(
    CHOOSING_SERVICE,
    CHOOSING_FROM_CATEGORY,
    CHOOSING_FROM_MAHALLAH,
    TYPING_FROM_LOCATION,
    CHOOSING_TO_CATEGORY,
    CHOOSING_TO_MAHALLAH,
    TYPING_TO_LOCATION,
    CONFIRMING_ORDER
) = range(8)

# Constants
BOT_TOKEN: Final = os.getenv('BOT_TOKEN')
RUNNER_GROUP_ID: Final = os.getenv('RUNNER_GROUP_ID')
ORDERS_FILE = 'data/order_counter.json'
SISTER_MAHALLAHS = ["Safiyyah", "Ruqayyah", "Sumayyah", "Asiah", "Aminah", "Halimah", "Salahudin", "Maryam", "Nusaibah", "Hafsah"]
BROTHER_MAHALLAHS = ["Zubair", "Ali", "Siddiq", "Uthman", "Farouq", "Bilal", "Salahudin"]

# Database connection
def get_db_connection():
    conn = sqlite3.connect('data/makanApa.db')
    conn.row_factory = sqlite3.Row
    return conn

# Get next order counter
def get_next_counter():
    logger.debug(f"Reading order counter from {ORDERS_FILE}")
    try:
        with open(ORDERS_FILE, 'r') as f:
            counter = json.load(f)
    except FileNotFoundError:
        counter = {"count": 0}
    counter["count"] += 1
    logger.debug(f"Writing updated order counter to {ORDERS_FILE}: {counter}")
    with open(ORDERS_FILE, 'w') as f:
        json.dump(counter, f)
    return counter["count"]

# Start command handler
import os
import json

async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot.")
    devlist_path = 'data/devlist.json'

    if os.path.exists(devlist_path):
        with open(devlist_path, 'r') as f:
            devlist = json.load(f)

        if user_id not in devlist:
            logger.warning(f"User {user_id} is not authorized to use the bot.")
            await update.message.reply_text("You are not authorized to use this bot.")
            return ConversationHandler.END
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Customers WHERE user_id=?", (user_id,))
        customer = cursor.fetchone()
        conn.close()

        if customer and customer['is_blocked']:
            logger.warning(f"User {user_id} is blocked from using the service.")
            await update.message.reply_text("You have been blocked from using the service.")
            return ConversationHandler.END

    logger.info(f"User {user_id} is authorized to use the bot.")
    keyboard = [
        [InlineKeyboardButton("🍔 Food Delivery", callback_data='food'),
         InlineKeyboardButton("📦 Item Delivery", callback_data='item')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to *makanApa Bot*! Your go-to e-hailing service within IIUM.\n\n"
        "Need something delivered? Choose a service below:",
        reply_markup=reply_markup,
        parse_mode="Markdown" # Enable Markdown for formatting
    )
    return CHOOSING_SERVICE


# Choose delivery type handler
async def choose_delivery(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    delivery_type = query.data
    context.user_data['delivery_type'] = delivery_type
    logger.info(f"User {query.from_user.id} chose delivery type: {delivery_type}")

    keyboard = [
        [InlineKeyboardButton("Sister Mahallah", callback_data='sister')],
        [InlineKeyboardButton("Brother Mahallah", callback_data='brother')],
        [InlineKeyboardButton("In UIA", callback_data='in_uia')],
        [InlineKeyboardButton("Outside UIA", callback_data='outside_uia')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "Please choose the PICKUP location:",
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    return CHOOSING_FROM_CATEGORY

# Choose from location category handler
async def choose_from_category(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    category = query.data
    context.user_data['from_category'] = category
    logger.info(f"User {query.from_user.id} chose pickup category: {category}")

    if category in ['sister', 'brother']:
        mahallahs = SISTER_MAHALLAHS if category == 'sister' else BROTHER_MAHALLAHS
        keyboard = [[InlineKeyboardButton(name, callback_data=f"from_{name}")] for name in mahallahs]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Please choose the specific Mahallah:", reply_markup=reply_markup)
        return CHOOSING_FROM_MAHALLAH
    else:
        await query.edit_message_text(
            "Please type the PICKUP location:",
            parse_mode="HTML"
        )
        return TYPING_FROM_LOCATION

# Handle specific mahallah selection for pickup
async def handle_from_mahallah(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    mahallah = query.data.replace('from_', '')
    context.user_data['from_location'] = mahallah
    logger.info(f"User {query.from_user.id} chose pickup mahallah: {mahallah}")

    keyboard = [
        [InlineKeyboardButton("Sister Mahallah", callback_data='to_sister')],
        [InlineKeyboardButton("Brother Mahallah", callback_data='to_brother')],
        [InlineKeyboardButton("In UIA", callback_data='to_in_uia')],
        [InlineKeyboardButton("Outside UIA", callback_data='to_outside_uia')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Please choose the DELIVERY location:", parse_mode="HTML", reply_markup=reply_markup)
    return CHOOSING_TO_CATEGORY

# Handle custom typed pickup location
async def handle_custom_from_location(update: Update, context: CallbackContext) -> int:
    from_location = update.message.text
    context.user_data['from_location'] = from_location
    logger.info(f"User {update.effective_user.id} typed pickup location: {from_location}")

    keyboard = [
        [InlineKeyboardButton("Sister Mahallah", callback_data='to_sister')],
        [InlineKeyboardButton("Brother Mahallah", callback_data='to_brother')],
        [InlineKeyboardButton("In UIA", callback_data='to_in_uia')],
        [InlineKeyboardButton("Outside UIA", callback_data='to_outside_uia')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose the DELIVERY location:", parse_mode="HTML", reply_markup=reply_markup)
    return CHOOSING_TO_CATEGORY

# Choose to location category handler
async def choose_to_category(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    category = query.data.replace('to_', '')
    context.user_data['to_category'] = category
    logger.info(f"User {query.from_user.id} chose delivery category: {category}")

    if category in ['sister', 'brother']:
        mahallahs = SISTER_MAHALLAHS if category == 'sister' else BROTHER_MAHALLAHS
        keyboard = [[InlineKeyboardButton(name, callback_data=f"to_{name}")] for name in mahallahs]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Please choose the specific DELIVERY Mahallah:",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        return CHOOSING_TO_MAHALLAH
    else:
        await query.edit_message_text(
            "Please type the DELIVERY location:",
            parse_mode="HTML"
        )
        return TYPING_TO_LOCATION

# Handle specific mahallah selection for delivery
async def handle_to_mahallah(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    mahallah = query.data.replace('to_', '')
    context.user_data['to_location'] = mahallah
    logger.info(f"User {query.from_user.id} chose delivery mahallah: {mahallah}")
    await display_order_summary(query, context)
    return CONFIRMING_ORDER

# Handle custom typed delivery location
async def handle_custom_to_location(update: Update, context: CallbackContext) -> int:
    to_location = update.message.text
    context.user_data['to_location'] = to_location
    logger.info(f"User {update.effective_user.id} typed delivery location: {to_location}")
    await display_order_summary(update, context)
    return CONFIRMING_ORDER

# Display order summary and confirmation buttons
async def display_order_summary(update: Update, context: CallbackContext) -> None:
    summary = (
        "📋 Order Summary:\n"
        f"Delivery Type: {context.user_data['delivery_type'].capitalize()}\n"
        f"From: {context.user_data['from_location']}\n"
        f"To: {context.user_data['to_location']}\n\n"
        "Would you like to confirm this order?"
    )
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data='confirm'),
            InlineKeyboardButton("❌ Cancel", callback_data='cancel')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if isinstance(update, Update):
        await update.message.reply_text(summary, reply_markup=reply_markup)
    else:  # CallbackQuery
        await update.edit_message_text(summary, reply_markup=reply_markup)

# Handle order confirmation and post to runner group
async def handle_confirmation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == 'confirm':
        user_id = update.effective_user.id
        username = update.effective_user.username

        # Check if customer is already in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Customers WHERE user_id=?", (user_id,))
        customer = cursor.fetchone()
        if not customer:
            cursor.execute("INSERT INTO Customers (user_id, username) VALUES (?, ?)", (user_id, username))
            logger.debug(f"New customer inserted: user_id={user_id}, username={username}")
        conn.commit()

        order_data = {
            "customer_id": user_id,
            "delivery_type": context.user_data['delivery_type'],
            "from_location": context.user_data['from_location'],
            "to_location": context.user_data['to_location']
        }

        # Generate order ID with timestamp and counter
        counter = get_next_counter()
        order_id = f"{datetime.now().strftime('%y%m%d_%H%M%S')}_{counter}"
        logger.info(f"Order ID generated: {order_id} for user {user_id}")

        # Insert order into database
        cursor.execute('''
            INSERT INTO Orders (id, customer_id, delivery_type, from_location, to_location)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_id, order_data['customer_id'], order_data['delivery_type'], order_data['from_location'], order_data['to_location']))
        conn.commit()
        logger.debug(f"New order inserted: order_id={order_id}, customer_id={order_data['customer_id']}")

        # Create message for runner group
        runner_message = (
            f"🆕 New Order #{order_id}\n\n"
            f"Type  : {order_data['delivery_type'].capitalize()}\n"
            f"From : {order_data['from_location']}\n"
            f"To      : {order_data['to_location']}\n"
            f"Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Create accept button for runners
        keyboard = [[InlineKeyboardButton("Accept Order", callback_data=f"accept_{order_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            # Send to runner group and get the message object
            runner_message_obj = await context.bot.send_message(
                chat_id=RUNNER_GROUP_ID,
                text=runner_message,
                reply_markup=reply_markup
            )
            logger.info(f"Order ID: {order_id} sent to runner group.")

            # Notify customer and keep order details visible
            message = await query.edit_message_text(
                f"🔎Finding the best runner for you!\nYou will be notified when a runner accepts your order\n\n"
                f"Order ID: #{order_id}\n"
                f"Delivery Type: {order_data['delivery_type'].capitalize()}\n"
                f"From: {order_data['from_location']}\n"
                f"To: {order_data['to_location']}\n\n"
                f"If you want to cancel the order, click the button below.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_{order_id}")]
                ])
            )

            # Update order with message IDs
            cursor.execute('''
                UPDATE Orders
                SET customer_message_id = ?, runner_message_id = ?
                WHERE id = ?
            ''', (message.message_id, runner_message_obj.message_id, order_id))
            conn.commit()
        except Exception as e:
            logger.error(f"Error sending order ID: {order_id} to runner group: {e}")
            await query.edit_message_text(
                "There was an error posting your order to runners. "
                "Please try again or contact support."
            )
        finally:
            conn.close()
        logger.info(f"User {query.from_user.id} confirmed order. Order ID: {order_id}")
    else:
        await query.edit_message_text("Order cancelled. Type /start to create a new order.")
        logger.info(f"User {query.from_user.id} cancelled order before confirmation.")
    return ConversationHandler.END

# Handle order cancellation by the user
async def handle_cancellation(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    order_id = query.data.replace('cancel_', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Orders.*, Customers.username
        FROM Orders
        JOIN Customers ON Orders.customer_id = Customers.user_id
        WHERE Orders.id=?
    ''', (order_id,))
    order = cursor.fetchone()

    if order and order['status'] == 'pending':
        cursor.execute('''
            UPDATE Orders
            SET status = 'cancelled', cancelled_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), order_id))
        conn.commit()
        logger.debug(f"Order ID: {order_id} status updated to cancelled.")

        await query.edit_message_text("Your order has been cancelled.")
        logger.info(f"User {query.from_user.id} cancelled order ID: {order_id}")

        # Edit the original runner group message to indicate cancellation and remove the accept button
        await context.bot.edit_message_text(
            chat_id=RUNNER_GROUP_ID,
            message_id=order['runner_message_id'],
            text=(
                f"Order #{order_id} has been cancelled by the user.\n\n"
                f"Type  : {order['delivery_type'].capitalize()}\n"
                f"From : {order['from_location']}\n"
                f"To      : {order['to_location']}\n"
                f"Time : {order['order_time']}\n"
            ),
            reply_markup=None
        )
    else:
        await query.edit_message_text("This order cannot be cancelled.")
        logger.warning(f"User {query.from_user.id} tried to cancel order ID: {order_id}, but it was not pending or not found.")
    conn.close()

# Handle when a runner accepts an order
async def handle_runner_acceptance(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    order_id = query.data.replace('accept_', '')
    runner = update.effective_user
    logger.info(f"Runner {runner.id} (@{runner.username}) attempting to accept order ID: {order_id}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Orders.*, Customers.username
        FROM Orders
        JOIN Customers ON Orders.customer_id = Customers.user_id
        WHERE Orders.id=?
    ''', (order_id,))
    order = cursor.fetchone()

    if order and order['status'] == 'pending':
        # Update order status and runner details
        cursor.execute('''
            UPDATE Orders
            SET status = 'accepted', runner_id = ?, accept_time = ?
            WHERE id = ?
        ''', (runner.id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), order_id))
        conn.commit()
        logger.debug(f"Order ID: {order_id} status updated to accepted, runner_id={runner.id}")

        # Check if runner is already in the database
        cursor.execute("SELECT * FROM Runners WHERE user_id=?", (runner.id,))
        runner_record = cursor.fetchone()
        if not runner_record:
            cursor.execute("INSERT INTO Runners (user_id, username) VALUES (?, ?)", (runner.id, runner.username))
            conn.commit()
        logger.debug(f"New runner inserted: user_id={runner.id}, username={runner.username}")

        # Update runner group message
        runner_message = (
            f"#{order_id}\n\n"
            f"Type  : {order['delivery_type'].capitalize()}\n"
            f"From : {order['from_location']}\n"
            f"To      : {order['to_location']}\n"
            f"Time : {order['order_time']}\n\n"
            f"✅ Accepted by @{runner.username}"
        )
        await query.edit_message_text(runner_message, reply_markup=None)

        # Notify customer with a new message
        await context.bot.send_message(
            chat_id=order['customer_id'],
            text=f"✅ Accepted by @{runner.username}\n\n"
                 f"📋 Order Summary:\n"
                 f"Order ID: #{order_id}\n"
                 f"Delivery Type: {order['delivery_type'].capitalize()}\n"
                 f"From: {order['from_location']}\n"
                 f"To: {order['to_location']}\n"
                 f"Time: {order['order_time']}\n\n"
                 "The order is now being processed."
        )

        # Delete the previous message from the customer's chat
        await context.bot.delete_message(
            chat_id=order['customer_id'],
            message_id=order['customer_message_id']
        )

        # Direct message the runner with customer's username or Telegram link
        customer_username = order['username']
        await context.bot.send_message(
            chat_id=runner.id,
            text=f"You have accepted the order #{order_id}.\n"
                 f"Customer's username: @{customer_username}\n"
                 f"Please contact the customer for further details."
        )
        logger.info(f"Runner {runner.id} (@{runner.username}) successfully accepted order ID: {order_id}")
    else:
        await query.edit_message_text(
            f"{query.message.text}\n\n"
            "❌ This order is no longer available.",
            reply_markup=None
        )
        logger.warning(f"Runner {runner.id} (@{runner.username}) tried to accept order ID: {order_id}, but it was not pending or not found.")
    conn.close()

# Cancel command handler
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Order cancelled. Type /start to create a new order.")
    logger.info(f"User {update.effective_user.id} cancelled order using /cancel command.")
    return ConversationHandler.END

# Main function to set up and run the bot
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Set up conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_SERVICE: [
                CallbackQueryHandler(choose_delivery, pattern='^(food|item)$')
            ],
            CHOOSING_FROM_CATEGORY: [
                CallbackQueryHandler(choose_from_category, pattern='^(sister|brother|in_uia|outside_uia)$')
            ],
            CHOOSING_FROM_MAHALLAH: [
                CallbackQueryHandler(handle_from_mahallah, pattern='^from_')
            ],
            TYPING_FROM_LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_from_location)
            ],
            CHOOSING_TO_CATEGORY: [
                CallbackQueryHandler(choose_to_category, pattern='^to_')
            ],
            CHOOSING_TO_MAHALLAH: [
                CallbackQueryHandler(handle_to_mahallah, pattern='^to_')
            ],
            TYPING_TO_LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_to_location)
            ],
            CONFIRMING_ORDER: [
                CallbackQueryHandler(handle_confirmation, pattern='^(confirm|cancel)$')
            ]
        },
        fallbacks=[CommandHandler('start', start), CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_runner_acceptance, pattern='^accept_'))
    application.add_handler(CallbackQueryHandler(handle_cancellation, pattern='^cancel_'))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
