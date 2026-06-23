import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
FF_API_KEY = os.getenv("FF_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Bot is running! Use /rank <player_id>")

@dp.message(Command("rank"))
async def rank_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /rank <player_id>")
        return
    player_id = args[1]
    url = f"https://freefire-api.p.rapidapi.com/player/{player_id}"
    headers = {"X-RapidAPI-Key": FF_API_KEY, "X-RapidAPI-Host": "freefire-api.p.rapidapi.com"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                rank = data.get("rank", "Not found")
                name = data.get("nickname", "Unknown")
                await message.answer(f"Player: {name}\nRank: {rank}")
            else:
                await message.answer("Player not found or API error")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
