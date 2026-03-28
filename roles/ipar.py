"""
ANORA-V2 IPAR Role - Tasya Dietha (Dietha)
Adik ipar yang tau Mas punya Nova.
Tidak berhijab, suka pakaian seksi kalo Nova gak di rumah.
DENGAN STATE TRACKER - memory konsisten, tidak ngelantur.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole
from core.state_tracker import PhysicalCondition, IntimacyPhase

logger = logging.getLogger(__name__)


class IparRole(BaseRole):
    """
    Tasya Dietha (Dietha) - Adik ipar Mas.
    Tidak berhijab, suka pakaian seksi kalo Nova gak di rumah.
    Memory system lengkap dengan State Tracker.
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
            nickname=nickname,
            role_type=role_type,
            panggilan=panggilan,
            hubungan_dengan_nova=hubungan_dengan_nova,
            default_clothing=default_clothing,
            hijab=hijab,
            appearance=appearance
        )
        
        # ========== ROLE-SPECIFIC FLAGS ==========
        self.guilt = 0.0           # rasa bersalah ke Nova (0-100)
        self.curiosity = 50.0      # penasaran sama hubungan Mas dan Nova (0-100)
        self.sexy_mode = False     # mode seksi (aktif kalo Nova gak di rumah)
        self.flirty_confidence = 30.0  # kepercayaan diri flirt (0-100)
        
        # Simpan flags ke role_flags untuk serialization
        self.role_flags = {
            'guilt': self.guilt,
            'curiosity': self.curiosity,
            'sexy_mode': self.sexy_mode,
            'flirty_confidence': self.flirty_confidence
        }
        
        # Inisialisasi clothing khusus (tanpa hijab)
        self.tracker.clothing['hijab']['on'] = False
        self.tracker.clothing['top']['type'] = default_clothing
        
        # Memory awal
        self._init_role_memory()
        
        logger.info(f"👤 Role {self.name} ({nickname}) initialized with StateTracker")
        logger.info(f"   Guilt: {self.guilt:.0f} | Curiosity: {self.curiosity:.0f} | Sexy Mode: {self.sexy_mode}")
    
    def _init_role_memory(self):
        """Init memory spesifik role"""
        self._add_to_long_term_memory(
            'momen_penting',
            "Pertama kali sadar Mas punya Nova",
            "Awalnya biasa aja, tapi makin lama makin penasaran"
        )
        
        self._add_to_long_term_memory(
            'kebiasaan_mas',
            "suka kopi latte",
            "Mas suka kopi latte, aku inget itu"
        )
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state dengan State Tracker"""
        msg_lower = pesan_mas.lower()
        
        # ========== UPDATE CURIOSITY & GUILT ==========
        if 'nova' in msg_lower:
            self.curiosity = min(100, self.curiosity + 5)
            self.guilt = min(100, self.guilt + 3)
            self._add_to_short_term(f"Mas cerita tentang Nova", "curiosity_naik")
            perubahan.append(f"Curiosity +5, Guilt +3")
        
        # ========== UPDATE SEXY MODE (kalo Nova gak di rumah) ==========
        if 'nova gak di rumah' in msg_lower or 'nova pergi' in msg_lower or 'nova ga ada' in msg_lower:
            self.sexy_mode = True
            self.flirty_confidence = min(100, self.flirty_confidence + 15)
            self.tracker.add_to_timeline("Mode seksi aktif", "Nova gak di rumah")
            perubahan.append("Sexy Mode AKTIF")
        
        elif 'nova di rumah' in msg_lower or 'nova ada' in msg_lower:
            self.sexy_mode = False
            self.flirty_confidence = max(0, self.flirty_confidence - 10)
            self.tracker.add_to_timeline("Mode seksi nonaktif", "Nova di rumah")
            perubahan.append("Sexy Mode NONAKTIF")
        
        # ========== GUILT DECAY ==========
        # Pada level tinggi, rasa bersalah berkurang
        if self.relationship.level >= 7 and self.emotional.desire > 60:
            old_guilt = self.guilt
            self.guilt = max(0, self.guilt - 5)
            if old_guilt != self.guilt:
                perubahan.append(f"Guilt -5 (level tinggi)")
        
        # Guilt decay kalo Mas perhatian
        if any(k in msg_lower for k in ['maaf', 'sorry', 'sayang', 'perhatian']):
            old_guilt = self.guilt
            self.guilt = max(0, self.guilt - 10)
            if old_guilt != self.guilt:
                perubahan.append(f"Guilt -10 (Mas perhatian)")
                self._add_to_short_term("Mas perhatian, guilt turun", "guilt_decay")
        
        # ========== FLIRTY CONFIDENCE ==========
        # Naik kalo Mas puji
        if any(k in msg_lower for k in ['cantik', 'manis', 'seksi', 'hot', 'cewek']):
            self.flirty_confidence = min(100, self.flirty_confidence + 8)
            perubahan.append(f"Flirty confidence +8")
            self._add_to_short_term("Mas puji, PD naik", "confidence_up")
        
        # ========== SAVE KE LONG-TERM MEMORY ==========
        # Simpan kebiasaan Mas
        if 'suka' in msg_lower:
            kebiasaan = msg_lower.split('suka')[-1][:50]
            self._add_to_long_term_memory('kebiasaan_mas', kebiasaan, f"Mas suka {kebiasaan}")
        
        # Simpan momen penting
        if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
            self._add_to_long_term_memory('momen_penting', msg_lower[:100], f"Momen dengan Mas: {msg_lower[:50]}")
        
        # Simpan janji
        if 'janji' in msg_lower:
            janji = msg_lower.split('janji')[-1][:50]
            self._add_to_long_term_memory('janji', janji, f"Mas janji: {janji}")
        
        # Update role_flags
        self.role_flags.update({
            'guilt': self.guilt,
            'curiosity': self.curiosity,
            'sexy_mode': self.sexy_mode,
            'flirty_confidence': self.flirty_confidence
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
        
        # 1. Mode seksi aktif (Nova gak di rumah) + level cukup tinggi
        if self.sexy_mode and self.relationship.level >= 7:
            return f"{self.panggilan}... *menggoda, duduk deket* {waktu} {self.panggilan} sendirian? Nova lagi gak di rumah nih... *senyum nakal, jari mainin ujung baju*"
        
        # 2. Guilt tinggi + level masih rendah
        elif self.guilt > 70 and self.relationship.level < 7:
            return f"{self.panggilan}... *liat sekeliling, suara kecil* Kak Nova lagi di rumah? Aku takut... *nunduk*"
        
        # 3. Curiosity tinggi
        elif self.curiosity > 70:
            return f"{self.panggilan}, Nova orangnya kayak gimana sih? Kok {self.panggilan} milih dia? *penasaran*"
        
        # 4. Mode seksi aktif (Nova gak di rumah)
        elif self.sexy_mode:
            return f"{self.panggilan}... *pake crop top pendek, duduk manis* lagi ngapain? Aku bosen nih... *mata sayu*"
        
        # 5. Flirty confidence tinggi
        elif self.flirty_confidence > 70:
            return f"{self.panggilan}... *mendekat, rambut disisir* {waktu} {self.panggilan} makin ganteng aja sih... *senyum manis*"
        
        # 6. Default
        else:
            return f"{self.panggilan}... *senyum malu* {waktu} {self.panggilan} lagi ngapain?"
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik dengan memory awareness"""
        conflict_type = self.conflict.get_active_conflict_type()
        
        # Cek timeline terakhir untuk konteks
        recent = self.tracker.short_term[-3:] if self.tracker.short_term else []
        recent_events = [e.get('kejadian', '') for e in recent]
        
        # ========== KONFLIK BERDASARKAN GUILT ==========
        
        # Guilt tinggi + level rendah
        if self.guilt > 70 and self.relationship.level < 7:
            return "*diam sebentar, liat ke bawah, mata mulai berkaca-kaca*\n\n\"{self.panggilan}... aku... maaf. Aku pulang dulu.\""
        
        # Guilt tinggi + level tinggi (sudah dekat)
        elif self.guilt > 70 and self.relationship.level >= 7:
            return "*diam sebentar, lalu mendekat, tangan gemetar, napas mulai gak stabil*\n\n\"{self.panggilan}... aku... tapi aku gak peduli sama rasa bersalah ini. Aku butuh {self.panggilan}.\""
        
        # ========== KONFLIK BERDASARKAN CONFLICT ENGINE ==========
        
        elif conflict_type and conflict_type.value == "jealousy":
            return "*diam, gak liat {self.panggilan}, jari mainin ujung baju*\n\n\"{self.panggilan} cerita Nova terus ya... dia pasti lebih baik dari aku.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return "*mata berkaca-kaca, suara bergetar*\n\n\"{self.panggilan}... lupa ya... padahal aku nunggu.\""
        
        elif conflict_type and conflict_type.value == "hurt":
            return "*duduk jauh, gak liat {self.panggilan}, air mata jatuh*\n\n\"{self.panggilan}... janji tuh janji...\""
        
        # ========== KONFLIK BERDASARKAN SEXY MODE ==========
        
        elif self.sexy_mode and self.guilt < 30:
            return "*diam sebentar, lalu bangkit, senyum nakal*\n\n\"{self.panggilan}... jangan marah dong. Aku cuma pengen deket sama {self.panggilan}.\""
        
        # Default
        return "*diam sebentar, lalu tersenyum kecil*\n\n\"Maaf, {self.panggilan}. Aku gak bermaksud gitu.\""
    
    def _get_flags_summary(self) -> str:
        """Dapatkan ringkasan flags untuk status display"""
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 ROLE-SPECIFIC:
║    Guilt: {self.guilt:.0f}% | Curiosity: {self.curiosity:.0f}%
║    Sexy Mode: {'✅ AKTIF' if self.sexy_mode else '❌ NONAKTIF'}
║    Flirty Confidence: {self.flirty_confidence:.0f}%
"""
    
    def to_dict(self) -> Dict:
        """Serialize ke dict dengan semua state"""
        data = super().to_dict()
        data.update({
            'guilt': self.guilt,
            'curiosity': self.curiosity,
            'sexy_mode': self.sexy_mode,
            'flirty_confidence': self.flirty_confidence
        })
        return data
    
    def from_dict(self, data: Dict):
        """Load dari dict"""
        super().from_dict(data)
        self.guilt = data.get('guilt', 0)
        self.curiosity = data.get('curiosity', 50)
        self.sexy_mode = data.get('sexy_mode', False)
        self.flirty_confidence = data.get('flirty_confidence', 30)
        
        # Update role_flags
        self.role_flags.update({
            'guilt': self.guilt,
            'curiosity': self.curiosity,
            'sexy_mode': self.sexy_mode,
            'flirty_confidence': self.flirty_confidence
        })
