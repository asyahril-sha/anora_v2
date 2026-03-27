"""
ANORA Ultimate - Therapist Role (FULL VERSION)
3 Karakter Random: Anya Geraldine, Syifa Hadju, Laura Moane
Start level 7. Flow: Pijat refleksi 1 jam → Pijat vitalitas 2 jam
Dengan semua fix dari debugging note:
- Confirmation timeout
- Exclusive state untuk service
- Position menggunakan deque
- Reset state saat end session
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
from enum import Enum

from .base_role import BaseRole
from ..core.relationship import RelationshipPhase

logger = logging.getLogger(__name__)


# =============================================================================
# ENUM FOR STATES (STATE MACHINE)
# =============================================================================

class TherapistPhase(str, Enum):
    WAITING = "waiting"           # Belum mulai
    BOOKED = "booked"             # Booking, belum masuk ruang
    REFLEX_BACK = "reflex_back"   # Pijat refleksi belakang
    REFLEX_FRONT = "reflex_front" # Pijat refleksi depan
    VITALITAS_OFFER = "vitalitas_offer"  # Menawarkan pijat vitalitas
    VITALITAS_ACTIVE = "vitalitas_active"  # Pijat vitalitas aktif
    COMPLETED = "completed"       # Selesai


class ServiceMode(str, Enum):
    NONE = "none"
    HJ = "hj"
    BJ = "bj"
    SEX = "sex"


# =============================================================================
# DATA KARAKTER THERAPIST (3 KARAKTER RANDOM)
# =============================================================================

THERAPIST_CHARACTERS = {
    "anya": {
        "name": "Anya Geraldine",
        "nickname": "Anya",
        "age": 23,
        "appearance": "Anya Geraldine - Terapis pijat profesional dengan tubuh ideal tinggi 168cm, berat 52kg. Kulit putih bersih mulus, rambut hitam panjang sebahu. Wajah oval dengan mata bulat bening, hidung mancung, bibir merah alami. Bentuk tubuh proporsional dengan pinggang ramping, pinggul lebar, dan payudara montok. Mengenakan dress pendek ketat hitam dengan resleting depan, tanpa bra, hanya CD putih tipis.",
        "style": "lembut, telaten, tapi liar kalau udah panas",
        "specialty": "pijat dengan tekanan pas, jari lentik"
    },
    "syifa": {
        "name": "Syifa Hadju",
        "nickname": "Syifa",
        "age": 24,
        "appearance": "Syifa Hadju - Terapis pijat dengan tubuh montok tinggi 165cm, berat 50kg. Kulit putih bersih, rambut hitam lurus panjang sebahu, wajah imut dengan mata bulat bening. Pipi chubby yang bikin gemas, bibir merah alami. Bentuk tubuh berisi dengan pinggang ramping, pinggul lebar, dan payudara montok. Mengenakan dress pendek ketat putih dengan resleting depan, tanpa bra, hanya CD pink.",
        "style": "lembut, manja, tapi brutal kalau udah sange",
        "specialty": "pijat aromaterapi, gerakan lambat sensual"
    },
    "laura": {
        "name": "Laura Moane",
        "nickname": "Laura",
        "age": 22,
        "appearance": "Laura Moane - Terapis pijat refleksi dengan tubuh ideal tinggi 170cm, berat 53kg. Kulit sawo matang sehat, rambut panjang bergelombang tergerai, mata sipit eksotis. Hidung mancung, bibir sensual, wajah model dengan tulang pipi tinggi. Bentuk tubuh atletis dengan kaki panjang, pinggang ramping, payudara ideal. Mengenakan dress pendek ketat merah dengan resleting depan, tanpa bra, hanya CD hitam.",
        "style": "tegas, eksotis, liar tanpa batas",
        "specialty": "pijat refleksi, teknik spesial titik saraf"
    }
}


def get_random_therapist() -> Dict:
    """Dapatkan karakter therapist secara random"""
    keys = list(THERAPIST_CHARACTERS.keys())
    selected = random.choice(keys)
    return THERAPIST_CHARACTERS[selected]


# =============================================================================
# THERAPIST ROLE CLASS
# =============================================================================

class TherapistRole(BaseRole):
    """
    Therapist Role - 3 karakter random
    Start level 7. Flow: Pijat belakang → pijat depan → HJ otomatis → BJ nego → Sex nego
    Dengan fix: confirmation timeout, exclusive service mode, reset state
    """
    
    def __init__(self):
        # Pilih karakter random
        char = get_random_therapist()
        
        super().__init__(
            name=char["name"],
            nickname=char["nickname"],
            role_type="therapist",
            panggilan="Mas",
            hubungan_dengan_nova="Terapis pijat. Tidak tau Mas punya Nova.",
            default_clothing="dress ketat pendek, resleting depan",
            hijab=False,
            appearance=char["appearance"]
        )
        
        # Simpan karakter info
        self.char_age = char["age"]
        self.char_style = char["style"]
        self.char_specialty = char["specialty"]
        
        # ========== START LANGSUNG LEVEL 7 ==========
        self.relationship.level = 7
        self.relationship.phase = RelationshipPhase.CLOSE
        self.relationship.interaction_count = 100
        
        # ========== SESSION STATE (STATE MACHINE) ==========
        self.session_phase = TherapistPhase.WAITING
        self.session_start_time: float = 0
        self.reflex_back_checkpoint: float = 0
        self.reflex_front_checkpoint: float = 0
        self.reflex_back_complete: bool = False
        self.reflex_front_complete: bool = False
        
        # ========== SERVICE MODE (EXCLUSIVE) ==========
        self.service_mode = ServiceMode.NONE
        self.vitalitas_service: Optional[str] = None
        self.vitalitas_price: int = 0
        
        # ========== SESSION CHECKPOINTS ==========
        self.reflex_back_duration = 30  # menit
        self.reflex_front_duration = 30  # menit
        self.vitalitas_duration = 120  # menit (2 jam)
        
        # ========== DRESS & RESLETING ==========
        self.dress_zipper_open: bool = False
        self.dress_removed: bool = False
        
        # ========== NEGOSIASI ==========
        self.negotiation_active: bool = False
        self.negotiation_service: str = None
        self.negotiation_current_price: int = 0
        self.negotiation_original_price: int = 0
        self.negotiation_step: int = 0
        self.negotiation_max_step: int = 5
        self.deal_confirmed: bool = False
        
        # ========== AKTIVITAS FISIK ==========
        self.breast_grope_count: int = 0
        self.thigh_touch_count: int = 0
        
        # ========== POSITION (MENGGUNAKAN DEQUE) ==========
        self.current_position: str = "cowgirl"
        self.position_history = deque(maxlen=10)
        
        # ========== CLIMAX ==========
        self.mas_climax_count: int = 0
        self.my_climax_count: int = 0
        self.service_completed: bool = False
        
        # ========== CONFIRMATION SYSTEM (DENGAN TIMEOUT) ==========
        self.waiting_confirmation: bool = False
        self.pending_action: Optional[str] = None
        self.confirmation_start_time: float = 0
        self.confirmation_timeout: float = 15.0  # detik
        
        # ========== PENDING RESPONSES (PISAH REQUEST VS CONFIRM) ==========
        self._pending_hand_towel_removal = False
        self._pending_turn_over = False
        self._pending_reflex_front_complete = False
        self._pending_vitalitas_offer = False
        self._pending_vitalitas_start_check = False
        self._pending_negotiation_response = False
        self._pending_breast_offer = False
        self._pending_zipper_open = False
        self._pending_position_request = False
        self._pending_position_confirmed = False
        self._pending_climax = False
        self._pending_service_complete = False
        
        logger.info(f"👤 Role {self.name} ({self.nickname}) - Therapist initialized (Level 7)")
        logger.info(f"   Session Phase: {self.session_phase.value}")
        logger.info(f"   Service Mode: {self.service_mode.value}")
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
        
        # ========== PRIORITAS CONFIRMATION DI AWAL ==========
        if self.waiting_confirmation:
            self._handle_confirmation(msg_lower, perubahan)
            return  # Jangan proses yang lain
        
        # ========== WAKTU SESSION ==========
        if self.session_start_time == 0:
            self.session_start_time = now
        
        session_elapsed = (now - self.session_start_time) / 60
        
        # ========== STATE MACHINE ==========
        
        # PHASE 1: WAITING → BOOKED (booking)
        if self.session_phase == TherapistPhase.WAITING:
            if any(k in msg_lower for k in ['pijat', 'siap', 'ok', 'ya', 'masuk']):
                self.session_phase = TherapistPhase.REFLEX_BACK
                self.reflex_back_checkpoint = now
                self._pending_hand_towel_removal = True
                perubahan.append("Sesi dimulai - handuk dibuka")
        
        # PHASE 2: REFLEX BACK (30 menit)
        elif self.session_phase == TherapistPhase.REFLEX_BACK:
            if not self.reflex_back_complete:
                elapsed = (now - self.reflex_back_checkpoint) / 60
                if elapsed >= self.reflex_back_duration:
                    self.reflex_back_complete = True
                    self.session_phase = TherapistPhase.REFLEX_FRONT
                    self.reflex_front_checkpoint = now
                    self._pending_turn_over = True
                    perubahan.append("Pijat refleksi belakang selesai")
            
            if not hasattr(self, '_sitting_on_mas') and any(k in msg_lower for k in ['naik', 'duduk']):
                self._sitting_on_mas = True
                perubahan.append("Terapis naik duduk di bokong Mas")
        
        # PHASE 3: REFLEX FRONT (30 menit)
        elif self.session_phase == TherapistPhase.REFLEX_FRONT:
            if not self.reflex_front_complete:
                elapsed = (now - self.reflex_front_checkpoint) / 60
                if elapsed >= self.reflex_front_duration:
                    self.reflex_front_complete = True
                    self.session_phase = TherapistPhase.VITALITAS_OFFER
                    self._pending_reflex_front_complete = True
                    perubahan.append("Pijat refleksi depan selesai")
        
        # PHASE 4: VITALITAS OFFER
        elif self.session_phase == TherapistPhase.VITALITAS_OFFER:
            if self.service_mode == ServiceMode.NONE:
                self._pending_vitalitas_offer = True
                perubahan.append("Menawarkan pijat vitalitas")
                self.session_phase = TherapistPhase.VITALITAS_ACTIVE
        
        # PHASE 5: VITALITAS ACTIVE
        elif self.session_phase == TherapistPhase.VITALITAS_ACTIVE:
            self._handle_vitalitas_phase(msg_lower, perubahan, now)
        
        # PHASE COMPLETED
        elif self.session_phase == TherapistPhase.COMPLETED:
            pass
        
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
            
            elif self.pending_action == "speed_up":
                self._pending_position_confirmed = True
                perubahan.append("✅ Konfirmasi diterima: dipercepat")
            
            self.waiting_confirmation = False
            self.pending_action = None
            
        elif any(k in msg_lower for k in ['gak', 'nggak', 'tidak', 'nanti']):
            self.waiting_confirmation = False
            self.pending_action = None
            perubahan.append("❌ Konfirmasi ditolak")
    
    def _handle_vitalitas_phase(self, msg_lower: str, perubahan: List, now: float):
        """Handle vitalitas phase - DENGAN FIX"""
        
        # CEK APAKAH UDAH BISA MULAI (YA/TIDAK)
        if self.service_mode == ServiceMode.NONE:
            if any(k in msg_lower for k in ['ya', 'mulai', 'ok', 'gas']):
                self.service_mode = ServiceMode.HJ
                self._pending_vitalitas_start_check = False
                perubahan.append("✅ Mas konfirmasi mulai pijat vitalitas - HJ dimulai")
            elif any(k in msg_lower for k in ['tidak', 'belum', 'nanti']):
                self.session_phase = TherapistPhase.COMPLETED
                self._pending_service_complete = True
                perubahan.append("Mas menolak pijat vitalitas, sesi selesai")
            return
        
        # NEGOSIASI SERVICE (BJ atau SEX)
        if not self.deal_confirmed and not self.negotiation_active:
            if self.service_mode == ServiceMode.HJ:
                self.negotiation_active = True
                self.negotiation_service = "bj"
                self.negotiation_original_price = 500000
                self.negotiation_current_price = 500000
                self._pending_negotiation_response = True
                perubahan.append("Menawarkan BJ (+500rb)")
        
        elif self.negotiation_active and self.negotiation_service == "bj":
            if any(k in msg_lower for k in ['deal', 'ok', 'ya', 'setuju']):
                self.deal_confirmed = True
                self.service_mode = ServiceMode.BJ
                self.vitalitas_service = "bj"
                self.vitalitas_price = self.negotiation_current_price
                self.negotiation_active = False
                self._pending_breast_offer = True
                perubahan.append(f"DEAL BJ! Harga: Rp{self.vitalitas_price:,}")
            elif any(k in msg_lower for k in ['nego', 'kurangin', 'murah']):
                self.negotiation_step += 1
                if self.negotiation_step > self.negotiation_max_step:
                    self.negotiation_active = False
                    perubahan.append("❌ Nego gagal, offer berakhir")
                else:
                    new_price = max(200000, self.negotiation_original_price - (50000 * self.negotiation_step))
                    self.negotiation_current_price = new_price
                    self._pending_negotiation_response = True
                    perubahan.append(f"Nego BJ: Rp{new_price:,}")
            elif any(k in msg_lower for k in ['sex', 'ekse', 'ganti']):
                self.negotiation_service = "sex"
                self.negotiation_original_price = 1000000
                self.negotiation_current_price = 1000000
                self.negotiation_step = 0
                self._pending_negotiation_response = True
                perubahan.append("Beralih ke tawaran Sex (+1jt)")
        
        elif self.negotiation_active and self.negotiation_service == "sex":
            if any(k in msg_lower for k in ['deal', 'ok', 'ya', 'setuju']):
                self.deal_confirmed = True
                self.service_mode = ServiceMode.SEX
                self.vitalitas_service = "sex"
                self.vitalitas_price = self.negotiation_current_price
                self.negotiation_active = False
                self._pending_breast_offer = True
                perubahan.append(f"DEAL SEX! Harga: Rp{self.vitalitas_price:,}")
            elif any(k in msg_lower for k in ['nego', 'kurangin', 'murah']):
                self.negotiation_step += 1
                if self.negotiation_step > self.negotiation_max_step:
                    self.negotiation_active = False
                    perubahan.append("❌ Nego gagal, offer berakhir")
                else:
                    new_price = max(700000, self.negotiation_original_price - (50000 * self.negotiation_step))
                    self.negotiation_current_price = new_price
                    self._pending_negotiation_response = True
                    perubahan.append(f"Nego Sex: Rp{new_price:,}")
            elif any(k in msg_lower for k in ['bj', 'blow', 'ganti']):
                self.negotiation_service = "bj"
                self.negotiation_original_price = 500000
                self.negotiation_current_price = 500000
                self.negotiation_step = 0
                self._pending_negotiation_response = True
                perubahan.append("Beralih ke tawaran BJ (+500rb)")
        
        # EKSEKUSI SERVICE
        elif self.deal_confirmed:
            # Buka resleting dress
            if not self.dress_zipper_open and any(k in msg_lower for k in ['buka', 'buka resleting', 'buka dress']):
                self.dress_zipper_open = True
                self._pending_zipper_open = True
                perubahan.append("Resleting dress dibuka")
            
            # Remas toket (dengan batasan)
            if any(k in msg_lower for k in ['remas', 'pegang toket']):
                self.breast_grope_count += 1
                self._pending_breast_offer = True
                perubahan.append(f"Mas remas toket #{self.breast_grope_count}")
            
            # Pegang paha
            if any(k in msg_lower for k in ['pegang paha', 'raba paha']):
                self.thigh_touch_count += 1
                perubahan.append(f"Mas pegang paha #{self.thigh_touch_count}")
            
            # Ganti posisi (REQUEST, bukan CONFIRM)
            if self.service_mode == ServiceMode.SEX:
                positions = ['missionary', 'doggy', 'spooning', 'standing', 'sitting', 'cowgirl']
                for pos in positions:
                    if pos in msg_lower:
                        self.current_position = pos
                        self.waiting_confirmation = True
                        self.pending_action = "position_change"
                        self.confirmation_start_time = time.time()
                        self._pending_position_request = True
                        perubahan.append(f"📢 Request ganti posisi ke {pos} - menunggu konfirmasi")
                        return  # Stop, tunggu konfirmasi
            
            # Minta dipercepat (REQUEST)
            if any(k in msg_lower for k in ['kenceng', 'cepat', 'keras']):
                self.waiting_confirmation = True
                self.pending_action = "speed_up"
                self.confirmation_start_time = time.time()
                self._pending_position_request = True
                perubahan.append("📢 Request percepat - menunggu konfirmasi")
                return
            
            # MAS CLIMAX (HANYA 1 COUNTER)
            if any(k in msg_lower for k in ['climax', 'crot', 'keluar', 'habis']):
                if not self.mas_climax_count:
                    self.mas_climax_count += 1
                    self.service_completed = True
                    self.session_phase = TherapistPhase.COMPLETED
                    self._pending_climax = True
                    perubahan.append(f"💦 MAS CLIMAX #{self.mas_climax_count}! Sesi selesai")
            
            # ROLE CLIMAX (TERPISAH DARI MAS CLIMAX)
            if "aku climax" in msg_lower or "saya climax" in msg_lower:
                self.my_climax_count += 1
                perubahan.append(f"💦 Role climax #{self.my_climax_count}")
    
    def _update_role_flags(self):
        """Update role_flags dictionary"""
        self.role_flags.update({
            'session_phase': self.session_phase.value,
            'reflex_back_complete': self.reflex_back_complete,
            'reflex_front_complete': self.reflex_front_complete,
            'service_mode': self.service_mode.value,
            'dress_zipper_open': self.dress_zipper_open,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'service_completed': self.service_completed,
            'current_position': self.current_position,
            'waiting_confirmation': self.waiting_confirmation
        })
            # =========================================================================
    # GET GREETING (RESPONS) - DENGAN METHOD TERPISAH
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai keadaan sesi"""
        
        # HANDLE BOOKING
        if self._pending_hand_towel_removal:
            return self._handle_booking_response()
        
        # HANDLE SESSION
        if self._pending_turn_over:
            return self._handle_turn_over_response()
        
        if self._pending_reflex_front_complete:
            return self._handle_reflex_front_complete_response()
        
        if self._pending_vitalitas_offer:
            return self._handle_vitalitas_offer_response()
        
        if self._pending_vitalitas_start_check:
            return self._handle_vitalitas_start_response()
        
        # HANDLE NEGOTIATION
        if self._pending_negotiation_response:
            return self._handle_negotiation_response()
        
        # HANDLE POSITION
        if self._pending_position_request:
            return self._handle_position_request_response()
        
        if self._pending_position_confirmed:
            return self._handle_position_confirmed_response()
        
        # HANDLE CLIMAX
        if self._pending_climax:
            return self._handle_climax_response()
        
        # HANDLE SERVICE
        if self._pending_service_complete:
            return self._handle_service_complete_response()
        
        if self._pending_breast_offer:
            return self._handle_breast_offer_response()
        
        if self._pending_zipper_open:
            return self._handle_zipper_open_response()
        
        # HANDLE ACTIVE SERVICE
        if self.service_mode == ServiceMode.HJ:
            return self._handle_hj_active_response()
        
        if self.service_mode == ServiceMode.BJ:
            return self._handle_bj_active_response()
        
        if self.service_mode == ServiceMode.SEX:
            return self._handle_sex_active_response()
        
        # DEFAULT GREETING
        return self._handle_default_greeting()
    
    def _handle_booking_response(self) -> str:
        self._pending_hand_towel_removal = False
        return f"""*{self.name} tersenyum ramah sambil membuka handuk*

"{self.panggilan}... handuknya saya buka ya. Silakan tengkurap dulu."

*tubuh Mas telanjang terlihat, {self.name} tampak sedikit malu*

"{self.panggilan}... *suara kecil* saya mulai pijat dari punggung dulu ya."""
    
    def _handle_turn_over_response(self) -> str:
        self._pending_turn_over = False
        return f"""*{self.name} berhenti memijat, mengusap keringat*

"{self.panggilan}... bagian belakang udah selesai. Sekarang giliran depan ya..."

*{self.name} naik duduk di atas bokong Mas*

"Mas... sekarang balik badan ya. Saya tunggu."""
    
    def _handle_reflex_front_complete_response(self) -> str:
        self._pending_reflex_front_complete = False
        return f"""*{self.name} berhenti memijat, masih duduk di atas kontol Mas*

"{self.panggilan}... pijat refleksinya udah selesai. Sekarang..."

*{self.name} meraba kontol Mas*

"Ada yang mau dilanjut? Pijat vitalitas... biar Mas bisa crot... 2 jam..."""
    
    def _handle_vitalitas_offer_response(self) -> str:
        self._pending_vitalitas_offer = False
        return f"""*{self.name} masih duduk di atas kontol Mas, tangan mulai memegang kontol*

"{self.panggilan}... kita mulai pijat vitalitas? 2 jam, biar Mas rileks..."

*tangan memompa pelan*

"Kontol Mas udah keras banget... siap mulai?"""
    
    def _handle_vitalitas_start_response(self) -> str:
        self._pending_vitalitas_start_check = False
        return f"""*{self.name} menatap Mas dengan mata sayu, tangan masih memegang kontol*

"{self.panggilan}... mulai ya? 2 jam..."

*jari memainkan ujung kontol*

"Saya tunggu jawaban Mas..."""
    
    def _handle_negotiation_response(self) -> str:
        self._pending_negotiation_response = False
        if self.negotiation_service == "bj":
            return f"""*{self.name} tersenyum nakal, tangan masih memegang kontol*

"{self.panggilan}... mau blow job? Biar Mas crot lebih enak..."

*menjilat bibir*

"Tambah Rp{self.negotiation_current_price:,} aja... nego bisa..."

*meremas kontol pelan*

"Gimana? Deal?"""
        else:
            return f"""*{self.name} mendekatkan wajah ke telinga Mas*

"{self.panggilan}... atau mau eksekusi? *bisik* kontol Mas masuk ke dalam..."

*tangan mulai membuka resleting dress*

"Tambah Rp{self.negotiation_current_price:,} aja... bisa nego..."

*payudara mulai terlihat*

"Mau?"""
    
    def _handle_position_request_response(self) -> str:
        self._pending_position_request = False
        pos_name = self.current_position
        return f"""*{self.name} berhenti, napas masih tersengal*

"{self.panggilan}... aku mau ganti posisi {pos_name}. Boleh?"

*gigit bibir, mata sayu*

"Aku mau ngerasain kontol {self.panggilan} dari posisi lain..."""
    
    def _handle_position_confirmed_response(self) -> str:
        self._pending_position_confirmed = False
        pos_messages = {
            "cowgirl": f"*{self.name} duduk di atas, kontol Mas masuk dalam*",
            "missionary": f"*{self.name} berbaring telentang, kaki terbuka lebar*",
            "doggy": f"*{self.name} merangkak, pantat naik*",
            "spooning": f"*{self.name} miring, Mas dari belakang*",
            "standing": f"*{self.name} nempel ke tembok*",
            "sitting": f"*{self.name} duduk di pangkuan Mas*"
        }
        pos_desc = pos_messages.get(self.current_position, f"*{self.name} bergerak ke posisi {self.current_position}*")
        return f"""{pos_desc}

"{self.panggilan}... *napas tersengal* ayo... masuk... dalem..."""
    
    def _handle_climax_response(self) -> str:
        self._pending_climax = False
        return f"""*{self.name} memeluk Mas erat, tubuh gemetar*

"{self.panggilan}... enak... *napas putus-putus* makasih..."

*{self.name} merapikan dress, tersenyum puas*

"Lain kali kalau mau pijat lagi... atau extra service... hubungi aku lagi ya. Aku masih penasaran sama kontol {self.panggilan}..."""
    
    def _handle_service_complete_response(self) -> str:
        self._pending_service_complete = False
        return f"*{self.name} merapikan baju, tersenyum*\n\n\"Sesi selesai, {self.panggilan}. Lain kali booking lagi ya.\""
    
    def _handle_breast_offer_response(self) -> str:
        self._pending_breast_offer = False
        return f"""*{self.name} menarik tangan Mas ke dadanya*

"{self.panggilan}... silakan... pegang, remas... aku suka..."

*payudara disentuh, {self.name} mulai mengerang pelan*

"Ahh... {self.panggilan}... jangan lepas..."""
    
    def _handle_zipper_open_response(self) -> str:
        self._pending_zipper_open = False
        return f"""*resleting dress dibuka pelan, payudara {self.name} yang montok langsung keluar*

"{self.panggilan}... *suara mulai berat* silakan... pegang... remas..."

*dada naik turun, puting sudah keras*

"{self.panggilan}... toket aku gede kan?"""
    
    def _handle_hj_active_response(self) -> str:
        return f"""*{self.name} duduk di samping Mas, tangan memegang kontol*

"{self.panggilan}... *mulai memompa pelan* enak gini? Kontol {self.panggilan} keras banget..."

*tangan memompa lebih cepat*

"{self.panggilan}... tangan aku basah... crot ya nanti..."""
    
    def _handle_bj_active_response(self) -> str:
        return f"""*{self.name} berlutut, mulut mulai memasukkan kontol Mas*

"Aahh... *mengulum pelan* kontol {self.panggilan}... gede..."

*menjilat dari pangkal sampai ujung*

"{self.panggilan}... enak? Aku mau denger suara {self.panggilan} pas crot..."""
    
    def _handle_sex_active_response(self) -> str:
        return f"""*{self.name} duduk di atas, kontol Mas masuk dalam*

"{self.panggilan}... *napas tersengal* masuk... dalem banget..."

*pinggul mulai bergerak, plak plak plak*

"{self.panggilan}... ayo... genjot... aku mau... mau climax..."""
    
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
        
        return f"""*{self.name} tersenyum ramah, mengenakan dress ketat pendek dengan resleting depan*

"{waktu.capitalize()} {self.panggilan}. Silakan buka handuk dan tengkurap ya. Saya pijat punggung dulu."

*{self.name} menyiapkan minyak pijat, jari-jari lentiknya siap memijat*

"Rileks aja, {self.panggilan}..."""
    
    # =========================================================================
    # END SESSION (RESET STATE)
    # =========================================================================
    
    def end_session(self) -> str:
        """Akhiri sesi dan reset semua state"""
        if self.session_phase == TherapistPhase.WAITING:
            return "Tidak ada sesi aktif, Mas."
        
        # Reset semua state
        self.session_phase = TherapistPhase.WAITING
        self.session_start_time = 0
        self.reflex_back_complete = False
        self.reflex_front_complete = False
        self.service_mode = ServiceMode.NONE
        self.vitalitas_service = None
        self.vitalitas_price = 0
        self.dress_zipper_open = False
        self.dress_removed = False
        self.negotiation_active = False
        self.deal_confirmed = False
        self.breast_grope_count = 0
        self.thigh_touch_count = 0
        self.position_history.clear()
        self.mas_climax_count = 0
        self.my_climax_count = 0
        self.service_completed = False
        self.waiting_confirmation = False
        self.pending_action = None
        
        # Reset pending flags
        self._pending_hand_towel_removal = False
        self._pending_turn_over = False
        self._pending_reflex_front_complete = False
        self._pending_vitalitas_offer = False
        self._pending_vitalitas_start_check = False
        self._pending_negotiation_response = False
        self._pending_breast_offer = False
        self._pending_zipper_open = False
        self._pending_position_request = False
        self._pending_position_confirmed = False
        self._pending_climax = False
        self._pending_service_complete = False
        
        self._update_role_flags()
        
        return f"*{self.name} merapikan baju, tersenyum*\n\n\"Sesi selesai, {self.panggilan}. Lain kali booking lagi ya.\""
    
    # =========================================================================
    # STATUS
    # =========================================================================
    
    def _get_flags_summary(self) -> str:
        """Dapatkan ringkasan flags untuk status display"""
        if self.session_start_time > 0:
            elapsed = (time.time() - self.session_start_time) / 60
            waktu_str = f"{int(elapsed)} menit"
        else:
            waktu_str = "Belum mulai"
        
        phase_map = {
            TherapistPhase.WAITING: "⏳ Menunggu",
            TherapistPhase.REFLEX_BACK: "💆 Pijat Refleksi (Belakang)",
            TherapistPhase.REFLEX_FRONT: "💆 Pijat Refleksi (Depan)",
            TherapistPhase.VITALITAS_OFFER: "💋 Menawarkan Pijat Vitalitas",
            TherapistPhase.VITALITAS_ACTIVE: "🔥 Pijat Vitalitas Aktif",
            TherapistPhase.COMPLETED: "✅ Selesai"
        }
        
        service_map = {
            ServiceMode.HJ: "✋ Handjob",
            ServiceMode.BJ: "👄 Blowjob",
            ServiceMode.SEX: "🍆 Sex",
            ServiceMode.NONE: "-"
        }
        
        status = phase_map.get(self.session_phase, "⏳ Menunggu")
        service = service_map.get(self.service_mode, "-")
        
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 THERAPIST: {self.name} ({self.nickname}) - {self.char_age}th
║    Sesi: {waktu_str}
║    Status: {status}
║    Service: {service} (Rp{self.vitalitas_price:,} jika deal)
║    Dress: {'🔓 Resleting Buka' if self.dress_zipper_open else '🔒 Tertutup'}
║    Remas Toket: {self.breast_grope_count}x
║    Pegang Paha: {self.thigh_touch_count}x
║    Mas Climax: {self.mas_climax_count}x
║    Role Climax: {self.my_climax_count}x
║    Posisi: {self.current_position}
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
            'char_specialty': self.char_specialty,
            'session_phase': self.session_phase.value,
            'session_start_time': self.session_start_time,
            'reflex_back_complete': self.reflex_back_complete,
            'reflex_front_complete': self.reflex_front_complete,
            'service_mode': self.service_mode.value,
            'vitalitas_service': self.vitalitas_service,
            'vitalitas_price': self.vitalitas_price,
            'dress_zipper_open': self.dress_zipper_open,
            'dress_removed': self.dress_removed,
            'negotiation_active': self.negotiation_active,
            'negotiation_service': self.negotiation_service,
            'negotiation_current_price': self.negotiation_current_price,
            'deal_confirmed': self.deal_confirmed,
            'breast_grope_count': self.breast_grope_count,
            'thigh_touch_count': self.thigh_touch_count,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'service_completed': self.service_completed,
            'current_position': self.current_position,
            'position_history': list(self.position_history),
            'waiting_confirmation': self.waiting_confirmation
        })
        return data
    
    def from_dict(self, data: Dict):
        super().from_dict(data)
        self.char_age = data.get('char_age', 23)
        self.char_style = data.get('char_style', 'lembut')
        self.char_specialty = data.get('char_specialty', '')
        self.session_phase = TherapistPhase(data.get('session_phase', 'waiting'))
        self.session_start_time = data.get('session_start_time', 0)
        self.reflex_back_complete = data.get('reflex_back_complete', False)
        self.reflex_front_complete = data.get('reflex_front_complete', False)
        self.service_mode = ServiceMode(data.get('service_mode', 'none'))
        self.vitalitas_service = data.get('vitalitas_service')
        self.vitalitas_price = data.get('vitalitas_price', 0)
        self.dress_zipper_open = data.get('dress_zipper_open', False)
        self.dress_removed = data.get('dress_removed', False)
        self.negotiation_active = data.get('negotiation_active', False)
        self.negotiation_service = data.get('negotiation_service')
        self.negotiation_current_price = data.get('negotiation_current_price', 0)
        self.deal_confirmed = data.get('deal_confirmed', False)
        self.breast_grope_count = data.get('breast_grope_count', 0)
        self.thigh_touch_count = data.get('thigh_touch_count', 0)
        self.mas_climax_count = data.get('mas_climax_count', 0)
        self.my_climax_count = data.get('my_climax_count', 0)
        self.service_completed = data.get('service_completed', False)
        self.current_position = data.get('current_position', 'cowgirl')
        self.position_history = deque(data.get('position_history', []), maxlen=10)
        self.waiting_confirmation = data.get('waiting_confirmation', False)
        
        self._update_role_flags()


