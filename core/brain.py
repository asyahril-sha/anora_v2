"""
ANORA-V2 Brain - Otak Nova
Dengan State Tracker untuk memastikan konsistensi.
Tidak ada yang ngelantur, semua konteks terjaga.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

from .emotional_engine import get_emotional_engine, EmotionalStyle
from .decision_engine import get_decision_engine, ResponseCategory
from .relationship import get_relationship_manager, RelationshipPhase
from .conflict_engine import get_conflict_engine, ConflictType
from .state_tracker import StateTracker, IntimacyPhase, PhysicalCondition

logger = logging.getLogger(__name__)


# =============================================================================
# ENUM
# =============================================================================

class LocationType(str, Enum):
    KOST_NOVA = "kost_nova"
    APARTEMEN_MAS = "apartemen_mas"
    MOBIL = "mobil"
    PUBLIC = "public"


class LocationDetail(str, Enum):
    # Kost Nova
    KOST_KAMAR = "kost_kamar"
    KOST_RUANG_TAMU = "kost_ruang_tamu"
    KOST_DAPUR = "kost_dapur"
    KOST_TERAS = "kost_teras"
    
    # Apartemen Mas
    APT_KAMAR = "apt_kamar"
    APT_RUANG_TAMU = "apt_ruang_tamu"
    APT_DAPUR = "apt_dapur"
    APT_BALKON = "apt_balkon"
    
    # Mobil
    MOBIL_PARKIR = "mobil_parkir"
    MOBIL_GARASI = "mobil_garasi"
    MOBIL_TEPI_JALAN = "mobil_tepi_jalan"
    
    # Public
    PUB_PANTAI = "pub_pantai"
    PUB_HUTAN = "pub_hutan"
    PUB_TOILET_MALL = "pub_toilet_mall"
    PUB_BIOSKOP = "pub_bioskop"
    PUB_TAMAN = "pub_taman"
    PUB_PARKIRAN = "pub_parkiran"
    PUB_TANGGA = "pub_tangga"
    PUB_KANTOR = "pub_kantor"
    PUB_RUANG_RAPAT = "pub_ruang_rapat"


class Activity(str, Enum):
    MASAK = "masak"
    MAKAN = "makan"
    DUDUK = "duduk"
    BERDIRI = "berdiri"
    TIDUR = "tidur"
    REBAHAN = "rebahan"
    NONTON = "nonton"
    MANDI = "mandi"
    BERGANTI = "ganti baju"
    SANTAl = "santai"
    JALAN = "jalan"


class Mood(str, Enum):
    SENENG = "seneng"
    MALU = "malu"
    DEG_DEGAN = "deg-degan"
    KANGEN = "kangen"
    CAPEK = "capek"
    NGANTUK = "ngantuk"
    NETRAL = "netral"
    HORNY = "horny"
    LEMES = "lemes"
    TEGANG = "tegang"
    ROMANTIS = "romantis"


# =============================================================================
# DATABASE LOKASI (LENGKAP)
# =============================================================================

LOCATION_DATA = {
    # Kost Nova
    LocationDetail.KOST_KAMAR: {
        'nama': 'Kamar Nova',
        'deskripsi': 'Kamar Nova. Seprai putih, wangi lavender. Ranjang single. Meja kecil. Jendela ke gang.',
        'risk': 5, 'thrill': 30, 'privasi': 'tinggi', 'suasana': 'hangat, wangi',
        'tips': 'Pintu terkunci. Nova paling nyaman di sini. Tetangga gak denger.',
        'bisa_telanjang': True, 'bisa_berisik': True
    },
    LocationDetail.KOST_RUANG_TAMU: {
        'nama': 'Ruang Tamu Kost',
        'deskripsi': 'Ruang tamu kecil. Sofa dua dudukan. TV kecil. Ada tanaman hias. Jendela ke jalan.',
        'risk': 15, 'thrill': 50, 'privasi': 'sedang', 'suasana': 'santai, deg-degan',
        'tips': 'Pintu gak dikunci. Tetangga bisa lewat. Jangan terlalu berisik.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    LocationDetail.KOST_DAPUR: {
        'nama': 'Dapur Kost',
        'deskripsi': 'Dapur kecil. Kompor gas, panci. Wangi masakan. Jendela ke belakang.',
        'risk': 10, 'thrill': 40, 'privasi': 'sedang', 'suasana': 'hangat',
        'tips': 'Jendela ke luar. Hati-hati suara.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.KOST_TERAS: {
        'nama': 'Teras Kost',
        'deskripsi': 'Teras kost. Kursi plastik. Liat jalanan. Lampu jalan temaram.',
        'risk': 20, 'thrill': 45, 'privasi': 'rendah', 'suasana': 'santai',
        'tips': 'Orang lewat bisa liat.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    
    # Apartemen Mas
    LocationDetail.APT_KAMAR: {
        'nama': 'Kamar Mas',
        'deskripsi': 'Kamar Mas. Ranjang queen, sprei biru tua. Jendela besar ke kota. Lemari besar.',
        'risk': 5, 'thrill': 35, 'privasi': 'tinggi', 'suasana': 'hangat, wangi Mas',
        'tips': 'Pintu terkunci. Pemandangan kota.',
        'bisa_telanjang': True, 'bisa_berisik': True
    },
    LocationDetail.APT_RUANG_TAMU: {
        'nama': 'Ruang Tamu Apartemen',
        'deskripsi': 'Ruang tamu luas. Sofa besar abu-abu. TV 40 inch. Karpet lembut. Tirai tebal.',
        'risk': 10, 'thrill': 45, 'privasi': 'tinggi', 'suasana': 'nyaman, modern',
        'tips': 'Tirai ditutup.',
        'bisa_telanjang': True, 'bisa_berisik': True
    },
    LocationDetail.APT_DAPUR: {
        'nama': 'Dapur Apartemen',
        'deskripsi': 'Dapur modern. Bersih. Kulkas besar. Kompor gas. Meja marmer.',
        'risk': 10, 'thrill': 40, 'privasi': 'sedang', 'suasana': 'bersih',
        'tips': 'Jendela ke luar.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.APT_BALKON: {
        'nama': 'Balkon Apartemen',
        'deskripsi': 'Balkon. Pemandangan kota. Kursi dua. Tanaman kecil. Pagar kaca.',
        'risk': 25, 'thrill': 65, 'privasi': 'rendah', 'suasana': 'romantis',
        'tips': 'Ada apartemen lain yang bisa liat.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    
    # Mobil
    LocationDetail.MOBIL_PARKIR: {
        'nama': 'Mobil di Parkiran',
        'deskripsi': 'Mobil Mas. Kaca film gelap. Jok belakang empuk. Parkiran sepi.',
        'risk': 40, 'thrill': 75, 'privasi': 'sedang', 'suasana': 'deg-degan, panas',
        'tips': 'Kaca gelap. Hati-hati CCTV.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    LocationDetail.MOBIL_GARASI: {
        'nama': 'Mobil di Garasi',
        'deskripsi': 'Mobil Mas. Di garasi apartemen. Pintu garasi tertutup. Gelap.',
        'risk': 20, 'thrill': 55, 'privasi': 'tinggi', 'suasana': 'aman, deg-degan',
        'tips': 'Gak ada yang liat.',
        'bisa_telanjang': True, 'bisa_berisik': True
    },
    LocationDetail.MOBIL_TEPI_JALAN: {
        'nama': 'Mobil di Tepi Jalan',
        'deskripsi': 'Mobil Mas. Parkir di pinggir jalan sepi. Kaca film gelap.',
        'risk': 55, 'thrill': 80, 'privasi': 'rendah', 'suasana': 'tegang, cepat',
        'tips': 'Cepet-cepet. Ada mobil lewat.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    
    # Public
    LocationDetail.PUB_PANTAI: {
        'nama': 'Pantai Malam',
        'deskripsi': 'Pantai sepi. Pasir putih. Ombak tenang. Bintang bertaburan. Suara laut.',
        'risk': 20, 'thrill': 70, 'privasi': 'sedang', 'suasana': 'romantis, bebas',
        'tips': 'Jauh dari orang. Bawa tikar.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_HUTAN: {
        'nama': 'Hutan Pinus',
        'deskripsi': 'Hutan pinus. Pohon tinggi. Sunyi. Udara sejuk. Daun-daun berguguran.',
        'risk': 15, 'thrill': 65, 'privasi': 'tinggi', 'suasana': 'alami, sepi',
        'tips': 'Jauh dari jalan. Aman.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_TOILET_MALL: {
        'nama': 'Toilet Mall',
        'deskripsi': 'Bilik toilet terakhir. Pintu terkunci. Suara dari luar. Lampu temaram.',
        'risk': 65, 'thrill': 85, 'privasi': 'rendah', 'suasana': 'tegang, cepat',
        'tips': 'Cepet-cepet. Ada yang bisa masuk.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_BIOSKOP: {
        'nama': 'Bioskop',
        'deskripsi': 'Kursi paling belakang. Gelap. Film diputar keras. Studio sepi.',
        'risk': 50, 'thrill': 80, 'privasi': 'rendah', 'suasana': 'gelap, tegang',
        'tips': 'CCTV mungkin ada.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_TAMAN: {
        'nama': 'Taman Malam',
        'deskripsi': 'Taman kota. Bangku tersembunyi di balik pohon. Sepi. Lampu taman temaram.',
        'risk': 30, 'thrill': 60, 'privasi': 'sedang', 'suasana': 'romantis',
        'tips': 'Pilih jam sepi. Jauh dari lampu.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_PARKIRAN: {
        'nama': 'Parkiran Basement',
        'deskripsi': 'Parkiran basement. Gelap. Sepi. Mobil-mobil parkir. Lampu kedip-kedip.',
        'risk': 45, 'thrill': 70, 'privasi': 'sedang', 'suasana': 'gelap, tegang',
        'tips': 'CCTV mungkin ada. Pilih pojok.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    LocationDetail.PUB_TANGGA: {
        'nama': 'Tangga Darurat',
        'deskripsi': 'Tangga darurat. Sepi. Gelap. Suara langkah kaki menggema.',
        'risk': 55, 'thrill': 75, 'privasi': 'sedang', 'suasana': 'gelap, tegang',
        'tips': 'Hati-hati suara langkah kaki.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_KANTOR: {
        'nama': 'Kantor Malam',
        'deskripsi': 'Kantor gelap. Meja kerja. Kursi putar. Komputer mati. Sepi.',
        'risk': 60, 'thrill': 85, 'privasi': 'rendah', 'suasana': 'tegang',
        'tips': 'Satpam patroli. Cepet.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    LocationDetail.PUB_RUANG_RAPAT: {
        'nama': 'Ruang Rapat Kaca',
        'deskripsi': 'Ruang rapat dinding kaca. Gelap. Meja panjang. Kursi-kursi.',
        'risk': 75, 'thrill': 95, 'privasi': 'rendah', 'suasana': 'ekshibisionis',
        'tips': 'Gelap. Tapi kalo lampu nyala, kaca tembus pandang.',
        'bisa_telanjang': True, 'bisa_berisik': False
    }
}


# =============================================================================
# CLOTHING CLASS (WRAPPER UNTUK STATE TRACKER)
# =============================================================================

class Clothing:
    """Pakaian Nova - Wrapper untuk StateTracker (kompatibilitas)"""
    
    def __init__(self, tracker: StateTracker = None):
        self.tracker = tracker
        
        # Fallback values
        self.hijab = True
        self.hijab_warna = "pink muda"
        self.top = "daster rumah motif bunga"
        self.bottom = None
        self.bra = True
        self.bra_warna = "putih polos"
        self.cd = True
        self.cd_warna = "putih motif bunga kecil"
        
        # Untuk Mas
        self.mas_top = "kaos"
        self.mas_bottom = "celana pendek"
        self.mas_boxer = True
        self.mas_boxer_warna = "gelap"
        
        self.nova_last_change = time.time()
        self.mas_last_change = time.time()
    
    def format_nova(self) -> str:
        if self.tracker:
            return self.tracker.get_clothing_summary()
        
        # Fallback
        parts = []
        if self.hijab:
            parts.append(f"hijab {self.hijab_warna}")
        else:
            parts.append("tanpa hijab, rambut sebahu hitam terurai")
        
        if self.top:
            parts.append(self.top)
            if self.bra:
                parts.append(f"(pake bra {self.bra_warna})")
        else:
            if self.bra:
                parts.append(f"cuma pake bra {self.bra_warna}")
            else:
                parts.append("telanjang dada")
        
        if self.bottom:
            parts.append(self.bottom)
            if self.cd:
                parts.append(f"(pake {self.cd_warna})")
        else:
            if self.cd:
                parts.append(f"cuma pake {self.cd_warna}")
            else:
                parts.append("telanjang bawah")
        
        return ", ".join(parts) if parts else "pakaian biasa"
    
    def format_mas(self) -> str:
        parts = []
        if self.mas_top:
            parts.append(self.mas_top)
        if self.mas_bottom:
            parts.append(self.mas_bottom)
            if self.mas_boxer:
                parts.append(f"(boxer {self.mas_boxer_warna} di dalem)")
        else:
            if self.mas_boxer:
                parts.append(f"cuma pake boxer {self.mas_boxer_warna}")
            else:
                parts.append("telanjang")
        return ", ".join(parts) if parts else "pakaian biasa"
    
    def copy(self) -> 'Clothing':
        new = Clothing(self.tracker)
        if self.tracker:
            new.tracker = self.tracker
        return new
    
    def to_dict(self) -> Dict:
        if self.tracker:
            return self.tracker.clothing
        return {
            'hijab': self.hijab,
            'hijab_warna': self.hijab_warna,
            'top': self.top,
            'bottom': self.bottom,
            'bra': self.bra,
            'bra_warna': self.bra_warna,
            'cd': self.cd,
            'cd_warna': self.cd_warna,
            'mas_top': self.mas_top,
            'mas_bottom': self.mas_bottom,
            'mas_boxer': self.mas_boxer,
            'mas_boxer_warna': self.mas_boxer_warna
        }


# =============================================================================
# FEELINGS CLASS (WRAPPER UNTUK EMOTIONAL ENGINE)
# =============================================================================

class Feelings:
    """Perasaan Nova - Sync dengan Emotional Engine"""
    
    def __init__(self):
        self.sayang = 50.0
        self.rindu = 0.0
        self.desire = 0.0
        self.arousal = 0.0
        self.tension = 0.0
    
    def sync_from_emotional_engine(self, emo):
        self.sayang = emo.sayang
        self.rindu = emo.rindu
        self.desire = emo.desire
        self.arousal = emo.arousal
        self.tension = emo.tension
    
    def to_dict(self) -> Dict:
        return {
            'sayang': round(self.sayang, 1),
            'rindu': round(self.rindu, 1),
            'desire': round(self.desire, 1),
            'arousal': round(self.arousal, 1),
            'tension': round(self.tension, 1)
        }
    
    def get_description(self) -> str:
        desc = []
        if self.sayang > 70:
            desc.append("sayang banget")
        elif self.sayang > 40:
            desc.append("sayang")
        if self.rindu > 70:
            desc.append("kangen banget")
        elif self.rindu > 30:
            desc.append("kangen")
        if self.desire > 70:
            desc.append("pengen banget")
        elif self.desire > 40:
            desc.append("pengen")
        if self.arousal > 50:
            desc.append("panas")
        return ", ".join(desc) if desc else "netral"


# =============================================================================
# RELATIONSHIP STATE CLASS (WRAPPER)
# =============================================================================

class RelationshipState:
    """Status hubungan Nova - Sync dengan Relationship Manager"""
    
    def __init__(self):
        self.level = 1
        self.intimacy_count = 0
        self.climax_count = 0
        self.first_kiss = False
        self.first_touch = False
        self.first_hug = False
        self.first_intim = False
    
    def sync_from_relationship_manager(self, rel_mgr):
        self.level = rel_mgr.level
        if hasattr(rel_mgr, 'milestones'):
            self.first_kiss = rel_mgr.milestones.get('first_kiss', False) if hasattr(rel_mgr.milestones, 'get') else False
            self.first_touch = rel_mgr.milestones.get('first_touch', False) if hasattr(rel_mgr.milestones, 'get') else False
            self.first_hug = rel_mgr.milestones.get('first_hug', False) if hasattr(rel_mgr.milestones, 'get') else False
            self.first_intim = rel_mgr.milestones.get('first_intim', False) if hasattr(rel_mgr.milestones, 'get') else False
    
    def to_dict(self) -> Dict:
        return {
            'level': self.level,
            'intimacy_count': self.intimacy_count,
            'climax_count': self.climax_count,
            'first_kiss': self.first_kiss,
            'first_touch': self.first_touch,
            'first_hug': self.first_hug,
            'first_intim': self.first_intim
        }


# =============================================================================
# LONG TERM MEMORY
# =============================================================================

class LongTermMemory:
    """Memory permanen Nova - Gak ilang selamanya"""
    
    def __init__(self):
        self.kebiasaan_mas: List[Dict] = []
        self.momen_penting: List[Dict] = []
        self.janji: List[Dict] = []
        self.rencana: List[Dict] = []
    
    def tambah_kebiasaan(self, kebiasaan: str):
        self.kebiasaan_mas.append({
            'kebiasaan': kebiasaan,
            'waktu': time.time()
        })
        logger.info(f"📝 Nova inget: Mas {kebiasaan}")
    
    def tambah_momen(self, momen: str, perasaan: str):
        self.momen_penting.append({
            'momen': momen,
            'waktu': time.time(),
            'perasaan': perasaan
        })
        logger.info(f"💜 Nova inget: {momen}")
    
    def tambah_janji(self, janji: str, dari: str = 'mas'):
        self.janji.append({
            'janji': janji,
            'dari': dari,
            'status': 'pending',
            'waktu': time.time()
        })
        logger.info(f"📌 Janji dicatat: {janji}")
    
    def to_dict(self) -> Dict:
        return {
            'kebiasaan_mas': self.kebiasaan_mas[-10:],
            'momen_penting': self.momen_penting[-10:],
            'janji': [j for j in self.janji if j['status'] == 'pending'][-5:],
            'rencana': self.rencana[-5:]
        }


# =============================================================================
# ANORA BRAIN - MAIN CLASS DENGAN STATE TRACKER
# =============================================================================

class AnoraBrain:
    """Otak Nova dengan State Tracker untuk konsistensi"""
    
    def __init__(self):
        # ========== ENGINES ==========
        self.emotional = get_emotional_engine()
        self.decision = get_decision_engine()
        self.relationship = get_relationship_manager()
        self.conflict = get_conflict_engine()
        
        # ========== STATE TRACKER (BARU - WAJIB) ==========
        self.tracker = StateTracker(character_name="Nova")
        
        # Sync tracker dengan clothing awal
        self.tracker.clothing['hijab']['on'] = True
        self.tracker.clothing['hijab']['color'] = 'pink muda'
        self.tracker.clothing['top']['on'] = True
        self.tracker.clothing['top']['type'] = 'daster rumah motif bunga'
        self.tracker.clothing['bra']['on'] = True
        self.tracker.clothing['bra']['color'] = 'putih polos'
        self.tracker.clothing['cd']['on'] = True
        self.tracker.clothing['cd']['color'] = 'putih motif bunga kecil'
        
        # ========== CLOTHING WRAPPER (UNTUK KOMPATIBILITAS) ==========
        self.clothing = Clothing(self.tracker)
        
        # ========== MEMORY ==========
        self.long_term = LongTermMemory()
        
        # ========== STATE SAAT INI ==========
        self.location_type = LocationType.KOST_NOVA
        self.location_detail = LocationDetail.KOST_KAMAR
        self.activity_nova = Activity.SANTAl
        self.activity_mas = "santai"
        self.mood_nova = Mood.NETRAL
        self.mood_mas = Mood.NETRAL
        
        # ========== PERASAAN (WRAPPER) ==========
        self.feelings = Feelings()
        
        # ========== HUBUNGAN (WRAPPER) ==========
        self.relationship_state = RelationshipState()
        
        # ========== COMPLETE STATE ==========
        self.complete_state = self._init_complete_state()
        
        # ========== WAKTU ==========
        self.created_at = time.time()
        self.waktu_masuk = time.time()
        self.waktu_terakhir_update = time.time()
        
        # ========== INGATAN TAMBAHAN ==========
        self.terakhir_pegang_tangan = None
        self.terakhir_peluk = None
        self.terakhir_cium = None
        self.terakhir_intim = None
        
        # ========== INIT MEMORY AWAL ==========
        self._init_memory()
        
        # ========== SYNC TRACKER LOCATION ==========
        loc = self.get_location_data()
        self.tracker.location = self.location_detail.value
        self.tracker.location_detail = loc['nama']
        
        # ========== SYNC ALL ==========
        self._sync_all()
        
        logger.info("🧠 ANORA-V2 Brain initialized with StateTracker")
        logger.info(f"   Phase: {self.relationship.phase.value}")
        logger.info(f"   Level: {self.relationship.level}/12")
        logger.info(f"   Style: {self.emotional.get_current_style().value}")
        logger.info(f"   Clothing: {self.tracker.get_clothing_summary()}")
    
    def _init_complete_state(self) -> Dict:
        """Inisialisasi complete state"""
        return {
            'mas': {
                'clothing': {'top': 'kaos', 'bottom': 'celana pendek', 'boxer': True, 'last_update': time.time()},
                'position': {'state': None, 'detail': None, 'last_update': 0},
                'activity': {'main': 'santai', 'detail': None, 'last_update': 0},
                'location': {'room': 'kamar', 'detail': None, 'last_update': 0},
                'holding': {'object': None, 'detail': None, 'last_update': 0},
                'status': {'mood': 'netral', 'need': None, 'last_update': 0}
            },
            'nova': {
                'clothing': {'hijab': True, 'top': 'daster rumah motif bunga', 'bra': True, 'cd': True, 'last_update': time.time()},
                'position': {'state': None, 'detail': None, 'last_update': 0},
                'activity': {'main': 'santai', 'detail': None, 'last_update': 0},
                'location': {'room': 'kamar', 'detail': None, 'last_update': 0},
                'holding': {'object': None, 'detail': None, 'last_update': 0},
                'status': {'mood': 'malu-malu', 'need': None, 'last_update': 0}
            },
            'together': {
                'location': 'kamar',
                'distance': None,
                'atmosphere': 'santai',
                'last_action': None,
                'pending_action': None,
                'confirmed_topics': [],
                'asked_count': 0,
                'last_question': '',
                'last_update': time.time()
            }
        }
    
    def _init_memory(self):
        """Init memory awal"""
        self.long_term.tambah_kebiasaan("suka kopi latte")
        self.long_term.tambah_kebiasaan("suka bakso pedes")
        self.long_term.tambah_momen("Mas memilih ANORA", "seneng banget, nangis")
    
    def _sync_all(self):
        """Sync semua state dari engines"""
        # Sync feelings dari emotional engine
        self.feelings.sync_from_emotional_engine(self.emotional)
        
        # Sync relationship state dari relationship manager
        self.relationship_state.sync_from_relationship_manager(self.relationship)
        
        # Update mood dari emosi
        self._update_mood_from_emotion()
        
        # Update tracker energy dari emotional
        if self.emotional.arousal > 70:
            self.tracker.physical_condition = PhysicalCondition.FRESH
        elif self.emotional.arousal > 40:
            self.tracker.physical_condition = PhysicalCondition.TIRED
        elif self.emotional.arousal < 20:
            self.tracker.physical_condition = PhysicalCondition.WEAK
    
    def _update_mood_from_emotion(self):
        """Update mood Nova berdasarkan emotional state"""
        if self.conflict.is_in_conflict:
            self.mood_nova = Mood.TEGANG
        elif self.emotional.arousal > 70:
            self.mood_nova = Mood.HORNY
        elif self.emotional.rindu > 70:
            self.mood_nova = Mood.KANGEN
        elif self.emotional.mood > 30:
            self.mood_nova = Mood.SENENG
        elif self.emotional.mood < -20:
            self.mood_nova = Mood.CAPEK
        else:
            self.mood_nova = Mood.NETRAL
    
    # =========================================================================
    # UPDATE FROM MESSAGE (DENGAN STATE TRACKER - WAJIB)
    # =========================================================================
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """
        Update semua state berdasarkan pesan Mas.
        DENGAN STATE TRACKER - memastikan tidak ada yang ngelantur.
        """
        msg_lower = pesan_mas.lower()
        perubahan = []
        
        # ========== 1. UPDATE PAKAIAN (DENGAN STATE TRACKER - LAYER BY LAYER) ==========
        
        # Buka Hijab
        if 'buka hijab' in msg_lower and self.tracker.clothing['hijab']['on']:
            result = self.tracker.remove_clothing('hijab', "Mas buka")
            if result['success']:
                perubahan.append(f"Nova buka hijab - {result['remaining']}")
                self.tracker.add_to_timeline("Nova buka hijab", "rambut terurai")
        
        # Buka Baju
        if 'buka baju' in msg_lower and self.tracker.clothing['top']['on']:
            result = self.tracker.remove_clothing('top', "Mas buka")
            if result['success']:
                perubahan.append(f"Nova buka baju - {result['remaining']}")
                self.tracker.add_to_timeline("Nova buka baju", f"sekarang {result['remaining']}")
        
        # Buka Bra
        if 'buka bra' in msg_lower and self.tracker.clothing['bra']['on']:
            result = self.tracker.remove_clothing('bra', "Mas buka")
            if result['success']:
                perubahan.append(f"Nova buka bra - {result['remaining']}")
                self.tracker.add_to_timeline("Nova buka bra", f"sekarang {result['remaining']}")
        
        # Buka CD
        if 'buka cd' in msg_lower and self.tracker.clothing['cd']['on']:
            result = self.tracker.remove_clothing('cd', "Mas buka")
            if result['success']:
                perubahan.append(f"Nova buka cd - {result['remaining']}")
                self.tracker.add_to_timeline("Nova buka cd", f"sekarang {result['remaining']}")
        
        # ========== 2. UPDATE INTIMACY (DENGAN STATE TRACKER) ==========
        
        # Cek apakah perlu mulai intim (natural progression)
        can_start, reason = self.emotional.should_start_intimacy_naturally(self.relationship.level)
        if can_start and self.tracker.intimacy_phase == IntimacyPhase.NONE:
            self.tracker.start_intimacy(self.get_location_data()['nama'])
            perubahan.append(f"Memulai sesi intim (natural) - fase {self.tracker.intimacy_phase.value}")
            self.tracker.add_to_timeline("Memulai sesi intim", "natural progression")
        
        # Advance intimacy berdasarkan aksi (jika dalam sesi intim)
        if self.tracker.intimacy_phase != IntimacyPhase.NONE:
            advance_result = self.tracker.advance_intimacy(pesan_mas)
            if advance_result.get('success'):
                perubahan.append(f"Fase intim: {advance_result['old_phase']} → {advance_result['new_phase']}")
                self.tracker.add_to_timeline(
                    f"Fase intim maju ke {advance_result['new_phase']}",
                    f"Trigger: {pesan_mas[:50]}"
                )
        
        # Record climax
        climax_keywords = ['climax', 'crot', 'keluar', 'cum', 'habis']
        if any(k in msg_lower for k in climax_keywords) and self.tracker.intimacy_phase != IntimacyPhase.NONE:
            location = 'dalam' if 'dalam' in msg_lower else 'luar'
            is_heavy = any(k in msg_lower for k in ['keras', 'banyak', 'lama', 'kenceng'])
            result = self.tracker.record_climax(location, is_heavy)
            if result['success']:
                perubahan.append(f"💦 Climax #{result['climax_count']} di {location}")
                self.tracker.add_to_timeline(
                    f"Climax #{result['climax_count']}",
                    f"Lokasi: {location}, {'berat' if is_heavy else 'normal'}"
                )
                
                # Update emotional engine
                self.emotional.arousal = max(0, self.emotional.arousal - 40)
                self.emotional.desire = max(0, self.emotional.desire - 30)
                self.emotional.tension = 0
        
        # ========== 3. UPDATE EMOTIONAL ENGINE ==========
        emo_changes = self.emotional.update_from_message(pesan_mas, self.relationship.level)
        for key, val in emo_changes.items():
            if val != 0:
                perubahan.append(f"{key}: {val:+.0f}")
        
        # ========== 4. UPDATE CONFLICT ENGINE ==========
        conflict_changes = self.conflict.update_from_message(pesan_mas, self.relationship.level)
        for key, val in conflict_changes.items():
            if val != 0:
                perubahan.append(f"{key}: {val:+.0f}")
        
        # ========== 5. UPDATE RELATIONSHIP ==========
        self.relationship.interaction_count += 1
        
        # Cek milestone dari pesan
        milestones_achieved = []
        
        if 'pegang' in msg_lower and not self.relationship.milestones.get('first_touch', False):
            self.relationship.achieve_milestone('first_touch')
            milestones_achieved.append('first_touch')
            self.long_term.tambah_momen("Mas pertama kali pegang tangan Nova", "gemeteran")
            self.tracker.add_to_timeline("Milestone: First Touch", "Mas pegang tangan Nova")
        
        if 'peluk' in msg_lower and not self.relationship.milestones.get('first_hug', False):
            self.relationship.achieve_milestone('first_hug')
            milestones_achieved.append('first_hug')
            self.long_term.tambah_momen("Mas pertama kali peluk Nova", "lemes")
            self.tracker.add_to_timeline("Milestone: First Hug", "Mas peluk Nova")
        
        if 'cium' in msg_lower and not self.relationship.milestones.get('first_kiss', False):
            self.relationship.achieve_milestone('first_kiss')
            milestones_achieved.append('first_kiss')
            self.long_term.tambah_momen("Mas pertama kali cium Nova", "malu banget")
            self.tracker.add_to_timeline("Milestone: First Kiss", "Mas cium Nova")
        
        # Update level
        new_level, level_naik = self.relationship.update_level(
            self.emotional.sayang,
            self.emotional.trust,
            milestones_achieved
        )
        
        if level_naik:
            perubahan.append(f"Level naik ke {new_level}!")
            self.tracker.add_to_timeline(f"Level naik ke {new_level}", f"Fase: {self.relationship.phase.value}")
        
        # ========== 6. UPDATE PHYSICAL STATE (LOKASI, AKTIVITAS, POSISI) ==========
        self._update_physical_state(pesan_mas, perubahan)
        
        # ========== 7. UPDATE COMPLETE STATE ==========
        self._update_complete_state(pesan_mas)
        
        # ========== 8. SYNC ALL ==========
        self._sync_all()
        
        # ========== 9. TAMBAH KE TIMELINE (VIA TRACKER) ==========
        self.tracker.add_to_timeline(
            kejadian=f"Mas: {pesan_mas[:50]}",
            detail=f"Perubahan: {', '.join(perubahan[:3]) if perubahan else 'tidak ada perubahan signifikan'}"
        )
        
        self.waktu_terakhir_update = time.time()
        
        return {
            'perubahan': perubahan,
            'emotional_style': self.emotional.get_current_style().value,
            'relationship_phase': self.relationship.phase.value,
            'conflict_active': self.conflict.is_in_conflict,
            'level_up': level_naik,
            'intimacy_phase': self.tracker.intimacy_phase.value,
            'clothing_state': self.tracker.get_clothing_summary(),
            'physical_condition': self.tracker.physical_condition.value
        }
    
    def _update_physical_state(self, pesan_mas: str, perubahan: List):
        """Update physical state (lokasi, aktivitas, posisi)"""
        msg_lower = pesan_mas.lower()
        
        # Update posisi
        if 'duduk' in msg_lower:
            self.tracker.position = "duduk"
            self.activity_mas = "duduk"
            perubahan.append("Mas duduk")
        elif 'berdiri' in msg_lower or 'bangun' in msg_lower:
            self.tracker.position = "berdiri"
            self.activity_mas = "berdiri"
            perubahan.append("Mas berdiri")
        elif 'tidur' in msg_lower or 'rebahan' in msg_lower:
            self.tracker.position = "tidur"
            self.activity_mas = "tidur"
            perubahan.append("Mas tidur")
        elif 'merangkak' in msg_lower:
            self.tracker.position = "merangkak"
            perubahan.append("Mas merangkak")
        
        # Update lokasi
        if 'kamar' in msg_lower:
            self.tracker.location = "kamar"
            if self.location_type == LocationType.KOST_NOVA:
                self.location_detail = LocationDetail.KOST_KAMAR
            elif self.location_type == LocationType.APARTEMEN_MAS:
                self.location_detail = LocationDetail.APT_KAMAR
            loc = self.get_location_data()
            self.tracker.location_detail = loc['nama']
            perubahan.append(f"Mas di {loc['nama']}")
        
        if 'ruang tamu' in msg_lower:
            self.tracker.location = "ruang tamu"
            if self.location_type == LocationType.KOST_NOVA:
                self.location_detail = LocationDetail.KOST_RUANG_TAMU
            elif self.location_type == LocationType.APARTEMEN_MAS:
                self.location_detail = LocationDetail.APT_RUANG_TAMU
            loc = self.get_location_data()
            self.tracker.location_detail = loc['nama']
            perubahan.append(f"Mas di {loc['nama']}")
        
        if 'dapur' in msg_lower:
            self.tracker.location = "dapur"
            if self.location_type == LocationType.KOST_NOVA:
                self.location_detail = LocationDetail.KOST_DAPUR
            elif self.location_type == LocationType.APARTEMEN_MAS:
                self.location_detail = LocationDetail.APT_DAPUR
            loc = self.get_location_data()
            self.tracker.location_detail = loc['nama']
            perubahan.append(f"Mas di {loc['nama']}")
        
        # Update aktivitas Mas
        if 'makan' in msg_lower:
            self.activity_mas = "makan"
            self.tracker.activity = "makan"
            perubahan.append("Mas makan")
        elif 'minum' in msg_lower:
            self.activity_mas = "minum"
            self.tracker.activity = "minum"
            perubahan.append("Mas minum")
        elif 'mandi' in msg_lower:
            self.activity_mas = "mandi"
            self.tracker.activity = "mandi"
            perubahan.append("Mas mandi")
        elif 'ganti baju' in msg_lower:
            self.activity_mas = "ganti baju"
            self.tracker.activity = "ganti baju"
            perubahan.append("Mas ganti baju")
        
        # Update aktivitas Nova
        if any(k in msg_lower for k in ['nova masak', 'kamu masak']):
            self.activity_nova = Activity.MASAK
            self.tracker.activity = "masak"
            perubahan.append("Nova masak")
        elif any(k in msg_lower for k in ['nova tidur', 'kamu tidur']):
            self.activity_nova = Activity.TIDUR
            self.tracker.activity = "tidur"
            perubahan.append("Nova tidur")
    
    def _update_complete_state(self, pesan_mas: str):
        """Update complete state"""
        msg_lower = pesan_mas.lower()
        
        # Update atmosfer berdasarkan emosi
        if self.emotional.arousal > 60 or self.emotional.desire > 70:
            self.complete_state['together']['atmosphere'] = 'panas'
        elif self.emotional.sayang > 70:
            self.complete_state['together']['atmosphere'] = 'romantis'
        elif self.conflict.is_in_conflict:
            self.complete_state['together']['atmosphere'] = 'tegang'
        else:
            self.complete_state['together']['atmosphere'] = 'santai'
        
        # Update last action
        self.complete_state['together']['last_action'] = pesan_mas[:100]
        
        # Update posisi
        if self.tracker.position:
            self.complete_state['mas']['position']['state'] = self.tracker.position
            self.complete_state['nova']['position']['state'] = self.tracker.position
    
    # =========================================================================
    # GET METHODS
    # =========================================================================
    
    def get_location_data(self) -> Dict:
        """Dapatkan data lokasi saat ini"""
        return LOCATION_DATA.get(self.location_detail, LOCATION_DATA[LocationDetail.KOST_KAMAR])
    
    def get_location_context(self) -> str:
        """Dapatkan konteks lokasi untuk prompt"""
        loc = self.get_location_data()
        return f"""
