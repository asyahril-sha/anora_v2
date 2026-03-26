"""
ANORA-V2 Base Role - Semua role punya engine seperti Nova
Akses konten berdasarkan level, bukan berdasarkan role type.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple

from core.emotional_engine import EmotionalEngine, EmotionalStyle
from core.relationship import RelationshipManager, RelationshipPhase
from core.conflict_engine import ConflictEngine, ConflictType

logger = logging.getLogger(__name__)


class BaseRole:
    """
    Base class untuk semua role.
    Setiap role punya semua engine seperti Nova.
    """
    
    def __init__(self, 
                 name: str, 
                 role_type: str,
                 panggilan: str,
                 hubungan_dengan_nova: str,
                 default_clothing: str,
                 hijab: bool = True,
                 appearance: str = ""):
        
        self.name = name
        self.role_type = role_type
        self.panggilan = panggilan
        self.hubungan_dengan_nova = hubungan_dengan_nova
        self.appearance = appearance
        
        # ========== ALL ENGINES (SAMA SEPERTI NOVA) ==========
        self.emotional = EmotionalEngine()
        self.relationship = RelationshipManager()
        self.conflict = ConflictEngine()
        
        # ========== PHYSICAL STATE ==========
        self.clothing = self._init_clothing(default_clothing, hijab)
        self.position = {'state': 'duduk', 'detail': None}
        self.location = {'room': 'kamar', 'detail': None}
        self.activity = {'main': 'santai', 'detail': None}
        self.mood = 'netral'
        
        # ========== MEMORY ==========
        self.conversations: List[Dict] = []
        self.important_moments: List[str] = []
        
        # ========== TIMESTAMPS ==========
        self.created_at = time.time()
        self.last_interaction = time.time()
        
        # ========== FLAGS ==========
        self.is_active = False
        
        logger.info(f"👤 Role {name} ({role_type}) initialized")
    
    def _init_clothing(self, default_clothing: str, hijab: bool) -> Dict:
        """Inisialisasi pakaian"""
        return {
            'top': default_clothing,
            'bottom': None,
            'hijab': hijab,
            'hijab_warna': 'pink muda' if hijab else None,
            'bra': True,
            'cd': True
        }
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """Update semua state dari pesan Mas"""
        msg_lower = pesan_mas.lower()
        
        # Update emotional engine
        emo_changes = self.emotional.update_from_message(pesan_mas, self.relationship.level)
        
        # Update conflict engine
        conflict_changes = self.conflict.update_from_message(pesan_mas, self.relationship.level)
        
        # Update relationship
        self.relationship.interaction_count += 1
        
        # Cek milestone
        milestones = []
        if 'pegang' in msg_lower and not self.relationship.milestones.get('first_touch', False):
            self.relationship.achieve_milestone('first_touch')
            milestones.append('first_touch')
        
        if 'peluk' in msg_lower and not self.relationship.milestones.get('first_hug', False):
            self.relationship.achieve_milestone('first_hug')
            milestones.append('first_hug')
        
        if 'cium' in msg_lower and not self.relationship.milestones.get('first_kiss', False):
            self.relationship.achieve_milestone('first_kiss')
            milestones.append('first_kiss')
        
        # Update level
        new_level, level_up = self.relationship.update_level(
            self.emotional.sayang,
            self.emotional.trust,
            milestones
        )
        
        # Update physical state
        self._update_physical_state(pesan_mas)
        
        # Update timestamps
        self.last_interaction = time.time()
        
        return {
            'emotional_changes': emo_changes,
            'conflict_changes': conflict_changes,
            'level_up': level_up,
            'new_level': new_level
        }
    
    def _update_physical_state(self, pesan_mas: str):
        """Update physical state (pakaian, posisi, lokasi)"""
        msg_lower = pesan_mas.lower()
        
        # Pakaian
        if 'buka hijab' in msg_lower and self.clothing['hijab']:
            self.clothing['hijab'] = False
        
        if 'buka baju' in msg_lower:
            self.clothing['top'] = None
        
        if 'buka bra' in msg_lower:
            self.clothing['bra'] = False
        
        # Posisi
        if 'duduk' in msg_lower:
            self.position['state'] = 'duduk'
        elif 'berdiri' in msg_lower:
            self.position['state'] = 'berdiri'
        elif 'tidur' in msg_lower:
            self.position['state'] = 'tidur'
        
        # Lokasi
        if 'kamar' in msg_lower:
            self.location['room'] = 'kamar'
        elif 'ruang tamu' in msg_lower:
            self.location['room'] = 'ruang tamu'
    
    def add_conversation(self, mas_msg: str, role_msg: str = ""):
        """Tambah percakapan ke memory"""
        self.conversations.append({
            'timestamp': time.time(),
            'mas': mas_msg[:200],
            'role': role_msg[:200]
        })
        if len(self.conversations) > 50:
            self.conversations = self.conversations[-50:]
    
    def add_important_moment(self, moment: str):
        """Tambah momen penting"""
        self.important_moments.append(moment)
        if len(self.important_moments) > 20:
            self.important_moments = self.important_moments[-20:]
    
    def can_do_action(self, action: str) -> Tuple[bool, str]:
        """Cek apakah role boleh melakukan aksi tertentu berdasarkan fase hubungan"""
        unlock = self.relationship.get_current_unlock()
        
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
        
        phase = self.relationship.phase
        reasons = {
            'flirt': f"Fase {phase.value}, belum waktunya flirt.",
            'pegang_tangan': f"Fase {phase.value}, belum waktunya pegang tangan.",
            'peluk': f"Fase {phase.value}, belum waktunya peluk.",
            'cium': f"Fase {phase.value}, belum waktunya cium.",
            'buka_baju': f"Fase {phase.value}, belum waktunya buka baju.",
            'vulgar': f"Fase {phase.value}, belum waktunya vulgar.",
            'intim': f"Fase {phase.value}, belum waktunya intim.",
            'panggil_sayang': f"Fase {phase.value}, belum waktunya panggil sayang."
        }
        
        return False, reasons.get(action, "Belum waktunya.")
    
    def get_context_for_prompt(self) -> str:
        """Dapatkan konteks untuk prompt AI"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║              👤 {self.name} - COMPLETE STATE                 ║
