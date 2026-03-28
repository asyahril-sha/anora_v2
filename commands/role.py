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
        
        style = role.emotional.get_current_style()
        phase = role.relationship.phase
        unlock = role.relationship.get_current_unlock()
        
        def bar(value, char="💜"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        try:
            clothing = role.tracker.get_clothing_summary() if hasattr(role, 'tracker') else "pakaian biasa"
        except:
            clothing = "pakaian biasa"
        
        try:
            location = role.tracker.location if hasattr(role, 'tracker') else "tidak diketahui"
        except:
            location = "tidak diketahui"
        
        condition_emoji = "💪"
        
        status = f"""
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
║ 💪 KONDISI: {condition_emoji}
╚══════════════════════════════════════════════════════════════╝
"""
        await update.message.reply_text(status, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Status role error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


def register_role_commands(app):
    """Register role commands"""
    app.add_handler(CommandHandler("role", role_command))
    app.add_handler(CommandHandler("statusrole", statusrole_command))
