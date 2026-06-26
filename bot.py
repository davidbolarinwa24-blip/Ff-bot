import os
import threading
import telebot
import requests
import json
import random
from datetime import datetime
import time
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

# ===== CONFIG =====
API_TOKEN = os.environ.get('BOT_TOKEN', '8303316737:AAGptofHkHLlhvx6Q-18WSsx9fyoWVOx-Xs')
START_VIDEO_ID = 'PASTE_VIDEO_FILE_ID_HERE' # Send video to bot, copy file_id from Railway logs
WEB_URL = os.environ.get('WEB_URL', 'https://your-railway-app.up.railway.app')

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

DATA_FILE = 'users.json'
user_state = {}
valid_regions = {'BD': 'bd', 'IND': 'ind', 'ME': 'me', 'PK': 'pk', 'US': 'us', 'SG': 'sg', 'ID': 'id', 'TH': 'th', 'VN': 'vn', 'BR': 'br'}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_today():
    return datetime.now().strftime('%Y-%m-%d')

def get_weighted_bonus():
    return random.randint(1, 10) if random.random() < 0.8 else random.randint(11, 50)

# ===== START WITH VIDEO + FRAME/INLINE BUTTONS =====
@bot.message_handler(commands=['start'])
def start(message):
    menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    menu_markup.row('❤️ Send Likes', '🔍 Scan Info')
    menu_markup.row('📦 Track Orders', '🏪 Open Store')
    menu_markup.row('🎁 Free Daily Spin & Referrals')
    menu_markup.row('📈 Level-Up UI', '👑 VIP Sniper')
    menu_markup.row('👤 Profile Visits', '⚙️ Settings')
    
    inline_markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("🔥 Like Tool", web_app=telebot.types.WebAppInfo(url=WEB_URL))
    btn2 = InlineKeyboardButton("📊 Stats", callback_data="stats")
    btn3 = InlineKeyboardButton("💎 VIP", callback_data="vip")
    btn4 = InlineKeyboardButton("❓ Help", callback_data="help")
    inline_markup.add(btn1, btn2, btn3, btn4)
    
    caption = (
        "⚡ | Hi Årmstrõng, nice to see you!\n"
        "👍 | Balance: 0\n"
        "🚀 | LevelUP: ❌Inactive\n"
        "⭐ Active Subscriptions ✨\n"
        "❌ No active subscriptions. Tap Open Store to upgrade!"
    )
    
    if START_VIDEO_ID != 'PASTE_VIDEO_FILE_ID_HERE':
        bot.send_video(message.chat.id, START_VIDEO_ID, caption=caption, reply_markup=inline_markup)
        bot.send_message(message.chat.id, "📱 Menu:", reply_markup=menu_markup)
    else:
        bot.send_message(message.chat.id, caption, reply_markup=menu_markup)

# ===== HANDLE INLINE BUTTONS =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    if call.data == "stats":
        bot.send_message(call.message.chat.id, "📊 Stats panel coming soon...")
    elif call.data == "vip":
        bot.send_message(call.message.chat.id, "💎 VIP access coming soon...")
    elif call.data == "help":
        bot.send_message(call.message.chat.id, "❓ Contact admin: @your_username")

# ===== FILE_ID GRABBER - DELETE AFTER YOU GET ID =====
@bot.message_handler(content_types=['video', 'video_note'])
def get_file_id(message):
    file_id = message.video.file_id if message.video else message.video_note.file_id
    vid_type = "Video" if message.video else "Video Note"
    bot.reply_to(message, 
        f"✅ {vid_type} File ID:\n\n`{file_id}`\n\nCopy → Paste in START_VIDEO_ID → Delete this handler",
        parse_mode='Markdown'
    )

# ===== YOUR EXISTING HANDLERS =====
@bot.message_handler(func=lambda m: m.text == '❤️ Send Likes')
def send_likes_btn(message):
    user_state[message.from_user.id] = 'waiting_uid'
    bot.send_message(message.chat.id, 
        "⚡ SEND LIKES\n─────────────────\nPlease type the UID:",
        reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home')
    )

@bot.message_handler(func=lambda m: m.text == '🔍 Scan Info')
def scan_info_btn(message):
    user_state[message.from_user.id] = 'scanning_uid'
    bot.send_message(message.chat.id, 
        "🔍 PROFILE SCANNER\n─────────────────\nPlease type the UID:",
        reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home')
    )

@bot.message_handler(func=lambda m: m.text == '⬅️ Back to Home')
def back_home(message):
    user_state.pop(message.from_user.id, None)
    start(message)

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'waiting_uid')
def get_uid(message):
    try:
        uid = int(message.text)
        if uid <= 0: raise ValueError
        user_state[message.from_user.id] = {'step': 'waiting_region', 'uid': uid, 'type': 'likes'}
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row('BD', 'IND', 'ME')
        markup.row('PK', 'US', 'SG')
        markup.row('⬅️ Back to Home')
        bot.send_message(message.chat.id, f"🎯 Target Locked: {uid}\n\nSelect server region:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ Invalid UID. Send numbers only.")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'scanning_uid')
