import telebot
from telebot import types
import json, os, time
from datetime import datetime

# ================= CONFIG =================
API_TOKEN = "8561540975:AAELrKmHB4vcMe8Txnbp4F47jxqJhxfq3u8"
CHANNEL_USERNAME = "@CouresbyAnkit"
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

ADMIN_IDS = [6003630443, 7197718325]   # 👈 YOUR TELEGRAM USER ID (NUMBER)
COURSES_FILE = "courses.json"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ================= DEFAULT COURSES =================
DEFAULT_COURSES = [
    {"name": "Edit To Earn – Video Editing", "link": "https://t.me/EditToEarnCoursesbyAnkit"},
    {"name": "Jeet Selal Fitness Course", "link": "https://arolinks.com/TrainingCoursebyJeetSelal"},
    {"name": "Go Viral – Kavya Karnatac", "link": "https://t.me/+d4Tto-Nc2hw2ODFl"},
    {"name": "Script & Storytelling – Saqlain Khan", "link": "https://arolinks.com/SaqlainkhanCourse"},
    {"name": "Instagram Growth – Detyo Bon", "link": "https://arolinks.com/DetyoBonInstagramCourse"},
    {"name": "ChatGPT Mastery – Dhruv Rathee", "link": "https://arolinks.com/Vus4S"},
    {"name": "Time Management – Dhruv Rathee", "link": "https://arolinks.com/Vus4S"},
    {"name": "YouTube Automation – Ammar Nisar", "link": "https://arolinks.com/BiM5K"},
    {"name": "CapCut Mastery Course", "link": "https://t.me/CouresbyAnkit/447"},
    {"name": "Mr Beast Editor Course", "link": "https://t.me/AttractionDecodedManLifestyle/28"},
]
ADMIN_STATE = {}


# ================= LOAD / SAVE =================
def load_courses():
    if not os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, "w") as f:
            json.dump(DEFAULT_COURSES, f, indent=2)
    with open(COURSES_FILE, "r") as f:
        return json.load(f)

def save_courses(data):
    with open(COURSES_FILE, "w") as f:
        json.dump(data, f, indent=2)

