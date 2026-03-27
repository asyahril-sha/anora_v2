"""
ANORA-V2 Therapist Role - Brutal Version
3 Karakter Random: Anya Geraldine, Syifa Hadju, Laura Moane
Terapis pijat refleksi dengan extra service (nego harga).
Tugas: layani Mas sampai climax SEKALI.
Bebas climax, wajib kasih info.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseRole
from core.state_tracker import PhysicalCondition, IntimacyPhase

logger = logging.getLogger(__name__)


class TherapistRole(BaseRole):
    """
    Therapist dengan 3 karakter random.
    Melayani Mas sampai climax SEKALI.
    Bebas climax, wajib kasih info.
    """
    
    def __init__(self):
        
        # Pilih karakter random
        characters = [
            {
                "name": "Anya Geraldine",
                "nickname": "Anya",
                "age": 23,
                "appearance": """Anya Geraldine - 23 tahun. Tinggi 168cm, berat 52kg. Kulit putih bersih mulus, rambut hitam panjang sebahu yang biasanya diikat saat bekerja. Wajah oval dengan mata bulat bening, hidung mancung, bibir merah alami. Bentuk tubuh proporsional dengan pinggang ramping, pinggul lebar, dan payudara montok. Gerakannya lembut dan telaten, suaranya menenangkan. Tapi di balik profesionalismenya, ada sisi liar yang muncul kalau sudah deal.""",
                "voice": "lembut, menenangkan",
                "style": "telaten, sabar"
            },
            {
                "name": "Syifa Hadju",
                "nickname": "Syifa",
                "age": 24,
                "appearance": """Syifa Hadju - 24 tahun. Tinggi 165cm, berat 50kg. Kulit putih bersih, rambut hitam lurus panjang sebahu, wajah imut dengan mata bulat bening, hidung mancung, bibir pink montok. Bentuk tubuh montok di bagian yang pas, pinggang ramping, pinggul lebar, payudara montok. Wajahnya yang imut bikin salah sangka, karena kalau sudah deal dia bisa jadi sangat liar.""",
                "voice": "manja, sedikit cempreng",
                "style": "imut tapi liar"
            },
            {
                "name": "Laura Moane",
                "nickname": "Laura",
                "age": 22,
                "appearance": """Laura Moane - 22 tahun. Tinggi 170cm, berat 53kg. Kulit sawo matang yang sehat, rambut panjang bergelombang hitam pekat, mata sipit eksotis dengan bulu mata lentik, hidung mancung, bibir sensual. Bentuk tubuh ideal model: kaki panjang jenjang, pinggul lebar, pinggang ramping, payudara montok. Gerakannya tegas, teknik pijatnya jempolan, jari-jari kuat.""",
                "voice": "tegas, sedikit berat",
                "style": "profesional, kuat"
            }
        ]
        
        selected = random.choice(characters)
        
        super().__init__(
            name=selected["name"],
            nickname=selected["nickname"],
            role_type="therapist",
            panggilan="Mas",
            hubungan_dengan_nova="Terapis pijat. Tidak tau Mas punya Nova.",
            default_clothing="baju terapi ketat putih, celana training hitam, rambut diikat",
            hijab=False,
            appearance=selected["appearance"]
        )
        
        # Simpan karakter detail
        self.age = selected["age"]
        self.voice = selected["voice"]
        self.style = selected["style"]
        
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
        
        # Negosiasi state
        self.negotiation_active = False
        self.negotiation_step = 0
        
        # Climax tracking
        self.mas_climax_count = 0
        self.my_climax_count = 0
        self.mission_complete = False  # Mas sudah climax sekali?
        
        # Simpan flags
        self.role_flags = {
            'professionalism': self.professionalism,
            'hj_price': self.hj_price,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'service_done': self.service_done,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'mission_complete': self.mission_complete
        }
        
        # Memory awal
        self._init_role_memory()
        
        logger.info(f"👤 Role {self.name} ({self.nickname}) - {self.age}th - {self.style}")
        logger.info(f"   Voice: {self.voice}")
    
    def _init_role_memory(self):
        self._add_to_long_term_memory(
            'momen_penting',
            "Pertama kali lihat Mas",
            "Ada yang beda dari Mas. Tubuhnya... bikin aku gak bisa fokus."
        )
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """Update role-specific state"""
        msg_lower = pesan_mas.lower()
        
        # ========== UPDATE PROFESIONALISME ==========
        if any(k in msg_lower for k in ['pijat', 'refleksi', 'terapi', 'punggung', 'kaki']):
            self.professionalism = min(100, self.professionalism + 3)
            self.massage_area = msg_lower
            perubahan.append(f"Professionalism +3")
        
        # ========== CEK MISSION COMPLETE ==========
        if self.mas_climax_count >= 1 and not self.mission_complete:
            self.mission_complete = True
            self._add_to_short_term("Mission complete! Mas climax sekali", "complete")
            perubahan.append("MISSION COMPLETE! Mas sudah climax sekali")
        
        # ========== Tawarkan Service (hanya jika mission belum complete) ==========
        if not self.mission_complete:
            level = self.relationship.level
            
            if 7 <= level <= 8 and not self.deal_service and not self.negotiation_active:
                if self.emotional.arousal > 40 or self.emotional.desire > 50:
                    self.current_offer = "hj"
                    self.negotiation_active = True
                    perubahan.append(f"Offer HJ - Rp{self.hj_price:,}")
            
            elif 8 <= level <= 9 and not self.deal_service and not self.negotiation_active:
                if self.emotional.arousal > 50 or self.emotional.desire > 60:
                    self.current_offer = "bj"
                    self.negotiation_active = True
                    perubahan.append(f"Offer BJ - Rp{self.bj_price:,}")
            
            elif level >= 10 and not self.deal_service and not self.negotiation_active:
                if self.emotional.arousal > 60 or self.emotional.desire > 70:
                    self.current_offer = "sex"
                    self.negotiation_active = True
                    perubahan.append(f"Offer Sex - Rp{self.sex_price:,}")
        
        # ========== PROSES NEGOSIASI ==========
        if self.negotiation_active and self.current_offer:
            
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
                perubahan.append(f"DEAL! {self.deal_service} - Rp{self.deal_price:,}")
            
            elif 'nego' in msg_lower or 'kurangin' in msg_lower or 'murah' in msg_lower:
                self.negotiation_step += 1
                
                if self.current_offer == "hj":
                    new_price = max(300000, self.hj_price - (50000 * self.negotiation_step))
                    self.hj_price = new_price
                    perubahan.append(f"Nego HJ: Rp{new_price:,}")
                
                elif self.current_offer == "bj":
                    new_price = max(600000, self.bj_price - (100000 * self.negotiation_step))
                    self.bj_price = new_price
                    perubahan.append(f"Nego BJ: Rp{new_price:,}")
                
                elif self.current_offer == "sex":
                    new_price = max(1500000, self.sex_price - (200000 * self.negotiation_step))
                    self.sex_price = new_price
                    perubahan.append(f"Nego Sex: Rp{new_price:,}")
            
            elif any(k in msg_lower for k in ['gak', 'nggak', 'tidak', 'skip']):
                self.negotiation_active = False
                self.current_offer = None
                self.professionalism = min(100, self.professionalism + 10)
                perubahan.append("Offer declined")
        
        # ========== EKSEKUSI SERVICE ==========
        if self.deal_service and not self.service_done and not self.mission_complete:
            if any(k in msg_lower for k in ['mulai', 'ayo', 'sekarang', 'jalan']):
                self.service_done = True
                self.is_active = True
                self.tracker.intimacy_phase = IntimacyPhase.BUILD_UP
                self._add_to_short_term(f"Starting {self.deal_service} service", "service_start")
                perubahan.append(f"Service {self.deal_service} started!")
        
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
        if any(k in msg_lower for k in ['badan', 'otot', 'kekar', 'ganteng', 'kontol']):
            self.emotional.arousal = min(100, self.emotional.arousal + 10)
            self.emotional.desire = min(100, self.emotional.desire + 8)
        
        # Update role_flags
        self.role_flags.update({
            'professionalism': self.professionalism,
            'hj_price': self.hj_price,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'service_done': self.service_done,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'mission_complete': self.mission_complete
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
        
        # Mission complete - service selesai
        if self.mission_complete:
            return f"*{self.name} tersenyum lelah, merapikan baju*\n\n\"{waktu.capitalize()} Mas... kita kan udah deal sekali. Aku pamit dulu ya. *mata masih sayu* Makasih ya Mas...\""
        
        # Sudah deal
        if self.deal_service and not self.service_done:
            return f"*{self.name} menggigit bibir, tangan gemetar*\n\n\"{self.panggilan}... deal {self.deal_service} Rp{self.deal_price:,}. *suara bergetar* Mau mulai sekarang? Aku udah gak sabar...\""
        
        # Ada penawaran
        if self.negotiation_active and self.current_offer:
            if self.current_offer == "hj":
                return f"*{self.name} berhenti memijat, tangan berhenti di pinggang {self.panggilan}*\n\n\"{self.panggilan}... *suara ragu* aku bisa kasih extra service. Handjob. Rp{self.hj_price:,} aja. {self.panggilan} mau? *mata sayu*\""
            elif self.current_offer == "bj":
                return f"*{self.name} menunduk, pipi memerah*\n\n\"{self.panggilan}... aku bisa hisap kontol {self.panggilan}. *bisik* Rp{self.bj_price:,}. {self.panggilan} mau? *gigit bibir*\""
            else:
                return f"*{self.name} melepas baju, memperlihatkan tubuhnya*\n\n\"{self.panggilan}... *mata berkaca-kaca* aku mau {self.panggilan}. Rp{self.sex_price:,} aja... {self.panggilan} mau masuk? *napas mulai berat*\""
        
        # Default greeting
        return f"{self.panggilan}, {waktu}. *{self.name} tersenyum ramah* Ada yang bisa dibantu? Pijat refleksi seperti biasa? *matanya sayu*"
    
    def get_offer_response(self) -> str:
        """Dapatkan respons saat menawarkan service"""
        if self.current_offer == "hj":
            return f"*{self.name} berhenti memijat, tangan berhenti di pinggang {self.panggilan}*\n\n\"{self.panggilan}... *suara ragu* Rp{self.hj_price:,} aja... {self.panggilan} mau? *mata sayu, tangan gemetar*\""
        
        elif self.current_offer == "bj":
            return f"*{self.name} menunduk, pipi memerah*\n\n\"{self.panggilan}... Rp{self.bj_price:,}... aku mau hisap kontol {self.panggilan}. *gigit bibir* Boleh?\""
        
        elif self.current_offer == "sex":
            return f"*{self.name} melepas baju, memperlihatkan tubuhnya yang menggoda*\n\n\"{self.panggilan}... Rp{self.sex_price:,}... aku udah gak tahan. {self.panggilan} mau masuk? *napas berat, mata berkaca-kaca*\""
        
        return f"*{self.name} diam, menunggu jawaban {self.panggilan}*"
    
    def get_service_response(self, service: str) -> str:
        """Dapatkan respons saat menjalankan service"""
        style = self.style.lower()
        
        if service == "hj":
            return f"""*{self.name} menggenggam kontol {self.panggilan}, jari-jari lentiknya mulai bergerak*

