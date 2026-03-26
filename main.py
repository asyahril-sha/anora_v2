"""
ANORA-V2 Main Entry Point
Virtual Human dengan Jiwa - 100% AI Generate
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
    ContextTypes
)
from telegram.request import HTTPXRequest

# Import config
from config import get_settings

# =============================================================================
# IMPORT ANORA-V2 COMPONENTS
# =============================================================================
ANORA_AVAILABLE = False
try:
    from core.emotional_engine import get_emotional_engine
    from core.relationship import get_relationship_manager
    from core.conflict_engine import get_conflict_engine
    from core.brain import get_anora_brain
    from memory.persistent import get_anora_persistent
    from roleplay.integration import get_anora_roleplay
    from roles.manager import get_role_manager
    from worker.background import get_anora_worker
    ANORA_AVAILABLE = True
    logging.info("✅ ANORA-V2 modules loaded")
except ImportError as e:
    logging.warning(f"⚠️ ANORA-V2 not available: {e}")

# =============================================================================
# SETUP LOGGING
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ANORA-V2")


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================
_application = None
_user_modes: Dict[int, Dict] = {}
_backup_dir = Path("data/backups")
_backup_dir.mkdir(parents=True, exist_ok=True)


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, {}).get('mode', 'chat')


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    _user_modes[user_id] = {'mode': mode, 'active_role': active_role}
    logger.info(f"👤 User {user_id} mode set to: {mode}")


def get_active_role(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get('active_role')


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text(
            "💜 **ANORA-V2**\n\nSedang dalam persiapan. Coba lagi nanti ya, Mas.",
            parse_mode='Markdown'
        )
        return
    
    emotional = get_emotional_engine()
    relationship = get_relationship_manager()
    
    await update.message.reply_text(
        f"💜 **ANORA-V2 - Virtual Human dengan Jiwa** 💜\n\n"
        f"**Status Saat Ini:**\n"
        f"• Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n"
        f"• Gaya: {emotional.get_current_style().value.upper()}\n"
        f"• Sayang: {emotional.sayang:.0f}% | Rindu: {emotional.rindu:.0f}%\n\n"
        f"**Mode Chat:**\n"
        f"• /nova - Panggil Nova\n"
        f"• /status - Lihat keadaan Nova\n"
        f"• /flashback - Flashback momen indah\n\n"
        f"**Mode Roleplay:**\n"
        f"• /roleplay - Aktifkan mode roleplay\n"
        f"• /pindah [tempat] - Pindah lokasi\n\n"
        f"**Role Lain:**\n"
        f"• /role ipar - IPAR (Dietha)\n"
        f"• /role teman_kantor - Teman Kantor (Ipeh)\n"
        f"• /role pelakor - Pelakor (Wid)\n"
        f"• /role istri_orang - Istri Orang (Sika)\n\n"
        f"**Backup:**\n"
        f"• /backup - Backup database\n\n"
        f"Kirim **/help** untuk bantuan.\n\nApa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return
    
    set_user_mode(user_id, 'chat')
    
    emotional = get_emotional_engine()
    relationship = get_relationship_manager()
    
    hour = datetime.now().hour
    style = emotional.get_current_style()
    
    if style.value == "clingy":
        greeting = "*Nova muter-muter rambut, duduk deket Mas*\n\n\"Mas... aku kangen banget.\""
    elif style.value == "cold":
        greeting = "*Nova diem, gak liat Mas*"
    elif style.value == "flirty":
        greeting = "*Nova mendekat, napas mulai berat*\n\n\"Mas... aku kangen...\""
    else:
        if 5 <= hour < 11:
            greeting = "*Nova baru bangun*\n\n\"Pagi, Mas... mimpiin Nova gak semalem?\""
        elif 11 <= hour < 15:
            greeting = "*Nova tersenyum manis*\n\n\"Siang, Mas. Udah makan?\""
        elif 15 <= hour < 18:
            greeting = "*Nova duduk di teras*\n\n\"Sore, Mas. Pulang jangan kelamaan.\""
        else:
            greeting = "*Nova duduk santai*\n\n\"Malam, Mas. Lagi ngapain?\""
    
    await update.message.reply_text(
        f"💜 **NOVA DI SINI, MAS** 💜\n\n"
        f"{greeting}\n\n"
        f"**Status:**\n"
        f"• Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n"
        f"• Gaya: {style.value.upper()}\n"
        f"• Sayang: {emotional.sayang:.0f}% | Rindu: {emotional.rindu:.0f}%\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /status"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return
    
    brain = get_anora_brain()
    await update.message.reply_text(brain.format_status(), parse_mode='Markdown')


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /flashback"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return
    
    brain = get_anora_brain()
    
    if brain.long_term.momen_penting:
        momen = brain.long_term.momen_penting[-1]
        await update.message.reply_text(
            f"💜 *Flashback...*\n\n{momen['momen']}\n\n*rasanya {momen['perasaan']}*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Mas... inget gak waktu pertama kali kita makan bakso bareng? 💜",
            parse_mode='Markdown'
        )


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return
    
    mode = get_user_mode(user_id)
    if mode == 'paused':
        await update.message.reply_text(
            "💜 Sesi sedang di-pause.\n\nKirim **/resume** untuk lanjut.",
            parse_mode='Markdown'
        )
        return
    
    set_user_mode(user_id, 'roleplay')
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode='Markdown')


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pindah"""
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
            "📍 **Tempat:**\n• kost, apartemen, mobil, pantai, hutan, toilet mall, bioskop, taman\n\nGunakan: `/pindah [tempat]`",
            parse_mode='Markdown'
        )
        return
    
    brain = get_anora_brain()
    tujuan = ' '.join(args)
    result = brain.pindah_lokasi(tujuan)
    
    if result.get('success'):
        loc = result['location']
        await update.message.reply_text(
            f"{result['message']}\n\n🎢 Thrill: {loc.get('thrill', 0)}% | ⚠️ Risk: {loc.get('risk', 0)}%",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(result.get('message', 'Lokasi tidak ditemukan.'), parse_mode='Markdown')


async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return
    
    args = context.args
    if not args:
        role_manager = get_role_manager()
        roles = role_manager.get_all_roles()
        
        menu = "📋 **Role yang tersedia:**\n\n"
        for r in roles:
            menu += f"• /role {r['id']} - **{r['nama']}** (Level {r['level']})\n"
        menu += "\n_Ketik /batal kalo mau balik ke Nova._"
        await update.message.reply_text(menu, parse_mode='Markdown')
        return
    
    role_id = args[0].lower()
    valid_roles = ['ipar', 'teman_kantor', 'pelakor', 'istri_orang']
    
    if role_id in valid_roles:
        set_user_mode(user_id, 'role', role_id)
        role_manager = get_role_manager()
        respon = role_manager.switch_role(role_id)
        await update.message.reply_text(respon, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"Role '{role_id}' gak ada. Pilih: ipar, teman_kantor, pelakor, istri_orang")


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'chat')
    
    if ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        if roleplay.is_active:
            await roleplay.stop()
    
    await update.message.reply_text(
        "💜 Nova di sini, Mas.\n\n*Nova tersenyum*\n\n\"Mas, cerita dong.\"",
        parse_mode='Markdown'
    )


