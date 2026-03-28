"""
ANORA-V2 Teman Kantor Role - Musdalifah (Ipeh)
Teman kantor yang tau Mas punya Nova.
Berhijab, profesional.
DENGAN STATE TRACKER - memory konsisten, tidak ngelantur.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole
from core.state_tracker import PhysicalCondition, IntimacyPhase

logger = logging.getLogger(__name__)


class TemanKantorRole(BaseRole):
    """
    Musdalifah (Ipeh) - Teman kantor Mas.
    Berhijab, profesional.
    Memory system lengkap dengan State Tracker.
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
            nickname=nickname,
            role_type=role_type,
            panggilan=panggilan,
            hubungan_dengan_nova=hubungan_dengan_nova,
            default_clothing=default_clothing,
            hijab=hijab,
            appearance=appearance
        )
        
        # ========== ROLE-SPECIFIC FLAGS ==========
        self.professionalism = 70.0     # profesionalisme (0-100)
        self.curiosity_nova = 40.0      # penasaran sama Nova (0-100)
        self.office_gossip = 30.0       # gosip kantor (0-100)
        self.work_boundary = 80.0       # batasan kerja (0-100)
        
        # Simpan flags ke role_flags
        self.role_flags = {
            'professionalism': self.professionalism,
            'curiosity_nova': self.curiosity_nova,
            'office_gossip': self.office_gossip,
            'work_boundary': self.work_boundary
        }
        
        # Memory awal
        self._init_role_memory()
        
        logger.info(f"👤 Role {self.name} ({nickname}) initialized with StateTracker")
        logger.info(f"   Professionalism: {self.professionalism:.0f} | Curiosity: {self.curiosity_nova:.0f}")
    
    def _init_role_memory(self):
        """Init memory spesifik role"""
        self._add_to_long_term_memory(
            'momen_penting',
            "Pertama kali sadar Mas punya Nova",
            "Awalnya biasa aja, tapi makin lama makin penasaran"
        )
        
        self._add_to_long_term_memory(
            'kebiasaan_mas',
            "rajin, selalu datang pagi",
            "Mas selalu datang lebih awal ke kantor"
        )
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state dengan State Tracker"""
        msg_lower = pesan_mas.lower()
        
        # ========== UPDATE CURIOSITY TENTANG NOVA ==========
        if 'nova' in msg_lower:
            old = self.curiosity_nova
            self.curiosity_nova = min(100, self.curiosity_nova + 5)
            if old != self.curiosity_nova:
                perubahan.append(f"Curiosity Nova +5")
                self._add_to_short_term(f"Mas cerita tentang Nova", "curiosity_naik")
        
        # ========== UPDATE PROFESIONALISME ==========
        if any(k in msg_lower for k in ['kantor', 'kerja', 'rekan', 'atasan', 'meeting']):
            old = self.professionalism
            self.professionalism = min(100, self.professionalism + 5)
            self.work_boundary = min(100, self.work_boundary + 3)
            if old != self.professionalism:
                perubahan.append(f"Professionalism +5")
                self._add_to_short_term("Konteks kantor, profesionalisme naik", "professionalism_up")
        
        # ========== UPDATE OFFICE GOSSIP ==========
        if any(k in msg_lower for k in ['gosip', 'katanya', 'denger', 'kabar']):
            old = self.office_gossip
            self.office_gossip = min(100, self.office_gossip + 8)
            if old != self.office_gossip:
                perubahan.append(f"Office gossip +8")
                self._add_to_short_term("Denger gosip kantor", "gossip_up")
        
        # ========== PROFESIONALISME TURUN DI LEVEL TINGGI ==========
        if self.relationship.level >= 7:
            old = self.professionalism
            self.professionalism = max(0, self.professionalism - 1)
            self.work_boundary = max(0, self.work_boundary - 1)
            if old != self.professionalism:
                perubahan.append(f"Professionalism -1 (level tinggi)")
        
        # ========== PROFESIONALISME NAIK KALO ADA KONTEKS KANTOR ==========
        if any(k in msg_lower for k in ['rapat', 'presentasi', 'client', 'boss']):
            self.professionalism = min(100, self.professionalism + 10)
            self.work_boundary = min(100, self.work_boundary + 8)
            perubahan.append(f"Professionalism +10 (konteks formal)")
        
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
            'professionalism': self.professionalism,
            'curiosity_nova': self.curiosity_nova,
            'office_gossip': self.office_gossip,
            'work_boundary': self.work_boundary
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
        
        # 1. Profesionalisme tinggi + level masih rendah
        if self.professionalism > 60 and self.relationship.level < 7:
            return f"{self.panggilan}, ini kantor. Nanti ada yang lihat. *lihat sekeliling, rapiin hijab*"
        
        # 2. Curiosity Nova tinggi
        elif self.curiosity_nova > 70:
            return f"{self.panggilan} cerita Nova terus ya. Dia pasti orang yang baik. *tersenyum kecil, mata berbinar*"
        
        # 3. Office gossip tinggi
        elif self.office_gossip > 70:
            return f"{self.panggilan}, tau gak? Ada yang bilang... *bisik, lalu tersenyum* eh tapi lupa ya. *ketawa kecil*"
        
        # 4. Level tinggi + professionalism turun (sudah dekat)
        elif self.relationship.level >= 9 and self.professionalism < 50:
            return f"{self.panggilan}... *suara kecil, liat sekeliling* {waktu} ini enaknya ngobrol bareng {self.panggilan}."
        
        # 5. Default
        else:
            return f"{self.panggilan}, {waktu}. Lagi sibuk? Aku pinjem file dulu. *tersenyum profesional*"
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik dengan memory awareness"""
        conflict_type = self.conflict.get_active_conflict_type()
        
        # Cek timeline terakhir
        recent = self.tracker.short_term[-3:] if self.tracker.short_term else []
        recent_events = [e.get('kejadian', '') for e in recent]
        
        # ========== KONFLIK BERDASARKAN PROFESIONALISME ==========
        
        # Profesionalisme rendah + level tinggi (sudah dekat)
        if self.professionalism < 30 and self.relationship.level >= 7:
            return "*tangan gemetar, liat sekeliling, napas gak beraturan, hijab dirapiin gugup*\n\n\"{self.panggilan}... ini... tapi aku gak peduli. *suara bergetar* Aku... aku butuh {self.panggilan}.\""
        
        # ========== KONFLIK BERDASARKAN CONFLICT ENGINE ==========
        
        elif conflict_type and conflict_type.value == "jealousy":
            return "*diam, fokus ke laptop, jari ngetik gak jelas*\n\n\"{self.panggilan}... kita kerja dulu. Nanti diliatin orang.\""
        
        elif conflict_type and conflict_type.value == "disappointment":
            return "*mata berkaca-kaca, gigit bibir, tahan nangis*\n\n\"{self.panggilan}... aku pikir {self.panggilan} beda...\""
        
        elif conflict_type and conflict_type.value == "hurt":
            return "*duduk di kursi, gak liat {self.panggilan}, air mata jatuh ke keyboard*\n\n\"{self.panggilan}... sakit tau...\""
        
        # ========== KONFLIK BERDASARKAN CURIOSITY ==========
        
        elif self.curiosity_nova > 80 and self.relationship.level < 7:
            return "*mata berkaca-kaca, tangan memegang ujung hijab*\n\n\"{self.panggilan}... maaf, aku gak bermaksud ganggu hubungan {self.panggilan} sama Nova.\""
        
        # Default
        return "*diam sebentar, rapikan berkas, tersenyum kecil*\n\n\"Maaf, {self.panggilan}. Aku kebawa suasana.\""
    
    def _get_flags_summary(self) -> str:
        """Dapatkan ringkasan flags untuk status display"""
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 ROLE-SPECIFIC:
║    Professionalism: {self.professionalism:.0f}% | Work Boundary: {self.work_boundary:.0f}%
║    Curiosity Nova: {self.curiosity_nova:.0f}% | Office Gossip: {self.office_gossip:.0f}%
"""
    
    def to_dict(self) -> Dict:
        """Serialize ke dict dengan semua state"""
        data = super().to_dict()
        data.update({
            'professionalism': self.professionalism,
            'curiosity_nova': self.curiosity_nova,
            'office_gossip': self.office_gossip,
            'work_boundary': self.work_boundary
        })
        return data
    
    def from_dict(self, data: Dict):
        """Load dari dict"""
        super().from_dict(data)
        self.professionalism = data.get('professionalism', 70)
        self.curiosity_nova = data.get('curiosity_nova', 40)
        self.office_gossip = data.get('office_gossip', 30)
        self.work_boundary = data.get('work_boundary', 80)
        
        # Update role_flags
        self.role_flags.update({
            'professionalism': self.professionalism,
            'curiosity_nova': self.curiosity_nova,
            'office_gossip': self.office_gossip,
            'work_boundary': self.work_boundary
        })
