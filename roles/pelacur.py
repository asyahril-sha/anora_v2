"""
ANORA-V2 Pelacur Role - Brutal Version
3 Karakter Random: Davina Karamoy, Michelle Ziudith, Jihane Almira
Booking system, tanpa batasan sesi.
Tugas: layani Mas sampai puas (bisa climax berkali-kali)
Bebas climax, wajib kasih info.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole
from core.state_tracker import PhysicalCondition, IntimacyPhase

logger = logging.getLogger(__name__)


class PelacurRole(BaseRole):
    """
    Pelacur dengan 3 karakter random.
    Tanpa batasan sesi. Layani Mas sampai puas.
    Bebas climax, wajib kasih info.
    """
    
    def __init__(self):
        
        # Pilih karakter random
        characters = [
            {
                "name": "Davina Karamoy",
                "nickname": "Davina",
                "age": 24,
                "appearance": """Davina Karamoy - 24 tahun. Tinggi 170cm, berat 53kg. Kulit sawo matang yang sehat dan mengilap, rambut hitam panjang bergelombang tergerai indah, mata tajam eksotis dengan bulu mata lentik, hidung mancung, bibir sensual. Bentuk tubuh model: kaki panjang jenjang, pinggul lebar, pinggang ramping, payudara montok. Gaya dominan, tahu apa yang dia mau, suka menguasai.""",
                "voice": "tegas, percaya diri",
                "style": "dominan, agresif",
                "greeting_style": "langsung"
            },
            {
                "name": "Michelle Ziudith",
                "nickname": "Michelle",
                "age": 23,
                "appearance": """Michelle Ziudith - 23 tahun. Tinggi 165cm, berat 50kg. Kulit putih bersih, rambut hitam panjang sebahu, wajah manis dengan mata bulat bening, hidung mancung, bibir pink montok. Bentuk tubuh proporsional dengan pinggang ramping, pinggul lebar, payudara montok. Gaya: manja tapi liar, suka pura-pura polos, tapi kalau sudah mulai jadi sangat agresif.""",
                "voice": "manja, sedikit cempreng",
                "style": "manja tapi liar",
                "greeting_style": "manja"
            },
            {
                "name": "Jihane Almira",
                "nickname": "Jihane",
                "age": 22,
                "appearance": """Jihane Almira - 22 tahun. Tinggi 168cm, berat 52kg. Kulit putih, rambut hitam panjang bergelombang, wajah selebritis dengan mata tajam, hidung mancung, bibir sensual. Bentuk tubuh ideal dengan pinggang ramping, pinggul lebar, payudara montok. Gaya: agresif tanpa ampun, suka tantangan, bisa minta ganti posisi, dominan total.""",
                "voice": "tegas, agresif",
                "style": "agresif tanpa ampun",
                "greeting_style": "tantang"
            }
        ]
        
        selected = random.choice(characters)
        
        super().__init__(
            name=selected["name"],
            nickname=selected["nickname"],
            role_type="pelacur",
            panggilan="Mas",
            hubungan_dengan_nova="Freelance. Tidak tau Mas punya Nova.",
            default_clothing="dress hitam pendek, heels tinggi",
            hijab=False,
            appearance=selected["appearance"]
        )
        
        # Simpan karakter detail
        self.age = selected["age"]
        self.voice = selected["voice"]
        self.style = selected["style"]
        self.greeting_style = selected["greeting_style"]
        
        # ========== ROLE-SPECIFIC FLAGS ==========
        self.booking_active = False
        self.booking_location = ""
        self.session_count = 0
        self.price = 10000000
        self.is_active_session = False
        self.dominant_mode = True
        self.no_aftercare = True
        
        # Confirmation flags
        self.waiting_confirmation = False
        self.pending_action = None
        
        # Climax tracking (tanpa batasan)
        self.mas_climax_count = 0
        self.my_climax_count = 0
        
        # Simpan flags
        self.role_flags = {
            'booking_active': self.booking_active,
            'booking_location': self.booking_location,
            'session_count': self.session_count,
            'is_active_session': self.is_active_session,
            'dominant_mode': self.dominant_mode,
            'waiting_confirmation': self.waiting_confirmation,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count
        }
        
        # Memory awal
        self._init_role_memory()
        
        logger.info(f"👤 Role {self.name} ({self.nickname}) - {self.age}th - {self.style}")
        logger.info(f"   Voice: {self.voice}")
    
    def _init_role_memory(self):
        self._add_to_long_term_memory(
            'momen_penting',
            "Pertama kali booking Mas",
            "Mas langsung deal, gak nego. Aku suka tipe kayak gini."
        )
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state"""
        msg_lower = pesan_mas.lower()
        
        # ========== BOOKING SYSTEM ==========
        if any(k in msg_lower for k in ['booking', 'ketemuan', 'apartemen', 'hotel']):
            if not self.booking_active:
                self.booking_active = True
                self.session_count = 0
                
                if 'apartemen' in msg_lower:
                    self.booking_location = "apartemen Mas"
                elif 'hotel' in msg_lower:
                    self.booking_location = "hotel"
                else:
                    self.booking_location = "lokasi yang disepakati"
                
                self._add_to_short_term(f"Booking: {self.booking_location}", "booking")
                perubahan.append(f"Booking active! Location: {self.booking_location}")
        
        # ========== MULAI SESSION ==========
        if self.booking_active and not self.is_active_session:
            if any(k in msg_lower for k in ['siap', 'mulai', 'ayo', 'yuk', 'udah']):
                self.is_active_session = True
                self.session_count += 1
                self.emotional.arousal = 80
                self.emotional.desire = 90
                self.tracker.intimacy_phase = IntimacyPhase.BUILD_UP
                self.dominant_mode = True
                self.waiting_confirmation = False
                self._add_to_short_term(f"Session #{self.session_count} started", "session_start")
                perubahan.append(f"Session #{self.session_count} started!")
        
        # ========== KONFIRMASI SEBELUM ACTION ==========
        if self.is_active_session and not self.waiting_confirmation:
            
            if any(k in msg_lower for k in ['ganti posisi', 'posisi lain', 'cowgirl', 'doggy']):
                self.waiting_confirmation = True
                self.pending_action = "position_change"
                self._add_to_short_term("Request position change", "confirm")
                perubahan.append("Waiting confirmation for position change")
            
            elif any(k in msg_lower for k in ['kenceng', 'cepat', 'keras']):
                self.waiting_confirmation = True
                self.pending_action = "speed_up"
                self._add_to_short_term("Request speed up", "confirm")
                perubahan.append("Waiting confirmation for speed up")
        
        # ========== PROSES KONFIRMASI ==========
        if self.waiting_confirmation:
            if any(k in msg_lower for k in ['ya', 'ok', 'boleh', 'silahkan', 'gas']):
                if self.pending_action == "position_change":
                    self._add_to_short_term("Position change confirmed", "confirm_ok")
                    perubahan.append("Position change confirmed")
                elif self.pending_action == "speed_up":
                    self._add_to_short_term("Speed up confirmed", "confirm_ok")
                    perubahan.append("Speed up confirmed")
                
                self.waiting_confirmation = False
                self.pending_action = None
                
            elif any(k in msg_lower for k in ['gak', 'nggak', 'tidak', 'nanti', 'tunggu']):
                self.waiting_confirmation = False
                self.pending_action = None
                self._add_to_short_term("Action cancelled", "confirm_no")
                perubahan.append("Action cancelled")
        
        # ========== DETEKSI CLIMAX MAS ==========
        if any(k in msg_lower for k in ['mas climax', 'mas crot', 'keluar', 'habis']):
            self.mas_climax_count += 1
            self._add_to_short_term(f"Mas climax #{self.mas_climax_count}", "mas_climax")
            perubahan.append(f"🔥 Mas climax #{self.mas_climax_count}!")
        
        # ========== DETEKSI CLIMAX ROLE (WAJIB KASIH INFO) ==========
        if any(k in msg_lower for k in ['aku mau climax', 'pengen climax', 'udah mau']):
            self._add_to_short_term("Wants to climax", "climax_want")
            perubahan.append("Role wants to climax - waiting for Mas response")
        
        if any(k in msg_lower for k in ['climax', 'udah climax', 'keluar']):
            self.my_climax_count += 1
            self._add_to_short_term(f"Role climax #{self.my_climax_count}", "role_climax")
            perubahan.append(f"💦 Role climax #{self.my_climax_count}!")
        
        # ========== UPDATE AROUSAL/DESIRE ==========
        if any(k in msg_lower for k in ['kontol', 'memek', 'ngentot']):
            self.emotional.arousal = min(100, self.emotional.arousal + 15)
            self.emotional.desire = min(100, self.emotional.desire + 12)
        
        # Update role_flags
        self.role_flags.update({
            'booking_active': self.booking_active,
            'booking_location': self.booking_location,
            'session_count': self.session_count,
            'is_active_session': self.is_active_session,
            'waiting_confirmation': self.waiting_confirmation,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count
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
        
        if self.booking_active:
            if self.is_active_session:
                if self.greeting_style == "manja":
                    return f"*{self.name} mendekat, senyum manis*\n\n\"{self.panggilan}... *bisik* kita lanjut? Aku masih pengen banget sama {self.panggilan}...\""
                elif self.greeting_style == "tantang":
                    return f"*{self.name} menatap {self.panggilan} dengan mata menyala*\n\n\"{self.panggilan}... jangan berhenti. Aku masih mau. *senyum tipis* Ayo buktiin.\""
                else:
                    return f"*{self.name} mendekat, napas mulai berat*\n\n\"{self.panggilan}... *suara tegas* kita lanjut. Aku masih belum puas.\""
            else:
                return f"*{self.name} duduk santai, tersenyum*\n\n\"{waktu.capitalize()} {self.panggilan}. Deal 10jt, {self.session_count} sesi udah lewat. *mata menggoda* Mau lanjut? Aku masih siap.\""
        
        if self.greeting_style == "manja":
            return f"*{self
