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

# ================= KEYBOARDS =================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('📚 All Courses')
    btn2 = types.KeyboardButton('🔎 Search Course')
    btn3 = types.KeyboardButton('⭐ VIP Access')
    btn4 = types.KeyboardButton('📞 Support')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

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

# ================= USER SIDE =================
@bot.message_handler(commands=["start"])
def start(message):
    save_user(message.from_user.id)
    if not is_member(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ I Joined", callback_data="check_join"))
        bot.send_message(message.chat.id, "🔐 *Access Restricted*\nPlease join our channel to use the bot.", reply_markup=markup)
        return
    
    bot.send_message(
        message.chat.id, 
        "📚 *Welcome to Ankit's Vault!*\n\nSelect an option from the menu below:", 
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join(c):
    if is_member(c.from_user.id):
        bot.answer_callback_query(c.id, "✅ Access Granted!")
        start(c.message)
    else:
        bot.answer_callback_query(c.id, "❌ Join the channel first!", show_alert=True)

@bot.message_handler(func=lambda m: m.text == '📚 All Courses')
def btn_all_courses(message):
    show_all(message)

@bot.message_handler(func=lambda m: m.text == '🔎 Search Course')
def btn_search_prompt(message):
    bot.send_message(message.chat.id, "🔍 **Ready to Search!**\n\nSend me the name of the course you want (e.g., 'CapCut' or 'Editing').")

@bot.message_handler(func=lambda m: m.text == '⭐ VIP Access')
def btn_vip(message):
    bot.send_message(message.chat.id, "⭐ **VIP Premium Access**\n\nGet original, watermark-free courses!\n\nContact @CoursesByAnkit for details.")

@bot.message_handler(func=lambda m: m.text == '📞 Support')
def btn_support(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Message Admin", url="https://t.me/CoursesByAnkit"))
    bot.send_message(message.chat.id, "📞 **Support & Requests**\n\nClick below to message me directly!", reply_markup=markup)

@bot.message_handler(commands=["courses"])
def show_all(message):
    if not is_member(message.from_user.id): return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for c in COURSES:
        # We use a unique ID or index to avoid long callback data errors
        markup.add(types.InlineKeyboardButton(text=f"🎓 {c['name']}", callback_data=f"get_c_{COURSES.index(c)}"))
    bot.send_message(message.chat.id, "📜 *Full Course List:*", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS and not m.text.startswith("/"))
def handle_search(m):
    if not is_member(m.from_user.id): return
    
    # --- FIX: IGNORE MENU BUTTON TEXT ---
    menu_buttons = ['📚 All Courses', '🔎 Search Course', '⭐ VIP Access', '📞 Support']
    if m.text in menu_buttons:
        return # Do nothing if the user just clicked a menu button

    query = m.text.strip()
    
    # Search Animation
    bot.send_chat_action(m.chat.id, 'typing')
    status_msg = bot.send_message(m.chat.id, "🎬 *Searching the vault...*")
    time.sleep(1.0) 

    # Log stats
    today = datetime.now().strftime("%Y-%m-%d")
    stats = load_json(f"stats_{today}.json", [])
    stats.append({"query": query})
    save_json(f"stats_{today}.json", stats)

    # Search Logic
    match = next((c for c in COURSES if query.lower() in c["name"].lower()), None)
    
    if match:
        bot.delete_message(m.chat.id, status_msg.message_id)
        bot.send_message(m.chat.id, f"✅ *Found!*\n\n🎉 *{match['name']}*\n🔗 {match['link']}")
    else:
        all_names = [c["name"] for c in COURSES]
        suggestions = difflib.get_close_matches(query, all_names, n=3, cutoff=0.3)
        
        if suggestions:
            markup = types.InlineKeyboardMarkup()
            for s in suggestions:
                # Find the index of the suggestion to create the callback
                idx = next((i for i, c in enumerate(COURSES) if c["name"] == s), None)
                if idx is not None:
                    markup.add(types.InlineKeyboardButton(text=f"🎓 {s}", callback_data=f"get_c_{idx}"))
            bot.edit_message_text("🔍 *Not found.* Did you mean one of these? 👇", m.chat.id, status_msg.message_id, reply_markup=markup)
        else:
            wishlist = load_json(WISHLIST_FILE, [])
            wishlist.append({"query": query, "date": today})
            save_json(WISHLIST_FILE, wishlist)
            
            rec_markup = types.InlineKeyboardMarkup()
            rec_markup.add(types.InlineKeyboardButton("🎬 Editing Mastery", callback_data="get_c_0")) # Index 0
            rec_markup.add(types.InlineKeyboardButton("🤖 ChatGPT Course", callback_data="get_c_5")) # Index 5
            
            text = (f"🚧 *Coming Soon!*\n\n"
                    f"I couldn't find `{query}`. It's added to our wishlist! 📝\n\n"
                    f"🔥 *Recommended for you:*")
            bot.edit_message_text(text, m.chat.id, status_msg.message_id, reply_markup=rec_markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("get_c_"))
def handle_suggest(c):
    try:
        idx = int(c.data.replace("get_c_", ""))
        match = COURSES[idx]
        bot.send_message(c.message.chat.id, f"🎉 *{match['name']}*\n🔗 {match['link']}")
        bot.answer_callback_query(c.id)
    except:
        bot.answer_callback_query(c.id, "❌ Error retrieving course.")

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
        bot.send_message(m.chat.id, "Admin Closed.", reply_markup=main_menu())
    
    elif m.text == "➕ Add Course":
        ADMIN_STATE[m.from_user.id] = "ADD_NAME"
        bot.send_message(m.chat.id, "Enter Course Name:")
    elif m.text == "➖ Delete Course":
        ADMIN_STATE[m.from_user.id] = "DELETE"
        bot.send_message(m.chat.id, "Enter EXACT Name to delete:")
    elif m.text == "📊 View Stats":
        total, counter = get_today_stats()
        text = f"📊 Today: {total} searches.\n" + "\n".join([f"• {k}: {v}" for k, v in counter.items()])
        bot.send_message(m.chat.id, text if total > 0 else "No searches today.")
    elif m.text == "📝 Wishlist":
        wishlist = load_json(WISHLIST_FILE, [])
        counts = Counter([i["query"] for i in wishlist])
        text = "📝 *Most Requested:* \n\n" + "\n".join([f"• {k} ({v})" for k, v in counts.most_common(10)])
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
            bot.send_message(m.chat.id, "✅ Course Added!")
            ADMIN_STATE[m.from_user.id] = None
        elif state == "DELETE":
            COURSES = [c for c in COURSES if c["name"].lower() != m.text.lower().strip()]
            save_json(COURSES_FILE, COURSES)
            bot.send_message(m.chat.id, "🗑️ Deleted.")
            ADMIN_STATE[m.from_user.id] = None
        elif state == "BC":
            users = load_json(USERS_FILE, [])
            for u in users:
                try: bot.send_message(u, f"📢 *New Announcement*\n\n{m.text}")
                except: pass
            bot.send_message(m.chat.id, "✅ Broadcast Sent.")
            ADMIN_STATE[m.from_user.id] = None

if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling()
