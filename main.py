# anora_v2/main.py
"""
ANORA-V2 Main Entry Point
Virtual Human dengan Jiwa - 100% AI Generate
"""

import os
import sys
import asyncio
import signal
import logging
import time
from pathlib import Path
from datetime import datetime

from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.request import HTTPXRequest

from config import get_settings
from commands import (
    register_general_commands,
    register_role_commands,
    register_therapist_commands,
    register_pelacur_commands
)
from handlers.message import message_handler, set_anora_available
from . import __version__

# =============================================================================
# SETUP LOGGING
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)
logger = logging.getLogger("ANORA-V2")

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================
_application = None
_backup_dir = Path("data/backups")
_backup_dir.mkdir(parents=True, exist_ok=True)

# Flag untuk ANORA availability (akan di-set setelah init)
ANORA_AVAILABLE = True
set_anora_available(ANORA_AVAILABLE)


# =============================================================================
# WEBHOOK HANDLERS
# =============================================================================

async def webhook_handler(request):
    """Handle Telegram webhook"""
    global _application
    
    logger.info(f"📨 Webhook called: {request.method} {request.path}")
    
    if request.method == 'GET':
        return web.Response(
            text="This endpoint is for Telegram webhook. Use POST method.",
            status=405
        )
    
    if not _application:
        logger.error("❌ _application is None! Bot not ready")
        return web.Response(status=503, text='Bot not ready')
    
    try:
        update_data = await request.json()
        logger.info(f"📨 Received update: {update_data}")
        
        if not update_data:
            return web.Response(status=400, text='No data')
        
        update = Update.de_json(update_data, _application.bot)
        await _application.process_update(update)
        logger.info("✅ Update processed successfully")
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "bot": "ANORA-V2",
        "version": __version__,
        "anora_available": ANORA_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    })


async def root_handler(request):
    """Root endpoint"""
    return web.json_response({
        "name": "ANORA-V2",
        "version": __version__,
        "status": "running"
    })


# =============================================================================
# MAIN BOT CLASS
# =============================================================================

