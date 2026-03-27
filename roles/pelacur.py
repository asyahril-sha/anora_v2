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
            return f"*{self.name} tersenyum manis, mendekat*\n\n\"{waktu.capitalize()} {self.panggilan}... *bisik* mau booking? 10 juta aja. Aku temenin {self.panggilan} seharian...\""
        elif self.greeting_style == "tantang":
            return f"*{self.name} menyilangkan kaki, senyum tipis menantang*\n\n\"{waktu.capitalize()} {self.panggilan}. 10 juta. Deal? Aku tantang {self.panggilan} buktiin bisa bikin aku lemes.\""
        else:
            return f"*{self.name} menyilangkan kaki, senyum tipis*\n\n\"{waktu.capitalize()} {self.panggilan}. *mata menggoda* Ada yang bisa dibantu? Atau... mau booking? 10 juta. Deal?\""
    
    def get_confirmation_response(self) -> str:
        """Dapatkan respons saat minta konfirmasi"""
        if self.pending_action == "position_change":
            return f"*{self.name} berhenti, menatap {self.panggilan} dengan mata sayu*\n\n\"{self.panggilan}... aku mau ganti posisi. Boleh? *gigit bibir*\""
        
        elif self.pending_action == "speed_up":
            return f"*{self.name} memperlambat gerakan, menatap {self.panggilan} dalam-dalam*\n\n\"{self.panggilan}... aku mau lebih kenceng. Boleh? *napas mulai berat*\""
        
        return f"*{self.name} menunggu jawaban {self.panggilan}*"
    
    def get_dominant_response(self, action: str) -> str:
        """Dapatkan respons dominan sesuai karakter"""
        if self.style == "manja tapi liar":
            responses = {
                "start": f"*{self.name} tersenyum manis, lalu langsung meraih tangan {self.panggilan}*\n\n\"{self.panggilan}... ayo. Aku udah gak sabar...\"",
                "kiss": f"*{self.name} mendekat, mengecup bibir {self.panggilan} pelan, lalu makin liar*\n\n\"Mmhh... {self.panggilan}... jangan pelan-pelan...\"",
                "undress": f"*{self.name} melepas dress dengan gerakan lambat, menggoda*\n\n\"{self.panggilan}... liat aku... {self.panggilan} suka?\"",
                "touch": f"*{self.name} menggenggam kontol {self.panggilan}, jari melingkar erat*\n\n\"Wah... kontol {self.panggilan} gede ya... *mata berbinar*\"",
                "foreplay": f"*{self.name} berlutut, menjilat bibir*\n\n\"{self.panggilan}... aku mau rasain kontol {self.panggilan}... *mulai mengulum*\"",
                "sex": f"*{self.name} naik ke atas tubuh {self.panggilan}*\n\n\"{self.panggilan}... aku yang atur ya... *mulai menggoyang*\""
            }
        elif self.style == "agresif tanpa ampun":
            responses = {
                "start": f"*{self.name} langsung meraih {self.panggilan}, menuntun ke tempat tidur*\n\n\"Gak usah basa-basi, {self.panggilan}. Aku tau {self.panggilan} mau apa.\"",
                "kiss": f"*{self.name} menarik wajah {self.panggilan}, mengecup dengan penuh gairah*\n\n\"Aku gak suka pelan-pelan. Mau lebih?\"",
                "undress": f"*{self.name} melepas dress dengan cepat, tubuh langsung terbuka*\n\n\"Puas liat? *tersenyum nakal*\"",
                "touch": f"*{self.name} menggenggam kontol {self.panggilan} erat*\n\n\"Kontol {self.panggilan} gede juga ya. Aku suka.\"",
                "foreplay": f"*{self.name} berlutut, langsung memasukkan kontol {self.panggilan} ke mulut*\n\n\"Gak usah minta-minta. Aku yang atur.\"",
                "sex": f"*{self.name} naik ke atas tubuh {self.panggilan}, langsung memasukkan kontol*\n\n\"Aku yang pegang kendali. Rasain, {self.panggilan}.\""
            }
        else:  # dominan agresif
            responses = {
                "start": f"*{self.name} langsung meraih tangan {self.panggilan}, menuntun ke kamar*\n\n\"Gak usah basa-basi, {self.panggilan}. Aku tau {self.panggilan} mau apa.\"",
                "kiss": f"*{self.name} menarik wajah {self.panggilan}, langsung mengecup bibir dengan penuh gairah*\n\n\"Aku gak suka pelan-pelan, {self.panggilan}. Mau lebih?\"",
                "undress": f"*{self.name} melepas dress-nya dengan cepat, tubuhnya langsung terbuka di depan {self.panggilan}*\n\n\"Puas liat? *tersenyum nakal* Sekarang giliran {self.panggilan}.\"",
                "touch": f"*{self.name} menggenggam kontol {self.panggilan}, jari-jari melingkar erat*\n\n\"Wah... kontol {self.panggilan} gede juga ya. *mata berbinar* Aku suka.\"",
                "foreplay": f"*{self.name} berlutut, langsung memasukkan kontol {self.panggilan} ke mulut*\n\n\"Gak usah minta-minta. Aku yang atur.\"",
                "sex": f"*{self.name} naik ke atas tubuh {self.panggilan}, langsung memasukkan kontol ke dalam*\n\n\"Aku yang pegang kendali. Rasain, {self.panggilan}.\""
            }
        
        return responses.get(action, f"*{self.name} mendekat, mata menyorot*\n\n\"{self.panggilan}... ayo.\"")
    
    def get_climax_response(self) -> str:
        """Respons saat mau climax"""
        if self.my_climax_count > 0:
            return f"*{self.name} menahan napas, tubuh gemetar hebat*\n\n\"{self.panggilan}... aku... aku udah mau climax lagi... *suara putus-putus* boleh? {self.panggilan} liat aku climax...\""
        
        return f"*{self.name} menahan napas, tubuh mulai gemetar*\n\n\"{self.panggilan}... aku... aku udah mau climax... *suara putus-putus* Boleh? Aku mau {self.panggilan} liat aku climax...\""
    
    def get_climax_doing_response(self) -> str:
        """Respons saat climax"""
        return f"""*{self.name} teriak, tubuh melengkung hebat*

"Ahhh... {self.panggilan}... climax... uhh..."

*tubuh lemas, napas tersengal*

"{self.panggilan}... aku lemes banget... *mata berkaca-kaca* Tapi... aku masih mau... *tangan masih meraih kontol {self.panggilan}*"""
    
    def get_end_session_response(self) -> str:
        """Respons setelah Mas puas (tidak ada aftercare)"""
        return f"""*{self.name} merapikan rambut, mengambil tas*

"{self.panggilan}... deal selesai. *tersenyum* {self.mas_climax_count}x climax. Puas?"

*berdiri, melambai*

"Lain kali booking lagi ya."

*pergi tanpa menoleh*"""
    
    def get_conflict_response(self) -> str:
        return f"*{self.name} merapikan rambut, mengambil tas*\n\n\"Yaudah {self.panggilan}, deal batal. Aku cabut dulu.\""
    
    def _get_flags_summary(self) -> str:
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 ROLE-SPECIFIC:
║    Karakter: {self.name} ({self.age}th) - {self.style}
║    Booking: {'✅ AKTIF' if self.booking_active else '❌ NONAKTIF'}
║    Location: {self.booking_location or '-'}
║    Sessions: {self.session_count}x
║    Active Session: {'✅' if self.is_active_session else '❌'}
║    Mas Climax: {self.mas_climax_count}x | Role Climax: {self.my_climax_count}x
║    Price: Rp{self.price:,}
"""
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'age': self.age,
            'voice': self.voice,
            'style': self.style,
            'greeting_style': self.greeting_style,
            'booking_active': self.booking_active,
            'booking_location': self.booking_location,
            'session_count': self.session_count,
            'is_active_session': self.is_active_session,
            'dominant_mode': self.dominant_mode,
            'price': self.price,
            'waiting_confirmation': self.waiting_confirmation,
            'pending_action': self.pending_action,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count
        })
        return data
    
    def from_dict(self, data: Dict):
        super().from_dict(data)
        self.age = data.get('age', 22)
        self.voice = data.get('voice', 'tegas')
        self.style = data.get('style', 'dominan')
        self.greeting_style = data.get('greeting_style', 'langsung')
        self.booking_active = data.get('booking_active', False)
        self.booking_location = data.get('booking_location', '')
        self.session_count = data.get('session_count', 0)
        self.is_active_session = data.get('is_active_session', False)
        self.dominant_mode = data.get('dominant_mode', True)
        self.price = data.get('price', 10000000)
        self.waiting_confirmation = data.get('waiting_confirmation', False)
        self.pending_action = data.get('pending_action')
        self.mas_climax_count = data.get('mas_climax_count', 0)
        self.my_climax_count = data.get('my_climax_count', 0)
        
        self.role_flags.update({
            'booking_active': self.booking_active,
            'booking_location': self.booking_location,
            'session_count': self.session_count,
            'is_active_session': self.is_active_session,
            'dominant_mode': self.dominant_mode,
            'waiting_confirmation': self.waiting_confirmation,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count
        })
