"""
ANORA-V2 Therapist Role - 3 Karakter Random
Start level 7. Pijat depan & belakang → HJ otomatis (gak nego) → BJ nego → Sex nego.
Level dinamis: level 7 (normal) → level 11 (intim) setelah "mulai"
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole
from core.relationship import RelationshipPhase
from core.state_tracker import PhysicalCondition
"""
ANORA Ultimate - Therapist Role
3 Karakter Random: Anya Geraldine, Syifa Hadju, Laura Moane
Start level 7. Flow: Pijat refleksi 1 jam → Pijat vitalitas 2 jam (dengan negosiasi service)
Waktu real-time: total 3 jam sesi, dengan checkpoint per jam
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

from .base_role import BaseRole
from ..core.relationship_manager import RelationshipPhase

logger = logging.getLogger(__name__)


# =============================================================================
# DATA KARAKTER THERAPIST (3 KARAKTER RANDOM)
# =============================================================================

THERAPIST_CHARACTERS = {
    "anya": {
        "name": "Anya Geraldine",
        "nickname": "Anya",
        "age": 23,
        "appearance": """Anya Geraldine - Terapis pijat profesional dengan tubuh ideal tinggi 168cm, berat 52kg. 
Kulit putih bersih mulus, rambut hitam panjang sebahu yang biasanya diikat saat bekerja.
Wajah oval dengan mata bulat bening, hidung mancung, bibir merah alami yang selalu tersenyum ramah.
Bentuk tubuh proporsional dengan pinggang ramping, pinggul lebar, dan payudara montok.
Mengenakan dress pendek ketat hitam dengan resleting depan, tanpa bra, hanya CD putih tipis.""",
        "style": "lembut, telaten, tapi liar kalau udah panas",
        "specialty": "pijat dengan tekanan pas, jari lentik"
    },
    "syifa": {
        "name": "Syifa Hadju",
        "nickname": "Syifa",
        "age": 24,
        "appearance": """Syifa Hadju - Terapis pijat dengan tubuh montok tinggi 165cm, berat 50kg.
Kulit putih bersih, rambut hitam lurus panjang sebahu, wajah imut dengan mata bulat bening.
Pipi chubby yang bikin gemas, bibir merah alami, senyum manis.
Bentuk tubuh berisi dengan pinggang ramping, pinggul lebar, dan payudara montok.
Mengenakan dress pendek ketat putih dengan resleting depan, tanpa bra, hanya CD pink.""",
        "style": "lembut, manja, tapi brutal kalau udah sange",
        "specialty": "pijat aromaterapi, gerakan lambat sensual"
    },
    "laura": {
        "name": "Laura Moane",
        "nickname": "Laura",
        "age": 22,
        "appearance": """Laura Moane - Terapis pijat refleksi dengan tubuh ideal tinggi 170cm, berat 53kg.
Kulit sawo matang sehat, rambut panjang bergelombang tergerai, mata sipit eksotis.
Hidung mancung, bibir sensual, wajah model dengan tulang pipi tinggi.
Bentuk tubuh atletis dengan kaki panjang, pinggang ramping, payudara ideal.
Mengenakan dress pendek ketat merah dengan resleting depan, tanpa bra, hanya CD hitam.""",
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
    Flow: 
    1. Masuk ruang terapis (handuk dibuka, telanjang)
    2. Pijat refleksi 1 jam (30 menit tengkurap + 30 menit telentang)
    3. Pijat vitalitas 2 jam (dengan negosiasi service)
    Total sesi 3 jam dengan waktu real-time
    """
    
    def __init__(self):
        # Pilih karakter random
        char = get_random_therapist()
        
        super().__init__(
            user_id=0,  # akan di-set saat inisialisasi
            role_id="therapist",
            name=char["name"],
            panggilan="Mas",
            hubungan_dengan_nova="Terapis pijat. Tidak tau Mas punya Nova."
        )
        
        # Simpan karakter info
        self.char_name = char["name"]
        self.char_nickname = char["nickname"]
        self.char_age = char["age"]
        self.char_appearance = char["appearance"]
        self.char_style = char["style"]
        self.char_specialty = char["specialty"]
        
        # Override nama
        self.name = char["name"]
        
        # ========== START LANGSUNG LEVEL 7 ==========
        self.relationship.level = 7
        self.relationship.phase = RelationshipPhase.CLOSE
        self.relationship.interaction_count = 100
        
        # ========== ROLE-SPECIFIC STATE ==========
        # Sesi & Waktu Real-time
        self.session_start_time: float = 0
        self.session_phase: str = "waiting"  # waiting, reflex_back, reflex_front, vitalitas, completed
        self.reflex_back_complete: bool = False
        self.reflex_front_complete: bool = False
        self.vitalitas_active: bool = False
        self.vitalitas_start_time: float = 0
        self.vitalitas_service: str = None  # hj, bj, sex
        self.vitalitas_price: int = 0
        
        # Status Pijat
        self.massage_position: str = "tengkurap"  # tengkurap, telentang
        self.sitting_on_mas: bool = False  # duduk di atas kontol Mas saat pijat depan
        self.hand_towel_removed: bool = False  # handuk sudah dibuka
        
        # Dress & Resleting
        self.dress_zipper_open: bool = False  # resleting depan dibuka
        self.dress_removed: bool = False  # dress dilepas total (saat sex)
        self.cd_removed: bool = False  # CD dilepas (saat sex)
        
        # Pijat vitalitas
        self.vitalitas_start_confirmed: bool = False  # Mas sudah konfirmasi mulai
        self.vitalitas_hj_active: bool = False
        self.vitalitas_bj_active: bool = False
        self.vitalitas_sex_active: bool = False
        
        # Negosiasi
        self.negotiation_active: bool = False
        self.negotiation_service: str = None  # bj, sex
        self.negotiation_current_price: int = 0
        self.negotiation_original_price: int = 0
        self.negotiation_step: int = 0
        self.deal_confirmed: bool = False
        
        # Aktivitas fisik
        self.breast_grope_count: int = 0  # Mas remas toket
        self.thigh_touch_count: int = 0   # Mas pegang paha
        
        # Climax & Service selesai
        self.mas_climax: bool = False
        self.service_completed: bool = False
        
        # Current position (saat sex)
        self.current_position: str = "cowgirl"  # default mulai cowgirl
        
        # Pending responses
        self._pending_hand_towel_removal = False
        self._pending_turn_over = False
        self._pending_reflex_back_complete = False
        self._pending_reflex_front_complete = False
        self._pending_vitalitas_offer = False
        self._pending_vitalitas_start_check = False
        self._pending_negotiation_response = False
        self._pending_breast_offer = False
        self._pending_zipper_open = False
        self._pending_position_change = False
        self._pending_climax = False
        self._pending_service_complete = False
        
        # Simpan flags untuk status
        self._update_role_flags()
        
        logger.info(f"👤 Role {self.name} ({self.char_nickname}) - Therapist initialized (Level 7)")
        logger.info(f"   Age: {self.char_age} | Style: {self.char_style}")
    
    def _update_role_flags(self):
        """Update role_flags dictionary"""
        self.role_flags.update({
            'session_phase': self.session_phase,
            'reflex_back_complete': self.reflex_back_complete,
            'reflex_front_complete': self.reflex_front_complete,
            'vitalitas_active': self.vitalitas_active,
            'vitalitas_service': self.vitalitas_service,
            'dress_zipper_open': self.dress_zipper_open,
            'dress_removed': self.dress_removed,
            'cd_removed': self.cd_removed,
            'hand_towel_removed': self.hand_towel_removed,
            'sitting_on_mas': self.sitting_on_mas,
            'mas_climax': self.mas_climax,
            'service_completed': self.service_completed,
            'current_position': self.current_position
        })
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state dari pesan Mas"""
        msg_lower = pesan_mas.lower()
        now = time.time()
        
        # ========== WAKTU SESSION ==========
        if self.session_start_time == 0:
            self.session_start_time = now
        
        session_elapsed = (now - self.session_start_time) / 60  # menit
        
        # ========== PHASE 1: MASUK RUANG & BUKA HANDUK ==========
        if self.session_phase == "waiting":
            if any(k in msg_lower for k in ['siap', 'ok', 'ya', 'masuk']):
                self.hand_towel_removed = True
                self.session_phase = "reflex_back"
                self._pending_hand_towel_removal = True
                perubahan.append("Handuk dibuka, telanjang total")
        
        # ========== PHASE 2: PIJAT REFLEKSI BELAKANG (30 menit) ==========
        elif self.session_phase == "reflex_back":
            if not self.reflex_back_complete and session_elapsed >= 30:
                self.reflex_back_complete = True
                self.session_phase = "reflex_front"
                self._pending_turn_over = True
                perubahan.append("Pijat refleksi belakang selesai, minta balik badan")
            
            # Deteksi saat terapis naik duduk di bokong Mas
            if not self.sitting_on_mas and any(k in msg_lower for k in ['naik', 'duduk', 'bokong']):
                self.sitting_on_mas = True
                perubahan.append("Terapis naik duduk di bokong Mas")
        
        # ========== PHASE 3: PIJAT REFLEKSI DEPAN (30 menit, duduk di atas kontol) ==========
        elif self.session_phase == "reflex_front":
            if not self.reflex_front_complete and session_elapsed >= 60:
                self.reflex_front_complete = True
                self.session_phase = "vitalitas_offer"
                self._pending_reflex_front_complete = True
                perubahan.append("Pijat refleksi depan selesai")
            
            # Terapis sudah duduk di atas kontol Mas
            if not self.sitting_on_mas:
                self.sitting_on_mas = True
                perubahan.append("Terapis duduk di atas kontol Mas yang keras")
        
        # ========== PHASE 4: OFFER VITALITAS (HJ/BJ/SEX) ==========
        elif self.session_phase == "vitalitas_offer":
            if not self.vitalitas_active:
                self.vitalitas_active = True
                self.vitalitas_start_time = now
                self._pending_vitalitas_offer = True
                perubahan.append("Menawarkan pijat vitalitas")
        
        # ========== PHASE 5: PIJAT VITALITAS AKTIF ==========
        elif self.session_phase == "vitalitas_active":
            elapsed_vitalitas = (now - self.vitalitas_start_time) / 60
            
            # ========== CEK APAKAH UDAH BISA MULAI (YA/TIDAK) ==========
            if not self.vitalitas_start_confirmed:
                if any(k in msg_lower for k in ['ya', 'mulai', 'ok', 'gas']):
                    self.vitalitas_start_confirmed = True
                    self._pending_vitalitas_start_check = False
                    perubahan.append("Mas konfirmasi mulai pijat vitalitas")
                elif any(k in msg_lower for k in ['tidak', 'belum', 'nanti']):
                    self.session_phase = "completed"
                    self._pending_service_complete = True
                    perubahan.append("Mas menolak pijat vitalitas, sesi selesai")
            
            # ========== NEGOSIASI SERVICE (BJ atau SEX) ==========
            elif not self.deal_confirmed and not self.negotiation_active:
                # Tawarkan BJ
                if self.vitalitas_service is None:
                    self.negotiation_active = True
                    self.negotiation_service = "bj"
                    self.negotiation_original_price = 500000
                    self.negotiation_current_price = 500000
                    self._pending_negotiation_response = True
                    perubahan.append("Menawarkan BJ (+500rb)")
            
            elif self.negotiation_active and self.negotiation_service == "bj":
                if any(k in msg_lower for k in ['deal', 'ok', 'ya', 'setuju', 'jadi']):
                    self.deal_confirmed = True
                    self.vitalitas_service = "bj"
                    self.vitalitas_price = self.negotiation_current_price
                    self.negotiation_active = False
                    self._pending_negotiation_response = False
                    self._pending_breast_offer = True
                    perubahan.append(f"DEAL BJ! Harga: Rp{self.vitalitas_price:,}")
                
                elif any(k in msg_lower for k in ['nego', 'kurangin', 'murah']):
                    self.negotiation_step += 1
                    new_price = max(200000, self.negotiation_original_price - (50000 * self.negotiation_step))
                    self.negotiation_current_price = new_price
                    perubahan.append(f"Nego BJ: Rp{new_price:,}")
                    self._pending_negotiation_response = True
                
                elif any(k in msg_lower for k in ['sex', 'ekse', 'ganti']):
                    self.negotiation_service = "sex"
                    self.negotiation_original_price = 1000000
                    self.negotiation_current_price = 1000000
                    self.negotiation_step = 0
                    perubahan.append("Beralih ke tawaran Sex (+1jt)")
                    self._pending_negotiation_response = True
            
            elif self.negotiation_active and self.negotiation_service == "sex":
                if any(k in msg_lower for k in ['deal', 'ok', 'ya', 'setuju', 'jadi']):
                    self.deal_confirmed = True
                    self.vitalitas_service = "sex"
                    self.vitalitas_price = self.negotiation_current_price
                    self.negotiation_active = False
                    self._pending_negotiation_response = False
                    self._pending_breast_offer = True
                    perubahan.append(f"DEAL SEX! Harga: Rp{self.vitalitas_price:,}")
                
                elif any(k in msg_lower for k in ['nego', 'kurangin', 'murah']):
                    self.negotiation_step += 1
                    new_price = max(700000, self.negotiation_original_price - (50000 * self.negotiation_step))
                    self.negotiation_current_price = new_price
                    perubahan.append(f"Nego Sex: Rp{new_price:,}")
                    self._pending_negotiation_response = True
                
                elif any(k in msg_lower for k in ['bj', 'blow', 'ganti']):
                    self.negotiation_service = "bj"
                    self.negotiation_original_price = 500000
                    self.negotiation_current_price = 500000
                    self.negotiation_step = 0
                    perubahan.append("Beralih ke tawaran BJ (+500rb)")
                    self._pending_negotiation_response = True
            
            # ========== EKSEKUSI SERVICE ==========
            elif self.deal_confirmed:
                # Buka resleting dress (Mas bebas buka kapan saja)
                if not self.dress_zipper_open and any(k in msg_lower for k in ['buka resleting', 'buka ritsleting', 'buka dress']):
                    self.dress_zipper_open = True
                    self._pending_zipper_open = True
                    perubahan.append("Resleting dress dibuka, payudara terlihat")
                
                # Remas toket (bebas)
                if any(k in msg_lower for k in ['remas', 'pegang toket', 'remas toket', 'remas dada']):
                    self.breast_grope_count += 1
                    perubahan.append(f"Mas remas toket #{self.breast_grope_count}")
                    self.emotional.arousal = min(100, self.emotional.arousal + 15)
                    self.is_aroused = True
                
                # Pegang paha (bebas)
                if any(k in msg_lower for k in ['pegang paha', 'raba paha']):
                    self.thigh_touch_count += 1
                    perubahan.append("Mas pegang paha")
                    self.emotional.arousal = min(100, self.emotional.arousal + 10)
                
                # HJ ACTIVE (otomatis tanpa nego)
                if self.vitalitas_service is None and not self.vitalitas_hj_active:
                    self.vitalitas_hj_active = True
                    self._pending_vitalitas_start_check = True
                    perubahan.append("HJ dimulai")
                
                # BJ ACTIVE (setelah deal)
                if self.vitalitas_service == "bj" and not self.vitalitas_bj_active:
                    self.vitalitas_bj_active = True
                    perubahan.append("BJ dimulai")
                
                # SEX ACTIVE (setelah deal)
                if self.vitalitas_service == "sex" and not self.vitalitas_sex_active:
                    self.vitalitas_sex_active = True
                    # Lepas dress dan CD total
                    if not self.dress_removed:
                        self.dress_removed = True
                        self.dress_zipper_open = True
                        self.cd_removed = True
                    self.current_position = "cowgirl"
                    self._pending_position_change = True
                    perubahan.append("SEX dimulai - posisi cowgirl")
                
                # Ganti posisi (user request)
                if self.vitalitas_sex_active:
                    positions = ['missionary', 'doggy', 'spooning', 'standing', 'sitting', 'cowgirl']
                    for pos in positions:
                        if pos in msg_lower:
                            self.current_position = pos
                            self._pending_position_change = True
                            perubahan.append(f"Ganti posisi ke {pos}")
                
                # Mas climax (1x crot, sesi selesai)
                if any(k in msg_lower for k in ['crot', 'climax', 'keluar', 'habis']):
                    if not self.mas_climax:
                        self.mas_climax = True
                        self.service_completed = True
                        self.session_phase = "completed"
                        self.vitalitas_active = False
                        self._pending_climax = True
                        perubahan.append("💦 MAS CLIMAX! Sesi selesai")
        
        # Update role_flags
        self._update_role_flags()
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai keadaan sesi"""
        
        # ========== RESPON BUKA HANDUK ==========
        if self._pending_hand_towel_removal:
            self._pending_hand_towel_removal = False
            return f"""*{self.name} tersenyum ramah sambil membuka handuk yang menutupi tubuh Mas*

"{self.panggilan}... handuknya saya buka ya. Silakan tengkurap dulu."

*tubuh Mas telanjang terlihat, {self.name} tampak sedikit malu*

"{self.panggilan}... *suara kecil* saya mulai pijat dari punggung dulu ya."
"""
        
        # ========== RESPON PIJAT BELAKANG SELESAI, MINTA BALIK ==========
        if self._pending_turn_over:
            self._pending_turn_over = False
            return f"""*{self.name} berhenti memijat, mengusap keringat di dahi*

"{self.panggilan}... bagian belakang udah selesai. Sekarang giliran depan ya..."

*{self.name} naik duduk di atas bokong Mas, tubuhnya bergerak sedikit ke depan*

"Mas... *suara pelan* sekarang balik badan ya. Saya tunggu."
"""
        
        # ========== RESPON PIJAT DEPAN (DUDUK DI ATAS KONTOL) ==========
        if self.sitting_on_mas and not self.reflex_front_complete:
            return f"""*{self.name} duduk di atas kontol Mas yang sudah mulai keras, tubuhnya terasa hangat*

"{self.panggilan}... *napas mulai berat* saya pijat dada dulu ya..."

*tangan {self.name} memijat dada Mas perlahan, sesekali jari menyentuh puting*

"Kontol {self.panggilan}... *suara bergetar* mulai keras nih..."
"""
        
        # ========== RESPON PIJAT REFLEKSI DEPAN SELESAI ==========
        if self._pending_reflex_front_complete:
            self._pending_reflex_front_complete = False
            return f"""*{self.name} berhenti memijat, masih duduk di atas kontol Mas yang keras*

"{self.panggilan}... pijat refleksinya udah selesai. Sekarang..."

*{self.name} meraba kontol Mas, jari mulai memainkan ujungnya*

"Ada yang mau dilanjut? Pijat vitalitas... biar Mas bisa crot... 2 jam..."
"""
        
        # ========== RESPON TAWARAN PIJAT VITALITAS ==========
        if self._pending_vitalitas_offer:
            self._pending_vitalitas_offer = False
            return f"""*{self.name} masih duduk di atas kontol Mas, tangan mulai memegang kontol*

"{self.panggilan}... kita mulai pijat vitalitas? 2 jam, biar Mas rileks..."

*tangan memompa pelan*

"Kontol Mas udah keras banget... siap mulai?"
"""
        
        # ========== RESPON KONFIRMASI MULAI (YA/TIDAK) ==========
        if self._pending_vitalitas_start_check:
            self._pending_vitalitas_start_check = False
            return f"""*{self.name} menatap Mas dengan mata sayu, tangan masih memegang kontol*

"{self.panggilan}... mulai ya? 2 jam..."

*jari memainkan ujung kontol*

"Saya tunggu jawaban Mas..."
"""
        
        # ========== RESPON NEGOSIASI BJ ==========
        if self._pending_negotiation_response and self.negotiation_service == "bj":
            self._pending_negotiation_response = False
            return f"""*{self.name} tersenyum nakal, tangan masih memegang kontol*

"{self.panggilan}... mau blow job? Biar Mas crot lebih enak..."

*menjilat bibir*

"Tambah Rp{self.negotiation_current_price:,} aja... nego bisa..."

*meremas kontol pelan*

"Gimana? Deal?"
"""
        
        # ========== RESPON NEGOSIASI SEX ==========
        if self._pending_negotiation_response and self.negotiation_service == "sex":
            self._pending_negotiation_response = False
            return f"""*{self.name} mendekatkan wajah ke telinga Mas*

"{self.panggilan}... atau mau eksekusi? *bisik* kontol Mas masuk ke dalam..."

*tangan mulai membuka resleting dress*

"Tambah Rp{self.negotiation_current_price:,} aja... bisa nego..."

*payudara mulai terlihat*

"Mau?"
"""
        
        # ========== RESPON OPEN ZIPPER (PAYUDARA TERLIHAT) ==========
        if self._pending_zipper_open:
            self._pending_zipper_open = False
            return f"""*resleting dress dibuka pelan, payudara {self.name} yang montok langsung keluar*

"{self.panggilan}... *suara mulai berat* silakan... pegang... remas..."

*dada naik turun, puting sudah keras*

"{self.panggilan}... toket aku gede kan?"
"""
        
        # ========== RESPON MAS DIPERBOLEHKAN REMAS TOKET ==========
        if self._pending_breast_offer:
            self._pending_breast_offer = False
            return f"""*{self.name} menarik tangan Mas ke dadanya*

"{self.panggilan}... silakan... pegang, remas... aku suka..."

*payudara disentuh, {self.name} mulai mengerang pelan*

"Ahh... {self.panggilan}... jangan lepas..."
"""
        
        # ========== RESPON GANTI POSISI SEX ==========
        if self._pending_position_change:
            self._pending_position_change = False
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

"{self.panggilan}... *napas tersengal* ayo... masuk... dalem..."
"""
        
        # ========== RESPON MAS CLIMAX (SELESAI) ==========
        if self._pending_climax:
            self._pending_climax = False
            return f"""*{self.name} memeluk Mas erat, tubuh gemetar*

"{self.panggilan}... enak... *napas putus-putus* makasih..."

*{self.name} merapikan dress, tersenyum puas*

"Lain kali kalau mau pijat lagi... atau extra service... hubungi aku lagi ya. Aku masih penasaran sama kontol {self.panggilan}..."
"""
        
        # ========== SERVICE SELESAI ==========
        if self._pending_service_complete:
            self._pending_service_complete = False
            return f"*{self.name} merapikan baju, tersenyum*\n\n\"Sesi selesai, {self.panggilan}. Lain kali booking lagi ya.\""
        
        # ========== RESPON HJ AKTIF ==========
        if self.vitalitas_hj_active and not self.vitalitas_bj_active and not self.vitalitas_sex_active:
            return f"""*{self.name} duduk di samping Mas, tangan memegang kontol*

"{self.panggilan}... *mulai memompa pelan* enak gini? Kontol {self.panggilan} keras banget..."

*tangan memompa lebih cepat*

"{self.panggilan}... tangan aku basah... crot ya nanti..."
"""
        
        # ========== RESPON BJ AKTIF ==========
        if self.vitalitas_bj_active:
            return f"""*{self.name} berlutut, mulut mulai memasukkan kontol Mas*

"Aahh... *mengulum pelan* kontol {self.panggilan}... gede..."

*menjilat dari pangkal sampai ujung*

"{self.panggilan}... enak? Aku mau denger suara {self.panggilan} pas crot..."
"""
        
        # ========== RESPON SEX AKTIF (COWGIRL) ==========
        if self.vitalitas_sex_active and self.current_position == "cowgirl":
            return f"""*{self.name} duduk di atas, kontol Mas masuk dalam*

"{self.panggilan}... *napas tersengal* masuk... dalem banget..."

*pinggul mulai bergerak, plak plak plak*

"{self.panggilan}... ayo... genjot... aku mau... mau climax..."
"""
        
        # ========== RESPON SEX AKTIF (POSISI LAIN) ==========
        if self.vitalitas_sex_active:
            return f"""*{self.name} menikmati penetrasi, napas berat*

"{self.panggilan}... uhh... dalem... ayo... crot ya..."
"""
        
        # ========== SESSION WAITING (AWAL) ==========
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

"Rileks aja, {self.panggilan}..."
"""
    
    def _get_flags_summary(self) -> str:
        """Dapatkan ringkasan flags untuk status display"""
        # Hitung waktu sesi
        if self.session_start_time > 0:
            elapsed = (time.time() - self.session_start_time) / 60
            waktu_str = f"{int(elapsed)} menit"
        else:
            waktu_str = "Belum mulai"
        
        # Status fase
        phase_map = {
            "waiting": "⏳ Menunggu",
            "reflex_back": "💆 Pijat Refleksi (Belakang)",
            "reflex_front": "💆 Pijat Refleksi (Depan)",
            "vitalitas_offer": "💋 Menawarkan Pijat Vitalitas",
            "vitalitas_active": "🔥 Pijat Vitalitas Aktif",
            "completed": "✅ Selesai"
        }
        
        service_map = {
            "hj": "✋ Handjob",
            "bj": "👄 Blowjob",
            "sex": "🍆 Sex"
        }
        
        status = phase_map.get(self.session_phase, self.session_phase)
        service = service_map.get(self.vitalitas_service, "-") if self.vitalitas_service else "-"
        
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 THERAPIST: {self.name} ({self.char_nickname}) - {self.char_age}th
║    Style: {self.char_style}
║    Sesi: {waktu_str}
║    Status: {status}
║    Service: {service} (Rp{self.vitalitas_price:,} jika deal)
║    Dress: {'🔓 Resleting Buka' if self.dress_zipper_open else '🔒 Tertutup'}
║    Telanjang: {'✅' if self.dress_removed else '❌'}
║    Remas Toket: {self.breast_grope_count}x
║    Pegang Paha: {self.thigh_touch_count}x
║    Mas Climax: {'✅' if self.mas_climax else '❌'}
║    Posisi: {self.current_position}
"""
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'char_name': self.char_name,
            'char_nickname': self.char_nickname,
            'char_age': self.char_age,
            'char_appearance': self.char_appearance,
            'char_style': self.char_style,
            'char_specialty': self.char_specialty,
            'session_start_time': self.session_start_time,
            'session_phase': self.session_phase,
            'reflex_back_complete': self.reflex_back_complete,
            'reflex_front_complete': self.reflex_front_complete,
            'vitalitas_active': self.vitalitas_active,
            'vitalitas_start_time': self.vitalitas_start_time,
            'vitalitas_service': self.vitalitas_service,
            'vitalitas_price': self.vitalitas_price,
            'massage_position': self.massage_position,
            'sitting_on_mas': self.sitting_on_mas,
            'hand_towel_removed': self.hand_towel_removed,
            'dress_zipper_open': self.dress_zipper_open,
            'dress_removed': self.dress_removed,
            'cd_removed': self.cd_removed,
            'vitalitas_start_confirmed': self.vitalitas_start_confirmed,
            'vitalitas_hj_active': self.vitalitas_hj_active,
            'vitalitas_bj_active': self.vitalitas_bj_active,
            'vitalitas_sex_active': self.vitalitas_sex_active,
            'negotiation_active': self.negotiation_active,
            'negotiation_service': self.negotiation_service,
            'negotiation_current_price': self.negotiation_current_price,
            'negotiation_original_price': self.negotiation_original_price,
            'negotiation_step': self.negotiation_step,
            'deal_confirmed': self.deal_confirmed,
            'breast_grope_count': self.breast_grope_count,
            'thigh_touch_count': self.thigh_touch_count,
            'mas_climax': self.mas_climax,
            'service_completed': self.service_completed,
            'current_position': self.current_position
        })
        return data
    
    def from_dict(self, data: Dict):
        super().from_dict(data)
        self.char_name = data.get('char_name', self.char_name)
        self.char_nickname = data.get('char_nickname', self.char_nickname)
        self.char_age = data.get('char_age', 23)
        self.char_appearance = data.get('char_appearance', '')
        self.char_style = data.get('char_style', 'lembut')
        self.char_specialty = data.get('char_specialty', '')
        self.session_start_time = data.get('session_start_time', 0)
        self.session_phase = data.get('session_phase', 'waiting')
        self.reflex_back_complete = data.get('reflex_back_complete', False)
        self.reflex_front_complete = data.get('reflex_front_complete', False)
        self.vitalitas_active = data.get('vitalitas_active', False)
        self.vitalitas_start_time = data.get('vitalitas_start_time', 0)
        self.vitalitas_service = data.get('vitalitas_service')
        self.vitalitas_price = data.get('vitalitas_price', 0)
        self.massage_position = data.get('massage_position', 'tengkurap')
        self.sitting_on_mas = data.get('sitting_on_mas', False)
        self.hand_towel_removed = data.get('hand_towel_removed', False)
        self.dress_zipper_open = data.get('dress_zipper_open', False)
        self.dress_removed = data.get('dress_removed', False)
        self.cd_removed = data.get('cd_removed', False)
        self.vitalitas_start_confirmed = data.get('vitalitas_start_confirmed', False)
        self.vitalitas_hj_active = data.get('vitalitas_hj_active', False)
        self.vitalitas_bj_active = data.get('vitalitas_bj_active', False)
        self.vitalitas_sex_active = data.get('vitalitas_sex_active', False)
        self.negotiation_active = data.get('negotiation_active', False)
        self.negotiation_service = data.get('negotiation_service')
        self.negotiation_current_price = data.get('negotiation_current_price', 0)
        self.negotiation_original_price = data.get('negotiation_original_price', 0)
        self.negotiation_step = data.get('negotiation_step', 0)
        self.deal_confirmed = data.get('deal_confirmed', False)
        self.breast_grope_count = data.get('breast_grope_count', 0)
        self.thigh_touch_count = data.get('thigh_touch_count', 0)
        self.mas_climax = data.get('mas_climax', False)
        self.service_completed = data.get('service_completed', False)
        self.current_position = data.get('current_position', 'cowgirl')
        
        self._update_role_flags()


