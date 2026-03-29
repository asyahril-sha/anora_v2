"""
ANORA-V2 Main Entry Point (FIXED)
- Loads state from DB on startup
- Saves full state periodically (not only roleplay)
- Webhook server for Railway (aiohttp)
"""

import os
import sys
import asyncio
import signal
import logging
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.request import HTTPXRequest

# Import config
from config import get_settings

# =============================================================================
# SETUP LOGGING - EARLY
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
logger = logging.getLogger("ANORA-V2")

# =============================================================================
# IMPORT ANORA-V2 COMPONENTS (SAFE MODE)
# =============================================================================
ANORA_AVAILABLE = True
ROLEPLAY_AVAILABLE = True
ROLE_MANAGER_AVAILABLE = True

logger.info("Importing ANORA-V2 modules...")

# Core
try:
    from core.emotional_engine import get_emotional_engine
except Exception as e:
    print("❌ emotional_engine ERROR:", e)
    ANORA_AVAILABLE = False

try:
    from core.relationship import get_relationship_manager
except Exception as e:
    print("❌ relationship ERROR:", e)
    ANORA_AVAILABLE = False

try:
    from core.conflict_engine import get_conflict_engine
except Exception as e:
    print("❌ conflict_engine ERROR:", e)
    ANORA_AVAILABLE = False

try:
    from core.brain import get_anora_brain
except Exception as e:
    print("❌ brain ERROR:", e)
    ANORA_AVAILABLE = False

# Memory
try:
    from memory.persistent import get_anora_persistent
except Exception as e:
    print("❌ memory ERROR:", e)
    ANORA_AVAILABLE = False

# Roleplay
try:
    from roleplay.integration import get_anora_roleplay
    ROLEPLAY_AVAILABLE = True
except Exception as e:
    print("❌ roleplay ERROR:", e)
    ROLEPLAY_AVAILABLE = False

# Roles
try:
    from roles.manager import get_role_manager
    ROLE_MANAGER_AVAILABLE = True
except Exception as e:
    print("❌ role manager ERROR:", e)
    ROLE_MANAGER_AVAILABLE = False

logger.info("✅ ANORA-V2 partial load complete")

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================
_application: Optional[Application] = None
_user_modes: Dict[int, Dict] = {}

_backup_dir = Path("data/backups")
_backup_dir.mkdir(parents=True, exist_ok=True)


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, {}).get("mode", "chat")


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    _user_modes[user_id] = {"mode": mode, "active_role": active_role}
    logger.info(f"👤 User {user_id} mode set to: {mode}")


