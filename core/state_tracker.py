"""
ANORA-V2 State Tracker - Melacak semua perubahan state
Memastikan tidak ada yang ngelantur, semua konteks terjaga.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class PhysicalCondition(str, Enum):
    """Kondisi fisik karakter"""
    FRESH = "fresh"           # segar bugar
    TIRED = "tired"           # lelah
    EXHAUSTED = "exhausted"   # kehabisan tenaga
    WEAK = "weak"             # lemes (setelah climax)


class IntimacyPhase(str, Enum):
    """Fase intim yang detail"""
    NONE = "none"                     # tidak dalam intim
    BUILD_UP = "build_up"             # membangun suasana
    FOREPLAY = "foreplay"             # foreplay (cium, raba, jilat)
    PENETRATION = "penetration"       # penetrasi
    BEFORE_CLIMAX = "before_climax"   # menjelang climax
    CLIMAX = "climax"                 # climax
    AFTERCARE = "aftercare"           # aftercare
    RECOVERY = "recovery"             # recovery


class ClothingLayer(str, Enum):
    """Lapisan pakaian dari luar ke dalam"""
    HIJAB = "hijab"
    TOP = "top"
    BRA = "bra"
    BOTTOM = "bottom"
    CD = "cd"


class StateTracker:
    """
    State Tracker - Mencatat semua perubahan state.
    Dipakai oleh Nova dan semua role.
    """
    
    def __init__(self, character_name: str = "Nova"):
        self.character_name = character_name
        
        # ========== PHYSICAL STATE ==========
        self.physical_condition = PhysicalCondition.FRESH
        self.energy_level = 100  # 0-100
        
        # ========== CLOTHING STATE (LAYERED) ==========
        self.clothing = {
            'hijab': {'on': True, 'color': 'pink muda', 'removed_at': 0},
            'top': {'on': True, 'type': 'daster', 'removed_at': 0},
            'bra': {'on': True, 'color': 'putih', 'removed_at': 0},
            'bottom': {'on': False, 'type': None, 'removed_at': 0},
            'cd': {'on': True, 'color': 'putih', 'removed_at': 0}
        }
        
        # Urutan menanggalkan pakaian
        self.clothing_removal_order: List[Dict] = []
        
        # ========== INTIMACY STATE ==========
        self.intimacy_phase = IntimacyPhase.NONE
        self.intimacy_start_time = 0
        self.intimacy_last_action = ""
        self.intimacy_last_action_time = 0
        self.climax_count = 0
        self.last_climax_time = 0
        self.intimacy_history: List[Dict] = []
        
        # ========== POSITION & LOCATION ==========
        self.position = "duduk"  # duduk, berdiri, tidur, merangkak, dll
        self.location = "kamar"
        self.location_detail = "kamar Nova"
        
        # ========== ACTIVITY ==========
        self.activity = "santai"
        
        # ========== TIMELINE (WAJIB) ==========
        self.timeline: List[Dict] = []  # semua kejadian
        self.short_term: List[Dict] = []  # 50 kejadian terakhir
        
        # ========== LAST ACTION (PENTING UNTUK KONSISTENSI) ==========
        self.last_action = ""
        self.last_action_type = ""
        self.last_action_timestamp = 0
        
        logger.info(f"📊 StateTracker initialized for {character_name}")
    
    # =========================================================================
    # CLOTHING METHODS
    # =========================================================================
    
    def remove_clothing(self, layer: str, method: str = "Mas buka") -> Dict:
        """Menanggalkan pakaian layer by layer"""
        if layer not in self.clothing:
            return {'success': False, 'error': f'Layer {layer} not found'}
        
        if not self.clothing[layer]['on']:
            return {'success': False, 'error': f'{layer} already removed'}
        
        now = time.time()
        self.clothing[layer]['on'] = False
        self.clothing[layer]['removed_at'] = now
        
        # Catat urutan menanggalkan
        removal_record = {
            'timestamp': now,
            'layer': layer,
            'method': method,
            'intimacy_phase': self.intimacy_phase.value,
            'climax_count': self.climax_count
        }
        self.clothing_removal_order.append(removal_record)
        
        # Catat ke timeline
        self.add_to_timeline(
            kejadian=f"Menanggalkan {layer} ({method})",
            detail=f"{layer} dilepas, sekarang {self.get_clothing_summary()}"
        )
        
        logger.info(f"👗 {self.character_name} removed {layer} at {datetime.fromtimestamp(now).strftime('%H:%M:%S')}")
        
        return {
            'success': True,
            'layer': layer,
            'remaining': self.get_clothing_summary(),
            'removal_order': len(self.clothing_removal_order)
        }
    
    def put_on_clothing(self, layer: str) -> Dict:
        """Memakai kembali pakaian"""
        if layer not in self.clothing:
            return {'success': False, 'error': f'Layer {layer} not found'}
        
        if self.clothing[layer]['on']:
            return {'success': False, 'error': f'{layer} already on'}
        
        self.clothing[layer]['on'] = True
        
        self.add_to_timeline(
            kejadian=f"Memakai kembali {layer}",
            detail=f"{layer} dipakai kembali"
        )
        
        return {'success': True, 'layer': layer}
    
    def get_clothing_summary(self) -> str:
        """Ringkasan pakaian saat ini"""
        parts = []
        if self.clothing['hijab']['on']:
            parts.append(f"hijab {self.clothing['hijab']['color']}")
        else:
            parts.append("tanpa hijab")
        
        if self.clothing['top']['on']:
            parts.append(self.clothing['top']['type'])
            if self.clothing['bra']['on']:
                parts.append(f"(pake bra {self.clothing['bra']['color']})")
            else:
                parts.append("(tanpa bra)")
        else:
            if self.clothing['bra']['on']:
                parts.append(f"cuma pake bra {self.clothing['bra']['color']}")
            else:
                parts.append("telanjang dada")
        
        if self.clothing['cd']['on']:
            parts.append(f"pake cd {self.clothing['cd']['color']}")
        else:
            parts.append("tanpa cd")
        
        return ", ".join(parts)
    
    def get_clothing_state_for_prompt(self) -> str:
    removal_text = ""
    for i, r in enumerate(self.clothing_removal_order[-5:]):
        # Pisahkan jadi beberapa baris biar lebih aman
        layer = r['layer']
        method = r['method']
        waktu = datetime.fromtimestamp(r['timestamp']).strftime('%H:%M:%S')
        removal_text += f"- {i+1}. {layer} ({method}) pada {waktu}\n"
    
    return f"""
