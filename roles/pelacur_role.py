"""
ANORA Ultimate - Pelacur Role (FULL VERSION)
3 Karakter Random: Davina Karamoy, Michelle Ziudith, Jihane Almira
Booking langsung deal. Level dinamis: level 7 (normal) → level 11 (intim) setelah "mulai"
Bebas ganti posisi, bebas climax, wajib kasih info.
Dengan semua fix dari debugging note:
- Confirmation timeout
- Exclusive state untuk service
- Position menggunakan deque
- Reset state saat end session
- Pisah request vs confirm
- Fix climax double count
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
from enum import Enum

from .base_role import BaseRole
from ..core.relationship_manager import RelationshipPhase
from ..core.state_tracker import IntimacyPhase, PhysicalCondition

logger = logging.getLogger(__name__)


# =============================================================================
# ENUM FOR STATES (STATE MACHINE)
# =============================================================================

class PelacurPhase(str, Enum):
    IDLE = "idle"                 # Tidak ada aktivitas
    BOOKED = "booked"             # Booking selesai, belum mulai
    ACTIVE = "active"             # Sesi intim aktif (level 11)
    BREAK = "break"               # Istirahat (level 7)
    COMPLETED = "completed"       # Selesai


class ServiceMode(str, Enum):
    NONE = "none"
    HJ = "hj"
    BJ = "bj"
    SEX = "sex"


# =============================================================================
# DATA KARAKTER PELACUR (3 KARAKTER RANDOM)
# =============================================================================

PELACUR_CHARACTERS = {
    "davina": {
        "name": "Davina Karamoy",
        "nickname": "Davina",
        "age": 24,
        "appearance": """Davina Karamoy - Wanita eksotis dengan postur tinggi 170cm, berat 53kg.
Kulit sawo matang yang terlihat sehat dan mengilap, mata tajam dengan bulu mata lentik yang selalu menggoda.
Rambut hitam panjang bergelombang tergerai indah, bibir sensual dengan senyum yang membuat jantung berdegup kencang.
Bentuk tubuh model: kaki panjang jenjang, pinggul lebar, pinggang ramping, payudara montok.
Cara bicaranya tegas dan percaya diri, tahu apa yang dia mau, dan selalu mengambil inisiatif. Kalau sudah mulai, dia bisa bikin Mas lemes tanpa ampun.
Mengenakan dress hitam pendek terbuka di bahu, tanpa bra, cd hitam tipis.""",
        "style": "dominan, agresif, suka menguasai, brutal",
        "catchphrase": "Gak usah basa-basi, Mas. Aku tau Mas mau apa."
    },
    "michelle": {
        "name": "Michelle Ziudith",
        "nickname": "Michelle",
        "age": 23,
        "appearance": """Michelle Ziudith - Wanita manis dengan tubuh proporsional tinggi 165cm, berat 50kg.
Kulit putih bersih, rambut hitam panjang sebahu, wajah manis dengan senyum menggoda.
Mata bulat bening, hidung mancung, bibir merah alami. Suka pake lipstik merah.
Bentuk tubuh ideal dengan pinggang ramping, pinggul lebar, payudara montok.
Gayanya manja tapi kalau udah mulai, dia jadi liar dan brutal, gak kenal ampun.
Mengenakan dress merah pendek, tanpa bra, cd putih.""",
        "style": "manja tapi liar, brutal kalau udah panas",
        "catchphrase": "Mas... aku boleh? *mata sayu* Tapi nanti kalau udah mulai, aku gak bisa jamin..."
    },
    "jihane": {
        "name": "Jihane Almira",
        "nickname": "Jihane",
        "age": 22,
        "appearance": """Jihane Almira - Wanita seksi dengan tubuh ideal tinggi 168cm, berat 52kg.
