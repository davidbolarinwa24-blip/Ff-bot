print("Årmstrøñg Bot v2.1 VALIDATION ACTIVE")

import telebot
import requests
import json
import random
from datetime import datetime
import os
import time

API_TOKEN = 'PASTE_NEW_TOKEN_HERE'
bot = telebot.TeleBot(API_TOKEN)

DATA_FILE = 'users.json'
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

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "🔥 **Årmstrøñg Bot v2.1 is online 24/7!** 🔥\n\n"
        "Type `/menu` to see all commands 👇",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['menu'])
def menu(message):
    menu_text = (
        "┏━━━━━━━━━━┓\n"
        "┃ ÅRMSTRØNG BOT MENU ┃\n"
        "┗━━━━━━━━━━┛\n\n"
        "🎯 **LIKE COMMANDS:**\n"
        "`/like [region] [uid]` - Send likes to player\n"
        "🎁 **BONUS COMMANDS:**\n"
        "`/daily` - Claim random 1-10 bonus likes daily\n"
        "`/spin` - Spin wheel for 1-20 bonus likes daily\n"
        "🌍 **REGIONS:** ind, bd, pk, br, us, sg, id, th, vn, me, ng\n"
        "Note: ng = Nigeria = me server\n"
        "┏━━━━━━━━━━┓\n"
        "┃ Årmstrøñg Bot v2.1 ┃\n"
        "┗━━━━━━━━━━┛"
    )
    bot.reply_to(message, menu_text, parse_mode='Markdown')

@bot.message_handler(commands=['like'])
def handle_like(message):
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ **Usage:** `/like {region} {uid}`\nExample: `/like ind 811094988`", parse_mode='Markdown')
        return

    region = args[1].lower()
    uid = args[2]

    if region == 'ng':
        region = 'me'

    if region not in valid_regions:
        bot.reply_to(message, f"❌ **Invalid Region**\nValid: {', '.join(valid_regions).upper()}", parse_mode='Markdown')
        return

    try:
        uid = int(uid)
        if uid <= 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "❌ **Error:** UID must be numbers only > 0")
        return

    sent_msg = bot.reply_to(message, "⏳ *Processing your request...*", parse_mode='Markdown')

    api_url = f"https://najmi-ob53-like-api-vvkb.vercel.app/like?uid={uid}&server_name={region}&key=NJM"

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()

        basic_info = data.get("basicInfo", {})
        name = basic_info.get("nickname", 'N/A')
        new_likes = basic_info.get("liked", 0)
        likes_before = data.get('LikesbeforeCommand', '0')
        likes_given = data.get('LikesGivenByAPI', '0')
        remaining = data.get('remains', 'N/A')
        region_display = "NG/ME" if region == 'me' else region.upper()

        template = (
            f"┏━━━━━━━━━━━━━━┓\n"
            f"┃ 🎉 LIKE SUCCESSFULLY ┃\n"
            f"┗━━━━━━━━━━━━━━┛\n\n"
            f"👑 Name: {name}\n"
            f"🆔 UID: {uid}\n"
            f"🌍 Region: {region_display}\n\n"
            f"❌ Likes Before: {likes_before}\n"
            f"📤 Likes Given: {likes_given}\n"
            f"💚 Likes After: {new_likes}\n\n"
            f"📊 Remaining Requests: {remaining}\n\n"
            f"┏━━━━━━━━━━━━━━┓\n"
            f"┃ Årmstrøñg Bot v2.1 ┃\n"
            f"┗━━━━━━━━━━━━━━┛"
        )
        bot.edit_message_text(template, chat_id=message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown')

    except requests.exceptions.Timeout:
        bot.edit_message_text("⏱️ **API Timeout**\nTry again in 10s", chat_id=message.chat.id, message_id=sent_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ **Error:** `{str(e)}`", chat_id=message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown')

@bot.message_handler(commands=['daily'])
def daily_bonus(message):
    user_id = str(message.from_user.id)
    data = load_data()
    today = get_today()

    if user_id in data and data[user_id].get('daily_date') == today:
        bot.reply_to(message, "❌ **Already claimed today!**\nCome back tomorrow for daily bonus 🎁")
        return

    bonus = random.randint(1, 10) # Random 1-10 likes, not fixed 5

    if user_id not in data:
        data[user_id] = {}

    data[user_id]['daily_date'] = today
    data[user_id]['bonus_likes'] = data[user_id].get('bonus_likes', 0) + bonus
    save_data(data)

    bot.reply_to(message, f"🎁 **Daily Bonus Claimed!**\n🎉 You got: **{bonus} Bonus Likes!**\n💚 Total Bonus: {data[user_id]['bonus_likes']}\n\nCome back tomorrow for more!")

@bot.message_handler(commands=['spin'])
def spin_wheel(message):
    user_id = str(message.from_user.id)
    data = load_data()
    today = get_today()

    if user_id in data and data[user_id].get('spin_date') == today:
        bot.reply_to(message, "❌ **Already spun today!**\nCome back tomorrow for another spin 🎰")
        return

    bonus = random.randint(1, 20) # Spin gives 1-20 random likes

    if user_id not in data:
        data[user_id] = {}

    data[user_id]['spin_date'] = today
    data[user_id]['bonus_likes'] = data[user_id].get('bonus_likes', 0) + bonus
    save_data(data)

    wheel = ["🎰", "🎲", "🎯", "🍀", "⭐", "💎"]
    spin_msg = bot.reply_to(message, f"{random.choice(wheel)} Spinning the wheel...")

    time.sleep(2)
    bot.edit_message_text(
        f"{random.choice(wheel)} **SPIN RESULT!** {random.choice(wheel)}\n\n"
        f"🎉 You won: **{bonus} Bonus Likes!**\n"
        f"💚 Total Bonus: {data[user_id]['bonus_likes']}\n\n"
        f"Come back tomorrow for another spin!",
        chat_id=message.chat.id, message_id=spin_msg.message_id, parse_mode='Markdown'
    )

print("Årmstrøñg Bot v2.1 is now online...")
bot.infinity_polling()
