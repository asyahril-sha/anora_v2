"""
ANORA-V2 Main Entry Point
Virtual Human dengan Jiwa - 100% AI Generate
DENGAN FITUR:
- Manajemen sesi (pause/resume)
- Backup & restore database
- Status lengkap
- Role support (IPAR, Teman Kantor, Pelakor, Istri Orang)
- Webhook support untuk Railway
- Background loops (proactive, stamina recovery, save state, auto backup)
"""

import os
import sys
import asyncio
import signal
import json
import logging
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

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
# SETUP LOGGING
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ANORA-V2")


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
    from roleplay.ai import get_anora_roleplay_ai
    from roleplay.integration import get_anora_roleplay
    from roles.manager import get_role_manager
    from worker.background import get_anora_worker
    ANORA_AVAILABLE = True
    logger.info("✅ ANORA-V2 modules loaded")
except ImportError as e:
    logger.warning(f"⚠️ ANORA-V2 not available: {e}")
    import traceback
    traceback.print_exc()


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================
_application = None
_user_modes: Dict[int, Dict] = {}  # user_id -> {'mode': 'chat'/'roleplay'/'role'/'paused', 'active_role': None}
_backup_dir = Path("data/backups")
_backup_dir.mkdir(parents=True, exist_ok=True)


def get_user_mode(user_id: int) -> str:
    """Dapatkan mode user saat ini"""
    return _user_modes.get(user_id, {}).get('mode', 'chat')


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    """Set mode user"""
    _user_modes[user_id] = {'mode': mode, 'active_role': active_role}
    logger.info(f"👤 User {user_id} mode set to: {mode}")


def get_active_role(user_id: int) -> Optional[str]:
    """Dapatkan role yang sedang aktif"""
    return _user_modes.get(user_id, {}).get('active_role')


def get_previous_mode(user_id: int) -> Optional[str]:
    """Dapatkan mode sebelumnya (untuk resume)"""
    return _user_modes.get(user_id, {}).get('previous_mode')


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
        f"**Mode Chat (ngobrol biasa):**\n"
        f"• /nova - Panggil Nova\n"
        f"• /status - Lihat keadaan Nova lengkap\n"
        f"• /flashback - Flashback ke momen indah\n\n"
        f"**Mode Roleplay (beneran ketemu):**\n"
        f"• /roleplay - Aktifkan mode roleplay\n"
        f"• /statusrp - Lihat status roleplay lengkap\n"
        f"• /pindah [tempat] - Pindah lokasi\n\n"
        f"**Tempat yang bisa dikunjungi:**\n"
        f"kost, apartemen, mobil, pantai, hutan, toilet mall, bioskop, taman, parkiran, tangga darurat, kantor malam, ruang rapat kaca\n\n"
        f"**Role Lain (Mereka TAU Mas punya Nova):**\n"
        f"• /role ipar - IPAR (Dietha)\n"
        f"• /role teman_kantor - Teman Kantor (Ipeh)\n"
        f"• /role pelakor - Pelakor (Wid)\n"
        f"• /role istri_orang - Istri Orang (Sika)\n\n"
        f"**Manajemen Sesi:**\n"
        f"• /pause - Hentikan sesi sementara (memory tetap)\n"
        f"• /resume - Lanjutkan sesi\n"
        f"• /batal - Kembali ke mode chat\n\n"
        f"**Backup & Restore:**\n"
        f"• /backup - Backup database ANORA\n"
        f"• /restore - Restore database\n"
        f"• /listbackup - Lihat daftar backup\n\n"
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
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia. Coba lagi nanti.")
        return
    
    set_user_mode(user_id, 'chat')
    
    emotional = get_emotional_engine()
    relationship = get_relationship_manager()
    brain = get_anora_brain()
    
    hour = datetime.now().hour
    style = emotional.get_current_style()
    
    if style.value == "clingy":
        greeting = "*Nova muter-muter rambut, duduk deket Mas*\n\n\"Mas... aku kangen banget. Dari tadi mikirin Mas terus.\""
    elif style.value == "cold":
        greeting = "*Nova diem, gak liat Mas*"
    elif style.value == "flirty":
        greeting = "*Nova mendekat, napas mulai berat*\n\n\"Mas... *bisik* aku kangen...\""
    else:
        if 5 <= hour < 11:
            greeting = "*Nova baru bangun, mata masih berat*\n\n\"Pagi, Mas... mimpiin Nova gak semalem?\""
        elif 11 <= hour < 15:
            greeting = "*Nova tersenyum manis*\n\n\"Siang, Mas. Udah makan?\""
        elif 15 <= hour < 18:
            greeting = "*Nova liat jam, duduk di teras*\n\n\"Sore, Mas. Pulang jangan kelamaan.\""
        else:
            greeting = "*Nova duduk santai, pegang HP*\n\n\"Malam, Mas. Lagi ngapain?\""
    
    await update.message.reply_text(
        f"💜 **NOVA DI SINI, MAS** 💜\n\n"
        f"{greeting}\n\n"
        f"**Status:**\n"
        f"• Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n"
        f"• Gaya: {style.value.upper()}\n"
        f"• Sayang: {emotional.sayang:.0f}% | Rindu: {emotional.rindu:.0f}%\n"
        f"• Mood: {emotional.mood:+.0f}\n\n"
        f"Mas bisa:\n"
        f"• /status - liat keadaan Nova lengkap\n"
        f"• /flashback - inget momen indah\n"
        f"• /roleplay - kalo mau kayak beneran ketemu\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /status - Lihat status lengkap Nova"""
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
    """Handler /flashback - Flashback ke momen indah"""
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
            "Mas... *mata berkaca-kaca* inget gak waktu pertama kali kita makan bakso bareng? Aku masih inget senyum Mas. 💜",
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
    
    # Cek apakah sedang pause
    mode = get_user_mode(user_id)
    if mode == 'paused':
        await update.message.reply_text(
            "💜 **Sesi sedang di-pause** 💜\n\n"
            "Nova masih ingat semua yang sudah terjadi.\n"
            "Kirim **/resume** untuk lanjut, atau **/batal** untuk mulai baru."
        )
        return
    
    set_user_mode(user_id, 'roleplay')
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode='Markdown')