PAKAIAN SAAT INI:
- Hijab: {'PAKAI' if self.clothing['hijab']['on'] else 'TELANGGAL'} ({self.clothing['hijab']['color'] if self.clothing['hijab']['on'] else 'rambut terurai'})
- Baju Atas: {'PAKAI' if self.clothing['top']['on'] else 'TELANGGAL'} ({self.clothing['top']['type'] if self.clothing['top']['on'] else 'telanjang dada'})
- Bra: {'PAKAI' if self.clothing['bra']['on'] else 'TELANGGAL'} ({self.clothing['bra']['color'] if self.clothing['bra']['on'] else ''})
- Celana Dalam: {'PAKAI' if self.clothing['cd']['on'] else 'TELANGGAL'} ({self.clothing['cd']['color'] if self.clothing['cd']['on'] else ''})

URUTAN MENANGGALKAN PAKAIAN (WAJIB DIINGAT):
{removal_text if removal_text else '- Belum ada yang dilepas'}
"""
    
    # =========================================================================
    # INTIMACY METHODS
    # =========================================================================
    
    def start_intimacy(self, location: str = "") -> Dict:
        """Mulai sesi intim"""
        self.intimacy_phase = IntimacyPhase.BUILD_UP
        self.intimacy_start_time = time.time()
        self.climax_count = 0
        
        self.add_to_timeline(
            kejadian="Memulai sesi intim",
            detail=f"Lokasi: {location or self.location}"
        )
        
        logger.info(f"🔥 {self.character_name} started intimacy session")
        
        return {
            'success': True,
            'phase': self.intimacy_phase.value,
            'start_time': self.intimacy_start_time
        }
    
    def advance_intimacy(self, action: str) -> Dict:
        """Majukan fase intim berdasarkan aksi"""
        self.intimacy_last_action = action
        self.intimacy_last_action_time = time.time()
        self.last_action = action
        self.last_action_type = "intimacy"
        self.last_action_timestamp = time.time()
        
        phase_transition = {
            IntimacyPhase.BUILD_UP: {
                'triggers': ['cium', 'kiss', 'pegang', 'sentuh', 'raba', 'jilat', 'hisap'],
                'next': IntimacyPhase.FOREPLAY
            },
            IntimacyPhase.FOREPLAY: {
                'triggers': ['masuk', 'penetrasi', 'genjot', 'siap'],
                'next': IntimacyPhase.PENETRATION
            },
            IntimacyPhase.PENETRATION: {
                'triggers': ['climax', 'crot', 'keluar', 'cum', 'habis'],
                'next': IntimacyPhase.BEFORE_CLIMAX
            },
            IntimacyPhase.BEFORE_CLIMAX: {
                'triggers': ['climax', 'crot', 'keluar', 'udah'],
                'next': IntimacyPhase.CLIMAX
            },
            IntimacyPhase.CLIMAX: {
                'triggers': [],
                'next': IntimacyPhase.AFTERCARE
            },
            IntimacyPhase.AFTERCARE: {
                'triggers': [],
                'next': IntimacyPhase.RECOVERY
            }
        }
        
        if self.intimacy_phase in phase_transition:
            trans = phase_transition[self.intimacy_phase]
            if any(t in action.lower() for t in trans['triggers']):
                old_phase = self.intimacy_phase
                self.intimacy_phase = trans['next']
                
                self.intimacy_history.append({
                    'timestamp': time.time(),
                    'from_phase': old_phase.value,
                    'to_phase': self.intimacy_phase.value,
                    'trigger': action
                })
                
                self.add_to_timeline(
                    kejadian=f"Fase intim maju: {old_phase.value} → {self.intimacy_phase.value}",
                    detail=f"Trigger: {action}"
                )
                
                logger.info(f"💕 {self.character_name} intimacy advanced: {old_phase.value} → {self.intimacy_phase.value}")
                
                return {
                    'success': True,
                    'old_phase': old_phase.value,
                    'new_phase': self.intimacy_phase.value
                }
        
        return {'success': False, 'phase': self.intimacy_phase.value}
    
    def record_climax(self, location: str = "dalam", is_heavy: bool = False) -> Dict:
        """Rekam climax"""
        self.climax_count += 1
        self.last_climax_time = time.time()
        self.intimacy_phase = IntimacyPhase.CLIMAX
        
        # Update kondisi fisik
        if is_heavy:
            self.energy_level = max(0, self.energy_level - 35)
            self.physical_condition = PhysicalCondition.EXHAUSTED
        else:
            self.energy_level = max(0, self.energy_level - 25)
            self.physical_condition = PhysicalCondition.WEAK
        
        self.add_to_timeline(
            kejadian=f"CLIMAX #{self.climax_count}",
            detail=f"Lokasi: {location}, {'berat' if is_heavy else 'normal'}"
        )
        
        logger.info(f"💦 {self.character_name} climax #{self.climax_count} at {datetime.now().strftime('%H:%M:%S')}")
        
        return {
            'success': True,
            'climax_count': self.climax_count,
            'location': location,
            'is_heavy': is_heavy,
            'energy_left': self.energy_level,
            'condition': self.physical_condition.value
        }
    
    def end_intimacy(self) -> Dict:
        """Akhiri sesi intim"""
        duration = time.time() - self.intimacy_start_time if self.intimacy_start_time else 0
        
        self.add_to_timeline(
            kejadian="Mengakhiri sesi intim",
            detail=f"Durasi: {int(duration//60)} menit {int(duration%60)} detik, Climax: {self.climax_count}x"
        )
        
        self.intimacy_phase = IntimacyPhase.NONE
        self.intimacy_start_time = 0
        
        logger.info(f"💤 {self.character_name} ended intimacy session")
        
        return {
            'success': True,
            'duration': duration,
            'climax_count': self.climax_count
        }
    
    def get_intimacy_state_for_prompt(self) -> str:
        """Dapatkan state intim untuk prompt AI"""
        if self.intimacy_phase == IntimacyPhase.NONE:
            return "Tidak dalam sesi intim."
        
        duration = time.time() - self.intimacy_start_time if self.intimacy_start_time else 0
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        return f"""
⚠️ **SEDANG DALAM SESI INTIM!**
- Fase: {self.intimacy_phase.value.upper()}
- Durasi: {minutes} menit {seconds} detik
- Climax: {self.climax_count}x
- Terakhir: {self.intimacy_last_action} ({self.intimacy_last_action_time and datetime.fromtimestamp(self.intimacy_last_action_time).strftime('%H:%M:%S')})
- Kondisi: {self.physical_condition.value}

