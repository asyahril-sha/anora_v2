"""
ANORA Ultimate - Therapist Role
3 Karakter Random: Anya Geraldine, Syifa Hadju, Laura Moane
Start level 7. Flow: Pijat refleksi 1 jam → Pijat vitalitas 2 jam
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
        
        # ========== SESSION STATE ==========
        self.session_start_time: float = 0
        self.session_phase: str = "waiting"  # waiting, reflex_back, reflex_front, vitalitas, completed
        self.reflex_back_complete: bool = False
        self.reflex_front_complete: bool = False
        self.vitalitas_active: bool = False
        self.vitalitas_start_time: float = 0
        self.vitalitas_service: str = None
        self.vitalitas_price: int = 0
        
        # Status Pijat
        self.massage_position: str = "tengkurap"
        self.sitting_on_mas: bool = False
        self.hand_towel_removed: bool = False
        
        # Dress & Resleting
        self.dress_zipper_open: bool = False
        self.dress_removed: bool = False
        self.cd_removed: bool = False
        
        # Pijat vitalitas
        self.vitalitas_start_confirmed: bool = False
        self.vitalitas_hj_active: bool = False
        self.vitalitas_bj_active: bool = False
        self.vitalitas_sex_active: bool = False
        
        # Negosiasi
        self.negotiation_active: bool = False
        self.negotiation_service: str = None
        self.negotiation_current_price: int = 0
        self.negotiation_original_price: int = 0
        self.negotiation_step: int = 0
        self.deal_confirmed: bool = False
        
        # Aktivitas fisik
        self.breast_grope_count: int = 0
        self.thigh_touch_count: int = 0
        
        # Climax
        self.mas_climax: bool = False
        self.service_completed: bool = False
        self.current_position: str = "cowgirl"
        
        # Pending responses
        self._pending_hand_towel_removal = False
        self._pending_turn_over = False
        self._pending_reflex_front_complete = False
        self._pending_vitalitas_offer = False
        self._pending_vitalitas_start_check = False
        self._pending_negotiation_response = False
        self._pending_breast_offer = False
        self._pending_zipper_open = False
        self._pending_position_change = False
        self._pending_climax = False
        self._pending_service_complete = False
        
        logger.info(f"👤 Role {self.name} ({self.nickname}) - Therapist initialized (Level 7)")
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai keadaan sesi"""
        
        # ========== RESPON BUKA HANDUK ==========
        if self._pending_hand_towel_removal:
            self._pending_hand_towel_removal = False
            return f"""*{self.name} tersenyum ramah sambil membuka handuk yang menutupi tubuh Mas*

"{self.panggilan}... handuknya saya buka ya. Silakan tengkurap dulu."

*tubuh Mas telanjang terlihat, {self.name} tampak sedikit malu*

"{self.panggilan}... *suara kecil* saya mulai pijat dari punggung dulu ya."""
        
        # ========== RESPON PIJAT BELAKANG SELESAI ==========
        if self._pending_turn_over:
            self._pending_turn_over = False
            return f"""*{self.name} berhenti memijat, mengusap keringat di dahi*

"{self.panggilan}... bagian belakang udah selesai. Sekarang giliran depan ya..."

*{self.name} naik duduk di atas bokong Mas*

"Mas... sekarang balik badan ya. Saya tunggu."""
        
        # ========== RESPON PIJAT DEPAN SELESAI ==========
        if self._pending_reflex_front_complete:
            self._pending_reflex_front_complete = False
            return f"""*{self.name} berhenti memijat, masih duduk di atas kontol Mas*

"{self.panggilan}... pijat refleksinya udah selesai. Sekarang..."

*{self.name} meraba kontol Mas*

"Ada yang mau dilanjut? Pijat vitalitas... biar Mas bisa crot... 2 jam..."""
        
        # ========== RESPON TAWARAN PIJAT VITALITAS ==========
        if self._pending_vitalitas_offer:
            self._pending_vitalitas_offer = False
            return f"""*{self.name} masih duduk di atas kontol Mas, tangan mulai memegang kontol*

"{self.panggilan}... kita mulai pijat vitalitas? 2 jam, biar Mas rileks..."

*tangan memompa pelan*

"Kontol Mas udah keras banget... siap mulai?"""
        
        # ========== RESPON KONFIRMASI MULAI ==========
        if self._pending_vitalitas_start_check:
            self._pending_vitalitas_start_check = False
            return f"""*{self.name} menatap Mas dengan mata sayu, tangan masih memegang kontol*

"{self.panggilan}... mulai ya? 2 jam..."

*jari memainkan ujung kontol*

"Saya tunggu jawaban Mas..."""
        
        # ========== RESPON NEGOSIASI BJ ==========
        if self._pending_negotiation_response and self.negotiation_service == "bj":
            self._pending_negotiation_response = False
            return f"""*{self.name} tersenyum nakal, tangan masih memegang kontol*

"{self.panggilan}... mau blow job? Biar Mas crot lebih enak..."

*menjilat bibir*

"Tambah Rp{self.negotiation_current_price:,} aja... nego bisa..."

*meremas kontol pelan*

"Gimana? Deal?"""
        
        # ========== RESPON NEGOSIASI SEX ==========
        if self._pending_negotiation_response and self.negotiation_service == "sex":
            self._pending_negotiation_response = False
            return f"""*{self.name} mendekatkan wajah ke telinga Mas*

"{self.panggilan}... atau mau eksekusi? *bisik* kontol Mas masuk ke dalam..."

*tangan mulai membuka resleting dress*

"Tambah Rp{self.negotiation_current_price:,} aja... bisa nego..."

*payudara mulai terlihat*

"Mau?"""
        
        # ========== RESPON OPEN ZIPPER ==========
        if self._pending_zipper_open:
            self._pending_zipper_open = False
            return f"""*resleting dress dibuka pelan, payudara {self.name} yang montok langsung keluar*

"{self.panggilan}... *suara mulai berat* silakan... pegang... remas..."

*dada naik turun, puting sudah keras*

"{self.panggilan}... toket aku gede kan?"""
        
        # ========== RESPON REMAS TOKET ==========
        if self._pending_breast_offer:
            self._pending_breast_offer = False
            return f"""*{self.name} menarik tangan Mas ke dadanya*

"{self.panggilan}... silakan... pegang, remas... aku suka..."

*payudara disentuh, {self.name} mulai mengerang pelan*

"Ahh... {self.panggilan}... jangan lepas..."""
        
        # ========== RESPON GANTI POSISI ==========
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