def get_active_role(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get("active_role")


# =============================================================================
# HELPERS: optional role managers
# =============================================================================
async def _get_therapist_manager(user_id: int):
    from roles.therapist_role import get_therapist_manager
    return get_therapist_manager(user_id)


async def _get_pelacur_manager(user_id: int):
    from roles.pelacur_role import get_pelacur_manager
    return get_pelacur_manager(user_id)


# =============================================================================
# COMMAND HANDLERS (minimal; keep yours if you want)
# =============================================================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()
    logger.info(f"📨 /start from user {user_id}")

    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return

    set_user_mode(user_id, "chat")

    await update.message.reply_text(
        "✅ ANORA-V2 siap.\n\n"
        "Command cepat:\n"
        "- /nova\n"
        "- /status\n"
        "- /roleplay\n"
        "- /backup\n",
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return

    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return

    set_user_mode(user_id, "chat")

    emotional = get_emotional_engine()
    relationship = get_relationship_manager()

    hour = datetime.now().hour
    style = emotional.get_current_style()

    if 5 <= hour < 11:
        greeting = "*Nova baru bangun*\n\n\"Pagi, Mas...\""
    elif 11 <= hour < 15:
        greeting = "*Nova tersenyum manis*\n\n\"Siang, Mas. Udah makan?\""
    elif 15 <= hour < 18:
        greeting = "*Nova duduk di teras*\n\n\"Sore, Mas...\""
    else:
        greeting = "*Nova duduk santai*\n\n\"Malam, Mas...\""

    await update.message.reply_text(
        f"""💜 **NOVA DI SINI, MAS** 💜

    {greeting}

    **Status singkat:**
    - Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)
    - Gaya: {style.value.upper()}
    """,
        parse_mode="Markdown",
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()
    if user_id != settings.admin_id:
        return
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return

    brain = get_anora_brain()
    await update.message.reply_text(brain.format_status(), parse_mode="Markdown")


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()
    if user_id != settings.admin_id:
        return
    if not ROLEPLAY_AVAILABLE:
        await update.message.reply_text("Roleplay belum tersedia.")
        return

    set_user_mode(user_id, "roleplay")
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode="Markdown")


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /backup"""
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        return

    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 tidak tersedia.")
        return

    try:
        persistent = await get_anora_persistent()
        db_path = persistent.db_path

        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = _backup_dir / f"anora_v2_backup_{timestamp}.db"
        shutil.copy(db_path, backup_path)

        size_kb = db_path.stat().st_size / 1024

        await update.message.reply_text(
            f"✅ Backup saved: `{backup_path.name}`
Size: {size_kb:.2f} KB",
            parse_mode="Markdown",
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Backup gagal: {e}")
            return

# =============================================================================
# MESSAGE HANDLER
# =============================================================================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()
    if user_id != settings.admin_id:
        return

    pesan = update.message.text if update.message else None
    if not pesan:
        return

    mode = get_user_mode(user_id)

    if mode == "paused":
        await update.message.reply_text(
            "💜 Sesi sedang di-pause. Kirim **/resume** untuk lanjut.",
            parse_mode="Markdown",
        )
        return

    # Roleplay mode
    if mode == "roleplay" and ROLEPLAY_AVAILABLE:
        try:
            roleplay = await get_anora_roleplay()
            respons = await roleplay.process(pesan)
            await update.message.reply_text(respons, parse_mode="Markdown")
            return
        except Exception as e:
            logger.error(f"❌ Roleplay error: {e}")
            await update.message.reply_text("*Nova bingung sebentar*", parse_mode="Markdown")
            return

    # Role mode (if you use roles manager)
    if mode == "role" and ROLE_MANAGER_AVAILABLE:
        active_role = get_active_role(user_id)
        if active_role:
            try:
                role_manager = get_role_manager()
                respons = await role_manager.chat(active_role, pesan)
                await update.message.reply_text(respons, parse_mode="Markdown")
                return
            except Exception as e:
                logger.error(f"Role chat error: {e}")
                await update.message.reply_text("Maaf, ada error.")
                return

    # Default chat mode response
    await update.message.reply_text(
        "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\"",
        parse_mode="Markdown",
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi error internal. Silakan coba lagi nanti, Mas.",
                parse_mode="Markdown",
            )
    except Exception:
        pass


# =============================================================================
# WEBHOOK & SERVER
# =============================================================================
async def webhook_handler(request: web.Request):
    global _application

    if request.method != "POST":
        return web.Response(text="Use POST", status=405)

    if not _application:
        return web.Response(status=503, text="Bot not ready")

    settings = get_settings()

    # Optional secret token verification (if you want it)
    secret = settings.webhook.secret_token
    if secret:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header_secret != secret:
            return web.Response(status=401, text="Invalid secret token")

    try:
        update_data = await request.json()
        update = Update.de_json(update_data, _application.bot)
        await _application.process_update(update)
        return web.Response(text="OK", status=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(status=500, text="Error")


async def health_handler(request: web.Request):
    return web.json_response(
        {
            "status": "healthy",
            "bot": "ANORA-V2",
            "version": "2.0.0",
            "anora_available": ANORA_AVAILABLE,
            "timestamp": datetime.now().isoformat(),
        }
    )


async def root_handler(request: web.Request):
    return web.json_response({"name": "ANORA-V2", "version": "2.0.0", "status": "running"})


# =============================================================================
# BACKGROUND LOOPS
# =============================================================================
async def save_state_loop():
    """
    FIX: Save FULL state periodically:
    - persistent.save_all_states(brain, emotional, relationship, conflict)
    - plus roleplay.save_state() if active
    """
    while True:
        await asyncio.sleep(60)
        if not ANORA_AVAILABLE:
            continue

        try:
            persistent = await get_anora_persistent()

            brain = get_anora_brain()
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            conflict = get_conflict_engine()

            # Full save
            await persistent.save_all_states(brain, emotional, relationship, conflict)

            # Roleplay extra save (only if active)
            if ROLEPLAY_AVAILABLE:
                roleplay = await get_anora_roleplay()
                if getattr(roleplay, "is_active", False):
                    await roleplay.save_state()

            logger.debug("💾 State saved (full)")
        except Exception as e:
            logger.error(f"Save state error: {e}")


async def auto_backup_loop():
    settings = get_settings()
    if not settings.features.auto_backup_enabled:
        logger.info("Auto backup disabled by settings")
        return

    while True:
        await asyncio.sleep(21600)  # 6 hours
        if not ANORA_AVAILABLE:
            continue

        try:
            persistent = await get_anora_persistent()
            db_path = persistent.db_path
            if db_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = _backup_dir / f"anora_v2_auto_{timestamp}.db"
                shutil.copy(db_path, backup_path)
                logger.info(f"💾 Auto backup saved: {backup_path.name}")
        except Exception as e:
            logger.error(f"Auto backup error: {e}")


# =============================================================================
# MAIN BOT CLASS
# =============================================================================
class AnoraBot:
    def __init__(self):
        self.start_time = time.time()
        self.application: Optional[Application] = None
        self._shutdown_flag = False
        self._save_task: Optional[asyncio.Task] = None
        self._backup_task: Optional[asyncio.Task] = None
        self._runner: Optional[web.AppRunner] = None

    async def init_anora(self) -> bool:
        """
        FIX: Load all state from DB at startup
        """
        logger.info("💜 Initializing ANORA-V2...")

        if not ANORA_AVAILABLE:
            return False

        try:
            # Ensure DB is ready
            persistent = await get_anora_persistent()

            # Create engines/singletons
            brain = get_anora_brain()
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            conflict = get_conflict_engine()

            # FIX: load all states (including tracker if you patched persistent.py)
            await persistent.load_all_states(brain, emotional, relationship, conflict)

            # Ensure wrappers are synced after load
            try:
                brain._sync_all()
            except Exception:
                pass

            logger.info("✅ ANORA-V2 ready!")
            logger.info(f" Phase: {relationship.phase.value} | Level: {relationship.level}/12")
            logger.info(f" Style: {emotional.get_current_style().value}")
            logger.info(f" Conflict: {'Active' if conflict.is_in_conflict else 'None'}")
            return True
        except Exception as e:
            logger.error(f"ANORA init error: {e}")
            return False

    async def init_application(self) -> Application:
        settings = get_settings()
        logger.info("🔧 Initializing Telegram application...")

        request = HTTPXRequest(connection_pool_size=50, connect_timeout=60)
        app = ApplicationBuilder().token(settings.telegram_token).request(request).build()

        # Register handlers (minimal set)
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("nova", nova_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("roleplay", roleplay_command))
        app.add_handler(CommandHandler("backup", backup_command))

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        app.add_error_handler(error_handler)

        handler_count = sum(len(h) for h in app.handlers.values())
        logger.info(f"✅ Handlers registered: {handler_count}")
        return app

    async def setup_webhook(self) -> bool:
        settings = get_settings()
        webhook_url = settings.webhook.url

        if not webhook_url:
            logger.warning("🌐 No webhook URL found, webhook will NOT be set.")
            return False

        logger.info(f"🔗 Setting webhook to: {webhook_url}")

        try:
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            await self.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True,
                secret_token=settings.webhook.secret_token,
            )

            info = await self.application.bot.get_webhook_info()
            logger.info(f"📡 Webhook info: {info.url}")
            return info.url == webhook_url
        except Exception as e:
            logger.error(f"Webhook setup error: {e}")
            return False

    async def start_web_server(self):
        settings = get_settings()
        port = int(os.environ.get("PORT", settings.webhook.port))

        app = web.Application()
        app.router.add_get("/", root_handler)
        app.router.add_get("/health", health_handler)
        app.router.add_post(settings.webhook.path, webhook_handler)

        self._runner = web.AppRunner(app)
        await self._runner.setup()

        site = web.TCPSite(self._runner, "0.0.0.0", port)
        await site.start()

        logger.info(f"🌐 Web server running on port {port}")
        logger.info(f" Health check: http://localhost:{port}/health")
        logger.info(f" Webhook endpoint: POST http://localhost:{port}{settings.webhook.path}")
        if settings.webhook.url:
            logger.info(f" Public webhook: {settings.webhook.url}")

    async def start(self):
        global _application

        logger.info("=" * 70)
        logger.info("🚀 ANORA-V2 Starting...")
        logger.info("=" * 70)

        await self.init_anora()

        self.application = await self.init_application()
        await self.application.initialize()
        await self.application.start()

        _application = self.application
        logger.info("✅ Application set to global variable")

        # Start background loops
        self._save_task = asyncio.create_task(save_state_loop())
        self._backup_task = asyncio.create_task(auto_backup_loop())

        # Setup webhook (if possible)
        webhook_ok = await self.setup_webhook()
        if webhook_ok:
            logger.info("✅ Webhook mode activated!")
        else:
            logger.warning("⚠️ Webhook not verified. Web server still running.")

        # Always start web server
        await self.start_web_server()

        logger.info("=" * 70)
        logger.info("✨ ANORA-V2 is ready!")
        logger.info(f"👑 Admin ID: {get_settings().admin_id}")
        logger.info("=" * 70)

        while not self._shutdown_flag:
            await asyncio.sleep(1)

    async def shutdown(self):
        logger.info("🛑 Shutting down...")
        self._shutdown_flag = True

        # Stop background loops
        for task in [self._save_task, self._backup_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Save final state
        if ANORA_AVAILABLE:
            try:
                persistent = await get_anora_persistent()
                brain = get_anora_brain()
                emotional = get_emotional_engine()
                relationship = get_relationship_manager()
                conflict = get_conflict_engine()

                await persistent.save_all_states(brain, emotional, relationship, conflict)

                if ROLEPLAY_AVAILABLE:
                    roleplay = await get_anora_roleplay()
                    if getattr(roleplay, "is_active", False):
                        await roleplay.save_state()

                logger.info("💾 Final state saved")
            except Exception as e:
                logger.error(f"Error saving final state: {e}")

        # Stop telegram app
        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("✅ Application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {e}")

        # Stop web server
        if self._runner:
            await self._runner.cleanup()
            logger.info("✅ Web server stopped")

        logger.info("👋 Goodbye from ANORA-V2!")


# =============================================================================
# ENTRY POINT
# =============================================================================
async def main():
    bot = AnoraBot()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.shutdown()))
        except NotImplementedError:
            # Some platforms don't support add_signal_handler
            pass

    try:
        await bot.start()
    except asyncio.CancelledError:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Main error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
