import telebot
from telebot import types
import json, os, time, difflib, threading
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

# YOUR COMPLETE COURSE LIST
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
ADMIN_STATE = {}

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
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📜 View All Courses", callback_data="show_all_inline"))

    bot.send_message(
        message.chat.id, 
        "📚 *Welcome to Ankit's Vault!*\n\n"
        "🔍 *How to find a course:*\n"
        "1️⃣ Use /courses to see the full list.\n"
        "2️⃣ Type a course name below to search.\n"
        "3️⃣ Click the button below for options.", 
        reply_markup=markup
    )

@bot.message_handler(commands=["courses"])
def show_all(message):
    if not is_member(message.from_user.id): return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, c in enumerate(COURSES):
        markup.add(types.InlineKeyboardButton(text=f"🎓 {c['name']}", callback_data=f"get_c_{i}"))
    bot.send_message(message.chat.id, "📜 *Full Course List:*", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "show_all_inline")
def callback_show_all(c):
    show_all(c.message)

@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join(c):
    if is_member(c.from_user.id):
        bot.answer_callback_query(c.id, "✅ Access Granted!")
        start(c.message)
    else:
        bot.answer_callback_query(c.id, "❌ Join first!", show_alert=True)

# ================= ADMIN COMMAND =================
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Course", "➖ Delete Course")
    markup.add("📊 View Stats", "📝 Wishlist")
    markup.add("📢 Broadcast", "❌ Exit Admin")
    bot.send_message(message.chat.id, "👮 *Admin Panel Active*", reply_markup=markup)

# ================= MASTER HANDLER (Fixes the Search/Admin Conflict) =================
@bot.message_handler(func=lambda m: True)
def master_handler(m):
    global COURSES
    # 1. CHECK IF IT IS AN ADMIN BUTTON CLICK
    if m.from_user.id in ADMIN_IDS:
        if m.text == "❌ Exit Admin":
            ADMIN_STATE.pop(m.from_user.id, None)
            bot.send_message(m.chat.id, "✅ Admin Panel Closed.", reply_markup=types.ReplyKeyboardRemove())
            return
        elif m.text == "➕ Add Course":
            ADMIN_STATE[m.from_user.id] = "ADD_NAME"
            bot.send_message(m.chat.id, "Enter Course Name:")
            return
        elif m.text == "➖ Delete Course":
            ADMIN_STATE[m.from_user.id] = "DELETE"
            bot.send_message(m.chat.id, "Enter EXACT Course Name to delete:")
            return
        elif m.text == "📊 View Stats":
            total, counter = get_today_stats()
            text = f"📊 Today: {total} searches.\n" + "\n".join([f"• {k}: {v}" for k, v in counter.items()])
            bot.send_message(m.chat.id, text if total > 0 else "No data yet.")
            return
        elif m.text == "📝 Wishlist":
            wishlist = load_json(WISHLIST_FILE, [])
            counts = Counter([i["query"] for i in wishlist])
            text = "📝 *Wishlist:*\n" + "\n".join([f"• {k} ({v})" for k, v in counts.most_common(10)])
            bot.send_message(m.chat.id, text if wishlist else "Wishlist is empty.")
            return
        elif m.text == "📢 Broadcast":
            ADMIN_STATE[m.from_user.id] = "BC"
            bot.send_message(m.chat.id, "Enter broadcast message:")
            return

        # 2. CHECK IF ADMIN IS CURRENTLY TYPING NEW DATA (Add/Delete/Broadcast)
        state = ADMIN_STATE.get(m.from_user.id)
        if state:
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
                bot.send_message(m.chat.id, f"🗑️ Processed deletion for: {m.text}")
                ADMIN_STATE[m.from_user.id] = None
            elif state == "BC":
                users = load_json(USERS_FILE, [])
                for u in users:
                    try: bot.send_message(u, f"📢 *New Announcement*\n\n{m.text}")
                    except: pass
                bot.send_message(m.chat.id, "✅ Broadcast sent!")
                ADMIN_STATE[m.from_user.id] = None
            return

    # 3. IF NOT AN ADMIN ACTION, TREAT AS SEARCH
    if not is_member(m.from_user.id): return
    query = m.text.strip()
    
    # Log Search for Stats
    today = datetime.now().strftime("%Y-%m-%d")
    stats = load_json(f"stats_{today}.json", [])
    stats.append({"query": query})
    save_json(f"stats_{today}.json", stats)

    status_msg = bot.send_message(m.chat.id, "🎬 *Searching for your course...*")
    time.sleep(0.5)

    match = next((c for c in COURSES if query.lower() in c["name"].lower()), None)
    
    if match:
        bot.edit_message_text(f"✅ *Found!*\n\n🎉 *{match['name']}*\n🔗 {match['link']}", m.chat.id, status_msg.message_id)
    else:
        all_names = [c["name"] for c in COURSES]
        suggestions = difflib.get_close_matches(query, all_names, n=2, cutoff=0.3)
        markup = types.InlineKeyboardMarkup()
        if suggestions:
            for s in suggestions:
                idx = next((i for i, c in enumerate(COURSES) if c["name"] == s), None)
                markup.add(types.InlineKeyboardButton(text=f"🎓 {s}", callback_data=f"get_c_{idx}"))
        
        wishlist = load_json(WISHLIST_FILE, [])
        wishlist.append({"query": query, "date": today})
        save_json(WISHLIST_FILE, wishlist)
        
        bot.edit_message_text(f"🚧 *Coming Soon!*\n\nAdded `{query}` to queue. 📝\n🆘 *Urgent?* DM: @ytmn20", m.chat.id, status_msg.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("get_c_"))
def callback_get_course(c):
    idx = int(c.data.replace("get_c_", ""))
    if idx < len(COURSES):
        match = COURSES[idx]
        bot.send_message(c.message.chat.id, f"🎉 *{match['name']}*\n🔗 {match['link']}")
    bot.answer_callback_query(c.id)

if __name__ == "__main__":
    bot.remove_webhook()
    print("🚀 Bot is live and listening...")
    bot.infinity_polling()
