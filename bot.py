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
BOT_TOKEN: Final = '8030428695:AAFdN__4SqJFJMLfXYktL19CD41MsYfIcXQ'
RUNNER_GROUP_ID: Final = '-1002344594546'
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
    try:
        with open(ORDERS_FILE, 'r') as f:
            counter = json.load(f)
    except FileNotFoundError:
        counter = {"count": 0}
    counter["count"] += 1
    with open(ORDERS_FILE, 'w') as f:
        json.dump(counter, f)
    return counter["count"]

# Start command handler
async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers WHERE user_id=?", (user_id,))
    customer = cursor.fetchone()
    conn.close()

    if customer and customer['is_blocked']:
        await update.message.reply_text("You have been blocked from using the service.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Food Delivery", callback_data='food')],
        [InlineKeyboardButton("Item Delivery", callback_data='item')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to makanApa the IIUM e-Hailing Bot! Please choose your delivery type:",
        reply_markup=reply_markup
    )
    return CHOOSING_SERVICE

# Choose delivery type handler
async def choose_delivery(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['delivery_type'] = query.data

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
    context.user_data['from_location'] = update.message.text

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
    await display_order_summary(query, context)
    return CONFIRMING_ORDER

# Handle custom typed delivery location
async def handle_custom_to_location(update: Update, context: CallbackContext) -> int:
    context.user_data['to_location'] = update.message.text
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
        conn.commit()

        order_data = {
            "customer_id": user_id,
            "delivery_type": context.user_data['delivery_type'],
            "from_location": context.user_data['from_location'],
            "to_location": context.user_data['to_location']
        }

        # Generate order ID with timestamp and counter
        counter = get_next_counter()
        order_id = f"ORDER_{datetime.now().strftime('%y%m%d_%H%M%S')}_{counter}"

        # Insert order into database
        cursor.execute('''
            INSERT INTO Orders (id, customer_id, delivery_type, from_location, to_location)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_id, order_data['customer_id'], order_data['delivery_type'], order_data['from_location'], order_data['to_location']))
        conn.commit()

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

            # Notify customer and keep order details visible
            message = await query.edit_message_text(
                f"✅ Your order has been posted to runners! "
                "You will be notified when a runner accepts your order.\n\n"
                f"📋 Order Summary:\n"
                f"Order ID: #{order_id}\n"
                f"Delivery Type: {order_data['delivery_type'].capitalize()}\n"
                f"From: {order_data['from_location']}\n"
                f"To: {order_data['to_location']}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "If you want to cancel the order, click the button below.",
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
            print(f"Error sending to runner group: {e}")
            await query.edit_message_text(
                "There was an error posting your order to runners. "
                "Please try again or contact support."
            )
        finally:
            conn.close()
    else:
        await query.edit_message_text("Order cancelled. Type /start to create a new order.")
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

        await query.edit_message_text("Your order has been cancelled.")

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
    conn.close()

# Handle when a runner accepts an order
async def handle_runner_acceptance(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    order_id = query.data.replace('accept_', '')
    runner = update.effective_user

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

        # Check if runner is already in the database
        cursor.execute("SELECT * FROM Runners WHERE user_id=?", (runner.id,))
        runner_record = cursor.fetchone()
        if not runner_record:
            cursor.execute("INSERT INTO Runners (user_id, username) VALUES (?, ?)", (runner.id, runner.username))
        conn.commit()

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
    else:
        await query.edit_message_text(
            f"{query.message.text}\n\n"
            "❌ This order is no longer available.",
            reply_markup=None
        )
    conn.close()

# Cancel command handler
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Order cancelled. Type /start to create a new order.")
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