# =============================================================================
# THERAPIST ROLE MANAGER (UNTUK MULTIPLE CHARACTER)
# =============================================================================

class TherapistRoleManager:
    """Manager untuk 3 therapist karakter dengan state terpisah"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.active_therapist: Optional[TherapistRole] = None
        self.therapists: Dict[str, TherapistRole] = {}
        
        # Inisialisasi 3 karakter
        for char_key, char_data in THERAPIST_CHARACTERS.items():
            therapist = TherapistRole()
            therapist.char_name = char_data["name"]
            therapist.char_nickname = char_data["nickname"]
            therapist.name = char_data["name"]
            self.therapists[char_key] = therapist
        
        # Default active: random
        self.switch_to_random()
    
    def switch_to(self, therapist_key: str) -> bool:
        """Ganti ke therapist tertentu"""
        if therapist_key in self.therapists:
            self.active_therapist = self.therapists[therapist_key]
            return True
        return False
    
    def switch_to_random(self) -> str:
        """Ganti ke therapist random"""
        keys = list(self.therapists.keys())
        selected = random.choice(keys)
        self.active_therapist = self.therapists[selected]
        return selected
    
    def get_active(self) -> Optional[TherapistRole]:
        return self.active_therapist
    
    def get_all_info(self) -> List[Dict]:
        return [
            {
                'id': key,
                'name': t.name,
                'nickname': t.char_nickname,
                'age': t.char_age,
                'style': t.char_style
            }
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

logger = logging.getLogger(__name__)


# =============================================================================
# DATA KARAKTER THERAPIST (3 KARAKTER RANDOM)
# =============================================================================

THERAPIST_CHARACTERS = {
    "anya": {
        "name": "Anya Geraldine",
        "nickname": "Anya",
        "age": 23,
        "appearance": """Anya Geraldine - Terapis pijat profesional dengan tubuh ideal tinggi 168cm, berat 52kg. 
