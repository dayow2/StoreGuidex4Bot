import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Retrieve variables from Render env
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

# --- Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Store Guide! Your premier shopping and retail companion.\n\n"
        "Available commands:\n"
        "/help - See how I can assist you\n"
        "/status - Check bot connection"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I am your Store Guide. Let me know what you'd like to do! "
        "I can help you navigate inventory, track shopping items, or find local branch hours."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Store Guide is up and running smoothly on Render!")

# --- Webhook & Server Setup ---
async def main():
    if not TOKEN:
        print("Error: No TELEGRAM_TOKEN found in environment variables.")
        return

    # Build the PTB Application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))

    # Initialize application components
    await application.initialize()
    await application.start()

    # Simple health check endpoint for Render's routing
    async def home_handler(request):
        return web.Response(text="Store Guide Bot is Live and Healthy!")

    # Telegram Webhook incoming data endpoint
    async def webhook_handler(request):
        try:
            data = await request.json()
            update = Update.de_json(data, application.bot)
            await application.process_update(update)
        except Exception as e:
            print(f"Error processing update: {e}")
        return web.Response(status=200)

    # Set up the web application
    app = web.Application()
    app.router.add_get("/", home_handler)
    app.router.add_post(f"/{TOKEN}", webhook_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    # Register our webhook URL with Telegram API
    if RENDER_URL:
        webhook_target_url = f"{RENDER_URL}/{TOKEN}"
        print(f"Setting Telegram Webhook to: {webhook_target_url}")
        await application.bot.set_webhook(url=webhook_target_url)
    else:
        print("WARNING: RENDER_EXTERNAL_URL environment variable is missing!")

    print(f"Store Guide server successfully started on port {PORT}")

    # Keep the event loop running infinitely
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        # Graceful cleanup on shutdown
        await application.stop()
        await application.shutdown()
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Server stopped cleanly.")
