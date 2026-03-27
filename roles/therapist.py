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
from core.state_tracker import PhysicalCondition, IntimacyPhase

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
