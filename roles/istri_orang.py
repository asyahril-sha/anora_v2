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
            'deskripsi': deskri
