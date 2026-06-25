print("Årmstrøñg Bot v2.4 VALIDATION ACTIVE")

import telebot
import requests
import json
import random
from datetime import datetime
import os
import time

API_TOKEN = '8303316737:AAGptofHkHLlhvx6Q-18WSsx9fyoWVOx-Xs'
bot = telebot.TeleBot(API_TOKEN)

bot.set_my_commands([
    telebot.types.BotCommand("start", "Open main menu"),
    telebot.types.BotCommand("ping", "Check bot speed"),
    telebot.types.BotCommand("spin", "Daily bonus spin"),
    telebot.types.BotCommand("balance", "Check bonus likes"),
    telebot.types.BotCommand("help", "Contact admin"),
    telebot.types.BotCommand("cancel", "Cancel process")
])

DATA_FILE = 'users.json'
user_state = {}
valid_regions = ['ind', 'bd', 'pk', 'br', 'us', 'sg', 'id', 'th', 'vn', 'me', 'ng']

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
    if random.random() < 0.8:
        return random.randint(1, 10)
    else:
        return random.randint(11, 50)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('❤️ Send Likes', '🔍 Scan Info')
    markup.row('📦 Track Orders', '🏪 Open Store')
    markup.row('🎁 Free Daily Spin & Referrals')
    markup.row('📈 Level-Up UI', '👑 VIP Sniper')
    markup.row('👤 Profile Visits', '⚙️ Settings')
    
    bot.send_message(message.chat.id, 
        "⚡ | Hi Årmstrõng, nice to see you!\n"
        "👍 | Balance: 0\n"
        "🚀 | LevelUP: ❌Inactive\n"
        "⭐ Active Subscriptions ✨\n"
        "❌ No active subscriptions. Tap Open Store to upgrade!",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == '❤️ Send Likes')
def send_likes_btn(message):
    user_state[message.from_user.id] = 'waiting_uid'
    bot.send_message(message.chat.id, 
        "⚡ SEND LIKES\n"
        "─────────────────\n"
        "Please type the UID you want to send likes to in the chat:",
        reply_markup=telebot.types.ReplyKeyboardMarkup().add('⬅️ Back to Home')
    )

@bot.message_handler(func=lambda m: m.text == '🔍 Scan Info')
def scan_info_btn(message):
    user_state[message.from_user.id] = 'scanning_uid'
    bot.send_message(message.chat.id, 
        "🔍 PROFILE SCANNER\n"
        "─────────────────\n"
        "Please type the UID you want to scan in the chat:",
        reply_markup=telebot.types.ReplyKeyboardMarkup().add('⬅️ Back to Home')
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
        user_state[message.from_user.id] = {'step': 'waiting_amount', 'uid': uid}
        bot.send_message(message.chat.id,
            f"🎯 Target Locked: {uid}\n\n"
            f"How many likes do you want to send? (Type a number, or type 0 for MAX)"
        )
    except:
        bot.send_message(message.chat.id, "❌ Invalid UID. Send numbers only.")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'scanning_uid')
