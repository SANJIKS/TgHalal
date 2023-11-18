import logging
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logger.info(f"Received message from {message.from_user.username}: {message.text}")

    async def on_post_process_message(self, message: types.Message, data: dict):
        logger.info(f"Processed message from {message.from_user.username}: {message.text}")