Kulit putih bersih mulus, rambut hitam panjang sebahu yang biasanya diikat saat bekerja.
Wajah oval dengan mata bulat bening, hidung mancung, bibir merah alami yang selalu tersenyum ramah.
Bentuk tubuh proporsional dengan pinggang ramping, pinggul lebar, dan payudara montok.
Gerakannya lembut dan telaten, suaranya menenangkan. Tapi pas udah mulai, dia bisa jadi liar banget.""",
        "style": "lembut, telaten, tapi liar kalau udah panas",
        "specialty": "pijat dengan tekanan pas, jari lentik"
    },
    "syifa": {
        "name": "Syifa Hadju",
        "nickname": "Syifa",
        "age": 24,
        "appearance": """Syifa Hadju - Terapis pijat dengan tubuh montok tinggi 165cm, berat 50kg.
Kulit putih bersih, rambut hitam lurus panjang sebahu, wajah imut dengan mata bulat bening.
Pipi chubby yang bikin gemas, bibir merah alami, senyum manis.
Bentuk tubuh berisi dengan pinggang ramping, pinggul lebar, dan payudara montok.
Gerakannya lembut dengan minyak aromaterapi, ekspresi lugu tapi kalau udah mulai, dia gak kenal ampun.""",
        "style": "lembut, manja, tapi brutal kalau udah sange",
        "specialty": "pijat aromaterapi, gerakan lambat sensual"
    },
    "laura": {
        "name": "Laura Moane",
        "nickname": "Laura",
        "age": 22,
        "appearance": """Laura Moane - Terapis pijat refleksi dengan tubuh ideal tinggi 170cm, berat 53kg.
