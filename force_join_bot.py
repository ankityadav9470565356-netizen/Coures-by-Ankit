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

def save_user(user_id):
    users = load_json(USERS_FILE, [])
    if user_id not in users:
        users.append(user_id)
        save_json(USERS_FILE, users)

# Initial list based on your file
INITIAL_COURSES = [
    {"name": "🎬 EDIT TO EARN – Video Editing", "link": "https://t.me/EditToEarnCoursesbyAnkit"},
    {"name": "🔥 Jeet Selal Training Course", "link": "https://arolinks.com/TrainingCoursebyJeetSelal"},
    {"name": "Stop Waiting Start Creating – Kavya Karnatac", "link": "https://t.me/+d4Tto-Nc2hw2ODFl"},
    {"name": "🌟 Saqlain Khan – Script & Storytelling Mastery", "link": "https://arolinks.com/SaqlainkhanCourse"},
    {"name": "🚀 Detyo Bon Instagram Course", "link": "https://arolinks.com/DetyoBonInstagramCourse"},
    {"name": "🤖 Master ChatGPT – Dhruv Rathee Academy", "link": "https://arolinks.com/Vus4S"},
    {"name": "⏰ Master Time Management – Dhruv Rathee", "link": "https://arolinks.com/Vus4S"},
    {"name": "🎥 CapCut Mastery: Beginner to Pro", "link": "https://t.me/CouresbyAnkit/447"}
]

COURSES = load_json(COURSES_FILE, INITIAL_COURSES)
ADMIN_STATE = {} # To track if admin is adding or deleting

# ================= HELPERS =================
def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except: return False

def get_today_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    if not os.path.exists(file): return 0, {}
    data = load_json(file, [])
    return len(data), Counter([d["query"] for d in data])

# ================= AUTO-DM STATS THREAD =================
def daily_report_task():
    last_sent_date = ""
    while True:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        if now.hour == 23 and now.minute == 59 and last_sent_date != current_date:
            total, counter = get_today_stats()
            if total > 0:
                report = f"📊 *Final Daily Report ({current_date})*\n\nTotal Searches: {total}\n"
                for k, v in counter.most_common(5): report += f"• `{k}`: {v}\n"
                for admin_id in ADMIN_IDS:
                    try: bot.send_message(admin_id, report)
                    except: pass
            last_sent_date = current_date
        time.sleep(30)

threading.Thread(target=daily_report_task, daemon=True).start()

# ================= USER COMMANDS =================
@bot.message_handler(commands=["start"])
def start(message):
    save_user(message.from_user.id)
    if not is_member(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ I Joined", callback_data="check_join"))
        bot.send_message(message.chat.id, "🔐 *Access Restricted*\nPlease join our channel to use the bot.", reply_markup=markup)
        return
    bot.send_message(message.chat.id, "📚 *Welcome!*\nType a course name to search or use /courses.")

@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join(c):
    if is_member(c.from_user.id):
        bot.answer_callback_query(c.id, "✅ Access Granted!")
        start(c.message)
    else:
        bot.answer_callback_query(c.id, "❌ Join first!", show_alert=True)

@bot.message_handler(commands=["courses"])
def show_all(message):
    if not is_member(message.from_user.id): return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for c in COURSES:
        markup.add(types.InlineKeyboardButton(text=f"🎓 {c['name']}", callback_data=f"get_c_{c['name'][:20]}"))
    bot.send_message(message.chat.id, "📜 *Full Course List:*", reply_markup=markup)

# ================= SEARCH FLOW =================
@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS and not m.text.startswith("/"))
def handle_search(m):
    if not is_member(m.from_user.id): return
    query = m.text.strip()
    
    # Log Stats
    today = datetime.now().strftime("%Y-%m-%d")
    stats = load_json(f"stats_{today}.json", [])
    stats.append({"query": query})
    save_json(f"stats_{today}.json", stats)

    status_msg = bot.send_message(m.chat.id, "🎬 *Searching for your course...*")
    time.sleep(1)

    match = next((c for c in COURSES if query.lower() in c["name"].lower()), None)
    
    if match:
        bot.edit_message_text(f"✅ *Found!*\n\n🎉 *{match['name']}*\n🔗 {match['link']}", m.chat.id, status_msg.message_id)
    else:
        all_names = [c["name"] for c in COURSES]
        suggestions = difflib.get_close_matches(query, all_names, n=3, cutoff=0.3)
        if suggestions:
            markup = types.InlineKeyboardMarkup()
            for s in suggestions:
                markup.add(types.InlineKeyboardButton(text=f"🎓 {s}", callback_data=f"get_c_{s[:20]}"))
            bot.edit_message_text("🔍 *Not found.* Did you mean? 👇", m.chat.id, status_msg.message_id, reply_markup=markup)
        else:
            wishlist = load_json(WISHLIST_FILE, [])
            wishlist.append({"query": query, "date": today})
            save_json(WISHLIST_FILE, wishlist)
            bot.edit_message_text(f"🚧 *Coming Soon!*\nAdded `{query}` to queue. 📝\n🆘 *Urgent?* DM: @ytmn20", m.chat.id, status_msg.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("get_c_"))
