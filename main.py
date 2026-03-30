"""
ANORA-V2 Main Entry Point (CONSOLIDATED - CLEAN)
- Telegram bot + aiohttp web server (Railway webhook)
- Command handlers: start/nova/status/flashback/roleplay/pindah/role/statusrole/pause/resume/batal/backup/help
- Robust imports: bot tetap jalan walau roleplay/roles error import
- Persistent load on startup + periodic full save
- Logger jelas untuk lihat fitur aktif atau tidak
"""

import os
import sys
import asyncio
import signal
import logging
import shutil
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

from config import get_settings


# =============================================================================
# LOGGING
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
logger = logging.getLogger("ANORA-V2")


# =============================================================================
# SAFE IMPORTS (core)
# =============================================================================
ANORA_AVAILABLE = True
ROLEPLAY_AVAILABLE = False
ROLE_MANAGER_AVAILABLE = False

logger.info("Importing ANORA-V2 modules...")

try:
    from core.emotional_engine import get_emotional_engine
except Exception as e:
    logger.error(f"❌ emotional_engine import ERROR: {e}", exc_info=True)
    ANORA_AVAILABLE = False

try:
    from core.relationship import get_relationship_manager
except Exception as e:
    logger.error(f"❌ relationship import ERROR: {e}", exc_info=True)
    ANORA_AVAILABLE = False

try:
    from core.conflict_engine import get_conflict_engine
except Exception as e:
    logger.error(f"❌ conflict_engine import ERROR: {e}", exc_info=True)
    ANORA_AVAILABLE = False

try:
    from core.brain import get_anora_brain
except Exception as e:
    logger.error(f"❌ brain import ERROR: {e}", exc_info=True)
    ANORA_AVAILABLE = False

try:
    from memory.persistent import get_anora_persistent
except Exception as e:
    logger.error(f"❌ memory.persistent import ERROR: {e}", exc_info=True)
    ANORA_AVAILABLE = False

# Roleplay (optional)
try:
    from roleplay.integration import get_anora_roleplay
    ROLEPLAY_AVAILABLE = True
except Exception as e:
    logger.error(f"❌ roleplay import ERROR: {e}", exc_info=True)
    ROLEPLAY_AVAILABLE = False

# Roles (optional)
try:
    from roles.manager import get_role_manager
    ROLE_MANAGER_AVAILABLE = True
except Exception as e:
    logger.error(f"❌ roles.manager import ERROR: {e}", exc_info=True)
    ROLE_MANAGER_AVAILABLE = False

logger.info("✅ Module import finished")
logger.info(
    f"FEATURE FLAGS | ANORA_AVAILABLE={ANORA_AVAILABLE} | "
    f"ROLEPLAY_AVAILABLE={ROLEPLAY_AVAILABLE} | ROLE_MANAGER_AVAILABLE={ROLE_MANAGER_AVAILABLE}"
)


# =============================================================================
# GLOBALS
# =============================================================================
_application: Optional[Application] = None
_user_modes: Dict[int, Dict] = {}

_backup_dir = Path("data/backups")
_backup_dir.mkdir(parents=True, exist_ok=True)


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, {}).get("mode", "chat")


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    _user_modes[user_id] = {"mode": mode, "active_role": active_role}
    logger.info(f"👤 User {user_id} mode set to: {mode} | active_role={active_role}")


