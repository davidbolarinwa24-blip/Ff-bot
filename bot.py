import telebot
import requests
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

API_TOKEN = '8303316737:AAGptofHkHLlhvx6Q-18WSsx9fyoWVOx-Xs'
START_VIDEO_ID = 'PASTE_VIDEO_FILE_ID_HERE'

bot = telebot.TeleBot(API_TOKEN)
user_state = {}
valid_regions = {'BD': 'bd', 'IND': 'ind', 'ME': 'me', 'PK': 'pk', 'US': 'us', 'SG': 'sg', 'ID': 'id', 'TH': 'th', 'VN': 'vn', 'BR': 'br'}

def load_data():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open('users.json', 'w') as f:
        json.dump(data, f)

# ===== START WITH VIDEO + FRAME + MENU =====
@bot.message_handler(commands=['start'])
def start(message):
    # 1. Inline keyboard "frame" under video - AUT bot style
    inline_markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("🔥 Send Likes", callback_data="send_likes")
    btn2 = InlineKeyboardButton("🔍 Scan Info", callback_data="scan_info")
    btn3 = InlineKeyboardButton("📊 Stats", callback_data="stats")
    btn4 = InlineKeyboardButton("❓ Help", callback_data="help")
    inline_markup.add(btn1, btn2, btn3, btn4)
    
    # 2. Reply keyboard menu below
    menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    menu_markup.row('❤️ Send Likes', '🔍 Scan Info')
    menu_markup.row('⬅️ Back to Home')
    
    caption = "⚡ | I'm Årmstrøñg, nice to see you!\n👍 | Balance: 0"
    
    if START_VIDEO_ID != 'PASTE_VIDEO_FILE_ID_HERE':
        bot.send_video(message.chat.id, START_VIDEO_ID, caption=caption, reply_markup=inline_markup)
        bot.send_message(message.chat.id, "📱 Menu:", reply_markup=menu_markup)
    else:
        bot.send_message(message.chat.id, caption, reply_markup=menu_markup)

# ===== HANDLE INLINE BUTTON CLICKS =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    
    if call.data == "send_likes":
        user_state[user_id] = 'waiting_uid'
        bot.send_message(call.message.chat.id, 
            "⚡ SEND LIKES\n─────────────────\nPlease type the UID:",
            reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home')
        )
    elif call.data == "scan_info":
        user_state[user_id] = 'scanning_uid'
        bot.send_message(call.message.chat.id, 
            "🔍 PROFILE SCANNER\n─────────────────\nPlease type the UID:",
            reply_markup=ReplyKeyboardMarkup().add('⬅️ Back to Home')
        )
    elif call.data == "stats":
        bot.send_message(call.message.chat.id, "📊 Stats panel coming soon...")
    elif call.data == "help":
        bot.send_message(call.message.chat.id, "❓ Contact admin: @your_username")

# ===== FILE_ID GRABBER =====
@bot.message_handler(content_types=['video', 'video_note'])
def get_file_id(message):
    file_id = message.video.file_id if message.video else message.video_note.file_id
    bot.reply_to(message, f"✅ File ID:\n`{file_id}`\n\nCopy → Paste in START_VIDEO_ID", parse_mode='Markdown')

# ===== BACK BUTTON =====
@bot.message_handler(func=lambda m: m.text == '⬅️ Back to Home')
def back_home(message):
    user_state.pop(message.from_user.id, None)
    start(message)

# ===== GET UID =====
@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'waiting_uid')
def get_uid(message):
    try:
        uid = int(message.text)
        user_state[message.from_user.id] = {'step': 'waiting_region', 'uid': uid}
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row('BD', 'IND', 'ME', 'PK')
        markup.row('US', 'SG', 'ID', 'TH')
        markup.row('⬅️ Back to Home')
        bot.send_message(message.chat.id, f"🎯 Target: {uid}\n\nSelect server region:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ Invalid UID. Send numbers only.")

# ===== GET REGION + EXACT SUCCESS FRAME FROM SCREENSHOT =====
@bot.message_handler(func=lambda m: user_state.get(m.from_user.id, {}).get('step') == 'waiting_region')
def get_region(message):
    if message.text not in valid_regions:
        bot.send_message(message.chat.id, "❌ Invalid region. Choose from buttons.")
        return
    
    data = user_state[message.from_user.id]
    uid = data['uid']
    region = valid_regions[message.text]
    user_state.pop(message.from_user.id, None)
    
    sent_msg = bot.send_message(message.chat.id, "⏳ Processing...")
    api_url = f"https://najmi-ob53-like-api-vvkb.vercel.app/like?uid={uid}&server_name={region}&key=NJM"
    
    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        name = data.get('PlayerNickname', 'N/A')
        likes_before = data.get('LikesbeforeCommand', '0')
        likes_given = data.get('LikesGivenByAPI', '0')
        likes_after = data.get('LikesafterCommand', '0')
        remaining = data.get('remains', 'N/A')
        
        # ===== EXACT FRAME FROM YOUR SCREENSHOT LINES 37-49 =====
        template = (
            "════════\n"
            "  🎉 LIKE SUCCESSFULLY 👍  \n"
            "════════\n\n"
            f"👑 Name: {name}\n"
            f"🆔 UID: {uid}\n"
            f"🌐 Region: {region.upper()}\n"
            "────────────────────────\n\n"
            f"❤️ Likes Before: {likes_before}\n"
            f"⚡ Likes Given: {likes_given}\n"
            f"💚 Likes after: {likes_after}\n\n"
            f"📊 Remaining Requests: {remaining}"
        )
        
        bot.edit_message_text(template, chat_id=message.chat.id, message_id=sent_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ **Error Connection to API**\n`{str(e)}`", 
            chat_id=message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown')

print("Årmstrøñg Bot v2.6.1 with FRAME is online...")
bot.infinity_polling()
