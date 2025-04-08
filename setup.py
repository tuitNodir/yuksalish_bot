import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "7723999912:AAE7aGPF6yNKIKLjnupS3cjNEEM_4fITPUc"

# Adminlar guruhi chat ID'si
ADMIN_GROUP_ID = -1001234567890  # <-- bu yerga adminlar guruhi chat ID sini yozing

# Filiallar ro'yxati va adminlar
branches = {
    "Yuksalish Chilonzor": {"admin": "@chilonzor_admin", "phone": "+998901234001"},
    "Yuksalish Sergeli": {"admin": "@sergeli_admin", "phone": "+998901234002"},
    "Yuksalish Yunusobod": {"admin": "@yunusobod_admin", "phone": "+998901234003"},
    "Yuksalish Yakkasaroy": {"admin": "@yakkasaroy_admin", "phone": "+998901234004"},
    "Yuksalish Mirobod": {"admin": "@mirobod_admin", "phone": "+998901234005"},
    "Yuksalish Olmazor": {"admin": "@olmazor_admin", "phone": "+998901234006"},
    "Yuksalish Uchtepa": {"admin": "@uchtepa_admin", "phone": "+998901234007"},
    "Yuksalish Shayxontohur": {"admin": "@shayxontohur_admin", "phone": "+998901234008"},
    "Yuksalish Yashnobod": {"admin": "@yashnobod_admin", "phone": "+998901234009"},
    "Yuksalish Bektemir": {"admin": "@bektemir_admin", "phone": "+998901234010"},
    "Yuksalish Mirzo Ulugbek": {"admin": "@mirzo_ulugbek_admin", "phone": "+998901234011"},
    "Yuksalish Toshkent viloyati": {"admin": "@toshvil_admin", "phone": "+998901234012"},
    "Yuksalish Qibray": {"admin": "@qibray_admin", "phone": "+998901234013"}
}

user_data = {}

# Filial tugmalari

def get_branch_keyboard():
    keyboard = []
    row = []
    for i, name in enumerate(branches):
        row.append(InlineKeyboardButton(name, callback_data=name))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


# /start komandasi
def start_text():
    return ("ASSALOMU ALAYKUM, siz 'YUKSALISH maktablari'ning murojaatlar botiga yozmoqdasiz!\n"
            "Qanday savol, taklif yoki murojaatingiz bo'lsa iltimos yozib qoldiring!\nFiliallardan birini tanlang:")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_text(), reply_markup=get_branch_keyboard())


# Filial tanlanganda
async def branch_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    branch = query.data
    user_id = query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]["branch"] = branch

    info = branches[branch]
    text = f"Filial: {branch}\nAdmin: {info['admin']}\nTelefon: {info['phone']}\n\nEndi murojaatingizni yozib yuboring."
    await query.edit_message_text(text)


# Foydalanuvchi murojaati
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data or "branch" not in user_data[user_id]:
        await update.message.reply_text("Iltimos, avval filialni tanlang.", reply_markup=get_branch_keyboard())
        return

    branch = user_data[user_id]["branch"]
    username = update.message.from_user.username or "Noma'lum"
    text = update.message.text

    message_to_admin = f"📩 <b>Yangi murojaat!</b>\n\n👤 <b>Foydalanuvchi:</b> @{username}\n🏫 <b>Filial:</b> {branch}\n📝 <b>Murojaat:</b> {text}"

    sent_msg = await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=message_to_admin,
        parse_mode="HTML",
        reply_to_message_id=None  # reply uchun bazaga saqlash mumkin
    )

    await update.message.reply_text("Murojaatingiz yuborildi. Tez orada siz bilan bog‘lanamiz.")


# Botni ishga tushirish
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(branch_selected))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
