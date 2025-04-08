import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)

BOT_TOKEN = '7723999912:AAE7aGPF6yNKIKLjnupS3cjNEEM_4fITPUc'
ADMIN_GROUP_ID = -1002181308980  # umumiy guruh ID (e'tibor bering: -100 prefix kerak)

logging.basicConfig(level=logging.INFO)

# States
ASK_NAME, ASK_PHONE, SELECT_BRANCH, GET_MESSAGE = range(4)

user_data_store = {}  # user_id -> dict

branches = {
    "Toshkent": ("+998951010600", "@yuksalish_maktab_admin"),
    "Ohangaron": ("+998952250600", "@Yuksalish_gymnasium"),
    "Chirchiq": ("+998955070808", "@Chirchiq_Yuksalish_admin"),
    "Olmaliq": ("+998881314114", "@Yuksalish_olmaliq"),
    "Andijon": ("+998771030606", "@Andijon_Yuksalish_Maktabi"),
    "Namangan": ("+998785551212", "@Nam_yuksalish_admin"),
    "Farg’ona": ("+998889414141", "@fargona_yuksalish_maktabi"),
    "Jizzax": ("+998953260600", "@yuksalish_maktabi_jizzax"),
    "Baxmal": ("+998974365551", "@Yuksalish_maktablari_Baxmal"),
    "Samarqand": ("+998915292225", "@Samarqand_Yuksalish_admin"),
    "Kattaqo’rg’on": ("+998904623536", "@Kattaqorgon_yuksalish_admin1"),
    "Navoiy": ("+998884714040", "@Navoiy_yuksalish_admin"),
    "G’ijduvon": ("+998914145995", "@yuksalish_maktabi_gijduvon"),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ism, familiyangizni kiriting:")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting (masalan: +998901234567):")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    # Branch selection
    keyboard = [
        [InlineKeyboardButton(name, callback_data=name)] for name in branches
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Filialni tanlang:", reply_markup=reply_markup)
    return SELECT_BRANCH

async def select_branch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    branch = query.data
    context.user_data["branch"] = branch

    await query.message.reply_text("Endi murojaatingizni yozing:")
    return GET_MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "yo‘q"
    name = context.user_data["name"]
    phone = context.user_data["phone"]
    branch = context.user_data["branch"]
    message = update.message.text

    branch_phone, branch_tag = branches[branch]

    # Store user data for reply tracking
    user_data_store[update.message.message_id] = user_id
    context.bot_data[user_id] = update.message.chat_id  # for reply back

    # Send to admin group
    text = (
        f"🏫 Filial: {branch}\n"
        f"📞 Tel: {phone}\n"
        f"👤 Ism: {name}\n"
        f"🆔 Telegram: @{username}\n"
        f"💬 Murojaat:\n{message}"
    )

    sent = await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=text)
    context.chat_data["last_message"] = (user_id, update.message.chat_id)
    context.bot_data[sent.message_id] = user_id  # reply uchun

    await update.message.reply_text("Murojaatingiz yuborildi. Tez orada javob olasiz.")
    return ConversationHandler.END

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        replied_message_id = update.message.reply_to_message.message_id
        user_id = context.bot_data.get(replied_message_id)
        if user_id:
            try:
                await context.bot.send_message(chat_id=user_id, text=f"✉️ Admin javobi:\n{update.message.text}")
            except Exception as e:
                await update.message.reply_text("Xabar yuborilmadi (foydalanuvchi botni to‘xtatgan bo‘lishi mumkin).")
        else:
            await update.message.reply_text("Foydalanuvchini aniqlab bo‘lmadi.")
    else:
        pass  # not a reply

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            SELECT_BRANCH: [CallbackQueryHandler(select_branch)],
            GET_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.REPLY & filters.ChatType.GROUPS, handle_reply))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