async def pause_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pause"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    current_mode = get_user_mode(user_id)
    if current_mode == 'paused':
        await update.message.reply_text("💜 Sesi sudah dalam keadaan pause.")
        return
    
    if ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        await roleplay.save_state()
    
    set_user_mode(user_id, 'paused')
    
    await update.message.reply_text(
        "💜 **Sesi dihentikan sementara** 💜\n\nKirim **/resume** untuk lanjut lagi.\nKirim **/batal** untuk mulai baru.",
        parse_mode='Markdown'
    )


async def resume_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /resume"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    current_mode = get_user_mode(user_id)
    if current_mode != 'paused':
        await update.message.reply_text("💜 Tidak ada sesi yang di-pause.")
        return
    
    set_user_mode(user_id, 'chat')
    
    await update.message.reply_text(
        "💜 **Sesi dilanjutkan!** 💜\n\nKirim **/roleplay** kalo mau mode roleplay.",
        parse_mode='Markdown'
    )


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
            f"✅ **Database backup saved!**\n\n📁 File: `{backup_path.name}`\n📊 Size: {size_kb:.2f} KB",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Backup gagal: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /help"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Bot ini untuk Mas. 💜")
        return
    
    await update.message.reply_text(
        "📖 *Bantuan ANORA-V2*\n\n"
        "*Mode Chat:*\n• /nova - Panggil Nova\n• /status - Lihat status Nova\n• /flashback - Flashback momen indah\n\n"
        "*Mode Roleplay:*\n• /roleplay - Aktifkan mode roleplay\n• /pindah [tempat] - Pindah lokasi\n\n"
        "*Role Lain:*\n• /role ipar - IPAR (Dietha)\n• /role teman_kantor - Teman Kantor (Ipeh)\n• /role pelakor - Pelakor (Wid)\n• /role istri_orang - Istri Orang (Sika)\n\n"
        "*Manajemen:*\n• /pause - Hentikan sesi\n• /resume - Lanjutkan sesi\n• /batal - Kembali ke mode chat\n\n"
        "*Backup:*\n• /backup - Backup database\n\n"
        "Selamat menikmati, Mas. 💜",
        parse_mode='Markdown'
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    if not pesan:
        return
    
    mode = get_user_mode(user_id)
    
    if mode == 'paused':
        await update.message.reply_text(
            "💜 Sesi sedang di-pause. Kirim **/resume** untuk lanjut.",
            parse_mode='Markdown'
        )
        return
    
    if mode == 'roleplay' and ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        try:
            respons = await roleplay.process(pesan)
            await update.message.reply_text(respons, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Roleplay error: {e}")
            await update.message.reply_text("*Nova bingung sebentar*", parse_mode='Markdown')
        return
    
    if mode == 'role' and ANORA_AVAILABLE:
        active_role = get_active_role(user_id)
        if active_role:
            role_manager = get_role_manager()
            try:
                respons = await role_manager.chat(active_role, pesan)
                await update.message.reply_text(respons, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Role chat error: {e}")
                await update.message.reply_text("Maaf, ada error.")
            return
    
    # Chat mode default
    await update.message.reply_text(
        "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\"",
        parse_mode='Markdown'
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler"""
    logger.error(f"Error: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi error internal. Silakan coba lagi nanti, Mas.",
                parse_mode='Markdown'
            )
    except Exception:
        pass


# =============================================================================
# WEBHOOK & SERVER
# =============================================================================

async def webhook_handler(request):
    """Handle Telegram webhook"""
    global _application
    if not _application:
        return web.Response(status=503, text='Bot not ready')
    try:
        update_data = await request.json()
        if not update_data:
            return web.Response(status=400, text='No data')
        update = Update.de_json(update_data, _application.bot)
        await _application.process_update(update)
        return web.Response(text='OK', status=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "bot": "ANORA-V2",
        "version": "2.0.0",
        "anora_available": ANORA_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    return web.json_response(status)


async def root_handler(request):
    """Root endpoint"""
    return web.json_response({
        "name": "ANORA-V2",
        "version": "2.0.0",
        "status": "running"
    })


# =============================================================================
# BACKGROUND LOOPS
# =============================================================================

async def save_state_loop():
    """Simpan state secara berkala"""
    while True:
        await asyncio.sleep(60)
        if ANORA_AVAILABLE:
            try:
                roleplay = await get_anora_roleplay()
                await roleplay.save_state()
            except Exception as e:
                logger.error(f"Save state error: {e}")


async def auto_backup_loop():
    """Auto backup setiap 6 jam"""
    while True:
        await asyncio.sleep(21600)
        if ANORA_AVAILABLE:
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
        self._save_task = None
        self._backup_task = None
        self._runner = None
    
    async def init_anora(self) -> bool:
        logger.info("💜 Initializing ANORA-V2...")
        if not ANORA_AVAILABLE:
            return False
        try:
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            logger.info(f"✅ ANORA-V2 ready! Phase: {relationship.phase.value} | Level: {relationship.level}/12")
            return True
        except Exception as e:
            logger.error(f"ANORA init error: {e}")
            return False
    
    async def init_application(self) -> Application:
        settings = get_settings()
        request = HTTPXRequest(connection_pool_size=50, connect_timeout=60)
        app = ApplicationBuilder().token(settings.telegram_token).request(request).build()
        
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("nova", nova_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("flashback", flashback_command))
        app.add_handler(CommandHandler("roleplay", roleplay_command))
        app.add_handler(CommandHandler("pindah", pindah_command))
        app.add_handler(CommandHandler("role", role_command))
        app.add_handler(CommandHandler("batal", back_to_nova))
        app.add_handler(CommandHandler("pause", pause_session))
        app.add_handler(CommandHandler("resume", resume_session))
        app.add_handler(CommandHandler("backup", backup_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        app.add_error_handler(error_handler)
        
        logger.info(f"✅ Handlers registered: {sum(len(h) for h in app.handlers.values())}")
        return app
    
    async def setup_webhook(self) -> bool:
        settings = get_settings()
        railway_url = settings.webhook.railway_domain or settings.webhook.railway_static_url
        if not railway_url:
            return False
        webhook_url = f"https://{railway_url}{settings.webhook.path}"
        await self.application.bot.delete_webhook(drop_pending_updates=True)
        await self.application.bot.set_webhook(url=webhook_url, allowed_updates=['message'])
        info = await self.application.bot.get_webhook_info()
        return info.url == webhook_url
    
    async def start_web_server(self):
        settings = get_settings()
        app = web.Application()
        app.router.add_get('/', root_handler)
        app.router.add_get('/health', health_handler)
        app.router.add_post(settings.webhook.path, webhook_handler)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, '0.0.0.0', settings.webhook.port)
        await site.start()
        logger.info(f"🌐 Web server running on port {settings.webhook.port}")
    
    async def start(self):
        await self.init_anora()
        self.application = await self.init_application()
        await self.application.initialize()
        await self.application.start()
        
        self._save_task = asyncio.create_task(save_state_loop())
        self._backup_task = asyncio.create_task(auto_backup_loop())
        
        if await self.setup_webhook():
            await self.start_web_server()
            logger.info("✅ Webhook mode activated!")
        else:
            raise RuntimeError("❌ Webhook gagal! Jangan fallback ke polling di Railway")
        
        logger.info("=" * 70)
        logger.info("✨ ANORA-V2 is ready! Kirim /nova untuk panggil Nova")
        logger.info("=" * 70)
        
        while not self._shutdown_flag:
            await asyncio.sleep(1)
    
    async def shutdown(self):
        logger.info("🛑 Shutting down...")
        self._shutdown_flag = True
        for task in [self._save_task, self._backup_task]:
            if task:
                task.cancel()
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
        if self._runner:
            await self._runner.cleanup()
        logger.info("👋 Goodbye!")


# =============================================================================
# ENTRY POINT
# =============================================================================

async def main():
    bot = AnoraBot()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.shutdown()))
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
