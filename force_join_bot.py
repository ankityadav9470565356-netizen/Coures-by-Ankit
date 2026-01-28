import telebot
from telebot import types
import json, os, time
import difflib
from datetime import datetime
from collections import Counter

# ================= CONFIG =================
API_TOKEN = "8561540975:AAELrKmHB4vcMe8Txnbp4F47jxqJhxfq3u8"
CHANNEL_USERNAME = "@CouresbyAnkit"
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

ADMIN_IDS = [6003630443, 7197718325]
COURSES_FILE = "courses.json"
COMING_SOON_FILE = "coming_soon.json"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ================= DATA LOADERS =================
def load_courses():
    if not os.path.exists(COURSES_FILE):
        default = [
            {"name": "Edit To Earn – Video Editing", "link": "https://t.me/EditToEarnCoursesbyAnkit"},
            {"name": "CapCut Mastery Course", "link": "https://t.me/CouresbyAnkit/447"},
        ]
        with open(COURSES_FILE, "w") as f:
            json.dump(default, f, indent=2)
    with open(COURSES_FILE) as f:
        return json.load(f)

def save_courses(data):
    with open(COURSES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_coming():
    if not os.path.exists(COMING_SOON_FILE):
        with open(COMING_SOON_FILE, "w") as f:
            json.dump([], f)
    with open(COMING_SOON_FILE, "r") as f:
        return json.load(f)

COURSES = load_courses()
ADMIN_STATE = {}

# ================= HELPERS =================
def get_suggestions(query):
    # Dynamically get names from your current COURSES list + extra hardcoded ones
    all_names = [c["name"] for c in COURSES]
    extra_names = [
        "Dhruv Rathee — YouTube Blueprint",
        "Saqlain Khan — Documentary Script",
        "Tharun Speaks — Video Editing",
        "Algrow — YouTube Course",
        "BeerBiceps — Video Editing",
        "Master AI Prompting — Tech Burner",
        "Dark Psychology — Aditya Raj Kashyap",
        "Edit To Earn Cohort"
    ]
    full_list = list(set(all_names + extra_names))
    return difflib.get_close_matches(query, full_list, n=3, cutoff=0.4)

def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

def log_search(query):
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    data = []
    if os.path.exists(file):
        with open(file, "r") as f:
            data = json.load(f)
    data.append({"query": query})
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def get_today_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    if not os.path.exists(file):
        return 0, {}
    with open(file, "r") as f:
        data = json.load(f)
    counter = Counter([d["query"] for d in data])
    return len(data), counter

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    if not is_member(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK),
            types.InlineKeyboardButton("✅ I Joined", callback_data="check_join")
        )
        bot.send_message(
            message.chat.id,
            "🔐 *Restricted Access*\n\nJoin our channel first to use this bot! 👇",
            reply_markup=markup
        )
        return

    bot.send_message(
        message.chat.id,
        "📚 *Welcome to Ankit's Vault!*\n\nUse /courses to see everything or simply *type a course name* to search. 🔍"
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join_callback(c):
    if is_member(c.from_user.id):
        bot.answer_callback_query(c.id, "✅ Access Granted!")
        start(c.message)
    else:
        bot.answer_callback_query(c.id, "❌ You haven't joined yet!", show_alert=True)

# ================= COURSES COMMAND =================
@bot.message_handler(commands=["courses"])
def show_courses(message):
    if not is_member(message.from_user.id): return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for c in COURSES:
        key = c["name"].lower().replace(" ", "_")[:20] # Shorten key for callback limit
        markup.add(types.InlineKeyboardButton(f"🎓 {c['name']}", callback_data=f"course_{key}"))

    bot.send_message(message.chat.id, "📚 *Available Courses*:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("course_"))
def course_open(c):
    key = c.data.replace("course_", "")
    for course in COURSES:
        if key == course["name"].lower().replace(" ", "_")[:20]:
            bot.send_message(c.message.chat.id, f"🎉 *{course['name']}*\n🔗 {course['link']}")
            return
    bot.answer_callback_query(c.id, "❌ Course link not found")

# ================= SEARCH LOGIC =================
@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS and not m.text.startswith("/"))
def handle_search(m):
    if not is_member(m.from_user.id): return
    
    query = m.text.strip()
    log_search(query)
    
    # Check for exact match first
    match = next((c for c in COURSES if query.lower() in c["name"].lower()), None)
    
    if match:
        bot.send_message(m.chat.id, f"✅ *Match Found!*\n\n🎉 *{match['name']}*\n🔗 {match['link']}")
    else:
        # If no exact match, show suggestions
        suggestions = get_suggestions(query)
        if suggestions:
            markup = types.InlineKeyboardMarkup()
            for s in suggestions:
                markup.add(types.InlineKeyboardButton(text=f"🎓 {s}", callback_data=f"suggest_{s[:20]}"))
            
            bot.send_message(
                m.chat.id, 
                "🔍 *I couldn't find that exact course.*\n\nDid you mean one of these? 👇",
                reply_markup=markup
            )
        else:
            bot.send_message(m.chat.id, "❌ *No results found.*\nTry checking your spelling or use /courses.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("suggest_"))
def handle_suggestion(c):
    suggestion_short = c.data.replace("suggest_", "")
    # Search for the full name in our courses
    match = next((course for course in COURSES if course["name"].lower().startswith(suggestion_short.lower())), None)
    
    if match:
        bot.edit_message_text(f"🎉 *{match['name']}*\n🔗 {match['link']}", c.message.chat.id, c.message.message_id)
    else:
        bot.answer_callback_query(c.id, "Please type the name manually.")

# ================= ADMIN PANEL =================
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Course", "➖ Remove Course")
    markup.add("📊 View Stats", "❌ Exit Admin")
    bot.send_message(message.chat.id, "👮 *Admin Panel Active*", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_input(m):
    if m.text == "❌ Exit Admin":
        ADMIN_STATE.pop(m.from_user.id, None)
        bot.send_message(m.chat.id, "❌ Exited admin", reply_markup=types.ReplyKeyboardRemove())
        return

    if m.text == "➕ Add Course":
        ADMIN_STATE[m.from_user.id] = "ADD"
        bot.send_message(m.chat.id, "Send in this format:\n`Course Name | Link`")
        return

    if m.text == "➖ Remove Course":
        ADMIN_STATE[m.from_user.id] = "REMOVE"
        text = "Type the exact name to remove:\n\n"
        for c in COURSES: text += f"• `{c['name']}`\n"
        bot.send_message(m.chat.id, text)
        return

    if m.text == "📊 View Stats":
        total, counter = get_today_stats()
        text = f"📊 *Today's Stats*\n\n🔍 Total Searches: {total}\n\n"
        for k, v in counter.items(): text += f"• `{k}`: {v}\n"
        bot.send_message(m.chat.id, text if total > 0 else "No searches today.")
        return

    # Handle Input based on State
    state = ADMIN_STATE.get(m.from_user.id)
    if state == "ADD" and "|" in m.text:
        try:
            name, link = map(str.strip, m.text.split("|", 1))
            COURSES.append({"name": name, "link": link})
            save_courses(COURSES)
            ADMIN_STATE[m.from_user.id] = None
            bot.send_message(m.chat.id, f"✅ Added: {name}")
        except:
            bot.send_message(m.chat.id, "❌ Format error. Use `Name | Link`")
    
    elif state == "REMOVE":
        global COURSES
        original_count = len(COURSES)
        COURSES = [c for c in COURSES if c["name"].lower() != m.text.lower().strip()]
        if len(COURSES) < original_count:
            save_courses(COURSES)
            bot.send_message(m.chat.id, "🗑️ Course removed successfully.")
        else:
            bot.send_message(m.chat.id, "❌ Name not found exactly.")
        ADMIN_STATE[m.from_user.id] = None

# ================= RUN =================
if __name__ == "__main__":
    print("🤖 Bot is starting...")
    bot.infinity_polling()
