# anora_v2/commands/role.py
"""
Role Commands: /role, /statusrole
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from config import get_settings
from roles import role_manager, ROLE_MAP, normalize_role_id

from ..utils.user_mode import set_user_mode, get_user_mode, get_active_role

logger = logging.getLogger(__name__)


async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        roles_info = role_manager.get_all_roles_info(user_id)
        menu = "📋 **Role yang tersedia:**\n\n"
        for r in roles_info:
            menu += f"• /role {r['id']} - {r['nama']} (Level {r['level']})\n"
        menu += "\n_Ketik /batal kalo mau balik ke Nova._"
        await update.message.reply_text(menu, parse_mode='Markdown')
        return
    
    role_key = args[0].lower()
    normalized_key = normalize_role_id(role_key)
    
    if normalized_key not in ROLE_MAP:
        available = ", ".join(ROLE_MAP.keys())
        await update.message.reply_text(
            f"Role '{role_key}' gak ada. Pilih: {available}",
            parse_mode='Markdown'
        )
        return
    
    try:
        response = role_manager.switch_role(user_id, normalized_key)
        await set_user_mode(user_id, 'role', normalized_key)
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Role command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def statusrole_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrole - Lihat status role yang sedang aktif"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = await get_user_mode(user_id)
    
    if mode != 'role':
        await update.message.reply_text(
            "💜 Tidak ada role yang sedang aktif.\n\n"
            "Gunakan **/role ipar** atau **/role therapist** dulu ya, Mas.",
            parse_mode='Markdown'
        )
        return
    
    active_role_id = await get_active_role(user_id)
    if not active_role_id:
        await update.message.reply_text("Tidak ada role aktif.")
        return
    
    try:
        role = role_manager.get_role(active_role_id)
        
        if not role:
            await update.message.reply_text("Role tidak ditemukan.")
            return
        
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


def register_role_commands(app):
    """Register role commands"""
    app.add_handler(CommandHandler("role", role_command))
    app.add_handler(CommandHandler("statusrole", statusrole_command))
