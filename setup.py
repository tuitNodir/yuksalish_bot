from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_GROUP_ID = -1002181308980  # Guruh ID

# Filial ma'lumotlari
FILIALS = {
    "Toshkent": ["+998951010600", "@yuksalish_maktab_admin"],
    "Ohangaron": ["+998952250600", "@Yuksalish_gymnasium"],
    "Chirchiq": ["+998955070808", "@Chirchiq_Yuksalish_admin"],
    "Olmaliq": ["+998881314114", "@Yuksalish_olmaliq"],
    "Andijon": ["+998771030606", "@Andijon_Yuksalish_Maktabi"],
    "Namangan": ["+998785551212", "@Nam_yuksalish_admin"],
    "Farg’ona": ["+998889414141", "@fargona_yuksalish_maktabi"],
    "Jizzax": ["+998953260600", "@yuksalish_maktabi_jizzax"],
    "Baxmal": ["+998974365551", "@Yuksalish_maktablari_Baxmal"],
    "Samarqand": ["+998915292225", "@Samarqand_Yuksalish_admin"],
    "Kattaqo’rg’on": ["+998904623536", "@Kattaqorgon_yuksalish_admin1"],
    "Navoiy": ["+998884714040", "@Navoiy_yuksalish_admin"],
    "G’ijduvon": ["+998914145995", "@yuksalish_maktabi_gijduvon"]
}

# Foydalanuvchi holati: {user_id: {"filial": str, "msg_id": int}}
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ASSALOMU ALAYKUM, siz 'YUKSALISH maktablari'ning murojaatlar botiga yozmoqdasiz!\n\n"
        "Qanday savol, taklif yoki murojaatingiz bo'lsa iltimos yozib qoldiring!\n\n"
        "Filialingizni tanlang:"
    )
    keyboard = []
    row = []
    for i, filial in enumerate(FILIALS):
        row.append(InlineKeyboardButton(filial, callback_data=f"filial:{filial}"))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def filial_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    filial = query.data.split(":")[1]
    phone, username = FILIALS[filial]

    context.user_data['filial'] = filial

    text = (
        f"Siz tanlagan filial: *{filial}*\n"
        f"📞 Telefon: {phone}\n"
        f"👤 Admin: {username}\n\n"
        f"Iltimos murojaatingizni yuboring."
    )
    await query.message.reply_text(text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    filial = context.user_data.get('filial')
    if not filial:
        await update.message.reply_text("Iltimos, avval filialni tanlang /start orqali.")
        return

    text = update.message.text
    full_name = update.message.from_user.full_name
    user_states[user_id] = {
        'msg_id': update.message.message_id,
        'chat_id': update.message.chat_id
    }

    admin_text = (
        f"📬 *Yangi murojaat!*\n"
        f"👤 Foydalanuvchi: {full_name} (ID: {user_id})\n"
        f"🏫 Filial: {filial}\n"
        f"💬 Murojaat: {text}"
    )
    sent = await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=admin_text, parse_mode="Markdown")
    context.user_data.clear()
    await update.message.reply_text("Murojaatingiz qabul qilindi. Tez orada javob olasiz.")

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    text = update.message.text
    reply_text = update.message.reply_to_message.text
    lines = reply_text.split("\n")
    user_id_line = next((l for l in lines if "ID:" in l), None)

    if not user_id_line:
        return

    user_id = int(user_id_line.split("ID:")[1].strip())
    try:
        await context.bot.send_message(chat_id=user_id, text=f"📝 Admin javobi:\n{text}")
        await update.message.reply_text("✅ Javob yuborildi.")
    except Exception as e:
        logger.error(f"Javob yuborishda xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Foydalanuvchiga yuborib bo'lmadi.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(filial_callback, pattern="^filial:"))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_reply))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
