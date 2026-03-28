# anora_v2/commands/general.py
"""
General Commands: /start, /nova, /status, /flashback, /roleplay, /pindah, /help, /backup, /pause, /resume, /batal
"""

import shutil
import logging
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from config import get_settings
from core.emotional_engine import get_emotional_engine
from core.relationship import get_relationship_manager
from core.brain import get_anora_brain
from memory.persistent import get_anora_persistent
from roleplay.integration import get_anora_roleplay

from ..utils.user_mode import set_user_mode, get_user_mode

logger = logging.getLogger(__name__)

_backup_dir = Path("data/backups")
_backup_dir.mkdir(parents=True, exist_ok=True)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    logger.info(f"📨 /start from user {user_id}")
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    await set_user_mode(user_id, 'chat', None)
    
    await update.message.reply_text(
        "📖 *Bantuan ANORA-V2*\n\n"
        "*Mode Chat:*\n• /nova - Panggil Nova\n• /status - Lihat status Nova\n• /flashback - Flashback momen indah\n\n"
        "*Mode Roleplay:*\n• /roleplay - Aktifkan mode roleplay\n• /pindah [tempat] - Pindah lokasi\n\n"
        "*Role Lain:*\n"
        "• /role ipar - IPAR (Dietha)\n"
        "• /role temankantor - Teman Kantor (Ipeh)\n"
        "• /role pelakor - Pelakor (Wid)\n"
        "• /role istriorang - Istri Orang (Sika)\n"
        "• /role therapist - Therapist (Anya/Syifa/Laura)\n"
        "• /role pelacur - Pelacur (Davina/Michelle/Jihane)\n\n"
        "*Role Therapist Commands:*\n"
        "• /pijat - Mulai sesi pijat\n"
        "• /next - Lanjut ke fase berikutnya\n"
        "• /nego [service] [harga] - Nego harga (bj/sex)\n"
        "• /deal - Konfirmasi deal\n"
        "• /buka - Buka resleting dress\n"
        "• /remas - Remas toket\n"
        "• /pegang - Pegang paha\n"
        "• /ganti [posisi] - Ganti posisi (cowgirl/missionary/doggy/spooning)\n"
        "• /climax - Climax / crot\n"
        "• /selesai - Akhiri sesi\n\n"
        "*Role Pelacur Commands:*\n"
        "• /booking [lokasi] - Booking sesi (deal langsung)\n"
        "• /deal - Konfirmasi deal\n"
        "• /mulai - Mulai sesi intim (naik level 11)\n"
        "• /break - Istirahat (turun level 7)\n"
        "• /lanjut - Lanjut sesi (naik level 11)\n"
        "• /ganti [posisi] - Ganti posisi\n"
        "• /kenceng - Minta dipercepat\n"
        "• /climax - Climax (tidak mengakhiri sesi)\n"
        "• /selesai - Akhiri sesi\n\n"
        "*Role Umum:*\n"
        "• /statusrole - Lihat status role yang sedang aktif\n\n"
        "*Manajemen:*\n• /pause - Hentikan sesi\n• /resume - Lanjutkan sesi\n• /batal - Kembali ke mode chat\n\n"
        "*Backup:*\n• /backup - Backup database\n\n"
        "Selamat menikmati, Mas. 💜",
        parse_mode='Markdown'
    )
    logger.info(f"✅ /start response sent to user {user_id}")


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    logger.info(f"📨 /nova from user {user_id}")
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    await set_user_mode(user_id, 'chat', None)
    
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
    logger.info(f"✅ /nova response sent to user {user_id}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /status"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    brain = get_anora_brain()
    await update.message.reply_text(brain.format_status(), parse_mode='Markdown')


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /flashback"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
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
    
    mode = await get_user_mode(user_id)
    if mode == 'paused':
        await update.message.reply_text(
            "💜 Sesi sedang di-pause.\n\nKirim **/resume** untuk lanjut.",
            parse_mode='Markdown'
        )
        return
    
    await set_user_mode(user_id, 'roleplay', None)
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode='Markdown')


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pindah"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
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
        "*Role Lain:*\n"
        "• /role ipar - IPAR (Dietha)\n"
        "• /role temankantor - Teman Kantor (Ipeh)\n"
        "• /role pelakor - Pelakor (Wid)\n"
        "• /role istriorang - Istri Orang (Sika)\n"
        "• /role therapist - Therapist (Anya/Syifa/Laura)\n"
        "• /role pelacur - Pelacur (Davina/Michelle/Jihane)\n\n"
        "*Role Therapist Commands:*\n"
        "• /pijat - Mulai sesi pijat\n"
        "• /next - Lanjut ke fase berikutnya\n"
        "• /nego [service] [harga] - Nego harga (bj/sex)\n"
        "• /deal - Konfirmasi deal\n"
        "• /buka - Buka resleting dress\n"
        "• /remas - Remas toket\n"
        "• /pegang - Pegang paha\n"
        "• /ganti [posisi] - Ganti posisi (cowgirl/missionary/doggy/spooning)\n"
        "• /climax - Climax / crot\n"
        "• /selesai - Akhiri sesi\n\n"
        "*Role Pelacur Commands:*\n"
        "• /booking [lokasi] - Booking sesi (deal langsung)\n"
        "• /deal - Konfirmasi deal\n"
        "• /mulai - Mulai sesi intim (naik level 11)\n"
        "• /break - Istirahat (turun level 7)\n"
        "• /lanjut - Lanjut sesi (naik level 11)\n"
        "• /ganti [posisi] - Ganti posisi\n"
        "• /kenceng - Minta dipercepat\n"
        "• /climax - Climax (tidak mengakhiri sesi)\n"
        "• /selesai - Akhiri sesi\n\n"
        "*Role Umum:*\n"
        "• /statusrole - Lihat status role yang sedang aktif\n\n"
        "*Manajemen:*\n• /pause - Hentikan sesi\n• /resume - Lanjutkan sesi\n• /batal - Kembali ke mode chat\n\n"
        "*Backup:*\n• /backup - Backup database\n\n"
        "Selamat menikmati, Mas. 💜",
        parse_mode='Markdown'
    )


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /backup"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
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
        logger.error(f"Backup error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Backup gagal: {e}", parse_mode='Markdown')