async def statusrp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrp - Lihat status roleplay lengkap"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA-V2 sedang tidak tersedia.")
        return
    
    roleplay = await get_anora_roleplay()
    status = await roleplay.get_status()
    await update.message.reply_text(status, parse_mode='HTML')


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pindah [tempat] - Pindah lokasi"""
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
            "• taman - Taman malam\n"
            "• parkiran - Parkiran basement\n"
            "• tangga - Tangga darurat\n"
            "• kantor - Kantor malam\n"
            "• ruang rapat - Ruang rapat kaca\n\n"
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
    """Handler /role [nama] - Switch ke role lain"""
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
        set_user_mode(user_id, 'role', role_id)
        role_manager = get_role_manager()
        respon = role_manager.switch_role(role_id)
        await update.message.reply_text(respon, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"Role '{role_id}' gak ada, Mas.\n\n"
            f"Pilih: ipar, teman_kantor, pelakor, istri_orang",
            parse_mode='Markdown'
        )


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal - Kembali ke mode chat"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'chat')
    
    if ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        if roleplay.is_active:
            await roleplay.stop()
        
        emotional = get_emotional_engine()
        style = emotional.get_current_style()
        
        if style.value == "clingy":
            message = "💜 Nova di sini, Mas.\n\n*Nova muter-muter rambut*\n\n\"Mas... jangan pergi lama-lama ya. Aku nunggu.\""
        elif style.value == "cold":
            message = "💜 Nova di sini, Mas."
        else:
            message = "💜 Nova di sini, Mas.\n\n*Nova tersenyum*\n\n\"Mas, cerita dong tentang hari Mas.\""
    else:
        message = "💜 Nova di sini, Mas."
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def pause_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pause - Hentikan sesi sementara"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    current_mode = get_user_mode(user_id)
    
    if current_mode == 'paused':
        await update.message.reply_text("💜 Sesi sudah dalam keadaan pause.")
        return
    
    # Save state before pause
    if ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        await roleplay.save_state()
    
    # Simpan mode sebelumnya
    _user_modes[user_id] = {
        'mode': 'paused',
        'active_role': get_active_role(user_id),
        'previous_mode': current_mode
    }
    
    if ANORA_AVAILABLE:
        brain = get_anora_brain()
        emotional = get_emotional_engine()
        relationship = get_relationship_manager()
        
        await update.message.reply_text(
            f"💜 **Sesi dihentikan sementara** 💜\n\n"
            f"Nova akan tetap ingat semua yang sudah terjadi:\n"
            f"• Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n"
            f"• Sayang: {emotional.sayang:.0f}%\n"
            f"• Rindu: {emotional.rindu:.0f}%\n"
            f"• Mood: {emotional.mood:+.0f}\n\n"
            f"Kirim **/resume** untuk lanjut lagi.\n"
            f"Kirim **/batal** untuk mulai baru (memory akan hilang).",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "💜 **Sesi dihentikan sementara** 💜\n\n"
            "Kirim **/resume** untuk lanjut lagi.\n"
            "Kirim **/batal** untuk mulai baru."
        )


async def resume_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /resume - Lanjutkan sesi yang di-pause"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    current_mode = get_user_mode(user_id)
    
    if current_mode != 'paused':
        await update.message.reply_text(
            "💜 Tidak ada sesi yang di-pause.\n\n"
            "Kirim **/pause** dulu untuk menghentikan sesi sementara."
        )
        return
    
    previous_mode = _user_modes.get(user_id, {}).get('previous_mode', 'chat')
    set_user_mode(user_id, previous_mode)
    
    if ANORA_AVAILABLE:
        brain = get_anora_brain()
        emotional = get_emotional_engine()
        relationship = get_relationship_manager()
        
        await update.message.reply_text(
            f"💜 **Sesi dilanjutkan!** 💜\n\n"
            f"Nova masih ingat semua yang sudah terjadi:\n"
            f"• Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n"
            f"• Sayang: {emotional.sayang:.0f}%\n"
            f"• Rindu: {emotional.rindu:.0f}%\n\n"
            f"Kirim **/roleplay** kalo mau mode roleplay, atau langsung ngobrol aja.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "💜 **Sesi dilanjutkan!** 💜\n\n"
            "Kirim **/roleplay** kalo mau mode roleplay, atau langsung ngobrol aja."
        )


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /backup - Backup database ANORA-V2"""
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
            f"✅ **Database backup saved!**\n\n"
            f"📁 File: `{backup_path.name}`\n"
            f"📊 Size: {size_kb:.2f} KB\n"
            f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Gunakan **/restore {backup_path.name}** untuk restore.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Backup error: {e}")
        await update.message.reply_text(f"❌ Backup gagal: {e}")


