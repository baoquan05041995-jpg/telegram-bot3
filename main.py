from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

TOKEN = "8351598294:AAEsqz_Zvo2h8oW_PJE3Jk4PSkerdevMAzU"
ADMIN_ID = 1856285251  # Thay bằng user_id admin

user_map = {}

# ===== /start =====
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Tin nhắn chào
    update.message.reply_text(
        "Hello! You are connected to admin. Let me know what support you need.\n"
        "💎💎💎💎💎💎"
    )

    # Gửi thông tin user cho admin
    admin_msg = context.bot.send_message(
        ADMIN_ID,
        f"👤 User connected:\nName: {user.full_name}\nUsername: @{user.username}\nChat ID: {chat_id}"
    )
    user_map[admin_msg.message_id] = chat_id

    # Tạo menu Quick Reply **2 cột, 6 nút**
    keyboard = [
        [InlineKeyboardButton("📈 Signal", callback_data='Signal'),
         InlineKeyboardButton("💰 Copytrade", callback_data='Copytrade')],
        [InlineKeyboardButton("🛠 Support", callback_data='Support'),
         InlineKeyboardButton("🏦 Capital Fund", callback_data='Capital Fund')],
        [InlineKeyboardButton("🎁 Cashback", callback_data='Cashback'),
         InlineKeyboardButton("❓ Other", callback_data='Other')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose quickly:", reply_markup=reply_markup)

# ===== Xử lý nút Quick Reply =====
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    service = query.data
    chat_id = query.message.chat.id
    user = query.from_user

    # Gửi 1 tin nhắn duy nhất: chữ dịch vụ + Ok bro
    combined_text = f"{service}\nI noticed, what language do you use?"
    sent_msg = context.bot.send_message(chat_id, combined_text)

    # Forward tin nhắn cho admin
    fwd = context.bot.forward_message(ADMIN_ID, chat_id, sent_msg.message_id)

    # Lưu mapping để admin reply
    user_map[fwd.message_id] = chat_id

# ===== Admin reply =====
def admin_reply(update: Update, context: CallbackContext):
    if update.effective_chat.id == ADMIN_ID and update.message.reply_to_message:
        reply_msg_id = update.message.reply_to_message.message_id
        if reply_msg_id in user_map:
            target_id = user_map[reply_msg_id]
            context.bot.send_message(target_id, f"👨‍💻  {update.message.text}")
        else:
            update.message.reply_text("⚠️ Cannot identify the user to reply.")

# ===== User nhắn tin tự do =====
def user_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Forward tin nhắn user → admin
    fwd = context.bot.forward_message(ADMIN_ID, chat_id, update.message.message_id)

    # Lưu mapping để admin reply
    user_map[fwd.message_id] = chat_id

# ===== Main =====
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.user(ADMIN_ID), user_message))
    dp.add_handler(MessageHandler(Filters.text & Filters.user(ADMIN_ID), admin_reply))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
