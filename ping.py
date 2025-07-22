import logging
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "YOUR_TELEGRAM_BOT_TOKEN"

# Dummy HTTP server using http.server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot Status: Online")
    
    def log_message(self, format, *args):
        pass

def run_http_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SimpleHandler)
    httpd.serve_forever()

# Telegram Bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    message = await update.message.reply_text("🛰️ Pinging...")
    end_time = time.time()
    
    ping_ms = round((end_time - start_time) * 1000, 2)
    
    await message.edit_text(f"🏓 Pong! {ping_ms}ms")

async def setup_commands(app: Application):
    commands = [BotCommand("start", "Check bot ping")]
    await app.bot.set_my_commands(commands)

def main():
    # Start HTTP server in a thread
    http_thread = threading.Thread(target=run_http_server)
    http_thread.daemon = True
    http_thread.start()
    
    # Start Telegram bot
    tg_app = Application.builder().token(TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.post_init = setup_commands
    
    tg_app.run_polling()

if __name__ == "__main__":
    main()