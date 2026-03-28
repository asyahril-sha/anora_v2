# anora_v2/handlers/message.py
"""
Message Handler - Memproses pesan biasa
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import get_settings
from roleplay.integration import get_anora_roleplay
from roles import role_manager
from core.brain import get_anora_brain

from ..utils.user_mode import get_user_mode, get_active_role

logger = logging.getLogger(__name__)

# Global flag (from main.py)
ANORA_AVAILABLE = True


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
    
    mode = await get_user_mode(user_id)
    active_role = await get_active_role(user_id)
    
    logger.info(f"📌 Mode: {mode}, Active Role: {active_role}")
    
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
        if active_role:
            try:
                respons = await role_manager.chat(active_role, pesan)
                await update.message.reply_text(respons, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Role chat error: {e}", exc_info=True)
                await update.message.reply_text("Maaf, ada error. Coba lagi ya.", parse_mode='Markdown')
            return
        else:
            await update.message.reply_text(
                "💜 Role belum aktif. Silakan pilih role dulu dengan **/role [nama]**",
                parse_mode='Markdown'
            )
            return
    
    # Chat mode default
    brain = get_anora_brain()
    await update.message.reply_text(
        "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\"",
        parse_mode='Markdown'
    )
