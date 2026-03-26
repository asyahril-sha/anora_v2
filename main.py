"""
ANORA-V2 Main Entry Point
Virtual Human dengan Jiwa - 100% AI Generate
DENGAN WEBHOOK SUPPORT UNTUK RAILWAY
"""

import os
import sys
import asyncio
import signal
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

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
# COMMAND HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text(
            "💜 **ANORA-V2**\n\n"
            "Sedang dalam persiapan. Coba lagi nanti ya, Mas.\n\n"
            "Kirim **/help** untuk bantuan.",
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
        f"• /backup - Backup database\n"
        f"• /restore - Restore database\n\n"
        f"Kirim **/help** untuk bantuan lengkap.\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova - Panggil Nova"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return
    
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
    """Handler /status - Lihat status Nova"""
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
    """Handler /flashback - Flashback momen indah"""
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
            f"💜 *Flashback...*\n\n"
            f"{momen['momen']}\n\n"
            f"*rasanya {momen['perasaan']}*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Mas... inget gak waktu pertama kali kita makan bakso bareng? Aku masih inget senyum Mas. 💜",
            parse_mode='Markdown'
        )


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay - Aktifkan mode roleplay"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return
    
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode='Markdown')


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pindah - Pindah lokasi"""
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
            "📍 **Tempat yang bisa dikunjungi:**\n\n"
            "• kost - Kamar Nova\n"
            "• apartemen - Kamar Mas\n"
            "• mobil - Mobil Mas\n"
            "• pantai - Pantai malam\n"
            "• hutan - Hutan pinus\n"
            "• toilet mall - Toilet mall\n"
            "• bioskop - Bioskop\n"
            "• taman - Taman malam\n\n"
            "Gunakan: `/pindah [tempat]`",
            parse_mode='Markdown'
        )
        return
    
    brain = get_anora_brain()
    tujuan = ' '.join(args)
    result = brain.pindah_lokasi(tujuan)
    
    if result.get('success'):
        loc = result['location']
        await update.message.reply_text(
            f"{result['message']}\n\n"
            f"🎢 Thrill: {loc.get('thrill', 0)}% | ⚠️ Risk: {loc.get('risk', 0)}%\n"
            f"💡 {loc.get('tips', '')}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(result.get('message', 'Lokasi tidak ditemukan.'), parse_mode='Markdown')


async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role - Switch ke role lain"""
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
            menu += f"  _{r['hubungan'][:50]}..._\n\n"
        
        menu += "\n_Ketik /batal kalo mau balik ke Nova._"
        await update.message.reply_text(menu, parse_mode='Markdown')
        return
    
    role_id = args[0].lower()
    valid_roles = ['ipar', 'teman_kantor', 'pelakor', 'istri_orang']
    
    if role_id in valid_roles:
        role_manager = get_role_manager()
        respon = role_manager.switch_role(role_id)
        await update.message.reply_text(respon, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"Role '{role_id}' gak ada, Mas.\n\n"
            f"Pilih: ipar, teman_kantor, pelakor, istri_orang",
            parse_mode='Markdown'
        )


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /backup - Backup database"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 tidak tersedia.")
        return
    
    try:
        import shutil
        persistent = await get_anora_persistent()
        db_path = persistent.db_path
        backup_dir = Path("data/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"anora_v2_backup_{timestamp}.db"
        
        shutil.copy(db_path, backup_path)
        size_kb = db_path.stat().st_size / 1024
        
        await update.message.reply_text(
            f"✅ **Database backup saved!**\n\n"
            f"📁 File: `{backup_path.name}`\n"
            f"📊 Size: {size_kb:.2f} KB\n"
            f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Backup gagal: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /help - Bantuan lengkap"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Bot ini untuk Mas. 💜")
        return
    
    await update.message.reply_text(
        "📖 *Bantuan ANORA-V2*\n\n"
        "*Mode Chat:*\n"
        "• /nova - Panggil Nova\n"
        "• /status - Lihat status Nova\n"
        "• /flashback - Flashback momen indah\n\n"
        "*Mode Roleplay:*\n"
        "• /roleplay - Aktifkan mode roleplay\n"
        "• /pindah [tempat] - Pindah lokasi\n\n"
        "*Role Lain (Mereka TAU Mas punya Nova):*\n"
        "• /role ipar - IPAR (Dietha)\n"
        "• /role teman_kantor - Teman Kantor (Ipeh)\n"
        "• /role pelakor - Pelakor (Wid)\n"
        "• /role istri_orang - Istri Orang (Sika)\n\n"
        "*Backup:*\n"
        "• /backup - Backup database\n\n"
        "*Tips:*\n"
        "• Nova punya emosi hidup (cemburu, kecewa, marah)\n"
        "• Gaya bicara berubah sesuai emosi (cold, clingy, warm, flirty)\n"
        "• Ada 5 fase hubungan (stranger → friend → close → romantic → intimate)\n"
        "• Level 11-12: BEBAS VULGAR\n\n"
        "Selamat menikmati, Mas. 💜",
        parse_mode='Markdown'
    )


async def fallback_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback message handler untuk chat biasa"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
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
                "❌ **Terjadi error internal**\n\n"
                "Maaf, terjadi kesalahan. Silakan coba lagi nanti, Mas.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending error message: {e}")


