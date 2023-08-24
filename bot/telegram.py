
from telebot.async_telebot import AsyncTeleBot
import asyncio


class Telegram:
    def __init__(self, token: str, handler):
        self.token = token
        bot = self.bot = AsyncTeleBot(token)
        self.handler = handler

        @self.bot.message_handler(
            func=lambda message: True, content_types=["location", "text", "photo", "document"]
        )
        async def handle_message(message):
            await handler(message, bot)

        @self.bot.callback_query_handler(func=lambda call: True)
        async def call_beck_admin1(call):
            await handler(call, bot)

        asyncio.run(bot.polling())
