# anora_v2/commands/therapist.py
"""
Therapist Commands: /pijat, /next, /nego, /deal, /buka, /remas, /pegang, /ganti, /climax, /selesai
"""

import time
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from config import get_settings

from ..utils.user_mode import get_user_mode, get_active_role

logger = logging.getLogger(__name__)


async def _get_therapist_manager(user_id: int):
    """Helper untuk mendapatkan therapist manager"""
    from roles.therapist_role import get_therapist_manager
    return get_therapist_manager(user_id)


async def therapist_pijat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pijat - Mulai sesi pijat"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'therapist':
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


def register_therapist_commands(app):
    """Register therapist commands"""
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
