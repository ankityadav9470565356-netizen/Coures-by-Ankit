import telebot
from telebot import types
import json, os, time
from datetime import datetime
from collections import Counter



COMING_SOON_FILE = "coming_soon.json"

def load_coming():
    if not os.path.exists(COMING_SOON_FILE):
        with open(COMING_SOON_FILE, "w") as f:
            json.dump([], f)
    with open(COMING_SOON_FILE, "r") as f:
        return json.load(f)

def save_coming(data):
    with open(COMING_SOON_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ================= CONFIG =================
API_TOKEN = "8561540975:AAELrKmHB4vcMe8Txnbp4F47jxqJhxfq3u8"
CHANNEL_USERNAME = "@CouresbyAnkit"
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

ADMIN_IDS = [6003630443, 7197718325]
COURSES_FILE = "courses.json"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ================= DATA =================
ADMIN_STATE = {}

DEFAULT_COURSES = [
    {"name": "Edit To Earn – Video Editing", "link": "https://t.me/EditToEarnCoursesbyAnkit"},
    {"name": "CapCut Mastery Course", "link": "https://t.me/CouresbyAnkit/447"},
]

# ================= LOAD / SAVE =================
def load_courses():
    if not os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, "w") as f:
            json.dump(DEFAULT_COURSES, f, indent=2)
    with open(COURSES_FILE) as f:
        return json.load(f)

def save_courses(data):
    with open(COURSES_FILE, "w") as f:
        json.dump(data, f, indent=2)

COURSES = load_courses()

def get_today_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"

    if not os.path.exists(file):
        return 0, {}

    with open(file, "r") as f:
        data = json.load(f)

    queries = [item["query"] for item in data]
    counter = Counter(queries)

    return len(queries), counter

# ================= FORCE JOIN =================
def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

# ================= STATS =================
def log_search(user, query):
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    data = []
    if os.path.exists(file):
        data = json.load(open(file))
    data.append({"query": query})
    json.dump(data, open(file, "w"), indent=2)

def get_today_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    if not os.path.exists(file):
        return 0, {}
    data = json.load(open(file))
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
            "🔐 *Restricted Access*\n\nJoin our channel first 👇",
            reply_markup=markup
        )
        return

    bot.send_message(
        message.chat.id,
        "📚 *Welcome!*\n\nUse /courses or type course name 🔍"
    )

# ================= COURSES =================
@bot.message_handler(commands=["courses"])
def courses(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for c in COURSES:
        key = c["name"].lower().replace(" ", "_")
        markup.add(types.InlineKeyboardButton(f"🎓 {c['name']}", callback_data=f"course_{key}"))

    bot.send_message(
        message.chat.id,
        "📚 *Available Courses*\n\n👇 Select a course:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("course_"))
def course_open(c):
    key = c.data.replace("course_", "")
    for course in COURSES:
        if key == course["name"].lower().replace(" ", "_"):
            bot.send_message(
                c.message.chat.id,
                f"🎉 *{course['name']}*\n🔗 {course['link']}"
            )
            return
    bot.answer_callback_query(c.id, "❌ Course not found")

# ================= SEARCH (NON-ADMIN ONLY) =================
# ================= SEARCH (NON-ADMIN ONLY) =================
suggestions = get_suggestions(query)

if suggestions:
    # Create an interactive keyboard for suggestions
    markup = telebot.types.InlineKeyboardMarkup()
    
    for s in suggestions:
        # Each button sends the course name back to the bot as a callback
        markup.add(telebot.types.InlineKeyboardButton(text=f"🎓 {s}", callback_data=f"search_{s}"))

    text = (
        "🔍 *I couldn't find an exact match.*\n\n"
        "Did you mean one of these? 👇"
    )

    bot.edit_message_text(
        chat_id=m.chat.id,
        message_id=msg.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    return


# ================= ADMIN PANEL =================
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Course")
    markup.add("➖ Remove Course")
    markup.add("📊 View Stats")
    markup.add("❌ Exit Admin")

    bot.send_message(
        message.chat.id,
        "👮 *Admin Panel*",
        reply_markup=markup
    )

# ================= ADMIN BUTTONS =================
@bot.message_handler(func=lambda m: m.text == "➕ Add Course" and m.from_user.id in ADMIN_IDS)
def add_course(m):
    ADMIN_STATE[m.from_user.id] = "ADD"
    bot.send_message(m.chat.id, "Send:\n`Course Name | Link`")

@bot.message_handler(func=lambda m: m.text == "➖ Remove Course" and m.from_user.id in ADMIN_IDS)
def remove_course(m):
    ADMIN_STATE[m.from_user.id] = "REMOVE"
    text = "Send exact course name to remove:\n\n"
    for c in COURSES:
        text += f"• {c['name']}\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📊 View Stats" and m.from_user.id in ADMIN_IDS)
def stats(m):
    total, counter = get_today_stats()
    text = f"📊 *Today Stats*\n\n🔍 Searches: {total}\n\n"
    for k, v in counter.items():
        text += f"• `{k}` → {v}\n"
    bot.send_message(m.chat.id, text or "_No data_")

@bot.message_handler(func=lambda m: m.text == "❌ Exit Admin" and m.from_user.id in ADMIN_IDS)
def exit_admin(m):
    ADMIN_STATE.pop(m.from_user.id, None)
    bot.send_message(m.chat.id, "❌ Exited admin", reply_markup=types.ReplyKeyboardRemove())

# ================= ADMIN INPUT HANDLER =================
@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_input(m):
    state = ADMIN_STATE.get(m.from_user.id)

    if state == "ADD" and "|" in m.text:
        name, link = map(str.strip, m.text.split("|", 1))
        COURSES.append({"name": name, "link": link})
        save_courses(COURSES)
        ADMIN_STATE[m.from_user.id] = None
        bot.send_message(m.chat.id, "✅ Course added")

    elif state == "REMOVE":
        before = len(COURSES)
        COURSES[:] = [c for c in COURSES if c["name"].lower() != m.text.lower()]
        save_courses(COURSES)
        ADMIN_STATE[m.from_user.id] = None
        bot.send_message(
            m.chat.id,
            "🗑️ Removed" if len(COURSES) < before else "❌ Course not found"
        )

# ================= RUN =================
print("🤖 Bot running...")
bot.infinity_polling()