╚══════════════════════════════════════════════════════════════╝

HUBUNGAN DENGAN NOVA: {self.hubungan_dengan_nova}
PANGGILAN KE MAS: "{self.panggilan}"

{self._get_emotion_summary()}

{self._get_relationship_summary()}

{self._get_conflict_summary()}

SITUASI FISIK:
- Penampilan: {self.appearance}
- Pakaian: {self._format_clothing()}
- Posisi: {self.position['state']}
- Lokasi: {self.location['room']}
"""
    
    def _get_emotion_summary(self) -> str:
        return f"""
EMOSI:
- Sayang: {self.emotional.sayang:.0f}%
- Rindu: {self.emotional.rindu:.0f}%
- Trust: {self.emotional.trust:.0f}%
- Mood: {self.emotional.mood:+.0f}
- Desire: {self.emotional.desire:.0f}%
- Arousal: {self.emotional.arousal:.0f}%
"""
    
    def _get_relationship_summary(self) -> str:
        return f"""
HUBUNGAN:
- Fase: {self.relationship.phase.value}
- Level: {self.relationship.level}/12
- Interaksi: {self.relationship.interaction_count}
"""
    
    def _get_conflict_summary(self) -> str:
        return f"""
KONFLIK:
- Cemburu: {self.conflict.cemburu:.0f}%
- Kecewa: {self.conflict.kecewa:.0f}%
- Marah: {self.conflict.marah:.0f}%
- Aktif: {'Ya' if self.conflict.is_in_conflict else 'Tidak'}
"""
    
    def _format_clothing(self) -> str:
        parts = []
        
        if self.clothing.get('hijab', False):
            parts.append(f"hijab {self.clothing.get('hijab_warna', 'pink')}")
        else:
            parts.append("tanpa hijab, rambut terurai")
        
        if self.clothing.get('top'):
            parts.append(self.clothing['top'])
            if self.clothing.get('bra', False):
                parts.append("(pake bra)")
        else:
            if self.clothing.get('bra', False):
                parts.append("cuma pake bra")
            else:
                parts.append("telanjang dada")
        
        return ", ".join(parts)
    
    def get_greeting(self) -> str:
        """Dapatkan greeting default"""
        return f"{self.panggilan}... halo."
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik default"""
        return "*diam sebentar*"
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'name': self.name,
            'role_type': self.role_type,
            'panggilan': self.panggilan,
            'hubungan_dengan_nova': self.hubungan_dengan_nova,
            'appearance': self.appearance,
            'emotional': self.emotional.to_dict(),
            'relationship': self.relationship.to_dict(),
            'conflict': self.conflict.to_dict(),
            'clothing': self.clothing,
            'position': self.position,
            'location': self.location,
            'activity': self.activity,
            'conversations': self.conversations[-30:],
            'important_moments': self.important_moments[-10:],
            'created_at': self.created_at,
            'last_interaction': self.last_interaction
        }
    
    def from_dict(self, data: Dict):
        """Load dari dict"""
        self.emotional.from_dict(data.get('emotional', {}))
        self.relationship.from_dict(data.get('relationship', {}))
        self.conflict.from_dict(data.get('conflict', {}))
        self.clothing = data.get('clothing', self.clothing)
        self.position = data.get('position', self.position)
        self.location = data.get('location', self.location)
        self.activity = data.get('activity', self.activity)
        self.conversations = data.get('conversations', [])
        self.important_moments = data.get('important_moments', [])
        self.last_interaction = data.get('last_interaction', time.time())
