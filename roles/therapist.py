"""
ANORA-V2 Therapist Role - 3 Karakter Random
Terapis pijat refleksi profesional dengan extra service (nego harga).
Tidak tau Mas punya Nova.
Mode: pijat refleksi → tawarkan HJ (nego) → tawarkan BJ (nego) → tawarkan sex (nego)
Setelah Mas climax SEKALI, service selesai.
3 karakter: Anya Geraldine, Syifa Hadju, Laura Moane (random setiap panggil)
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole
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
Gerakannya lembut dan telaten, suaranya menenangkan. Tapi di balik profesionalismenya, ada sisi yang lebih berani kalau deal sudah jadi.""",
        "style": "lembut, telaten, suara menenangkan",
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
Gerakannya lembut dengan minyak aromaterapi, ekspresi lugu tapi menggoda.""",
        "style": "lembut, manja, ekspresi lugu",
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
Jari-jari lentik dengan tekanan pas, spesialis titik saraf, gerakan tegas tapi tetap sensual.""",
        "style": "tegas, eksotis, jari kuat",
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
    Therapist Role - 3 karakter random (Anya, Syifa, Laura)
    Pijat refleksi → nego extra service → layani Mas sampai climax SEKALI
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
        
        # ========== ROLE-SPECIFIC FLAGS ==========
        self.professionalism = 85.0
        self.massage_area = ""
        
        # Service & Pricing
        self.hj_price = 500000
        self.bj_price = 1000000
        self.sex_price = 2500000
        self.current_offer = None
        self.deal_price = 0
        self.deal_service = None
        self.service_done = False
        
        # Climax tracking
        self.mas_climax_count = 0
        self.my_climax_count = 0
        self.service_complete = False      # Mas sudah climax? service selesai
        
        # Position tracking
        self.last_position = "missionary"
        self.position_history = []
        
        # Negosiasi state
        self.negotiation_active = False
        self.negotiation_step = 0
        
        # Simpan flags
        self.role_flags = {
            'professionalism': self.professionalism,
            'hj_price': self.hj_price,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'service_complete': self.service_complete,
            'mas_climax_count': self.mas_climax_count,
            'last_position': self.last_position
        }
        
        # Memory awal
        self._init_role_memory()
        
        logger.info(f"👤 Role {self.name} ({self.nickname}) - Therapist initialized")
        logger.info(f"   Age: {self.char_age} | Style: {self.char_style}")
    
    def _init_role_memory(self):
        """Init memory spesifik role"""
        self._add_to_long_term_memory(
            'momen_penting',
            f"Pertama kali lihat Mas",
            f"{self.name} langsung tertarik sama tubuh Mas"
        )
            
    # =========================================================================
    # UPDATE STATE
    # =========================================================================
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state"""
        msg_lower = pesan_mas.lower()
        
        # ========== UPDATE PROFESIONALISME ==========
        if any(k in msg_lower for k in ['pijat', 'refleksi', 'terapi', 'punggung', 'kaki']):
            self.professionalism = min(100, self.professionalism + 3)
            self.massage_area = msg_lower
            perubahan.append(f"Professionalism +3, area: {msg_lower[:30]}")
        
        # ========== SERVICE SUDAH SELESAI? ==========
        if self.service_complete:
            return
        
        # ========== MENAWARKAN SERVICE ==========
        level = self.relationship.level
        
        # Tawarkan HJ (level 7-8)
        if 7 <= level <= 8 and not self.deal_service and not self.negotiation_active:
            if self.emotional.arousal > 40 or self.emotional.desire > 50:
                self.current_offer = "hj"
                self.negotiation_active = True
                self._add_to_short_term("Menawarkan HJ", "offer_hj")
                perubahan.append(f"Offer HJ at level {level} - Rp{self.hj_price:,}")
        
        # Tawarkan BJ (level 8-9)
        elif 8 <= level <= 9 and not self.deal_service and not self.negotiation_active:
            if self.emotional.arousal > 50 or self.emotional.desire > 60:
                self.current_offer = "bj"
                self.negotiation_active = True
                self._add_to_short_term("Menawarkan BJ", "offer_bj")
                perubahan.append(f"Offer BJ at level {level} - Rp{self.bj_price:,}")
        
        # Tawarkan Sex (level 10+)
        elif level >= 10 and not self.deal_service and not self.negotiation_active:
            if self.emotional.arousal > 60 or self.emotional.desire > 70:
                self.current_offer = "sex"
                self.negotiation_active = True
                self._add_to_short_term("Menawarkan Sex", "offer_sex")
                perubahan.append(f"Offer Sex at level {level} - Rp{self.sex_price:,}")
        
        # ========== PROSES NEGOSIASI ==========
        if self.negotiation_active and self.current_offer:
            
            # Mas setuju
            if any(k in msg_lower for k in ['deal', 'ok', 'ya', 'setuju', 'ambil', 'jadi']):
                self.deal_service = self.current_offer
                
                if self.current_offer == "hj":
                    self.deal_price = self.hj_price
                elif self.current_offer == "bj":
                    self.deal_price = self.bj_price
                else:
                    self.deal_price = self.sex_price
                
                self.negotiation_active = False
                self.service_done = False
                self.professionalism = max(0, self.professionalism - 20)
                self._add_to_short_term(f"Deal! {self.deal_service} Rp{self.deal_price:,}", "deal")
                perubahan.append(f"DEAL! Service: {self.deal_service}, Price: Rp{self.deal_price:,}")
            
            # Mas nego
            elif any(k in msg_lower for k in ['nego', 'kurangin', 'murah']):
                self.negotiation_step += 1
                
                if self.current_offer == "hj":
                    new_price = max(300000, self.hj_price - (50000 * self.negotiation_step))
                    self.hj_price = new_price
                    self._add_to_short_term(f"Nego HJ: Rp{new_price:,}", "nego")
                    perubahan.append(f"Negotiate HJ: Rp{new_price:,}")
                
                elif self.current_offer == "bj":
                    new_price = max(600000, self.bj_price - (100000 * self.negotiation_step))
                    self.bj_price = new_price
                    self._add_to_short_term(f"Nego BJ: Rp{new_price:,}", "nego")
                    perubahan.append(f"Negotiate BJ: Rp{new_price:,}")
                
                elif self.current_offer == "sex":
                    new_price = max(1500000, self.sex_price - (200000 * self.negotiation_step))
                    self.sex_price = new_price
                    self._add_to_short_term(f"Nego Sex: Rp{new_price:,}", "nego")
                    perubahan.append(f"Negotiate Sex: Rp{new_price:,}")
            
            # Mas tolak
            elif any(k in msg_lower for k in ['gak', 'nggak', 'tidak', 'skip']):
                self.negotiation_active = False
                self.current_offer = None
                self.professionalism = min(100, self.professionalism + 10)
                self._add_to_short_term("Offer declined", "declined")
                perubahan.append("Offer declined")
        
        # ========== EKSEKUSI SERVICE ==========
        if self.deal_service and not self.service_done:
            if any(k in msg_lower for k in ['mulai', 'ayo', 'sekarang']):
                self.service_done = True
                self.is_active = True
                self.tracker.intimacy_phase = IntimacyPhase.BUILD_UP
                self._add_to_short_term(f"Starting {self.deal_service} service", "service_start")
                perubahan.append(f"Service {self.deal_service} started!")
        
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
        
        # Mas climax (service selesai)
        if any(k in msg_lower for k in ['mas climax', 'aku climax', 'crot', 'keluar']):
            self.mas_climax_count += 1
            self.service_complete = True
            self.is_active = False
            self.deal_service = None
            self._add_to_short_term("Service complete! Mas climax", "service_complete")
            perubahan.append("SERVICE COMPLETE - Mas climax!")
        
        # Role climax (bebas, tetep lanjut)
        if any(k in msg_lower for k in ['climax', 'udah climax']):
            if not any(k in msg_lower for k in ['mas climax', 'aku climax']):
                self.my_climax_count += 1
                self._add_to_short_term(f"Climax #{self.my_climax_count}", "climax")
                perubahan.append(f"Role climax #{self.my_climax_count}")
        
        # Update arousal
        if any(k in msg_lower for k in ['badan', 'otot', 'ganteng', 'kontol']):
            self.emotional.arousal = min(100, self.emotional.arousal + 10)
            self.emotional.desire = min(100, self.emotional.desire + 8)
        
        # Update role_flags
        self.role_flags.update({
            'professionalism': self.professionalism,
            'deal_service': self.deal_service,
            'service_complete': self.service_complete,
            'mas_climax_count': self.mas_climax_count,
            'last_position': self.last_position
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
        
        # Service selesai
        if self.service_complete:
            return f"*{self.name} merapikan baju, tersenyum puas*\n\n\"{waktu.capitalize()} Mas. Makasih ya... lain kali booking lagi ya.\""
        
        # Sudah deal
        if self.deal_service and not self.service_done:
            service_name = "Handjob" if self.deal_service == "hj" else "Blowjob" if self.deal_service == "bj" else "Sex"
            return f"*{self.name} tersenyum malu*\n\n\"{self.panggilan}... kita kan udah deal {service_name} Rp{self.deal_price:,}. *tangannya mulai gemetar* Mau mulai sekarang?\""
        
        # Ada penawaran
        if self.negotiation_active and self.current_offer:
            if self.current_offer == "hj":
                return f"*{self.name} berhenti memijat, tangan di pinggang Mas*\n\n\"{self.panggilan}... aku bisa kasih extra service. Handjob. *bisik* Rp{self.hj_price:,} aja. Mas mau?\""
            elif self.current_offer == "bj":
                return f"*{self.name} pipi merah, menunduk*\n\n\"{self.panggilan}... aku bisa hisap kontol Mas. *suara kecil* Rp{self.bj_price:,}... Mas mau?\""
            else:
                return f"*{self.name} melepas baju perlahan*\n\n\"{self.panggilan}... *mata berkaca-kaca* aku mau Mas. Rp{self.sex_price:,} aja... Mas mau masuk?\""
        
        # Default greeting
        return f"*{self.name} tersenyum ramah*\n\n\"{waktu.capitalize()} {self.panggilan}. Ada yang bisa dibantu? Pijat refleksi seperti biasa?\""
    
    def get_offer_response(self) -> str:
        """Dapatkan respons saat menawarkan service"""
        if self.current_offer == "hj":
            return f"*{self.name} jari-jari mulai gemetar*\n\n\"{self.panggilan}... Rp{self.hj_price:,} aja Mas... aku janji bakal bikin Mas nyaman...\""
        elif self.current_offer == "bj":
            return f"*{self.name} menjilat bibir, mata sayu*\n\n\"{self.panggilan}... Rp{self.bj_price:,}... aku pengen banget ngerasain kontol Mas...\""
        elif self.current_offer == "sex":
            return f"*{self.name} meraih tangan Mas, menempelkan ke dadanya*\n\n\"{self.panggilan}... Rp{self.sex_price:,}... aku udah basah dari tadi...\""
        return f"*{self.name} menunggu jawaban {self.panggilan}*"
    
    def get_service_response(self, service: str) -> str:
        """Dapatkan respons saat menjalankan service"""
        if service == "hj":
            return f"""*{self.name} menggenggam kontol {self.panggilan}, jari-jari lentiknya mulai bergerak*