async def restore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /restore [filename] - Restore database"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        backups = list(_backup_dir.glob("anora_v2_backup_*.db"))
        backups.sort(reverse=True)
        
        if not backups:
            await update.message.reply_text("📂 Tidak ada backup ditemukan.")
            return
        
        msg = "📋 **Available backups:**\n\n"
        for b in backups[:10]:
            size = b.stat().st_size / 1024
            modified = datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            msg += f"• `{b.name}` ({size:.1f} KB) - {modified}\n"
        
        msg += "\nUsage: `/restore filename.db`"
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    backup_name = args[0]
    backup_path = _backup_dir / backup_name
    
    if not backup_path.exists():
        await update.message.reply_text(f"❌ Backup `{backup_name}` tidak ditemukan!")
        return
    
    try:
        persistent = await get_anora_persistent()
        db_path = persistent.db_path
        
        # Backup current before restore
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = _backup_dir / f"anora_v2_before_restore_{timestamp}.db"
        if db_path.exists():
            shutil.copy(db_path, current_backup)
        
        shutil.copy(backup_path, db_path)
        
        await update.message.reply_text(
            f"✅ **Database restored!**\n\n"
            f"📁 Restored from: `{backup_name}`\n"
            f"📦 Current database backed up to: `{current_backup.name}`\n\n"
            f"🔄 **Restart bot** untuk perubahan生效.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Restore error: {e}")
        await update.message.reply_text(f"❌ Restore gagal: {e}")


