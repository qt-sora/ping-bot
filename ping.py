import logging
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure modern logging with colored output
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and modern styling"""

    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = self.formatTime(record, '%H:%M:%S')
        return (
            f"{self.DIM}{timestamp}{self.RESET} "
            f"{color}{self.BOLD}[{record.levelname:^8}]{self.RESET} "
            f"{self.BOLD}{record.name}{self.RESET} → {record.getMessage()}"
        )

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    return logging.getLogger(__name__)

logger = setup_logging()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "YOUR_TELEGRAM_BOT_TOKEN"

# Dummy HTTP server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logger.info(f"🌐 HTTP request from {self.client_address[0]}:{self.client_address[1]}")
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("✅ Bot Status: Online".encode("utf-8"))

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        logger.info(f"📡 {format % args}")

def run_http_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SimpleHandler)
    logger.info("🚀 Keep-alive server launched on port 8080")
    httpd.serve_forever()

# Telegram command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"💬 /start from @{user.username or 'N/A'} ({user.full_name}) [ID: {user.id}]")

    start_time = time.time()
    await update.message.reply_text("🛰️ Pinging...")
    end_time = time.time()

    ping_ms = round((end_time - start_time) * 1000, 2)
    logger.info(f"⚡ Response time: {ping_ms}ms")

    await update.message.reply_text(f"🏓 Pong! {ping_ms}ms")

# Configure command list
async def setup_commands(app: Application):
    commands = [BotCommand("start", "Check bot ping")]
    try:
        await app.bot.set_my_commands(commands)
        logger.info("⚙️  Command menu configured: /start")
    except Exception as e:
        logger.warning(f"⚠️ Failed to set commands: {e}")

# App entry point
def main():
    if not TOKEN or TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.critical("❌ TELEGRAM_BOT_TOKEN not set! Exiting.")
        return

    http_thread = threading.Thread(target=run_http_server)
    http_thread.daemon = True
    http_thread.start()

    logger.info("🤖 Initializing Telegram bot...")
    tg_app = Application.builder().token(TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.post_init = setup_commands

    logger.info("✨ Bot is ready! Listening for messages...")
    tg_app.run_polling()

if __name__ == "__main__":
    main()