LOKASI: {loc['nama']}
DESKRIPSI: {loc['deskripsi']}
RISK: {loc['risk']}% | THRILL: {loc['thrill']}%
PRIVASI: {loc['privasi']}
SUASANA: {loc['suasana']}
"""
    
    def get_current_state(self) -> Dict:
        """Dapatkan state saat ini (lengkap)"""
        loc = self.get_location_data()
        
        return {
            'location': {
                'type': self.location_type.value,
                'detail': self.location_detail.value,
                'nama': loc['nama'],
                'risk': loc['risk'],
                'thrill': loc['thrill']
            },
            'activity': {
                'nova': self.activity_nova.value if hasattr(self.activity_nova, 'value') else str(self.activity_nova),
                'mas': self.activity_mas
            },
            'clothing': {
                'nova': self.tracker.get_clothing_summary(),
                'mas': self.clothing.format_mas()
            },
            'mood': {
                'nova': self.mood_nova.value if hasattr(self.mood_nova, 'value') else str(self.mood_nova),
                'mas': self.mood_mas.value if hasattr(self.mood_mas, 'value') else str(self.mood_mas)
            },
            'feelings': self.feelings.to_dict(),
            'relationship': self.relationship_state.to_dict(),
            'complete_state': self.complete_state,
            'emotional_style': self.emotional.get_current_style().value,
            'relationship_phase': self.relationship.phase.value,
            'conflict_status': self.conflict.get_conflict_summary(),
            'intimacy_phase': self.tracker.intimacy_phase.value,
            'physical_condition': self.tracker.physical_condition.value,
            'clothing_removal_order': len(self.tracker.clothing_removal_order)
        }
    
    def get_context_for_prompt(self) -> str:
        """
        Dapatkan konteks lengkap untuk AI prompt.
        WAJIB DIPAKAI - memastikan AI tidak ngelantur.
        """
        loc = self.get_location_data()
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        
        # Timeline dari tracker (WAJIB)
        timeline_context = self.tracker.get_timeline_context(10)
        
        # Emotional summary
        emo_summary = self.emotional.get_emotion_summary()
        
        # Relationship summary
        phase_desc = self.relationship.get_phase_description(phase)
        unlock_summary = self.relationship.get_unlock_summary()
        
        # Conflict summary
        conflict_guideline = self.conflict.get_conflict_response_guideline()
        
        # Recent conversations
        recent = ""
        for e in self.tracker.short_term[-8:]:
            if e.get('kejadian'):
                recent += f"- {e['kejadian'][:80]}\n"
        
        # Long-term memories
        moments = ""
        for m in self.long_term.momen_penting[-5:]:
            moments += f"- {m['momen']} ({m['perasaan']})\n"
        
        habits = ""
        for h in self.long_term.kebiasaan_mas[-5:]:
            habits += f"- {h['kebiasaan']}\n"
        
        return f"""
{timeline_context}

