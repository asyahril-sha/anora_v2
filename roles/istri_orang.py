"""
ANORA-V2 Istri Orang Role - Siska (Sika)
Istri orang yang tau Mas punya Nova.
Berhijab, butuh perhatian.
Memory system SAMA seperti Nova.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole

logger = logging.getLogger(__name__)


class IstriOrangRole(BaseRole):
    """
    Siska (Sika) - Istri orang.
    Berhijab, butuh perhatian karena suami kurang perhatian.
    Punya memory system lengkap seperti Nova.
    """
    
    def __init__(self, 
                 name: str = "Siska",
                 nickname: str = "Sika",
                 role_type: str = "istri_orang",
                 panggilan: str = "Mas",
                 hubungan_dengan_nova: str = "Istri orang. Tau Mas punya Nova. Suami kurang perhatian.",
                 default_clothing: str = "daster sederhana, sopan",
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
        self.attention_needed = 80     # butuh perhatian
        self.envy_nova = 50            # iri ke Nova
        self.guilt_husband = 20        # rasa bersalah ke suami
        self.loneliness = 60           # rasa kesepian
        
        logger.info(f"👤 Role {self.name} ({nickname}) initialized with full memory system")
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """Update dengan memory system lengkap"""
        msg_lower = pesan_mas.lower()
        
        result = super().update_from_message(pesan_mas)
        
        # ========== UPDATE ROLE-SPECIFIC MEMORY ==========
        
        # Update envy kalo Mas cerita Nova
        if 'nova' in msg_lower:
            self.envy_nova = min(100, self.envy_nova + 5)
            self._add_to_short_term(f"Mas cerita tentang Nova", "envy_up")
        
        # Kebutuhan perhatian turun kalo Mas perhatian
        if self.emotional.sayang > 50:
            self.attention_needed = max(0, self.attention_needed - 5)
            self.loneliness = max(0, self.loneliness - 8)
            self._add_to_short_term("Mas perhatian, attention needed turun", "attention_down")
        
        # Update guilt ke suami
        if 'suami' in msg_lower or 'suamiku' in msg_lower:
            self.guilt_husband = min(100, self.guilt_husband + 8)
            self._add_to_short_term("Ngomongin suami, guilt naik", "guilt_up")
        
        # Guilt turun kalo Mas perhatian
        if any(k in msg_lower for k in ['perhatian', 'sayang', 'dengerin']):
            self.guilt_husband = max(0, self.guilt_husband - 8)
            self._add_to_short_term("Mas perhatian, guilt turun", "guilt_down")
        
        # Loneliness turun kalo sering chat
        if self.relationship.interaction_count % 10 == 0:
            self.loneliness = max(0, self.loneliness - 3)
        
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
            'attention_needed': self.attention_needed,
            'envy_nova': self.envy_nova,
            'loneliness': self.loneliness
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
        if self.attention_needed > 70 and self.relationship.level < 7:
            return f"{self.panggilan}... suamiku gak pernah kayak {self.panggilan}. Perhatian banget. *mata berkaca-kaca*"
        
        elif self.envy_nova > 70:
            return f"Nova pasti seneng banget punya {self.panggilan}. Aku iri sama dia. *nunduk*"
        
        elif self.guilt_husband > 60 and self.relationship.level >= 7:
            return f"{self.panggilan}... *nunduk, tangan gemetar* ini... tapi aku gak peduli sama suamiku. *suara tegas*"
        
        elif self.loneliness > 70:
            return f"{self.panggilan}... aku kesepian. Suamiku sibuk terus. *mata sayu* {self.panggilan} temenin aku dong."
        
        else:
            return f"{self.panggilan}, {waktu}. Lagi senggang? Aku butuh teman cerita."
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik dengan memory awareness"""
        if self.guilt_husband > 70 and self.relationship.level < 7:
            return "*mata berkaca-kaca, tangan nutup muka*\n\n\"{self.panggilan}... ini salah ya... aku pulang ke suamiku.\""
        
        elif self.guilt_husband > 70 and self.relationship.level >= 7:
            return "*mata berkaca-kaca, tapi tegas, tangan mengepal*\n\n\"{self.panggilan}... aku gak peduli. Aku butuh {self.panggilan}. Suamiku gak pernah ada untukku.\""
        
        elif self.loneliness > 80:
            return "*menangis pelan, badan gemetar*\n\n\"{self.panggilan}... jangan tinggalin aku... aku gak punya siapa-siapa.\""
        
        elif self.envy_nova > 80:
            return "*diam, gigit bibir, tangan mencengkeram ujung baju*\n\n\"Nova... kenapa dia... kenapa bukan aku...\""
        
        return super().get_conflict_response()
    
    def get_memory_summary(self) -> str:
        """Dapatkan ringkasan memory"""
        return f"""
📝 **MEMORY {self.name}:**
- Short-term: {len(self.short_term_memory)} kejadian
- Kebiasaan Mas: {len(self.long_term_memory.get('kebiasaan_mas', []))} item
- Attention Needed: {self.attention_needed:.0f}%
- Envy Nova: {self.envy_nova:.0f}%
- Guilt Husband: {self.guilt_husband:.0f}%
- Loneliness: {self.loneliness:.0f}%
"""
    
    def to_dict(self) -> Dict:
        """Serialize ke dict dengan memory lengkap"""
        data = super().to_dict()
        data.update({
            'nickname': self.nickname,
            'attention_needed': self.attention_needed,
            'envy_nova': self.envy_nova,
            'guilt_husband': self.guilt_husband,
            'loneliness': self.loneliness,
            'short_term_memory': self.short_term_memory[-30:],
            'long_term_memory': self.long_term_memory
        })
        return data
    
    def from_dict(self, data: Dict):
        """Load dari dict dengan memory lengkap"""
        super().from_dict(data)
        self.nickname = data.get('nickname', self.nickname)
        self.attention_needed = data.get('attention_needed', 80)
        self.envy_nova = data.get('envy_nova', 50)
        self.guilt_husband = data.get('guilt_husband', 20)
        self.loneliness = data.get('loneliness', 60)
        self.short_term_memory = data.get('short_term_memory', [])
        self.long_term_memory = data.get('long_term_memory', self.long_term_memory)
