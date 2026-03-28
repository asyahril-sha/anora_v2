# anora_v2/commands/pelacur.py
"""
Pelacur Commands: /booking, /deal, /mulai, /break, /lanjut, /ganti, /kenceng, /climax, /selesai, /confirm
"""

import time
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from config import get_settings

from ..utils.user_mode import get_user_mode, get_active_role

logger = logging.getLogger(__name__)


async def _get_pelacur_manager(user_id: int):
    """Helper untuk mendapatkan pelacur manager"""
    from roles.pelacur_role import get_pelacur_manager
    return get_pelacur_manager(user_id)


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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    if mode != 'role' or active_role != 'pelacur':
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


def register_pelacur_commands(app):
    """Register pelacur commands"""
    app.add_handler(CommandHandler("booking", pelacur_booking_command))
    app.add_handler(CommandHandler("deal", pelacur_deal_command))
    app.add_handler(CommandHandler("mulai", pelacur_mulai_command))
    app.add_handler(CommandHandler("break", pelacur_break_command))
    app.add_handler(CommandHandler("lanjut", pelacur_lanjut_command))
    app.add_handler(CommandHandler("ganti", pelacur_ganti_command))
    app.add_handler(CommandHandler("kenceng", pelacur_kenceng_command))
    app.add_handler(CommandHandler("climax", pelacur_climax_command))
    app.add_handler(CommandHandler("selesai", pelacur_selesai_command))
    app.add_handler(CommandHandler("confirm", pelacur_confirm_command))