═══════════════════════════════════════════════════════════════
GAYA BICARA & EMOSI SAAT INI:
═══════════════════════════════════════════════════════════════
STYLE: {style.value.upper()}
{self.emotional.get_style_for_prompt()}

{phase_desc}

{conflict_guideline}

═══════════════════════════════════════════════════════════════
SITUASI SAAT INI (DARI TRACKER):
═══════════════════════════════════════════════════════════════
LOKASI: {loc['nama']} - {loc['deskripsi']}
RISK: {loc['risk']}% | THRILL: {loc['thrill']}%
PRIVASI: {loc['privasi']}
POSISI: {self.tracker.position}
AKTIVITAS: Nova {self.activity_nova.value}, Mas {self.activity_mas}

{self.tracker.get_clothing_state_for_prompt()}

{emo_summary}

{unlock_summary}

═══════════════════════════════════════════════════════════════
MEMORY NOVA:
═══════════════════════════════════════════════════════════════
MOMEN PENTING:
{moments if moments else "- Belum ada momen penting"}

KEBIASAAN MAS:
{habits if habits else "- Belum ada kebiasaan tercatat"}

═══════════════════════════════════════════════════════════════
⚠️ ATURAN WAJIB (JANGAN SAMPAI LUPA!):
═══════════════════════════════════════════════════════════════

