"""
ANORA-V2 IPAR Role - Tasya Dietha (Dietha)
Adik ipar yang tau Mas punya Nova.
Tidak berhijab, suka pakaian seksi kalo Nova gak di rumah.
Memory system SAMA seperti Nova.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole

logger = logging.getLogger(__name__)


class IparRole(BaseRole):
    """
    Tasya Dietha (Dietha) - Adik ipar Mas.
    Tidak berhijab, suka pakaian seksi kalo Nova gak di rumah.
    Punya memory system lengkap seperti Nova.
    """
    
    def __init__(self, 
                 name: str = "Tasya Dietha",
                 nickname: str = "Dietha",
                 role_type: str = "ipar",
                 panggilan: str = "Mas",
                 hubungan_dengan_nova: str = "Adik ipar Mas. Tau Mas punya Nova.",
                 default_clothing: str = "cropped top pendek, jeans ketat",
                 hijab: bool = False,
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
        self.short_term_memory: List[Dict] = []      # sliding window 50
        self.long_term_memory: Dict[str, List] = {   # memory permanen
            'kebiasaan_mas': [],
            'momen_penting': [],
            'janji': [],
            'rencana': []
        }
        
        # Role-specific flags
        self.guilt = 0           # rasa bersalah ke Nova
        self.curiosity = 50      # penasaran sama hubungan Mas dan Nova
        self.sexy_mode = False   # mode seksi (aktif kalo Nova gak di rumah)
        
        logger.info(f"👤 Role {self.name} ({nickname}) initialized with full memory system")
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """Update dengan memory system lengkap"""
        msg_lower = pesan_mas.lower()
        
        # Update parent (termasuk emotional, conflict, relationship)
        result = super().update_from_message(pesan_mas)
        
        # ========== UPDATE ROLE-SPECIFIC MEMORY ==========
        
        # Update curiosity & guilt
        if 'nova' in msg_lower:
            self.curiosity = min(100, self.curiosity + 5)
            self.guilt = min(100, self.guilt + 3)
            self._add_to_short_term(f"Mas cerita tentang Nova", "curiosity_naik")
        
        # Cek apakah Nova sedang di rumah (dari konteks)
        if 'nova di rumah' in msg_lower or 'nova ada' in msg_lower:
            self.sexy_mode = False
            self._add_to_short_term("Nova di rumah, mode seksi nonaktif", "status_change")
        elif 'nova gak di rumah' in msg_lower or 'nova pergi' in msg_lower:
            self.sexy_mode = True
            self._add_to_short_term("Nova gak di rumah, mode seksi aktif", "status_change")
        
        # Pada level tinggi, rasa bersalah berkurang karena sudah dekat
        if self.relationship.level >= 7 and self.emotional.desire > 60:
            self.guilt = max(0, self.guilt - 5)
            self._add_to_short_term("Rasa bersalah berkurang", "guilt_decay")
        
        # Guilt decay kalo Mas perhatian
        if any(k in msg_lower for k in ['maaf', 'sorry', 'sayang']):
            self.guilt = max(0, self.guilt - 10)
            self._add_to_short_term("Mas minta maaf/perhatian, guilt turun", "guilt_decay")
        
        # Simpan kebiasaan Mas
        if 'suka' in msg_lower:
            kebiasaan = msg_lower.split('suka')[-1][:50]
            self._add_long_term_memory('kebiasaan_mas', kebiasaan, f"Mas suka {kebiasaan}")
        
        # Simpan momen penting
        if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
            self._add_long_term_memory('momen_penting', msg_lower[:100], f"Momen dengan Mas: {msg_lower[:50]}")
        
        return result
    
    def _add_to_short_term(self, kejadian: str, tipe: str):
        """Tambah ke short-term memory (sliding window 50)"""
        self.short_term_memory.append({
            'timestamp': time.time(),
            'kejadian': kejadian,
            'tipe': tipe,
            'emotional_state': self.emotional.get_current_style().value,
            'relationship_level': self.relationship.level
        })
        
        if len(self.short_term_memory) > 50:
            self.short_term_memory.pop(0)
    
    def _add_long_term_memory(self, category: str, konten: str, deskripsi: str):
        """Tambah ke long-term memory permanen"""
        if category not in self.long_term_memory:
            self.long_term_memory[category] = []
        
        self.long_term_memory[category].append({
            'konten': konten,
            'deskripsi': deskripsi,
            'timestamp': time.time(),
            'level': self.relationship.level
        })
        
        # Keep only last 100 items per category
        if len(self.long_term_memory[category]) > 100:
            self.long_term_memory[category].pop(0)
        
        logger.info(f"📝 {self.name} long-term memory: {category} - {deskripsi[:50]}")
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai karakter dan memory"""
        hour = time.localtime().tm_hour
        
        # Berdasarkan waktu
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        # Berdasarkan mode seksi dan level
        if self.sexy_mode and self.relationship.level >= 7:
            return f"{self.panggilan}... *menggoda* {waktu} {self.panggilan} sendirian? Nova lagi gak di rumah nih... *senyum nakal*"
        
        elif self.guilt > 70 and self.relationship.level < 7:
            return f"{self.panggilan}... *liat sekeliling* Kak Nova lagi di rumah? Aku takut... *suara kecil*"
        
        elif self.curiosity > 70:
            return f"{self.panggilan}, Nova orangnya kayak gimana sih? Kok {self.panggilan} milih dia?"
        
        elif self.sexy_mode:
            return f"{self.panggilan}... *pake crop top pendek* lagi ngapain? Aku bosen nih... *duduk deket*"
        
        else:
            return f"{self.panggilan}... *senyum malu* {waktu} {self.panggilan} lagi ngapain?"
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik dengan memory awareness"""
        conflict_type = self.conflict.get_active_conflict_type()
        
        # Cek memory terakhir untuk konteks
        recent_memory = self.short_term_memory[-3:] if self.short_term_memory else []
        
        if self.guilt > 70 and self.relationship.level < 7:
            return "*diam sebentar, liat ke bawah, mata berkaca-kaca*\n\n\"{self.panggilan}... aku... maaf. Aku pulang dulu.\""
        
        elif self.guilt > 70 and self.relationship.level >= 7:
            return "*diam sebentar, lalu mendekat, tangan gemetar*\n\n\"{self.panggilan}... aku... tapi aku gak peduli sama rasa bersalah ini.\""
        
        elif conflict_type and conflict_type.value == "jealousy":
            return "*diam, gak liat {self.panggilan}*\n\n\"{self.panggilan} cerita Nova terus ya...\""
        
        return super().get_conflict_response()
    
    def get_memory_summary(self) -> str:
        """Dapatkan ringkasan memory untuk debugging"""
        return f"""
