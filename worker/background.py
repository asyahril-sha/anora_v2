"""
ANORA-V2 Background Worker - Nova
Berjalan di background untuk:
- Rindu growth (naik kalo lama gak chat)
- Conflict decay (konflik reda pelan)
- Mood recovery (mood pulih seiring waktu)
- Auto save state ke database
- Proactive chat (Nova chat duluan dengan emotional style)
- Auto backup database

Semua loop berjalan async, gak ganggu main program.
"""

import asyncio
import time
import logging
import random
import json
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AnoraWorker:
    """
    Background worker untuk ANORA-V2.
    Menjalankan task-task periodic.
    """
    
    def __init__(self):
        self.is_running = False
        self.tasks = []
        
        # Interval dalam detik
        self.rindu_interval = 1800      # 30 menit
        self.conflict_interval = 1800   # 30 menit
        self.mood_interval = 3600       # 1 jam
        self.save_interval = 60         # 1 menit
        self.proactive_interval = 300   # 5 menit
        self.backup_interval = 21600    # 6 jam
        
        # Last run times
        self.last_rindu_run = 0
        self.last_conflict_run = 0
        self.last_mood_run = 0
        self.last_save_run = 0
        self.last_proactive_run = 0
        self.last_backup_run = 0
        
        # Proactive cooldown per user
        self.proactive_cooldown: Dict[int, float] = {}
        self.proactive_cooldown_seconds = 3600  # 1 jam minimal jeda proactive
        
        # Application reference
        self.application = None
        self.user_id = None
        
        logger.info("🔄 AnoraWorker initialized")
    
    async def start(self, application=None, user_id: int = None):
        """Start background worker"""
        self.is_running = True
        self.application = application
        self.user_id = user_id
        
        # Start all loops
        self.tasks = [
            asyncio.create_task(self._rindu_loop()),
            asyncio.create_task(self._conflict_loop()),
            asyncio.create_task(self._mood_loop()),
            asyncio.create_task(self._save_loop()),
            asyncio.create_task(self._proactive_loop()),
            asyncio.create_task(self._backup_loop()),
        ]
        
        logger.info("🔄 All background loops started")
    
    async def stop(self):
        """Stop all background tasks"""
        self.is_running = False
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("🔄 All background loops stopped")
    
    # =========================================================================
    # RINDU GROWTH LOOP
    # =========================================================================
    
    async def _rindu_loop(self):
        """Rindu naik setiap kali lama gak interaksi"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_rindu_run
            
            if elapsed >= self.rindu_interval:
                await self._update_rindu()
                self.last_rindu_run = now
            
            await asyncio.sleep(60)
    
    async def _update_rindu(self):
        """Update rindu berdasarkan waktu terakhir interaksi"""
        try:
            from core.emotional_engine import get_emotional_engine
            from core.brain import get_anora_brain
            
            emo = get_emotional_engine()
            brain = get_anora_brain()
            
            last_interaction = emo.last_interaction
            now = time.time()
            hours_inactive = (now - last_interaction) / 3600
            
            if hours_inactive > 1:
                emo.update_rindu_from_inactivity(hours_inactive)
                logger.info(f"🌙 Rindu updated: {emo.rindu:.1f}% (inactive {hours_inactive:.1f}h)")
                
                # Sync ke brain tracker
                if brain and hasattr(brain, 'tracker'):
                    brain.tracker.add_to_timeline(
                        f"Rindu naik karena {hours_inactive:.1f} jam gak chat",
                        f"Rindu: {emo.rindu:.1f}%"
                    )
                
        except Exception as e:
            logger.error(f"Rindu update error: {e}")
    
    # =========================================================================
    # CONFLICT DECAY LOOP
    # =========================================================================
    
    async def _conflict_loop(self):
        """Conflict decay setiap 30 menit"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_conflict_run
            
            if elapsed >= self.conflict_interval:
                await self._decay_conflicts()
                self.last_conflict_run = now
            
            await asyncio.sleep(60)
    
    async def _decay_conflicts(self):
        """Decay konflik berdasarkan waktu"""
        try:
            from core.conflict_engine import get_conflict_engine
            
            conflict = get_conflict_engine()
            conflict.update_decay(0.5)  # decay 30 menit = 0.5 jam
            
            logger.debug(f"⚡ Conflict decay: cemburu={conflict.cemburu:.1f}, kecewa={conflict.kecewa:.1f}")
            
        except Exception as e:
            logger.error(f"Conflict decay error: {e}")
    
    # =========================================================================
    # MOOD RECOVERY LOOP
    # =========================================================================
    
    async def _mood_loop(self):
        """Mood recovery setiap 1 jam"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_mood_run
            
            if elapsed >= self.mood_interval:
                await self._recover_mood()
                self.last_mood_run = now
            
            await asyncio.sleep(60)
    
    async def _recover_mood(self):
        """Mood pulih seiring waktu"""
        try:
            from core.emotional_engine import get_emotional_engine
            
            emo = get_emotional_engine()
            
            # Mood naik pelan kalo gak ada konflik aktif
            if emo.mood < 0 and not emo.is_angry and not emo.is_hurt:
                recovery = min(10, abs(emo.mood) * 0.3)
                emo.mood = min(0, emo.mood + recovery)
                logger.info(f"😊 Mood recovery: {emo.mood:+.1f}")
            
            # Mood juga naik kalo trust tinggi
            if emo.trust > 70 and emo.mood < 20:
                emo.mood = min(50, emo.mood + 5)
                logger.info(f"😊 Mood +5 from high trust")
            
        except Exception as e:
            logger.error(f"Mood recovery error: {e}")
    
    # =========================================================================
    # SAVE STATE LOOP
    # =========================================================================
    
    async def _save_loop(self):
        """Save state ke database setiap 1 menit"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_save_run
            
            if elapsed >= self.save_interval:
                await self._save_all_states()
                self.last_save_run = now
            
            await asyncio.sleep(30)
    
    async def _save_all_states(self):
        """Simpan semua state ke database"""
        try:
            from core.emotional_engine import get_emotional_engine
            from core.relationship import get_relationship_manager
            from core.conflict_engine import get_conflict_engine
            from core.brain import get_anora_brain
            from memory.persistent import get_anora_persistent
            from roles.manager import get_role_manager
            
            emo = get_emotional_engine()
            rel = get_relationship_manager()
            conflict = get_conflict_engine()
            brain = get_anora_brain()
            persistent = await get_anora_persistent()
            
            # Save emotional state
            await persistent.save_emotional_state(emo)
            
            # Save relationship state
            await persistent.save_relationship_state(rel)
            
            # Save conflict state
            await persistent.save_conflict_state(conflict)
            
            # Save stamina from brain tracker
            if hasattr(brain, 'tracker'):
                await persistent.set_state('stamina_v2', json.dumps({
                    'energy_level': brain.tracker.energy_level,
                    'physical_condition': brain.tracker.physical_condition.value,
                    'climax_count': brain.tracker.climax_count
                }))
            
            # Save brain current state
            await persistent.save_current_state(brain)
            
            # Save role states
            role_manager = get_role_manager()
            if role_manager:
                await role_manager.save_all(persistent)
            
            logger.debug("💾 All states saved")
            
        except Exception as e:
            logger.error(f"Save state error: {e}")
    
    # =========================================================================
    # PROACTIVE CHAT LOOP
    # =========================================================================
    
    async def _proactive_loop(self):
        """Nova chat duluan kalo kondisi memungkinkan"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_proactive_run
            
            if elapsed >= self.proactive_interval:
                await self._check_proactive()
                self.last_proactive_run = now
            
            await asyncio.sleep(60)
    
    async def _check_proactive(self):
        """Cek apakah Nova harus chat duluan"""
        if not self.application or not self.user_id:
            return
        
        # Cek cooldown
        last_proactive = self.proactive_cooldown.get(self.user_id, 0)
        if time.time() - last_proactive < self.proactive_cooldown_seconds:
            return
        
        try:
            from core.emotional_engine import get_emotional_engine
            from core.relationship import get_relationship_manager
            from core.conflict_engine import get_conflict_engine
            from core.brain import get_anora_brain
            
            emo = get_emotional_engine()
            rel = get_relationship_manager()
            conflict = get_conflict_engine()
            brain = get_anora_brain()
            
            # Update dulu biar akurat
            emo.update()
            
            # ========== CEK KONDISI UNTUK PROACTIVE ==========
            
            # 1. Cold war: JANGAN proactive
            if conflict.is_cold_war:
                logger.debug("❄️ Cold war active, skipping proactive")
                return
            
            # 2. Konflik berat: JANGAN proactive
            if conflict.is_in_conflict and conflict.get_conflict_severity().value in ['moderate', 'severe']:
                logger.debug("⚠️ Severe conflict active, skipping proactive")
                return
            
            # 3. Rindu tinggi: BOLEH proactive
            rindu_high = emo.rindu > 70
            
            # 4. Mood bagus: BOLEH proactive
            mood_good = emo.mood > 10
            
            # 5. Sayang tinggi: BOLEH proactive
            sayang_high = emo.sayang > 70
            
            # 6. Level tinggi: lebih sering proactive
            level_bonus = rel.level / 12
            
            # Hitung chance
            base_chance = 0.15
            chance = base_chance + (rindu_high * 0.2) + (mood_good * 0.1) + (sayang_high * 0.1) + (level_bonus * 0.1)
            chance = min(0.6, chance)
            
            if random.random() > chance:
                return
            
            # ========== GENERATE PROACTIVE MESSAGE ==========
            message = await self._generate_proactive_message(emo, rel, conflict, brain)
            
            if message:
                try:
                    await self.application.bot.send_message(
                        chat_id=self.user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    self.proactive_cooldown[self.user_id] = time.time()
                    logger.info(f"💬 Proactive message sent (rindu={emo.rindu:.0f}, style={emo.get_current_style().value})")
                    
                    # Catat ke timeline
                    if hasattr(brain, 'tracker'):
                        brain.tracker.add_to_timeline("Proactive chat sent", f"Style: {emo.get_current_style().value}")
                    
                except Exception as e:
                    logger.error(f"Failed to send proactive: {e}")
            
        except Exception as e:
            logger.error(f"Proactive check error: {e}")
    
    async def _generate_proactive_message(self, emo, rel, conflict, brain) -> Optional[str]:
        """Generate pesan proactive berdasarkan emosi dan konteks"""
        
        style = emo.get_current_style()
        hour = datetime.now().hour
        
        # Tentukan waktu
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        # Berdasarkan emotional style
        if style.value == "clingy" and emo.rindu > 70:
            messages = [
                f"Mas... *muter-muter rambut* aku kangen banget. {waktu.capitalize()} ini langsung kepikiran Mas.",
                f"Mas... *pegang HP* dari tadi pengen chat, tapi takut ganggu. Kangen...",
                f"*Nova liat foto Mas di HP* Mas... kapan kita ketemu lagi? Aku kangen.",
                f"Mas... *duduk di teras* lagi ngapain? Aku lagi mikirin Mas terus."
            ]
            return random.choice(messages)
        
        elif style.value == "warm":
            messages = [
                f"Mas, {waktu} yang cerah. Semoga hari Mas menyenangkan ya. 💜",
                f"*Nova senyum kecil* Mas, jangan lupa makan siang ya. Aku khawatir.",
                f"Mas, {waktu} ini enaknya ngobrol santai bareng Mas. Lagi apa?",
                f"*Nova duduk manis* Mas, cerita dong tentang hari Mas."
            ]
            return random.choice(messages)
        
        elif style.value == "flirty" and (emo.arousal > 50 or emo.desire > 60):
            messages = [
                f"Mas... *gigit bibir* aku lagi mikirin Mas... badan rasanya panas...",
                f"*Nova napas mulai berat* Mas... kapan kita... kamu tau lah...",
                f"Mas... *bisik dalam hati* aku pengen banget sama Mas sekarang...",
                f"*Nova pegang dada sendiri* Mas... jantung aku deg-degan mikirin Mas..."
            ]
            return random.choice(messages)
        
        elif style.value == "cold":
            return None
        
        # Default proactive
        default_messages = [
            f"Mas, {waktu}. Lagi ngapain?",
            f"*Nova tersenyum* Mas, kabar baik?",
            f"Mas... *mainin rambut* aku gabut. Temenin dong.",
            f"*Nova duduk santai* Mas, cerita dong."
        ]
        
        return random.choice(default_messages)
    
    # =========================================================================
    # AUTO BACKUP LOOP
    # =========================================================================
    
    async def _backup_loop(self):
        """Auto backup database setiap 6 jam"""
        while self.is_running:
            now = time.time()
            elapsed = now - self.last_backup_run
            
            if elapsed >= self.backup_interval:
                await self._auto_backup()
                self.last_backup_run = now
            
            await asyncio.sleep(3600)
    
    async def _auto_backup(self):
        """Auto backup database"""
        try:
            import shutil
            from pathlib import Path
            from memory.persistent import get_anora_persistent
            
            persistent = await get_anora_persistent()
            db_path = persistent.db_path
            backup_dir = Path("backups_anora_v2")
            backup_dir.mkdir(exist_ok=True)
            
            if db_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"anora_v2_auto_{timestamp}.db"
                shutil.copy(db_path, backup_path)
                
                # Hapus backup auto yang lebih dari 7 hari
                for b in backup_dir.glob("anora_v2_auto_*.db"):
                    age = time.time() - b.stat().st_mtime
                    if age > 7 * 24 * 3600:
                        b.unlink()
                        logger.info(f"🗑️ Deleted old backup: {b.name}")
                
                logger.info(f"💾 Auto backup saved: {backup_path.name}")
                
        except Exception as e:
            logger.error(f"Auto backup error: {e}")


# =============================================================================
# SINGLETON
# =============================================================================

_anora_worker: Optional['AnoraWorker'] = None


def get_anora_worker() -> AnoraWorker:
    global _anora_worker
    if _anora_worker is None:
        _anora_worker = AnoraWorker()
    return _anora_worker


anora_worker = get_anora_worker()