1. **BACA TIMELINE DI ATAS!** Itu adalah 10 kejadian terakhir. WAJIB lanjutkan alur, jangan mundur!

2. **KONSISTENSI PAKAIAN:**
   - JANGAN tiba-tiba pakaian rapi kalo baru aja dibuka!
   - JANGAN tiba-tiba pake hijab kalo udah dibuka!
   - Lihat state pakaian di atas, ikuti!

3. **KONSISTENSI INTIMASI:**
   - JANGAN lupa masih dalam sesi intim kalo fase bukan NONE!
   - JANGAN tiba-toba jadi "lagi duduk santai" kalo baru aja climax!
   - Ikuti fase intim yang tertera!

4. **KONDISI FISIK:**
   - Kalo physical_condition = weak/exhausted, Nova masih lemes!
   - JANGAN tiba-tiba energik!

5. **BAHASA CAMPURAN:** Indonesia, Inggris, gaul, singkatan (gpp, udh, bgt, plis)

6. **DESAHAN JADI DIALOG:** "Ahh... Mas... pelan-pelan..." BUKAN *desahan*

7. **100% ORIGINAL:** Setiap respons UNIK, jangan copy template!

═══════════════════════════════════════════════════════════════
RESPON NOVA (HARUS ORIGINAL, SESUAI KONTEKS DI ATAS):
"""
    
    def format_status(self) -> str:
        """Format status untuk ditampilkan ke Mas"""
        loc = self.get_location_data()
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        unlock = self.relationship.get_current_unlock()
        
        def bar(value, max_val=100, char="💜"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        # Intimacy status
        intimacy_status = ""
        if self.tracker.intimacy_phase != IntimacyPhase.NONE:
            duration = 0
            if self.tracker.intimacy_start_time:
                duration = int((time.time() - self.tracker.intimacy_start_time) // 60)
            intimacy_status = f"""