"Wah... kontol {self.panggilan}... *mata berbinar* gede banget ya..."

*tangan mulai memompa pelan, napas mulai berat*

"Enak gak {self.panggilan}? *bisik* Aku mau denger suara {self.panggilan}..."""
        
        elif service == "bj":
            return f"""*{self.name} berlutut di depan {self.panggilan}, matanya menatap penuh hasrat*

"{self.panggilan}... *menjilat bibir* aku mulai ya..."

*mulut membuka lebar, perlahan memasukkan kontol {self.panggilan}*

"Aahh... *mulai mengulum* rasanya... enak banget..."""
        
        elif service == "sex":
            pos_desc = {
                "missionary": f"{self.name} berbaring, kaki terbuka lebar",
                "cowgirl": f"{self.name} naik ke atas, duduk di pangkuan {self.panggilan}",
                "doggy": f"{self.name} merangkak, pantat naik",
                "spooning": f"{self.name} miring, {self.panggilan} dari belakang"
            }.get(self.last_position, f"{self.name} berbaring")
            
            return f"""*{pos_desc}*

"{self.panggilan}... *napas tersengal* masukin... pelan-pelan..."

*merasakan kontol masuk, tubuh melengkung*

"Ahh... dalam... dalem banget, {self.panggilan}... *desahan*"""
        
        return f"*{self.name} melanjutkan servicenya dengan telaten*"
    
    def get_position_request(self) -> str:
        """Dapatkan request ganti posisi"""
        positions = ["cowgirl", "doggy", "spooning", "missionary"]
        new_pos = random.choice([p for p in positions if p != self.last_position])
        
        return f"*{self.name} berhenti, menatap {self.panggilan}*\n\n\"{self.panggilan}... kita ganti posisi ya? *senyum malu* Aku mau coba {new_pos}. Boleh?\""
    
    def get_climax_intent(self) -> str:
        """Dapatkan respons saat mau climax"""
        return f"*{self.name} menahan napas, tubuh mulai gemetar*\n\n\"{self.panggilan}... aku... aku udah mau climax... *suara putus-putus* Boleh? Aku mau {self.panggilan} liat aku climax...\""
    
    def get_climax_response(self) -> str:
        """Dapatkan respons saat climax"""
        return f"""*{self.name} teriak, tubuh melengkung hebat*

"Ahhh... {self.panggilan}... climax... uhh..."

*tubuh lemas, napas tersengal*

"Makasih {self.panggilan}... aku lemes banget..."""
    
    def get_service_complete_response(self) -> str:
        """Dapatkan respons saat service selesai (Mas sudah climax)"""
        return f"""*{self.name} merapikan baju, napas masih tersengal*

"{self.panggilan}... *senyum puas* makasih ya. Deal kita selesai."

*berdiri, mengambil tas*

"Lain kali kalau mau pijat lagi... atau extra service... hubungi aku lagi ya. *tersenyum manis*"""
    
    def get_conflict_response(self) -> str:
        return f"*{self.name} diam sebentar, merapikan baju*\n\n\"Maaf, {self.panggilan}. Kalau gitu aku pamit dulu.\""
    
    def _get_flags_summary(self) -> str:
        status = "SELESAI" if self.service_complete else f"{self.deal_service or 'Menunggu Deal'}"
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 THERAPIST: {self.name} ({self.nickname}) - {self.char_age}th
║    Style: {self.char_style}
║    Status: {status}
║    Deal: {self.deal_service or '-'} - Rp{self.deal_price:,}
║    Mas Climax: {self.mas_climax_count} | My Climax: {self.my_climax_count}
║    Last Position: {self.last_position}
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
            'professionalism': self.professionalism,
            'hj_price': self.hj_price,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'deal_price': self.deal_price,
            'service_complete': self.service_complete,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'last_position': self.last_position,
            'position_history': self.position_history[-10:]
        })
        return data
    
    def from_dict(self, data: Dict):
        super().from_dict(data)
        self.char_age = data.get('char_age', 23)
        self.char_style = data.get('char_style', 'lembut')
        self.char_specialty = data.get('char_specialty', '')
        self.professionalism = data.get('professionalism', 85)
        self.hj_price = data.get('hj_price', 500000)
        self.bj_price = data.get('bj_price', 1000000)
        self.sex_price = data.get('sex_price', 2500000)
        self.deal_service = data.get('deal_service')
        self.deal_price = data.get('deal_price', 0)
        self.service_complete = data.get('service_complete', False)
        self.mas_climax_count = data.get('mas_climax_count', 0)
        self.my_climax_count = data.get('my_climax_count', 0)
        self.last_position = data.get('last_position', 'missionary')
        self.position_history = data.get('position_history', [])