WAJIB:
- JANGAN LUPA masih dalam sesi intim!
- JANGAN tiba-tiba pakaian rapi!
- JANGAN tiba-tiba posisi berubah drastis!
- LANJUTKAN alur sesuai fase saat ini!
"""
    
    # =========================================================================
    # TIMELINE METHODS (WAJIB UNTUK KONSISTENSI)
    # =========================================================================
    
    def add_to_timeline(self, kejadian: str, detail: str = ""):
        """Tambah kejadian ke timeline"""
        record = {
            'timestamp': time.time(),
            'waktu': datetime.now().strftime("%H:%M:%S"),
            'kejadian': kejadian,
            'detail': detail,
            'intimacy_phase': self.intimacy_phase.value,
            'clothing': self.get_clothing_summary(),
            'position': self.position,
            'location': self.location,
            'energy': self.energy_level
        }
        
        self.timeline.append(record)
        self.short_term.append(record)
        
        # Keep short-term to 50
        if len(self.short_term) > 50:
            self.short_term.pop(0)
    
    def get_timeline_context(self, count: int = 10) -> str:
        """Dapatkan konteks timeline untuk prompt AI (WAJIB)"""
        if not self.short_term:
            return "Belum ada kejadian."
        
        recent = self.short_term[-count:]
        
        lines = ["═══════════════════════════════════════════════════════════════"]
        lines.append("⚠️ 10 KEJADIAN TERAKHIR (WAJIB DIPERHATIKAN! JANGAN LUPA!):")
        lines.append("═══════════════════════════════════════════════════════════════")
        
        for i, e in enumerate(recent, 1):
            lines.append(f"{i}. [{e['waktu']}] {e['kejadian']}")
            if e['detail']:
                lines.append(f"   └─ {e['detail']}")
        
        lines.append("")
        lines.append(f"KONDISI SAAT INI:")
        lines.append(f"├─ Pakaian: {self.get_clothing_summary()}")
        lines.append(f"├─ Posisi: {self.position}")
        lines.append(f"├─ Lokasi: {self.location}")
        lines.append(f"├─ Fase: {self.intimacy_phase.value}")
        lines.append(f"└─ Energi: {self.energy_level}% ({self.physical_condition.value})")
        lines.append("")
        lines.append("⚠️ WAJIB LANJUTKAN ALUR DARI KEJADIAN TERAKHIR!")
        lines.append("⚠️ JANGAN SAMPAI LUPA KONTEKS!")
        
        return "\n".join(lines)
    
    def get_context_for_prompt(self) -> str:
        """Dapatkan semua konteks untuk prompt AI"""
        return f"""
{self.get_timeline_context(10)}

