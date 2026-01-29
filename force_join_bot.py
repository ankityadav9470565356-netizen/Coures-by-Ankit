import telebot
from telebot import types
import json, os, time, threading
import difflib
from datetime import datetime
from collections import Counter

# ================= CONFIG =================
API_TOKEN = "8561540975:AAELrKmHB4vcMe8Txnbp4F47jxqJhxfq3u8"
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

COURSES = load_json(COURSES_FILE, [
    {"name": "Edit To Earn – Video Editing", "link": "https://t.me/EditToEarnCoursesbyAnkit"},
    {"name": "CapCut Mastery Course", "link": "https://t.me/CouresbyAnkit/447"}
])
ADMIN_STATE = {}

# ================= HELPERS =================
def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except: return False

def log_search(query):
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    data = load_json(file, [])
    data.append({"query": query, "time": datetime.now().strftime("%H:%M:%S")})
    save_json(file, data)

def log_wishlist(query):
    wishlist = load_json(WISHLIST_FILE, [])
    wishlist.append({"query": query, "date": datetime.now().strftime("%Y-%m-%d")})
    save_json(WISHLIST_FILE, wishlist)

def get_today_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    if not os.path.exists(file): return 0, {}
    data = load_json(file, [])
    return len(data), Counter([d["query"] for d in data])

# ================= AUTO-DM THREAD =================
def daily_report_task():
    last_sent_date = ""
    while True:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        if now.hour == 23 and now.minute == 59 and last_sent_date != current_date:
            total, counter = get_today_stats()
            report = f"📊 *Final Daily Report ({current_date})*\n\n"
            report += f"✅ Total Searches: {total}\n\n"
            if total > 0:
                report += "*Top Searches:* \n"
                for k, v in counter.most_common(5): report += f"• `{k}`: {v} times\n"
            for admin_id in ADMIN_IDS:
                try: bot.send_message(admin_id, report)
                except: pass
            last_sent_date = current_date
        time.sleep(30)

threading.Thread(target=daily_report_task, daemon=True).start()

# ================= START / JOIN =================
@bot.message_handler(commands=["start"])
def start(message):
    save_user(message.from_user.id)
    if not is_member(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ I Joined", callback_data="check_join"))
        bot.send_message(message.chat.id, "🔐 *Access Restricted*\n\nPlease join our channel to use the bot.", reply_markup=markup)
        return
    bot.send_message(message.chat.id, "📚 *Welcome!*\n\nType a course name to search or use /courses.")

@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join(c):
    if is_member(c.from_user.id):
        bot.answer_callback_query(c.id, "✅ Access Granted!")
        start(c.message)
    else:
        bot.answer_callback_query(c.id, "❌ Join the channel first!", show_alert=True)

# ================= SEARCH FLOW =================
@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS and not m.text.startswith("/"))
def handle_search(m):
    if not is_member(m.from_user.id): return
    query = m.text.strip()
    log_search(query)
    
    status_msg = bot.send_message(m.chat.id, "🎬 *Searching for your course...*")
    time.sleep(0.8)

    # 1. Exact Match
    match = next((c for c in COURSES if query.lower() == c["name"].lower()), None)
    if match:
        bot.edit_message_text(f"✅ *Course Found!*\n\n🎉 *{match['name']}*\n🔗 {match['link']}", m.chat.id, status_msg.message_id)
        return

    # 2. Similar Match (Suggestions)
    all_names = [c["name"] for c in COURSES]
    suggestions = difflib.get_close_matches(query, all_names, n=3, cutoff=0.4)
    if suggestions:
        markup = types.InlineKeyboardMarkup()
        for s in suggestions:
            markup.add(types.InlineKeyboardButton(text=f"🎓 {s}", callback_data=f"search_btn_{s[:20]}"))
        bot.edit_message_text("🔍 *No exact match.*\nDid you mean one of these? 👇", m.chat.id, status_msg.message_id, reply_markup=markup)
    else:
        # 3. Coming Soon
        log_wishlist(query)
        bot.edit_message_text(f"🚧 *Coming Soon!*\n\nSorry, `{query}` isn't available yet. I've added it to our upload queue! 📝", m.chat.id, status_msg.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("search_btn_"))
def search_btn(c):
    suggestion = c.data.replace("search_btn_", "")
    match = next((course for course in COURSES if course["name"].lower().startswith(suggestion.lower())), None)
    if match:
        bot.edit_message_text(f"🎉 *{match['name']}*\n🔗 {match['link']}", c.message.chat.id, c.message.message_id)

# ================= ADMIN PANEL =================
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Course", "➖ Remove Course")
    markup.add("📊 View Stats", "📝 Wishlist")
    markup.add("📢 Broadcast", "❌ Exit Admin")
    bot.send_message(message.chat.id, "👮 *Admin Panel*", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_handler(m):
    global COURSES
    if m.text == "❌ Exit Admin":
        ADMIN_STATE.pop(m.from_user.id, None)
        bot.send_message(m.chat.id, "❌ Admin Exited", reply_markup=types.ReplyKeyboardRemove())
    
    elif m.text == "📊 View Stats":
        total, counter = get_today_stats()
        text = f"📊 *Today's Searches:* {total}\n\n"
        for k, v in counter.items(): text += f"• `{k}`: {v}\n"
        bot.send_message(m.chat.id, text if total > 0 else "No data today.")

    elif m.text == "📝 Wishlist":
        wishlist = load_json(WISHLIST_FILE, [])
        if not wishlist:
            bot.send_message(m.chat.id, "Wishlist is empty.")
        else:
            counts = Counter([i["query"] for i in wishlist])
            text = "📝 *User Requests (Coming Soon):*\n\n"
            for k, v in counts.most_common(10): text += f"• `{k}` ({v} requests)\n"
            bot.send_message(m.chat.id, text)

    elif m.text == "📢 Broadcast":
        ADMIN_STATE[m.from_user.id] = "BC"
        bot.send_message(m.chat.id, "Send message to broadcast:")

    elif m.text == "➕ Add Course":
        ADMIN_STATE[m.from_user.id] = "ADD"
        bot.send_message(m.chat.id, "Format: `Name | Link`")

    elif m.text == "➖ Remove Course":
        ADMIN_STATE[m.from_user.id] = "REM"
        bot.send_message(m.chat.id, "Type exact name to remove.")

    else:
        state = ADMIN_STATE.get(m.from_user.id)
        if state == "BC":
            users = load_json(USERS_FILE, [])
            for u in users:
                try: bot.send_message(u, f"📢 *Update*\n\n{m.text}")
                except: pass
            bot.send_message(m.chat.id, "✅ Broadcast Sent")
            ADMIN_STATE[m.from_user.id] = None
        elif state == "ADD" and "|" in m.text:
            n, l = map(str.strip, m.text.split("|", 1))
            COURSES.append({"name": n, "link": l})
            save_json(COURSES_FILE, COURSES)
            bot.send_message(m.chat.id, "✅ Added")
            ADMIN_STATE[m.from_user.id] = None
        elif state == "REM":
            COURSES = [c for c in COURSES if c["name"].lower() != m.text.lower().strip()]
            save_json(COURSES_FILE, COURSES)
            bot.send_message(m.chat.id, "🗑️ Removed")
            ADMIN_STATE[m.from_user.id] = None

# ================= RUN =================
if __name__ == "__main__":
    print("🤖 Bot Running...")
    bot.infinity_polling()
