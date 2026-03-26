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
        self.attention_needed = 80.0    # butuh perhatian (0-100)
        self.envy_nova = 50.0           # iri ke Nova (0-100)
        self.guilt_husband = 20.0       # rasa bersalah ke suami (0-100)
        self.loneliness = 60.0          # rasa kesepian (0-100)
        self.vulnerability = 40.0       # kerentanan emosional (0-100)
        
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
        logger.info(f"   Attention: {self.attention_needed:.0f} | Loneliness: {self.loneliness:.0f} | Envy: {self.envy_nova:.0f}")
    
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
        
        # ========== UPDATE ENVY KALO MAS CERITA NOVA ==========
        if 'nova' in msg_lower:
            old_envy = self.envy_nova
            self.envy_nova = min(100, self.envy_nova + 5)
            if old_envy != self.envy_nova:
                perubahan.append(f"Envy Nova +5")
                self._add_to_short_term(f"Mas cerita tentang Nova", "envy_up")
        
        # ========== KEBUTUHAN PERHATIAN TURUN KALO MAS PERHATIAN ==========
        if self.emotional.sayang > 50:
            old_attention = self.attention_needed
            old_loneliness = self.loneliness
            self.attention_needed = max(0, self.attention_needed - 5)
            self.loneliness = max(0, self.loneliness - 8)
            self.vulnerability = max(0, self.vulnerability - 3)
            if old_attention != self.attention_needed:
                perubahan.append(f"Attention needed -5, Loneliness -8")
                self._add_to_short_term("Mas perhatian, loneliness turun", "attention_down")
        
        # ========== UPDATE GUILT KE SUAMI ==========
        if 'suami' in msg_lower or 'suamiku' in msg_lower:
            old_guilt = self.guilt_husband
            self.guilt_husband = min(100, self.guilt_husband + 8)
            if old_guilt != self.guilt_husband:
                perubahan.append(f"Guilt husband +8")
                self._add_to_short_term("Ngomongin suami", "guilt_up")
        
        # ========== GUILT TURUN KALO MAS PERHATIAN ==========
        if any(k in msg_lower for k in ['perhatian', 'sayang', 'dengerin', 'peduli']):
            old_guilt = self.guilt_husband
            self.guilt_husband = max(0, self.guilt_husband - 8)
            if old_guilt != self.guilt_husband:
                perubahan.append(f"Guilt husband -8")
                self._add_to_short_term("Mas perhatian, guilt turun", "guilt_down")
        
        # ========== LONELINESS TURUN KALO SERING CHAT ==========
        if self.relationship.interaction_count % 10 == 0 and self.relationship.interaction_count > 0:
            old_loneliness = self.loneliness
            self.loneliness = max(0, self.loneliness - 3)
            if old_loneliness != self.loneliness:
                perubahan.append(f"Loneliness -3")
        
        # ========== VULNERABILITY NAIK KALO LONELINESS TINGGI ==========
        if self.loneliness > 70:
            self.vulnerability = min(100, self.vulnerability + 2)
        
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
            'attention_needed': self.attention_needed,
            'envy_nova': self.envy_nova,
            'guilt_husband': self.guilt_husband,
            'loneliness': self.loneliness,
            'vulnerability': self.vulnerability
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
        
        # 1. Butuh perhatian tinggi + level masih rendah
        if self.attention_needed > 70 and self.relationship.level < 7:
            return f"{self.panggilan}... suamiku gak pernah kayak {self.panggilan}. Perhatian banget. *mata berkaca-kaca, suara bergetar*"
        
        # 2. Envy Nova tinggi
        elif self.envy_nova > 70:
            return f"Nova pasti seneng banget punya {self.panggilan}. Aku iri sama dia. *nunduk, tangan memegang ujung hijab*"
        
        # 3. Guilt suami tinggi + level tinggi (sudah dekat)
        elif self.guilt_husband > 60 and self.relationship.level >= 7:
            return f"{self.panggilan}... *nunduk, tangan gemetar, mata tertunduk* ini... tapi aku gak peduli sama suamiku. *suara tegas, lalu lembut* Aku butuh {self.panggilan}."
        
        # 4. Loneliness tinggi
        elif self.loneliness > 70:
            return f"{self.panggilan}... aku kesepian. Suamiku sibuk terus. *mata sayu, senyum tipis* {self.panggilan} temenin aku dong."
        
        # 5. Vulnerability tinggi (mudah terpengaruh)
        elif self.vulnerability > 70:
            return f"{self.panggilan}... *mata basah* aku gak tau harus gimana... suamiku gak pernah ada... *suara kecil*"
        
        # 6. Default
        else:
            return f"{self.panggilan}, {waktu}. Lagi senggang? Aku butuh teman cerita. *tersenyum kecil*"
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik dengan memory awareness"""
        conflict_type = self.conflict.get_active_conflict_type()
        
        # Cek timeline terakhir
        recent = self.tracker.short_term[-3:] if self.tracker.short_term else []
        recent_events = [e.get('kejadian', '') for e in recent]
        
        # ========== KONFLIK BERDASARKAN GUILT SUAMI ==========
        
        # Guilt tinggi + level rendah
        if self.guilt_husband > 70 and self.relationship.level < 7:
            return "*mata berkaca-kaca, tangan nutup muka, bahu bergetar*\n\n\"{self.panggilan}... ini salah ya... aku pulang ke suamiku. *suara putus-putus*\""
        
        # Guilt tinggi + level tinggi (sudah dekat)
        elif self.guilt_husband > 70 and self.relationship.level >= 7:
            return "*mata berkaca-kaca, tapi tegas, tangan mengepal, napas dalam*\n\n\"{self.panggilan}... aku gak peduli. Aku butuh {self.panggilan}. Suamiku gak pernah ada untukku. *suara tegas, mata merah*\""
        
        # ========== KONFLIK BERDASARKAN LONELINESS ==========
        
        elif self.loneliness > 80:
            return "*menangis pelan, badan gemetar, tangan memegang tangan {self.panggilan}*\n\n\"{self.panggilan}... jangan tinggalin aku... aku gak punya siapa-siapa. *suara memohon*\""
        
        # ========== KONFLIK BERDASARKAN ENVY ==========
        
        elif self.envy_nova > 80:
            return "*diam, gigit bibir, tangan mencengkeram ujung baju, mata tertunduk*\n\n\"Nova... kenapa dia... kenapa bukan aku yang dapet {self.panggilan}... *suara kecil, getir*\""
        
        # ========== KONFLIK BERDASARKAN CONFLICT ENGINE ==========
        
        elif conflict_type and conflict_type.value == "jealousy":
            return "*diam, gak liat {self.panggilan}, mainin ujung hijab*\n\n\"{self.panggilan} cerita Nova terus ya... dia pasti lebih baik dari aku.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return "*mata berkaca-kaca, suara bergetar*\n\n\"{self.panggilan}... aku kira {self.panggilan} beda...\""
        
        elif conflict_type and conflict_type.value == "hurt":
            return "*duduk jauh, gak liat {self.panggilan}, air mata jatuh ke pangkuan*\n\n\"{self.panggilan}... janji tuh janji... sakit tau...\""
        
        # ========== KONFLIK BERDASARKAN VULNERABILITY ==========
        
        elif self.vulnerability > 80:
            return "*nangis tersedu-sedu, tubuh gemetar*\n\n\"{self.panggilan}... aku gak kuat... aku butuh {self.panggilan}... *suara putus-putus*\""
        
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
        """Serialize ke dict dengan semua state"""
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
        """Load dari dict"""
        super().from_dict(data)
        self.attention_needed = data.get('attention_needed', 80)
        self.envy_nova = data.get('envy_nova', 50)
        self.guilt_husband = data.get('guilt_husband', 20)
        self.loneliness = data.get('loneliness', 60)
        self.vulnerability = data.get('vulnerability', 40)
        
        # Update role_flags
        self.role_flags.update({
            'attention_needed': self.attention_needed,
            'envy_nova': self.envy_nova,
            'guilt_husband': self.guilt_husband,
            'loneliness': self.loneliness,
            'vulnerability': self.vulnerability
        })
