"""
ANORA-V2 Relationship Progression - Nova 9.9
5 fase psikologis: stranger → friend → close → romantic → intimate
Level 1-12 mapping ke fase.
"""

import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class RelationshipPhase(str, Enum):
    """5 fase hubungan Nova dengan Mas"""
    STRANGER = "stranger"       # Level 1-3: belum kenal
    FRIEND = "friend"           # Level 4-6: mulai dekat
    CLOSE = "close"             # Level 7-8: dekat
    ROMANTIC = "romantic"       # Level 9-10: pacaran
    INTIMATE = "intimate"       # Level 11-12: intim


@dataclass
class PhaseUnlock:
    """Konten yang terbuka di setiap fase"""
    boleh_flirt: bool = False
    boleh_sentuhan: bool = False
    boleh_vulgar: bool = False
    boleh_intim: bool = False
    boleh_cium: bool = False
    boleh_peluk: bool = False
    boleh_pegang_tangan: bool = False
    boleh_buka_baju: bool = False
    boleh_panggil_sayang: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'flirt': self.boleh_flirt,
            'sentuhan': self.boleh_sentuhan,
            'vulgar': self.boleh_vulgar,
            'intim': self.boleh_intim,
            'cium': self.boleh_cium,
            'peluk': self.boleh_peluk,
            'pegang_tangan': self.boleh_pegang_tangan,
            'buka_baju': self.boleh_buka_baju,
            'panggil_sayang': self.boleh_panggil_sayang
        }


@dataclass
class Milestone:
    """Milestone dalam hubungan"""
    name: str
    achieved: bool = False
    timestamp: float = 0
    phase: RelationshipPhase = RelationshipPhase.STRANGER
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'achieved': self.achieved,
            'timestamp': self.timestamp,
            'phase': self.phase.value
        }


