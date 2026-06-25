print("Årmstrøñg Bot v2.1 VALIDATION ACTIVE")

import telebot
import requests

API_TOKEN = '8303316737:AAGptofHkHLlhvx6Q-18WSsx9fyoWVOx-Xs'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "🔥 **Årmstrøñg Bot v2.1 is online 24/7!** 🔥\n\n"
        "Usage: `/like [region] [uid]`\n"
        "Example: `/like ind 811094988`\n\n"
        "Regions: ind, bd, pk, br, us",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['like'])
def handle_like(message):
    args = message.text.split()

    # 1. VALIDATION: Check argument count
    if len(args) < 3:
        bot.reply_to(message, "❌ **Usage:** `/like {region} {uid}`\nExample: `/like ind 811094988`", parse_mode='Markdown')
        return

    region = args[1].lower()
    uid = args[2]

    # 2. VALIDATION: Check region
    valid_regions = ['ind', 'bd', 'pk', 'br', 'us', 'sg', 'id', 'th', 'vn']
    if region not in valid_regions:
        bot.reply_to(message, f"❌ **Invalid Region**\nValid: {', '.join(valid_regions).upper()}\nExample: `/like ind 811094988`")
        return

    # 3. VALIDATION: Check UID is numeric
    try:
        uid = int(uid)
        if uid <= 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "❌ **Error:** UID must be numbers only > 0\nExample: `/like ind 811094988`")
        return

    sent_msg = bot.reply_to(message, "⏳ *Processing your request...*", parse_mode='Markdown')

    api_url = f"https://najmi-ob53-like-api-vvkb.vercel.app/like?uid={uid}&server_name={region}&key=NJM"

    try:
        # 4. SAFETY: timeout + raise_for_status
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()

        basic_info = data.get("basicInfo", {})
        name = basic_info.get("nickname", 'N/A')
        new_likes = basic_info.get("liked", 0)

        likes_before = data.get('LikesbeforeCommand', '0')
        likes_given = data.get('LikesGivenByAPI', '0')
        remaining = data.get('remains', 'N/A')

        template = (
            f"┏━━━━━━━━━━━━━━┓\n"
            f"┃ 🎉 LIKE SUCCESSFULLY ┃\n"
            f"┗━━━━━━━━━━━━━━┛\n\n"
            f"👑 Name: {name}\n"
            f"🆔 UID: {uid}\n"
            f"🌍 Region: {region.upper()}\n\n"
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
        bot.edit_message_text("⏱️ **API Timeout**\nAPI took too long. Try again in 10s",
            chat_id=message.chat.id, message_id=sent_msg.message_id)

    except requests.exceptions.HTTPError as e:
        bot.edit_message_text(f"❌ **API HTTP Error:** {response.status_code}\n\n{response.text}",
            chat_id=message.chat.id, message_id=sent_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ **Error:** `{str(e)}`",
            chat_id=message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown')

print("Årmstrøñg Bot v2.1 is now online...")
bot.infinity_polling()
