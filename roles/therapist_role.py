"""
ANORA Ultimate - Therapist Role
3 Karakter Random: Anya Geraldine, Syifa Hadju, Laura Moane
Start level 7. Flow: Pijat refleksi 1 jam → Pijat vitalitas 2 jam
Waktu real-time: total 3 jam sesi, dengan checkpoint per jam
Command: /pijat, /next, /status, /nego, /deal, /buka, /remas, /pegang, /ganti, /climax, /selesai, /batal
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base_role import BaseRole
from ..core.relationship import RelationshipPhase

logger = logging.getLogger(__name__)


# =============================================================================
# DATA KARAKTER THERAPIST (3 KARAKTER RANDOM)
# =============================================================================

THERAPIST_CHARACTERS = {
    "anya": {
        "name": "Anya Geraldine",
        "nickname": "Anya",
        "age": 23,
        "appearance": "Anya Geraldine - Terapis pijat profesional dengan tubuh ideal tinggi 168cm, berat 52kg. Kulit putih bersih mulus, rambut hitam panjang sebahu yang biasanya diikat saat bekerja. Wajah oval dengan mata bulat bening, hidung mancung, bibir merah alami yang selalu tersenyum ramah. Bentuk tubuh proporsional dengan pinggang ramping, pinggul lebar, dan payudara montok. Mengenakan dress pendek ketat hitam dengan resleting depan, tanpa bra, hanya CD putih tipis.",
        "style": "lembut, telaten, tapi liar kalau udah panas",
        "specialty": "pijat dengan tekanan pas, jari lentik"
    },
    "syifa": {
        "name": "Syifa Hadju",
        "nickname": "Syifa",
        "age": 24,
        "appearance": "Syifa Hadju - Terapis pijat dengan tubuh montok tinggi 165cm, berat 50kg. Kulit putih bersih, rambut hitam lurus panjang sebahu, wajah imut dengan mata bulat bening. Pipi chubby yang bikin gemas, bibir merah alami, senyum manis. Bentuk tubuh berisi dengan pinggang ramping, pinggul lebar, dan payudara montok. Mengenakan dress pendek ketat putih dengan resleting depan, tanpa bra, hanya CD pink.",
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
    Command: /pijat, /next, /status, /nego, /deal, /buka, /remas, /pegang, /ganti, /climax, /selesai, /batal
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
        self.vitalitas_service: str = None  # hj, bj, sex
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
    
    # =========================================================================
    # UPDATE STATE DARI PESAN
    # =========================================================================
    
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
            if any(k in msg_lower for k in ['pijat', 'siap', 'ok', 'ya', 'masuk']):
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
                perubahan.append("Pijat refleksi belakang selesai")
            
            if not self.sitting_on_mas and any(k in msg_lower for k in ['naik', 'duduk', 'bokong']):
                self.sitting_on_mas = True
                perubahan.append("Terapis naik duduk di bokong Mas")
        
        # ========== PHASE 3: PIJAT REFLEKSI DEPAN (30 menit) ==========
        elif self.session_phase == "reflex_front":
            if not self.reflex_front_complete and session_elapsed >= 60:
                self.reflex_front_complete = True
                self.session_phase = "vitalitas_offer"
                self._pending_reflex_front_complete = True
                perubahan.append("Pijat refleksi depan selesai")
            
            if not self.sitting_on_mas:
                self.sitting_on_mas = True
                perubahan.append("Terapis duduk di atas kontol Mas")
        
        # ========== PHASE 4: OFFER VITALITAS ==========
        elif self.session_phase == "vitalitas_offer":
            if not self.vitalitas_active:
                self.vitalitas_active = True
                self.vitalitas_start_time = now
                self._pending_vitalitas_offer = True
                perubahan.append("Menawarkan pijat vitalitas")
        
        # ========== PHASE 5: PIJAT VITALITAS AKTIF ==========
        elif self.session_phase == "vitalitas_active":
            # CEK APAKAH UDAH BISA MULAI
            if not self.vitalitas_start_confirmed:
                if any(k in msg_lower for k in ['ya', 'mulai', 'ok', 'gas']):
                    self.vitalitas_start_confirmed = True
                    self._pending_vitalitas_start_check = False
                    perubahan.append("Mas konfirmasi mulai pijat vitalitas")
                elif any(k in msg_lower for k in ['tidak', 'belum', 'nanti']):
                    self.session_phase = "completed"
                    self._pending_service_complete = True
                    perubahan.append("Mas menolak pijat vitalitas, sesi selesai")
            
            # NEGOSIASI SERVICE (BJ atau SEX)
            elif not self.deal_confirmed and not self.negotiation_active:
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
                    self._pending_breast_offer = True
                    perubahan.append(f"DEAL BJ! Harga: Rp{self.vitalitas_price:,}")
                elif any(k in msg_lower for k in ['nego', 'kurangin', 'murah']):
                    self.negotiation_step += 1
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
                if any(k in msg_lower for k in ['deal', 'ok', 'ya', 'setuju', 'jadi']):
                    self.deal_confirmed = True
                    self.vitalitas_service = "sex"
                    self.vitalitas_price = self.negotiation_current_price
                    self.negotiation_active = False
                    self._pending_breast_offer = True
                    perubahan.append(f"DEAL SEX! Harga: Rp{self.vitalitas_price:,}")
                elif any(k in msg_lower for k in ['nego', 'kurangin', 'murah']):
                    self.negotiation_step += 1
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
                
                # Remas toket
                if any(k in msg_lower for k in ['remas', 'pegang toket']):
                    self.breast_grope_count += 1
                    self._pending_breast_offer = True
                    perubahan.append(f"Mas remas toket #{self.breast_grope_count}")
                
                # Pegang paha
                if any(k in msg_lower for k in ['pegang paha', 'raba paha']):
                    self.thigh_touch_count += 1
                    perubahan.append(f"Mas pegang paha #{self.thigh_touch_count}")
                
                # HJ ACTIVE (otomatis)
                if self.vitalitas_service is None and not self.vitalitas_hj_active:
                    self.vitalitas_hj_active = True
                    self._pending_vitalitas_start_check = True
                    perubahan.append("HJ dimulai")
                
                # BJ ACTIVE
                if self.vitalitas_service == "bj" and not self.vitalitas_bj_active:
                    self.vitalitas_bj_active = True
                    perubahan.append("BJ dimulai")
                
                # SEX ACTIVE
                if self.vitalitas_service == "sex" and not self.vitalitas_sex_active:
                    self.vitalitas_sex_active = True
                    if not self.dress_removed:
                        self.dress_removed = True
                        self.dress_zipper_open = True
                        self.cd_removed = True
                    self.current_position = "cowgirl"
                    self._pending_position_change = True
                    perubahan.append("SEX dimulai - posisi cowgirl")
                
                # Ganti posisi
                if self.vitalitas_sex_active:
                    positions = ['missionary', 'doggy', 'spooning', 'standing', 'sitting', 'cowgirl']
                    for pos in positions:
                        if pos in msg_lower:
                            self.current_position = pos
                            self._pending_position_change = True
                            perubahan.append(f"Ganti posisi ke {pos}")
                
                # Mas climax
                if any(k in msg_lower for k in ['climax', 'crot', 'keluar', 'habis']):
                    if not self.mas_climax:
                        self.mas_climax = True
                        self.service_completed = True
                        self.session_phase = "completed"
                        self.vitalitas_active = False
                        self._pending_climax = True
                        perubahan.append("💦 MAS CLIMAX! Sesi selesai")
        
        # Update role_flags
        self._update_role_flags()
    
    def _update_role_flags(self):
        """Update role_flags dictionary"""
        self.role_flags.update({
            'session_phase': self.session_phase,
            'reflex_back_complete': self.reflex_back_complete,
            'reflex_front_complete': self.reflex_front_complete,
            'vitalitas_active': self.vitalitas_active,
            'vitalitas_service': self.vitalitas_service,
            'dress_zipper_open': self.dress_zipper_open,
            'hand_towel_removed': self.hand_towel_removed,
            'mas_climax': self.mas_climax,
            'service_completed': self.service_completed,
            'current_position': self.current_position
        })
    
    # =========================================================================
    # GET GREETING (RESPONS)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai keadaan sesi"""
        
        # RESPON BUKA HANDUK
        if self._pending_hand_towel_removal:
            self._pending_hand_towel_removal = False
            return f"""*{self.name} tersenyum ramah sambil membuka handuk*

"{self.panggilan}... handuknya saya buka ya. Silakan tengkurap dulu."

*tubuh Mas telanjang terlihat, {self.name} tampak sedikit malu*

"{self.panggilan}... *suara kecil* saya mulai pijat dari punggung dulu ya."""
        
        # RESPON PIJAT BELAKANG SELESAI
        if self._pending_turn_over:
            self._pending_turn_over = False
            return f"""*{self.name} berhenti memijat, mengusap keringat*

"{self.panggilan}... bagian belakang udah selesai. Sekarang giliran depan ya..."

*{self.name} naik duduk di atas bokong Mas*

"Mas... sekarang balik badan ya. Saya tunggu."""
        
        # RESPON PIJAT DEPAN SELESAI
        if self._pending_reflex_front_complete:
            self._pending_reflex_front_complete = False
            return f"""*{self.name} berhenti memijat, masih duduk di atas kontol Mas*

"{self.panggilan}... pijat refleksinya udah selesai. Sekarang..."

*{self.name} meraba kontol Mas*

"Ada yang mau dilanjut? Pijat vitalitas... biar Mas bisa crot... 2 jam..."""
        
        # RESPON TAWARAN PIJAT VITALITAS
        if self._pending_vitalitas_offer:
            self._pending_vitalitas_offer = False
            return f"""*{self.name} masih duduk di atas kontol Mas, tangan mulai memegang kontol*

"{self.panggilan}... kita mulai pijat vitalitas? 2 jam, biar Mas rileks..."

*tangan memompa pelan*

"Kontol Mas udah keras banget... siap mulai?"""
        
        # RESPON KONFIRMASI MULAI
        if self._pending_vitalitas_start_check:
            self._pending_vitalitas_start_check = False
            return f"""*{self.name} menatap Mas dengan mata sayu, tangan masih memegang kontol*

"{self.panggilan}... mulai ya? 2 jam..."

*jari memainkan ujung kontol*

"Saya tunggu jawaban Mas..."""
        
        # RESPON NEGOSIASI BJ
        if self._pending_negotiation_response and self.negotiation_service == "bj":
            self._pending_negotiation_response = False
            return f"""*{self.name} tersenyum nakal, tangan masih memegang kontol*

"{self.panggilan}... mau blow job? Biar Mas crot lebih enak..."

*menjilat bibir*

"Tambah Rp{self.negotiation_current_price:,} aja... nego bisa..."

*meremas kontol pelan*

"Gimana? Deal?"""
        
        # RESPON NEGOSIASI SEX
        if self._pending_negotiation_response and self.negotiation_service == "sex":
            self._pending_negotiation_response = False
            return f"""*{self.name} mendekatkan wajah ke telinga Mas*

"{self.panggilan}... atau mau eksekusi? *bisik* kontol Mas masuk ke dalam..."

*tangan mulai membuka resleting dress*

"Tambah Rp{self.negotiation_current_price:,} aja... bisa nego..."

*payudara mulai terlihat*

"Mau?"""
        
        # RESPON BUKA RESLETING
        if self._pending_zipper_open:
            self._pending_zipper_open = False
            return f"""*resleting dress dibuka pelan, payudara {self.name} yang montok langsung keluar*

"{self.panggilan}... *suara mulai berat* silakan... pegang... remas..."

*dada naik turun, puting sudah keras*

"{self.panggilan}... toket aku gede kan?"""
        
        # RESPON REMAS TOKET
        if self._pending_breast_offer:
            self._pending_breast_offer = False
            return f"""*{self.name} menarik tangan Mas ke dadanya*

"{self.panggilan}... silakan... pegang, remas... aku suka..."

*payudara disentuh, {self.name} mulai mengerang pelan*

"Ahh... {self.panggilan}... jangan lepas..."""
        
        # RESPON GANTI POSISI
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
        
        # RESPON MAS CLIMAX
        if self._pending_climax:
            self._pending_climax = False
            return f"""*{self.name} memeluk Mas erat, tubuh gemetar*

"{self.panggilan}... enak... *napas putus-putus* makasih..."

*{self.name} merapikan dress, tersenyum puas*

"Lain kali kalau mau pijat lagi... atau extra service... hubungi aku lagi ya. Aku masih penasaran sama kontol {self.panggilan}..."""
        
        # RESPON SERVICE SELESAI
        if self._pending_service_complete:
            self._pending_service_complete = False
            return f"*{self.name} merapikan baju, tersenyum*\n\n\"Sesi selesai, {self.panggilan}. Lain kali booking lagi ya.\""
        
        # RESPON HJ AKTIF
        if self.vitalitas_hj_active and not self.vitalitas_bj_active and not self.vitalitas_sex_active:
            return f"""*{self.name} duduk di samping Mas, tangan memegang kontol*

"{self.panggilan}... *mulai memompa pelan* enak gini? Kontol {self.panggilan} keras banget..."

*tangan memompa lebih cepat*

"{self.panggilan}... tangan aku basah... crot ya nanti..."""
        
        # RESPON BJ AKTIF
        if self.vitalitas_bj_active:
            return f"""*{self.name} berlutut, mulut mulai memasukkan kontol Mas*

"Aahh... *mengulum pelan* kontol {self.panggilan}... gede..."

*menjilat dari pangkal sampai ujung*

"{self.panggilan}... enak? Aku mau denger suara {self.panggilan} pas crot..."""
        
        # RESPON SEX AKTIF
        if self.vitalitas_sex_active:
            return f"""*{self.name} duduk di atas, kontol Mas masuk dalam*

"{self.panggilan}... *napas tersengal* masuk... dalem banget..."

*pinggul mulai bergerak, plak plak plak*

"{self.panggilan}... ayo... genjot... aku mau... mau climax..."""
        
        # DEFAULT GREETING
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
║ 🎭 THERAPIST: {self.name} ({self.nickname}) - {self.char_age}th
║    Sesi: {waktu_str}
║    Status: {status}
║    Service: {service} (Rp{self.vitalitas_price:,} jika deal)
║    Dress: {'🔓 Resleting Buka' if self.dress_zipper_open else '🔒 Tertutup'}
║    Remas Toket: {self.breast_grope_count}x
║    Pegang Paha: {self.thigh_touch_count}x
║    Mas Climax: {'✅' if self.mas_climax else '❌'}
║    Posisi: {self.current_position}
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