COURSES = load_courses()

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
    data.append({
        "user": user.first_name,
        "username": user.username,
        "query": query,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    json.dump(data, open(file, "w"), indent=2)

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
        f"🎉 *Welcome {message.from_user.first_name}!* \n\n📚 Use /courses or search by typing 🔍"
    )

# ================= JOIN CHECK =================
@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join(c):
    if is_member(c.from_user.id):
        bot.edit_message_text(
            "✅ *Access Granted!*\n\n📚 Use /courses",
            c.message.chat.id,
            c.message.message_id
        )
    else:
        bot.answer_callback_query(c.id, "❌ Join channel first!", show_alert=True)

# ================= COURSES INLINE =================
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

# ================= COURSE CLICK =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("course_"))
def course_open(c):
    key = c.data.replace("course_", "")
    for course in COURSES:
        if key == course["name"].lower().replace(" ", "_"):
            bot.send_message(
                c.message.chat.id,
                f"🎉 *{course['name']}*\n\n🔗 {course['link']}"
            )
            bot.answer_callback_query(c.id)
            return
    bot.answer_callback_query(c.id, "❌ Course not found")

# ================= SEARCH =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def search(m):
    query = m.text.lower()
    log_search(m.from_user, query)

    msg = bot.send_message(m.chat.id, "🔍 Searching 🎬")
    for i in range(3):
        time.sleep(0.4)
        bot.edit_message_text(f"🔍 Searching 🎬{'.'*(i+1)}", m.chat.id, msg.message_id)

    for c in COURSES:
        if query in c["name"].lower():
            bot.edit_message_text(
                f"🎉 *Found!*\n\n🎓 {c['name']}\n🔗 {c['link']}",
                m.chat.id,
                msg.message_id
            )
            return

    bot.edit_message_text(
        "😔 *Course Not Available*\n\n🚧 Coming Soon!\n📩 DM 👉 @coursesbyankit",
        m.chat.id,
        msg.message_id
    )

# ================= ADMIN =================
@bot.message_handler(commands=["admin"])
def admin(m):
    if m.from_user.id not in ADMIN_IDS:
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Add Course", "➖ Remove Course", "❌ Exit")
    bot.send_message(m.chat.id, "👮 *Admin Panel*", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "➕ Add Course" and m.from_user.id in ADMIN_IDS)
def add_course(m):
    bot.send_message(m.chat.id, "Send:\n`Course Name | Link`")

@bot.message_handler(func=lambda m: "|" in m.text and m.from_user.id in ADMIN_IDS)
def save_course(m):
    name, link = map(str.strip, m.text.split("|", 1))
    COURSES.append({"name": name, "link": link})
    save_courses(COURSES)
    bot.send_message(m.chat.id, "✅ Course added!")

@bot.message_handler(func=lambda m: m.text == "➖ Remove Course" and m.from_user.id in ADMIN_IDS)
def remove_course(m):
    text = "Send course name to remove:\n"
    for c in COURSES:
        text += f"• {c['name']}\n"
    bot.send_message(m.chat.id, text)


#Admin Command 
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS:
        return

    ADMIN_STATE[message.from_user.id] = None

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Course")
    markup.add("➖ Remove Course")
    markup.add("📊 View Stats")
    markup.add("❌ Exit Admin")

    bot.send_message(
        message.chat.id,
        "👮 *Admin Panel*\n\nSelect an option:",
        reply_markup=markup
    )


#Add course 
@bot.message_handler(func=lambda m: m.text == "➕ Add Course" and m.from_user.id in ADMIN_IDS)
def admin_add_course(message):
    bot.send_message(
        message.chat.id,
        "➕ *Add Course*\n\nSend like:\n`Course Name | https://link`"
    )
@bot.message_handler(func=lambda m: "|" in m.text and m.from_user.id in ADMIN_IDS)
def save_course(message):
    try:
        name, link = map(str.strip, message.text.split("|", 1))
        COURSES.append({"name": name, "link": link})
        save_courses(COURSES)
        bot.send_message(message.chat.id, f"✅ *Added:* {name}")
    except:
        bot.send_message(message.chat.id, "❌ Format wrong")


#Remove Course 
@bot.message_handler(func=lambda m: m.text == "➖ Remove Course" and m.from_user.id in ADMIN_IDS)
def admin_remove_course(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in COURSES:
        markup.add(f"🗑 {c['name']}")
    markup.add("⬅️ Back")

    bot.send_message(
        message.chat.id,
        "🗑 *Select course to delete*",
        reply_markup=markup
    ) 
@bot.message_handler(func=lambda m: m.text.startswith("🗑 ") and m.from_user.id in ADMIN_IDS)
def delete_course(message):
    name = message.text.replace("🗑 ", "")
    global COURSES
    COURSES = [c for c in COURSES if c["name"] != name]
    save_courses(COURSES)

    bot.send_message(message.chat.id, f"🗑️ *Removed:* {name}")


#Status button 

@bot.message_handler(func=lambda m: m.text == "📊 View Stats" and m.from_user.id in ADMIN_IDS)
def admin_stats_button(message):
    total, counter = get_today_stats()

    text = "📊 *Today Stats*\n\n"
    text += f"🔍 Total Searches: *{total}*\n\n"

    if counter:
        text += "🔥 *Top Searches:*\n"
        for k, v in sorted(counter.items(), key=lambda x: x[1], reverse=True)[:5]:
            text += f"• `{k}` → {v}\n"
    else:
        text += "_No searches today_"

    bot.send_message(message.chat.id, text)
@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_text_handler(message):
    state = ADMIN_STATE.get(message.from_user.id)

    # ADD COURSE MODE
    if state == "ADD" and "|" in message.text:
        name, link = map(str.strip, message.text.split("|", 1))
        COURSES.append({"name": name, "link": link})
        save_courses(COURSES)
        ADMIN_STATE[message.from_user.id] = None
        bot.send_message(message.chat.id, "✅ Course added successfully!")
        return

    # REMOVE COURSE MODE
    if state == "REMOVE":
        global COURSES
        COURSES = [c for c in COURSES if c["name"].lower() != message.text.lower()]
        save_courses(COURSES)
        ADMIN_STATE[message.from_user.id] = None
        bot.send_message(message.chat.id, "🗑️ Course removed (if existed).")
        return



# ================= RUN =================
print("🤖 Bot is running...")
bot.infinity_polling()


