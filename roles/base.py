"""
ANORA-V2 Base Role - Semua role punya engine seperti Nova
DENGAN STATE TRACKER - memastikan tidak ada yang ngelantur
Akses konten berdasarkan level, bukan berdasarkan role type.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from core.emotional_engine import EmotionalEngine, EmotionalStyle
from core.relationship import RelationshipManager, RelationshipPhase
from core.conflict_engine import ConflictEngine, ConflictType
from core.state_tracker import StateTracker, IntimacyPhase, PhysicalCondition

logger = logging.getLogger(__name__)


class BaseRole:
    """
    Base class untuk semua role.
    Setiap role punya semua engine seperti Nova, termasuk State Tracker.
    """
    
    def __init__(self, 
                 name: str, 
                 nickname: str,
                 role_type: str,
                 panggilan: str,
                 hubungan_dengan_nova: str,
                 default_clothing: str,
                 hijab: bool = True,
                 appearance: str = ""):
        
        self.name = name
        self.nickname = nickname
        self.role_type = role_type
        self.panggilan = panggilan
        self.hubungan_dengan_nova = hubungan_dengan_nova
        self.appearance = appearance
        
        # ========== ALL ENGINES (SAMA SEPERTI NOVA) ==========
        self.emotional = EmotionalEngine()
        self.relationship = RelationshipManager()
        self.conflict = ConflictEngine()
        
        # ========== STATE TRACKER (BARU - WAJIB) ==========
        self.tracker = StateTracker(character_name=name)
        
        # Sync tracker dengan clothing awal
        self.tracker.clothing['hijab']['on'] = hijab
        self.tracker.clothing['hijab']['color'] = 'pink muda' if hijab else None
        self.tracker.clothing['top']['on'] = True
        self.tracker.clothing['top']['type'] = default_clothing
        self.tracker.clothing['bra']['on'] = True
        self.tracker.clothing['bra']['color'] = 'putih polos'
        self.tracker.clothing['cd']['on'] = True
        self.tracker.clothing['cd']['color'] = 'putih motif bunga'
        
        # ========== PHYSICAL STATE (SYNC DENGAN TRACKER) ==========
        self.position = "duduk"
        self.location = "kamar"
        self.activity = "santai"
        self.mood = "netral"
        
        # Sync tracker location
        self.tracker.position = self.position
        self.tracker.location = self.location
        self.tracker.location_detail = "ruangan"
        self.tracker.activity = self.activity
        
        # ========== MEMORY (SAMA SEPERTI NOVA) ==========
        self.conversations: List[Dict] = []
        self.important_moments: List[str] = []
        
        # Short-term memory (sliding window) - sync dengan tracker
        # Tracker sudah punya short_term, jadi pakai itu
        
        # Long-term memory
        self.long_term_memory: Dict[str, List] = {
            'kebiasaan_mas': [],
            'momen_penting': [],
            'janji': [],
            'rencana': []
        }
        
        # ========== ROLE-SPECIFIC MEMORY (AKAN DIOVERRIDE DI SUBCLASS) ==========
        self.role_flags: Dict[str, float] = {}
        
        # ========== TIMESTAMPS ==========
        self.created_at = time.time()
        self.last_interaction = time.time()
        
        # ========== FLAGS ==========
        self.is_active = False
        
        # Init memory awal
        self._init_memory()
        
        logger.info(f"👤 Role {self.name} ({nickname}) initialized with StateTracker")
        logger.info(f"   Phase: {self.relationship.phase.value}")
        logger.info(f"   Level: {self.relationship.level}/12")
        logger.info(f"   Style: {self.emotional.get_current_style().value}")
        logger.info(f"   Clothing: {self.tracker.get_clothing_summary()}")
    
    def _init_memory(self):
        """Init memory awal untuk role"""
        self.long_term_memory['kebiasaan_mas'].append({
            'konten': "suka kopi latte",
            'deskripsi': "Mas suka kopi latte",
            'timestamp': time.time()
        })
    
    # =========================================================================
    # UPDATE FROM MESSAGE (DENGAN STATE TRACKER)
    # =========================================================================
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """
        Update semua state dari pesan Mas.
        DENGAN STATE TRACKER - memastikan tidak ada yang ngelantur.
        """
        msg_lower = pesan_mas.lower()
        perubahan = []
        
        # ========== 1. UPDATE PAKAIAN (DENGAN STATE TRACKER) ==========
        
        # Buka Hijab (hanya jika berhijab)
        if self.tracker.clothing['hijab']['on'] and 'buka hijab' in msg_lower:
            result = self.tracker.remove_clothing('hijab', "Mas buka")
            if result['success']:
                perubahan.append(f"{self.name} buka hijab")
                self.tracker.add_to_timeline(f"{self.name} buka hijab", "rambut terurai")
        
        # Buka Baju
        if self.tracker.clothing['top']['on'] and 'buka baju' in msg_lower:
            result = self.tracker.remove_clothing('top', "Mas buka")
            if result['success']:
                perubahan.append(f"{self.name} buka baju")
                self.tracker.add_to_timeline(f"{self.name} buka baju", f"sekarang {result['remaining']}")
        
        # Buka Bra
        if self.tracker.clothing['bra']['on'] and 'buka bra' in msg_lower:
            result = self.tracker.remove_clothing('bra', "Mas buka")
            if result['success']:
                perubahan.append(f"{self.name} buka bra")
                self.tracker.add_to_timeline(f"{self.name} buka bra", f"sekarang {result['remaining']}")
        
        # Buka CD
        if self.tracker.clothing['cd']['on'] and 'buka cd' in msg_lower:
            result = self.tracker.remove_clothing('cd', "Mas buka")
            if result['success']:
                perubahan.append(f"{self.name} buka cd")
                self.tracker.add_to_timeline(f"{self.name} buka cd", f"sekarang {result['remaining']}")
        
        # ========== 2. UPDATE INTIMACY (DENGAN STATE TRACKER) ==========
        
        # Cek apakah perlu mulai intim (natural progression)
        if self.emotional.should_start_intimacy_naturally(self.relationship.level)[0] and self.tracker.intimacy_phase == IntimacyPhase.NONE:
            self.tracker.start_intimacy(self.location)
            perubahan.append(f"Memulai sesi intim - fase {self.tracker.intimacy_phase.value}")
            self.tracker.add_to_timeline(f"{self.name} memulai sesi intim", "natural progression")
        
        # Advance intimacy berdasarkan aksi
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
            is_heavy = any(k in msg_lower for k in ['keras', 'banyak', 'lama'])
            result = self.tracker.record_climax(location, is_heavy)
            if result['success']:
                perubahan.append(f"💦 Climax #{result['climax_count']}")
                self.tracker.add_to_timeline(
                    f"Climax #{result['climax_count']}",
                    f"Lokasi: {location}"
                )
                
                # Update emotional
                self.emotional.arousal = max(0, self.emotional.arousal - 40)
                self.emotional.desire = max(0, self.emotional.desire - 30)
        
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
        
        # Cek milestone
        milestones = []
        if 'pegang' in msg_lower and not self.relationship.milestones.get('first_touch', False):
            self.relationship.achieve_milestone('first_touch')
            milestones.append('first_touch')
            self._add_to_long_term_memory('momen_penting', f"Mas pegang tangan {self.name}", "first touch")
            self.tracker.add_to_timeline(f"Milestone: First Touch", f"{self.name} pertama kali dipegang tangannya")
        
        if 'peluk' in msg_lower and not self.relationship.milestones.get('first_hug', False):
            self.relationship.achieve_milestone('first_hug')
            milestones.append('first_hug')
            self._add_to_long_term_memory('momen_penting', f"Mas peluk {self.name}", "first hug")
            self.tracker.add_to_timeline(f"Milestone: First Hug", f"{self.name} pertama kali dipeluk")
        
        if 'cium' in msg_lower and not self.relationship.milestones.get('first_kiss', False):
            self.relationship.achieve_milestone('first_kiss')
            milestones.append('first_kiss')
            self._add_to_long_term_memory('momen_penting', f"Mas cium {self.name}", "first kiss")
            self.tracker.add_to_timeline(f"Milestone: First Kiss", f"{self.name} pertama kali dicium")
        
        # Update level
        new_level, level_up = self.relationship.update_level(
            self.emotional.sayang,
            self.emotional.trust,
            milestones
        )
        
        if level_up:
            perubahan.append(f"Level naik ke {new_level}!")
            self.tracker.add_to_timeline(f"Level naik ke {new_level}", f"Fase: {self.relationship.phase.value}")
        
        # ========== 6. UPDATE PHYSICAL STATE ==========
        self._update_physical_state(pesan_mas, perubahan)
        
        # ========== 7. UPDATE ROLE-SPECIFIC STATE (OVERRIDE DI SUBCLASS) ==========
        self._update_role_specific_state(pesan_mas, perubahan)
        
        # ========== 8. UPDATE TIMESTAMPS ==========
        self.last_interaction = time.time()
        
        # ========== 9. TAMBAH KE TIMELINE (VIA TRACKER) ==========
        self.tracker.add_to_timeline(
            kejadian=f"Mas: {pesan_mas[:50]}",
            detail=f"Perubahan: {', '.join(perubahan[:3]) if perubahan else 'tidak ada perubahan'}"
        )
        
        # ========== 10. SIMPAN KE CONVERSATION HISTORY ==========
        self.add_conversation(pesan_mas, "")
        
        return {
            'emotional_changes': emo_changes,
            'conflict_changes': conflict_changes,
            'level_up': level_up,
            'new_level': new_level,
            'perubahan': perubahan,
            'intimacy_phase': self.tracker.intimacy_phase.value,
            'clothing_state': self.tracker.get_clothing_summary(),
            'physical_condition': self.tracker.physical_condition.value
        }
    
    def _update_physical_state(self, pesan_mas: str, perubahan: List):
        """Update physical state (posisi, lokasi, aktivitas)"""
        msg_lower = pesan_mas.lower()
        
        # Update posisi
        if 'duduk' in msg_lower:
            self.position = "duduk"
            self.tracker.position = "duduk"
            perubahan.append("Posisi duduk")
        elif 'berdiri' in msg_lower or 'bangun' in msg_lower:
            self.position = "berdiri"
            self.tracker.position = "berdiri"
            perubahan.append("Posisi berdiri")
        elif 'tidur' in msg_lower or 'rebahan' in msg_lower:
            self.position = "tidur"
            self.tracker.position = "tidur"
            perubahan.append("Posisi tidur")
        elif 'merangkak' in msg_lower:
            self.position = "merangkak"
            self.tracker.position = "merangkak"
            perubahan.append("Posisi merangkak")
        
        # Update lokasi
        if 'kamar' in msg_lower:
            self.location = "kamar"
            self.tracker.location = "kamar"
            perubahan.append("Di kamar")
        elif 'ruang tamu' in msg_lower:
            self.location = "ruang tamu"
            self.tracker.location = "ruang tamu"
            perubahan.append("Di ruang tamu")
        elif 'dapur' in msg_lower:
            self.location = "dapur"
            self.tracker.location = "dapur"
            perubahan.append("Di dapur")
        elif 'teras' in msg_lower or 'balkon' in msg_lower:
            self.location = "teras"
            self.tracker.location = "teras"
            perubahan.append("Di teras")
        
        # Update aktivitas
        if 'makan' in msg_lower:
            self.activity = "makan"
            self.tracker.activity = "makan"
            perubahan.append("Sedang makan")
        elif 'minum' in msg_lower:
            self.activity = "minum"
            self.tracker.activity = "minum"
            perubahan.append("Sedang minum")
        elif 'mandi' in msg_lower:
            self.activity = "mandi"
            self.tracker.activity = "mandi"
            perubahan.append("Sedang mandi")
        elif 'nonton' in msg_lower:
            self.activity = "nonton"
            self.tracker.activity = "nonton"
            perubahan.append("Sedang nonton")
    
    def _update_role_specific_state(self, pesan_mas: str, perubahan: List):
        """
        Update role-specific state - OVERRIDE DI SUBCLASS
        Untuk menambahkan flag khusus seperti guilt, curiosity, dll
        """
        pass
    
    # =========================================================================
    # MEMORY METHODS (SAMA SEPERTI NOVA)
    # =========================================================================
    
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
        self.tracker.add_to_timeline("Momen Penting", moment[:100])
    
    def _add_to_short_term(self, kejadian: str, tipe: str):
        """Tambah ke short-term memory (via tracker)"""
        self.tracker.add_to_timeline(kejadian, tipe)
    
    def _add_to_long_term_memory(self, category: str, konten: str, deskripsi: str):
        """Tambah ke long-term memory permanen"""
        if category not in self.long_term_memory:
            self.long_term_memory[category] = []
        
        self.long_term_memory[category].append({
            'konten': konten,
            'deskripsi': deskripsi,
            'timestamp': time.time(),
            'level': self.relationship.level
        })
        
        if len(self.long_term_memory[category]) > 100:
            self.long_term_memory[category].pop(0)
        
        logger.info(f"📝 {self.name} long-term memory: {category} - {deskripsi[:50]}")
    
    # =========================================================================
    # CAN DO ACTION (BERDASARKAN LEVEL)
    # =========================================================================
    
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
    
    # =========================================================================
    # GREETING & CONFLICT RESPONSE (DAPAT DIOVERRIDE)
    # =========================================================================
    
    def get_greeting(self) -> str:
        """Dapatkan greeting - OVERRIDE DI SUBCLASS"""
        hour = time.localtime().tm_hour
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        return f"{self.panggilan}... {waktu}. Ada apa?"
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik - OVERRIDE DI SUBCLASS"""
        return "*diam sebentar*"
    
    # =========================================================================
    # CONTEXT FOR PROMPT (DENGAN STATE TRACKER - WAJIB)
    # =========================================================================
    
    def get_context_for_prompt(self) -> str:
        """Dapatkan konteks untuk prompt AI dengan State Tracker"""
        
        # Timeline dari tracker (WAJIB)
        timeline_context = self.tracker.get_timeline_context(10)
        
        # Emotional summary
        emo_summary = self._get_emotion_summary()
        
        # Relationship summary
        rel_summary = self.relationship.get_phase_description()
        unlock_summary = self.relationship.get_unlock_summary()
        
        # Conflict summary
        conflict_summary = self.conflict.get_conflict_response_guideline()
        
        return f"""
{timeline_context}

═══════════════════════════════════════════════════════════════
IDENTITAS & PENAMPILAN:
═══════════════════════════════════════════════════════════════
Nama: {self.name} ({self.nickname})
Panggilan ke Mas: "{self.panggilan}"
Hubungan dengan Nova: {self.hubungan_dengan_nova}
Penampilan: {self.appearance[:200]}

═══════════════════════════════════════════════════════════════
SITUASI SAAT INI (DARI TRACKER):
═══════════════════════════════════════════════════════════════
POSISI: {self.tracker.position}
LOKASI: {self.tracker.location}
AKTIVITAS: {self.tracker.activity}

{self.tracker.get_clothing_state_for_prompt()}

{emo_summary}

{rel_summary}

{unlock_summary}

{conflict_summary}

═══════════════════════════════════════════════════════════════
PERCAKAPAN TERAKHIR:
═══════════════════════════════════════════════════════════════
{chr(10).join([f"Mas: {c['mas']}" for c in self.conversations[-5:]])}

═══════════════════════════════════════════════════════════════
⚠️ ATURAN WAJIB:
═══════════════════════════════════════════════════════════════
1. BACA TIMELINE DI ATAS! Itu 10 kejadian terakhir. WAJIB lanjutkan alur!
2. JANGAN LUPA konteks pakaian! JANGAN tiba-tiba rapi kalo baru dibuka!
3. JANGAN LUPA masih dalam intim kalo fase bukan NONE!
4. KAMU TAHU Mas punya Nova - ini mempengaruhi perasaanmu!
5. RESPON NATURAL: 2-4 kalimat, bahasa campuran Indo-Inggris-gaul
6. JANGAN PAKAI TEMPLATE! Setiap respons harus UNIK!

═══════════════════════════════════════════════════════════════
RESPON {self.name}:
"""
    
    def _get_emotion_summary(self) -> str:
        """Dapatkan ringkasan emosi"""
        def bar(value, char="💜"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💜 EMOSI {self.name.upper()} SAAT INI                 ║
╠══════════════════════════════════════════════════════════════╣
║ Sayang:  {bar(self.emotional.sayang)} {self.emotional.sayang:.0f}%
║ Rindu:   {bar(self.emotional.rindu, '🌙')} {self.emotional.rindu:.0f}%
║ Trust:   {bar(self.emotional.trust, '🤝')} {self.emotional.trust:.0f}%
║ Mood:    {self.emotional.mood:+.0f}
╠══════════════════════════════════════════════════════════════╣
║ Desire:  {bar(self.emotional.desire, '💕')} {self.emotional.desire:.0f}%
║ Arousal: {bar(self.emotional.arousal, '🔥')} {self.emotional.arousal:.0f}%
║ Tension: {bar(self.emotional.tension, '⚡')} {self.emotional.tension:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ Cemburu: {bar(self.conflict.cemburu, '💢')} {self.conflict.cemburu:.0f}%
║ Kecewa:  {bar(self.conflict.kecewa, '💔')} {self.conflict.kecewa:.0f}%
╚══════════════════════════════════════════════════════════════╝
"""
    
    # =========================================================================
    # FORMAT STATUS
    # =========================================================================
    
    def format_status(self) -> str:
        """Format status role untuk ditampilkan"""
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        unlock = self.relationship.get_current_unlock()
        
        def bar(value, char="💜"):
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
        
        # Physical condition
        condition_emoji = {
            PhysicalCondition.FRESH: "💪",
            PhysicalCondition.TIRED: "😊",
            PhysicalCondition.EXHAUSTED: "😩",
            PhysicalCondition.WEAK: "😵"
        }.get(self.tracker.physical_condition, "😐")
        
        # Role flags summary (dari subclass)
        flags_summary = self._get_flags_summary()
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    👤 {self.name} ({self.nickname})                         ║
╠══════════════════════════════════════════════════════════════╣
║ FASE: {phase.value.upper()} ({self.relationship.level}/12)
║ STYLE: {style.value.upper()}
║ HUBUNGAN: {self.hubungan_dengan_nova}
╠══════════════════════════════════════════════════════════════╣
║ EMOSI:
║   Sayang: {bar(self.emotional.sayang)} {self.emotional.sayang:.0f}%
║   Rindu:  {bar(self.emotional.rindu, '🌙')} {self.emotional.rindu:.0f}%
║   Trust:  {bar(self.emotional.trust, '🤝')} {self.emotional.trust:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ DESIRE: {bar(self.emotional.desire, '💕')} {self.emotional.desire:.0f}%
║ AROUSAL: {bar(self.emotional.arousal, '🔥')} {self.emotional.arousal:.0f}%
{intimacy_status}
╠══════════════════════════════════════════════════════════════╣
║ KONFLIK: {self.conflict.get_conflict_summary()}
╠══════════════════════════════════════════════════════════════╣
║ UNLOCK:
║   Flirt: {'✅' if unlock.boleh_flirt else '❌'} | Vulgar: {'✅' if unlock.boleh_vulgar else '❌'}
║   Intim: {'✅' if unlock.boleh_intim else '❌'} | Cium: {'✅' if unlock.boleh_cium else '❌'}
╠══════════════════════════════════════════════════════════════╣
║ 👗 PAKAIAN: {self.tracker.get_clothing_summary()[:40]}
║ 📍 LOKASI: {self.tracker.location}
║ 💪 KONDISI: {condition_emoji} {self.tracker.physical_condition.value}
{flags_summary}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def _get_flags_summary(self) -> str:
        """Dapatkan ringkasan flags - OVERRIDE DI SUBCLASS"""
        return ""
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return {
            'name': self.name,
            'nickname': self.nickname,
            'role_type': self.role_type,
            'panggilan': self.panggilan,
            'hubungan_dengan_nova': self.hubungan_dengan_nova,
            'appearance': self.appearance,
            
            # Engines
            'emotional': self.emotional.to_dict(),
            'relationship': self.relationship.to_dict(),
            'conflict': self.conflict.to_dict(),
            
            # State Tracker
            'tracker': self.tracker.to_dict(),
            
            # Memory
            'conversations': self.conversations[-30:],
            'important_moments': self.important_moments[-10:],
            'long_term_memory': self.long_term_memory,
            'role_flags': self.role_flags,
            
            # Timestamps
            'created_at': self.created_at,
            'last_interaction': self.last_interaction
        }
    
    def from_dict(self, data: Dict):
        """Load dari dict"""
        # Engines
        self.emotional.from_dict(data.get('emotional', {}))
        self.relationship.from_dict(data.get('relationship', {}))
        self.conflict.from_dict(data.get('conflict', {}))
        
        # State Tracker
        if 'tracker' in data:
            self.tracker.from_dict(data['tracker'])
        
        # Memory
        self.conversations = data.get('conversations', [])
        self.important_moments = data.get('important_moments', [])
        self.long_term_memory = data.get('long_term_memory', self.long_term_memory)
        self.role_flags = data.get('role_flags', {})
        
        # Timestamps
        self.last_interaction = data.get('last_interaction', time.time())
        
        logger.info(f"📀 Role {self.name} loaded from database")
