import telebot
from telebot import types
import json, os, time, difflib
from datetime import datetime
from collections import Counter

# ================= CONFIG =================
API_TOKEN = "8561540975:AAEt3BAw87kFqIE8uLXRQpwTBRE9umdtTYs"
CHANNEL_USERNAME = "@CouresbyAnkit"
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

ADMIN_IDS = [6003630443, 7197718325]
COURSES_FILE = "courses.json"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ================= DATA LOADERS =================
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump(default, f, indent=2)
    with open(file, "r") as f: return json.load(f)

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=2)

# RE-ADDING ALL YOUR COURSES
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

def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except: return False

# ================= USER HANDLERS =================
@bot.message_handler(commands=["start"])
def start(message):
    if not is_member(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, "🔐 *Access Restricted*\nPlease join our channel to use the bot.", reply_markup=markup)
        return
    bot.send_message(message.chat.id, "📚 *Welcome to Ankit's Vault!*", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ['📚 All Courses', '🔎 Search Course', '⭐ VIP Access', '📞 Support'])
def handle_menu_buttons(m):
    if not is_member(m.from_user.id): return
    
    if m.text == '📚 All Courses':
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, c in enumerate(COURSES[:20]): # Show all 16+ courses
            markup.add(types.InlineKeyboardButton(text=f"🎓 {c['name']}", callback_data=f"get_c_{i}"))
        bot.send_message(m.chat.id, "📜 *Available Courses:*", reply_markup=markup)
        
    elif m.text == '🔎 Search Course':
        bot.send_message(m.chat.id, "🔍 **Ready!** Send the course name you're looking for.")
        
    elif m.text == '📞 Support':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 Message Ankit", url="https://t.me/CoursesByAnkit"))
        bot.send_message(m.chat.id, "📞 **Support Hub**\nClick below to chat with me!", reply_markup=markup)

@bot.message_handler(func=lambda m: not m.text.startswith("/"))
def handle_search(m):
    if not is_member(m.from_user.id): return
    query = m.text.strip()
    
    # Notify Admin of Search
    for admin_id in ADMIN_IDS:
        try: bot.send_message(admin_id, f"🔎 *Search:* `{query}` by {m.from_user.first_name}")
        except: pass

    bot.send_chat_action(m.chat.id, 'typing')
    status_msg = bot.send_message(m.chat.id, "🎬 *Searching...*")
    time.sleep(0.8)

    match = next((c for c in COURSES if query.lower() in c["name"].lower()), None)
    
    if match:
        bot.delete_message(m.chat.id, status_msg.message_id)
        bot.send_message(m.chat.id, f"✅ *Found!*\n\n🎉 *{match['name']}*\n🔗 {match['link']}")
    else:
        all_names = [c["name"] for c in COURSES]
        suggestions = difflib.get_close_matches(query, all_names, n=2, cutoff=0.3)
        markup = types.InlineKeyboardMarkup()
        if suggestions:
            for s in suggestions:
                idx = next((i for i, c in enumerate(COURSES) if c["name"] == s), None)
                markup.add(types.InlineKeyboardButton(text=f"🎓 {s}", callback_data=f"get_c_{idx}"))
        
        markup.add(types.InlineKeyboardButton("📩 Request Course", callback_data=f"req_{query[:20]}"))
        bot.edit_message_text(f"🚧 *Not Found!*\n\nI couldn't find `{query}`. Request it below?", m.chat.id, status_msg.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(c):
    if c.data.startswith("get_c_"):
        idx = int(c.data.replace("get_c_", ""))
        match = COURSES[idx]
        bot.send_message(c.message.chat.id, f"🎉 *{match['name']}*\n🔗 {match['link']}")
        bot.answer_callback_query(c.id)
    elif c.data.startswith("req_"):
        bot.answer_callback_query(c.id, "✅ Request sent!")
        for admin_id in ADMIN_IDS:
            bot.send_message(admin_id, f"🚨 *REQUEST:* `{c.data.replace('req_', '')}` from {c.from_user.first_name}")

if __name__ == "__main__":
    bot.infinity_polling()
