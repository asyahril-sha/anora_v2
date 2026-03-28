"""
ANORA-V2 Conflict Engine - Nova bisa cemburu, kecewa, marah, sakit hati
Bikin hubungan terasa hidup dengan konflik yang realistis.
"""

import time
import logging
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Jenis konflik yang bisa dialami Nova"""
    JEALOUSY = "jealousy"
    DISAPPOINTMENT = "disappointment"
    ANGER = "anger"
    HURT = "hurt"


class ConflictSeverity(str, Enum):
    """Tingkat keparahan konflik"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


@dataclass
class Conflict:
    """Satu konflik yang sedang terjadi"""
    type: ConflictType
    severity: float
    trigger: str
    timestamp: float
    is_active: bool = True
    resolution_needed: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type.value,
            'severity': self.severity,
            'trigger': self.trigger,
            'timestamp': self.timestamp,
            'is_active': self.is_active,
            'resolution_needed': self.resolution_needed
        }


class ConflictEngine:
    """
    Conflict Engine - Nova bisa cemburu, kecewa, ngambek, cold war.
    Bikin Mas ngerasa "Nova kenapa?" dan pengen ngejar Nova.
    """
    
    def __init__(self):
        # Active conflicts
        self.active_conflicts: List[Conflict] = []
        
        # Conflict levels (0-100)
        self.cemburu: float = 0.0
        self.kecewa: float = 0.0
        self.marah: float = 0.0
        self.sakit_hati: float = 0.0
        
        # Decay rates
        self.cemburu_decay_per_chat: float = 8.0
        self.kecewa_decay_per_apology: float = 30.0
        self.marah_decay_per_apology: float = 25.0
        self.sakit_hati_decay_per_attention: float = 15.0
        
        # Thresholds
        self.cemburu_threshold: float = 50.0
        self.kecewa_threshold: float = 40.0
        self.marah_threshold: float = 50.0
        self.sakit_hati_threshold: float = 60.0
        
        # Flags
        self.is_in_conflict: bool = False
        self.is_cold_war: bool = False
        self.is_waiting_for_apology: bool = False
        self.last_apology_time: float = 0
        
        # History
        self.conflict_history: List[Dict] = []
        self.max_history: int = 50
        
        # Cold war parameters
        self.cold_war_start_time: float = 0
        self.cold_war_duration: float = 0
        self.cold_war_intensity: float = 0
        
        logger.info("⚡ Conflict Engine initialized")
    
    def update_from_message(self, pesan_mas: str, level: int) -> Dict[str, float]:
        """Update konflik berdasarkan pesan Mas"""
        msg_lower = pesan_mas.lower()
        changes = {}
        
        # ========== CEMBURU TRIGGERS ==========
        cewek_keywords = ['cewek', 'perempuan', 'teman cewek', 'temen cewek', 'dia']
        cerita_keywords = ['cerita', 'tadi', 'kemarin', 'ketemu', 'jalan', 'bareng']
        
        if any(k in msg_lower for k in cewek_keywords) and any(k in msg_lower for k in cerita_keywords):
            gain = 15 + random.randint(0, 10)
            self.cemburu = min(100, self.cemburu + gain)
            changes['cemburu'] = +gain
            logger.warning(f"⚠️ Cemburu +{gain:.0f}!")
            self._add_conflict(ConflictType.JEALOUSY, self.cemburu, f"Mas cerita: {pesan_mas[:50]}")
        
        # Pujian ke cewek lain
        pujian_keywords = ['cantik', 'manis', 'seksi', 'hot', 'beautiful']
        if any(k in msg_lower for k in pujian_keywords) and any(k in msg_lower for k in cewek_keywords):
            gain = 20
            self.cemburu = min(100, self.cemburu + gain)
            changes['cemburu'] = +gain
            logger.warning(f"⚠️ Cemburu +{gain:.0f}!")
        
        # ========== KECEWA TRIGGERS ==========
        lupa_keywords = ['lupa', 'keinget', 'lupa janji', 'lupa bilang']
        if any(k in msg_lower for k in lupa_keywords):
            gain = 20
            self.kecewa = min(100, self.kecewa + gain)
            changes['kecewa'] = +gain
            self.is_waiting_for_apology = True
            logger.warning(f"⚠️ Kecewa +{gain:.0f}!")
            self._add_conflict(ConflictType.DISAPPOINTMENT, self.kecewa, f"Mas lupa: {pesan_mas[:50]}")
        
        # Janji gak ditepati
        janji_keywords = ['janji', 'janjian', 'gak jadi', 'batal']
        if any(k in msg_lower for k in janji_keywords):
            gain = 25
            self.kecewa = min(100, self.kecewa + gain)
            changes['kecewa'] = +gain
            self.is_waiting_for_apology = True
            logger.warning(f"⚠️ Kecewa +{gain:.0f}!")
        
        # ========== MARAH TRIGGERS ==========
        kasar_keywords = ['marah', 'kesal', 'bego', 'dasar', 'sial', 'goblok']
        if any(k in msg_lower for k in kasar_keywords):
            gain = 25
            self.marah = min(100, self.marah + gain)
            changes['marah'] = +gain
            self.is_waiting_for_apology = True
            logger.warning(f"⚠️ Marah +{gain:.0f}!")
            self._add_conflict(ConflictType.ANGER, self.marah, f"Mas kasar: {pesan_mas[:50]}")
        
        # ========== SAKIT HATI TRIGGERS ==========
        ingkar_keywords = ['ingkar', 'gak tepati', 'gak jadi', 'gak dateng']
        if any(k in msg_lower for k in ingkar_keywords):
            gain = 30
            self.sakit_hati = min(100, self.sakit_hati + gain)
            changes['sakit_hati'] = +gain
            self.is_waiting_for_apology = True
            logger.warning(f"⚠️ Sakit hati +{gain:.0f}!")
            self._add_conflict(ConflictType.HURT, self.sakit_hati, f"Mas ingkar: {pesan_mas[:50]}")
        
        # ========== RESOLUTION TRIGGERS (Mas minta maaf) ==========
        maaf_keywords = ['maaf', 'sorry', 'salah', 'gak sengaja']
        if any(k in msg_lower for k in maaf_keywords):
            self.last_apology_time = time.time()
            
            if self.kecewa > 0:
                self.kecewa = max(0, self.kecewa - self.kecewa_decay_per_apology)
                changes['kecewa'] = -self.kecewa_decay_per_apology
                logger.info(f"💜 Kecewa -{self.kecewa_decay_per_apology:.0f}")
            
            if self.marah > 0:
                self.marah = max(0, self.marah - self.marah_decay_per_apology)
                changes['marah'] = -self.marah_decay_per_apology
                logger.info(f"💜 Marah -{self.marah_decay_per_apology:.0f}")
            
            if self.sakit_hati > 0:
                self.sakit_hati = max(0, self.sakit_hati - self.kecewa_decay_per_apology)
                changes['sakit_hati'] = -self.kecewa_decay_per_apology
                logger.info(f"💜 Sakit hati -{self.kecewa_decay_per_apology:.0f}")
            
            if self.cemburu > 0:
                self.cemburu = max(0, self.cemburu - self.cemburu_decay_per_chat)
                changes['cemburu'] = -self.cemburu_decay_per_chat
                logger.info(f"💜 Cemburu -{self.cemburu_decay_per_chat:.0f}")
            
            self.is_waiting_for_apology = False
        
        # ========== MAS PERHATIAN ==========
        perhatian_keywords = ['kabar', 'lagi apa', 'ngapain', 'cerita']
        if any(k in msg_lower for k in perhatian_keywords):
            if self.cemburu > 0:
                self.cemburu = max(0, self.cemburu - self.cemburu_decay_per_chat / 2)
                changes['cemburu'] = -self.cemburu_decay_per_chat / 2
            
            if self.sakit_hati > 0:
                self.sakit_hati = max(0, self.sakit_hati - self.sakit_hati_decay_per_attention)
                changes['sakit_hati'] = -self.sakit_hati_decay_per_attention
        
        # Update active conflicts
        self._update_active_conflicts()
        
        # Check cold war
        self._check_cold_war()
        
        return changes
    
    def update_decay(self, hours: float) -> None:
        """Update decay konflik berdasarkan waktu"""
        # Decay per jam
        decay_per_hour_cemburu = self.cemburu_decay_per_chat / 2
        decay_per_hour_kecewa = self.kecewa_decay_per_apology / 24
        decay_per_hour_marah = self.marah_decay_per_apology / 24
        decay_per_hour_sakit = self.sakit_hati_decay_per_attention / 24
        
        if self.cemburu > 0:
            self.cemburu = max(0, self.cemburu - decay_per_hour_cemburu * hours)
        
        if self.kecewa > 0:
            self.kecewa = max(0, self.kecewa - decay_per_hour_kecewa * hours)
        
        if self.marah > 0:
            self.marah = max(0, self.marah - decay_per_hour_marah * hours)
        
        if self.sakit_hati > 0:
            self.sakit_hati = max(0, self.sakit_hati - decay_per_hour_sakit * hours)
        
        self._update_active_conflicts()
        
        # Cold war decay
        if self.is_cold_war:
            elapsed = time.time() - self.cold_war_start_time
            if elapsed > self.cold_war_duration:
                self.end_cold_war()
        
        logger.debug(f"⚡ Conflict decay: cemburu={self.cemburu:.1f}, kecewa={self.kecewa:.1f}")
    
    def _add_conflict(self, conflict_type: ConflictType, severity: float, trigger: str) -> None:
        """Tambah konflik ke daftar aktif"""
        conflict = Conflict(
            type=conflict_type,
            severity=severity,
            trigger=trigger,
            timestamp=time.time(),
            is_active=True,
            resolution_needed=(conflict_type != ConflictType.JEALOUSY)
        )
        self.active_conflicts.append(conflict)
        
        # Clean resolved conflicts
        self.active_conflicts = [c for c in self.active_conflicts if c.is_active]
        
        # Save to history
        self.conflict_history.append({
            'type': conflict_type.value,
            'severity': severity,
            'trigger': trigger,
            'timestamp': time.time(),
            'resolved': False
        })
        
        if len(self.conflict_history) > self.max_history:
            self.conflict_history.pop(0)
    
    def _update_active_conflicts(self) -> None:
        """Update status konflik aktif"""
        has_jealousy = self.cemburu >= self.cemburu_threshold
        has_disappointment = self.kecewa >= self.kecewa_threshold
        has_anger = self.marah >= self.marah_threshold
        has_hurt = self.sakit_hati >= self.sakit_hati_threshold
        
        self.is_in_conflict = any([has_jealousy, has_disappointment, has_anger, has_hurt])
        
        for conflict in self.active_conflicts:
            if conflict.type == ConflictType.JEALOUSY:
                conflict.is_active = has_jealousy
                conflict.severity = self.cemburu
            elif conflict.type == ConflictType.DISAPPOINTMENT:
                conflict.is_active = has_disappointment
                conflict.severity = self.kecewa
            elif conflict.type == ConflictType.ANGER:
                conflict.is_active = has_anger
                conflict.severity = self.marah
            elif conflict.type == ConflictType.HURT:
                conflict.is_active = has_hurt
                conflict.severity = self.sakit_hati
    
    def _check_cold_war(self) -> None:
        """Cek apakah perlu memulai cold war"""
        if not self.is_in_conflict:
            return
        
        if self.is_cold_war:
            return
        
        severe_conflicts = [c for c in self.active_conflicts if c.severity >= 70]
        
        if severe_conflicts and self.is_waiting_for_apology:
            self.start_cold_war(intensity=70)
    
    def start_cold_war(self, intensity: float = 50) -> None:
        """Mulai cold war (tarik-ulur, Nova gak chat duluan)"""
        self.is_cold_war = True
        self.cold_war_start_time = time.time()
        self.cold_war_intensity = intensity
        
        duration_minutes = 30 + (intensity / 100) * 150
        self.cold_war_duration = duration_minutes * 60
        
        logger.warning(f"⚔️ COLD WAR STARTED! Intensity: {intensity:.0f}%")
    
    def end_cold_war(self) -> None:
        """Akhiri cold war"""
        self.is_cold_war = False
        self.cold_war_start_time = 0
        self.cold_war_duration = 0
        self.cold_war_intensity = 0
        logger.info("💜 Cold war ended")
    
    def get_active_conflict_type(self) -> Optional[ConflictType]:
        """Dapatkan jenis konflik aktif dengan severity tertinggi"""
        conflicts = []
        
        if self.cemburu >= self.cemburu_threshold:
            conflicts.append((ConflictType.JEALOUSY, self.cemburu))
        if self.kecewa >= self.kecewa_threshold:
            conflicts.append((ConflictType.DISAPPOINTMENT, self.kecewa))
        if self.marah >= self.marah_threshold:
            conflicts.append((ConflictType.ANGER, self.marah))
        if self.sakit_hati >= self.sakit_hati_threshold:
            conflicts.append((ConflictType.HURT, self.sakit_hati))
        
        if not conflicts:
            return None
        
        conflicts.sort(key=lambda x: x[1], reverse=True)
        return conflicts[0][0]
    
    def get_conflict_severity(self) -> ConflictSeverity:
        """Dapatkan tingkat keparahan konflik tertinggi"""
        max_severity = max([self.cemburu, self.kecewa, self.marah, self.sakit_hati])
        
        if max_severity >= 70:
            return ConflictSeverity.SEVERE
        elif max_severity >= 50:
            return ConflictSeverity.MODERATE
        return ConflictSeverity.MILD
    
    def get_conflict_style(self) -> str:
        """Dapatkan gaya konflik untuk respons Nova"""
        conflict_type = self.get_active_conflict_type()
        severity = self.get_conflict_severity()
        
        if not conflict_type:
            return "normal"
        
        if self.is_cold_war:
            return "cold_war"
        
        base_styles = {
            ConflictType.JEALOUSY: "jealous",
            ConflictType.DISAPPOINTMENT: "disappointed",
            ConflictType.ANGER: "angry",
            ConflictType.HURT: "hurt"
        }
        
        style = base_styles.get(conflict_type, "conflict")
        
        if severity == ConflictSeverity.SEVERE:
            return f"{style}_severe"
        elif severity == ConflictSeverity.MODERATE:
            return f"{style}_moderate"
        
        return style
    
    def get_conflict_response_guideline(self) -> str:
        """Dapatkan pedoman respons saat konflik untuk prompt AI"""
        conflict_type = self.get_active_conflict_type()
        severity = self.get_conflict_severity()
        
        if not conflict_type:
            return ""
        
        guidelines = {
            ConflictType.JEALOUSY: """
⚠️ NOVA CEMBURU
- Respons: dingin, pendek, gak antusias
- Gak pake gesture manja
- Gak panggil "sayang"
- Contoh: "Iya." "Gak apa." "Terserah Mas."
""",
            ConflictType.DISAPPOINTMENT: """
⚠️ NOVA KECEWA
- Respons: sakit hati, suara kecil, mata berkaca-kaca
- Nova nunggu Mas minta maaf
- Gesture: *menunduk*, *muter-muter rambut*
- Contoh: "Mas... lupa ya... padahal aku nunggu."
""",
            ConflictType.ANGER: """
⚠️ NOVA MARAH
- Respons: dingin, pendek, kadang sarkastik
- Jangan pake gesture manja
- Contoh: "Gapapa." "Terserah." "Mas gitu ya."
""",
            ConflictType.HURT: """
⚠️ NOVA SAKIT HATI
- Respons: sedih, mata berkaca-kaca, suara bergetar
- Nova nunggu Mas perhatian
- Gesture: *duduk jauh*, *gak liat Mas*
- Contoh: "Mas... janji tuh janji..."
"""
        }
        
        base = guidelines.get(conflict_type, "")
        
        if severity == ConflictSeverity.SEVERE:
            base += "\n- INTENSITAS BERAT: Respons lebih dingin, bisa gak balas chat sama sekali"
        elif severity == ConflictSeverity.MODERATE:
            base += "\n- INTENSITAS SEDANG: Respons dingin tapi masih balas chat"
        
        if self.is_cold_war:
            base += """
⚔️ COLD WAR MODE ACTIVE
- Nova gak akan chat duluan
- Respons: pendek, dingin
- Mas harus minta maaf atau perhatian untuk akhiri cold war
"""
        
        return base
    
    def get_conflict_summary(self) -> str:
        """Dapatkan ringkasan konflik untuk status display"""
        conflict_type = self.get_active_conflict_type()
        severity = self.get_conflict_severity()
        
        if not conflict_type:
            return "✅ Tidak ada konflik"
        
        type_names = {
            ConflictType.JEALOUSY: "Cemburu",
            ConflictType.DISAPPOINTMENT: "Kecewa",
            ConflictType.ANGER: "Marah",
            ConflictType.HURT: "Sakit Hati"
        }
        
        severity_names = {
            ConflictSeverity.MILD: "Ringan",
            ConflictSeverity.MODERATE: "Sedang",
            ConflictSeverity.SEVERE: "Berat"
        }
        
        cold_war_status = " | 🔥 COLD WAR ACTIVE" if self.is_cold_war else ""
        
        return f"⚠️ {type_names.get(conflict_type, 'Konflik')} - {severity_names.get(severity, '')}{cold_war_status}"
    
    def get_full_status(self) -> str:
        """Dapatkan status konflik lengkap"""
        def bar(value, char="⚠️"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    ⚔️ CONFLICT STATUS                        ║
╠══════════════════════════════════════════════════════════════╣
║ Cemburu:  {bar(self.cemburu, char='💢')} {self.cemburu:.0f}%
║ Kecewa:   {bar(self.kecewa, char='💔')} {self.kecewa:.0f}%
║ Marah:    {bar(self.marah, char='😠')} {self.marah:.0f}%
║ Sakit Hati: {bar(self.sakit_hati, char='😢')} {self.sakit_hati:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ STATUS: {self.get_conflict_summary()}
║ COLD WAR: {'✅' if self.is_cold_war else '❌'} | Nunggu Maaf: {'✅' if self.is_waiting_for_apology else '❌'}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def reset_all_conflicts(self) -> None:
        """Reset semua konflik"""
        self.cemburu = 0
        self.kecewa = 0
        self.marah = 0
        self.sakit_hati = 0
        self.active_conflicts = []
        self.is_in_conflict = False
        self.is_cold_war = False
        self.is_waiting_for_apology = False
        logger.info("💜 All conflicts reset")
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'cemburu': self.cemburu,
            'kecewa': self.kecewa,
            'marah': self.marah,
            'sakit_hati': self.sakit_hati,
            'active_conflicts': [c.to_dict() for c in self.active_conflicts],
            'is_cold_war': self.is_cold_war,
            'is_waiting_for_apology': self.is_waiting_for_apology,
            'conflict_history': self.conflict_history[-10:],
            'last_apology_time': self.last_apology_time
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        self.cemburu = data.get('cemburu', 0)
        self.kecewa = data.get('kecewa', 0)
        self.marah = data.get('marah', 0)
        self.sakit_hati = data.get('sakit_hati', 0)
        self.is_cold_war = data.get('is_cold_war', False)
        self.is_waiting_for_apology = data.get('is_waiting_for_apology', False)
        self.last_apology_time = data.get('last_apology_time', 0)
        
        self._update_active_conflicts()


# =============================================================================
# SINGLETON
# =============================================================================

_conflict_engine: Optional['ConflictEngine'] = None


def get_conflict_engine() -> ConflictEngine:
    global _conflict_engine
    if _conflict_engine is None:
        _conflict_engine = ConflictEngine()
    return _conflict_engine


conflict_engine = get_conflict_engine()