def scan_uid(message):
    try:
        uid = int(message.text)
        if uid <= 0: raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ Invalid UID. Send numbers only.")
        return

    user_state.pop(message.from_user.id, None)
    loading_msg = bot.send_message(message.chat.id, "🔍 Scanning profile...")

    region = 'me'
    api_url = f"https://najmi-ob53-like-api-vvkb.vercel.app/like?uid={uid}&server_name={region}&key=NJM"

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()

        basic = data.get("basicInfo", {})
        guild = data.get("guildInfo", {})
        ranking = data.get("rankingInfo", {})
        pet = data.get("petInfo", {})
        credit = data.get("creditScoreInfo", {})

        template = (
            f"🔍 **PROFILE SCANNER**\n\n"
            f"🛡️ **Account Status**\n"
            f"Status: 🟢 ACTIVE\n"
            f"Region: ME\n"
            f"Last Login: {basic.get('lastLogin', 'N/A')}\n\n"
            f"👤 **Basic Information**\n"
            f"Nickname: {basic.get('nickname', 'N/A')}\n"
            f"Level: {basic.get('level', 'N/A')}\n"
            f"Rank: {basic.get('rank', 'N/A')}\n"
            f"Max Rank: {basic.get('maxRank', 'N/A')}\n"
            f"Experience: {basic.get('exp', 'N/A')}\n"
            f"Liked: {basic.get('liked', 'N/A')}\n"
            f"Account ID: {uid}\n"
            f"Account Created: {basic.get('createdAt', 'N/A')}\n"
            f"Account Type: Regular\n"
            f"🏆 **Guild Information**\n"
            f"Guild Name: {guild.get('name', 'None')}\n"
            f"Guild Level: {guild.get('level', 'N/A')}\n"
            f"Guild ID: {guild.get('id', 'N/A')}\n"
            f"Members: {guild.get('members', '0/40')}\n\n"
            f"🏅 **Ranking Information**\n"
            f"BR Rank: {ranking.get('brRank', 'N/A')}\n"
            f"BR Points: {ranking.get('brPoints', 'N/A')}\n"
            f"CS Rank: {ranking.get('csRank', 'N/A')}\n"
            f"CS Points: {ranking.get('csPoints', 'N/A')}\n\n"
            f"⭐ **Pet Information**\n"
            f"Pet Name: {pet.get('name', 'None')}\n"
            f"Pet Level: {pet.get('level', 'N/A')}\n"
            f"Pet Experience: {pet.get('exp', 'N/A')}\n\n"
            f"💳 **Credit Score**\n"
            f"Credit Score: {credit.get('score', '100')}"
        )

        bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
        bot.send_message(message.chat.id, template,
            reply_markup=telebot.types.ReplyKeyboardMarkup().add('⬅️ Back to Home'), parse_mode='Markdown')

    except Exception as e:
        bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
        bot.send_message(message.chat.id, f"❌ Scan Failed: {str(e)}",
            reply_markup=telebot.types.ReplyKeyboardMarkup().add('⬅️ Back to Home'))

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id, {}).get('step') == 'waiting_amount')
def get_amount(message):
    data = user_state[message.from_user.id]
    uid = data['uid']
    
    try:
        amount = int(message.text)
        if amount < 0: raise ValueError
        if amount == 0: amount = 1000
    except:
        bot.send_message(message.chat.id, "❌ Invalid amount. Send numbers only.")
        return

    user_state.pop(message.from_user.id, None)
    loading_msg = bot.send_message(message.chat.id, "⏳ Processing your request...")

    region = 'me'
    api_url = f"https://najmi-ob53-like-api-vvkb.vercel.app/like?uid={uid}&server_name={region}&key=NJM"

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        api_data = response.json()

        basic_info = api_data.get("basicInfo", {})
        name = basic_info.get("nickname", 'N/A')
        new_likes = basic_info.get("liked", 0)
        likes_before = api_data.get('LikesbeforeCommand', '0')
        likes_given = amount
        level = basic_info.get("level", '52')

        template = (
            f"Årmstrõng Bot v2.4 🍀\n\n"
            f"Player: #{name}#\n"
            f"UID: {uid}\n"
            f"Level: {level}\n\n"
            f"Likes Before: {likes_before}\n"
            f"Likes After: {new_likes}\n"
            f"Likes Given: {likes_given}\n\n"
            f"Status: ✅ Success"
        )

        bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
        bot.send_message(message.chat.id, template,
            reply_markup=telebot.types.ReplyKeyboardMarkup().add('⬅️ Back to Home'))

    except Exception as e:
        bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}",
            reply_markup=telebot.types.ReplyKeyboardMarkup().add('⬅️ Back to Home'))

@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.perf_counter_ns()
    sent_msg = bot.send_message(message.chat.id, "🏓 Pong!")
    end_time = time.perf_counter_ns()
    
    response_time_ns = end_time - start_time
    response_time_ms = response_time_ns / 1_000_000
    
    bot.edit_message_text(
        f"🏓 Pong!\n\n⚡ Response time: `{response_time_ns}` ns\n📊 Speed: `{response_time_ms:.2f}` ms",
        chat_id=message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown'
    )

@bot.message_handler(commands=['balance'])
def balance(message):
    data = load_data()
    user_id = str(message.from_user.id)
    bonus = data.get(user_id, {}).get('bonus_likes', 0)
    bot.send_message(message.chat.id, f"👍 | Balance: {bonus}\n⭐ Check Balance And Whitelist Sub🍀")

@bot.message_handler(commands=['spin'])
def spin_wheel(message):
    user_id = str(message.from_user.id)
    data = load_data()
    today = get_today()

    if user_id in data and data[user_id].get('spin_date') == today:
        bot.send_message(message.chat.id, "❌ Already spun today!\nCome back tomorrow for another spin 🎰")
        return

    bonus = get_weighted_bonus()
    if user_id not in data: data[user_id] = {}

    data[user_id]['spin_date'] = today
    data[user_id]['bonus_likes'] = data[user_id].get('bonus_likes', 0) + bonus
    save_data(data)

    wheel = ["🎰", "🎲", "🎯", "🍀", "⭐", "💎", "🔒"]
    spin_msg = bot.send_message(message.chat.id, f"{random.choice(wheel)} Spinning daily wheel...")
    time.sleep(2)

    rarity = "🔓 COMMON" if bonus <= 10 else "🔒 RARE/LOCKED"
    bot.edit_message_text(
        f"{random.choice(wheel)} **SPIN WHEEL RESULT!** {random.choice(wheel)}\n\n"
        f"🎉 You won: **{bonus} Bonus Likes!**\n"
        f"Rarity: {rarity}\n"
        f"💚 Total Bonus: {data[user_id]['bonus_likes']}\n\n"
        f"Come back tomorrow for another spin!",
        chat_id=message.chat.id, message_id=spin_msg.message_id, parse_mode='Markdown'
    )

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, "📞 Contact An Admin ✅\nDM @your_username for support")

@bot.message_handler(commands=['cancel'])
def cancel(message):
    user_state.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "❌ Cancelled Background Process 🔴", reply_markup=telebot.types.ReplyKeyboardRemove())
    start(message)

print("Årmstrøñg Bot v2.4 is now online...")
bot.infinity_polling()
