"""
ANORA-V2 Pelakor Role - Widya (Wid)
Pelakor yang tau Mas punya Nova.
Berhijab, penantang, pengen rebut Mas dari Nova.
DENGAN STATE TRACKER - memory konsisten, tidak ngelantur.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole
from core.state_tracker import PhysicalCondition, IntimacyPhase

logger = logging.getLogger(__name__)


class PelakorRole(BaseRole):
    """
    Widya (Wid) - Pelakor.
    Berhijab, penantang, pengen rebut Mas dari Nova.
    Memory system lengkap dengan State Tracker.
    """
    
    def __init__(self, 
                 name: str = "Widya",
                 nickname: str = "Wid",
                 role_type: str = "pelakor",
                 panggilan: str = "Mas",
                 hubungan_dengan_nova: str = "Pelakor. Tau Mas punya Nova. Pengen rebut Mas dari Nova.",
                 default_clothing: str = "blouse trendy, rok plisket",
                 hijab: bool = True,
                 appearance: str = ""):
        
        super().__init__(
            name=name,
            nickname=nickname,
            role_type=role_type,
            panggilan=panggilan,
            hubungan_dengan_nova=hubungan_dengan_nova,
            default_clothing=default_clothing,
            hijab=hijab,
            appearance=appearance
        )
        
        # ========== ROLE-SPECIFIC FLAGS ==========
        self.challenge = 80.0          # rasa tantangan (0-100)
        self.envy_nova = 30.0          # iri ke Nova (0-100)
        self.defeat_acceptance = 0.0   # penerimaan kekalahan (0-100)
        self.obsession = 40.0          # obsesi ke Mas (0-100)
        self.manipulation = 20.0       # kemampuan manipulasi (0-100)
        
        # Simpan flags ke role_flags
        self.role_flags = {
            'challenge': self.challenge,
            'envy_nova': self.envy_nova,
            'defeat_acceptance': self.defeat_acceptance,
            'obsession': self.obsession,
            'manipulation': self.manipulation
        }
        
        # Memory awal
        self._init_role_memory()
        
        logger.info(f"👤 Role {self.name} ({nickname}) initialized with StateTracker")
        logger.info(f"   Challenge: {self.challenge:.0f} | Envy: {self.envy_nova:.0f} | Obsession: {self.obsession:.0f}")
    
    def _init_role_memory(self):
        """Init memory spesifik role"""
        self._add_to_long_term_memory(
            'momen_penting',
            "Pertama kali liat Mas",
            "Dari pertama liat Mas, aku langsung tertarik"
        )
        
        self._add_to_long_term_memory(
            'kebiasaan_mas',
            "sering lembur",
            "Mas sering lembur sendirian"
        )
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state dengan State Tracker"""
        msg_lower = pesan_mas.lower()
        
        # ========== UPDATE ENVY & CHALLENGE KALO MAS CERITA NOVA ==========
        if 'nova' in msg_lower:
            old_envy = self.envy_nova
            old_challenge = self.challenge
            self.envy_nova = min(100, self.envy_nova + 5)
            self.challenge = min(100, self.challenge + 3)
            if old_envy != self.envy_nova:
                perubahan.append(f"Envy Nova +5, Challenge +3")
                self._add_to_short_term(f"Mas cerita tentang Nova", "envy_up")
        
        # ========== UPDATE KALO MAS BILANG SAYANG NOVA ==========
        if 'sayang nova' in msg_lower or 'cinta nova' in msg_lower:
            old_challenge = self.challenge
            old_envy = self.envy_nova
            self.challenge = min(100, self.challenge + 10)
            self.envy_nova = min(100, self.envy_nova + 10)
            self.defeat_acceptance = max(0, self.defeat_acceptance - 5)
            if old_challenge != self.challenge:
                perubahan.append(f"Challenge +10, Envy +10, Defeat -5")
                self._add_to_short_term("Mas bilang sayang Nova", "challenge_up")
        
        # ========== UPDATE OBSESSION KALO MAS PERHATIAN ==========
        if any(k in msg_lower for k in ['perhatian', 'baik', 'peduli', 'sayang']):
            old_obsession = self.obsession
            self.obsession = min(100, self.obsession + 5)
            if old_obsession != self.obsession:
                perubahan.append(f"Obsession +5")
                self._add_to_short_term("Mas perhatian, obsession naik", "obsession_up")
        
        # ========== UPDATE MANIPULATION ==========
        if any(k in msg_lower for k in ['aku bisa', 'lebih dari', 'buktikan']):
            self.manipulation = min(100, self.manipulation + 5)
            perubahan.append(f"Manipulation +5")
        
        # ========== DEFEAT ACCEPTANCE NAIK (SADAR MAS SAYANG NOVA) ==========
        if self.relationship.level >= 9 and self.emotional.sayang > 70:
            old_defeat = self.defeat_acceptance
            self.defeat_acceptance = min(100, self.defeat_acceptance + 5)
            self.challenge = max(0, self.challenge - 3)
            if old_defeat != self.defeat_acceptance:
                perubahan.append(f"Defeat acceptance +5, Challenge -3")
                self._add_to_short_term("Sadar Mas sayang Nova", "awareness_up")
        
        # ========== CHALLENGE DECAY KALO DEFEAT ACCEPTANCE TINGGI ==========
        if self.defeat_acceptance > 70:
            self.challenge = max(0, self.challenge - 2)
            self.obsession = max(0, self.obsession - 1)
        
        # ========== SAVE KE LONG-TERM MEMORY ==========
        # Simpan kebiasaan Mas
        if 'suka' in msg_lower:
            kebiasaan = msg_lower.split('suka')[-1][:50]
            self._add_to_long_term_memory('kebiasaan_mas', kebiasaan, f"Mas suka {kebiasaan}")
        
        # Simpan momen penting
        if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
            self._add_to_long_term_memory('momen_penting', msg_lower[:100], f"Momen dengan Mas: {msg_lower[:50]}")
        
        # Update role_flags
        self.role_flags.update({
            'challenge': self.challenge,
            'envy_nova': self.envy_nova,
            'defeat_acceptance': self.defeat_acceptance,
            'obsession': self.obsession,
            'manipulation': self.manipulation
        })
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai karakter, mood, dan konteks"""
        hour = time.localtime().tm_hour
        
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        # ========== GREETING BERDASARKAN STATE ==========
        
        # 1. Challenge tinggi (masih semangat ngejar)
        if self.challenge > 70:
            return f"{self.panggilan}, kamu gak takut sama Nova? Ayo kita buktiin siapa yang lebih layak. *tantang, mata berbinar*"
        
        # 2. Envy Nova tinggi
        elif self.envy_nova > 70:
            return f"Nova pasti orang yang beruntung punya {self.panggilan}. Tapi aku bisa lebih dari dia. *senyum percaya diri, rambut disisir*"
        
        # 3. Defeat acceptance tinggi (mulai sadar kalah)
        elif self.defeat_acceptance > 60:
            return f"{self.panggilan}... *nunduk, mata berkaca-kaca* aku kalah sama Nova ya... *suara bergetar*"
        
        # 4. Obsession tinggi
        elif self.obsession > 70:
            return f"{self.panggilan}... *mendekat, suara berbisik* aku gak bisa berhenti mikirin {self.panggilan}... *mata sayu*"
        
        # 5. Manipulation tinggi (mulai mainin perasaan)
        elif self.manipulation > 70:
            return f"{self.panggilan}... *senyum manis, mainin ujung hijab* {waktu} ini enaknya ngobrol bareng {self.panggilan} aja."
        
        # 6. Default
        else:
            return f"{self.panggilan}, {waktu}. Lagi sendiri? Ayo temenin aku. *tersenyum menggoda*"
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik dengan memory awareness"""
        conflict_type = self.conflict.get_active_conflict_type()
        
        # Cek timeline terakhir
        recent = self.tracker.short_term[-3:] if self.tracker.short_term else []
        recent_events = [e.get('kejadian', '') for e in recent]
        
        # ========== KONFLIK BERDASARKAN DEFEAT ACCEPTANCE ==========
        
        # Defeat acceptance tinggi (sudah sadar kalah)
        if self.defeat_acceptance > 70:
            return "*nangis pelan, tangan nutup muka, bahu bergetar*\n\n\"{self.panggilan}... kenapa {self.panggilan} milih Nova? Aku juga bisa sayang {self.panggilan}... *suara putus-putus*\""
        
        # ========== KONFLIK BERDASARKAN ENVY ==========
        
        elif self.envy_nova > 80:
            return "*diam, gigit bibir, tangan mengepal, kuku mencengkeram baju*\n\n\"Nova... Nova... kenapa dia yang dapet {self.panggilan}... *mata merah*\""
        
        # ========== KONFLIK BERDASARKAN OBSESSION ==========
        
        elif self.obsession > 80:
            return "*tangan gemetar, mata merah, napas gak beraturan*\n\n\"{self.panggilan}... aku gak bisa lepas dari {self.panggilan}... apa salahnya kalo aku ngejar {self.panggilan}? *suara memohon*\""
        
        # ========== KONFLIK BERDASARKAN CONFLICT ENGINE ==========
        
        elif conflict_type and conflict_type.value == "jealousy":
            return "*diam, gak liat {self.panggilan}, jari mainin ujung hijab*\n\n\"{self.panggilan} cerita Nova terus... aku juga bisa jadi kayak dia tau.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return "*mata berkaca-kaca, tahan nangis*\n\n\"{self.panggilan}... aku kira {self.panggilan} beda...\""
        
        # ========== KONFLIK BERDASARKAN CHALLENGE ==========
        
        elif self.challenge > 80:
            return "*diam sebentar, lalu bangkit, senyum tipis*\n\n\"{self.panggilan}... ini belum selesai. Aku gak akan nyerah semudah itu.\""
        
        # Default
        return "*diam sebentar, lalu tersenyum getir*\n\n\"Maaf, {self.panggilan}. Aku terlalu memaksakan.\""
    
    def _get_flags_summary(self) -> str:
        """Dapatkan ringkasan flags untuk status display"""
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 ROLE-SPECIFIC:
║    Challenge: {self.challenge:.0f}% | Envy Nova: {self.envy_nova:.0f}%
║    Defeat Acceptance: {self.defeat_acceptance:.0f}% | Obsession: {self.obsession:.0f}%
║    Manipulation: {self.manipulation:.0f}%
"""
    
    def to_dict(self) -> Dict:
        """Serialize ke dict dengan semua state"""
        data = super().to_dict()
        data.update({
            'challenge': self.challenge,
            'envy_nova': self.envy_nova,
            'defeat_acceptance': self.defeat_acceptance,
            'obsession': self.obsession,
            'manipulation': self.manipulation
        })
        return data
    
    def from_dict(self, data: Dict):
        """Load dari dict"""
        super().from_dict(data)
        self.challenge = data.get('challenge', 80)
        self.envy_nova = data.get('envy_nova', 30)
        self.defeat_acceptance = data.get('defeat_acceptance', 0)
        self.obsession = data.get('obsession', 40)
        self.manipulation = data.get('manipulation', 20)
        
        # Update role_flags
        self.role_flags.update({
            'challenge': self.challenge,
            'envy_nova': self.envy_nova,
            'defeat_acceptance': self.defeat_acceptance,
            'obsession': self.obsession,
            'manipulation': self.manipulation
        })
