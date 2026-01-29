import telebot
from telebot import types
import json, os, time, threading
import difflib
from datetime import datetime
from collections import Counter

# ================= CONFIG =================
API_TOKEN = "8561540975:AAEt3BAw87kFqIE8uLXRQpwTBRE9umdtTYs"
CHANNEL_USERNAME = "@CouresbyAnkit"
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

# Your Admin IDs
ADMIN_IDS = [6003630443, 7197718325]
COURSES_FILE = "courses.json"
USERS_FILE = "users.json"
WISHLIST_FILE = "wishlist.json"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ================= DATA LOADERS =================
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump(default, f, indent=2)
    with open(file, "r") as f: return json.load(f)

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=2)

# Your specific list provided 
INITIAL_COURSES = [
    {"name": "🎬 EDIT TO EARN – Video Editing", "link": "https://t.me/EditToEarnCoursesbyAnkit"},
    {"name": "🔥 Jeet Selal Training Course", "link": "https://arolinks.com/TrainingCoursebyJeetSelal"},
    {"name": "Stop Waiting Start Creating – Kavya Karnatac", "link": "https://t.me/+d4Tto-Nc2hw2ODFl"},
    {"name": "🌟 Saqlain Khan – Script & Storytelling", "link": "https://arolinks.com/SaqlainkhanCourse"},
    {"name": "🚀 Detyo Bon Instagram Course", "link": "https://arolinks.com/DetyoBonInstagramCourse"},
    {"name": "🤖 Master ChatGPT – Dhruv Rathee", "link": "https://arolinks.com/Vus4S"},
    {"name": "⏰ Master Time Management – Dhruv Rathee", "link": "https://arolinks.com/Vus4S"},
    {"name": "🔥 Attraction Decoded – Indian Men", "link": "https://arolinks.com/Vus4S"},
    {"name": "🚀 YouTube Automation – Ammar Nisar", "link": "https://arolinks.com/BiM5K"},
    {"name": "🎥 CapCut Mastery: Beginner to Pro", "link": "https://t.me/CouresbyAnkit/447"},
    {"name": "💰 Take Charge of Your Money – Ankur Warikoo", "link": "https://t.me/SaqlainKhancoursebyAnkit"},
    {"name": "🎞️ Hayden Hillier Video Editing Course", "link": "https://t.me/AttractionDecodedManLifestyle/28"},
    {"name": "🎓 Time Management For Students - Warikoo", "link": "https://t.me/SaqlainKhancoursebyAnkit"},
    {"name": "📈 Beat Youtube In 18 Days - Algrow", "link": "https://t.me/CouresbyAnkit/188"},
    {"name": "🛡️ Iron Man Lifestyle - Attraction Decoded", "link": "https://t.me/AttractionDecodedManLifestyle"}
]

COURSES = load_json(COURSES_FILE, INITIAL_COURSES)
ADMIN_STATE = {}

# ================= AUTO-DM STATS THREAD =================
def daily_report_task():
    last_sent_date = ""
    while True:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        if now.hour == 23 and now.minute == 59 and last_sent_date != current_date:
            today_file = f"stats_{current_date}.json"
            if os.path.exists(today_file):
                data = load_json(today_file, [])
                counter = Counter([d["query"] for d in data])
                report = f"📊 *Final Daily Report ({current_date})*\n\n"
                report += f"✅ Total Searches: {len(data)}\n\n"
                report += "*Top 5 Searches:* \n"
                for k, v in counter.most_common(5): report += f"• `{k}`: {v} times\n"
                
                for admin_id in ADMIN_IDS:
                    try: bot.send_message(admin_id, report)
                    except: pass
            last_sent_date = current_date
        time.sleep(30)

threading.Thread(target=daily_report_task, daemon=True).start()

# ================= SEARCH LOGIC =================
@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS and not m.text.startswith("/"))
def handle_search(m):
    query = m.text.strip()
    status_msg = bot.send_message(m.chat.id, "🎬 *Searching for your course...*")
    
    # Log Stats
    today = datetime.now().strftime("%Y-%m-%d")
    stats = load_json(f"stats_{today}.json", [])
    stats.append({"query": query})
    save_json(f"stats_{today}.json", stats)

    # 1. Check Course List
    match = next((c for c in COURSES if query.lower() in c["name"].lower()), None)
    if match:
        bot.edit_message_text(f"✅ *Found!*\n\n🎉 *{match['name']}*\n🔗 {match['link']}", m.chat.id, status_msg.message_id)
    else:
        # 2. Check Suggestions
        all_names = [c["name"] for c in COURSES]
        suggestions = difflib.get_close_matches(query, all_names, n=3, cutoff=0.3)
        if suggestions:
            markup = types.InlineKeyboardMarkup()
            for s in suggestions:
                markup.add(types.InlineKeyboardButton(text=f"🎓 {s}", callback_data=f"get_course_{s[:20]}"))
            bot.edit_message_text("🔍 *Not found.* Did you mean one of these? 👇", m.chat.id, status_msg.message_id, reply_markup=markup)
        else:
            # 3. Coming Soon & Admin DM 
            wishlist = load_json(WISHLIST_FILE, [])
            wishlist.append({"query": query, "date": today})
            save_json(WISHLIST_FILE, wishlist)
            bot.edit_message_text(f"🚧 *Coming Soon!*\n\n`{query}` isn't available yet. Added to queue! 📝\n\n🆘 *Urgent?* DM: @ytmn20", m.chat.id, status_msg.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("get_course_"))
def get_suggested(c):
    name_part = c.data.replace("get_course_", "").lower()
    match = next((course for course in COURSES if course["name"].lower().startswith(name_part)), None)
    if match:
        bot.edit_message_text(f"🎉 *{match['name']}*\n🔗 {match['link']}", c.message.chat.id, c.message.message_id)

# ================= ADMIN PANEL =================
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 View Stats", "📝 Wishlist")
    markup.add("📢 Broadcast", "❌ Exit Admin")
    bot.send_message(message.chat.id, "👮 *Admin Panel*", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_input(m):
    if m.text == "📝 Wishlist":
        wishlist = load_json(WISHLIST_FILE, [])
        counts = Counter([i["query"] for i in wishlist])
        text = "📝 *Most Requested:* \n\n" + "\n".join([f"• `{k}` ({v})" for k, v in counts.most_common(10)])
        bot.send_message(m.chat.id, text if wishlist else "Empty Wishlist.")
    # (Rest of admin ADD/REMOVE/BC logic goes here...)

if __name__ == "__main__":
    bot.infinity_polling()