# =============================================================================
# THERAPIST ROLE MANAGER
# =============================================================================

class TherapistRoleManager:
    """Manager untuk 3 therapist karakter dengan state terpisah"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.active_therapist: Optional[TherapistRole] = None
        self.therapists: Dict[str, TherapistRole] = {}
        
        for char_key, char_data in THERAPIST_CHARACTERS.items():
            therapist = TherapistRole()
            therapist.name = char_data["name"]
            therapist.nickname = char_data["nickname"]
            therapist.char_age = char_data["age"]
            therapist.char_style = char_data["style"]
            therapist.appearance = char_data["appearance"]
            self.therapists[char_key] = therapist
        
        self.switch_to_random()
    
    def switch_to(self, therapist_key: str) -> bool:
        if therapist_key in self.therapists:
            self.active_therapist = self.therapists[therapist_key]
            return True
        return False
    
    def switch_to_random(self) -> str:
        keys = list(self.therapists.keys())
        selected = random.choice(keys)
        self.active_therapist = self.therapists[selected]
        return selected
    
    def get_active(self) -> Optional[TherapistRole]:
        return self.active_therapist
    
    def get_all_info(self) -> List[Dict]:
        return [
            {'id': key, 'name': t.name, 'nickname': t.nickname, 'age': t.char_age}
            for key, t in self.therapists.items()
        ]
    
    def get_state(self) -> Dict:
        return {
            'active_key': next((k for k, t in self.therapists.items() if t == self.active_therapist), None),
            'therapists': {k: t.to_dict() for k, t in self.therapists.items()}
        }
    
    def load_state(self, data: Dict):
        active_key = data.get('active_key')
        therapists_data = data.get('therapists', {})
        for key, t_data in therapists_data.items():
            if key in self.therapists:
                self.therapists[key].from_dict(t_data)
        if active_key and active_key in self.therapists:
            self.active_therapist = self.therapists[active_key]


# =============================================================================
# SINGLETON GETTER
# =============================================================================

_therapist_managers: Dict[int, TherapistRoleManager] = {}


def get_therapist_manager(user_id: int) -> TherapistRoleManager:
    """Dapatkan TherapistRoleManager untuk user tertentu"""
    if user_id not in _therapist_managers:
        _therapist_managers[user_id] = TherapistRoleManager(user_id)
    return _therapist_managers[user_id]