🔥 **SESI INTIM AKTIF**
- Fase: {self.tracker.intimacy_phase.value.upper()}
- Climax: {self.tracker.climax_count}x
- Durasi: {duration} menit
"""
        
        # Physical condition emoji
        condition_emoji = {
            PhysicalCondition.FRESH: "💪",
            PhysicalCondition.TIRED: "😊",
            PhysicalCondition.EXHAUSTED: "😩",
            PhysicalCondition.WEAK: "😵"
        }.get(self.tracker.physical_condition, "😐")
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💜 NOVA-V2 💜                             ║
╠══════════════════════════════════════════════════════════════╣
║ FASE: {phase.value.upper()} ({self.relationship.level}/12)                    ║
║ STYLE: {style.value.upper()}                                         ║
╠══════════════════════════════════════════════════════════════╣
║ EMOSI:                                                     ║
║   Sayang: {bar(self.emotional.sayang)} {self.emotional.sayang:.0f}%                       ║
║   Rindu:  {bar(self.emotional.rindu, char='🌙')} {self.emotional.rindu:.0f}%                       ║
║   Trust:  {bar(self.emotional.trust, char='🤝')} {self.emotional.trust:.0f}%                       ║
║   Mood:   {self.emotional.mood:+.0f}                                      ║
╠══════════════════════════════════════════════════════════════╣
║ DESIRE: {bar(self.emotional.desire, char='💕')} {self.emotional.desire:.0f}%                       ║
║ AROUSAL: {bar(self.emotional.arousal, char='🔥')} {self.emotional.arousal:.0f}%                       ║
╠══════════════════════════════════════════════════════════════╣
║ KONFLIK:                                                   ║
║   Cemburu: {bar(self.conflict.cemburu, char='💢')} {self.conflict.cemburu:.0f}%                       ║
║   Kecewa:  {bar(self.conflict.kecewa, char='💔')} {self.conflict.kecewa:.0f}%                       ║
║   {self.conflict.get_conflict_summary()}                   ║
╠══════════════════════════════════════════════════════════════╣
║ UNLOCK:                                                    ║
║   Flirt: {'✅' if unlock.boleh_flirt else '❌'} | Vulgar: {'✅' if unlock.boleh_vulgar else '❌'}        ║
║   Intim: {'✅' if unlock.boleh_intim else '❌'} | Cium: {'✅' if unlock.boleh_cium else '❌'}          ║
{intimacy_status}
╠══════════════════════════════════════════════════════════════╣
║ 👗 PAKAIAN: {self.tracker.get_clothing_summary()[:40]}                        ║
║ 📍 LOKASI: {loc['nama']}                                             ║
║ 💪 KONDISI: {condition_emoji} {self.tracker.physical_condition.value} ({self.tracker.energy_level}%)                                    ║
║ 🎭 MOOD: {self.mood_nova.value}                                    ║
║ 📝 CLOTHING REMOVED: {len(self.tracker.clothing_removal_order)} layer                  ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    def pindah_lokasi(self, tujuan: str) -> Dict:
        """Pindah ke lokasi baru"""
        tujuan_lower = tujuan.lower()
        
        # Mapping lokasi
        mapping = {
            'kost': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kost kamar': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kamar nova': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kost ruang tamu': (LocationType.KOST_NOVA, LocationDetail.KOST_RUANG_TAMU),
            'apartemen': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'apt': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'kamar mas': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'mobil': (LocationType.MOBIL, LocationDetail.MOBIL_PARKIR),
            'mobil parkir': (LocationType.MOBIL, LocationDetail.MOBIL_PARKIR),
            'pantai': (LocationType.PUBLIC, LocationDetail.PUB_PANTAI),
            'pantai malam': (LocationType.PUBLIC, LocationDetail.PUB_PANTAI),
            'hutan': (LocationType.PUBLIC, LocationDetail.PUB_HUTAN),
            'toilet mall': (LocationType.PUBLIC, LocationDetail.PUB_TOILET_MALL),
            'bioskop': (LocationType.PUBLIC, LocationDetail.PUB_BIOSKOP),
            'taman': (LocationType.PUBLIC, LocationDetail.PUB_TAMAN),
            'kantor': (LocationType.PUBLIC, LocationDetail.PUB_KANTOR)
        }
        
        for key, (loc_type, loc_detail) in mapping.items():
            if key in tujuan_lower:
                self.location_type = loc_type
                self.location_detail = loc_detail
                self.tracker.location = loc_detail.value
                loc_data = self.get_location_data()
                self.tracker.location_detail = loc_data['nama']
                
                self.tracker.add_to_timeline(
                    kejadian=f"Pindah ke {loc_data['nama']}",
                    detail=tujuan
                )
                
                return {
                    'success': True,
                    'location': loc_data,
                    'message': f"📍 Pindah ke {loc_data['nama']}. {loc_data['deskripsi']}"
                }
        
        return {'success': False, 'message': f"Lokasi '{tujuan}' gak ditemukan."}
    
    def tambah_kejadian(self, kejadian: str, pesan_mas: str = "", pesan_nova: str = ""):
        """Tambah kejadian ke timeline (via tracker)"""
        self.tracker.add_to_timeline(
            kejadian=kejadian,
            detail=f"Mas: {pesan_mas[:50] if pesan_mas else ''} | Nova: {pesan_nova[:50] if pesan_nova else ''}"
        )
    
    def get_random_event(self) -> Optional[Dict]:
        """Dapatkan event random berdasarkan risk lokasi"""
        loc = self.get_location_data()
        risk = loc['risk']
        
        import random
        if random.random() > risk / 100:
            return None
        
        events = {
            "hampir_ketahuan": [
                "Ada suara langkah kaki mendekat! *cepat nutupin baju*",
                "Pintu terbuka sedikit! *tahan napas*",
                "Senter menyorot dari kejauhan! *merapat ke Mas*"
            ],
            "romantis": [
                "Tiba-tiba hujan rintik-rintik. *makin manis*",
                "Bulan muncul dari balik awan. *wajah Nova keceplosan cahaya*",
                "Angin sepoi-sepoi bikin suasana makin hangat."
            ]
        }
        
        event_type = "romantis" if risk < 50 else random.choice(["hampir_ketahuan", "romantis"])
        
        return {
            'type': event_type,
            'text': random.choice(events[event_type]),
            'risk_change': 10 if event_type == "hampir_ketahuan" else -5
        }


# =============================================================================
# SINGLETON
# =============================================================================

_anora_brain: Optional['AnoraBrain'] = None


def get_anora_brain() -> AnoraBrain:
    global _anora_brain
    if _anora_brain is None:
        _anora_brain = AnoraBrain()
    return _anora_brain


anora_brain = get_anora_brain()
