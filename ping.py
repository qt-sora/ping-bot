import os
import time
import logging
import asyncio
import socket
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
PORT = int(os.getenv('PORT', '8080'))

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_server():
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)
    server_socket.setblocking(False)
    
    logger.info(f"UptimeRobot async server running on port {PORT}")
    
    while True:
        try:
            conn, addr = await asyncio.get_event_loop().sock_accept(server_socket)
            await asyncio.get_event_loop().sock_sendall(conn, b'HTTP/1.1 200 OK\r\n\r\nOK')
            conn.close()
        except Exception:
            await asyncio.sleep(0.1)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.perf_counter()
    message = await update.message.reply_text("⏱️ Measuring response time...")
    
    end_time = time.perf_counter()
    response_time = round((end_time - start_time) * 1000, 2)
    
    await message.edit_text(f"🚀 Response time: {response_time}ms")

async def main():
    if not BOT_TOKEN:
        return
    
    asyncio.create_task(start_server())
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    
    commands = [
        BotCommand("start", "Check bot response time")
    ]
    await app.bot.set_my_commands(commands)
    
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())