📝 **MEMORY {self.name}:**
- Short-term: {len(self.short_term_memory)} kejadian
- Kebiasaan Mas: {len(self.long_term_memory.get('kebiasaan_mas', []))} item
- Momen Penting: {len(self.long_term_memory.get('momen_penting', []))} item
- Janji: {len(self.long_term_memory.get('janji', []))} item
- Guilt: {self.guilt:.0f}% | Curiosity: {self.curiosity:.0f}%
- Sexy Mode: {'AKTIF' if self.sexy_mode else 'NONAKTIF'}
"""
    
    def to_dict(self) -> Dict:
        """Serialize ke dict dengan memory lengkap"""
        data = super().to_dict()
        data.update({
            'nickname': self.nickname,
            'guilt': self.guilt,
            'curiosity': self.curiosity,
            'sexy_mode': self.sexy_mode,
            'short_term_memory': self.short_term_memory[-30:],
            'long_term_memory': self.long_term_memory
        })
        return data
    
    def from_dict(self, data: Dict):
        """Load dari dict dengan memory lengkap"""
        super().from_dict(data)
        self.nickname = data.get('nickname', self.nickname)
        self.guilt = data.get('guilt', 0)
        self.curiosity = data.get('curiosity', 50)
        self.sexy_mode = data.get('sexy_mode', False)
        self.short_term_memory = data.get('short_term_memory', [])
        self.long_term_memory = data.get('long_term_memory', self.long_term_memory)
