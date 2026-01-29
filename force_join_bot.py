import telebot
from telebot import types
import json, os, time, difflib

# ================= CONFIG =================
API_TOKEN = "8561540975:AAEt3BAw87kFqIE8uLXRQpwTBRE9umdtTYs"
CHANNEL_USERNAME = "@CouresbyAnkit"
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

ADMIN_IDS = [6003630443, 7197718325]
COURSES_FILE = "courses.json"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")
ADMIN_STATE = {} 

# ================= DATA LOADERS =================
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump(default, f, indent=2)
    with open(file, "r") as f: return json.load(f)

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=2)

INITIAL_COURSES = [
    {"name": "🎬 EDIT TO EARN – Video Editing", "link": "https://t.me/EditToEarnCoursesbyAnkit"},
    {"name": "🔥 Jeet Selal Training Course", "link": "https://arolinks.com/TrainingCoursebyJeetSelal"},
    {"name": "Stop Waiting Start Creating – Kavya Karnatac", "link": "https://t.me/+d4Tto-Nc2hw2ODFl"},
    {"name": "🌟 Saqlain Khan – Script & Storytelling", "link": "https://arolinks.com/SaqlainkhanCourse"},
    {"name": "🚀 Detyo Bon Instagram Course", "link": "https://arolinks.com/DetyoBonInstagramCourse"},
    {"name": "🤖 Master ChatGPT – Dhruv Rathee Academy", "link": "https://arolinks.com/Vus4S"},
    {"name": "⏰ Master Time Management – Dhruv Rathee", "link": "https://arolinks.com/Vus4S"},
    {"name": "🔥 Attraction Decoded – Indian Men", "link": "https://arolinks.com/Vus4S"},
    {"name": "🚀 YouTube Automation – Ammar Nisar", "link": "https://arolinks.com/BiM5K"},
    {"name": "🎥 CapCut Mastery: Beginner to Pro", "link": "https://t.me/CouresbyAnkit/447"},
    {"name": "💰 Take Charge of Your Money – Ankur Warikoo", "link": "https://t.me/SaqlainKhancoursebyAnkit"},
    {"name": "🎞️ Hayden Hillier Video Editing Course", "link": "https://t.me/AttractionDecodedManLifestyle/28"},
    {"name": "🎓 Time Management For Students - Warikoo", "link": "https://t.me/SaqlainKhancoursebyAnkit"},
    {"name": "📈 Beat Youtube In 18 Days - Algrow", "link": "https://t.me/CouresbyAnkit/188"},
    {"name": "🛡️ Iron Man Lifestyle - Attraction Decoded", "link": "https://t.me/AttractionDecodedManLifestyle"},
    {"name": "🧠 Research & Scripting Mastery", "link": "https://arolinks.com/SaqlainkhanCourse"}
]

COURSES = load_json(COURSES_FILE, INITIAL_COURSES)

# ================= KEYBOARDS =================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('📚 All Courses'), types.KeyboardButton('🔎 Search Course'))
    markup.add(types.KeyboardButton('⭐ VIP Access'), types.KeyboardButton('📞 Support'))
    return markup

def admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Course", "➖ Delete Course")
    markup.add("📢 Broadcast", "❌ Exit Admin")
    return markup

def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except: return False

# ================= HANDLERS =================
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS: return
    bot.send_message(message.chat.id, "👮 *Admin Panel Active*", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS and m.text in ["➕ Add Course", "➖ Delete Course", "📢 Broadcast", "❌ Exit Admin"])
def admin_button_handler(m):
    if m.text == "❌ Exit Admin":
        ADMIN_STATE.pop(m.from_user.id, None)
        bot.send_message(m.chat.id, "Admin Closed.", reply_markup=main_menu())
    elif m.text == "➕ Add Course":
        ADMIN_STATE[m.from_user.id] = "ADD_NAME"
        bot.send_message(m.chat.id, "Enter the Course Name:")
    elif m.text == "➖ Delete Course":
        ADMIN_STATE[m.from_user.id] = "DELETE"
        bot.send_message(m.chat.id, "Enter EXACT name to delete:")
    elif m.text == "📢 Broadcast":
        ADMIN_STATE[m.from_user.id] = "BC"
        bot.send_message(m.chat.id, "Enter broadcast message:")

@bot.message_handler(commands=["start"])
def start(message):
    if not is_member(message.from_user.id):
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, "🔐 *Access Restricted*", reply_markup=markup)
        return
    bot.send_message(message.chat.id, "📚 *Welcome!*", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ['📚 All Courses', '🔎 Search Course', '📞 Support'])
def menu_buttons(m):
    if not is_member(m.from_user.id): return
    if m.text == '📚 All Courses':
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, c in enumerate(COURSES):
            markup.add(types.InlineKeyboardButton(text=f"🎓 {c['name']}", callback_data=f"get_c_{i}"))
        bot.send_message(m.chat.id, "📜 *Courses:*", reply_markup=markup)
    elif m.text == '🔎 Search Course':
        bot.send_message(m.chat.id, "🔍 Send the name.")
    elif m.text == '📞 Support':
        bot.send_message(m.chat.id, "Contact @CoursesByAnkit")

@bot.message_handler(func=lambda m: not m.text.startswith("/"))
def main_handler(m):
    global COURSES # MOVED TO THE TOP TO FIX SYNTAX ERROR
    if not is_member(m.from_user.id): return
    
    state = ADMIN_STATE.get(m.from_user.id)
    
    if m.from_user.id in ADMIN_IDS and state:
        if state == "ADD_NAME":
            ADMIN_STATE[m.from_user.id] = {"name": m.text, "step": "ADD_LINK"}
            bot.send_message(m.chat.id, "Enter the link:")
        elif isinstance(state, dict) and state.get("step") == "ADD_LINK":
            COURSES.append({"name": state["name"], "link": m.text})
            save_json(COURSES_FILE, COURSES)
            bot.send_message(m.chat.id, "✅ Added!", reply_markup=admin_menu())
            ADMIN_STATE.pop(m.from_user.id)
        elif state == "DELETE":
            COURSES = [c for c in COURSES if c["name"].lower() != m.text.lower().strip()]
            save_json(COURSES_FILE, COURSES)
            bot.send_message(m.chat.id, "🗑️ Deleted.", reply_markup=admin_menu())
            ADMIN_STATE.pop(m.from_user.id)
        return

    # SEARCH LOGIC
    query = m.text.strip()
    match = next((c for c in COURSES if query.lower() in c["name"].lower()), None)
    if match:
        bot.send_message(m.chat.id, f"✅ *Found!*\n\n🎉 *{match['name']}*\n🔗 {match['link']}")
    else:
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📩 Request", callback_data=f"req_{query[:20]}"))
        bot.send_message(m.chat.id, f"❌ Not found: `{query}`", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    if c.data.startswith("get_c_"):
        idx = int(c.data.replace("get_c_", ""))
        bot.send_message(c.message.chat.id, f"🎉 *{COURSES[idx]['name']}*\n🔗 {COURSES[idx]['link']}")
    elif c.data.startswith("req_"):
        bot.answer_callback_query(c.id, "✅ Request sent!")

if __name__ == "__main__":
    bot.infinity_polling()
