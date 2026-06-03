import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Retrieve token and port from environment variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8443))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL") # Provided automatically by Render

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Buy Buddy! Your shopping companion.\n\n"
        "Available commands:\n"
        "/help - See how I can assist you\n"
        "/status - Check bot connection"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tell me what you'd like to do! I can help track your shopping or look up deals.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Buy Buddy is up and running smoothly!")

async def main():
    if not TOKEN:
        print("Error: No TELEGRAM_TOKEN found in environment variables.")
        return

    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))

    # Initialize the application infrastructure
    await application.initialize()

    # Configure Webhook for Render deployment
    if RENDER_URL:
        print(f"Starting webhook on port {PORT} via {RENDER_URL}")
        
        # Start webhook server natively within the async loop
        await application.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{RENDER_URL}/{TOKEN}"
        )
        await application.start()
        
        # Keep the bot running infinitely
        while True:
            await asyncio.sleep(3600)
    else:
        # Fallback to local polling if running on your machine
        print("Starting local polling...")
        await application.updater.start_polling()
        await application.start()
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    # This block safely initializes the asyncio event loop for Python 3.14+
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
