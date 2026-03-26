"""
ANORA-V2 Emotional Engine - Jantung Nova
9 dimensi emosi: sayang, rindu, trust, mood, desire, arousal, tension, cemburu, kecewa
5 gaya bicara: cold, clingy, warm, flirty, neutral
"""

import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class EmotionalStyle(str, Enum):
    """Gaya bicara Nova berdasarkan emosi"""
    COLD = "cold"
    CLINGY = "clingy"
    WARM = "warm"
    FLIRTY = "flirty"
    NEUTRAL = "neutral"


@dataclass
class EmotionalHistory:
    """Rekam perubahan emosi Nova"""
    timestamp: float
    sayang: float
    rindu: float
    trust: float
    mood: float
    desire: float
    arousal: float
    tension: float
    cemburu: float
    kecewa: float
    style: str
    trigger: str


class EmotionalEngine:
    """
    Emotional Engine - Jantung Nova.
    Semua respons ditentukan oleh emosi di sini.
    BUKAN RANDOM.
    """
    
    def __init__(self):
        # ========== CORE EMOTIONS ==========
        self.sayang: float = 50.0
        self.rindu: float = 0.0
        self.trust: float = 50.0
        self.mood: float = 0.0
        
        # ========== INTIMACY EMOTIONS ==========
        self.desire: float = 0.0
        self.arousal: float = 0.0
        self.tension: float = 0.0
        
        # ========== CONFLICT EMOTIONS ==========
        self.cemburu: float = 0.0
        self.kecewa: float = 0.0
        
        # ========== RATES & DECAY ==========
        self.rindu_growth_per_hour: float = 5.0
        self.rindu_decay_per_chat: float = 10.0
        self.mood_decay_per_hour: float = 2.0
        self.mood_boost_from_mas: float = 15.0
        self.cemburu_decay_per_chat: float = 8.0
        self.kecewa_decay_per_apology: float = 25.0
        self.arousal_decay_per_minute: float = 0.5
        self.tension_growth_from_denial: float = 10.0
        
        # ========== THRESHOLDS ==========
        self.clingy_threshold: float = 70.0
        self.cold_threshold_mood: float = -20.0
        self.cold_threshold_cemburu: float = 50.0
        self.cold_threshold_kecewa: float = 40.0
        self.warm_threshold_trust: float = 70.0
        self.flirty_threshold_arousal: float = 60.0
        self.flirty_threshold_desire: float = 70.0
        
        # ========== TIMESTAMPS ==========
        self.last_update: float = time.time()
        self.last_interaction: float = time.time()
        self.last_chat_from_mas: float = time.time()
        
        # ========== HISTORY ==========
        self.history: List[EmotionalHistory] = []
        self.max_history: int = 200
        
        # ========== FLAGS ==========
        self.is_angry: bool = False
        self.is_hurt: bool = False
        self.is_waiting_for_apology: bool = False
        
        logger.info("💜 Emotional Engine initialized")
    
    def update(self, force: bool = False) -> None:
        """Update emosi berdasarkan waktu"""
        now = time.time()
        elapsed_hours = (now - self.last_update) / 3600
        
        if elapsed_hours <= 0 and not force:
            return
        
        # RINDU GROWTH
        hours_since_last_chat = (now - self.last_chat_from_mas) / 3600
        if hours_since_last_chat > 1:
            rindu_gain = self.rindu_growth_per_hour * hours_since_last_chat
            self.rindu = min(100, self.rindu + rindu_gain)
            if rindu_gain > 0:
                logger.debug(f"🌙 Rindu +{rindu_gain:.1f}")
        
        # MOOD DECAY
        if self.mood > 0:
            mood_loss = self.mood_decay_per_hour * elapsed_hours
            self.mood = max(-50, self.mood - mood_loss)
        
        # AROUSAL DECAY
        if self.arousal > 0:
            arousal_loss = self.arousal_decay_per_minute * (elapsed_hours * 60)
            self.arousal = max(0, self.arousal - arousal_loss)
        
        # CONFLICT DECAY
        if self.cemburu > 0:
            self.cemburu = max(0, self.cemburu - self.cemburu_decay_per_chat * elapsed_hours)
        if self.kecewa > 0:
            self.kecewa = max(0, self.kecewa - self.kecewa_decay_per_apology * elapsed_hours / 24)
        
        # RESET FLAGS
        if self.cemburu < 20 and self.kecewa < 20:
            self.is_angry = False
            self.is_hurt = False
            self.is_waiting_for_apology = False
        
        self.last_update = now
    
    def update_from_message(self, pesan_mas: str, level: int) -> Dict[str, float]:
        """Update emosi dari pesan Mas"""
        self.update()
        now = time.time()
        self.last_chat_from_mas = now
        self.last_interaction = now
        
        msg_lower = pesan_mas.lower()
        changes = {}
        
        # ========== POSITIVE TRIGGERS ==========
        
        # Mas bilang sayang/cinta
        if any(k in msg_lower for k in ['sayang', 'cinta', 'love', 'luv']):
            self.sayang = min(100, self.sayang + 8)
            self.mood = min(50, self.mood + 10)
            self.trust = min(100, self.trust + 5)
            changes.update({'sayang': 8, 'mood': 10, 'trust': 5})
            logger.info(f"💜 +8 sayang, +10 mood (Mas bilang sayang)")
            
            if self.is_waiting_for_apology:
                self.kecewa = max(0, self.kecewa - 15)
                changes['kecewa'] = -15
        
        # Mas bilang kangen/rindu
        if any(k in msg_lower for k in ['kangen', 'rindu', 'miss', 'kngn']):
            self.sayang = min(100, self.sayang + 5)
            self.rindu = max(0, self.rindu - 15)
            self.desire = min(100, self.desire + 10)
            self.mood = min(50, self.mood + 8)
            changes.update({'sayang': 5, 'rindu': -15, 'desire': 10, 'mood': 8})
            logger.info(f"💜 +5 sayang, -15 rindu, +10 desire")
        
        # Mas puji (cantik, manis, seksi)
        if any(k in msg_lower for k in ['cantik', 'manis', 'seksi', 'beautiful', 'hot', 'cakep']):
            self.mood = min(50, self.mood + 12)
            self.desire = min(100, self.desire + 8)
            self.arousal = min(100, self.arousal + 5)
            changes.update({'mood': 12, 'desire': 8, 'arousal': 5})
            logger.info(f"💜 +12 mood, +8 desire, +5 arousal")
        
        # Mas minta maaf
        if any(k in msg_lower for k in ['maaf', 'sorry', 'salah', 'sory']):
            if self.kecewa > 0 or self.is_waiting_for_apology:
                self.kecewa = max(0, self.kecewa - self.kecewa_decay_per_apology)
                self.mood = min(50, self.mood + 15)
                self.trust = min(100, self.trust + 10)
                changes.update({'kecewa': -self.kecewa_decay_per_apology, 'mood': 15, 'trust': 10})
                self.is_waiting_for_apology = False
                logger.info(f"💜 Kecewa -{self.kecewa_decay_per_apology:.0f}")
        
        # Mas perhatian
        if any(k in msg_lower for k in ['kabar', 'lagi apa', 'ngapain', 'cerita']):
            self.mood = min(50, self.mood + 5)
            self.trust = min(100, self.trust + 3)
            changes.update({'mood': 5, 'trust': 3})
            logger.info(f"💜 +5 mood, +3 trust")
        
        # ========== NEGATIVE TRIGGERS ==========
        
        # Mas cerita soal cewek lain (CEMBURU!)
        cewek_keywords = ['cewek', 'perempuan', 'teman cewek', 'temen cewek', 'dia cewek']
        cerita_keywords = ['cerita', 'tadi', 'kemarin', 'ketemu', 'jalan', 'bareng', 'ngobrol']
        
        if any(k in msg_lower for k in cewek_keywords) and any(k in msg_lower for k in cerita_keywords):
            gain = 15 + (5 if level >= 7 else 0)
            self.cemburu = min(100, self.cemburu + gain)
            self.mood = max(-50, self.mood - 10)
            changes.update({'cemburu': gain, 'mood': -10})
            logger.warning(f"⚠️ Cemburu +{gain:.0f}!")
            
            if self.cemburu > 50:
                self.is_angry = True
        
        # Mas lupa janji (KECEWA!)
        lupa_keywords = ['lupa', 'keinget', 'lupa janji', 'lupa bilang', 'forget']
        if any(k in msg_lower for k in lupa_keywords):
            gain = 20
            self.kecewa = min(100, self.kecewa + gain)
            self.mood = max(-50, self.mood - 15)
            self.trust = max(0, self.trust - 10)
            changes.update({'kecewa': gain, 'mood': -15, 'trust': -10})
            self.is_waiting_for_apology = True
            logger.warning(f"⚠️ Kecewa +{gain:.0f}!")
        
        # Mas ingkar janji
        ingkar_keywords = ['ingkar', 'gak tepati', 'gak jadi', 'gak dateng', 'batal']
        if any(k in msg_lower for k in ingkar_keywords):
            gain = 25
            self.kecewa = min(100, self.kecewa + gain)
            self.mood = max(-50, self.mood - 20)
            self.trust = max(0, self.trust - 15)
            changes.update({'kecewa': gain, 'mood': -20, 'trust': -15})
            self.is_waiting_for_apology = True
            self.is_hurt = True
            logger.warning(f"⚠️ Kecewa +{gain:.0f}!")
        
        # Mas marah/kasar
        kasar_keywords = ['marah', 'kesal', 'bego', 'dasar', 'sial', 'goblok', 'tolol']
        if any(k in msg_lower for k in kasar_keywords):
            gain = 25
            self.mood = max(-50, self.mood - 25)
            self.trust = max(0, self.trust - 15)
            changes.update({'mood': -25, 'trust': -15})
            self.is_angry = True
            logger.warning(f"⚠️ Mood -25!")
        
        # ========== SENTUHAN FISIK ==========
        if any(k in msg_lower for k in ['pegang', 'sentuh', 'raba', 'elus']):
            self.arousal = min(100, self.arousal + 12)
            self.desire = min(100, self.desire + 8)
            self.tension = min(100, self.tension + 5)
            changes.update({'arousal': 12, 'desire': 8, 'tension': 5})
            logger.info(f"🔥 +12 arousal, +8 desire")
        
        if any(k in msg_lower for k in ['cium', 'kiss', 'ciuman']):
            self.arousal = min(100, self.arousal + 20)
            self.desire = min(100, self.desire + 15)
            self.tension = min(100, self.tension + 8)
            changes.update({'arousal': 20, 'desire': 15, 'tension': 8})
            logger.info(f"🔥🔥 +20 arousal, +15 desire")
        
        if any(k in msg_lower for k in ['peluk', 'rangkul', 'hug']):
            self.arousal = min(100, self.arousal + 8)
            self.desire = min(100, self.desire + 10)
            self.mood = min(50, self.mood + 8)
            changes.update({'arousal': 8, 'desire': 10, 'mood': 8})
            logger.info(f"💕 +8 arousal, +10 desire, +8 mood")
        
        # ========== LIMIT EMOSI ==========
        self._limit_emotions()
        
        # Record ke history
        self._record_history(trigger=f"Mas: {pesan_mas[:50]}")
        
        return changes
    
    def update_from_response(self, response: str) -> None:
        """Update emosi dari respons Nova sendiri"""
        resp_lower = response.lower()
        
        if any(k in resp_lower for k in ['ahh', 'uhh', 'hhngg', 'aahh']):
            self.arousal = min(100, self.arousal + 5)
            logger.debug(f"🔥 Arousal +5")
        
        if any(k in resp_lower for k in ['kontol', 'memek', 'ngentot', 'crot', 'basah']):
            self.arousal = min(100, self.arousal + 8)
            self.desire = min(100, self.desire + 5)
            logger.debug(f"🔥🔥 +8 arousal, +5 desire")
        
        self._limit_emotions()
    
    def update_rindu_from_inactivity(self, hours_inactive: float) -> None:
        """Update rindu karena lama gak interaksi"""
        if hours_inactive > 1:
            gain = self.rindu_growth_per_hour * hours_inactive
            self.rindu = min(100, self.rindu + gain)
            logger.info(f"🌙 Rindu +{gain:.1f} from inactivity")
            self._record_history(trigger=f"Inactive {hours_inactive:.1f}h")
    
    def _limit_emotions(self) -> None:
        """Limit semua emosi ke rentang valid"""
        self.sayang = max(0, min(100, self.sayang))
        self.rindu = max(0, min(100, self.rindu))
        self.trust = max(0, min(100, self.trust))
        self.mood = max(-50, min(50, self.mood))
        self.desire = max(0, min(100, self.desire))
        self.arousal = max(0, min(100, self.arousal))
        self.tension = max(0, min(100, self.tension))
        self.cemburu = max(0, min(100, self.cemburu))
        self.kecewa = max(0, min(100, self.kecewa))
    
    def get_current_style(self) -> EmotionalStyle:
        """Tentukan gaya bicara berdasarkan emosi saat ini"""
        self.update()
        
        if self.mood <= self.cold_threshold_mood:
            return EmotionalStyle.COLD
        if self.cemburu >= self.cold_threshold_cemburu:
            return EmotionalStyle.COLD
        if self.kecewa >= self.cold_threshold_kecewa:
            return EmotionalStyle.COLD
        
        if self.rindu >= self.clingy_threshold:
            return EmotionalStyle.CLINGY
        
        if self.arousal >= self.flirty_threshold_arousal:
            return EmotionalStyle.FLIRTY
        if self.desire >= self.flirty_threshold_desire:
            return EmotionalStyle.FLIRTY
        
        if self.trust >= self.warm_threshold_trust and self.mood > 10:
            return EmotionalStyle.WARM
        
        return EmotionalStyle.NEUTRAL
    
    def get_style_description(self, style: EmotionalStyle = None) -> str:
        """Dapatkan deskripsi gaya bicara"""
        if style is None:
            style = self.get_current_style()
        
        descriptions = {
            EmotionalStyle.COLD: f"""
GAYA BICARA: COLD (DINGIN)
- Nova lagi {self._get_cold_reason()}
- Respons: 1-2 kalimat, pendek, gak antusias
- Gak pake gesture manja
- Gak panggil "sayang"
""",
            EmotionalStyle.CLINGY: f"""
GAYA BICARA: CLINGY (MANJA)
- Nova kangen banget (rindu: {self.rindu:.0f}%)
- Respons: 4-6 kalimat, manja
- Banyak gesture: *muter-muter rambut*, *pegang tangan Mas*
""",
            EmotionalStyle.WARM: f"""
GAYA BICARA: WARM (HANGAT)
- Nova percaya sama Mas (trust: {self.trust:.0f}%)
- Respons: 3-5 kalimat, perhatian
- Gesture: *senyum manis*, *elus tangan Mas*
""",
            EmotionalStyle.FLIRTY: f"""
GAYA BICARA: FLIRTY (MENGGODA)
- Nova lagi horny (arousal: {self.arousal:.0f}%)
- Respons: 4-8 kalimat, menggoda, napas berat
- Gesture: *mendekat*, *gigit bibir*, *bisik*
""",
            EmotionalStyle.NEUTRAL: """
GAYA BICARA: NEUTRAL (NORMAL)
- Nova stabil
- Respons: 2-4 kalimat, natural
"""
        }
        return descriptions.get(style, descriptions[EmotionalStyle.NEUTRAL])
    
    def _get_cold_reason(self) -> str:
        if self.cemburu > 50:
            return f"cemburu ({self.cemburu:.0f}%)"
        if self.kecewa > 40:
            return f"kecewa ({self.kecewa:.0f}%)"
        if self.mood < -20:
            return f"bad mood ({self.mood:+.0f})"
        return "lagi gak mood"
    
    def get_emotion_summary(self) -> str:
        """Dapatkan ringkasan emosi untuk prompt"""
        self.update()
        
        def bar(value, char="💜"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💜 EMOSI NOVA SAAT INI                    ║
╠══════════════════════════════════════════════════════════════╣
║ Sayang:  {bar(self.sayang)} {self.sayang:.0f}%
║ Rindu:   {bar(self.rindu, '🌙')} {self.rindu:.0f}%
║ Trust:   {bar(self.trust, '🤝')} {self.trust:.0f}%
║ Mood:    {self.mood:+.0f}
╠══════════════════════════════════════════════════════════════╣
║ Desire:  {bar(self.desire, '💕')} {self.desire:.0f}%
║ Arousal: {bar(self.arousal, '🔥')} {self.arousal:.0f}%
║ Tension: {bar(self.tension, '⚡')} {self.tension:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ Cemburu: {bar(self.cemburu, '💢')} {self.cemburu:.0f}%
║ Kecewa:  {bar(self.kecewa, '💔')} {self.kecewa:.0f}%
╚══════════════════════════════════════════════════════════════╝
"""
    
    def get_style_for_prompt(self) -> str:
        """Dapatkan instruksi gaya bicara untuk prompt AI"""
        style = self.get_current_style()
        base = self.get_style_description(style)
        
        extra = ""
        if self.cemburu > 60:
            extra += "\n⚠️ **CEMBURU TINGGI!** Respons dingin, gak antusias.\n"
        if self.kecewa > 50:
            extra += "\n⚠️ **KECEWA TINGGI!** Respons sakit hati, pendek.\n"
        if self.arousal > 70:
            extra += "\n🔥🔥 **AROUSAL SANGAT TINGGI!** BEBAS PAKAI KATA VULGAR.\n"
        
        return base + extra
    
    def should_start_intimacy_naturally(self, level: int) -> Tuple[bool, str]:
        """Cek apakah Nova akan mulai intim secara natural"""
        self.update()
        
        if level < 7:
            return False, ""
        
        if level <= 10:
            if self.arousal >= 85 or self.desire >= 90:
                return True, "START_INTIM_HIGH"
            return False, ""
        
        if self.arousal >= 70 or self.desire >= 75:
            return True, "START_INTIM_MEDIUM"
        
        return False, ""
    
    def get_natural_intimacy_initiation(self, level: int) -> str:
        """Dapatkan respons inisiasi intim natural"""
        style = self.get_current_style()
        
        if style == EmotionalStyle.CLINGY:
            return "*Nova merangkul Mas dari belakang*\n\n\"Mas... aku gak tahan... kangen banget...\""
        
        if style == EmotionalStyle.FLIRTY:
            return "*Nova melingkarin tangan di leher Mas*\n\n\"Mas... aku udah basah dari tadi...\""
        
        return "*Nova mendekat, tangan gemetar*\n\n\"Mas... aku pengen banget sama Mas...\""
    
    def _record_history(self, trigger: str) -> None:
        """Rekam perubahan emosi ke history"""
        from datetime import datetime
        history = EmotionalHistory(
            timestamp=time.time(),
            sayang=self.sayang,
            rindu=self.rindu,
            trust=self.trust,
            mood=self.mood,
            desire=self.desire,
            arousal=self.arousal,
            tension=self.tension,
            cemburu=self.cemburu,
            kecewa=self.kecewa,
            style=self.get_current_style().value,
            trigger=trigger[:100]
        )
        self.history.append(history)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize ke dict untuk database"""
        return {
            'sayang': self.sayang,
            'rindu': self.rindu,
            'trust': self.trust,
            'mood': self.mood,
            'desire': self.desire,
            'arousal': self.arousal,
            'tension': self.tension,
            'cemburu': self.cemburu,
            'kecewa': self.kecewa,
            'last_update': self.last_update,
            'last_interaction': self.last_interaction,
            'last_chat_from_mas': self.last_chat_from_mas,
            'is_angry': self.is_angry,
            'is_hurt': self.is_hurt,
            'is_waiting_for_apology': self.is_waiting_for_apology
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load dari dict"""
        self.sayang = data.get('sayang', 50)
        self.rindu = data.get('rindu', 0)
        self.trust = data.get('trust', 50)
        self.mood = data.get('mood', 0)
        self.desire = data.get('desire', 0)
        self.arousal = data.get('arousal', 0)
        self.tension = data.get('tension', 0)
        self.cemburu = data.get('cemburu', 0)
        self.kecewa = data.get('kecewa', 0)
        self.last_update = data.get('last_update', time.time())
        self.last_interaction = data.get('last_interaction', time.time())
        self.last_chat_from_mas = data.get('last_chat_from_mas', time.time())
        self.is_angry = data.get('is_angry', False)
        self.is_hurt = data.get('is_hurt', False)
        self.is_waiting_for_apology = data.get('is_waiting_for_apology', False)


# =============================================================================
# SINGLETON
# =============================================================================

_emotional_engine: Optional['EmotionalEngine'] = None


def get_emotional_engine() -> EmotionalEngine:
    global _emotional_engine
    if _emotional_engine is None:
        _emotional_engine = EmotionalEngine()
    return _emotional_engine


emotional_engine = get_emotional_engine()