async def pause_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pause"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    current_mode = await get_user_mode(user_id)
    if current_mode == 'paused':
        await update.message.reply_text("💜 Sesi sudah dalam keadaan pause.")
        return
    
    if ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        await roleplay.save_state()
    
    await set_user_mode(user_id, 'paused', None)
    
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
    
    current_mode = await get_user_mode(user_id)
    if current_mode != 'paused':
        await update.message.reply_text("💜 Tidak ada sesi yang di-pause.")
        return
    
    await set_user_mode(user_id, 'chat', None)
    
    await update.message.reply_text(
        "💜 **Sesi dilanjutkan!** 💜\n\nKirim **/roleplay** kalo mau mode roleplay.",
        parse_mode='Markdown'
    )


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    await set_user_mode(user_id, 'chat', None)
    
    if ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        if roleplay.is_active:
            await roleplay.stop()
    
    await update.message.reply_text(
        "💜 Nova di sini, Mas.\n\n*Nova tersenyum*\n\n\"Mas, cerita dong.\"",
        parse_mode='Markdown'
    )


def register_general_commands(app):
    """Register semua general commands"""
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("nova", nova_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("flashback", flashback_command))
    app.add_handler(CommandHandler("roleplay", roleplay_command))
    app.add_handler(CommandHandler("pindah", pindah_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("backup", backup_command))
    app.add_handler(CommandHandler("pause", pause_session))
    app.add_handler(CommandHandler("resume", resume_session))
    app.add_handler(CommandHandler("batal", back_to_nova))