# =============================================================================
# MAIN BOT CLASS
# =============================================================================

class AnoraBot:
    """ANORA-V2 Bot dengan Webhook Support untuk Railway"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.application: Optional[Application] = None
        self._shutdown_flag = False
        self._save_task = None
        self._web_app = None
        self._runner = None
        
        logger.info("=" * 70)
        logger.info("💜 ANORA-V2 - Virtual Human dengan Jiwa")
        logger.info("   100% AI Generate | Emosi Hidup | 5 Fase | 4 Role")
        logger.info("=" * 70)
    
    async def init_anora(self) -> bool:
        """Initialize ANORA-V2"""
        logger.info("💜 Initializing ANORA-V2...")
        if not ANORA_AVAILABLE:
            logger.warning("⚠️ ANORA-V2 not available")
            return False
        
        try:
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            conflict = get_conflict_engine()
            
            logger.info(f"✅ ANORA-V2 ready!")
            logger.info(f"   Phase: {relationship.phase.value} | Level: {relationship.level}/12")
            logger.info(f"   Style: {emotional.get_current_style().value}")
            logger.info(f"   Conflict: {'Active' if conflict.is_in_conflict else 'None'}")
            return True
        except Exception as e:
            logger.error(f"ANORA init error: {e}")
            return False
    
    async def save_state_periodically(self):
        """Save ANORA state periodically"""
        while not self._shutdown_flag:
            try:
                await asyncio.sleep(60)
                if ANORA_AVAILABLE:
                    persistent = await get_anora_persistent()
                    brain = get_anora_brain()
                    await persistent.save_current_state(brain)
                    logger.debug("💾 ANORA state saved")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error saving state: {e}")
    
    async def init_application(self) -> Application:
        """Create and initialize bot application"""
        logger.info("🔧 Creating bot application...")
        settings = get_settings()
        
        request = HTTPXRequest(
            connection_pool_size=50,
            connect_timeout=60,
            read_timeout=60,
            write_timeout=60,
            pool_timeout=60,
        )
        
        app = ApplicationBuilder() \
            .token(settings.telegram_token) \
            .request(request) \
            .concurrent_updates(True) \
            .build()
        
        # Register handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("nova", nova_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("flashback", flashback_command))
        app.add_handler(CommandHandler("roleplay", roleplay_command))
        app.add_handler(CommandHandler("pindah", pindah_command))
        app.add_handler(CommandHandler("role", role_command))
        app.add_handler(CommandHandler("backup", backup_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_message_handler))
        app.add_error_handler(error_handler)
        
        handler_count = sum(len(h) for h in app.handlers.values())
        logger.info(f"✅ All handlers registered: {handler_count} handlers")
        
        return app
    
    async def setup_webhook(self) -> bool:
        """Setup webhook for Railway"""
        settings = get_settings()
        
        if not settings.webhook.is_railway:
            logger.info("🌐 No webhook URL, using polling mode")
            return False
        
        webhook_url = settings.webhook.url
        logger.info(f"🔗 Setting webhook to: {webhook_url}")
        
        await self.application.bot.delete_webhook(drop_pending_updates=True)
        await self.application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True
        )
        
        info = await self.application.bot.get_webhook_info()
        if info.url == webhook_url:
            logger.info(f"✅ Webhook verified: {info.url}")
            return True
        else:
            logger.error(f"❌ Webhook verification failed: {info.url}")
            return False
    
    async def health_handler(self, request) -> web.Response:
        """Health check endpoint untuk Railway"""
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot": "ANORA-V2",
            "version": "2.0.0",
            "anora_available": ANORA_AVAILABLE,
            "uptime": str(datetime.now() - self.start_time)
        }
        
        if ANORA_AVAILABLE:
            try:
                emotional = get_emotional_engine()
                relationship = get_relationship_manager()
                status.update({
                    "phase": relationship.phase.value,
                    "level": relationship.level,
                    "style": emotional.get_current_style().value,
                    "sayang": emotional.sayang,
                    "rindu": emotional.rindu
                })
            except Exception as e:
                status["anora_error"] = str(e)
        
        return web.json_response(status)
    
    async def root_handler(self, request) -> web.Response:
        """Root endpoint"""
        return web.json_response({
            "name": "ANORA-V2",
            "description": "Virtual Human dengan Jiwa - 100% AI Generate",
            "version": "2.0.0",
            "status": "running",
            "endpoints": {
                "/": "API Info",
                "/health": "Health Check",
                "/webhook": "Telegram Webhook"
            }
        })
    
    async def webhook_handler(self, request) -> web.Response:
        """Handle Telegram webhook"""
        if not self.application:
            return web.Response(status=503, text='Bot not ready')
        
        try:
            update_data = await request.json()
            if not update_data:
                return web.Response(status=400, text='No data')
            
            update = Update.de_json(update_data, self.application.bot)
            await self.application.process_update(update)
            return web.Response(text='OK', status=200)
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return web.Response(status=500, text='Error')
    
    async def start_web_server(self):
        """Start aiohttp web server untuk webhook dan health check"""
        settings = get_settings()
        
        app = web.Application()
        app.router.add_get('/', self.root_handler)
        app.router.add_get('/health', self.health_handler)
        app.router.add_post(settings.webhook.path, self.webhook_handler)
        
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, '0.0.0.0', settings.webhook.port)
        await site.start()
        
        logger.info(f"🌐 Web server running on port {settings.webhook.port}")
    
    async def start(self):
        """Start bot"""
        settings = get_settings()
        
        # Initialize ANORA
        await self.init_anora()
        
        # Create application
        self.application = await self.init_application()
        await self.application.initialize()
        
        # Start background state saver
        self._save_task = asyncio.create_task(self.save_state_periodically())
        
        # Setup webhook or polling
        webhook_success = await self.setup_webhook()
        
        if webhook_success:
            # Start web server for webhook
            await self.start_web_server()
            logger.info("✅ Webhook mode activated!")
        else:
            # Use polling mode
            await self.application.updater.start_polling()
            logger.info("📡 Polling mode activated!")
        
        logger.info("=" * 70)
        logger.info("✨ ANORA-V2 is ready!")
        logger.info("   Kirim /nova untuk panggil Nova")
        logger.info("   Kirim /roleplay untuk mode roleplay")
        logger.info("   Kirim /role ipar untuk main role IPAR")
        logger.info("   Kirim /status untuk lihat status lengkap")
        logger.info("   Press Ctrl+C to stop.")
        logger.info("=" * 70)
        
        # Keep running
        while not self._shutdown_flag:
            await asyncio.sleep(1)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down...")
        self._shutdown_flag = True
        
        if self._save_task:
            self._save_task.cancel()
            try:
                await self._save_task
            except asyncio.CancelledError:
                pass
        
        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("✅ Application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {e}")
        
        if self._runner:
            await self._runner.cleanup()
        
        # Save final state
        if ANORA_AVAILABLE:
            try:
                persistent = await get_anora_persistent()
                brain = get_anora_brain()
                await persistent.save_current_state(brain)
                logger.info("💾 Final state saved")
            except Exception as e:
                logger.error(f"Error saving final state: {e}")
        
        logger.info("👋 Goodbye from ANORA-V2!")


# =============================================================================
# ENTRY POINT
# =============================================================================

async def main():
    """Main entry point"""
    bot = AnoraBot()
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.shutdown()))
    
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