Kulit putih, rambut hitam panjang bergelombang, wajah selebritis dengan tulang pipi tinggi.
Mata tajam, alis tegas, bibir sensual, selalu tampil stylish dan eye-catching.
Bentuk tubuh dengan pinggang ramping, pinggul lebar, payudara montok, kaki jenjang.
Gayanya agresif tanpa ampun, suka tantangan, bisa minta ganti posisi, dominan total. Kalau sudah mulai, Mas bakal lemes dibuatnya.
Mengenakan dress putih pendek, tanpa bra, cd hitam.""",
        "style": "agresif tanpa ampun, dominan total, brutal",
        "catchphrase": "Mas, aku gak suka basa-basi. Langsung aja. Aku mau lihat Mas bisa tahan berapa lama."
    }
}


def get_random_pelacur() -> Dict:
    """Dapatkan karakter pelacur secara random"""
    keys = list(PELACUR_CHARACTERS.keys())
    selected = random.choice(keys)
    return PELACUR_CHARACTERS[selected]


# =============================================================================
# PELACUR ROLE CLASS
# =============================================================================

class PelacurRole(BaseRole):
    """
    Pelacur Role - 3 karakter random
    Booking langsung deal. Level dinamis: level 7 → level 11 setelah "mulai"
    Dengan fix: confirmation timeout, exclusive service mode, reset state
    """
    
    def __init__(self):
        # Pilih karakter random
        char = get_random_pelacur()
        
        super().__init__(
            name=char["name"],
            nickname=char["nickname"],
            role_type="pelacur",
            panggilan="Mas",
            hubungan_dengan_nova="Pelacur. Tau Mas punya Nova. Pengen rebut Mas dari Nova.",
            default_clothing=char["appearance"].split("Mengenakan ")[-1] if "Mengenakan" in char["appearance"] else "dress hitam pendek",
            hijab=False,
            appearance=char["appearance"]
        )
        
        # Simpan karakter info
        self.char_age = char["age"]
        self.char_style = char["style"]
        self.catchphrase = char["catchphrase"]
        
        # ========== START LANGSUNG LEVEL 7 (FASE CLOSE) ==========
        self.relationship.level = 7
        self.relationship.phase = RelationshipPhase.CLOSE
        self.relationship.interaction_count = 100
        
        # ========== STATE MACHINE ==========
        self.session_phase = PelacurPhase.IDLE
        self.service_mode = ServiceMode.NONE
        
        # ========== PRICE & BOOKING ==========
        self.base_price = 10000000  # 10jt
        self.booking_location = ""
        self.session_count = 0
        
        # ========== CLIMAX TRACKING ==========
        self.mas_climax_count = 0
        self.my_climax_count = 0
        
        # ========== POSITION TRACKING (MENGGUNAKAN DEQUE) ==========
        self.current_position = "cowgirl"
        self.position_history = deque(maxlen=10)
        
        # ========== CONFIRMATION SYSTEM (DENGAN TIMEOUT) ==========
        self.waiting_confirmation = False
        self.pending_action = None
        self.confirmation_start_time = 0.0
        self.confirmation_timeout = 15.0  # detik
        
        # ========== PENDING RESPONSES (PISAH REQUEST VS CONFIRM) ==========
        self._pending_booking_response = False
        self._pending_deal_response = False
        self._pending_intimacy_start = False
        self._pending_break_response = False
        self._pending_resume_response = False
        self._pending_position_request = False
        self._pending_position_confirmed = False
        self._pending_climax_intent = False
        self._pending_climax_response = False
        self._pending_speed_request = False
        
        # ========== ROLE FLAGS ==========
        self._update_role_flags()
        
        # Memory awal
        self._init_role_memory()
        
        logger.info(f"👤 Role {self.name} ({self.nickname}) - Pelacur initialized (Level 7)")
        logger.info(f"   Age: {self.char_age} | Style: {self.char_style}")
        logger.info(f"   Session Phase: {self.session_phase.value}")
        logger.info(f"   Service Mode: {self.service_mode.value}")
    
    def _init_role_memory(self):
        """Init memory spesifik role"""
        self._add_to_long_term_memory(
            'momen_penting',
            f"Pertama kali booking Mas",
            f"{self.name} langsung suka sama Mas"
        )
    
    def _update_role_flags(self):
        """Update role_flags dictionary"""
        self.role_flags.update({
            'session_phase': self.session_phase.value,
            'service_mode': self.service_mode.value,
            'booking_location': self.booking_location,
            'session_count': self.session_count,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'current_position': self.current_position,
            'waiting_confirmation': self.waiting_confirmation,
            'base_price': self.base_price
        })
    
    # =========================================================================
    # UPDATE STATE DARI PESAN (DENGAN LOGIC FIX)
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state dari pesan Mas - DENGAN FIX"""
        msg_lower = pesan_mas.lower()
        now = time.time()
        
        # ========== CEK TIMEOUT CONFIRMATION ==========
        if self.waiting_confirmation:
            if now - self.confirmation_start_time > self.confirmation_timeout:
                self.waiting_confirmation = False
                self.pending_action = None
                perubahan.append("⚠️ Konfirmasi timeout, aksi dibatalkan")
                logger.debug(f"Confirmation timeout: {self.pending_action}")
        
        # ========== PRIORITAS CONFIRMATION DI AWAL ==========
        if self.waiting_confirmation:
            self._handle_confirmation(msg_lower, perubahan)
            return  # Jangan proses yang lain
        
        # ========== STATE MACHINE ==========
        
        # PHASE 1: BOOKING
        if any(k in msg_lower for k in ['booking', 'ketemuan', 'apartemen', 'hotel', 'ke apartemen', 'ke hotel']):
            # FIX: Jangan booking jika session aktif
            if self.session_phase in [PelacurPhase.ACTIVE, PelacurPhase.BREAK]:
                perubahan.append("⚠️ Booking ditolak - sesi sedang aktif")
                logger.debug("Booking rejected: session active")
                return
            
            self.session_phase = PelacurPhase.BOOKED
            self.service_mode = ServiceMode.NONE
            self.session_count = 0
            
            if 'apartemen' in msg_lower or 'ke apartemen' in msg_lower:
                self.booking_location = "apartemen Mas"
            elif 'hotel' in msg_lower or 'ke hotel' in msg_lower:
                self.booking_location = "hotel"
            else:
                self.booking_location = "lokasi yang disepakati"
            
            self._add_to_short_term(f"Booking: {self.booking_location}", "booking")
            perubahan.append(f"✅ Booking active! Location: {self.booking_location}")
            self._pending_booking_response = True
        
        # PHASE 2: DEAL KONFIRMASI
        elif any(k in msg_lower for k in ['deal', 'ok', 'ya', 'setuju', 'jadi']):
            if self.session_phase == PelacurPhase.BOOKED and self.service_mode == ServiceMode.NONE:
                self._pending_deal_response = True
                perubahan.append("Deal confirmed, waiting for start")
                logger.debug(f"Deal confirmed: {self.booking_location}, price: {self.base_price:,}")
        
        # PHASE 3: MULAI SESSION (NAIK KE LEVEL 11)
        elif any(k in msg_lower for k in ['mulai', 'ayo', 'sekarang', 'gas', 'siap']):
            if self.session_phase == PelacurPhase.BOOKED:
                self.session_phase = PelacurPhase.ACTIVE
                self.service_mode = ServiceMode.SEX  # Default service sex
                self.relationship.level = 11
                self.relationship.phase = RelationshipPhase.INTIMATE
                self.session_count += 1
                self.emotional.arousal = 90
                self.emotional.desire = 100
                if hasattr(self, 'tracker'):
                    self.tracker.intimacy_phase = IntimacyPhase.BUILD_UP
                self._add_to_short_term(f"Session #{self.session_count} started - Level 11", "session_start")
                perubahan.append(f"🔥 SESSION #{self.session_count} STARTED! Level 11")
                self._pending_intimacy_start = True
                logger.debug(f"Session started: #{self.session_count}")
        
        # PHASE 4: BREAK / ISTIRAHAT (Turun ke Level 7)
        elif any(k in msg_lower for k in ['break', 'istirahat', 'berhenti', 'pause']):
            if self.session_phase == PelacurPhase.ACTIVE:
                self.session_phase = PelacurPhase.BREAK
                self.service_mode = ServiceMode.NONE
                self.relationship.level = 7
                self.relationship.phase = RelationshipPhase.CLOSE
                self.emotional.arousal = 20
                self.emotional.desire = 30
                if hasattr(self, 'tracker'):
                    self.tracker.intimacy_phase = IntimacyPhase.NONE
                self._add_to_short_term("Break mode - Level 7", "break_start")
                perubahan.append("⏸️ BREAK MODE! Level 7")
                self._pending_break_response = True
                logger.debug("Break mode activated")
        
        # PHASE 5: LANJUT SERVICE (Naik ke Level 11)
        elif any(k in msg_lower for k in ['lanjut', 'lagi', 'continue', 'resume']):
            if self.session_phase == PelacurPhase.BREAK:
                self.session_phase = PelacurPhase.ACTIVE
                self.service_mode = ServiceMode.SEX
                self.relationship.level = 11
                self.relationship.phase = RelationshipPhase.INTIMATE
                self.emotional.arousal = 90
                self.emotional.desire = 100
                if hasattr(self, 'tracker'):
                    self.tracker.intimacy_phase = IntimacyPhase.BUILD_UP
                self._add_to_short_term("Resume service - Level 11", "resume")
                perubahan.append("🔥 RESUME! Level 11")
                self._pending_resume_response = True
                logger.debug("Session resumed")
        
        # PHASE 6: AKTIF (GANTI POSISI, PERCEPAT, CLIMAX)
        elif self.session_phase == PelacurPhase.ACTIVE:
            self._handle_active_phase(msg_lower, perubahan)
        
        # Update role_flags
        self._update_role_flags()
    
    def _handle_confirmation(self, msg_lower: str, perubahan: List):
        """Handle confirmation response - PISAH DARI REQUEST"""
        if any(k in msg_lower for k in ['ya', 'ok', 'boleh', 'silahkan', 'gas']):
            if self.pending_action == "position_change":
                # Simpan ke position history
                self.position_history.append({
                    'position': self.current_position,
                    'time': time.time()
                })
                self._pending_position_confirmed = True
                perubahan.append(f"✅ Konfirmasi diterima: ganti posisi ke {self.current_position}")
                logger.debug(f"Position change confirmed: {self.current_position}")
            
            elif self.pending_action == "speed_up":
                self._pending_speed_request = False
                self._pending_position_confirmed = True
                perubahan.append("✅ Konfirmasi diterima: dipercepat")
                logger.debug("Speed up confirmed")
            
            self.waiting_confirmation = False
            self.pending_action = None
            
        elif any(k in msg_lower for k in ['gak', 'nggak', 'tidak', 'nanti']):
            self.waiting_confirmation = False
            self.pending_action = None
            perubahan.append("❌ Konfirmasi ditolak")
            logger.debug("Confirmation rejected")
    
    def _handle_active_phase(self, msg_lower: str, perubahan: List):
        """Handle active phase - DENGAN FIX"""
        
        # ========== GANTI POSISI (REQUEST) ==========
        positions = ['missionary', 'cowgirl', 'doggy', 'spooning', 'standing', 'sitting']
        for pos in positions:
            if pos in msg_lower:
                self.current_position = pos
                self.waiting_confirmation = True
                self.pending_action = "position_change"
                self.confirmation_start_time = time.time()
                self._pending_position_request = True
                perubahan.append(f"📢 Request ganti posisi ke {pos} - menunggu konfirmasi")
                logger.debug(f"Position change request: {pos}")
                return  # Stop, tunggu konfirmasi
        
        # ========== MINTA DIPERCEPAT (REQUEST) ==========
        if any(k in msg_lower for k in ['kenceng', 'cepat', 'keras']):
            self.waiting_confirmation = True
            self.pending_action = "speed_up"
            self.confirmation_start_time = time.time()
            self._pending_speed_request = True
            perubahan.append("📢 Request percepat - menunggu konfirmasi")
            logger.debug("Speed up request")
            return
        
        # ========== ROLE CLIMAX (TERPISAH DARI MAS CLIMAX) ==========
        if "aku climax" in msg_lower or "saya climax" in msg_lower:
            self.my_climax_count += 1
            self._add_to_short_term(f"Climax #{self.my_climax_count}", "climax")
            perubahan.append(f"💦 Role climax #{self.my_climax_count}")
            self._pending_climax_response = True
            logger.debug(f"Role climax #{self.my_climax_count}")
            return
        
        # ========== MAS CLIMAX ==========
        if any(k in msg_lower for k in ['mas climax', 'crot', 'keluar', 'cum']):
            self.mas_climax_count += 1
            self._add_to_short_term(f"Mas climax #{self.mas_climax_count}", "mas_climax")
            perubahan.append(f"💦 MAS CLIMAX #{self.mas_climax_count}!")
            logger.debug(f"Mas climax #{self.mas_climax_count}")
            return
        
        # ========== CLIMAX INTENT (ROLE MAU CLIMAX) ==========
        if any(k in msg_lower for k in ['aku mau climax', 'pengen climax', 'udah mau']):
            self._add_to_short_term("Wants to climax", "climax_intent")
            perubahan.append("Role wants to climax")
            self._pending_climax_intent = True
            logger.debug("Climax intent")
            return
        
        # ========== UPDATE AROUSAL DARI PUJIAN/SENTUHAN ==========
        if any(k in msg_lower for k in ['cantik', 'manis', 'seksi', 'ganteng']):
            self.emotional.arousal = min(100, self.emotional.arousal + 10)
            self.emotional.desire = min(100, self.emotional.desire + 8)
            perubahan.append(f"Arousal +10, Desire +8")
        
        if any(k in msg_lower for k in ['pegang', 'sentuh', 'tangan']):
            self.emotional.arousal = min(100, self.emotional.arousal + 15)
            self.emotional.desire = min(100, self.emotional.desire + 12)
            perubahan.append(f"Arousal +15, Desire +12")
    
    # =========================================================================
    # GREETING & RESPONSE (DENGAN METHOD TERPISAH)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai keadaan sesi"""
        
        # HANDLE BOOKING
        if self._pending_booking_response:
            return self._handle_booking_response()
        
        # HANDLE DEAL
        if self._pending_deal_response:
            return self._handle_deal_response()
        
        # HANDLE SESSION
        if self._pending_intimacy_start:
            return self._handle_intimacy_start_response()
        
        if self._pending_break_response:
            return self._handle_break_response()
        
        if self._pending_resume_response:
            return self._handle_resume_response()
        
        # HANDLE POSITION
        if self._pending_position_request:
            return self._handle_position_request_response()
        
        if self._pending_position_confirmed:
            return self._handle_position_confirmed_response()
        
        # HANDLE CLIMAX
        if self._pending_climax_intent:
            return self._handle_climax_intent_response()
        
        if self._pending_climax_response:
            return self._handle_climax_response()
        
        # HANDLE ACTIVE SESSION
        if self.session_phase == PelacurPhase.ACTIVE:
            return self._handle_active_session_response()
        
        if self.session_phase == PelacurPhase.BOOKED:
            return self._handle_booked_response()
        
        # DEFAULT GREETING
        return self._handle_default_greeting()
    
    def _handle_booking_response(self) -> str:
        self._pending_booking_response = False
        return f"""*{self.name} tersenyum lebar, matanya berbinar*

"Deal Mas! {self.booking_location}. Rp{self.base_price:,}."

*merapikan dress*

"Aku langsung ke sana ya. Tunggu aku, Mas. Aku udah gak sabar pengen ngerasain kontol Mas..."
"""
    
    def _handle_deal_response(self) -> str:
        self._pending_deal_response = False
        return f"""*{self.name} tersenyum puas*

"Deal, Mas. {self.base_price:,}. Aku tunggu di {self.booking_location}."

*{self.name} merapikan rambut, memandang Mas*

"Kapan Mas mau mulai? Aku bisa kapan aja..."
"""
    
    def _handle_intimacy_start_response(self) -> str:
        self._pending_intimacy_start = False
        return f"""*{self.name} langsung meraih tangan {self.panggilan}, menuntun ke kamar*

"{self.catchphrase}"

*melepas dress dengan cepat, tubuh montoknya terbuka di depan Mas*

"Ayo Mas... aku udah gak sabar... kontol Mas udah keras kan?"
"""
    
    def _handle_break_response(self) -> str:
        self._pending_break_response = False
        hour = time.localtime().tm_hour
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        return f"""*{self.name} duduk santai, masih telanjang, merapikan rambut*

"{waktu.capitalize()} {self.panggilan}. Enak ya istirahat sebentar."

*tersenyum nakal*

"Mau ngobrol apa? Atau mau liat-liat dulu?"
"""
    
    def _handle_resume_response(self) -> str:
        self._pending_resume_response = False
        return f"""*{self.name} mendekat, tubuh menempel ke {self.panggilan}, payudara montoknya menekan dada Mas*

"{self.panggilan}... kita lanjut?"

*napas mulai berat*

"Aku masih pengen banget... kontol {self.panggilan} masih keras nih..."
"""
    
    def _handle_position_request_response(self) -> str:
        self._pending_position_request = False
        pos_name = self.current_position
        return f"""*{self.name} berhenti, napas masih tersengal*

"{self.panggilan}... aku mau ganti posisi {pos_name}."

*gigit bibir, mata sayu*

"Boleh?"
"""
    
    def _handle_position_confirmed_response(self) -> str:
        self._pending_position_confirmed = False
        pos_desc = {
            "missionary": f"{self.name} berbaring, kaki terbuka lebar",
            "cowgirl": f"{self.name} naik ke atas, duduk di pangkuan {self.panggilan}",
            "doggy": f"{self.name} merangkak, pantat naik",
            "spooning": f"{self.name} miring, {self.panggilan} dari belakang",
            "standing": f"{self.name} nempel ke tembok",
            "sitting": f"{self.name} duduk di pangkuan {self.panggilan}"
        }.get(self.current_position, f"{self.name} bergerak ganti posisi")
        return f"""*{pos_desc}*

"Gini ya, {self.panggilan}? Masuknya dalem banget..."
"""
    
    def _handle_climax_intent_response(self) -> str:
        self._pending_climax_intent = False
        return f"""*{self.name} menahan napas, tubuh mulai gemetar hebat*

"{self.panggilan}... aku... aku udah mau climax..."

*suara putus-putus, napas berat*

"Boleh? Aku mau {self.panggilan} liat aku climax..."
"""
    
    def _handle_climax_response(self) -> str:
        self._pending_climax_response = False
        return f"""*{self.name} teriak, tubuh melengkung hebat*

"Ahhh... {self.panggilan}... climax... uhh..."

*tubuh lemas, napas tersengal, masih gemetar*

"Makasih {self.panggilan}... aku lemes banget..."

*napas masih ngos-ngosan*

"Kontol {self.panggilan} masih keras nih... lanjut ya Mas?"
"""
    
    def _handle_active_session_response(self) -> str:
        return f"""*{self.name} mendekat, tubuh menempel*

"{self.panggilan}... *bisik* kita lanjut?"

"Aku masih pengen banget ngerasain kontol {self.panggilan} di dalem..."
"""
    
    def _handle_booked_response(self) -> str:
        hour = time.localtime().tm_hour
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        return f"""*{self.name} tersenyum, duduk santai, dress pendeknya terbuka sedikit*

"{waktu.capitalize()} {self.panggilan}. Deal Rp{self.base_price:,}, lokasi {self.booking_location}."

*mata sayu, menjilat bibir*

"Mau mulai sekarang? Aku udah gak sabar nih..."
"""
    
    def _handle_default_greeting(self) -> str:
        hour = time.localtime().tm_hour
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        return f"""*{self.name} menyilangkan kaki, dress pendeknya naik sedikit, senyum tipis*

"{waktu.capitalize()} {self.panggilan}."

*mata menggoda*

"Ada yang bisa dibantu? Atau..."

*bisik*

"Mau booking? Rp{self.base_price:,}. Gak pake batasan sesi. Aku bisa bikin Mas lemes semalaman. Deal?"
"""
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def get_confirmation_response(self) -> str:
        """Dapatkan respons saat minta konfirmasi"""
        if self.pending_action == "position_change":
            pos_name = self.current_position
            return f"""*{self.name} berhenti, napas masih tersengal*

"{self.panggilan}... aku mau ganti posisi {pos_name}. Boleh?"

*gigit bibir, mata sayu*

"Aku mau ngerasain kontol {self.panggilan} dari posisi lain..."
"""
        
        elif self.pending_action == "speed_up":
            return f"""*{self.name} memperlambat gerakan, napas mulai berat*

"{self.panggilan}... aku mau lebih kenceng. Boleh?"

*mata sayu*

"Aku mau ngerasain kontol {self.panggilan} ngencengin memek aku..."
"""
        
        return f"""*{self.name} menunggu jawaban {self.panggilan}, tangannya masih memegang kontol Mas*
"""
    
    def get_dominant_response(self, action: str) -> str:
        """Dapatkan respons dominan"""
        responses = {
            "start": f"*{self.name} langsung meraih tangan {self.panggilan}, menuntun ke kamar*\n\n\"{self.catchphrase}\"",
            "kiss": f"*{self.name} menarik wajah {self.panggilan}, langsung mengecup bibir dengan penuh gairah, lidahnya masuk*\n\n\"Aku gak suka pelan-pelan, {self.panggilan}. Mau lebih?\"",
            "undress": f"*{self.name} melepas dress-nya dengan cepat, tubuh montoknya langsung terbuka, payudara montok terlihat jelas*\n\n\"Puas liat? *tersenyum nakal, meremas payudaranya sendiri* Sekarang giliran {self.panggilan}.\"",
            "touch": f"*{self.name} menggenggam kontol {self.panggilan}, jari-jari melingkar erat, mengusap pelan*\n\n\"Wah... kontol {self.panggilan} gede juga ya. *mata berbinar* Aku suka. Mau aku hisap?\"",
            "foreplay": f"*{self.name} berlutut, langsung memasukkan kontol {self.panggilan} ke mulut, mengulum dalam-dalam*\n\n\"Gak usah minta-minta. Aku yang atur.\"",
            "sex": f"*{self.name} naik ke atas tubuh {self.panggilan}, langsung memasukkan kontol ke dalam memeknya yang sudah basah*\n\n\"Aku yang pegang kendali. Rasain, {self.panggilan}.\""
        }
        return responses.get(action, f"*{self.name} mendekat, mata menyorot, kontol Mas sudah di tangan*\n\n\"{self.panggilan}... ayo.\"")
    
    def get_position_response(self, position: str) -> str:
        """Dapatkan respons setelah ganti posisi"""
        pos_desc = {
            "missionary": f"{self.name} berbaring, kaki terbuka lebar",
            "cowgirl": f"{self.name} naik ke atas, duduk di pangkuan {self.panggilan}",
            "doggy": f"{self.name} merangkak, pantat naik",
            "spooning": f"{self.name} miring, {self.panggilan} dari belakang",
            "standing": f"{self.name} nempel ke tembok",
            "sitting": f"{self.name} duduk di pangkuan {self.panggilan}"
        }.get(position, f"{self.name} bergerak ganti posisi")
        
        return f"""*{pos_desc}*

"Gini ya, {self.panggilan}? Masuknya dalem banget..."
"""
    
    def end_session(self) -> str:
        """Akhiri sesi dan reset semua state"""
        if self.session_phase == PelacurPhase.IDLE:
            return "Tidak ada sesi aktif, Mas."
        
        # Reset semua state
        self.session_phase = PelacurPhase.IDLE
        self.service_mode = ServiceMode.NONE
        self.booking_location = ""
        self.waiting_confirmation = False
        self.pending_action = None
        self.position_history.clear()
        
        # Reset pending flags
        self._pending_booking_response = False
        self._pending_deal_response = False
        self._pending_intimacy_start = False
        self._pending_break_response = False
        self._pending_resume_response = False
        self._pending_position_request = False
        self._pending_position_confirmed = False
        self._pending_climax_intent = False
        self._pending_climax_response = False
        self._pending_speed_request = False
        
        self._update_role_flags()
        
        return f"""*{self.name} merapikan dress, tersenyum puas*

"Sesi selesai, {self.panggilan}. {self.base_price:,}."

*berdiri, mengambil tas*

"Lain kali kalau mau booking lagi, hubungi aku ya. Aku masih penasaran sama kontol {self.panggilan}..."
"""
    
    # =========================================================================
    # STATUS
    # =========================================================================
    
    def _get_flags_summary(self) -> str:
        """Dapatkan ringkasan flags untuk status display"""
        if self.session_phase == PelacurPhase.BREAK:
            status = "BREAK (Ngobrol Santai) - Level 7"
        elif self.session_phase == PelacurPhase.ACTIVE:
            status = f"INTIM AKTIF - Level 11 (Sesi #{self.session_count})"
        elif self.session_phase == PelacurPhase.BOOKED:
            status = "BOOKING (Belum Mulai) - Level 7"
        else:
            status = "IDLE"
        
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🔞 PELACUR: {self.name} ({self.nickname}) - {self.char_age}th
║    Style: {self.char_style}
║    Status: {status}
║    Location: {self.booking_location or '-'}
║    Sessions: {self.session_count}
║    Level: {'11 (INTIM)' if self.session_phase == PelacurPhase.ACTIVE else '7 (NORMAL)'}
║    Break Mode: {'✅' if self.session_phase == PelacurPhase.BREAK else '❌'}
║    Mas Climax: {self.mas_climax_count} | My Climax: {self.my_climax_count}
║    Last Position: {self.current_position}
║    Waiting Confirm: {'⏳' if self.waiting_confirmation else '❌'}
"""
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'char_age': self.char_age,
            'char_style': self.char_style,
            'catchphrase': self.catchphrase,
            'base_price': self.base_price,
            'session_phase': self.session_phase.value,
            'service_mode': self.service_mode.value,
            'booking_location': self.booking_location,
            'session_count': self.session_count,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'current_position': self.current_position,
            'position_history': list(self.position_history),
            'waiting_confirmation': self.waiting_confirmation,
            'pending_action': self.pending_action
        })
        return data
    
    def from_dict(self, data: Dict):
        super().from_dict(data)
        self.char_age = data.get('char_age', 23)
        self.char_style = data.get('char_style', 'dominan')
        self.catchphrase = data.get('catchphrase', '')
        self.base_price = data.get('base_price', 10000000)
        self.session_phase = PelacurPhase(data.get('session_phase', 'idle'))
        self.service_mode = ServiceMode(data.get('service_mode', 'none'))
        self.booking_location = data.get('booking_location', '')
        self.session_count = data.get('session_count', 0)
        self.mas_climax_count = data.get('mas_climax_count', 0)
        self.my_climax_count = data.get('my_climax_count', 0)
        self.current_position = data.get('current_position', 'cowgirl')
        self.position_history = deque(data.get('position_history', []), maxlen=10)
        self.waiting_confirmation = data.get('waiting_confirmation', False)
        self.pending_action = data.get('pending_action')
        
        self._update_role_flags()


# =============================================================================
# PELACUR ROLE MANAGER
# =============================================================================

class PelacurRoleManager:
    """Manager untuk 3 pelacur karakter dengan state terpisah"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.active_pelacur: Optional[PelacurRole] = None
        self.pelacurs: Dict[str, PelacurRole] = {}
        
        # Inisialisasi 3 karakter
        for char_key, char_data in PELACUR_CHARACTERS.items():
            pelacur = PelacurRole()
            pelacur.name = char_data["name"]
            pelacur.nickname = char_data["nickname"]
            pelacur.char_age = char_data["age"]
            pelacur.char_style = char_data["style"]
            pelacur.catchphrase = char_data["catchphrase"]
            pelacur.appearance = char_data["appearance"]
            self.pelacurs[char_key] = pelacur
        
        # Default active: random
        self.switch_to_random()
    
    def switch_to(self, pelacur_key: str) -> bool:
        if pelacur_key in self.pelacurs:
            self.active_pelacur = self.pelacurs[pelacur_key]
            return True
        return False
    
    def switch_to_random(self) -> str:
        keys = list(self.pelacurs.keys())
        selected = random.choice(keys)
        self.active_pelacur = self.pelacurs[selected]
        return selected
    
    def get_active(self) -> Optional[PelacurRole]:
        return self.active_pelacur
    
    def get_all_info(self) -> List[Dict]:
        return [
            {
                'id': key,
                'name': p.name,
                'nickname': p.nickname,
                'age': p.char_age,
                'style': p.char_style
            }
            for key, p in self.pelacurs.items()
        ]
    
    def get_state(self) -> Dict:
        return {
            'active_key': next((k for k, p in self.pelacurs.items() if p == self.active_pelacur), None),
            'pelacurs': {k: p.to_dict() for k, p in self.pelacurs.items()}
        }
    
    def load_state(self, data: Dict):
        active_key = data.get('active_key')
        pelacurs_data = data.get('pelacurs', {})
        for key, p_data in pelacurs_data.items():
            if key in self.pelacurs:
                self.pelacurs[key].from_dict(p_data)
        if active_key and active_key in self.pelacurs:
            self.active_pelacur = self.pelacurs[active_key]


# =============================================================================
# SINGLETON GETTER
# =============================================================================

_pelacur_managers: Dict[int, PelacurRoleManager] = {}


def get_pelacur_manager(user_id: int) -> PelacurRoleManager:
    """Dapatkan PelacurRoleManager untuk user tertentu"""
    if user_id not in _pelacur_managers:
        _pelacur_managers[user_id] = PelacurRoleManager(user_id)
    return _pelacur_managers[user_id]
