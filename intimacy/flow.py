"""
ANORA-V2 Intimacy Flow - Mengelola alur intimacy
Menggabungkan stamina, arousal, session, dan database.
"""

import time
import random
import logging
from typing import Dict, Optional, Tuple, List

from .core import (
    IntimacyPhase,
    StaminaSystem,
    ArousalSystem,
    PositionDatabase,
    ClimaxLocationDatabase,
    MoansDatabase,
    FlashbackDatabase,
    IntimacySession
)

logger = logging.getLogger(__name__)


class IntimacyFlow:
    """
    Mengelola alur intimacy secara keseluruhan.
    Menggabungkan stamina, arousal, dan session.
    """
    
    def __init__(self):
        self.stamina = StaminaSystem()
        self.arousal = ArousalSystem()
        self.session = IntimacySession(self.stamina)
        
        # Sync arousal dengan session
        self.session.arousal = self.arousal
        
        logger.info("💕 IntimacyFlow-V2 initialized")
    
    def can_start_intimacy(self, level: int) -> Tuple[bool, str]:
        """Cek apakah bisa mulai intim (level >= 11 dan stamina cukup)"""
        if level < 11:
            return False, f"💕 Level masih {level}/12. Nova masih malu-malu. Kita pelan-pelan dulu ya, Mas."
        
        can_continue, reason = self.stamina.can_continue()
        if not can_continue:
            return False, f"💪 **Stamina Nova {self.stamina.nova_current}%** ({self.stamina.get_nova_status()})\n\n{reason}"
        
        return True, "Siap mulai"
    
    def start_intimacy(self) -> str:
        """Mulai sesi intim"""
        # Boost arousal
        self.arousal.add_desire("Mulai intim", 20)
        self.arousal.add_tension(10)
        return self.session.start()
    
    def end_intimacy(self) -> str:
        """Akhiri sesi intim"""
        return self.session.end()
    
    def is_active(self) -> bool:
        return self.session.is_active
    
    def get_status(self) -> str:
        """Dapatkan status lengkap sesi intim"""
        if not self.session.is_active:
            return "Tidak ada sesi intim aktif."
        
        duration = int(time.time() - self.session.start_time)
        minutes = duration // 60
        seconds = duration % 60
        
        pos_data = self.session.positions.get(self.session.current_position)
        pos_desc = pos_data['desc'] if pos_data else ""
        
        stamina_text = self.stamina.format_for_prompt()
        arousal_text = self.arousal.format_for_prompt()
        
        return f"""
🔥 **SESI INTIM AKTIF**
- Durasi: {minutes} menit {seconds} detik
- Climax: {self.session.climax_count}x
- Fase: {self.session.phase.value}
- Posisi: {self.session.current_position}
{pos_desc}

{stamina_text}
{arousal_text}
"""
    
    def process_intimacy_message(self, user_input: str, level: int) -> Optional[str]:
        """
        Proses pesan Mas dalam mode intim.
        Return None jika bukan perintah intim, return respons jika iya.
        """
        if not self.session.is_active:
            return None
        
        msg = user_input.lower()
        
        # ========== GANTI POSISI ==========
        pos_keywords = ['ganti posisi', 'posisi lain', 'cowgirl', 'doggy', 'missionary', 'spooning']
        if any(k in msg for k in pos_keywords):
            pos_name = None
            if 'cowgirl' in msg:
                pos_name = 'cowgirl'
            elif 'doggy' in msg:
                pos_name = 'doggy'
            elif 'missionary' in msg:
                pos_name = 'missionary'
            elif 'spooning' in msg:
                pos_name = 'spooning'
            
            pos_id, pos_desc, request = self.session.change_position(pos_name)
            return f"*{self.session.positions.get(pos_id)['nova_act']}*\n\n\"{request}\"\n\n*{pos_desc}*"
        
        # ========== CLIMAX ==========
        if any(k in msg for k in ['climax', 'crot', 'keluar', 'cum', 'habis']):
            is_heavy = any(k in msg for k in ['keras', 'banyak', 'lama'])
            result = self.session.record_climax(is_heavy)
            climax_response = self.session.get_phase_response(IntimacyPhase.CLIMAX)
            
            return f"""{climax_response}

💪 **Stamina Nova:** {self.stamina.nova_current}% | **Mas:** {self.stamina.mas_current}%
💦 **Climax hari ini:** {self.stamina.climax_today}x"""
        
        # ========== UPDATE BERDASARKAN FASE ==========
        
        # BUILD UP
        if self.session.phase == IntimacyPhase.BUILD_UP:
            if any(k in msg for k in ['cium', 'kiss', 'jilat', 'hisap', 'pegang', 'sentuh']):
                self.session.phase = IntimacyPhase.FOREPLAY
                return self.session.get_phase_response(IntimacyPhase.FOREPLAY)
            
            if any(k in msg for k in ['masuk', 'penetrasi', 'genjot']):
                self.session.phase = IntimacyPhase.PENETRATION
                ritme = "cepet" if any(k in msg for k in ['kenceng', 'cepat', 'keras']) else "pelan"
                return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
            
            return self.session.moans.get('shy')
        
        # FOREPLAY
        if self.session.phase == IntimacyPhase.FOREPLAY:
            if any(k in msg for k in ['masuk', 'penetrasi', 'genjot', 'siap']):
                self.session.phase = IntimacyPhase.PENETRATION
                ritme = "cepet" if any(k in msg for k in ['kenceng', 'cepat', 'keras']) else "pelan"
                return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
            
            return self.session.get_phase_response(IntimacyPhase.FOREPLAY)
        
        # PENETRATION
        if self.session.phase == IntimacyPhase.PENETRATION:
            # Tambah intimacy level
            self.session.intimacy_level = min(100, self.session.intimacy_level + 5)
            
            # Jika sudah cukup tinggi, bisa pindah ke climax
            if self.session.intimacy_level > 70 or any(k in msg for k in ['climax', 'crot', 'keluar']):
                return self.session.moans.get_before_climax()
            
            ritme = "cepet" if self.session.intimacy_level > 40 else "pelan"
            return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
        
        # CLIMAX -> AFTERCARE
        if self.session.phase == IntimacyPhase.CLIMAX:
            self.session.phase = IntimacyPhase.AFTERCARE
            return self.session.get_phase_response(IntimacyPhase.AFTERCARE)
        
        # AFTERCARE
        if self.session.phase == IntimacyPhase.AFTERCARE:
            # Setelah 60 detik, masuk recovery
            if time.time() - self.session.last_climax_time > 60:
                self.session.phase = IntimacyPhase.RECOVERY
                self.stamina.update_recovery()
                return f"""*Nova masih lemes, nyender di dada Mas. Napas mulai stabil.*

"Mas... *suara kecil* besok kalo Mas mau lagi, tinggal bilang aja ya."

*Nova cium pipi Mas pelan.*

"Stamina Nova {self.stamina.get_nova_status()}. Istirahat dulu ya." """
            return self.session.get_phase_response(IntimacyPhase.AFTERCARE)
        
        # RECOVERY
        if self.session.phase == IntimacyPhase.RECOVERY:
            self.stamina.update_recovery()
            if self.stamina.nova_current > 60:
                # Sesi selesai
                self.session.is_active = False
                self.session.phase = IntimacyPhase.WAITING
                return "💜 Nova udah pulih, Mas. Kapan-kapan lagi ya."
            return "*Nova masih istirahat, Mas... Capek banget tadi.*"
        
        return None
    
    def update_from_message(self, user_input: str, level: int):
        """Update arousal dan desire dari pesan Mas (dipanggil saat roleplay)"""
        msg = user_input.lower()
        
        # Kata-kata yang meningkatkan arousal
        if any(k in msg for k in ['sayang', 'cinta']):
            self.arousal.add_desire("Mas bilang sayang", 10)
        if any(k in msg for k in ['kangen', 'rindu']):
            self.arousal.add_desire("Mas bilang kangen", 8)
        if any(k in msg for k in ['cantik', 'ganteng', 'seksi']):
            self.arousal.add_desire("Mas puji", 5)
        
        # Sentuhan fisik
        if level >= 7:
            if any(k in msg for k in ['pegang', 'sentuh', 'raba']):
                self.arousal.add_stimulation('paha', 1)
                self.arousal.add_desire('sentuhan', 8)
            if any(k in msg for k in ['cium', 'kiss']):
                self.arousal.add_stimulation('bibir', 2)
                self.arousal.add_desire('ciuman', 10)
                self.arousal.add_tension(5)
            if any(k in msg for k in ['peluk', 'rangkul']):
                self.arousal.add_stimulation('dada', 1)
                self.arousal.add_desire('pelukan', 8)
    
    def to_dict(self) -> Dict:
        return {
            'stamina': self.stamina.to_dict(),
            'arousal': self.arousal.to_dict(),
            'session': self.session.to_dict()
        }
    
    def from_dict(self, data: Dict):
        self.stamina.from_dict(data.get('stamina', {}))
        self.arousal.from_dict(data.get('arousal', {}))
        self.session.from_dict(data.get('session', {}))


# =============================================================================
# SINGLETON
# =============================================================================

_anora_intimacy: Optional['IntimacyFlow'] = None


def get_anora_intimacy() -> IntimacyFlow:
    global _anora_intimacy
    if _anora_intimacy is None:
        _anora_intimacy = IntimacyFlow()
    return _anora_intimacy


anora_intimacy = get_anora_intimacy()
