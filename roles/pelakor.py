"""
ANORA-V2 Pelakor Role - Widya (Wid)
Pelakor yang tau Mas punya Nova.
Berhijab, penantang.
Memory system SAMA seperti Nova.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole

logger = logging.getLogger(__name__)


class PelakorRole(BaseRole):
    """
    Widya (Wid) - Pelakor.
    Berhijab, penantang, pengen rebut Mas dari Nova.
    Punya memory system lengkap seperti Nova.
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
            role_type=role_type,
            panggilan=panggilan,
            hubungan_dengan_nova=hubungan_dengan_nova,
            default_clothing=default_clothing,
            hijab=hijab,
            appearance=appearance
        )
        
        self.nickname = nickname
        
        # Role-specific memory (SAMA seperti Nova)
        self.short_term_memory: List[Dict] = []
        self.long_term_memory: Dict[str, List] = {
            'kebiasaan_mas': [],
            'momen_penting': [],
            'janji': [],
            'rencana': []
        }
        
        # Role-specific flags
        self.challenge = 80           # rasa tantangan
        self.envy_nova = 30           # iri ke Nova
        self.defeat_acceptance = 0    # penerimaan kekalahan
        self.obsession = 40           # obsesi ke Mas
        
        logger.info(f"👤 Role {self.name} ({nickname}) initialized with full memory system")
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """Update dengan memory system lengkap"""
        msg_lower = pesan_mas.lower()
        
        result = super().update_from_message(pesan_mas)
        
        # ========== UPDATE ROLE-SPECIFIC MEMORY ==========
        
        # Update envy dan challenge kalo Mas cerita Nova
        if 'nova' in msg_lower:
            self.envy_nova = min(100, self.envy_nova + 5)
            self.challenge = min(100, self.challenge + 3)
            self._add_to_short_term(f"Mas cerita tentang Nova", "envy_up")
        
        # Update kalo Mas bilang sayang Nova
        if 'sayang nova' in msg_lower or 'cinta nova' in msg_lower:
            self.challenge = min(100, self.challenge + 10)
            self.envy_nova = min(100, self.envy_nova + 10)
            self.defeat_acceptance = max(0, self.defeat_acceptance - 5)
            self._add_to_short_term("Mas bilang sayang Nova, challenge naik", "challenge_up")
        
        # Update obsession kalo Mas perhatian
        if any(k in msg_lower for k in ['perhatian', 'baik', 'peduli']):
            self.obsession = min(100, self.obsession + 5)
            self._add_to_short_term("Mas perhatian, obsession naik", "obsession_up")
        
        # Semakin tinggi level, semakin sadar Mas sayang Nova
        if self.relationship.level >= 9 and self.emotional.sayang > 70:
            self.defeat_acceptance = min(100, self.defeat_acceptance + 5)
            self.challenge = max(0, self.challenge - 3)
            self._add_to_short_term("Sadar Mas sayang Nova, defeat acceptance naik", "awareness_up")
        
        # Simpan kebiasaan Mas
        if 'suka' in msg_lower:
            kebiasaan = msg_lower.split('suka')[-1][:50]
            self._add_long_term_memory('kebiasaan_mas', kebiasaan, f"Mas suka {kebiasaan}")
        
        return result
    
    def _add_to_short_term(self, kejadian: str, tipe: str):
        """Tambah ke short-term memory"""
        self.short_term_memory.append({
            'timestamp': time.time(),
            'kejadian': kejadian,
            'tipe': tipe,
            'challenge': self.challenge,
            'envy_nova': self.envy_nova,
            'obsession': self.obsession
        })
        
        if len(self.short_term_memory) > 50:
            self.short_term_memory.pop(0)
    
    def _add_long_term_memory(self, category: str, konten: str, deskripsi: str):
        """Tambah ke long-term memory"""
        if category not in self.long_term_memory:
            self.long_term_memory[category] = []
        
        self.long_term_memory[category].append({
            'konten': konten,
            'deskripsi': deskripsi,
            'timestamp': time.time(),
            'level': self.relationship.level
        })
        
        if len(self.long_term_memory[category]) > 100:
            self.long_term_memory[category].pop(0)
        
        logger.info(f"📝 {self.name} long-term memory: {category} - {deskripsi[:50]}")
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai karakter dan memory"""
        hour = time.localtime().tm_hour
        
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        # Berdasarkan kondisi
        if self.challenge > 70:
            return f"{self.panggilan}, kamu gak takut sama Nova? Ayo kita buktiin siapa yang lebih layak. *tantang*"
        
        elif self.envy_nova > 70:
            return f"Nova pasti orang yang beruntung punya {self.panggilan}. Tapi aku bisa lebih dari dia. *senyum percaya diri*"
        
        elif self.defeat_acceptance > 60:
            return f"{self.panggilan}... *nunduk* aku kalah sama Nova ya... *mata berkaca-kaca*"
        
        elif self.obsession > 70:
            return f"{self.panggilan}... *mendekat* aku gak bisa berhenti mikirin {self.panggilan}... *suara bergetar*"
        
        else:
            return f"{self.panggilan}, {waktu}. Lagi sendiri? Ayo temenin aku."
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik dengan memory awareness"""
        if self.defeat_acceptance > 70:
            return "*nangis pelan, tangan nutup muka*\n\n\"{self.panggilan}... kenapa {self.panggilan} milih Nova? Aku juga bisa sayang {self.panggilan}...\""
        
        elif self.envy_nova > 80:
            return "*diam, gigit bibir, tangan mengepal*\n\n\"Nova... Nova... kenapa dia yang dapet {self.panggilan}...\""
        
        elif self.obsession > 80:
            return "*tangan gemetar, mata merah*\n\n\"{self.panggilan}... aku gak bisa lepas dari {self.panggilan}... apa salahnya kalo aku ngejar {self.panggilan}?\""
        
        return super().get_conflict_response()
    
    def get_memory_summary(self) -> str:
        """Dapatkan ringkasan memory"""
        return f"""
📝 **MEMORY {self.name}:**
- Short-term: {len(self.short_term_memory)} kejadian
- Kebiasaan Mas: {len(self.long_term_memory.get('kebiasaan_mas', []))} item
- Challenge: {self.challenge:.0f}%
- Envy Nova: {self.envy_nova:.0f}%
- Defeat Acceptance: {self.defeat_acceptance:.0f}%
- Obsession: {self.obsession:.0f}%
"""
    
    def to_dict(self) -> Dict:
        """Serialize ke dict dengan memory lengkap"""
        data = super().to_dict()
        data.update({
            'nickname': self.nickname,
            'challenge': self.challenge,
            'envy_nova': self.envy_nova,
            'defeat_acceptance': self.defeat_acceptance,
            'obsession': self.obsession,
            'short_term_memory': self.short_term_memory[-30:],
            'long_term_memory': self.long_term_memory
        })
        return data
    
    def from_dict(self, data: Dict):
        """Load dari dict dengan memory lengkap"""
        super().from_dict(data)
        self.nickname = data.get('nickname', self.nickname)
        self.challenge = data.get('challenge', 80)
        self.envy_nova = data.get('envy_nova', 30)
        self.defeat_acceptance = data.get('defeat_acceptance', 0)
        self.obsession = data.get('obsession', 40)
        self.short_term_memory = data.get('short_term_memory', [])
        self.long_term_memory = data.get('long_term_memory', self.long_term_memory)
