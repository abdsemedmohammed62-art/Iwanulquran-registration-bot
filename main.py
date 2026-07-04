import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# 🔗 ከBotFather እና ከግሩፑ የተገኙ ትክክለኛ መረጃዎች
BOT_TOKEN = "8345852664:AAEWFENKlPFXDDLHVjAqQCI4d2d3gjCOYbQ"
ADMIN_CHAT_ID = "-1002241951909"

bot = telebot.TeleBot(BOT_TOKEN)

# የተማሪዎችን ጊዜያዊ ምላሽ መያዣ
user_data = {}

# የትምህርት ክፍሎች ማውጫ
COURSES = ["ቃኢዳ (ኑራኒያ)", "ሐዲስ", "ፊቅህ", "ዓቂዳ"]

# ተማሪው /start ሲል ምዝገባ የሚጀምርበት ክፍል
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {} # ለዚህ ተማሪ አዲስ መዝገብ መክፈት
    
    welcome_text = (
        "እንኳን ወደ ኢዋኑል ቁርአን ኦንላይን መድረሳ የመመዝገቢያ ቦት በሰላም መጡ! ✨\n\n"
        "የምዝገባ ሂደቱን ለመጀመር እባክዎ **ሙሉ ስምዎን** በጽሁፍ ያስገቡ፦"
    )
    msg = bot.send_message(chat_id, welcome_text, parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_name)

# ስም ከተቀበለ በኋላ ስልክ ቁጥር የሚጠይቅበት ክፍል
def process_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    
    # ስልክ ቁጥር በቅጽበት ለመቀበል በተን ማዘጋጀት
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(KeyboardButton("📲 ስልክ ቁጥሬን በቅጽበት ላክ", request_contact=True))
    
    msg = bot.send_message(chat_id, "በጣም ጥሩ! አሁን ደግሞ ከታች ያለውን አረንጓዴ በተን በመጫን ስልክ ቁጥርዎን ያጋሩን (ወይም በጽሁፍ ያስገቡ)፦", reply_markup=markup)
    bot.register_next_step_handler(msg, process_phone)

# ስልክ ከተቀበለ በኋላ የትምህርት አይነት የሚጠይቅበት ክፍል
def process_phone(message):
    chat_id = message.chat.id
    if message.contact is not None:
        user_data[chat_id]['phone'] = message.contact.phone_number
    else:
        user_data[chat_id]['phone'] = message.text
        
    # የትምህርት አይነቶችን በተን አድርጎ ማቅረብ
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for course in COURSES:
        markup.add(KeyboardButton(course))
        
    msg = bot.send_message(chat_id, "ማሻአላህ! መማር የሚፈልጉትን የትምህርት አይነት ከታች ካሉት በተኖች ይምረጡ፦", reply_markup=markup)
    bot.register_next_step_handler(msg, process_course)

# የትምህርት አይነት ከተቀበለ በኋላ የሪፈራል ኮድ የሚጠይቅበት ክፍል
def process_course(message):
    chat_id = message.chat.id
    course_selection = message.text
    
    if course_selection not in COURSES:
        msg = bot.send_message(chat_id, "እባክዎ ከተሰጡት አማራጮች በተን ላይ ብቻ በመጫን ይምረጡ፦")
        bot.register_next_step_handler(msg, process_course)
        return
        
    user_data[chat_id]['course'] = course_selection
    
    msg = bot.send_message(chat_id, "በመጨረሻም፤ ወደ መድረሳችን የጋበዘዎት ሰው (አምባሳደር) ካለ የሰጠዎትን **ልዩ መለያ ኮድ (Promo Code)** ያስገቡ (የጋበዘዎት ሰው ከሌለ 'የለኝም' ብለው ይጻፉ)፦")
    bot.register_next_step_handler(msg, process_promo)

# ሁሉንም መረጃ አደራጅቶ ለተማሪው ማረጋገጫ፣ ለአስተዳዳሪው ደግሞ ኖቲፊኬሽን የሚልክበት ክፍል
def process_promo(message):
    chat_id = message.chat.id
    user_data[chat_id]['promo'] = message.text
    
    name = user_data[chat_id]['name']
    phone = user_data[chat_id]['phone']
    course = user_data[chat_id]['course']
    promo = user_data[chat_id]['promo']
    
    # ለተማሪው የሚላክ መልዕክት
    success_student = (
        "🎉 ማሻአላህ ምዝገባዎ በተሳካ ሁኔታ ተጠናቋል!\n\n"
        f"📝 **ስም፦** {name}\n"
        f"📞 **ስልክ፦** {phone}\n"
        f"📚 **ትምህርት፦** {course}\n"
        f"🎟 **የአምባሳደር ኮድ፦** {promo}\n\n"
        "የአንድ ሳምንት ነጻ የሙከራ ክፍላችን ከመጀመሩ በፊት በአስተዳዳሪዎቻችን በኩል በቅርቡ መረጃ ይደርስዎታል። ስላመለከቱ እናመሰግናለን!"
    )
    bot.send_message(chat_id, success_student)
    
    # ለናንተ ለሶስታችሁ ግሩፕ የሚመጣው ዝርዝር መረጃ
    admin_notification = (
        "🚨 **አዲስ የተማሪ ምዝገባ ደርሷል!** 🚨\n\n"
        f"👤 **የተማሪው ስም፦** {name}\n"
        f"📞 **የስልክ ቁጥር፦** {phone}\n"
        f"📖 **የመረጠው ክፍል፦** {course}\n"
        f"🏷 **የአምባሳደር ኮድ (Promo)፦** {promo}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💡 *ይህንን መረጃ ወደ ዋናው የክትትል ኤክሴል ፋይል መቅዳት እንዳይረሱ!*"
    )
    bot.send_message(ADMIN_CHAT_ID, admin_notification, parse_mode="Markdown")

# ቦቱ እንዳይቆም ማድረጊያ መስመር
print("የኢዋኑል ቁርአን ቦት በተሳካ ሁኔታ ስራ ጀምሯል...")
bot.infinity_polling()