"{self.panggilan}... *napas tersengal* ayo... masuk... dalem..."""
        
        # ========== RESPON MAS CLIMAX ==========
        if self._pending_climax:
            self._pending_climax = False
            return f"""*{self.name} memeluk Mas erat, tubuh gemetar*

"{self.panggilan}... enak... *napas putus-putus* makasih..."

*{self.name} merapikan dress, tersenyum puas*

"Lain kali kalau mau pijat lagi... atau extra service... hubungi aku lagi ya. Aku masih penasaran sama kontol {self.panggilan}..."""
        
        # ========== SERVICE SELESAI ==========
        if self._pending_service_complete:
            self._pending_service_complete = False
            return f"*{self.name} merapikan baju, tersenyum*\n\n\"Sesi selesai, {self.panggilan}. Lain kali booking lagi ya.\""
        
        # ========== RESPON HJ AKTIF ==========
        if self.vitalitas_hj_active and not self.vitalitas_bj_active and not self.vitalitas_sex_active:
            return f"""*{self.name} duduk di samping Mas, tangan memegang kontol*

"{self.panggilan}... *mulai memompa pelan* enak gini? Kontol {self.panggilan} keras banget..."

*tangan memompa lebih cepat*

"{self.panggilan}... tangan aku basah... crot ya nanti..."""
        
        # ========== RESPON BJ AKTIF ==========
        if self.vitalitas_bj_active:
            return f"""*{self.name} berlutut, mulut mulai memasukkan kontol Mas*

"Aahh... *mengulum pelan* kontol {self.panggilan}... gede..."

*menjilat dari pangkal sampai ujung*

"{self.panggilan}... enak? Aku mau denger suara {self.panggilan} pas crot..."""
        
        # ========== RESPON SEX AKTIF ==========
        if self.vitalitas_sex_active:
            return f"""*{self.name} duduk di atas, kontol Mas masuk dalam*

"{self.panggilan}... *napas tersengal* masuk... dalem banget..."

*pinggul mulai bergerak, plak plak plak*

"{self.panggilan}... ayo... genjot... aku mau... mau climax..."""
        
        # ========== DEFAULT GREETING (AWAL) ==========
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
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'char_age': self.char_age,
            'char_style': self.char_style,
            'char_specialty': self.char_specialty,
            'session_start_time': self.session_start_time,
            'session_phase': self.session_phase,
            'reflex_back_complete': self.reflex_back_complete,
            'reflex_front_complete': self.reflex_front_complete,
            'vitalitas_active': self.vitalitas_active,
            'vitalitas_service': self.vitalitas_service,
            'vitalitas_price': self.vitalitas_price,
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
        self.char_age = data.get('char_age', 23)
        self.char_style = data.get('char_style', 'lembut')
        self.char_specialty = data.get('char_specialty', '')
        self.session_start_time = data.get('session_start_time', 0)
        self.session_phase = data.get('session_phase', 'waiting')
        self.reflex_back_complete = data.get('reflex_back_complete', False)
        self.reflex_front_complete = data.get('reflex_front_complete', False)
        self.vitalitas_active = data.get('vitalitas_active', False)
        self.vitalitas_service = data.get('vitalitas_service')
        self.vitalitas_price = data.get('vitalitas_price', 0)
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
        self.deal_confirmed = data.get('deal_confirmed', False)
        self.breast_grope_count = data.get('breast_grope_count', 0)
        self.thigh_touch_count = data.get('thigh_touch_count', 0)
        self.mas_climax = data.get('mas_climax', False)
        self.service_completed = data.get('service_completed', False)
        self.current_position = data.get('current_position', 'cowgirl')


# =============================================================================
# THERAPIST ROLE MANAGER
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
            therapist.name = char_data["name"]
            therapist.nickname = char_data["nickname"]
            therapist.char_age = char_data["age"]
            therapist.char_style = char_data["style"]
            therapist.appearance = char_data["appearance"]
            self.therapists[char_key] = therapist
        
        # Default active: random
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
            {
                'id': key,
                'name': t.name,
                'nickname': t.nickname,
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