class AnoraBot:
    def __init__(self):
        self.start_time = time.time()
        self.application: Application = None
        self._shutdown_flag = False
        self._runner = None
    
    async def init_anora(self) -> bool:
        global ANORA_AVAILABLE
        logger.info("💜 Initializing ANORA-V2...")
        try:
            from core.emotional_engine import get_emotional_engine
            from core.relationship import get_relationship_manager
            from core.conflict_engine import get_conflict_engine
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            conflict = get_conflict_engine()
            logger.info(f"✅ ANORA-V2 ready!")
            logger.info(f"   Phase: {relationship.phase.value} | Level: {relationship.level}/12")
            logger.info(f"   Style: {emotional.get_current_style().value}")
            logger.info(f"   Conflict: {'Active' if conflict.is_in_conflict else 'None'}")
            ANORA_AVAILABLE = True
            set_anora_available(True)
            return True
        except Exception as e:
            logger.error(f"ANORA init error: {e}", exc_info=True)
            ANORA_AVAILABLE = False
            set_anora_available(False)
            return False
    
    async def init_application(self) -> Application:
        settings = get_settings()
        logger.info("🔧 Initializing Telegram application...")
        request = HTTPXRequest(connection_pool_size=50, connect_timeout=60)
        app = ApplicationBuilder().token(settings.telegram_token).request(request).build()
        
        # Register all commands
        register_general_commands(app)
        register_role_commands(app)
        register_therapist_commands(app)
        register_pelacur_commands(app)
        
        # Message handler (must be last)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        # Error handler
        async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            logger.error(f"Error: {context.error}", exc_info=True)
            try:
                if update and update.effective_message:
                    await update.effective_message.reply_text(
                        "❌ Terjadi error internal. Silakan coba lagi nanti, Mas.",
                        parse_mode='Markdown'
                    )
            except Exception:
                pass
        
        app.add_error_handler(error_handler)
        
        handler_count = sum(len(h) for h in app.handlers.values())
        logger.info(f"✅ Handlers registered: {handler_count}")
        return app
    
    async def setup_webhook(self) -> bool:
        settings = get_settings()
        railway_url = settings.webhook.railway_domain or settings.webhook.railway_static_url
        
        if not railway_url:
            logger.info("🌐 No webhook URL (Railway domain not set), using polling mode")
            return False
        
        webhook_url = f"https://{railway_url}{settings.webhook.path}"
        logger.info(f"🔗 Setting webhook to: {webhook_url}")
        
        try:
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            await self.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True
            )
            
            info = await self.application.bot.get_webhook_info()
            logger.info(f"📡 Webhook info: {info.url}")
            
            if info.url == webhook_url:
                logger.info("✅ Webhook verified!")
                return True
            else:
                logger.warning(f"⚠️ Webhook URL mismatch: set={webhook_url}, actual={info.url}")
                return False
            
        except Exception as e:
            logger.error(f"Webhook setup error: {e}", exc_info=True)
            return False
    
    async def start_web_server(self):
        settings = get_settings()
        port = int(os.environ.get("PORT", 8080))
        
        app = web.Application()
        app.router.add_get('/', root_handler)
        app.router.add_get('/health', health_handler)
        app.router.add_post(settings.webhook.path, webhook_handler)
        
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, '0.0.0.0', port)
        await site.start()
        logger.info(f"🌐 Web server running on port {port}")
        logger.info(f"   Health check: http://localhost:{port}/health")
        logger.info(f"   Webhook endpoint: POST http://localhost:{port}{settings.webhook.path}")
        if settings.webhook.railway_domain:
            logger.info(f"   Public URL: https://{settings.webhook.railway_domain}{settings.webhook.path}")
    
    async def start(self):
        """Start bot"""
        global _application
        
        logger.info("=" * 70)
        logger.info(f"🚀 ANORA-V2 v{__version__} Starting...")
        logger.info("=" * 70)
        
        # Initialize ANORA
        await self.init_anora()
        
        # Create application
        self.application = await self.init_application()
        await self.application.initialize()
        await self.application.start()
        
        # Set global application
        _application = self.application
        logger.info("✅ Application set to global variable")
        
        # Setup webhook
        webhook_success = await self.setup_webhook()
        
        # Always start web server
        await self.start_web_server()
        
        if webhook_success:
            logger.info("✅ Webhook mode activated! Bot is ready to receive messages.")
        else:
            logger.warning("⚠️ Webhook not set properly, but web server is running.")
            logger.info("📡 Check: RAILWAY_PUBLIC_DOMAIN environment variable")
        
        logger.info("=" * 70)
        logger.info("✨ ANORA-V2 is ready!")
        logger.info(f"👑 Admin ID: {get_settings().admin_id}")
        logger.info("   Kirim /nova untuk panggil Nova")
        logger.info("   Kirim /roleplay untuk mode roleplay")
        logger.info("   Kirim /role therapist untuk mode terapis")
        logger.info("   Kirim /role pelacur untuk mode pelacur")
        logger.info("   Kirim /status untuk lihat status lengkap")
        logger.info("   Kirim /pause untuk hentikan sesi sementara")
        logger.info("   Kirim /backup untuk backup database")
        logger.info("=" * 70)
        
        # Keep running
        while not self._shutdown_flag:
            await asyncio.sleep(1)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down...")
        self._shutdown_flag = True
        
        # Stop application
        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("✅ Application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {e}", exc_info=True)
        
        # Cleanup web server
        if self._runner:
            await self._runner.cleanup()
            logger.info("✅ Web server stopped")
        
        logger.info("👋 Goodbye from ANORA-V2!")


# =============================================================================
# ENTRY POINT
# =============================================================================

async def main():
    """Main entry point"""
    bot = AnoraBot()
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.shutdown()))
    
    try:
        await bot.start()
    except asyncio.CancelledError:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Main error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
