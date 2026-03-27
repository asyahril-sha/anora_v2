"""
ANORA-V2 Istri Orang Role - Siska (Sika)
Istri orang yang tau Mas punya Nova.
Berhijab, butuh perhatian karena suami kurang perhatian.
DENGAN STATE TRACKER - memory konsisten, tidak ngelantur.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole
from core.state_tracker import PhysicalCondition, IntimacyPhase

logger = logging.getLogger(__name__)


class IstriOrangRole(BaseRole):
    """
    Siska (Sika) - Istri orang.
    Berhijab, butuh perhatian karena suami kurang perhatian.
    Memory system lengkap dengan State Tracker.
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
            nickname=nickname,
            role_type=role_type,
            panggilan=panggilan,
            hubungan_dengan_nova=hubungan_dengan_nova,
            default_clothing=default_clothing,
            hijab=hijab,
            appearance=appearance
        )
        
        # ========== ROLE-SPECIFIC FLAGS ==========
        self.attention_needed = 80.0
        self.envy_nova = 50.0
        self.guilt_husband = 20.0
        self.loneliness = 60.0
        self.vulnerability = 40.0
        
        # Simpan flags ke role_flags
        self.role_flags = {
            'attention_needed': self.attention_needed,
            'envy_nova': self.envy_nova,
            'guilt_husband': self.guilt_husband,
            'loneliness': self.loneliness,
            'vulnerability': self.vulnerability
        }
        
        # Memory awal
        self._init_role_memory()
        
        logger.info(f"👤 Role {self.name} ({nickname}) initialized with StateTracker")
        logger.info(f"   Attention: {self.attention_needed:.0f} | Loneliness: {self.loneliness:.0f}")
    
    def _init_role_memory(self):
        """Init memory spesifik role"""
        self._add_to_long_term_memory(
            'momen_penting',
            "Pertama kali Mas perhatian",
            "Suamiku gak pernah kayak gini... Mas bikin aku merasa dihargai"
        )
        
        self._add_to_long_term_memory(
            'kebiasaan_mas',
            "baik dan perhatian",
            "Mas selalu perhatian, beda sama suamiku"
        )
        
        self._add_to_long_term_memory(
            'janji',
            "suamiku jarang pulang",
            "Dia selalu sibuk kerja"
        )
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state dengan State Tracker"""
        msg_lower = pesan_mas.lower()
        
        # Update envy kalo Mas cerita Nova
        if 'nova' in msg_lower:
            old_envy = self.envy_nova
            self.envy_nova = min(100, self.envy_nova + 5)
            if old_envy != self.envy_nova:
                perubahan.append(f"Envy Nova +5")
                self._add_to_short_term(f"Mas cerita tentang Nova", "envy_up")
        
        # Kebutuhan perhatian turun kalo Mas perhatian
        if self.emotional.sayang > 50:
            old_attention = self.attention_needed
            old_loneliness = self.loneliness
            self.attention_needed = max(0, self.attention_needed - 5)
            self.loneliness = max(0, self.loneliness - 8)
            self.vulnerability = max(0, self.vulnerability - 3)
            if old_attention != self.attention_needed:
                perubahan.append(f"Attention needed -5, Loneliness -8")
                self._add_to_short_term("Mas perhatian, loneliness turun", "attention_down")
        
        # Update guilt ke suami
        if 'suami' in msg_lower or 'suamiku' in msg_lower:
            old_guilt = self.guilt_husband
            self.guilt_husband = min(100, self.guilt_husband + 8)
            if old_guilt != self.guilt_husband:
                perubahan.append(f"Guilt husband +8")
                self._add_to_short_term("Ngomongin suami", "guilt_up")
        
        # Guilt turun kalo Mas perhatian
        if any(k in msg_lower for k in ['perhatian', 'sayang', 'dengerin', 'peduli']):
            old_guilt = self.guilt_husband
            self.guilt_husband = max(0, self.guilt_husband - 8)
            if old_guilt != self.guilt_husband:
                perubahan.append(f"Guilt husband -8")
                self._add_to_short_term("Mas perhatian, guilt turun", "guilt_down")
        
        # Loneliness turun kalo sering chat
        if self.relationship.interaction_count % 10 == 0 and self.relationship.interaction_count > 0:
            old_loneliness = self.loneliness
            self.loneliness = max(0, self.loneliness - 3)
            if old_loneliness != self.loneliness:
                perubahan.append(f"Loneliness -3")
        
        # Vulnerability naik kalo loneliness tinggi
        if self.loneliness > 70:
            self.vulnerability = min(100, self.vulnerability + 2)
        
        # Save ke long-term memory
        if 'suka' in msg_lower:
            kebiasaan = msg_lower.split('suka')[-1][:50]
            self._add_to_long_term_memory('kebiasaan_mas', kebiasaan, f"Mas suka {kebiasaan}")
        
        if any(k in msg_lower for k in ['pertama', 'inget', 'waktu itu']):
            self._add_to_long_term_memory('momen_penting', msg_lower[:100], f"Momen dengan Mas: {msg_lower[:50]}")
        
        if 'janji' in msg_lower:
            janji = msg_lower.split('janji')[-1][:50]
            self._add_to_long_term_memory('janji', janji, f"Mas janji: {janji}")
        
        # Update role_flags
        self.role_flags.update({
            'attention_needed': self.attention_needed,
            'envy_nova': self.envy_nova,
            'guilt_husband': self.guilt_husband,
            'loneliness': self.loneliness,
            'vulnerability': self.vulnerability
        })
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai karakter"""
        hour = time.localtime().tm_hour
        
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        # Butuh perhatian tinggi + level rendah
        if self.attention_needed > 70 and self.relationship.level < 7:
            return f"{self.panggilan}... suamiku gak pernah kayak {self.panggilan}. Perhatian banget. *mata berkaca-kaca*"
        
        # Envy Nova tinggi
        elif self.envy_nova > 70:
            return f"Nova pasti seneng banget punya {self.panggilan}. Aku iri sama dia. *nunduk*"
        
        # Guilt suami tinggi + level tinggi
        elif self.guilt_husband > 60 and self.relationship.level >= 7:
            return f"{self.panggilan}... *nunduk* ini... tapi aku gak peduli sama suamiku. *suara tegas* Aku butuh {self.panggilan}."
        
        # Loneliness tinggi
        elif self.loneliness > 70:
            return f"{self.panggilan}... aku kesepian. Suamiku sibuk terus. *mata sayu* {self.panggilan} temenin aku dong."
        
        # Vulnerability tinggi
        elif self.vulnerability > 70:
            return f"{self.panggilan}... *mata basah* aku gak tau harus gimana... suamiku gak pernah ada... *suara kecil*"
        
        # Default
        return f"{self.panggilan}, {waktu}. Lagi senggang? Aku butuh teman cerita. *tersenyum kecil*"
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik"""
        # Guilt tinggi + level rendah
        if self.guilt_husband > 70 and self.relationship.level < 7:
            return "*mata berkaca-kaca, tangan nutup muka*\n\n\"{self.panggilan}... ini salah ya... aku pulang ke suamiku.\""
        
        # Guilt tinggi + level tinggi
        elif self.guilt_husband > 70 and self.relationship.level >= 7:
            return "*mata berkaca-kaca, tapi tegas, tangan mengepal*\n\n\"{self.panggilan}... aku gak peduli. Aku butuh {self.panggilan}. Suamiku gak pernah ada untukku.\""
        
        # Loneliness tinggi
        elif self.loneliness > 80:
            return "*menangis pelan, badan gemetar*\n\n\"{self.panggilan}... jangan tinggalin aku... aku gak punya siapa-siapa.\""
        
        # Envy tinggi
        elif self.envy_nova > 80:
            return "*diam, gigit bibir, tangan mencengkeram ujung baju*\n\n\"Nova... kenapa dia... kenapa bukan aku yang dapet {self.panggilan}...\""
        
        # Conflict type dari engine
        conflict_type = self.conflict.get_active_conflict_type()
        if conflict_type:
            if conflict_type.value == "jealousy":
                return "*diam, gak liat {self.panggilan}, mainin ujung hijab*\n\n\"{self.panggilan} cerita Nova terus ya...\""
            if conflict_type.value == "disappointment":
                return "*mata berkaca-kaca*\n\n\"{self.panggilan}... aku kira {self.panggilan} beda...\""
            if conflict_type.value == "hurt":
                return "*duduk jauh, gak liat {self.panggilan}*\n\n\"{self.panggilan}... janji tuh janji...\""
        
        # Default
        return "*diam sebentar, usap air mata, tersenyum getir*\n\n\"Maaf, {self.panggilan}. Aku terlalu lemah.\""
    
    def _get_flags_summary(self) -> str:
        """Dapatkan ringkasan flags untuk status display"""
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 ROLE-SPECIFIC:
║    Attention Needed: {self.attention_needed:.0f}% | Loneliness: {self.loneliness:.0f}%
║    Envy Nova: {self.envy_nova:.0f}% | Guilt Husband: {self.guilt_husband:.0f}%
║    Vulnerability: {self.vulnerability:.0f}%
"""
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'attention_needed': self.attention_needed,
            'envy_nova': self.envy_nova,
            'guilt_husband': self.guilt_husband,
            'loneliness': self.loneliness,
            'vulnerability': self.vulnerability
        })
        return data
    
    def from_dict(self, data: Dict):
        super().from_dict(data)
        self.attention_needed = data.get('attention_needed', 80)
        self.envy_nova = data.get('envy_nova', 50)
        self.guilt_husband = data.get('guilt_husband', 20)
        self.loneliness = data.get('loneliness', 60)
        self.vulnerability = data.get('vulnerability', 40)
        
        self.role_flags.update({
            'attention_needed': self.attention_needed,
            'envy_nova': self.envy_nova,
            'guilt_husband': self.guilt_husband,
            'loneliness': self.loneliness,
            'vulnerability': self.vulnerability
        })