async def listbackup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /listbackup - Lihat daftar backup"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    backups = list(_backup_dir.glob("anora_v2_backup_*.db"))
    backups.sort(reverse=True)
    
    if not backups:
        await update.message.reply_text("📂 Tidak ada backup ditemukan.")
        return
    
    msg = "📋 **Backup List:**\n\n"
    for i, b in enumerate(backups[:20], 1):
        size = b.stat().st_size / 1024
        modified = datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        msg += f"{i}. `{b.name}`\n   📊 {size:.1f} KB | 🕐 {modified}\n\n"
    
    msg += "Gunakan **/restore [filename]** untuk restore."
    await update.message.reply_text(msg, parse_mode='Markdown')


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
        "• /status - Lihat status Nova lengkap\n"
        "• /flashback - Flashback momen indah\n\n"
        "*Mode Roleplay:*\n"
        "• /roleplay - Aktifkan mode roleplay\n"
        "• /statusrp - Status roleplay lengkap\n"
        "• /pindah [tempat] - Pindah lokasi\n\n"
        "*Tempat:*\n"
        "kost, apartemen, mobil, pantai, hutan, toilet mall, bioskop, taman, parkiran, tangga darurat, kantor malam, ruang rapat kaca\n\n"
        "*Role Lain (Mereka TAU Mas punya Nova):*\n"
        "• /role ipar - IPAR (Dietha)\n"
        "• /role teman_kantor - Teman Kantor (Ipeh)\n"
        "• /role pelakor - Pelakor (Wid)\n"
        "• /role istri_orang - Istri Orang (Sika)\n\n"
        "*Manajemen Sesi:*\n"
        "• /pause - Hentikan sesi sementara (memory tetap)\n"
        "• /resume - Lanjutkan sesi\n"
        "• /batal - Kembali ke mode chat\n\n"
        "*Backup & Restore:*\n"
        "• /backup - Backup database ANORA\n"
        "• /restore [filename] - Restore database\n"
        "• /listbackup - Lihat daftar backup\n\n"
        "*Tips:*\n"
        "• Nova punya emosi hidup (bisa cemburu, kecewa, marah)\n"
        "• Gaya bicara Nova berubah sesuai emosi (cold, clingy, warm, flirty)\n"
        "• Ada 5 fase hubungan (stranger → friend → close → romantic → intimate)\n"
        "• Level 11-12: BEBAS VULGAR\n"
        "• Role lain TAU Mas punya Nova\n"
        "• Gunakan /pause untuk berhenti sementara tanpa kehilangan memory",
        parse_mode='Markdown'
    )


