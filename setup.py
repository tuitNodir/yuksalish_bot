from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Filial ro'yxati
filial_list = [
    "Toshkent - +998951010600",
    "Ohangaron - +998952250600",
    "Chirchiq - +998955070808",
    "Olmaliq - +998881314114",
    "Andijon - +998771030606",
    "Namangan - +998785551212",
    "Farg’ona - +998889414141",
    "Jizzax - +998953260600",
    "Baxmal - +998974365551",
    "Samarqand - +998915292225",
    "Kattaqo’rg’on - +998904623536",
    "Navoiy - +998884714040",
    "G’ijduvon - +998914145995"
]

# Bot token
TOKEN = "7723999912:AAE7aGPF6yNKIKLjnupS3cjNEEM_4fITPUc"

# Assalomu alaykum xabari
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    welcome_message = (
        "ASSALOMU ALAYKUM, siz 'YUKSALISH maktablari'ning murojaatlar botiga yozmoqdasiz!\n\n"
        "Qanday savol, taklif yoki murojaatingiz bo'lsa iltimos yozib qoldiring!\n\n"
        "Iltimos, o'zingizning filialingizni tanlang:\n"
        "Filiallar ro'yxati:\n"
    )
    # Filial ro'yxatini 3 qator qilib ko'rsatish
    formatted_filials = "\n".join(f"{i+1}. {filial_list[i]}" for i in range(len(filial_list)))
    
    update.message.reply_text(welcome_message + formatted_filials)

# Murojaatni olish
def receive_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    user_name = update.message.from_user.full_name
    
    # Murojaatni qabul qilish va admin guruhga yuborish
    admin_group_id = -1002181308980  # Admin guruh ID
    message = f"Yangi murojaat:\n\n"
    message += f"Ism: {user_name}\n"
    message += f"Murojaat: {user_message}\n"

    context.bot.send_message(chat_id=admin_group_id, text=message)

    # Foydalanuvchiga murojaat yuborilganini bildirish
    update.message.reply_text("Sizning murojaatingiz qabul qilindi. Yaqin orada javob olasiz!")

def main() -> None:
    # Updater va Dispatcher o'rnatish
    updater = Updater(TOKEN)
    
    # Botni ishlashga tayyorlash
    dp = updater.dispatcher

    # /start komandasi uchun handler
    dp.add_handler(CommandHandler("start", start))

    # Foydalanuvchi yuborgan xabarni qabul qilish
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, receive_message))

    # Botni ishga tushirish
    updater.start_polling()

    # Botni ishlashda davom ettirish
    updater.idle()

if __name__ == '__main__':
    main()
