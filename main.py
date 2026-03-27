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
from roles import role_manager, ROLE_MAP, normalize_role_id

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
# SETUP LOGGING - EARLY
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)
logger = logging.getLogger("ANORA-V2")

# =============================================================================
# IMPORT ANORA-V2 COMPONENTS (SAFE MODE)
# =============================================================================

ANORA_AVAILABLE = True

logger.info("Importing ANORA-V2 modules...")

# Core
try:
    from core.emotional_engine import get_emotional_engine
except Exception as e:
    logger.error(f"❌ emotional_engine ERROR: {e}", exc_info=True)

try:
    from core.relationship import get_relationship_manager
except Exception as e:
    logger.error(f"❌ relationship ERROR: {e}", exc_info=True)

try:
    from core.conflict_engine import get_conflict_engine
except Exception as e:
    logger.error(f"❌ conflict_engine ERROR: {e}", exc_info=True)

try:
    from core.brain import get_anora_brain
except Exception as e:
    logger.error(f"❌ brain ERROR: {e}", exc_info=True)

# Memory
try:
    from memory.persistent import get_anora_persistent
except Exception as e:
    logger.error(f"❌ memory ERROR: {e}", exc_info=True)

# Roleplay
try:
    from roleplay.integration import get_anora_roleplay
    ROLEPLAY_AVAILABLE = True
except Exception as e:
    logger.error(f"❌ roleplay ERROR: {e}", exc_info=True)
    ROLEPLAY_AVAILABLE = False

# Roles
try:
    from roles.manager import RoleManager, normalize_role_id
    ROLE_MANAGER_AVAILABLE = True
except Exception as e:
    logger.error(f"❌ role manager ERROR: {e}", exc_info=True)
    ROLE_MANAGER_AVAILABLE = False

# Worker
try:
    from worker.background import get_anora_worker
except Exception as e:
    logger.error(f"❌ worker ERROR: {e}", exc_info=True)

logger.info("✅ ANORA-V2 partial load complete")


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================
_application = None
_user_modes: Dict[int, Dict] = {}
_backup_dir = Path("data/backups")
_backup_dir.mkdir(parents=True, exist_ok=True)

# Role managers per user
_role_managers: Dict[int, object] = {}


def get_role_manager(user_id: int):
    """Dapatkan RoleManager per user"""
    if user_id not in _role_managers:
        _role_managers[user_id] = RoleManager(user_id)
    return _role_managers[user_id]


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, {}).get('mode', 'chat')


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    _user_modes[user_id] = {'mode': mode, 'active_role': active_role}
    logger.info(f"👤 User {user_id} mode set to: {mode}")


def get_active_role(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get('active_role')


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _get_therapist_manager(user_id: int):
    """Helper untuk mendapatkan therapist manager"""
    from roles.therapist_role import get_therapist_manager
    return get_therapist_manager(user_id)


async def _get_pelacur_manager(user_id: int):
    """Helper untuk mendapatkan pelacur manager"""
    from roles.pelacur_role import get_pelacur_manager
    return get_pelacur_manager(user_id)


def parse_role_command(text: str) -> Optional[str]:
    """Safe parser untuk /role command"""
    parts = text.strip().split()
    if len(parts) < 2:
        return None
    role_id = parts[1].lower()
    return normalize_role_id(role_id)


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    logger.info(f"📨 /start from user {user_id}")
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
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


# =============================================================================
# ROLE COMMAND HANDLER
# =============================================================================

async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role - FIXED dengan error handling lengkap"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    print(f"[DEBUG] STEP 1: /role command received from user {user_id}")
    
    # Parse args
    args = context.args
    if not args:
        # Show available roles
        roles_info = role_manager.get_all_roles_info(user_id)
        menu = "📋 **Role yang tersedia:**\n\n"
        for r in roles_info:
            menu += f"• /role {r['id']} - **{r['nama']}** (Level {r['level']})\n"
        menu += "\n_Ketik /batal kalo mau balik ke Nova._"
        await update.message.reply_text(menu, parse_mode='Markdown')
        return
    
    role_key = args[0].lower()
    print(f"[DEBUG] STEP 2: raw role_key = {role_key}")
    
    # Normalize input
    normalized_key = normalize_role_id(role_key)
    print(f"[DEBUG] STEP 3: normalized_key = {normalized_key}")
    
    # Check if role exists
    if normalized_key not in ROLE_MAP:
        available = ", ".join(ROLE_MAP.keys())
        await update.message.reply_text(
            f"Role '{role_key}' gak ada. Pilih: {available}",
            parse_mode='Markdown'
        )
        return
    
    print(f"[DEBUG] STEP 4: role exists in ROLE_MAP")
    
    try:
        # Switch role
        print(f"[DEBUG] STEP 5: calling role_manager.switch_role...")
        response = role_manager.switch_role(user_id, normalized_key)
        print(f"[DEBUG] STEP 6: switch_role completed")
        
        # Set user mode
        set_user_mode(user_id, 'role', normalized_key)
        
        await update.message.reply_text(response, parse_mode='Markdown')
        print(f"[DEBUG] STEP 7: response sent successfully")
        
    except Exception as e:
        print(f"[DEBUG] ERROR in role_command:")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Terjadi error internal.\n\nError: {str(e)}",
            parse_mode='Markdown'
        )