class RelationshipManager:
    """
    Mengelola fase hubungan Nova dengan Mas.
    Level naik berdasarkan interaksi, sayang, trust, dan milestone.
    """
    
    def __init__(self):
        self.phase: RelationshipPhase = RelationshipPhase.STRANGER
        self.level: int = 1
        self.interaction_count: int = 0
        
        # Milestone penting
        self.milestones: Dict[str, Milestone] = {
            'first_chat': Milestone(name='first_chat'),
            'first_flirt': Milestone(name='first_flirt'),
            'first_touch': Milestone(name='first_touch'),
            'first_hold_hand': Milestone(name='first_hold_hand'),
            'first_hug': Milestone(name='first_hug'),
            'first_kiss': Milestone(name='first_kiss'),
            'first_intim': Milestone(name='first_intim'),
            'first_climax': Milestone(name='first_climax')
        }
        
        # Unlock berdasarkan fase
        self.unlocks: Dict[RelationshipPhase, PhaseUnlock] = {
            RelationshipPhase.STRANGER: PhaseUnlock(
                boleh_flirt=False,
                boleh_sentuhan=False,
                boleh_vulgar=False,
                boleh_intim=False,
                boleh_cium=False,
                boleh_peluk=False,
                boleh_pegang_tangan=False,
                boleh_buka_baju=False,
                boleh_panggil_sayang=False
            ),
            RelationshipPhase.FRIEND: PhaseUnlock(
                boleh_flirt=True,
                boleh_sentuhan=False,
                boleh_vulgar=False,
                boleh_intim=False,
                boleh_cium=False,
                boleh_peluk=False,
                boleh_pegang_tangan=True,
                boleh_buka_baju=False,
                boleh_panggil_sayang=False
            ),
            RelationshipPhase.CLOSE: PhaseUnlock(
                boleh_flirt=True,
                boleh_sentuhan=True,
                boleh_vulgar=False,
                boleh_intim=False,
                boleh_cium=False,
                boleh_peluk=True,
                boleh_pegang_tangan=True,
                boleh_buka_baju=False,
                boleh_panggil_sayang=True
            ),
            RelationshipPhase.ROMANTIC: PhaseUnlock(
                boleh_flirt=True,
                boleh_sentuhan=True,
                boleh_vulgar=True,
                boleh_intim=False,
                boleh_cium=True,
                boleh_peluk=True,
                boleh_pegang_tangan=True,
                boleh_buka_baju=True,
                boleh_panggil_sayang=True
            ),
            RelationshipPhase.INTIMATE: PhaseUnlock(
                boleh_flirt=True,
                boleh_sentuhan=True,
                boleh_vulgar=True,
                boleh_intim=True,
                boleh_cium=True,
                boleh_peluk=True,
                boleh_pegang_tangan=True,
                boleh_buka_baju=True,
                boleh_panggil_sayang=True
            )
        }
        
        # Threshold untuk level
        self.phase_thresholds = {
            RelationshipPhase.STRANGER: 3,
            RelationshipPhase.FRIEND: 6,
            RelationshipPhase.CLOSE: 8,
            RelationshipPhase.ROMANTIC: 10,
            RelationshipPhase.INTIMATE: 12
        }
        
        self.last_update = time.time()
        self.created_at = time.time()
    
    def update_level(self, 
                      sayang: float, 
                      trust: float, 
                      milestones_achieved: List[str] = None) -> Tuple[int, bool]:
        """
        Update level berdasarkan sayang, trust, dan milestone.
        Returns: (new_level, level_naik)
        """
        old_level = self.level
        
        # Base level dari interaksi
        interaction_level = min(12, self.interaction_count // 10 + 1)
        
        # Bonus dari sayang
        sayang_bonus = int(sayang / 15)
        
        # Bonus dari trust
        trust_bonus = int(trust / 20)
        
        # Bonus dari milestone
        milestone_bonus = 0
        if milestones_achieved:
            milestone_bonus = len(milestones_achieved)
        
        # Hitung level
        new_level = min(12, interaction_level + sayang_bonus + trust_bonus + milestone_bonus)
        new_level = max(1, new_level)
        
        self.level = new_level
        
        # Update fase berdasarkan level
        self._update_phase()
        
        level_naik = new_level > old_level
        if level_naik:
            logger.info(f"📈 Level naik: {old_level} → {new_level} (fase: {self.phase.value})")
        
        return new_level, level_naik
    
    def _update_phase(self) -> None:
        """Update fase berdasarkan level"""
        if self.level <= 3:
            self.phase = RelationshipPhase.STRANGER
        elif self.level <= 6:
            self.phase = RelationshipPhase.FRIEND
        elif self.level <= 8:
            self.phase = RelationshipPhase.CLOSE
        elif self.level <= 10:
            self.phase = RelationshipPhase.ROMANTIC
        else:
            self.phase = RelationshipPhase.INTIMATE
    
    def get_current_unlock(self) -> PhaseUnlock:
        """Dapatkan unlock untuk fase saat ini"""
        return self.unlocks.get(self.phase, self.unlocks[RelationshipPhase.STRANGER])
    
    def get_unlock_summary(self) -> str:
        """Dapatkan ringkasan unlock untuk prompt AI"""
        unlock = self.get_current_unlock()
        unlocked = []
        locked = []
        
        for key, value in unlock.to_dict().items():
            if value:
                unlocked.append(key)
            else:
                locked.append(key)
        
        return f"""
UNLOCKED: {', '.join(unlocked) if unlocked else 'belum ada'}
LOCKED: {', '.join(locked) if locked else '-'}
"""
    
    def achieve_milestone(self, milestone_name: str) -> bool:
        """
        Catat milestone yang dicapai.
        Returns: True jika milestone baru tercapai
        """
        if milestone_name not in self.milestones:
            logger.warning(f"Milestone {milestone_name} tidak dikenal")
            return False
        
        milestone = self.milestones[milestone_name]
        if not milestone.achieved:
            milestone.achieved = True
            milestone.timestamp = time.time()
            milestone.phase = self.phase
            logger.info(f"🏆 MILESTONE: {milestone_name} achieved at phase {self.phase.value}")
            return True
        
        return False
    
    def get_milestone_status(self) -> Dict[str, bool]:
        """Dapatkan status semua milestone"""
        return {name: m.achieved for name, m in self.milestones.items()}
    
    def get_phase_description(self, phase: RelationshipPhase = None) -> str:
        """Dapatkan deskripsi fase untuk prompt AI"""
        if phase is None:
            phase = self.phase
        
        descriptions = {
            RelationshipPhase.STRANGER: """
FASE: STRANGER (BELUM KENAL)
- Nova masih malu-malu sama Mas
- Belum berani flirt, belum berani sentuhan
- Gak boleh panggil "sayang"
- Gak boleh pakai kata vulgar
- Fokus: saling kenalan, ngobrol santai
""",
            RelationshipPhase.FRIEND: """
FASE: FRIEND (SUDAH DEKAT)
- Nova mulai nyaman sama Mas
- Mulai berani flirt ringan
- Boleh pegang tangan
- Belum boleh vulgar, belum boleh intim
- Fokus: membangun kedekatan
""",
            RelationshipPhase.CLOSE: """
FASE: CLOSE (DEKAT)
- Nova udah dekat banget sama Mas
- Boleh flirt aktif, boleh peluk
- Boleh panggil "sayang"
- Belum boleh vulgar, belum boleh intim
- Fokus: deepening connection
""",
            RelationshipPhase.ROMANTIC: """
FASE: ROMANTIC (PACARAN)
- Nova dan Mas pacaran
- Boleh flirt, boleh vulgar terbatas
- Boleh cium, boleh buka baju
- Belum boleh intim (penetrasi)
- Fokus: romantic bonding
""",
            RelationshipPhase.INTIMATE: """
FASE: INTIMATE (INTIM)
- Nova udah percaya penuh sama Mas
- BEBAS VULGAR: kontol, memek, ngentot, crot
- BEBAS INTIM: foreplay, penetrasi, climax
- BEBAS semua konten
- Fokus: intimacy, bonding, pleasure
"""
        }
        
        return descriptions.get(phase, descriptions[RelationshipPhase.STRANGER])
    
    def get_phase_requirements(self, target_phase: RelationshipPhase) -> str:
        """Dapatkan requirements untuk naik ke fase tertentu"""
        requirements = {
            RelationshipPhase.FRIEND: "• Level 4+ • Minimal 10 interaksi • Ada first flirt",
            RelationshipPhase.CLOSE: "• Level 7+ • Minimal 30 interaksi • Ada first touch atau first hug",
            RelationshipPhase.ROMANTIC: "• Level 9+ • Minimal 50 interaksi • Ada first kiss",
            RelationshipPhase.INTIMATE: "• Level 11+ • Minimal 100 interaksi • Sayang > 70 • Trust > 70"
        }
        return requirements.get(target_phase, "Belum ada requirement")
    
    def can_do_action(self, action: str) -> Tuple[bool, str]:
        """
        Cek apakah Nova boleh melakukan aksi tertentu.
        Returns: (boleh, alasan)
        """
        unlock = self.get_current_unlock()
        
        action_map = {
            'flirt': unlock.boleh_flirt,
            'pegang_tangan': unlock.boleh_pegang_tangan,
            'peluk': unlock.boleh_peluk,
            'cium': unlock.boleh_cium,
            'buka_baju': unlock.boleh_buka_baju,
            'vulgar': unlock.boleh_vulgar,
            'intim': unlock.boleh_intim,
            'panggil_sayang': unlock.boleh_panggil_sayang
        }
        
        if action not in action_map:
            return True, "Boleh"
        
        if action_map[action]:
            return True, "Boleh"
        
        reasons = {
            'flirt': "Nova masih malu, Mas... belum waktunya flirt.",
            'pegang_tangan': "Nova masih malu pegang tangan... nanti dulu ya.",
            'peluk': "Nova masih malu dipeluk... belum waktunya.",
            'cium': "Nova belum siap ciuman... minta waktunya dulu ya.",
            'buka_baju': "Nova belum siap buka baju... masih malu.",
            'vulgar': "Nova masih malu ngomong kayak gitu... nanti dulu ya.",
            'intim': f"Nova masih {self.phase.value}. Belum waktunya intim.",
            'panggil_sayang': "Nova masih malu panggil sayang... nanti dulu ya."
        }
        
        return False, reasons.get(action, "Nova belum siap.")
    
    def get_progress_percentage(self) -> float:
        """Dapatkan progress menuju next level"""
        if self.level >= 12:
            return 100.0
        
        target_interactions = self.level * 10
        progress = min(100, (self.interaction_count / target_interactions) * 100)
        return progress
    
    def format_for_prompt(self) -> str:
        """Format untuk prompt AI"""
        unlock = self.get_current_unlock()
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💕 RELATIONSHIP STATUS                    ║
╠══════════════════════════════════════════════════════════════╣
║ FASE: {self.phase.value.upper()}                                  ║
║ LEVEL: {self.level}/12                                            ║
║ INTERAKSI: {self.interaction_count}                               ║
╠══════════════════════════════════════════════════════════════╣
║ UNLOCK:                                                    ║
║   Flirt: {'✅' if unlock.boleh_flirt else '❌'} | Sentuhan: {'✅' if unlock.boleh_sentuhan else '❌'}
║   Vulgar: {'✅' if unlock.boleh_vulgar else '❌'} | Intim: {'✅' if unlock.boleh_intim else '❌'}
║   Cium: {'✅' if unlock.boleh_cium else '❌'} | Peluk: {'✅' if unlock.boleh_peluk else '❌'}
║   Pegang Tangan: {'✅' if unlock.boleh_pegang_tangan else '❌'} | Panggil Sayang: {'✅' if unlock.boleh_panggil_sayang else '❌'}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def to_dict(self) -> Dict:
        return {
            'phase': self.phase.value,
            'level': self.level,
            'interaction_count': self.interaction_count,
            'milestones': {name: m.achieved for name, m in self.milestones.items()},
            'created_at': self.created_at,
            'last_update': self.last_update
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load dari dict"""
        self.phase = RelationshipPhase(data.get('phase', 'stranger'))
        self.level = data.get('level', 1)
        self.interaction_count = data.get('interaction_count', 0)
        
        milestones_data = data.get('milestones', {})
        for name, achieved in milestones_data.items():
            if name in self.milestones:
                self.milestones[name].achieved = achieved
        
        self.created_at = data.get('created_at', time.time())
        self.last_update = data.get('last_update', time.time())


# =============================================================================
# SINGLETON
# =============================================================================

_relationship_manager: Optional['RelationshipManager'] = None


def get_relationship_manager() -> RelationshipManager:
    global _relationship_manager
    if _relationship_manager is None:
        _relationship_manager = RelationshipManager()
    return _relationship_manager


relationship_manager = get_relationship_manager()
