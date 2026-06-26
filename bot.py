import telebot
import requests
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8303316737:AAGptofHkHLlhvx6Q-18WSsx9fyoWVOx-Xs'
START_PHOTO_ID = 'AgACAgQAAxkBAAIBFGo-ureHxrSmHPvpyvfhXS8aMC4GAAKSDmsbsAAB-VF47IxC27I5PwEAAwIAA3gAAzwE'

bot = telebot.TeleBot(API_TOKEN)
user_state = {}
valid_regions = {'BD': 'bd', 'IND': 'ind', 'ME': 'me', 'PK': 'pk', 'US': 'us', 'SG': 'sg', 'ID': 'id', 'TH': 'th', 'VN': 'vn', 'BR': 'br'}

# ===== START - HOT AUT STYLE: PHOTO + 6 FRAME BUTTONS ONLY =====
@bot.message_handler(commands=['start'])
def start(message):
    # AUT style inline frame - 3 rows, 2 buttons each
    inline_markup = InlineKeyboardMarkup(row_width=2)
    inline_markup.add(
        InlineKeyboardButton("❤️ Send Likes", callback_data="send_likes"),
        InlineKeyboardButton("🔍 Scan Info", callback_data="scan_info")
    )
    inline_markup.add(
        InlineKeyboardButton("📦 Track Orders", callback_data="orders"),
        InlineKeyboardButton("🛒 Open Store", callback_data="store")
    )
    inline_markup.add(
        InlineKeyboardButton("🎁 Free Daily Spin", callback_data="spin"),
        InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    )

    # HOT caption like AUT
    caption = (
        "⚡ | I'm Årmstrøñg, nice to see you!\n"
        "👍 | Balance: 0\n"
        "🎯 | LevelUP: ❌ Inactive\n"
        "💎 | Active Subscriptions ✨\n"
        "❌ No active subscriptions. Tap Open Store to upgrade!"
    )

    if START_PHOTO_ID!= 'PASTE_PHOTO_FILE_ID_HERE':
        bot.send_photo(message.chat.id, START_PHOTO_ID, caption=caption, reply_markup=inline_markup)
    else:
        bot.send_message(message.chat.id, caption)

# ===== HANDLE ALL BUTTON CLICKS =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    if call.data == "send_likes":
        user_state[user_id] = 'waiting_uid'
        bot.send_message(call.message.chat.id, "⚡ SEND LIKES\n─────────────────\nPlease type the UID:")
    elif call.data == "scan_info":
        user_state[user_id] = 'scanning_uid'
        bot.send_message(call.message.chat.id, "🔍 PROFILE SCANNER\n─────────────────\nPlease type the UID:")
    elif call.data == "orders":
        bot.send_message(call.message.chat.id, "📦 Track Orders panel coming soon...")
    elif call.data == "store":
        bot.send_message(call.message.chat.id, "🛒 Store panel coming soon...")
    elif call.data == "spin":
        bot.send_message(call.message.chat.id, "🎁 Daily Spin: You got 50 coins!")
    elif call.data == "settings":
        bot.send_message(call.message.chat.id, "⚙️ Settings panel coming soon...")
    elif call.data == "stats":
        bot.send_message(call.message.chat.id, "📊 Stats panel coming soon...")
    elif call.data == "help":
        bot.send_message(call.message.chat.id, "❓ Contact admin: @your_username")

# ===== FILE_ID GRABBER =====
@bot.message_handler(content_types=['photo', 'video', 'video_note'])
def get_file_id(message):
    if message.photo:
        file_id = message.photo[-1].file_id
        bot.reply_to(message, f"✅ Photo File ID:\n`{file_id}`\n\nCopy → Paste in START_PHOTO_ID", parse_mode='Markdown')
    else:
        file_id = message.video.file_id if message.video else message.video_note.file_id
        bot.reply_to(message, f"✅ Video File ID:\n`{file_id}`\n\nCopy → Paste in START_PHOTO_ID", parse_mode='Markdown')

# ===== GET UID =====
@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'waiting_uid')
def get_uid(message):
    try:
        uid = int(message.text)
        user_state[message.from_user.id] = {'step': 'waiting_region', 'uid': uid}
        markup = InlineKeyboardMarkup(row_width=4)
        markup.add(
            InlineKeyboardButton('BD', callback_data='region_BD'),
            InlineKeyboardButton('IND', callback_data='region_IND'),
            InlineKeyboardButton('ME', callback_data='region_ME'),
            InlineKeyboardButton('PK', callback_data='region_PK')
        )
        markup.add(
            InlineKeyboardButton('US', callback_data='region_US'),
            InlineKeyboardButton('SG', callback_data='region_SG'),
            InlineKeyboardButton('ID', callback_data='region_ID'),
            InlineKeyboardButton('TH', callback_data='region_TH')
        )
        bot.send_message(message.chat.id, f"🎯 Target: {uid}\n\nSelect server region:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ Invalid UID. Send numbers only.")

# ===== GET REGION + SUCCESS FRAME =====
@bot.callback_query_handler(func=lambda call: call.data.startswith('region_'))
def get_region(call):
    region_code = call.data.split('_')[1]
    region = valid_regions[region_code]
    uid = user_state[call.from_user.id]['uid']
    user_state.pop(call.from_user.id, None)

    sent_msg = bot.send_message(call.message.chat.id, "⏳ Processing...")
    api_url = f"https://najmi-ob53-like-api-vvkb.vercel.app/like?uid={uid}&server_name={region}&key=NJM"

    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()

        name = data.get('PlayerNickname', 'N/A')
        likes_before = data.get('LikesbeforeCommand', '0')
        likes_given = data.get('LikesGivenByAPI', '0')
        likes_after = data.get('LikesafterCommand', '0')
        remaining = data.get('remains', 'N/A')

        template = (
            "════════\n"
            " 🎉 LIKE SUCCESSFULLY 👍 \n"
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

        bot.edit_message_text(template, chat_id=call.message.chat.id, message_id=sent_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ **Error Connection to API**\n`{str(e)}`",
            chat_id=call.message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown')

print("Årmstrøñg Bot HOT AUT Style is online...")
bot.infinity_polling()
