from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging

# === Sozlamalar ===
TOKEN = "7723999912:AAE7aGPF6yNKIKLjnupS3cjNEEM_4fITPUc"
ADMIN_GROUP_ID = -1002181308980

# Filiallar ro'yxati
filials = {
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
    "G’ijduvon": ("+998914145995", "@yuksalish_maktabi_gijduvon")
}

# User holatlari
user_data = {}

# Logger sozlamasi
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data[user.id] = {"step": "selecting_branch"}

    keyboard = []
    row = []
    for idx, branch in enumerate(filials.keys(), 1):
        row.append(InlineKeyboardButton(branch, callback_data=branch))
        if idx % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "ASSALOMU ALAYKUM, siz \"YUKSALISH maktablari\"ning murojaatlar botiga yozmoqdasiz!\n\n"
        "Qanday savol, taklif yoki murojaatingiz bo'lsa iltimos yozib qoldiring!",
        reply_markup=markup
    )

async def branch_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    branch = query.data
    user_data[user_id]["branch"] = branch
    user_data[user_id]["step"] = "waiting_message"

    phone, username = filials[branch]
    await query.message.reply_text(
        f"📍 *{branch}* filiali tanlandi\n"
        f"📞 Telefon: {phone}\n👤 Admin: {username}\n\n"
        "Endi murojaatingizni yuboring:",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    if user_id not in user_data or user_data[user_id].get("step") != "waiting_message":
        await update.message.reply_text("Iltimos, avval /start tugmasini bosing va filialni tanlang.")
        return

    branch = user_data[user_id]["branch"]
    message_text = update.message.text
    user_data[user_id]["step"] = "done"

    # Guruhga yuborish
    text = (
        f"📩 Yangi murojaat\n"
        f"👤 Ism: {user.first_name} (@{user.username or 'yoq'})\n"
        f"🏫 Filial: {branch}\n"
        f"📝 Murojaat:\n{message_text}"
    )

    sent = await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=text)

    # User IDni reply uchun saqlaymiz
    context.chat_data[sent.message_id] = user_id

    await update.message.reply_text("Murojaatingiz yuborildi! Tez orada siz bilan bog’lanishadi.")

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    replied_msg_id = update.message.reply_to_message.message_id
    user_id = context.chat_data.get(replied_msg_id)
    if not user_id:
        return

    await context.bot.send_message(chat_id=user_id, text=f"📬 Admin javobi:\n{update.message.text}")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(branch_selected))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    app.add_handler(MessageHandler(filters.REPLY & filters.ChatType.GROUPS, handle_reply))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
