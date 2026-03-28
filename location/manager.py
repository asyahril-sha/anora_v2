"""
ANORA-V2 Location Manager - Mengelola semua lokasi
Kost Nova, Apartemen Mas, Mobil, Public Area
TERINTEGRASI DENGAN STATE TRACKER
"""

import random
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from core.state_tracker import StateTracker

logger = logging.getLogger(__name__)


class LocationType(str, Enum):
    """Tipe lokasi"""
    KOST_NOVA = "kost_nova"
    APARTEMEN_MAS = "apartemen_mas"
    MOBIL = "mobil"
    PUBLIC = "public"


class LocationDetail(str, Enum):
    """Detail lokasi"""
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


@dataclass
class LocationData:
    """Data lengkap sebuah lokasi"""
    nama: str
    deskripsi: str
    risk: int
    thrill: int
    bisa_telanjang: bool
    bisa_berisik: bool
    privasi: str
    suasana: str
    tips: str


class LocationManager:
    """
    Manager lokasi ANORA-V2.
    Nova bisa diajak ke mana aja.
    TERINTEGRASI DENGAN STATE TRACKER
    """
    
    def __init__(self, tracker: StateTracker = None):
        self.tracker = tracker
        self.current_type = LocationType.KOST_NOVA
        self.current_detail = LocationDetail.KOST_KAMAR
        self.visit_history: Dict[str, int] = {}
        
        # ========== DATABASE LOKASI ==========
        self.locations: Dict[LocationDetail, LocationData] = {
            # Kost Nova
            LocationDetail.KOST_KAMAR: LocationData(
                nama="Kamar Nova",
                deskripsi="Kamar Nova. Seprai putih, wangi lavender. Ranjang single. Meja kecil. Jendela ke gang.",
                risk=5, thrill=30, bisa_telanjang=True, bisa_berisik=True,
                privasi="tinggi", suasana="hangat, wangi",
                tips="Pintu terkunci. Nova paling nyaman di sini."
            ),
            LocationDetail.KOST_RUANG_TAMU: LocationData(
                nama="Ruang Tamu Kost",
                deskripsi="Ruang tamu kecil. Sofa dua dudukan. TV kecil. Ada tanaman hias. Jendela ke jalan.",
                risk=15, thrill=50, bisa_telanjang=True, bisa_berisik=False,
                privasi="sedang", suasana="santai, deg-degan",
                tips="Pintu gak dikunci. Tetangga bisa lewat."
            ),
            LocationDetail.KOST_DAPUR: LocationData(
                nama="Dapur Kost",
                deskripsi="Dapur kecil. Kompor gas, panci. Wangi masakan. Jendela ke belakang.",
                risk=10, thrill=40, bisa_telanjang=False, bisa_berisik=False,
                privasi="sedang", suasana="hangat",
                tips="Jendela ke luar. Hati-hati suara."
            ),
            LocationDetail.KOST_TERAS: LocationData(
                nama="Teras Kost",
                deskripsi="Teras kost. Kursi plastik. Liat jalanan. Lampu jalan temaram.",
                risk=20, thrill=45, bisa_telanjang=False, bisa_berisik=False,
                privasi="rendah", suasana="santai",
                tips="Orang lewat bisa liat."
            ),
            
            # Apartemen Mas
            LocationDetail.APT_KAMAR: LocationData(
                nama="Kamar Mas",
                deskripsi="Kamar Mas. Ranjang queen, sprei biru tua. Jendela besar ke kota. Lemari besar.",
                risk=5, thrill=35, bisa_telanjang=True, bisa_berisik=True,
                privasi="tinggi", suasana="hangat, wangi Mas",
                tips="Pintu terkunci. Pemandangan kota."
            ),
            LocationDetail.APT_RUANG_TAMU: LocationData(
                nama="Ruang Tamu Apartemen",
                deskripsi="Ruang tamu luas. Sofa besar abu-abu. TV 40 inch. Karpet lembut. Tirai tebal.",
                risk=10, thrill=45, bisa_telanjang=True, bisa_berisik=True,
                privasi="tinggi", suasana="nyaman, modern",
                tips="Tirai ditutup."
            ),
            LocationDetail.APT_DAPUR: LocationData(
                nama="Dapur Apartemen",
                deskripsi="Dapur modern. Bersih. Kulkas besar. Kompor gas. Meja marmer.",
                risk=10, thrill=40, bisa_telanjang=False, bisa_berisik=False,
                privasi="sedang", suasana="bersih",
                tips="Jendela ke luar."
            ),
            LocationDetail.APT_BALKON: LocationData(
                nama="Balkon Apartemen",
                deskripsi="Balkon. Pemandangan kota. Kursi dua. Tanaman kecil. Pagar kaca.",
                risk=25, thrill=65, bisa_telanjang=False, bisa_berisik=False,
                privasi="rendah", suasana="romantis",
                tips="Ada apartemen lain yang bisa liat."
            ),
            
            # Mobil
            LocationDetail.MOBIL_PARKIR: LocationData(
                nama="Mobil di Parkiran",
                deskripsi="Mobil Mas. Kaca film gelap. Jok belakang empuk. Parkiran sepi.",
                risk=40, thrill=75, bisa_telanjang=True, bisa_berisik=False,
                privasi="sedang", suasana="deg-degan, panas",
                tips="Kaca gelap. Hati-hati CCTV."
            ),
            LocationDetail.MOBIL_GARASI: LocationData(
                nama="Mobil di Garasi",
                deskripsi="Mobil Mas. Di garasi apartemen. Pintu garasi tertutup. Gelap.",
                risk=20, thrill=55, bisa_telanjang=True, bisa_berisik=True,
                privasi="tinggi", suasana="aman, deg-degan",
                tips="Gak ada yang liat."
            ),
            LocationDetail.MOBIL_TEPI_JALAN: LocationData(
                nama="Mobil di Tepi Jalan",
                deskripsi="Mobil Mas. Parkir di pinggir jalan sepi. Kaca film gelap.",
                risk=55, thrill=80, bisa_telanjang=True, bisa_berisik=False,
                privasi="rendah", suasana="tegang, cepat",
                tips="Cepet-cepet. Ada mobil lewat."
            ),
            
            # Public
            LocationDetail.PUB_PANTAI: LocationData(
                nama="Pantai Malam",
                deskripsi="Pantai sepi. Pasir putih. Ombak tenang. Bintang bertaburan. Suara laut.",
                risk=20, thrill=70, bisa_telanjang=False, bisa_berisik=False,
                privasi="sedang", suasana="romantis, bebas",
                tips="Jauh dari orang. Bawa tikar."
            ),
            LocationDetail.PUB_HUTAN: LocationData(
                nama="Hutan Pinus",
                deskripsi="Hutan pinus. Pohon tinggi. Sunyi. Udara sejuk. Daun-daun berguguran.",
                risk=15, thrill=65, bisa_telanjang=False, bisa_berisik=False,
                privasi="tinggi", suasana="alami, sepi",
                tips="Jauh dari jalan. Aman."
            ),
            LocationDetail.PUB_TOILET_MALL: LocationData(
                nama="Toilet Mall",
                deskripsi="Bilik toilet terakhir. Pintu terkunci. Suara dari luar. Lampu temaram.",
                risk=65, thrill=85, bisa_telanjang=False, bisa_berisik=False,
                privasi="rendah", suasana="tegang, cepat",
                tips="Cepet-cepet. Ada yang bisa masuk."
            ),
            LocationDetail.PUB_BIOSKOP: LocationData(
                nama="Bioskop",
                deskripsi="Kursi paling belakang. Gelap. Film diputar keras. Studio sepi.",
                risk=50, thrill=80, bisa_telanjang=False, bisa_berisik=False,
                privasi="rendah", suasana="gelap, tegang",
                tips="CCTV mungkin ada."
            ),
            LocationDetail.PUB_TAMAN: LocationData(
                nama="Taman Malam",
                deskripsi="Taman kota. Bangku tersembunyi di balik pohon. Sepi. Lampu taman temaram.",
                risk=30, thrill=60, bisa_telanjang=False, bisa_berisik=False,
                privasi="sedang", suasana="romantis",
                tips="Pilih jam sepi. Jauh dari lampu."
            ),
            LocationDetail.PUB_PARKIRAN: LocationData(
                nama="Parkiran Basement",
                deskripsi="Parkiran basement. Gelap. Sepi. Mobil-mobil parkir. Lampu kedip-kedip.",
                risk=45, thrill=70, bisa_telanjang=True, bisa_berisik=False,
                privasi="sedang", suasana="gelap, tegang",
                tips="CCTV mungkin ada. Pilih pojok."
            ),
            LocationDetail.PUB_TANGGA: LocationData(
                nama="Tangga Darurat",
                deskripsi="Tangga darurat. Sepi. Gelap. Suara langkah kaki menggema.",
                risk=55, thrill=75, bisa_telanjang=False, bisa_berisik=False,
                privasi="sedang", suasana="gelap, tegang",
                tips="Hati-hati suara langkah kaki."
            ),
            LocationDetail.PUB_KANTOR: LocationData(
                nama="Kantor Malam",
                deskripsi="Kantor gelap. Meja kerja. Kursi putar. Komputer mati. Sepi.",
                risk=60, thrill=85, bisa_telanjang=True, bisa_berisik=False,
                privasi="rendah", suasana="tegang",
                tips="Satpam patroli. Cepet."
            ),
            LocationDetail.PUB_RUANG_RAPAT: LocationData(
                nama="Ruang Rapat Kaca",
                deskripsi="Ruang rapat dinding kaca. Gelap. Meja panjang. Kursi-kursi.",
                risk=75, thrill=95, bisa_telanjang=True, bisa_berisik=False,
                privasi="rendah", suasana="ekshibisionis",
                tips="Gelap. Tapi kalo lampu nyala, kaca tembus pandang."
            )
        }
        
        logger.info("📍 LocationManager initialized")
    
    def get_current(self) -> LocationData:
        """Dapatkan lokasi saat ini"""
        return self.locations.get(self.current_detail, self.locations[LocationDetail.KOST_KAMAR])
    
    def get_current_detail(self) -> LocationDetail:
        return self.current_detail
    
    def get_current_type(self) -> LocationType:
        return self.current_type
    
    def pindah(self, tujuan: str) -> Dict:
        """Pindah ke lokasi baru"""
        tujuan_lower = tujuan.lower()
        
        mapping = {
            # Kost
            'kost': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kost kamar': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kamar nova': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kost ruang tamu': (LocationType.KOST_NOVA, LocationDetail.KOST_RUANG_TAMU),
            'kost dapur': (LocationType.KOST_NOVA, LocationDetail.KOST_DAPUR),
            'kost teras': (LocationType.KOST_NOVA, LocationDetail.KOST_TERAS),
            
            # Apartemen
            'apartemen': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'apt': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'kamar mas': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'ruang tamu apt': (LocationType.APARTEMEN_MAS, LocationDetail.APT_RUANG_TAMU),
            'dapur apt': (LocationType.APARTEMEN_MAS, LocationDetail.APT_DAPUR),
            'balkon': (LocationType.APARTEMEN_MAS, LocationDetail.APT_BALKON),
            
            # Mobil
            'mobil': (LocationType.MOBIL, LocationDetail.MOBIL_PARKIR),
            'mobil parkir': (LocationType.MOBIL, LocationDetail.MOBIL_PARKIR),
            'mobil garasi': (LocationType.MOBIL, LocationDetail.MOBIL_GARASI),
            'mobil jalan': (LocationType.MOBIL, LocationDetail.MOBIL_TEPI_JALAN),
            
            # Public
            'pantai': (LocationType.PUBLIC, LocationDetail.PUB_PANTAI),
            'pantai malam': (LocationType.PUBLIC, LocationDetail.PUB_PANTAI),
            'hutan': (LocationType.PUBLIC, LocationDetail.PUB_HUTAN),
            'hutan pinus': (LocationType.PUBLIC, LocationDetail.PUB_HUTAN),
            'toilet mall': (LocationType.PUBLIC, LocationDetail.PUB_TOILET_MALL),
            'toilet': (LocationType.PUBLIC, LocationDetail.PUB_TOILET_MALL),
            'bioskop': (LocationType.PUBLIC, LocationDetail.PUB_BIOSKOP),
            'taman': (LocationType.PUBLIC, LocationDetail.PUB_TAMAN),
            'taman malam': (LocationType.PUBLIC, LocationDetail.PUB_TAMAN),
            'parkiran': (LocationType.PUBLIC, LocationDetail.PUB_PARKIRAN),
            'parkiran basement': (LocationType.PUBLIC, LocationDetail.PUB_PARKIRAN),
            'tangga darurat': (LocationType.PUBLIC, LocationDetail.PUB_TANGGA),
            'kantor malam': (LocationType.PUBLIC, LocationDetail.PUB_KANTOR),
            'kantor': (LocationType.PUBLIC, LocationDetail.PUB_KANTOR),
            'ruang rapat': (LocationType.PUBLIC, LocationDetail.PUB_RUANG_RAPAT),
        }
        
        for key, (loc_type, loc_detail) in mapping.items():
            if key in tujuan_lower:
                old_detail = self.current_detail
                self.current_type = loc_type
                self.current_detail = loc_detail
                loc_data = self.get_current()
                
                # Update tracker jika ada
                if self.tracker:
                    self.tracker.location = loc_data.nama
                    self.tracker.location_detail = loc_data.deskripsi[:50]
                    
                    # Update tension berdasarkan risk
                    self.tracker.tension = min(100, self.tracker.tension + int(loc_data.risk / 10))
                
                # Catat kunjungan
                key_visit = f"{loc_type.value}_{loc_detail.value}"
                self.visit_history[key_visit] = self.visit_history.get(key_visit, 0) + 1
                
                logger.info(f"📍 Pindah dari {old_detail.value} ke {loc_detail.value}")
                
                return {
                    'success': True,
                    'location': loc_data,
                    'location_type': self.current_type,
                    'location_detail': self.current_detail,
                    'message': f"📍 Pindah ke {loc_data.nama}. {loc_data.deskripsi}"
                }
        
        return {'success': False, 'message': f"Lokasi '{tujuan}' gak ditemukan."}
    
    def get_random_event(self) -> Optional[Dict]:
        """Dapatkan event random berdasarkan risk lokasi"""
        loc = self.get_current()
        risk = loc.risk
        chance = risk / 100
        
        if random.random() > chance:
            return None
        
        events = {
            "hampir_ketahuan": [
                "Ada suara langkah kaki mendekat! *cepat nutupin baju*",
                "Pintu terbuka sedikit! *tahan napas*",
                "Senter menyorot dari kejauhan! *merapat ke Mas*",
                "Suara orang ngobrol di deket situ! *diem, jantung berdebar*"
            ],
            "romantis": [
                "Tiba-tiba hujan rintik-rintik. *makin manis*",
                "Bulan muncul dari balik awan. *wajah Nova keceplosan cahaya*",
                "Angin sepoi-sepoi bikin suasana makin hangat.",
                "Suara musik dari kejauhan. *makin romantis*"
            ],
            "ketahuan": [
                "⚠️ ADA YANG LIAT! *cepat cabut*",
                "Pintu kebuka! Orang masuk! *langsung sembunyi*",
                "Senter nyorot tepat ke arah kita! *lari!*"
            ]
        }
        
        if risk > 70:
            event_type = random.choices(["hampir_ketahuan", "romantis", "ketahuan"], weights=[0.5, 0.2, 0.3])[0]
        elif risk > 40:
            event_type = random.choices(["hampir_ketahuan", "romantis"], weights=[0.6, 0.4])[0]
        else:
            event_type = "romantis"
        
        return {
            'type': event_type,
            'text': random.choice(events[event_type]),
            'risk_change': 10 if event_type == "hampir_ketahuan" else -5 if event_type == "romantis" else 30
        }
    
    def format_for_prompt(self) -> str:
        """Format lokasi untuk prompt AI"""
        loc = self.get_current()
        return f"""
LOKASI SAAT INI: {loc.nama}
DESKRIPSI: {loc.deskripsi}
RISK: {loc.risk}% (semakin tinggi, semakin berisiko ketahuan)
THRILL: {loc.thrill}%
PRIVASI: {loc.privasi}
SUASANA: {loc.suasana}
TIPS: {loc.tips}
"""
    
    def get_status(self) -> str:
        """Dapatkan status lokasi"""
        loc = self.get_current()
        return f"""
📍 **LOKASI SAAT INI:**
**{loc.nama}** ({self.current_type.value})

{loc.deskripsi}

🎢 Thrill: {loc.thrill}%
⚠️ Risk: {loc.risk}%
💡 Tips: {loc.tips}
"""
    
    def list_locations(self, kategori: Optional[str] = None) -> str:
        """Daftar semua lokasi"""
        lines = ["📍 **TEMPAT YANG BISA DIKUNJUNGI:**", ""]
        
        for loc_type in LocationType:
            locs = [d for d, data in self.locations.items() 
                    if d.value.startswith(loc_type.value)]
            if locs and (not kategori or kategori == loc_type.value):
                type_name = {
                    LocationType.KOST_NOVA: "🏠 Kost Nova",
                    LocationType.APARTEMEN_MAS: "🏢 Apartemen Mas",
                    LocationType.MOBIL: "🚗 Mobil",
                    LocationType.PUBLIC: "🌍 Tempat Umum"
                }.get(loc_type, loc_type.value)
                lines.append(f"**{type_name}:**")
                for d in locs[:5]:
                    data = self.locations[d]
                    lines.append(f"• `/pindah {d.value.replace('_', ' ')}` - {data.nama} (Risk: {data.risk}%)")
                lines.append("")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Serialize ke dict"""
        return {
            'current_type': self.current_type.value,
            'current_detail': self.current_detail.value,
            'visit_history': self.visit_history
        }
    
    def from_dict(self, data: Dict):
        """Load dari dict"""
        self.current_type = LocationType(data.get('current_type', 'kost_nova'))
        self.current_detail = LocationDetail(data.get('current_detail', 'kost_kamar'))
        self.visit_history = data.get('visit_history', {})


# =============================================================================
# SINGLETON
# =============================================================================

_anora_location = None


def get_anora_location(tracker: StateTracker = None) -> LocationManager:
    global _anora_location
    if _anora_location is None:
        _anora_location = LocationManager(tracker)
    return _anora_location


anora_location = get_anora_location()