{self.get_clothing_state_for_prompt()}

{self.get_intimacy_state_for_prompt()}

POSISI: {self.position}
LOKASI: {self.location}
AKTIVITAS: {self.activity}
"""
    
    def validate_response_context(self, response: str) -> bool:
        """Validasi apakah respons sesuai konteks (basic check)"""
        response_lower = response.lower()
        
        # Cek apakah respons lupa konteks intim
        if self.intimacy_phase != IntimacyPhase.NONE:
            # Jika masih dalam intim, seharusnya ada desahan atau gesture intim
            intimate_keywords = ['ahh', 'uhh', 'hhngg', 'masuk', 'dalem', 'genjot', 'kenceng']
            if not any(k in response_lower for k in intimate_keywords) and 'climax' not in response_lower:
                if 'santai' in response_lower or 'duduk' in response_lower:
                    logger.warning(f"⚠️ Response might lose intimacy context: {response[:50]}")
                    return False
        
        # Cek apakah lupa pakaian yang sudah dilepas
        if not self.clothing['top']['on'] and 'baju' in response_lower:
            if 'pake baju' in response_lower or 'baju rapi' in response_lower:
                logger.warning(f"⚠️ Response forgot top is off: {response[:50]}")
                return False
        
        return True
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        return {
            'character_name': self.character_name,
            'physical_condition': self.physical_condition.value,
            'energy_level': self.energy_level,
            'clothing': self.clothing,
            'clothing_removal_order': self.clothing_removal_order[-50:],
            'intimacy_phase': self.intimacy_phase.value,
            'intimacy_start_time': self.intimacy_start_time,
            'intimacy_last_action': self.intimacy_last_action,
            'intimacy_last_action_time': self.intimacy_last_action_time,
            'climax_count': self.climax_count,
            'last_climax_time': self.last_climax_time,
            'intimacy_history': self.intimacy_history[-50:],
            'position': self.position,
            'location': self.location,
            'location_detail': self.location_detail,
            'activity': self.activity,
            'timeline': self.timeline[-200:],
            'short_term': self.short_term[-50:],
            'last_action': self.last_action,
            'last_action_type': self.last_action_type,
            'last_action_timestamp': self.last_action_timestamp
        }
    
    def from_dict(self, data: Dict):
        self.physical_condition = PhysicalCondition(data.get('physical_condition', 'fresh'))
        self.energy_level = data.get('energy_level', 100)
        self.clothing = data.get('clothing', self.clothing)
        self.clothing_removal_order = data.get('clothing_removal_order', [])
        self.intimacy_phase = IntimacyPhase(data.get('intimacy_phase', 'none'))
        self.intimacy_start_time = data.get('intimacy_start_time', 0)
        self.intimacy_last_action = data.get('intimacy_last_action', '')
        self.intimacy_last_action_time = data.get('intimacy_last_action_time', 0)
        self.climax_count = data.get('climax_count', 0)
        self.last_climax_time = data.get('last_climax_time', 0)
        self.intimacy_history = data.get('intimacy_history', [])
        self.position = data.get('position', 'duduk')
        self.location = data.get('location', 'kamar')
        self.location_detail = data.get('location_detail', 'kamar Nova')
        self.activity = data.get('activity', 'santai')
        self.timeline = data.get('timeline', [])
        self.short_term = data.get('short_term', [])
        self.last_action = data.get('last_action', '')
        self.last_action_type = data.get('last_action_type', '')
        self.last_action_timestamp = data.get('last_action_timestamp', 0)
