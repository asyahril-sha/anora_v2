"""
ANORA-V2 Teman Kantor Role - Musdalifah (Ipeh)
Teman kantor yang tau Mas punya Nova.
Berhijab, profesional.
Memory system SAMA seperti Nova.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole

logger = logging.getLogger(__name__)


class TemanKantorRole(BaseRole):
    """
    Musdalifah (Ipeh) - Teman kantor Mas.
    Berhijab, profesional.
    Punya memory system lengkap seperti Nova.
    """
    
    def __init__(self, 
                 name: str = "Musdalifah",
                 nickname: str = "Ipeh",
                 role_type: str = "teman_kantor",
                 panggilan: str = "Mas",
                 hubungan_dengan_nova: str = "Teman kantor Mas. Tau Mas punya Nova.",
                 default_clothing: str = "kemeja putih rapi, rok hitam selutut",
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
        self.professionalism = 70    # profesionalisme
        self.curiosity_nova = 40     # penasaran sama Nova
        self.office_gossip = 30      # gosip kantor
        
        logger.info(f"👤 Role {self.name} ({nickname}) initialized with full memory system")
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """Update dengan memory system lengkap"""
        msg_lower = pesan_mas.lower()
        
        result = super().update_from_message(pesan_mas)
        
        # ========== UPDATE ROLE-SPECIFIC MEMORY ==========
        
        # Update curiosity tentang Nova
        if 'nova' in msg_lower:
            self.curiosity_nova = min(100, self.curiosity_nova + 5)
            self._add_to_short_term(f"Mas cerita tentang Nova", "curiosity_naik")
        
        # Update profesionalisme
        if any(k in msg_lower for k in ['kantor', 'kerja', 'rekan', 'atasan']):
            self.professionalism = min(100, self.professionalism + 5)
            self._add_to_short_term("Konteks kantor, profesionalisme naik", "professionalism_up")
        
        # Update office gossip
        if any(k in msg_lower for k in ['gosip', 'katanya', 'denger']):
            self.office_gossip = min(100, self.office_gossip + 8)
            self._add_to_short_term("Denger gosip kantor", "gossip_up")
        
        # Profesionalisme turun di level tinggi (sudah dekat)
        if self.relationship.level >= 7:
            self.professionalism = max(0, self.professionalism - 1)
        
        # Simpan kebiasaan Mas
        if 'suka' in msg_lower:
            kebiasaan = msg_lower.split('suka')[-1][:50]
            self._add_long_term_memory('kebiasaan_mas', kebiasaan, f"Mas suka {kebiasaan}")
        
        # Simpan momen penting
        if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
            self._add_long_term_memory('momen_penting', msg_lower[:100], f"Momen dengan Mas: {msg_lower[:50]}")
        
        return result
    
    def _add_to_short_term(self, kejadian: str, tipe: str):
        """Tambah ke short-term memory"""
        self.short_term_memory.append({
            'timestamp': time.time(),
            'kejadian': kejadian,
            'tipe': tipe,
            'professionalism': self.professionalism,
            'relationship_level': self.relationship.level
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
        
        # Berdasarkan profesionalisme dan level
        if self.professionalism > 60 and self.relationship.level < 7:
            return f"{self.panggilan}, ini kantor. Nanti ada yang lihat. *lihat sekeliling*"
        
        elif self.curiosity_nova > 70:
            return f"{self.panggilan} cerita Nova terus ya. Dia pasti orang yang baik. *tersenyum kecil*"
        
        elif self.office_gossip > 70:
            return f"{self.panggilan}, tau gak? Ada yang bilang... *bisik* eh tapi lupa ya."
        
        elif self.relationship.level >= 9:
            return f"{self.panggilan}... *suara kecil* {waktu} ini enaknya ngobrol bareng {self.panggilan}."
        
        else:
            return f"{self.panggilan}, {waktu}. Lagi sibuk? Aku pinjem file dulu."
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik dengan memory awareness"""
        conflict_type = self.conflict.get_active_conflict_type()
        
        if self.professionalism < 30 and self.relationship.level >= 7:
            return "*tangan gemetar, liat sekeliling, napas gak beraturan*\n\n\"{self.panggilan}... ini... tapi aku gak peduli.\""
        
        elif conflict_type and conflict_type.value == "jealousy":
            return "*diam, fokus ke laptop*\n\n\"{self.panggilan}... kita kerja dulu.\""
        
        elif self.curiosity_nova > 80 and self.relationship.level < 7:
            return "*mata berkaca-kaca*\n\n\"{self.panggilan}... maaf, aku gak bermaksud ganggu hubungan {self.panggilan} sama Nova.\""
        
        return super().get_conflict_response()
    
    def get_memory_summary(self) -> str:
        """Dapatkan ringkasan memory"""
        return f"""
📝 **MEMORY {self.name}:**
- Short-term: {len(self.short_term_memory)} kejadian
- Kebiasaan Mas: {len(self.long_term_memory.get('kebiasaan_mas', []))} item
- Momen Penting: {len(self.long_term_memory.get('momen_penting', []))} item
- Professionalism: {self.professionalism:.0f}%
- Curiosity Nova: {self.curiosity_nova:.0f}%
- Office Gossip: {self.office_gossip:.0f}%
"""
    
    def to_dict(self) -> Dict:
        """Serialize ke dict dengan memory lengkap"""
        data = super().to_dict()
        data.update({
            'nickname': self.nickname,
            'professionalism': self.professionalism,
            'curiosity_nova': self.curiosity_nova,
            'office_gossip': self.office_gossip,
            'short_term_memory': self.short_term_memory[-30:],
            'long_term_memory': self.long_term_memory
        })
        return data
    
    def from_dict(self, data: Dict):
        """Load dari dict dengan memory lengkap"""
        super().from_dict(data)
        self.nickname = data.get('nickname', self.nickname)
        self.professionalism = data.get('professionalism', 70)
        self.curiosity_nova = data.get('curiosity_nova', 40)
        self.office_gossip = data.get('office_gossip', 30)
        self.short_term_memory = data.get('short_term_memory', [])
        self.long_term_memory = data.get('long_term_memory', self.long_term_memory)