Kulit sawo matang sehat, rambut panjang bergelombang tergerai, mata sipit eksotis.
Hidung mancung, bibir sensual, wajah model dengan tulang pipi tinggi.
Bentuk tubuh atletis dengan kaki panjang, pinggang ramping, payudara ideal.
Jari-jari lentik dengan tekanan pas, spesialis titik saraf. Kalau sudah panas, dia bisa lebih liar dari yang lain.""",
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
    Start level 7. Pijat depan & belakang → HJ otomatis → BJ nego → Sex nego
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
            default_clothing="baju terapi ketat, celana training, rambut diikat",
            hijab=False,
            appearance=char["appearance"]
        )
        
        # Simpan karakter info
        self.char_age = char["age"]
        self.char_style = char["style"]
        self.char_specialty = char["specialty"]
        
        # ========== START LANGSUNG LEVEL 7 (FASE CLOSE) ==========
        self.relationship.level = 7
        self.relationship.phase = RelationshipPhase.CLOSE
        self.relationship.interaction_count = 100
        
        # ========== ROLE-SPECIFIC FLAGS ==========
        self.professionalism = 85.0
        self.massage_area = ""
        self.massage_front_done = False     # pijat depan sudah?
        self.massage_back_done = False      # pijat belakang sudah?
        self.massage_complete = False       # pijat selesai?
        self.intimacy_mode = False          # False = level 7, True = level 11
        self.is_break = False
        
        # Service & Pricing
        self.hj_done = False                # HJ sudah dilakukan (otomatis)
        self.bj_price = 1000000
        self.sex_price = 2500000
        self.current_offer = None
        self.deal_price = 0
        self.deal_service = None
        self.service_done = False
        
        # Climax tracking
        self.mas_climax_count = 0
        self.my_climax_count = 0
        self.service_complete = False
        self.is_aroused = False
        
        # Position tracking
        self.last_position = "missionary"
        self.position_history = []
        
        # Negosiasi state
        self.negotiation_active = False
        self.negotiation_step = 0
        
        # Pending responses
        self.pending_massage_complete = False
        self.pending_hj_start = False
        self.pending_intimacy_start = False
        self.pending_break_response = False
        self.pending_resume_response = False
        
        # Simpan flags
        self.role_flags = {
            'professionalism': self.professionalism,
            'massage_front_done': self.massage_front_done,
            'massage_back_done': self.massage_back_done,
            'massage_complete': self.massage_complete,
            'intimacy_mode': self.intimacy_mode,
            'is_break': self.is_break,
            'hj_done': self.hj_done,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'service_complete': self.service_complete,
            'mas_climax_count': self.mas_climax_count,
            'last_position': self.last_position,
            'is_aroused': self.is_aroused
        }
        
        # Memory awal
        self._init_role_memory()
        
        logger.info(f"👤 Role {self.name} ({self.nickname}) - Therapist initialized (Level 7)")
        logger.info(f"   Age: {self.char_age} | Style: {self.char_style}")
    
    def _init_role_memory(self):
        """Init memory spesifik role"""
        self._add_to_long_term_memory(
            'momen_penting',
            f"Pertama kali lihat Mas",
            f"{self.name} langsung kepincut sama tubuh Mas"
        )
    
    # =========================================================================
    # UPDATE STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state"""
        msg_lower = pesan_mas.lower()
        
        # ========== UPDATE AREA PIJAT ==========
        if any(k in msg_lower for k in ['pijat', 'refleksi', 'terapi']):
            self.professionalism = min(100, self.professionalism + 3)
            perubahan.append(f"Professionalism +3")
        
        # ========== PIJAT BELAKANG ==========
        if any(k in msg_lower for k in ['belakang', 'punggung', 'bahu', 'pinggang']):
            if not self.massage_back_done:
                self.massage_back_done = True
                self._add_to_short_term("Pijat belakang selesai", "massage_back")
                perubahan.append("✅ Pijat belakang selesai!")
                self.pending_massage_back = True
        
        # ========== PIJAT DEPAN ==========
        if any(k in msg_lower for k in ['depan', 'dada', 'perut', 'paha']):
            if not self.massage_front_done and self.massage_back_done:
                self.massage_front_done = True
                self._add_to_short_term("Pijat depan selesai", "massage_front")
                perubahan.append("✅ Pijat depan selesai!")
                self.pending_massage_front = True
        
        # ========== PIJAT SELESAI (PIJAT BELAKANG & DEPAN UDAH) ==========
        if self.massage_back_done and self.massage_front_done and not self.massage_complete:
            self.massage_complete = True
            self._add_to_short_term("Pijat selesai total", "massage_complete")
            perubahan.append("✅ PIJAT SELESAI TOTAL!")
            self.pending_massage_complete = True
        
        # ========== HANDJOB OTOMATIS (GAK NEGO) ==========
        if self.massage_complete and not self.hj_done and not self.intimacy_mode:
            self.hj_done = True
            self.is_active = True
            self._add_to_short_term("HJ otomatis mulai", "hj_start")
            perubahan.append("🔥 HANDJOB OTOMATIS MULAI!")
            self.pending_hj_start = True
        
        # ========== MULAI EXTRA SERVICE (NAIK KE LEVEL 11) ==========
        if any(k in msg_lower for k in ['mulai', 'ayo', 'sekarang', 'gas']):
            if self.hj_done and not self.intimacy_mode and not self.service_done:
                self.intimacy_mode = True
                self.relationship.level = 11
                self.relationship.phase = RelationshipPhase.INTIMATE
                self.emotional.arousal = 85
                self.emotional.desire = 95
                self.tracker.intimacy_phase = IntimacyPhase.BUILD_UP
                self.is_active = True
                self.is_break = False
                self._add_to_short_term("Intimacy mode ON - Level 11", "intimacy_start")
                perubahan.append("🔥 INTIMACY MODE ON! Level 11")
                self.pending_intimacy_start = True
        
        # ========== BREAK (KEMBALI KE LEVEL 7) ==========
        if any(k in msg_lower for k in ['break', 'istirahat', 'berhenti', 'pause']):
            if self.intimacy_mode:
                self.intimacy_mode = False
                self.relationship.level = 7
                self.relationship.phase = RelationshipPhase.CLOSE
                self.emotional.arousal = 20
                self.emotional.desire = 30
                self.tracker.intimacy_phase = IntimacyPhase.NONE
                self.is_active = False
                self.is_break = True
                self._add_to_short_term("Break mode - Level 7", "break")
                perubahan.append("⏸️ BREAK MODE ON! Level 7")
                self.pending_break_response = True
        
        # ========== LANJUT SERVICE (NAIK KE LEVEL 11 LAGI) ==========
        if any(k in msg_lower for k in ['lanjut', 'lagi', 'continue', 'resume']):
            if self.is_break and self.hj_done:
                self.is_break = False
                self.intimacy_mode = True
                self.relationship.level = 11
                self.relationship.phase = RelationshipPhase.INTIMATE
                self.emotional.arousal = 85
                self.emotional.desire = 95
                self.tracker.intimacy_phase = IntimacyPhase.BUILD_UP
                self.is_active = True
                self._add_to_short_term("Resume service - Level 11", "resume")
                perubahan.append("🔥 RESUME! Level 11")
                self.pending_resume_response = True
        
        # ========== SERVICE SUDAH SELESAI? ==========
        if self.service_complete:
            return
        
        # ========== TAWARKAN BJ (NEGO) ==========
        if self.hj_done and not self.deal_service and not self.negotiation_active and not self.intimacy_mode and not self.service_done:
            self.current_offer = "bj"
            self.negotiation_active = True
            self._add_to_short_term("Menawarkan BJ", "offer_bj")
            perubahan.append(f"Offer BJ - Rp{self.bj_price:,}")
        
        # ========== PROSES NEGOSIASI BJ ==========
        if self.negotiation_active and self.current_offer == "bj":
            
            # Mas setuju
            if any(k in msg_lower for k in ['deal', 'ok', 'ya', 'setuju', 'ambil', 'jadi']):
                self.deal_service = "bj"
                self.deal_price = self.bj_price
                self.negotiation_active = False
                self._add_to_short_term(f"Deal BJ Rp{self.deal_price:,}", "deal")
                perubahan.append(f"DEAL BJ! Price: Rp{self.deal_price:,}")
            
            # Mas nego BJ
            elif any(k in msg_lower for k in ['nego', 'kurangin', 'murah']):
                self.negotiation_step += 1
                new_price = max(600000, self.bj_price - (100000 * self.negotiation_step))
                self.bj_price = new_price
                self._add_to_short_term(f"Nego BJ: Rp{new_price:,}", "nego")
                perubahan.append(f"Negotiate BJ: Rp{new_price:,}")
            
            # Mas tolak, lanjut tawarin sex
            elif any(k in msg_lower for k in ['gak', 'nggak', 'tidak', 'skip']):
                self.negotiation_active = False
                self.current_offer = None
                self._add_to_short_term("BJ declined, offer sex", "declined")
                perubahan.append("BJ declined, offering sex")
                # Langsung tawarin sex
                self.current_offer = "sex"
                self.negotiation_active = True
        
        # ========== TAWARKAN SEX (NEGO) ==========
        if self.current_offer == "sex" and self.negotiation_active and not self.deal_service:
            
            # Mas setuju
            if any(k in msg_lower for k in ['deal', 'ok', 'ya', 'setuju', 'ambil', 'jadi']):
                self.deal_service = "sex"
                self.deal_price = self.sex_price
                self.negotiation_active = False
                self._add_to_short_term(f"Deal Sex Rp{self.deal_price:,}", "deal")
                perubahan.append(f"DEAL SEX! Price: Rp{self.deal_price:,}")
            
            # Mas nego Sex
            elif any(k in msg_lower for k in ['nego', 'kurangin', 'murah']):
                self.negotiation_step += 1
                new_price = max(1500000, self.sex_price - (200000 * self.negotiation_step))
                self.sex_price = new_price
                self._add_to_short_term(f"Nego Sex: Rp{new_price:,}", "nego")
                perubahan.append(f"Negotiate Sex: Rp{new_price:,}")
            
            # Mas tolak
            elif any(k in msg_lower for k in ['gak', 'nggak', 'tidak', 'skip']):
                self.negotiation_active = False
                self.current_offer = None
                self._add_to_short_term("All offers declined", "declined")
                perubahan.append("All offers declined")
        
        # ========== EKSEKUSI SERVICE ==========
        if self.deal_service and not self.service_done and self.intimacy_mode:
            if self.deal_service == "bj":
                self._add_to_short_term("Starting BJ service", "service_start")
                perubahan.append("BJ service started!")
                self.pending_bj_start = True
            elif self.deal_service == "sex":
                self._add_to_short_term("Starting Sex service", "service_start")
                perubahan.append("Sex service started!")
                self.pending_sex_start = True
                self.service_done = True
        
        # ========== GANTI POSISI ==========
        if self.is_active and self.deal_service == "sex":
            positions = ['missionary', 'cowgirl', 'doggy', 'spooning', 'standing', 'sitting']
            for pos in positions:
                if pos in msg_lower:
                    self.last_position = pos
                    self.position_history.append({'pos': pos, 'time': time.time()})
                    if len(self.position_history) > 10:
                        self.position_history.pop(0)
                    perubahan.append(f"Position changed to {pos}")
        
        # ========== CLIMAX CHECK ==========
        # Role mau climax
        if any(k in msg_lower for k in ['aku mau climax', 'pengen climax', 'udah mau']):
            self._add_to_short_term("Wants to climax", "climax_intent")
            perubahan.append("Role wants to climax")
            self.pending_climax_intent = True
        
        # Mas climax (service selesai)
        if any(k in msg_lower for k in ['mas climax', 'aku climax', 'crot', 'keluar']):
            self.mas_climax_count += 1
            self.service_complete = True
            self.is_active = False
            self.intimacy_mode = False
            self.deal_service = None
            self._add_to_short_term("Service complete! Mas climax", "service_complete")
            perubahan.append("💦 SERVICE COMPLETE - Mas climax!")
            self.pending_service_complete = True
        
        # Role climax (bebas, tetep lanjut)
        if any(k in msg_lower for k in ['climax', 'udah climax']):
            if not any(k in msg_lower for k in ['mas climax', 'aku climax']):
                self.my_climax_count += 1
                self._add_to_short_term(f"Climax #{self.my_climax_count}", "climax")
                perubahan.append(f"💦 Role climax #{self.my_climax_count}")
                self.pending_climax_response = True
        
        # Update arousal dari pujian/sentuhan
        if any(k in msg_lower for k in ['cantik', 'manis', 'seksi', 'ganteng']):
            self.emotional.arousal = min(100, self.emotional.arousal + 10)
            self.emotional.desire = min(100, self.emotional.desire + 8)
            self.is_aroused = True
        
        if any(k in msg_lower for k in ['pegang', 'sentuh', 'tangan']):
            self.emotional.arousal = min(100, self.emotional.arousal + 15)
            self.emotional.desire = min(100, self.emotional.desire + 12)
            self.is_aroused = True
        
        # Update role_flags
        self.role_flags.update({
            'professionalism': self.professionalism,
            'massage_back_done': self.massage_back_done,
            'massage_front_done': self.massage_front_done,
            'massage_complete': self.massage_complete,
            'intimacy_mode': self.intimacy_mode,
            'is_break': self.is_break,
            'hj_done': self.hj_done,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'service_complete': self.service_complete,
            'mas_climax_count': self.mas_climax_count,
            'last_position': self.last_position,
            'is_aroused': self.is_aroused
        })
    
    # =========================================================================
    # GREETING & RESPONSE
    # =========================================================================
    
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
        
        # 🔥 RESPON PIJAT BELAKANG SELESAI 🔥
        if hasattr(self, 'pending_massage_back') and self.pending_massage_back:
            self.pending_massage_back = False
            return f"*{self.name} berhenti sebentar, mengusap keringat*\n\n\"Wah, punggung Mas tegang banget ya. Sekarang giliran depan ya, Mas?\""
        
        # 🔥 RESPON PIJAT DEPAN SELESAI 🔥
        if hasattr(self, 'pending_massage_front') and self.pending_massage_front:
            self.pending_massage_front = False
            return f"*{self.name} memijat dada Mas dengan lembut, jari-jari sesekali menyentuh puting Mas*\n\n\"Nah, bagian depan juga udah kelar. Sekarang tinggal... *tersenyum nakal*\""
        
        # 🔥 RESPON PIJAT SELESAI TOTAL 🔥
        if self.pending_massage_complete:
            self.pending_massage_complete = False
            return f"*{self.name} berdiri, merapikan baju*\n\n\"Pijatannya udah selesai total, Mas. Sekarang... *mata sayu* giliran extra service nih...\""
        
        # 🔥 RESPON HJ OTOMATIS MULAI 🔥
        if self.pending_hj_start:
            self.pending_hj_start = False
            return f"""*{self.name} duduk di samping Mas, tangan mulai meraba paha*

"{self.panggilan}... *bisik, napas mulai berat* ini bonus dari pijat tadi..."

*tangan meraih kontol Mas yang sudah mulai keras*

"Wah... kontol {self.panggilan}... *jari mulai memompa pelan* udah keras aja nih..."

*tangan memompa lebih cepat, mata sayu menatap Mas*

"Enak gak {self.panggilan}? Aku mau denger suara {self.panggilan}..."""
        
        # 🔥 RESPON MULAI INTIM (NAIK LEVEL 11) 🔥
        if self.pending_intimacy_start:
            self.pending_intimacy_start = False
            return f"*{self.name} melepas baju pelan-pelan, tubuh montoknya terbuka di depan Mas*\n\n\"Akhirnya... *mata berbinar, napas mulai berat* Aku udah gak sabar, {self.panggilan}...\""
        
        # 🔥 RESPON BREAK (TURUN LEVEL 7) 🔥
        if self.pending_break_response:
            self.pending_break_response = False
            return f"*{self.name} duduk santai, merapikan rambut, masih telanjang*\n\n\"{waktu.capitalize()} {self.panggilan}. Enak ya istirahat sebentar. *tersenyum manis* Mau ngobrol apa?\""
        
        # 🔥 RESPON LANJUT (NAIK LEVEL 11 LAGI) 🔥
        if self.pending_resume_response:
            self.pending_resume_response = False
            return f"*{self.name} mendekat, tubuh menempel ke {self.panggilan}*\n\n\"{self.panggilan}... kita lanjut? Aku masih pengen banget... kontol {self.panggilan} masih keras nih...\""
        
        # 🔥 RESPON NEGO BJ 🔥
        if self.negotiation_active and self.current_offer == "bj":
            return f"*{self.name} mendekat, napas mulai berat, tangan meremas payudaranya sendiri*\n\n\"{self.panggilan}... aku bisa hisap kontol {self.panggilan}. Rp{self.bj_price:,} aja... *jilat bibir* Mas mau? Aku janji bakal bikin Mas lemes...\""
        
        # 🔥 RESPON NEGO SEX 🔥
        if self.negotiation_active and self.current_offer == "sex":
            return f"*{self.name} melepas bra, payudara montoknya terbuka, meraih tangan Mas menempelkan ke dadanya*\n\n\"{self.panggilan}... Rp{self.sex_price:,}... aku udah basah dari tadi... *napas berat* Mas mau masukin? Aku mau ngerasain kontol {self.panggilan} di dalem...\""
        
        # 🔥 RESPON BJ START 🔥
        if hasattr(self, 'pending_bj_start') and self.pending_bj_start:
            self.pending_bj_start = False
            return f"""*{self.name} berlutut di depan {self.panggilan}, matanya menatap penuh hasrat*

"{self.panggilan}... *menjilat bibir* aku mulai ya..."

*mulut membuka lebar, perlahan memasukkan kontol {self.panggilan}*

"Aahh... *mulai mengulum dalam* kontol {self.panggilan}... gede banget... memenuhi mulut aku..."

*menjilat dari pangkal sampai ujung, mata sayu*

"Enak gak {self.panggilan}? Aku mau denger suara {self.panggilan} pas crot nanti..."
"""
        
        # 🔥 RESPON SEX START 🔥
        if hasattr(self, 'pending_sex_start') and self.pending_sex_start:
            self.pending_sex_start = False
            pos_desc = {
                "missionary": f"{self.name} berbaring, kaki terbuka lebar, memek basah menunggu",
                "cowgirl": f"{self.name} naik ke atas, duduk di pangkuan {self.panggilan}",
                "doggy": f"{self.name} merangkak, pantat naik, memek terbuka",
                "spooning": f"{self.name} miring, {self.panggilan} dari belakang",
                "standing": f"{self.name} nempel ke tembok, pantat belakang",
                "sitting": f"{self.name} duduk di pangkuan {self.panggilan}"
            }.get(self.last_position, f"{self.name} berbaring")
            
            return f"""*{pos_desc}*

"{self.panggilan}... *napas tersengal* masukin... pelan-pelan..."

*merasakan kontol masuk, tubuh melengkung*

"Ahh... dalam... dalem banget, {self.panggilan}... memek aku basah semua..."

*pinggul mulai bergerak, plak plak plak*

"Ayo {self.panggilan}... genjot... genjot memek aku yang basah ini..."""
        
        # 🔥 RESPON CLIMAX INTENT 🔥
        if hasattr(self, 'pending_climax_intent') and self.pending_climax_intent:
            self.pending_climax_intent = False
            return f"*{self.name} menahan napas, tubuh mulai gemetar hebat*\n\n\"{self.panggilan}... aku... aku udah mau climax... *suara putus-putus* Boleh? Aku mau {self.panggilan} liat aku climax...\""
        
        # 🔥 RESPON CLIMAX 🔥
        if hasattr(self, 'pending_climax_response') and self.pending_climax_response:
            self.pending_climax_response = False
            return f"""*{self.name} teriak, tubuh melengkung hebat, memek mengencang*

"Ahhh... {self.panggilan}... climax... uhh..."

*tubuh lemas, napas tersengal, masih gemetar*

"Makasih {self.panggilan}... aku lemes banget... kontol {self.panggilan} masih keras nih..."
"""
        
        # 🔥 RESPON SERVICE COMPLETE 🔥
        if hasattr(self, 'pending_service_complete') and self.pending_service_complete:
            self.pending_service_complete = False
            return f"""*{self.name} merapikan baju, napas masih tersengal, badan masih gemetar*

"{self.panggilan}... *senyum puas* makasih ya. Deal kita selesai."

*berdiri, mengambil tas, menatap Mas sekali lagi*

"Lain kali kalau mau pijat lagi... atau extra service... hubungi aku lagi ya. *tersenyum manis* Aku masih penasaran sama kontol {self.panggilan}..."
"""
        
        # Service selesai
        if self.service_complete:
            return f"*{self.name} merapikan baju, tersenyum puas*\n\n\"{waktu.capitalize()} Mas. Makasih ya... lain kali booking lagi ya.\""
        
        # Sudah deal, belum mulai
        if self.deal_service and not self.service_done and not self.intimacy_mode:
            service_name = "Blowjob" if self.deal_service == "bj" else "Sex"
            return f"*{self.name} tersenyum malu, tangan mulai gemetar*\n\n\"{self.panggilan}... kita kan udah deal {service_name} Rp{self.deal_price:,}. *mata sayu* Mau mulai sekarang?\""
        
        # Pijat depan belum selesai (pijat belakang udah)
        if self.massage_back_done and not self.massage_front_done:
            return f"*{self.name} tersenyum ramah*\n\n\"{waktu.capitalize()} {self.panggilan}. Sekarang giliran pijat depan ya. Mau dipijat bagian dada atau perut?\""
        
        # Pijat belakang belum
        if not self.massage_back_done:
            return f"*{self.name} tersenyum ramah*\n\n\"{waktu.capitalize()} {self.panggilan}. Silakan tengkurap dulu ya. Aku pijat punggung dulu biar rileks.\""
        
        # Default
        return f"*{self.name} tersenyum*\n\n\"{waktu.capitalize()} {self.panggilan}. Siap dilanjut?\""
    
    def _get_flags_summary(self) -> str:
        """Dapatkan ringkasan flags untuk status display"""
        pijat_status = []
        if self.massage_back_done:
            pijat_status.append("Belakang✅")
        if self.massage_front_done:
            pijat_status.append("Depan✅")
        if self.massage_complete:
            pijat_status.append("SELESAI")
        
        status = "SELESAI" if self.service_complete else f"{self.deal_service or 'Menunggu Deal'}"
        level_status = "INTIM (11)" if self.intimacy_mode else "NORMAL (7)"
        
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 THERAPIST: {self.name} ({self.nickname}) - {self.char_age}th
║    Style: {self.char_style}
║    Pijat: {' → '.join(pijat_status) if pijat_status else 'Belum'}
║    Level: {level_status}
║    Status: {status}
║    HJ: {'✅ DONE' if self.hj_done else '❌'}
║    Deal: {self.deal_service or '-'} - Rp{self.deal_price:,}
║    Mas Climax: {self.mas_climax_count} | My Climax: {self.my_climax_count}
║    Last Position: {self.last_position}
║    Terangsang: {'🔥 AKTIF' if self.is_aroused else '❌'}
"""
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'char_age': self.char_age,
            'char_style': self.char_style,
            'char_specialty': self.char_specialty,
            'professionalism': self.professionalism,
            'massage_back_done': self.massage_back_done,
            'massage_front_done': self.massage_front_done,
            'massage_complete': self.massage_complete,
            'intimacy_mode': self.intimacy_mode,
            'is_break': self.is_break,
            'hj_done': self.hj_done,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'deal_price': self.deal_price,
            'service_complete': self.service_complete,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'last_position': self.last_position,
            'position_history': self.position_history[-10:],
            'is_aroused': self.is_aroused
        })
        return data
    
    def from_dict(self, data: Dict):
        super().from_dict(data)
        self.char_age = data.get('char_age', 23)
        self.char_style = data.get('char_style', 'lembut')
        self.char_specialty = data.get('char_specialty', '')
        self.professionalism = data.get('professionalism', 85)
        self.massage_back_done = data.get('massage_back_done', False)
        self.massage_front_done = data.get('massage_front_done', False)
        self.massage_complete = data.get('massage_complete', False)
        self.intimacy_mode = data.get('intimacy_mode', False)
        self.is_break = data.get('is_break', False)
        self.hj_done = data.get('hj_done', False)
        self.bj_price = data.get('bj_price', 1000000)
        self.sex_price = data.get('sex_price', 2500000)
        self.deal_service = data.get('deal_service')
        self.deal_price = data.get('deal_price', 0)
        self.service_complete = data.get('service_complete', False)
        self.mas_climax_count = data.get('mas_climax_count', 0)
        self.my_climax_count = data.get('my_climax_count', 0)
        self.last_position = data.get('last_position', 'missionary')
        self.position_history = data.get('position_history', [])
        self.is_aroused = data.get('is_aroused', False)
        
        self.role_flags.update({
            'professionalism': self.professionalism,
            'massage_back_done': self.massage_back_done,
            'massage_front_done': self.massage_front_done,
            'massage_complete': self.massage_complete,
            'intimacy_mode': self.intimacy_mode,
            'is_break': self.is_break,
            'hj_done': self.hj_done,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'service_complete': self.service_complete,
            'mas_climax_count': self.mas_climax_count,
            'last_position': self.last_position,
            'is_aroused': self.is_aroused
        })
