import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Bot tokeningizni shu yerga joylashtiring
token = "7723999912:AAE7aGPF6yNKIKLjnupS3cjNEEM_4fITPUc"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Filiallar ro'yxati
branches = [
    "Yuksalish 1 - Chilonzor",
    "Yuksalish 2 - Olmazor",
    "Yuksalish 3 - Sergeli",
    "Yuksalish 4 - Yunusobod",
    "Yuksalish 5 - Mirobod",
    "Yuksalish 6 - Yakkasaroy",
    "Yuksalish 7 - Uchtepa",
    "Yuksalish 8 - Shayxontohur",
    "Yuksalish 9 - Mirzo Ulug'bek",
    "Yuksalish 10 - Bektemir",
    "Yuksalish 11 - Yangihayot",
    "Yuksalish 12 - Yashnobod",
    "Yuksalish 13 - Toshkent viloyati"
]

# Har bir user uchun ma'lumotlar
user_data = {}

# /start komandasi
def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data[user.id] = {}

    keyboard = [[InlineKeyboardButton(branch, callback_data=branch)] for branch in branches]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Assalomu alaykum, {user.first_name}!\nQuyidagi filiallardan birini tanlang:",
        reply_markup=reply_markup
    )

# Filial tanlanganda
async def branch_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}

    branch = query.data
    user_data[user_id]["branch"] = branch

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=f"Tanlangan filial: {branch}\nIltimos, murojaatingizni yozib yuboring."
    )

# Foydalanuvchi xabar yuborganida
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text

    if user_id not in user_data or "branch" not in user_data[user_id]:
        await update.message.reply_text("Iltimos, avval filialni tanlang: /start")
        return

    branch = user_data[user_id]["branch"]

    # Adminlar guruhiga yuborish (admin group ID bilan almashtiring)
    admin_group_id = -1001234567890
    sent_message = await context.bot.send_message(
        chat_id=admin_group_id,
        text=f"📥 *Yangi murojaat!*\n\n👤 Foydalanuvchi: {update.effective_user.full_name}\n🏢 Filial: {branch}\n💬 Xabar: {message}",
        parse_mode="Markdown"
    )

    # Foydalanuvchiga javob yozilganida javob yuborish uchun context saqlanadi
    user_data[sent_message.message_id] = user_id

    await update.message.reply_text("Murojaatingiz qabul qilindi. Tez orada javob olasiz!")

# Admin javob berganida
async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    original_message = update.message.reply_to_message
    replied_message_id = original_message.message_id

    if replied_message_id in user_data:
        user_id = user_data[replied_message_id]
        reply_text = update.message.text

        await context.bot.send_message(
            chat_id=user_id,
            text=f"✉️ Sizga javob keldi:\n\n{reply_text}"
        )

# Botni ishga tushurish
if __name__ == '__main__':
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(branch_selected))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.REPLY, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()