def handle_callback(c):
    name_part = c.data.replace("get_c_", "").lower()
    match = next((course for course in COURSES if course["name"].lower().startswith(name_part)), None)
    if match:
        bot.edit_message_text(f"🎉 *{match['name']}*\n🔗 {match['link']}", c.message.chat.id, c.message.message_id)

# ================= ADMIN PANEL =================
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Course", "➖ Delete Course")
    markup.add("📊 View Stats", "📝 Wishlist")
    markup.add("📢 Broadcast", "❌ Exit Admin")
    bot.send_message(message.chat.id, "👮 *Admin Panel Active*", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_handler(m):
    global COURSES
    if m.text == "❌ Exit Admin":
        ADMIN_STATE.pop(m.from_user.id, None)
        bot.send_message(m.chat.id, "Admin Closed.", reply_markup=types.ReplyKeyboardRemove())
    
    elif m.text == "➕ Add Course":
        ADMIN_STATE[m.from_user.id] = "ADD_NAME"
        bot.send_message(m.chat.id, "Enter Course Name:")

    elif m.text == "➖ Delete Course":
        ADMIN_STATE[m.from_user.id] = "DELETE"
        bot.send_message(m.chat.id, "Enter EXACT Course Name to delete:")

    elif m.text == "📊 View Stats":
        total, counter = get_today_stats()
        text = f"📊 Today: {total} searches.\n" + "\n".join([f"• {k}: {v}" for k, v in counter.items()])
        bot.send_message(m.chat.id, text if total > 0 else "No data.")

    elif m.text == "📝 Wishlist":
        wishlist = load_json(WISHLIST_FILE, [])
        counts = Counter([i["query"] for i in wishlist])
        text = "📝 *Wishlist:*\n" + "\n".join([f"• {k} ({v})" for k, v in counts.most_common(10)])
        bot.send_message(m.chat.id, text if wishlist else "Empty.")

    elif m.text == "📢 Broadcast":
        ADMIN_STATE[m.from_user.id] = "BC"
        bot.send_message(m.chat.id, "Enter broadcast message:")

    else:
        state = ADMIN_STATE.get(m.from_user.id)
        if state == "ADD_NAME":
            ADMIN_STATE[m.from_user.id] = {"name": m.text, "state": "ADD_LINK"}
            bot.send_message(m.chat.id, f"Now enter link for: {m.text}")
        elif isinstance(state, dict) and state.get("state") == "ADD_LINK":
            COURSES.append({"name": state["name"], "link": m.text})
            save_json(COURSES_FILE, COURSES)
            bot.send_message(m.chat.id, "✅ Added successfully!")
            ADMIN_STATE[m.from_user.id] = None
        elif state == "DELETE":
            COURSES = [c for c in COURSES if c["name"].lower() != m.text.lower().strip()]
            save_json(COURSES_FILE, COURSES)
            bot.send_message(m.chat.id, "🗑️ Deleted (if it existed).")
            ADMIN_STATE[m.from_user.id] = None
        elif state == "BC":
            users = load_json(USERS_FILE, [])
            for u in users:
                try: bot.send_message(u, f"📢 *Update*\n\n{m.text}")
                except: pass
            bot.send_message(m.chat.id, "✅ Sent.")
            ADMIN_STATE[m.from_user.id] = None

if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling()