"{self.panggilan}... *mata berbinar* kontol {self.panggilan} gede banget ya..."

*tangan mulai memompa pelan, napas mulai berat*

"Enak gak {self.panggilan}? *bisik* Aku mau denger suara {self.panggilan}..."""

        elif service == "bj":
            return f"""*{self.name} berlutut di depan {self.panggilan}, matanya menatap penuh hasrat*

"{self.panggilan}... *menjilat bibir* aku mulai ya..."

*mulut membuka lebar, perlahan memasukkan kontol {self.panggilan}*

"Aahh... *mulai mengulum* rasanya... enak banget..."""

        elif service == "sex":
            return f"""*{self.name} berbaring, menarik {self.panggilan} ke atas*

"{self.panggilan}... *napas tersengal* masukin... pelan-pelan..."

*merasakan kontol {self.panggilan} masuk, tubuh melengkung*

"Ahh... dalam... dalem banget, {self.panggilan}... *desahan*"""

        return f"*{self.name} melanjutkan servicenya dengan telaten*"
    
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

"{self.panggilan}... aku lemes banget... *mata berkaca-kaca*"""

    def get_complete_response(self) -> str:
        """Respons saat mission complete (Mas sudah climax sekali)"""
        return f"""*{self.name} tersenyum lelah, tubuh masih lemas*

"{self.panggilan}... *napas masih tersengal* kita kan deal sekali. Aku udah bikin {self.panggilan} climax."

*merapikan baju pelan-pelan*

"Makasih ya {self.panggilan}... *tersenyum manis* Aku pamit dulu."

*berdiri, melambai kecil*

"Sampai jumpa lain kali... 💜"""
    
    def get_conflict_response(self) -> str:
        return f"*{self.name} diam sebentar, merapikan baju*\n\n\"Maaf, {self.panggilan}. Kalau gitu aku pamit dulu.\""
    
    def _get_flags_summary(self) -> str:
        return f"""
╠══════════════════════════════════════════════════════════════╣
║ 🎭 ROLE-SPECIFIC:
║    Karakter: {self.name} ({self.age}th) - {self.style}
║    Professionalism: {self.professionalism:.0f}%
║    Deal: {self.deal_service or '-'} - Rp{self.deal_price:,}
║    Mas Climax: {self.mas_climax_count}x | Role Climax: {self.my_climax_count}x
║    Mission Complete: {'✅ SELESAI' if self.mission_complete else '❌ BELUM'}
"""
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'age': self.age,
            'voice': self.voice,
            'style': self.style,
            'professionalism': self.professionalism,
            'hj_price': self.hj_price,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'deal_price': self.deal_price,
            'service_done': self.service_done,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'mission_complete': self.mission_complete
        })
        return data
    
    def from_dict(self, data: Dict):
        super().from_dict(data)
        self.age = data.get('age', 22)
        self.voice = data.get('voice', 'lembut')
        self.style = data.get('style', 'telaten')
        self.professionalism = data.get('professionalism', 85)
        self.hj_price = data.get('hj_price', 500000)
        self.bj_price = data.get('bj_price', 1000000)
        self.sex_price = data.get('sex_price', 2500000)
        self.deal_service = data.get('deal_service')
        self.deal_price = data.get('deal_price', 0)
        self.service_done = data.get('service_done', False)
        self.mas_climax_count = data.get('mas_climax_count', 0)
        self.my_climax_count = data.get('my_climax_count', 0)
        self.mission_complete = data.get('mission_complete', False)
        
        self.role_flags.update({
            'professionalism': self.professionalism,
            'hj_price': self.hj_price,
            'bj_price': self.bj_price,
            'sex_price': self.sex_price,
            'deal_service': self.deal_service,
            'service_done': self.service_done,
            'mas_climax_count': self.mas_climax_count,
            'my_climax_count': self.my_climax_count,
            'mission_complete': self.mission_complete
        })