def scan_uid_step(message):
    try:
        uid = int(message.text)
        if uid <= 0: raise ValueError
        user_state[message.from_user.id] = {'step': 'waiting_region', 'uid': uid, 'type': 'scan'}
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row('BD', 'IND', 'ME')
        markup.row('PK', 'US', 'SG')
        markup.row('⬅️ Back to Home')
        bot.send_message(message.chat.id, f"🔍 UID: {uid}\n\nSelect server region to scan:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ Invalid UID. Send numbers only.")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id, {}).get('step') == 'waiting_region')
def get_region(message):
    if message.text not in valid_regions:
        bot.send_message(message.chat.id, "❌ Invalid region. Choose BD/IND/ME/PK/US/SG/ID/TH/VN/BR")
        return
    data = user_state[message.from_user.id]
    uid = data['uid']
    region = valid_regions[message.text]
    if data['type'] == 'scan':
        user_state.pop(message.from_user.id, None)
        scan_profile(message.chat.id, uid, region)
    else:
        user_state[message.from_user.id] = {'step': 'waiting_amount', 'uid': uid, 'region': region}
        bot.send_message(message.chat.id, f"🌍 Region: {message.text}\n\nHow many likes? Type 0 for MAX", reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home'))

def scan_profile(chat_id, uid, region):
    loading_msg = bot.send_message(chat_id, "🔍 Scanning profile...")
    api_url = f"https://najmi-ob53-like-api-vvkb.vercel.app/like?uid={uid}&server_name={region}&key=NJM"
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        basic = data.get("basicInfo", {})
        template = f"🔍 **PROFILE SCANNER** [{region.upper()}]\n\n🛡️ Status: 🟢 ACTIVE\n👤 Nickname: {basic.get('nickname', 'N/A')}\nLevel: {basic.get('level', 'N/A')}"
        bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
        bot.send_message(chat_id, template, parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home'))
    except:
        bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
        bot.send_message(chat_id, "❌ Scan Failed", reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home'))

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id, {}).get('step') == 'waiting_amount')
def get_amount(message):
    data = user_state[message.from_user.id]
    uid = data['uid']
    region = data['region']
    try:
        amount = int(message.text)
        if amount < 0: raise ValueError
        if amount == 0: amount = 1000
    except:
        bot.send_message(message.chat.id, "❌ Invalid amount. Send numbers only.")
        return
    user_state.pop(message.from_user.id, None)
    loading_msg = bot.send_message(message.chat.id, "⏳ Processing...")
    api_url = f"https://najmi-ob53-like-api-vvkb.vercel.app/like?uid={uid}&server_name={region}&key=NJM"
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        api_data = response.json()
        basic_info = api_data.get("basicInfo", {})
        name = basic_info.get("nickname", 'N/A')
        new_likes = basic_info.get("liked", 0)
        likes_before = api_data.get('LikesbeforeCommand', '0')
        level = basic_info.get("level", '52')
        template = f"Årmstrõng Bot v2.6.1 🍀\n\nPlayer: #{name}#\nUID: {uid}\nLevel: {level}\nRegion: {region.upper()}\n\nLikes Before: {likes_before}\nLikes After: {new_likes}\nLikes Given: {amount}\n\nStatus: ✅ Success"
        bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
        bot.send_message(message.chat.id, template, reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home'))
    except:
        bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
        bot.send_message(message.chat.id, "❌ API Error: Server is down", reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home'))

@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.perf_counter_ns()
    sent_msg = bot.send_message(message.chat.id, "🏓 Pong!")
    end_time = time.perf_counter_ns()
    response_time_ms = (end_time - start_time) / 1_000_000
    bot.edit_message_text(f"🏓 Pong!\n\n⚡ Response time: `{response_time_ms:.2f}` ms", chat_id=message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown')

@bot.message_handler(commands=['balance'])
def balance(message):
    data = load_data()
    user_id = str(message.from_user.id)
    bonus = data.get(user_id, {}).get('bonus_likes', 0)
    bot.send_message(message.chat.id, f"👍 | Balance: {bonus}")

@bot.message_handler(commands=['spin'])
def spin_wheel(message):
    user_id = str(message.from_user.id)
    data = load_data()
    today = get_today()
    if user_id in data and data[user_id].get('spin_date') == today:
        bot.send_message(message.chat.id, "❌ Already spun today!")
        return
    bonus = get_weighted_bonus()
    if user_id not in data: data[user_id] = {}
    data[user_id]['spin_date'] = today
    data[user_id]['bonus_likes'] = data[user_id].get('bonus_likes', 0) + bonus
    save_data(data)
    bot.send_message(message.chat.id, f"🎉 You won: **{bonus} Bonus Likes!**\n💚 Total Bonus: {data[user_id]['bonus_likes']}", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, "📞 Contact An Admin ✅")

@bot.message_handler(commands=['cancel'])
def cancel(message):
    user_state.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "❌ Cancelled", reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home'))
    start(message)

# ===== FLASK FOR RAILWAY =====
@app.route('/')
def home():
    return "Årmstrøñg Bot v2.6.1 + API Running ✅"

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    print("Årmstrøñg Bot v2.6.1 FILE_ID GRABBER ACTIVE")
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
