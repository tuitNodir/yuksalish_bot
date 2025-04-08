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

# Filiallar ro'yxati va adminlar
branches = [
    {"name": "Toshkent", "contact": "+998951010600", "admin": "@yuksalish_maktab_admin"},
    {"name": "Ohangaron", "contact": "+998952250600", "admin": "@Yuksalish_gymnasium"},
    {"name": "Chirchiq", "contact": "+998955070808", "admin": "@Chirchiq_Yuksalish_admin"},
    {"name": "Olmaliq", "contact": "+998881314114", "admin": "@Yuksalish_olmaliq"},
    {"name": "Andijon", "contact": "+998771030606", "admin": "@Andijon_Yuksalish_Maktabi"},
    {"name": "Namangan", "contact": "+998785551212", "admin": "@Nam_yuksalish_admin"},
    {"name": "Farg’ona", "contact": "+998889414141", "admin": "@fargona_yuksalish_maktabi"},
    {"name": "Jizzax", "contact": "+998953260600", "admin": "@yuksalish_maktabi_jizzax"},
    {"name": "Baxmal", "contact": "+998974365551", "admin": "@Yuksalish_maktablari_Baxmal"},
    {"name": "Samarqand", "contact": "+998915292225", "admin": "@Samarqand_Yuksalish_admin"},
    {"name": "Kattaqo’rg’on", "contact": "+998904623536", "admin": "@Kattaqorgon_yuksalish_admin1"},
    {"name": "Navoiy", "contact": "+998884714040", "admin": "@Navoiy_yuksalish_admin"},
    {"name": "G’ijduvon", "contact": "+998914145995", "admin": "@yuksalish_maktabi_gijduvon"}
]

# Har bir user uchun ma'lumotlar
user_data = {}

# /start komandasi
def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data[user.id] = {}

    # "Assalomu alaykum" xabarini yuborish
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ASSALOMU ALAYKUM, siz 'YUKSALISH maktablari'ning murojaatlar botiga yozmoqdasiz! "
             "Qanday savol, taklif yoki murojaatingiz bo'lsa iltimos yozib qoldiring!"
    )

    # Filiallarni tugmalar ko'rinishida yaratish
    keyboard = [
        [InlineKeyboardButton(f"{branch['name']}", callback_data=branch['name']) for branch in branches[i:i + 3]]
        for i in range(0, len(branches), 3)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Foydalanuvchiga filial tanlash uchun xabar yuborish
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Quyidagi filiallardan birini tanlang:",
        reply_markup=reply_markup
    )

# Filial tanlanganda
async def branch_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}

    branch_name = query.data
    branch = next(b for b in branches if b["name"] == branch_name)
    user_data[user_id]["branch"] = branch_name

    # Filial haqida ma'lumot yuborish
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=f"Tanlangan filial: {branch_name}\n"
             f"📞 Kontakt: {branch['contact']}\n"
             f"👤 Admin: {branch['admin']}\n"
             "Iltimos, murojaatingizni yozib yuboring."
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
    admin_group_id = -1001234567890  # Guruh ID sini o'zgartiring
    sent_message = await context.bot.send_message(
        chat_id=admin_group_id,
        text=f"📥 *Yangi murojaat!*\n\n👤 Foydalanuvchi: {update.effective_user.full_name}\n"
             f"🏢 Filial: {branch}\n💬 Xabar: {message}",
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

    # Handlerlarni qo'shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(branch_selected))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.REPLY, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()