def get_active_role(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get("active_role")


# =============================================================================
# COMMAND HANDLERS
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
        (
            "✅ ANORA-V2 siap.\n\n"
            "Command cepat:\n"
            "- /nova\n"
            "- /status\n"
            "- /flashback\n"
            "- /roleplay\n"
            "- /pindah <tempat>\n"
            "- /role <id>\n"
            "- /statusrole\n"
            "- /pause, /resume, /batal\n"
            "- /backup\n"
            "- /help\n\n"
            "Status fitur:\n"
            f"- ANORA_AVAILABLE: {ANORA_AVAILABLE}\n"
            f"- ROLEPLAY_AVAILABLE: {ROLEPLAY_AVAILABLE}\n"
            f"- ROLE_MANAGER_AVAILABLE: {ROLE_MANAGER_AVAILABLE}\n"
        )
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    logger.info(f"📨 /nova from user {user_id}")

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

    # 1 line safe string
    await update.message.reply_text(
        f"💜 **NOVA DI SINI, MAS** 💜\n\n{greeting}\n\n**Status singkat:**\n- Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n- Gaya: {style.value.upper()}\n",
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


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        return

    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return

    brain = get_anora_brain()

    try:
        if getattr(brain, "long_term", None) and getattr(brain.long_term, "momen_penting", None):
            if brain.long_term.momen_penting:
                momen = brain.long_term.momen_penting[-1]
                await update.message.reply_text(
                    f"💜 *Flashback...*\n\n{momen.get('momen','')}\n\n*rasanya {momen.get('perasaan','')}*",
                    parse_mode="Markdown",
                )
                return
    except Exception:
        pass

    await update.message.reply_text(
        "Mas... inget gak waktu pertama kali kita makan bakso bareng? 💜",
        parse_mode="Markdown",
    )


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        return

    if not ROLEPLAY_AVAILABLE:
        await update.message.reply_text(
            "Roleplay belum tersedia. Cek log Railway untuk error import roleplay.",
            parse_mode="Markdown",
        )
        return

    mode = get_user_mode(user_id)
    if mode == "paused":
        await update.message.reply_text(
            "💜 Sesi sedang di-pause.\n\nKirim **/resume** untuk lanjut.",
            parse_mode="Markdown",
        )
        return

    set_user_mode(user_id, "roleplay")

    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode="Markdown")


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        return

    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "📍 Gunakan: `/pindah <tempat>`\nContoh: `/pindah kamar`",
            parse_mode="Markdown",
        )
        return

    brain = get_anora_brain()
    tujuan = " ".join(args)
    result = brain.pindah_lokasi(tujuan)

    if result.get("success"):
        loc = result.get("location", {})
        await update.message.reply_text(
            f"{result.get('message','')}\n\n🎢 Thrill: {loc.get('thrill', 0)}% | ⚠️ Risk: {loc.get('risk', 0)}%",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(result.get("message", "Lokasi tidak ditemukan."), parse_mode="Markdown")


async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        return

    if not ROLE_MANAGER_AVAILABLE:
        await update.message.reply_text("Role manager belum tersedia. Cek log Railway untuk error import roles.manager.")
        return

    args = context.args
    role_manager = get_role_manager()

    if not args:
        roles = role_manager.get_all_roles()
        menu = "📋 Role yang tersedia:\n\n"
        for r in roles:
            menu += f"• /role {r['id']} - {r['nama']} (Level {r['level']})
    "
        menu += "\nKetik /batal kalo mau balik ke Nova."
        await update.message.reply_text(menu)
        return

    role_id = args[0].lower()
    set_user_mode(user_id, "role", role_id)

    try:
        respon = role_manager.switch_role(role_id)
        # IMPORTANT: kirim TANPA Markdown supaya tidak kena 'Can't parse entities'
        await update.message.reply_text(respon)
    except Exception as e:
        logger.error(f"Role switch error: {e}", exc_info=True)
        await update.message.reply_text("Maaf, ada error saat switch role.")


async def statusrole_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        return

    if not ROLE_MANAGER_AVAILABLE:
        await update.message.reply_text("Role manager belum tersedia.")
        return

    mode = get_user_mode(user_id)
    if mode != "role":
        await update.message.reply_text("💜 Tidak ada role yang sedang aktif.\n\nGunakan /role <id> dulu ya, Mas.")
        return

    active_role_id = get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("Tidak ada role aktif.")
        return

    role_manager = get_role_manager()
    role = role_manager.get_role(active_role_id)

    if not role:
        await update.message.reply_text("Role tidak ditemukan.")
        return

    try:
        status = role.format_status()
    except Exception as e:
        logger.error(f"Status role error: {e}", exc_info=True)
        status = "Status role tidak tersedia."

    # Kirim tanpa Markdown untuk aman
    await update.message.reply_text(status)

async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        return

    set_user_mode(user_id, "chat")

    if ROLEPLAY_AVAILABLE:
        try:
            roleplay = await get_anora_roleplay()
            if getattr(roleplay, "is_active", False):
                await roleplay.stop()
        except Exception as e:
            logger.warning(f"Stop roleplay failed: {e}")

    await update.message.reply_text(
        "💜 Nova di sini, Mas.\n\n*Nova tersenyum*\n\n\"Mas, cerita dong.\"",
        parse_mode="Markdown",
    )


async def pause_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        return

    current_mode = get_user_mode(user_id)
    if current_mode == "paused":
        await update.message.reply_text("💜 Sesi sudah dalam keadaan pause.")
        return

    set_user_mode(user_id, "paused")

    if ROLEPLAY_AVAILABLE:
        try:
            roleplay = await get_anora_roleplay()
            await roleplay.save_state()
        except Exception as e:
            logger.warning(f"Pause save roleplay failed: {e}")

    await update.message.reply_text(
        "💜 **Sesi dihentikan sementara** 💜\n\nKirim **/resume** untuk lanjut lagi.\nKirim **/batal** untuk mulai baru.",
        parse_mode="Markdown",
    )


async def resume_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        return

    current_mode = get_user_mode(user_id)
    if current_mode != "paused":
        await update.message.reply_text("💜 Tidak ada sesi yang di-pause.")
        return

    set_user_mode(user_id, "chat")
    await update.message.reply_text(
        "💜 **Sesi dilanjutkan!** 💜\n\nKirim **/roleplay** kalo mau mode roleplay.",
        parse_mode="Markdown",
    )


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            f"✅ Backup saved: `{backup_path.name}`\nSize: {size_kb:.2f} KB",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Backup gagal: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_settings()

    if user_id != settings.admin_id:
        await update.message.reply_text("Bot ini untuk Mas. 💜")
        return

    await update.message.reply_text(
        (
            "📖 *Bantuan ANORA-V2*\n\n"
            "*Command:*\n"
            "• /nova\n"
            "• /status\n"
            "• /flashback\n"
            "• /roleplay\n"
            "• /pindah <tempat>\n"
            "• /role <id>\n"
            "• /statusrole\n"
            "• /pause /resume /batal\n"
            "• /backup\n"
        ),
        parse_mode="Markdown",
    )


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
    logger.info(f"📨 Message from {user_id} | mode={mode} | text={pesan[:80]}")

    if mode == "paused":
        await update.message.reply_text(
            "💜 Sesi sedang di-pause. Kirim **/resume** untuk lanjut.",
            parse_mode="Markdown",
        )
        return

    if mode == "roleplay":
        if not ROLEPLAY_AVAILABLE:
            await update.message.reply_text("Roleplay belum tersedia.", parse_mode="Markdown")
            return
        try:
            roleplay = await get_anora_roleplay()
            respons = await roleplay.process(pesan)
            await update.message.reply_text(respons, parse_mode="Markdown")
            return
        except Exception as e:
            logger.error(f"❌ Roleplay error: {e}", exc_info=True)
            await update.message.reply_text("*Nova bingung sebentar*", parse_mode="Markdown")
            return

    if mode == "role" and ROLE_MANAGER_AVAILABLE:
        active_role = get_active_role(user_id)
        if active_role:
            try:
                role_manager = get_role_manager()
                respons = await role_manager.chat(active_role, pesan)
                await update.message.reply_text(respons, parse_mode="Markdown")
                return
            except Exception as e:
                logger.error(f"Role chat error: {e}", exc_info=True)
                await update.message.reply_text("Maaf, ada error.")
                return

    await update.message.reply_text(
        "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\"",
        parse_mode="Markdown",
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Global error handler: {context.error}", exc_info=True)
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

    secret = settings.webhook.secret_token
    if secret:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header_secret != secret:
            return web.Response(status=401, text="Invalid secret token")

    try:
        update_data = await request.json()
        upd = Update.de_json(update_data, _application.bot)
        await _application.process_update(upd)
        return web.Response(text="OK", status=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return web.Response(status=500, text="Error")


async def health_handler(request: web.Request):
    settings = get_settings()
    return web.json_response(
        {
            "status": "healthy",
            "bot": "ANORA-V2",
            "anora_available": ANORA_AVAILABLE,
            "roleplay_available": ROLEPLAY_AVAILABLE,
            "role_manager_available": ROLE_MANAGER_AVAILABLE,
            "db_path": str(getattr(settings.database, "path", "unknown")),
            "timestamp": datetime.now().isoformat(),
        }
    )


async def root_handler(request: web.Request):
    return web.json_response({"name": "ANORA-V2", "status": "running"})


# =============================================================================
# BACKGROUND LOOPS
# =============================================================================
async def save_state_loop():
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

            await persistent.save_all_states(brain, emotional, relationship, conflict)

            # save roles
            if ROLE_MANAGER_AVAILABLE:
                try:
                    role_manager = get_role_manager()
                    await role_manager.save_all(persistent)
                    logger.info("💾 Autosave roles OK")
                except Exception as e:
                    logger.error(f"Autosave roles error: {e}", exc_info=True)

            # roleplay extra save
            if ROLEPLAY_AVAILABLE:
                roleplay = await get_anora_roleplay()
                if getattr(roleplay, "is_active", False):
                    await roleplay.save_state()

            logger.info("💾 Autosave OK (full)")
        except Exception as e:
            logger.error(f"Autosave error: {e}", exc_info=True)


async def auto_backup_loop():
    settings = get_settings()
    if not settings.features.auto_backup_enabled:
        logger.info("Auto backup disabled by settings")
        return

    while True:
        await asyncio.sleep(21600)

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
            logger.error(f"Auto backup error: {e}", exc_info=True)


# =============================================================================
# BOT CLASS
# =============================================================================
class AnoraBot:
    def __init__(self):
        self.application: Optional[Application] = None
        self._shutdown_flag = False
        self._save_task: Optional[asyncio.Task] = None
        self._backup_task: Optional[asyncio.Task] = None
        self._runner: Optional[web.AppRunner] = None

    async def init_anora(self) -> bool:
        logger.info("💜 Initializing ANORA-V2 (startup load)...")

        if not ANORA_AVAILABLE:
            logger.warning("ANORA not available; skipping init_anora")
            return False

        try:
            persistent = await get_anora_persistent()

            brain = get_anora_brain()
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            conflict = get_conflict_engine()

            await persistent.load_all_states(brain, emotional, relationship, conflict)

            # load roles state
            if ROLE_MANAGER_AVAILABLE:
                try:
                    role_manager = get_role_manager()
                    await role_manager.load_all(persistent)
                    logger.info("✅ Roles loaded from DB")
                except Exception as e:
                    logger.error(f"Role load_all error: {e}", exc_info=True)

            try:
                brain._sync_all()
            except Exception:
                pass

            logger.info("✅ Startup load completed")
            logger.info(
                f"STATE | phase={relationship.phase.value} | level={relationship.level}/12 | "
                f"style={emotional.get_current_style().value}"
            )
            return True
        except Exception as e:
            logger.error(f"init_anora error: {e}", exc_info=True)
            return False

    async def init_application(self) -> Application:
        settings = get_settings()
        logger.info("🔧 Initializing Telegram application...")

        request = HTTPXRequest(connection_pool_size=50, connect_timeout=60)
        app = ApplicationBuilder().token(settings.telegram_token).request(request).build()

        # Commands
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("nova", nova_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("flashback", flashback_command))
        app.add_handler(CommandHandler("roleplay", roleplay_command))
        app.add_handler(CommandHandler("pindah", pindah_command))
        app.add_handler(CommandHandler("role", role_command))
        app.add_handler(CommandHandler("statusrole", statusrole_command))
        app.add_handler(CommandHandler("pause", pause_session))
        app.add_handler(CommandHandler("resume", resume_session))
        app.add_handler(CommandHandler("batal", back_to_nova))
        app.add_handler(CommandHandler("backup", backup_command))
        app.add_handler(CommandHandler("help", help_command))

        # Message handler last
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
            logger.error(f"Webhook setup error: {e}", exc_info=True)
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
        logger.info("✅ Telegram Application started and set globally")

        webhook_ok = await self.setup_webhook()
        logger.info(f"WEBHOOK | ok={webhook_ok}")

        self._save_task = asyncio.create_task(save_state_loop())
        self._backup_task = asyncio.create_task(auto_backup_loop())

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

        for task in [self._save_task, self._backup_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if ANORA_AVAILABLE:
            try:
                persistent = await get_anora_persistent()
                brain = get_anora_brain()
                emotional = get_emotional_engine()
                relationship = get_relationship_manager()
                conflict = get_conflict_engine()

                await persistent.save_all_states(brain, emotional, relationship, conflict)

                if ROLE_MANAGER_AVAILABLE:
                    try:
                        role_manager = get_role_manager()
                        await role_manager.save_all(persistent)
                        logger.info("💾 Final roles saved")
                    except Exception as e:
                        logger.error(f"Final roles save error: {e}", exc_info=True)

                if ROLEPLAY_AVAILABLE:
                    roleplay = await get_anora_roleplay()
                    if getattr(roleplay, "is_active", False):
                        await roleplay.save_state()

                logger.info("💾 Final state saved")
            except Exception as e:
                logger.error(f"Final save error: {e}", exc_info=True)

        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("✅ Telegram application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {e}", exc_info=True)

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
            pass

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
        sys.exit(1)
