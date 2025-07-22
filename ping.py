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
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    def format(self, record):
        # Get color for log level
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Format timestamp
        timestamp = self.formatTime(record, '%H:%M:%S')
        
        # Create styled log message
        log_message = (
            f"{self.DIM}{timestamp}{self.RESET} "
            f"{color}{self.BOLD}[{record.levelname:^8}]{self.RESET} "
            f"{self.BOLD}{record.name}{self.RESET} → {record.getMessage()}"
        )
        
        return log_message

# Set up modern logging
def setup_logging():
    """Configure beautiful logging with colors and modern formatting"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with colored formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter())
    
    logger.addHandler(console_handler)
    
    # Reduce telegram library noise
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "YOUR_TELEGRAM_BOT_TOKEN"

# Dummy HTTP server using http.server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logger.info(f"🌐 HTTP request from {self.client_address[0]}:{self.client_address[1]}")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot Status: Online")
    
    def log_message(self, format, *args):
        # Use our modern logger instead of default stdout logging
        logger.info(f"📡 {format % args}")

def run_http_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SimpleHandler)
    logger.info("🚀 Keep-alive server launched on port 8080")
    httpd.serve_forever()

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"❌ Exception while handling update: {context.error}")

# Telegram Bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"💬 /start from @{user.username or 'N/A'} ({user.full_name}) [ID: {user.id}]")
    
    start_time = time.time()
    message = await update.message.reply_text("🛰️ Pinging...")
    end_time = time.time()
    
    ping_ms = round((end_time - start_time) * 1000, 2)
    logger.info(f"⚡ Response time: {ping_ms}ms")
    
    await message.edit_text(f"🏓 Pong! {ping_ms}ms")

async def setup_commands(app: Application):
    commands = [BotCommand("start", "Check bot ping")]
    await app.bot.set_my_commands(commands)
    logger.info("⚙️  Command menu configured: /start")

def main():
    # Start HTTP server in a thread
    http_thread = threading.Thread(target=run_http_server)
    http_thread.daemon = True
    http_thread.start()
    
    # Start Telegram bot
    logger.info("🤖 Initializing Telegram bot...")
    tg_app = Application.builder().token(TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_error_handler(error_handler)
    tg_app.post_init = setup_commands
    
    logger.info("✨ Bot is ready! Listening for messages...")
    tg_app.run_polling()

if __name__ == "__main__":
    main()