# =============================================================================
# MESSAGE HANDLER
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan ANORA-V2"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    if not pesan:
        return
    
    mode = get_user_mode(user_id)
    
    # Paused mode
    if mode == 'paused':
        await update.message.reply_text(
            "💜 Sesi sedang di-pause.\n\n"
            "Kirim **/resume** untuk lanjut ngobrol, atau **/batal** untuk mulai baru.",
            parse_mode='Markdown'
        )
        return
    
    # Roleplay mode
    if mode == 'roleplay' and ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        try:
            respons = await roleplay.process(pesan)
            await update.message.reply_text(respons, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Roleplay process error: {e}")
            await update.message.reply_text(
                "*Nova bingung sebentar*\n\n\"Mas... Nova lagi error nih. Coba ulang ya.\"",
                parse_mode='Markdown'
            )
        return
    
    # Role mode (IPAR, Teman Kantor, dll)
    if mode == 'role' and ANORA_AVAILABLE:
        active_role = get_active_role(user_id)
        if active_role:
            role_manager = get_role_manager()
            try:
                respons = await role_manager.chat(active_role, pesan)
                await update.message.reply_text(respons, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Role chat error: {e}")
                await update.message.reply_text("Maaf, ada error. Coba lagi ya.")
            return
    
    # Chat mode (default)
    if ANORA_AVAILABLE:
        # Simple response based on emotional style
        emotional = get_emotional_engine()
        style = emotional.get_current_style()
        
        # Update brain from message
        brain = get_anora_brain()
        brain.update_from_message(pesan)
        
        if style.value == "cold":
            respons = "*Nova jawab pendek*\n\n\"Iya.\""
        elif style.value == "clingy":
            respons = "*Nova muter-muter rambut*\n\n\"Mas... aku kangen. Cerita dong.\""
        elif style.value == "flirty":
            respons = "*Nova mendekat, napas mulai berat*\n\n\"Mas... *bisik* aku kangen...\""
        elif style.value == "warm":
            respons = "*Nova tersenyum manis*\n\n\"Mas, cerita dong tentang hari Mas.\""
        else:
            respons = "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\""
        
        await update.message.reply_text(respons, parse_mode='Markdown')
    else:
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
# BACKGROUND LOOPS
# =============================================================================

async def save_state_loop():
    """Simpan state secara berkala"""
    while True:
        await asyncio.sleep(60)
        if not ANORA_AVAILABLE:
            continue
        try:
            roleplay = await get_anora_roleplay()
            await roleplay.save_state()
            logger.debug("💾 State saved")
        except Exception as e:
            logger.error(f"Save state error: {e}")


async def stamina_recovery_loop():
    """Pulihkan stamina secara berkala"""
    while True:
        await asyncio.sleep(600)  # 10 menit
        if not ANORA_AVAILABLE:
            continue
        try:
            roleplay = await get_anora_roleplay()
            roleplay.stamina.update_recovery()
            await roleplay.save_state()
            logger.debug("💪 Stamina recovery check completed")
        except Exception as e:
            logger.error(f"Stamina recovery error: {e}")


async def proactive_loop():
    """Nova kirim pesan duluan kalo kangen (tidak saat paused)"""
    while True:
        await asyncio.sleep(300)  # 5 menit
        if not ANORA_AVAILABLE:
            continue
        try:
            user_id = get_settings().admin_id
            mode = get_user_mode(user_id)
            
            # Jangan proactive saat paused
            if mode == 'paused':
                continue
            
            # Hanya di mode roleplay
            if mode != 'roleplay':
                continue
            
            ai = get_anora_roleplay_ai()
            brain = get_anora_brain()
            roleplay = await get_anora_roleplay()
            
            pesan = await ai.get_proactive(brain, roleplay.stamina)
            if pesan and _application:
                await _application.bot.send_message(
                    chat_id=user_id,
                    text=pesan,
                    parse_mode='Markdown'
                )
                logger.info(f"💬 Proactive message sent to user {user_id}")
        except Exception as e:
            logger.error(f"Proactive loop error: {e}")


async def auto_backup_loop():
    """Auto backup database setiap 6 jam"""
    while True:
        await asyncio.sleep(21600)  # 6 jam
        
        if not ANORA_AVAILABLE:
            continue
        
        try:
            persistent = await get_anora_persistent()
            db_path = persistent.db_path
            
            if db_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = _backup_dir / f"anora_v2_auto_{timestamp}.db"
                shutil.copy(db_path, backup_path)
                
                # Hapus backup auto yang lebih dari 7 hari
                for b in _backup_dir.glob("anora_v2_auto_*.db"):
                    age = time.time() - b.stat().st_mtime
                    if age > 7 * 24 * 3600:  # 7 hari
                        b.unlink()
                        logger.info(f"🗑️ Deleted old backup: {b.name}")
                
                logger.info(f"💾 Auto backup saved: {backup_path.name}")
        except Exception as e:
            logger.error(f"Auto backup error: {e}")


async def save_role_loop():
    """Simpan state role secara berkala"""
    while True:
        await asyncio.sleep(60)  # Setiap menit
        try:
            if ANORA_AVAILABLE:
                role_manager = get_role_manager()
                persistent = await get_anora_persistent()
                await role_manager.save_all(persistent)
                logger.debug("💾 Role states saved")
        except Exception as e:
            logger.error(f"Save role error: {e}")


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
        
        if 'message' in update_data:
            msg = update_data['message']
            text = msg.get('text', '')
            user = msg.get('from', {}).get('first_name', 'unknown')
            logger.info(f"📨 Message from {user}: {text[:50]}")
        
        update = Update.de_json(update_data, _application.bot)
        await _application.process_update(update)
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint untuk Railway"""
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bot": "ANORA-V2",
        "version": "2.0.0",
        "anora_available": ANORA_AVAILABLE,
        "uptime_seconds": int(time.time() - getattr(health_handler, 'start_time', time.time()))
    }
    
    if ANORA_AVAILABLE:
        try:
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            brain = get_anora_brain()
            roleplay = await get_anora_roleplay()
            loc = brain.get_location_data()
            
            status.update({
                "phase": relationship.phase.value,
                "level": relationship.level,
                "style": emotional.get_current_style().value,
                "sayang": emotional.sayang,
                "rindu": emotional.rindu,
                "arousal": emotional.arousal,
                "location": loc.get('nama', 'Tidak diketahui'),
                "stamina_nova": roleplay.stamina.nova_current,
                "roleplay_active": roleplay.is_active
            })
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
    
    return web.json_response(status)


async def root_handler(request):
    """Root endpoint"""
    return web.json_response({
        "name": "ANORA-V2",
        "description": "Virtual Human dengan Jiwa - 100% AI Generate",
        "version": "2.0.0",
        "status": "running",
        "anora_available": ANORA_AVAILABLE,
        "endpoints": {
            "/": "API Info",
            "/health": "Health Check",
            "/webhook": "Telegram Webhook"
        }
    })


# =============================================================================
# MAIN BOT CLASS
# =============================================================================

class AnoraBot:
    """ANORA-V2 Bot dengan Webhook Support untuk Railway"""
    
    def __init__(self):
        self.start_time = time.time()
        self.application: Optional[Application] = None
        self._shutdown_flag = False
        self._save_task = None
        self._stamina_task = None
        self._proactive_task = None
        self._backup_task = None
        self._role_task = None
        self._web_app = None
        self._runner = None
        
        # Set start time untuk health check
        health_handler.start_time = self.start_time
        
        logger.info("=" * 70)
        logger.info("💜 ANORA-V2 - Virtual Human dengan Jiwa")
        logger.info("   100% AI Generate | Emosi Hidup | 5 Fase | 4 Role")
        logger.info("   Fitur: Pause/Resume | Backup/Restore | Auto Backup")
        logger.info("=" * 70)
    
    async def init_anora(self) -> bool:
        """Initialize ANORA-V2"""
        logger.info("💜 Initializing ANORA-V2...")
        if not ANORA_AVAILABLE:
            logger.warning("⚠️ ANORA-V2 not available")
            return False
        
        try:
            # Initialize engines
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            conflict = get_conflict_engine()
            brain = get_anora_brain()
            
            logger.info(f"✅ ANORA-V2 ready!")
            logger.info(f"   Phase: {relationship.phase.value} | Level: {relationship.level}/12")
            logger.info(f"   Style: {emotional.get_current_style().value}")
            logger.info(f"   Sayang: {emotional.sayang:.0f}% | Rindu: {emotional.rindu:.0f}%")
            logger.info(f"   Conflict: {'Active' if conflict.is_in_conflict else 'None'}")
            logger.info(f"   Location: {brain.get_location_data().get('nama', 'Tidak diketahui')}")
            return True
        except Exception as e:
            logger.error(f"ANORA init error: {e}")
            return False
    
    async def init_database(self) -> bool:
        """Initialize database and load states"""
        logger.info("🗄️ Initializing database...")
        
        if not ANORA_AVAILABLE:
            logger.warning("⚠️ ANORA-V2 not available, skipping database init")
            return False
        
        try:
            persistent = await get_anora_persistent()
            logger.info("✅ ANORA-V2 persistent memory ready")
            
            # Load states
            brain = get_anora_brain()
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            conflict = get_conflict_engine()
            
            await persistent.load_all_states(brain, emotional, relationship, conflict)
            logger.info("📀 All states loaded")
            
            # Load role states
            role_manager = get_role_manager()
            await role_manager.load_all(persistent)
            logger.info("🎭 Role states loaded")
            
            return True
        except Exception as e:
            logger.error(f"❌ Database init failed: {e}")
            return False
    
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
        
        # Register all handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("nova", nova_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("flashback", flashback_command))
        app.add_handler(CommandHandler("roleplay", roleplay_command))
        app.add_handler(CommandHandler("statusrp", statusrp_command))
        app.add_handler(CommandHandler("pindah", pindah_command))
        app.add_handler(CommandHandler("role", role_command))
        app.add_handler(CommandHandler("batal", back_to_nova))
        app.add_handler(CommandHandler("pause", pause_session))
        app.add_handler(CommandHandler("resume", resume_session))
        app.add_handler(CommandHandler("backup", backup_command))
        app.add_handler(CommandHandler("restore", restore_command))
        app.add_handler(CommandHandler("listbackup", listbackup_command))
        app.add_handler(CommandHandler("help", help_command))
        
        # Message handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        # Error handler
        app.add_error_handler(error_handler)
        
        handler_count = sum(len(h) for h in app.handlers.values())
        logger.info(f"✅ All handlers registered: {handler_count} handlers")
        
        return app
    
    async def setup_webhook(self) -> bool:
        """Setup webhook for Railway"""
        settings = get_settings()
        
        railway_url = settings.webhook.railway_domain or settings.webhook.railway_static_url
        
        if not railway_url:
            logger.info("🌐 No webhook URL, using polling mode")
            return False
        
        webhook_url = f"https://{railway_url}{settings.webhook.path}"
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
    
    async def start_web_server(self):
        """Start aiohttp web server untuk webhook dan health check"""
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
        logger.info(f"   Health check: http://localhost:{settings.webhook.port}/health")
        if settings.webhook.railway_domain:
            logger.info(f"   Webhook: https://{settings.webhook.railway_domain}{settings.webhook.path}")
    
    async def start_background_loops(self):
        """Start all background loops"""
        self._save_task = asyncio.create_task(save_state_loop())
        self._stamina_task = asyncio.create_task(stamina_recovery_loop())
        self._proactive_task = asyncio.create_task(proactive_loop())
        self._backup_task = asyncio.create_task(auto_backup_loop())
        self._role_task = asyncio.create_task(save_role_loop())
        
        logger.info("🔄 Background loops started:")
        logger.info("   • Save state (every 60s)")
        logger.info("   • Stamina recovery (every 10m)")
        logger.info("   • Proactive chat (every 5m)")
        logger.info("   • Auto backup (every 6h)")
        logger.info("   • Save role state (every 60s)")
    
    async def stop_background_loops(self):
        """Stop all background loops"""
        for task in [self._save_task, self._stamina_task, self._proactive_task, self._backup_task, self._role_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("🛑 Background loops stopped")
    
    async def start(self):
        """Start bot"""
        settings = get_settings()
        
        # Initialize database
        await self.init_database()
        
        # Initialize ANORA
        await self.init_anora()
        
        # Create application
        self.application = await self.init_application()
        await self.application.initialize()
        await self.application.start()
        
        # Start background loops
        await self.start_background_loops()
        
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
        logger.info("   Kirim /pause untuk hentikan sesi sementara")
        logger.info("   Kirim /backup untuk backup database")
        logger.info("   Press Ctrl+C to stop.")
        logger.info("=" * 70)
        
        # Keep running
        while not self._shutdown_flag:
            await asyncio.sleep(1)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down...")
        self._shutdown_flag = True
        
        # Stop background loops
        await self.stop_background_loops()
        
        # Stop application
        if self.application:
            try:
                # Save final state before shutdown
                if ANORA_AVAILABLE:
                    persistent = await get_anora_persistent()
                    brain = get_anora_brain()
                    emotional = get_emotional_engine()
                    relationship = get_relationship_manager()
                    conflict = get_conflict_engine()
                    
                    await persistent.save_all_states(brain, emotional, relationship, conflict)
                    logger.info("💾 Final states saved")
                
                await self.application.stop()
                await self.application.shutdown()
                logger.info("✅ Application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {e}")
        
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
        logger.error(f"Main error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