async def statusrole_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrole - Lihat status role yang sedang aktif"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    
    if mode != 'role':
        await update.message.reply_text(
            "💜 Tidak ada role yang sedang aktif.\n\n"
            "Gunakan **/role ipar** atau **/role therapist** dulu ya, Mas.",
            parse_mode='Markdown'
        )
        return
    
    active_role_id = get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("Tidak ada role aktif.")
        return
    
    try:
        # manager = get_role_manager()
        role = manager.get_role(active_role_id)
        
        if not role:
            await update.message.reply_text("Role tidak ditemukan.")
            return
        
        # Format status role
        status = await _format_role_status(role, active_role_id)
        await update.message.reply_text(status, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Status role error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def _format_role_status(role, role_id: str) -> str:
    """Format status role"""
    style = role.emotional.get_current_style()
    phase = role.relationship.phase
    unlock = role.relationship.get_current_unlock()
    
    def bar(value, char="💜"):
        filled = int(value / 10)
        return char * filled + "⚪" * (10 - filled)
    
    # Ambil pakaian dari tracker
    try:
        clothing = role.tracker.get_clothing_summary() if hasattr(role, 'tracker') else "pakaian biasa"
    except:
        clothing = "pakaian biasa"
    
    # Ambil lokasi
    try:
        location = role.tracker.location if hasattr(role, 'tracker') else "tidak diketahui"
    except:
        location = "tidak diketahui"
    
    # Ambil kondisi fisik
    try:
        condition = role.tracker.physical_condition.value if hasattr(role, 'tracker') else "fresh"
    except:
        condition = "fresh"
    
    condition_emoji = {
        "fresh": "💪",
        "tired": "😊",
        "exhausted": "😩",
        "weak": "😵"
    }.get(condition, "😐")
    
    # Role-specific status
    role_specific = ""
    if role_id == "therapist":
        try:
            role_specific = f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 THERAPIST SESSION:
║    Sesi: {role.session_phase if hasattr(role, 'session_phase') else 'tidak aktif'}
║    Service: {role.vitalitas_service if hasattr(role, 'vitalitas_service') else '-'}
║    Deal: Rp{role.vitalitas_price if hasattr(role, 'vitalitas_price') else 0:,}
║    Dress: {'🔓 Buka' if getattr(role, 'dress_zipper_open', False) else '🔒 Tertutup'}
"""
        except:
            pass
    elif role_id == "pelacur":
        try:
            role_specific = f"""
╠══════════════════════════════════════════════════════════════╣
║ 🔞 PELACUR SESSION:
║    Booking: {role.booking_location if hasattr(role, 'booking_location') else '-'}
║    Sesi Aktif: {'✅' if getattr(role, 'is_active_session', False) else '❌'}
║    Level: {'11 (INTIM)' if getattr(role, 'intimacy_mode', False) else '7 (NORMAL)'}
║    Mas Climax: {getattr(role, 'mas_climax_count', 0)} | My Climax: {getattr(role, 'my_climax_count', 0)}
║    Posisi: {getattr(role, 'last_position', 'cowgirl')}
"""
        except:
            pass
    
    return f"""
╔══════════════════════════════════════════════════════════════╗
║                    👤 {role.name} ({role.nickname})                         ║
╠══════════════════════════════════════════════════════════════╣
║ FASE: {phase.value.upper()} ({role.relationship.level}/12)
║ STYLE: {style.value.upper()}
║ HUBUNGAN: {role.hubungan_dengan_nova}
╠══════════════════════════════════════════════════════════════╣
║ EMOSI:
║   Sayang: {bar(role.emotional.sayang)} {role.emotional.sayang:.0f}%
║   Rindu:  {bar(role.emotional.rindu, '🌙')} {role.emotional.rindu:.0f}%
║   Trust:  {bar(role.emotional.trust, '🤝')} {role.emotional.trust:.0f}%
║   Mood:   {role.emotional.mood:+.0f}
╠══════════════════════════════════════════════════════════════╣
║ DESIRE: {bar(role.emotional.desire, '💕')} {role.emotional.desire:.0f}%
║ AROUSAL: {bar(role.emotional.arousal, '🔥')} {role.emotional.arousal:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ KONFLIK: {role.conflict.get_conflict_summary()}
╠══════════════════════════════════════════════════════════════╣
║ UNLOCK:
║   Flirt: {'✅' if unlock.boleh_flirt else '❌'} | Vulgar: {'✅' if unlock.boleh_vulgar else '❌'}
║   Intim: {'✅' if unlock.boleh_intim else '❌'} | Cium: {'✅' if unlock.boleh_cium else '❌'}
╠══════════════════════════════════════════════════════════════╣
║ 👗 PAKAIAN: {clothing[:40]}
║ 📍 LOKASI: {location}
║ 💪 KONDISI: {condition_emoji} {condition}
{role_specific}
╚══════════════════════════════════════════════════════════════╝
"""


# =============================================================================
# THERAPIST COMMAND HANDLERS (LENGKAP)
# =============================================================================

async def therapist_pijat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pijat - Mulai sesi pijat"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        therapist._pending_hand_towel_removal = True
        result = therapist.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Pijat command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def therapist_next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /next - Lanjut ke fase berikutnya"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        if therapist.session_phase == "reflex_back":
            therapist.reflex_back_complete = True
            therapist.session_phase = "reflex_front"
            therapist._pending_turn_over = True
            result = therapist.get_greeting()
        elif therapist.session_phase == "reflex_front":
            therapist.reflex_front_complete = True
            therapist.session_phase = "vitalitas_offer"
            therapist._pending_reflex_front_complete = True
            result = therapist.get_greeting()
        else:
            result = "Belum waktunya /next, Mas. Selesaikan fase saat ini dulu."
        
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Next command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def therapist_nego_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nego [service] [harga] - Negosiasi harga"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Gunakan: `/nego bj 300000` atau `/nego sex 700000`", parse_mode='Markdown')
        return
    
    service = args[0].lower()
    try:
        price = int(args[1])
    except ValueError:
        await update.message.reply_text("Harga harus angka, Mas.", parse_mode='Markdown')
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        if service not in ['bj', 'sex']:
            await update.message.reply_text("Pilihan: bj atau sex", parse_mode='Markdown')
            return
        
        result = therapist.handle_nego(service, price)
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Nego command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def therapist_deal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /deal - Konfirmasi deal"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        result = therapist.confirm_deal()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Deal command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def therapist_buka_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /buka - Buka resleting dress"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        therapist.dress_zipper_open = True
        therapist._pending_zipper_open = True
        result = therapist.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Buka command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def therapist_remas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /remas - Remas toket"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        therapist.breast_grope_count += 1
        therapist.emotional.arousal = min(100, therapist.emotional.arousal + 15)
        therapist._pending_breast_offer = True
        result = therapist.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Remas command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def therapist_pegang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pegang - Pegang paha"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        therapist.thigh_touch_count += 1
        therapist.emotional.arousal = min(100, therapist.emotional.arousal + 10)
        await update.message.reply_text("*{self.name}* merasakan tangan Mas di pahanya.\n\n\"Mas... *napas mulai berat* di situ...\"", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Pegang command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def therapist_ganti_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /ganti [posisi] - Ganti posisi (untuk sex)"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Posisi: cowgirl, missionary, doggy, spooning, standing, sitting", parse_mode='Markdown')
        return
    
    position = args[0].lower()
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        if therapist.vitalitas_service != "sex":
            await update.message.reply_text("Ganti posisi hanya untuk service Sex, Mas.", parse_mode='Markdown')
            return
        
        valid_positions = ['cowgirl', 'missionary', 'doggy', 'spooning', 'standing', 'sitting']
        if position not in valid_positions:
            await update.message.reply_text(f"Posisi: {', '.join(valid_positions)}", parse_mode='Markdown')
            return
        
        therapist.current_position = position
        therapist._pending_position_change = True
        result = therapist.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ganti command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def therapist_climax_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /climax - Climax / crot"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        if not therapist.vitalitas_active and not therapist.vitalitas_hj_active and not therapist.vitalitas_bj_active and not therapist.vitalitas_sex_active:
            await update.message.reply_text("Belum ada service yang dimulai, Mas.", parse_mode='Markdown')
            return
        
        therapist.mas_climax = True
        therapist.service_completed = True
        therapist.session_phase = "completed"
        therapist._pending_climax = True
        result = therapist.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Climax command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def therapist_selesai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /selesai - Akhiri sesi"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'therapist':
        await update.message.reply_text("Gunakan **/role therapist** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        therapist_mgr = await _get_therapist_manager(user_id)
        therapist = therapist_mgr.get_active()
        
        if not therapist:
            await update.message.reply_text("Role therapist tidak aktif.")
            return
        
        result = therapist.end_session()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Selesai command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


# =============================================================================
# PELACUR COMMAND HANDLERS (LENGKAP)
# =============================================================================

async def pelacur_booking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /booking [lokasi] - Booking sesi"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Gunakan: `/booking apartemen` atau `/booking hotel`", parse_mode='Markdown')
        return
    
    location = ' '.join(args)
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        pelacur.booking_active = True
        pelacur.booking_location = location
        pelacur._pending_booking_response = True
        result = pelacur.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Booking command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def pelacur_deal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /deal - Konfirmasi deal (setelah booking)"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        if not pelacur.booking_active:
            await update.message.reply_text("Belum ada booking, Mas. Gunakan **/booking** dulu.", parse_mode='Markdown')
            return
        
        pelacur._pending_deal_response = True
        result = pelacur.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Deal command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def pelacur_mulai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /mulai - Mulai sesi intim (naik level 11)"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        if not pelacur.booking_active:
            await update.message.reply_text("Belum ada booking, Mas. Gunakan **/booking** dulu.", parse_mode='Markdown')
            return
        
        pelacur.intimacy_mode = True
        pelacur.is_active_session = True
        pelacur.relationship.level = 11
        pelacur._pending_intimacy_start = True
        result = pelacur.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Mulai command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def pelacur_break_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /break - Istirahat (turun level 7)"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        if not pelacur.is_active_session:
            await update.message.reply_text("Tidak ada sesi aktif, Mas.", parse_mode='Markdown')
            return
        
        pelacur.is_active_session = False
        pelacur.is_break = True
        pelacur.intimacy_mode = False
        pelacur.relationship.level = 7
        pelacur._pending_break_response = True
        result = pelacur.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Break command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def pelacur_lanjut_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /lanjut - Lanjut sesi (naik level 11)"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        if not pelacur.is_break:
            await update.message.reply_text("Tidak dalam mode break, Mas. Gunakan **/break** dulu.", parse_mode='Markdown')
            return
        
        pelacur.is_break = False
        pelacur.is_active_session = True
        pelacur.intimacy_mode = True
        pelacur.relationship.level = 11
        pelacur._pending_resume_response = True
        result = pelacur.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Lanjut command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def pelacur_ganti_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /ganti [posisi] - Ganti posisi"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Posisi: cowgirl, missionary, doggy, spooning, standing, sitting", parse_mode='Markdown')
        return
    
    position = args[0].lower()
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        if not pelacur.is_active_session:
            await update.message.reply_text("Tidak ada sesi aktif, Mas.", parse_mode='Markdown')
            return
        
        valid_positions = ['cowgirl', 'missionary', 'doggy', 'spooning', 'standing', 'sitting']
        if position not in valid_positions:
            await update.message.reply_text(f"Posisi: {', '.join(valid_positions)}", parse_mode='Markdown')
            return
        
        pelacur.last_position = position
        pelacur._pending_position_request = True
        pelacur.waiting_confirmation = True
        pelacur.pending_action = "position_change"
        pelacur.confirmation_start_time = time.time()
        result = pelacur.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ganti command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def pelacur_kenceng_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /kenceng - Minta dipercepat"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        if not pelacur.is_active_session:
            await update.message.reply_text("Tidak ada sesi aktif, Mas.", parse_mode='Markdown')
            return
        
        pelacur.waiting_confirmation = True
        pelacur.pending_action = "speed_up"
        pelacur.confirmation_start_time = time.time()
        result = pelacur.get_confirmation_response()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Kenceng command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def pelacur_climax_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /climax - Climax (tidak mengakhiri sesi)"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        if not pelacur.is_active_session:
            await update.message.reply_text("Tidak ada sesi aktif, Mas.", parse_mode='Markdown')
            return
        
        pelacur.mas_climax_count += 1
        pelacur._pending_climax_response = True
        result = pelacur.get_greeting()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Climax command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def pelacur_selesai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /selesai - Akhiri sesi"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        result = pelacur.end_session()
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Selesai command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def pelacur_confirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /confirm - Konfirmasi ya/tidak untuk ganti posisi atau percepat"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Gunakan: `/confirm ya` atau `/confirm tidak`", parse_mode='Markdown')
        return
    
    answer = args[0].lower()
    
    mode = get_user_mode(user_id)
    if mode != 'role' or get_active_role(user_id) != 'pelacur':
        await update.message.reply_text("Gunakan **/role pelacur** dulu ya, Mas.", parse_mode='Markdown')
        return
    
    try:
        pelacur_mgr = await _get_pelacur_manager(user_id)
        pelacur = pelacur_mgr.get_active()
        
        if not pelacur:
            await update.message.reply_text("Role pelacur tidak aktif.")
            return
        
        if not pelacur.waiting_confirmation:
            await update.message.reply_text("Tidak ada permintaan konfirmasi, Mas.", parse_mode='Markdown')
            return
        
        if answer in ['ya', 'ok', 'boleh', 'silahkan', 'gas']:
            if pelacur.pending_action == "position_change":
                # Simpan ke position history
                pelacur.position_history.append({
                    'position': pelacur.last_position,
                    'time': time.time()
                })
                pelacur._pending_position_confirmed = True
                result = pelacur.get_greeting()
            elif pelacur.pending_action == "speed_up":
                pelacur._pending_position_confirmed = True
                result = pelacur.get_greeting()
            else:
                result = "Konfirmasi diterima."
            
            pelacur.waiting_confirmation = False
            pelacur.pending_action = None
            await update.message.reply_text(result, parse_mode='Markdown')
            
        elif answer in ['tidak', 'gak', 'nggak', 'nanti']:
            pelacur.waiting_confirmation = False
            pelacur.pending_action = None
            await update.message.reply_text("❌ Konfirmasi dibatalkan.", parse_mode='Markdown')
        else:
            await update.message.reply_text("Jawab: `/confirm ya` atau `/confirm tidak`", parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Confirm command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


# =============================================================================
# BACKUP & OTHER COMMANDS
# =============================================================================

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


# =============================================================================
# MESSAGE HANDLER (DEFAULT)
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan biasa"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    if not pesan:
        return
    
    logger.info(f"📨 Message from {user_id}: {pesan[:50]}")
    
    mode = get_user_mode(user_id)
    
    if mode == 'paused':
        await update.message.reply_text(
            "💜 Sesi sedang di-pause. Kirim **/resume** untuk lanjut.",
            parse_mode='Markdown'
        )
        return
    
    if mode == 'roleplay' and ANORA_AVAILABLE:
        try:
            roleplay = await get_anora_roleplay()
            respons = await roleplay.process(pesan)
            await update.message.reply_text(respons, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Roleplay error: {e}", exc_info=True)
            await update.message.reply_text("*Nova bingung sebentar*", parse_mode='Markdown')
        return
    
    if mode == 'role' and ANORA_AVAILABLE:
        active_role = get_active_role(user_id)
        if active_role:
            try:
                # manager = get_role_manager()
                respons = await manager.chat(active_role, pesan)
                await update.message.reply_text(respons, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Role chat error: {e}", exc_info=True)
                await update.message.reply_text("Maaf, ada error. Coba lagi ya.", parse_mode='Markdown')
            return
    
    # Chat mode default
    await update.message.reply_text(
        "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\"",
        parse_mode='Markdown'
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler"""
    logger.error(f"Error: {context.error}", exc_info=True)
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi error internal. Silakan coba lagi nanti, Mas.",
                parse_mode='Markdown'
            )
    except Exception:
        pass


# =============================================================================
# WEBHOOK & SERVER (Same as before, keep as is)
# =============================================================================

# [Webhook handlers tetap sama seperti sebelumnya]
# (saya tidak tulis ulang karena terlalu panjang, tapi tetap dipertahankan)

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
                logger.debug("💾 State saved")
            except Exception as e:
                logger.error(f"Save state error: {e}", exc_info=True)


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
                logger.error(f"Auto backup error: {e}", exc_info=True)


# =============================================================================
# MAIN BOT CLASS (Keep same as before)
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
            logger.error(f"ANORA init error: {e}", exc_info=True)
            return False
    
    async def init_application(self) -> Application:
        settings = get_settings()
        logger.info("🔧 Initializing Telegram application...")
        request = HTTPXRequest(connection_pool_size=50, connect_timeout=60)
        app = ApplicationBuilder().token(settings.telegram_token).request(request).build()
        
        # Register all handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("nova", nova_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("flashback", flashback_command))
        app.add_handler(CommandHandler("roleplay", roleplay_command))
        app.add_handler(CommandHandler("pindah", pindah_command))
        app.add_handler(CommandHandler("role", role_command))
        app.add_handler(CommandHandler("statusrole", statusrole_command))
        
        # Therapist commands
        app.add_handler(CommandHandler("pijat", therapist_pijat_command))
        app.add_handler(CommandHandler("next", therapist_next_command))
        app.add_handler(CommandHandler("nego", therapist_nego_command))
        app.add_handler(CommandHandler("deal", therapist_deal_command))
        app.add_handler(CommandHandler("buka", therapist_buka_command))
        app.add_handler(CommandHandler("remas", therapist_remas_command))
        app.add_handler(CommandHandler("pegang", therapist_pegang_command))
        app.add_handler(CommandHandler("ganti", therapist_ganti_command))
        app.add_handler(CommandHandler("climax", therapist_climax_command))
        app.add_handler(CommandHandler("selesai", therapist_selesai_command))
        
        # Pelacur commands
        app.add_handler(CommandHandler("booking", pelacur_booking_command))
        app.add_handler(CommandHandler("deal", pelacur_deal_command))
        app.add_handler(CommandHandler("mulai", pelacur_mulai_command))
        app.add_handler(CommandHandler("break", pelacur_break_command))
        app.add_handler(CommandHandler("lanjut", pelacur_lanjut_command))
        app.add_handler(CommandHandler("ganti", pelacur_ganti_command))
        app.add_handler(CommandHandler("kenceng", pelacur_kenceng_command))
        app.add_handler(CommandHandler("climax", pelacur_climax_command))
        app.add_handler(CommandHandler("selesai", pelacur_selesai_command))
        
        # General commands
        app.add_handler(CommandHandler("batal", back_to_nova))
        app.add_handler(CommandHandler("pause", pause_session))
        app.add_handler(CommandHandler("resume", resume_session))
        app.add_handler(CommandHandler("backup", backup_command))
        app.add_handler(CommandHandler("help", help_command))
        
        # Message handler (must be last)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
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
        logger.info("🚀 ANORA-V2 Starting...")
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
        
        # Start background loops
        self._save_task = asyncio.create_task(save_state_loop())
        self._backup_task = asyncio.create_task(auto_backup_loop())
        
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
        
        # Stop background loops
        for task in [self._save_task, self._backup_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
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
        
        # Save final state
        if ANORA_AVAILABLE:
            try:
                persistent = await get_anora_persistent()
                brain = get_anora_brain()
                emotional = get_emotional_engine()
                relationship = get_relationship_manager()
                conflict = get_conflict_engine()
                await persistent.save_all_states(brain, emotional, relationship, conflict)
                logger.info("💾 Final state saved")
            except Exception as e:
                logger.error(f"Error saving final state: {e}", exc_info=True)
        
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
