#!/usr/bin/env python3

import os
import time
import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.perf_counter()
    message = await update.message.reply_text("⏱️ Measuring response time...")
    
    end_time = time.perf_counter()
    response_time = round((end_time - start_time) * 1000, 2)
    
    await message.edit_text(f"🚀 Response time: {response_time}ms")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    
    await app.bot.set_my_commands([
        BotCommand("start", "Check bot response time")
    ])
    
    logger.info("Starting bot...")
    
    async with app:
        await app.start()
        await app.updater.start_polling()
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down...")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")