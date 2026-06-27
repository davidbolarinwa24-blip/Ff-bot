import telebot
import requests
import json
import os
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

API_TOKEN = '8303316737:AAGptofHkHLlhvx6Q-18WSsx9fyoWVOx-Xs'
START_PHOTO_ID = 'AgACAgQAAxkBAAIBFGo-ureHxrSmHPvpyvfhXS8aMC4GAAKSDmsbsAAB-VF47IxC27I5PwEAAwIAA3gAAzwE'

bot = telebot.TeleBot(API_TOKEN)
user_state = {}
user_likes = {}

valid_regions = {'BD': 'bd', 'IND': 'ind', 'ME': 'me', 'PK': 'pk', 'US': 'us', 'SG': 'sg', 'ID': 'id', 'TH': 'th', 'VN': 'vn', 'BR': 'br'}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    if user_id not in user_likes:
        user_likes[user_id] = 0

    inline_markup = InlineKeyboardMarkup(row_width=2)
    inline_markup.add(
        InlineKeyboardButton("❤️ Send Likes", callback_data="send_likes"),
        InlineKeyboardButton("🔍 Scan Info", callback_data="scan_info")
    )
    inline_markup.add(
        InlineKeyboardButton("📋 Track Orders", callback_data="orders"),
        InlineKeyboardButton("🛒 Open Store", callback_data="store")
    )
    inline_markup.add(
        InlineKeyboardButton("🎁 Free Daily Spin & Referrals", callback_data="spin")
    )
    inline_markup.add(
        InlineKeyboardButton("🎯 Level-Up UI", callback_data="levelup"),
        InlineKeyboardButton("🎯 VIP Sniper", callback_data="sniper")
    )
    inline_markup.add(
        InlineKeyboardButton("👥 Profile Visits", callback_data="visits"),
        InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    )

    caption = (
        f"👋 | Hi {first_name}, nice to see you!\n"
        f"👍 | Balance: {user_likes[user_id]}\n"
        f"🎯 | LevelUP: ❌ Inactive\n"
        f"💎 | Active Subscriptions ✨\n"
        f"❌ No active subscriptions. Tap Open Store to upgrade!"
    )

    if START_PHOTO_ID!= 'PASTE_PHOTO_FILE_ID_HERE':
        bot.send_photo(message.chat.id, START_PHOTO_ID, caption=caption, reply_markup=inline_markup)
    else:
        bot.send_message(message.chat.id, caption, reply_markup=inline_markup)

    menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    menu_markup.row('☰ Menu')
    bot.send_message(message.chat.id, "Menu", reply_markup=menu_markup)

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

    elif call.data == "spin":
        spin_likes = random.randint(5, 20)
        user_likes[user_id] = user_likes.get(user_id, 0) + spin_likes
        bot.send_message(call.message.chat.id, f"🎁 Daily Spin: You got {spin_likes} likes! New balance: {user_likes[user_id]}")

    elif call.data in ["orders", "store", "levelup", "sniper", "visits", "settings"]:
        panels = {
            "orders": "📦 Track Orders panel coming soon...",
            "store": "🛒 Store panel coming soon...",
            "levelup": "🎯 Level-Up UI panel coming soon...",
            "sniper": "🎯 VIP Sniper panel coming soon...",
            "visits": "👥 Profile Visits panel coming soon...",
            "settings": "⚙️ Settings panel coming soon..."
        }
        bot.send_message(call.message.chat.id, panels[call.data])

    elif call.data.startswith('region_'):
        region_code = call.data.split('_')[1]

        if region_code not in valid_regions:
            bot.send_message(call.message.chat.id, f"❌ Invalid region: {region_code}")
            return

        region = valid_regions[region_code]

        if user_id not in user_state or 'uid' not in user_state[user_id]:
            bot.send_message(call.message.chat.id, "❌ UID not found. Click Send Likes again.")
            return

        uid = user_state[user_id]['uid']
        user_state.pop(user_id, None)

        sent_msg = bot.send_message(call.message.chat.id, "⏳ Processing...")

        # FIXED API URL - YOUR NEW VERCEL LINK
        api_url = f"https://free-fire-api-eta.vercel.app/like?uid={uid}&server_name={region}&key=NJM"

        try:
            response = requests.get(api_url, timeout=15)
            data = response.json()

            name = data.get('PlayerNickname', 'N/A')
            likes_before = data.get('LikesbeforeCommand', '0')
            likes_given = data.get('LikesGivenByAPI', '0')
            likes_after = data.get('LikesafterCommand', '0')
            remaining = data.get('remains', 'N/A')

            likes_given_int = int(likes_given) if str(likes_given).isdigit() else 0
            user_likes[user_id] = user_likes.get(user_id, 0) + likes_given_int

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
                f"📊 Remaining Requests: {remaining}\n"
                f"💰 Your Balance: {user_likes[user_id]}"
            )

            bot.edit_message_text(template, chat_id=call.message.chat.id, message_id=sent_msg.message_id)

        except Exception as e:
            bot.edit_message_text(f"❌ **API Error**\n`{str(e)}`",
                chat_id=call.message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown')

@bot.message_handler(content_types=['photo', 'video', 'video_note'])
def get_file_id(message):
    if message.photo:
        file_id = message.photo[-1].file_id
        bot.reply_to(message, f"✅ Photo File ID:\n`{file_id}`\n\nCopy → Paste in START_PHOTO_ID", parse_mode='Markdown')
    else:
        file_id = message.video.file_id if message.video else message.video_note.file_id
        bot.reply_to(message, f"✅ Video File ID:\n`{file_id}`\n\nCopy → Paste in START_VIDEO_ID", parse_mode='Markdown')

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'waiting_uid')
def get_uid(message):
    try:
        uid = int(message.text)
        user_state[message.from_user.id] = {'uid': uid}
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

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'scanning_uid')
def scan_uid(message):
    try:
        uid = int(message.text)
        user_state.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, f"🔍 Scanning UID: {uid}...\n⏳ Please wait...")

        fake_name = f"Player_{uid}"
        fake_level = random.randint(20, 80)
        fake_likes = random.randint(1000, 99999)

        result = (
            "════════\n"
            " 🔍 SCAN RESULT\n"
            "════════\n\n"
            f"👑 Name: {fake_name}\n"
            f"🆔 UID: {uid}\n"
            f"🎯 Level: {fake_level}\n"
            f"❤️ Total Likes: {fake_likes}\n"
            f"🌐 Region: Unknown"
        )
        bot.send_message(message.chat.id, result)
    except:
        bot.send_message(message.chat.id, "❌ Invalid UID. Send numbers only.")

print("Årmstrøñg Bot AUT Style - Spin 5-20 + Region Fixed is online...")
bot.infinity_polling()
