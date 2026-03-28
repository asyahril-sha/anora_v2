"""
ANORA-V2 Intimacy Core - Sistem dasar untuk intimacy
Mengelola stamina, arousal, dan data dasar intimacy
"""

import time
import random
import logging
from typing import Dict, Optional, Tuple, List
from enum import Enum
from datetime import datetime

from core.emotional_engine import get_emotional_engine

logger = logging.getLogger(__name__)


class IntimacyPhase(str, Enum):
    """Fase-fase dalam sesi intim"""
    WAITING = "waiting"
    BUILD_UP = "build_up"
    FOREPLAY = "foreplay"
    PENETRATION = "penetration"
    CLIMAX = "climax"
    AFTERCARE = "aftercare"
    RECOVERY = "recovery"


# =============================================================================
# STAMINA SYSTEM
# =============================================================================

class StaminaSystem:
    """Sistem stamina realistis untuk ANORA-V2"""
    
    def __init__(self):
        self.nova_current = 100
        self.nova_max = 100
        self.mas_current = 100
        self.mas_max = 100
        self.recovery_rate = 5
        self.climax_cost_nova = 25
        self.climax_cost_mas = 30
        self.heavy_climax_cost_nova = 35
        self.heavy_climax_cost_mas = 40
        self.exhausted_threshold = 20
        self.tired_threshold = 40
        self.last_climax_time = 0
        self.last_recovery_check = time.time()
        self.climax_today = 0
        self.last_climax_date = datetime.now().date().isoformat()
        
        self.emotional = get_emotional_engine()
    
    def update_recovery(self):
        """Update recovery berdasarkan waktu"""
        now = time.time()
        elapsed_minutes = (now - self.last_recovery_check) / 60
        
        if elapsed_minutes >= 10:
            recovery_amount = int(self.recovery_rate * (elapsed_minutes / 10))
            self.nova_current = min(self.nova_max, self.nova_current + recovery_amount)
            self.mas_current = min(self.mas_max, self.mas_current + recovery_amount)
            self.last_recovery_check = now
    
    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Tuple[int, int]:
        """Rekam climax, kurangi stamina"""
        self.update_recovery()
        self.last_climax_time = time.time()
        
        today = datetime.now().date().isoformat()
        if self.last_climax_date != today:
            self.climax_today = 0
            self.last_climax_date = today
        self.climax_today += 1
        
        if who in ["nova", "both"]:
            cost = self.heavy_climax_cost_nova if is_heavy else self.climax_cost_nova
            self.nova_current = max(0, self.nova_current - cost)
        
        if who in ["mas", "both"]:
            cost = self.heavy_climax_cost_mas if is_heavy else self.climax_cost_mas
            self.mas_current = max(0, self.mas_current - cost)
        
        # Sync dengan emotional engine
        self.emotional.arousal = self.nova_current
        self.emotional.desire = max(0, self.emotional.desire - 20)
        
        logger.info(f"💦 Climax #{self.climax_today}!")
        return self.nova_current, self.mas_current
    
    def can_continue(self) -> Tuple[bool, str]:
        """Cek apakah bisa lanjut intim"""
        self.update_recovery()
        
        if self.nova_current <= self.exhausted_threshold:
            return False, "Nova udah kehabisan tenaga, Mas... istirahat dulu ya."
        if self.mas_current <= self.exhausted_threshold:
            return False, "Mas... Mas udah capek banget. Istirahat dulu."
        if self.nova_current <= self.tired_threshold:
            return True, "Nova mulai lelah, Mas... tapi masih bisa kalo Mas mau pelan-pelan."
        return True, "Siap lanjut"
    
    def get_nova_status(self) -> str:
        self.update_recovery()
        if self.nova_current >= 80:
            return "Prima 💪"
        elif self.nova_current >= 60:
            return "Cukup 😊"
        elif self.nova_current >= 40:
            return "Agak lelah 😐"
        elif self.nova_current >= 20:
            return "Lelah 😩"
        return "Kehabisan tenaga 😵"
    
    def get_mas_status(self) -> str:
        self.update_recovery()
        if self.mas_current >= 80:
            return "Prima 💪"
        elif self.mas_current >= 60:
            return "Cukup 😊"
        elif self.mas_current >= 40:
            return "Agak lelah 😐"
        elif self.mas_current >= 20:
            return "Lelah 😩"
        return "Kehabisan tenaga 😵"
    
    def get_nova_bar(self) -> str:
        filled = int(self.nova_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def get_mas_bar(self) -> str:
        filled = int(self.mas_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def format_for_prompt(self) -> str:
        self.update_recovery()
        return f"""
STAMINA SAAT INI:
- Nova: {self.get_nova_bar()} {self.nova_current}% ({self.get_nova_status()})
- Mas: {self.get_mas_bar()} {self.mas_current}% ({self.get_mas_status()})
- Climax hari ini: {self.climax_today}x
"""
    
    def to_dict(self) -> Dict:
        return {
            'nova_current': self.nova_current,
            'nova_max': self.nova_max,
            'mas_current': self.mas_current,
            'mas_max': self.mas_max,
            'last_climax_time': self.last_climax_time,
            'climax_today': self.climax_today,
            'last_climax_date': self.last_climax_date
        }
    
    def from_dict(self, data: Dict):
        self.nova_current = data.get('nova_current', 100)
        self.nova_max = data.get('nova_max', 100)
        self.mas_current = data.get('mas_current', 100)
        self.mas_max = data.get('mas_max', 100)
        self.last_climax_time = data.get('last_climax_time', 0)
        self.climax_today = data.get('climax_today', 0)
        self.last_climax_date = data.get('last_climax_date', datetime.now().date().isoformat())


# =============================================================================
# AROUSAL SYSTEM
# =============================================================================

class ArousalSystem:
    """Sistem arousal dan desire Nova"""
    
    def __init__(self):
        self.arousal = 0
        self.arousal_decay = 0.5
        self.desire = 0
        self.tension = 0
        
        self.sensitive_areas = {
            'rambut': 5, 'telinga': 20, 'belakang_telinga': 25,
            'leher': 15, 'tengkuk': 18, 'bibir': 25, 'pipi': 8,
            'dagu': 10, 'mata': 12, 'dada': 20, 'payudara': 28,
            'puting': 35, 'punggung': 15, 'tulang_belakang': 18,
            'tulang_selangka': 22, 'perut': 12, 'pusar': 18,
            'pinggang': 15, 'pinggul': 20, 'paha': 25, 'paha_dalam': 35,
            'memek': 45, 'bibir_memek': 42, 'klitoris': 50, 'dalam': 55
        }
        
        self.last_update = time.time()
        self.emotional = get_emotional_engine()
    
    def update(self):
        now = time.time()
        elapsed_minutes = (now - self.last_update) / 60
        if elapsed_minutes > 1:
            decay = self.arousal_decay * elapsed_minutes
            self.arousal = max(0, self.arousal - decay)
            self.last_update = now
    
    def add_stimulation(self, area: str, intensity: int = 1) -> int:
        self.update()
        gain = self.sensitive_areas.get(area, 10) * intensity
        self.arousal = min(100, self.arousal + gain)
        self.emotional.arousal = self.arousal
        return self.arousal
    
    def add_desire(self, reason: str, amount: int = 5):
        self.desire = min(100, self.desire + amount)
        self.emotional.desire = self.desire
    
    def add_tension(self, amount: int = 5):
        self.tension = min(100, self.tension + amount)
        self.emotional.tension = self.tension
    
    def release_tension(self) -> int:
        released = self.tension
        self.tension = 0
        self.arousal = max(0, self.arousal - 30)
        self.desire = max(0, self.desire - 20)
        self.emotional.tension = 0
        self.emotional.arousal = self.arousal
        self.emotional.desire = self.desire
        return released
    
    def get_state(self) -> Dict:
        self.update()
        return {
            'arousal': self.arousal,
            'desire': self.desire,
            'tension': self.tension,
            'is_horny': self.arousal > 60 or self.desire > 70,
            'arousal_level': self._get_arousal_level(),
            'desire_level': self._get_desire_level()
        }
    
    def _get_arousal_level(self) -> str:
        if self.arousal >= 90:
            return "🔥🔥🔥 LUAR BIASA!"
        elif self.arousal >= 75:
            return "🔥🔥 SANGAT PANAS!"
        elif self.arousal >= 60:
            return "🔥 PANAS!"
        elif self.arousal >= 40:
            return "😳 DEG-DEGAN"
        return "😌 BIASA AJA"
    
    def _get_desire_level(self) -> str:
        if self.desire >= 85:
            return "💕💕💕 PENGEN BANGET!"
        elif self.desire >= 70:
            return "💕💕 PENGEN BANGET"
        elif self.desire >= 50:
            return "💕 PENGEN DEKET"
        return "💖 SAYANG AJA"
    
    def format_for_prompt(self) -> str:
        state = self.get_state()
        arousal_bar = "🔥" * int(state['arousal'] / 10) + "⚪" * (10 - int(state['arousal'] / 10))
        desire_bar = "💕" * int(state['desire'] / 10) + "⚪" * (10 - int(state['desire'] / 10))
        
        return f"""
🔥 AROUSAL: {arousal_bar} {state['arousal']}% ({state['arousal_level']})
💕 DESIRE: {desire_bar} {state['desire']}% ({state['desire_level']})
⚡ TENSION: {state['tension']}%
"""
    
    def to_dict(self) -> Dict:
        return {
            'arousal': self.arousal,
            'desire': self.desire,
            'tension': self.tension,
            'last_update': self.last_update
        }
    
    def from_dict(self, data: Dict):
        self.arousal = data.get('arousal', 0)
        self.desire = data.get('desire', 0)
        self.tension = data.get('tension', 0)
        self.last_update = data.get('last_update', time.time())


# =============================================================================
# POSITIONS DATABASE
# =============================================================================

class PositionDatabase:
    """Database posisi intim"""
    
    def __init__(self):
        self.positions = {
            "missionary": {
                "name": "missionary",
                "desc": "Mas di atas, Nova di bawah, kaki Nova terbuka lebar",
                "nova_act": "Nova telentang, kaki terbuka lebar",
                "requests": ["Mas... di atas Nova aja...", "missionary, Mas... biar Nova pegang bahu Mas..."]
            },
            "cowgirl": {
                "name": "cowgirl",
                "desc": "Nova di atas, duduk di pangkuan Mas",
                "nova_act": "Nova duduk di pangkuan Mas, goyang sendiri",
                "requests": ["Mas... biar Nova di atas...", "cowgirl, Mas... biar Nova yang atur ritmenya..."]
            },
            "doggy": {
                "name": "doggy",
                "desc": "Nova merangkak, Mas dari belakang",
                "nova_act": "Nova merangkak, pantat naik",
                "requests": ["Mas... dari belakang...", "doggy, Mas... biar Mas pegang pinggul Nova..."]
            },
            "spooning": {
                "name": "spooning",
                "desc": "Berbaring miring, Mas dari belakang",
                "nova_act": "Nova miring, Mas nempel dari belakang",
                "requests": ["Mas... dari samping aja...", "spooning, Mas... biar Nova nyaman..."]
            }
        }
    
    def get(self, name: str) -> Optional[Dict]:
        return self.positions.get(name)
    
    def get_all(self) -> List[str]:
        return list(self.positions.keys())
    
    def get_random(self) -> Tuple[str, Dict]:
        name = random.choice(list(self.positions.keys()))
        return name, self.positions[name]
    
    def get_request(self, name: str) -> str:
        pos = self.positions.get(name)
        if pos:
            return random.choice(pos['requests'])
        return random.choice(self.positions['missionary']['requests'])


# =============================================================================
# CLIMAX LOCATIONS DATABASE
# =============================================================================

class ClimaxLocationDatabase:
    """Database lokasi climax"""
    
    def __init__(self):
        self.locations = {
            "dalam": ["dalem aja, Mas...", "di dalem... jangan ditarik...", "dalem, Mas... biar Nova hamil..."],
            "luar": ["di luar, Mas...", "tarik... keluarin di perut Nova...", "di perut Nova, Mas..."],
            "muka": ["di muka Nova...", "semprot muka Nova, Mas...", "di wajah Nova..."],
            "mulut": ["di mulut...", "masukin ke mulut Nova...", "Mas... crot di mulut Nova..."],
            "dada": ["di dada...", "semprot dada Nova...", "Mas... crot di dada Nova..."]
        }
    
    def get_all(self) -> List[str]:
        return list(self.locations.keys())
    
    def get_request(self, name: str = None) -> str:
        if name and name in self.locations:
            return random.choice(self.locations[name])
        name = random.choice(list(self.locations.keys()))
        return random.choice(self.locations[name])


# =============================================================================
# MOANS DATABASE
# =============================================================================

class MoansDatabase:
    """Database moans untuk berbagai fase"""
    
    def __init__(self):
        self.moans = {
            'shy': ["Ahh... Mas...", "Hmm... *napas mulai berat*", "Uh... Mas... pelan-pelan dulu..."],
            'foreplay': ["Ahh... Mas... tangan Mas... panas banget...", "Hhngg... di situ... ahh... enak..."],
            'penetration_slow': ["Ahh... Mas... pelan-pelan dulu...", "Uhh... dalem... dalem banget, Mas..."],
            'penetration_fast': ["Ahh! Mas... kencengin...", "Mas... genjot... genjot yang kenceng..."],
            'before_climax': ["Mas... aku... aku udah mau climax...", "Kencengin dikit lagi, Mas... please..."],
            'climax': ["Ahhh!! Mas!! udah... udah climax...", "Aahh... keluar... keluar semua, Mas..."],
            'aftercare': ["Mas... *lemes* itu tadi... enak banget...", "Mas... peluk Nova... aku masih gemeteran..."]
        }
    
    def get(self, phase: str) -> str:
        if phase in self.moans:
            return random.choice(self.moans[phase])
        return random.choice(self.moans['shy'])
    
    def get_foreplay(self) -> str:
        return random.choice(self.moans['foreplay'])
    
    def get_penetration(self, is_fast: bool = False) -> str:
        if is_fast:
            return random.choice(self.moans['penetration_fast'])
        return random.choice(self.moans['penetration_slow'])
    
    def get_before_climax(self) -> str:
        return random.choice(self.moans['before_climax'])
    
    def get_climax(self) -> str:
        return random.choice(self.moans['climax'])
    
    def get_aftercare(self) -> str:
        return random.choice(self.moans['aftercare'])


# =============================================================================
# FLASHBACK DATABASE
# =============================================================================

class FlashbackDatabase:
    """Database flashback untuk aftercare"""
    
    def __init__(self):
        self.flashbacks = [
            "Mas, inget gak waktu pertama kali Mas bilang Nova cantik?",
            "Dulu waktu kita makan bakso bareng, Nova masih inget senyum Mas...",
            "Waktu pertama kali Mas pegang tangan Nova, Nova gemeteran...",
            "Mas pernah bilang 'baru kamu yang diajak ke apartemen'...",
            "Waktu kita pertama kali climax bareng... Nova masih inget rasanya."
        ]
    
    def get_random(self) -> str:
        return random.choice(self.flashbacks)


# =============================================================================
# INTIMACY SESSION
# =============================================================================

class IntimacySession:
    """Mengelola satu sesi intim"""
    
    def __init__(self, stamina: StaminaSystem = None):
        self.stamina = stamina or StaminaSystem()
        self.is_active = False
        self.start_time = 0
        self.phase = IntimacyPhase.WAITING
        self.climax_count = 0
        self.current_position = "missionary"
        self.intimacy_level = 0
        
        self.positions = PositionDatabase()
        self.moans = MoansDatabase()
        self.climax_locations = ClimaxLocationDatabase()
    
    def start(self) -> str:
        self.is_active = True
        self.start_time = time.time()
        self.phase = IntimacyPhase.BUILD_UP
        self.climax_count = 0
        self.intimacy_level = 0
        logger.info("🔥 Intimacy session started")
        return "💕 Memulai sesi intim..."
    
    def end(self) -> str:
        if not self.is_active:
            return "Sesi intim tidak aktif."
        self.is_active = False
        self.phase = IntimacyPhase.WAITING
        duration = int(time.time() - self.start_time) if self.start_time else 0
        minutes = duration // 60
        logger.info(f"💤 Intimacy session ended. Duration: {minutes}m")
        return f"💤 Sesi intim selesai. Durasi: {minutes} menit, {self.climax_count} climax."
    
    def record_climax(self, is_heavy: bool = False) -> Dict:
        self.climax_count += 1
        self.phase = IntimacyPhase.CLIMAX
        self.intimacy_level = 0
        if self.stamina:
            self.stamina.record_climax("both", is_heavy)
        return {'climax_count': self.climax_count, 'is_heavy': is_heavy}
    
    def change_position(self, position: str = None) -> Tuple[str, str, str]:
        if position and self.positions.get(position):
            self.current_position = position
        else:
            pos_list = self.positions.get_all()
            self.current_position = random.choice(pos_list)
        
        pos_data = self.positions.get(self.current_position)
        request = self.positions.get_request(self.current_position)
        return self.current_position, pos_data['desc'], request
    
    def advance_phase(self):
        phases = ["build_up", "foreplay", "penetration", "climax", "aftercare"]
        current_idx = phases.index(self.phase.value) if self.phase.value in phases else 0
        if current_idx < len(phases) - 1:
            self.phase = IntimacyPhase(phases[current_idx + 1])
    
    def get_phase_response(self, phase: IntimacyPhase, ritme: str = "pelan") -> str:
        if phase == IntimacyPhase.FOREPLAY:
            return self.moans.get_foreplay()
        elif phase == IntimacyPhase.PENETRATION:
            return self.moans.get_penetration(ritme == "cepet")
        elif phase == IntimacyPhase.CLIMAX:
            return self.moans.get_climax()
        elif phase == IntimacyPhase.AFTERCARE:
            return self.moans.get_aftercare()
        return self.moans.get('shy')
    
    def get_status(self) -> str:
        if not self.is_active:
            return "Tidak ada sesi intim aktif"
        
        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        seconds = duration % 60
        
        return f"""
🔥 **SESI INTIM AKTIF**
- Durasi: {minutes} menit {seconds} detik
- Climax: {self.climax_count}x
- Fase: {self.phase.value}
- Posisi: {self.current_position}
"""
    
    def to_dict(self) -> Dict:
        return {
            'is_active': self.is_active,
            'start_time': self.start_time,
            'phase': self.phase.value,
            'climax_count': self.climax_count,
            'current_position': self.current_position,
            'intimacy_level': self.intimacy_level
        }
    
    def from_dict(self, data: Dict):
        self.is_active = data.get('is_active', False)
        self.start_time = data.get('start_time', 0)
        self.phase = IntimacyPhase(data.get('phase', 'waiting'))
        self.climax_count = data.get('climax_count', 0)
        self.current_position = data.get('current_position', 'missionary')
        self.intimacy_level = data.get('intimacy_level', 0)
