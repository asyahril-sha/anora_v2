"""
ANORA-V2 Roleplay Integration - Nova
Menyatukan semua sistem roleplay:
- Brain (complete state memory)
- Emotional Engine (emosi driver)
- Decision Engine (weighted selection)
- Relationship Progression (5 fase)
- Conflict Engine (cemburu, kecewa)
- Stamina System (realistis)
- Intimacy System (fase intim)

100% AI Generate, NO TEMPLATE STATIS!
"""

import asyncio
import time
import random
import json
import logging
import re
from typing import Dict, Optional, Any, Tuple
from datetime import datetime

from core.emotional_engine import get_emotional_engine, EmotionalStyle
from core.decision_engine import get_decision_engine, ResponseCategory
from core.relationship import get_relationship_manager, RelationshipPhase
from core.conflict_engine import get_conflict_engine, ConflictType
from core.brain import get_anora_brain

from .ai import get_anora_roleplay_ai

logger = logging.getLogger(__name__)


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
    
    def update_recovery(self):
        now = time.time()
        elapsed_minutes = (now - self.last_recovery_check) / 60
        
        if elapsed_minutes >= 10:
            recovery_amount = int(self.recovery_rate * (elapsed_minutes / 10))
            self.nova_current = min(self.nova_max, self.nova_current + recovery_amount)
            self.mas_current = min(self.mas_max, self.mas_current + recovery_amount)
            self.last_recovery_check = now
    
    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Tuple[int, int]:
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
        
        return self.nova_current, self.mas_current
    
    def can_continue(self) -> Tuple[bool, str]:
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
    
    def to_dict(self) -> Dict:
        return {
            'nova_current': self.nova_current,
            'mas_current': self.mas_current,
            'climax_today': self.climax_today,
            'last_climax_date': self.last_climax_date
        }
    
    def from_dict(self, data: Dict):
        self.nova_current = data.get('nova_current', 100)
        self.mas_current = data.get('mas_current', 100)
        self.climax_today = data.get('climax_today', 0)
        self.last_climax_date = data.get('last_climax_date', datetime.now().date().isoformat())


# =============================================================================
# INTIMACY SESSION
# =============================================================================

class IntimacySession:
    """Mengelola sesi intim - Level 11-12"""
    
    def __init__(self, stamina: StaminaSystem):
        self.stamina = stamina
        self.is_active = False
        self.start_time = 0
        self.climax_count = 0
        self.current_phase = "build_up"
        self.current_position = "missionary"
        
        self.positions = {
            "missionary": "Mas di atas, Nova di bawah, kaki Nova terbuka lebar",
            "cowgirl": "Nova di atas, duduk di pangkuan Mas, menghadap Mas",
            "doggy": "Nova merangkak, Mas dari belakang",
            "spooning": "Berbaring miring, Mas dari belakang",
            "standing": "Berdiri, Nova menghadap tembok",
            "sitting": "Duduk, Nova di pangkuan Mas"
        }
        
        self.phases = ["build_up", "foreplay", "penetration", "climax", "aftercare"]
    
    def start(self) -> str:
        self.is_active = True
        self.start_time = time.time()
        self.climax_count = 0
        self.current_phase = "build_up"
        logger.info("🔥 Intimacy session started")
        return "💕 Memulai sesi intim..."
    
    def end(self) -> str:
        self.is_active = False
        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        logger.info(f"💤 Intimacy session ended. Duration: {minutes}m, Climax: {self.climax_count}")
        return f"💤 Sesi intim selesai. Durasi: {minutes} menit, {self.climax_count} climax."
    
    def change_position(self, position: str) -> Optional[str]:
        if position in self.positions:
            self.current_position = position
            return f"Ganti posisi jadi {position}: {self.positions[position]}"
        return None
    
    def advance_phase(self):
        current_idx = self.phases.index(self.current_phase)
        if current_idx < len(self.phases) - 1:
            self.current_phase = self.phases[current_idx + 1]
    
    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Dict:
        self.climax_count += 1
        self.stamina.record_climax(who, is_heavy)
        self.current_phase = "aftercare"
        return {
            'climax_count': self.climax_count,
            'stamina_nova': self.stamina.nova_current,
            'stamina_mas': self.stamina.mas_current
        }
    
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
- Fase: {self.current_phase}
- Posisi: {self.current_position}
- Stamina Nova: {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
- Stamina Mas: {self.stamina.mas_current}% ({self.stamina.get_mas_status()})
"""
    
    def to_dict(self) -> Dict:
        return {
            'is_active': self.is_active,
            'start_time': self.start_time,
            'climax_count': self.climax_count,
            'current_phase': self.current_phase,
            'current_position': self.current_position
        }
    
    def from_dict(self, data: Dict):
        self.is_active = data.get('is_active', False)
        self.start_time = data.get('start_time', 0)
        self.climax_count = data.get('climax_count', 0)
        self.current_phase = data.get('current_phase', 'build_up')
        self.current_position = data.get('current_position', 'missionary')


# =============================================================================
# ANORA ROLEPLAY - MAIN CLASS
# =============================================================================

class AnoraRoleplay:
    """Roleplay Nova yang fully integrated dengan semua engine"""
    
    def __init__(self):
        self.brain = get_anora_brain()
        self.ai = get_anora_roleplay_ai()
        self.emotional = get_emotional_engine()
        self.relationship = get_relationship_manager()
        self.conflict = get_conflict_engine()
        
        self.stamina = StaminaSystem()
        self.intimacy = IntimacySession(self.stamina)
        
        self.is_active = False
        self.start_time = None
        self.message_count = 0
        self.last_save = 0
        
        logger.info("🎭 AnoraRoleplay-V2 initialized")
        logger.info(f"   Phase: {self.relationship.phase.value}")
        logger.info(f"   Level: {self.relationship.level}/12")
        logger.info(f"   Style: {self.emotional.get_current_style().value}")
    
    async def init(self):
        """Inisialisasi, load dari database"""
        try:
            from memory.persistent import get_anora_persistent
            persistent = await get_anora_persistent()
            
            stamina_data = await persistent.get_state('stamina')
            if stamina_data:
                self.stamina.from_dict(json.loads(stamina_data))
            
            intimacy_data = await persistent.get_state('intimacy')
            if intimacy_data:
                self.intimacy.from_dict(json.loads(intimacy_data))
                
            emotional_data = await persistent.get_state('emotional')
            if emotional_data:
                self.emotional.from_dict(json.loads(emotional_data))
                
            relationship_data = await persistent.get_state('relationship')
            if relationship_data:
                self.relationship.from_dict(json.loads(relationship_data))
                
            conflict_data = await persistent.get_state('conflict')
            if conflict_data:
                self.conflict.from_dict(json.loads(conflict_data))
                
        except Exception as e:
            logger.warning(f"Could not load state: {e}")
        
        logger.info("✅ AnoraRoleplay-V2 ready")
    
    async def save_state(self):
        """Simpan semua state ke database"""
        try:
            from memory.persistent import get_anora_persistent
            persistent = await get_anora_persistent()
            
            await persistent.set_state('stamina', json.dumps(self.stamina.to_dict()))
            await persistent.set_state('intimacy', json.dumps(self.intimacy.to_dict()))
            await persistent.set_state('emotional', json.dumps(self.emotional.to_dict()))
            await persistent.save_relationship_state(self.relationship)
            await persistent.set_state('conflict', json.dumps(self.conflict.to_dict()))
            await persistent.save_current_state(self.brain)
            
            self.last_save = time.time()
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    async def start(self) -> str:
        """Mulai roleplay session"""
        self.is_active = True
        self.start_time = time.time()
        self.message_count = 0
        self.intimacy.is_active = False
        
        # Reset state awal
        from core.brain import LocationType, LocationDetail, Activity, Mood
        self.brain.location_type = LocationType.KOST_NOVA
        self.brain.location_detail = LocationDetail.KOST_KAMAR
        self.brain.activity_nova = Activity.SANTAl
        self.brain.activity_mas = "baru dateng"
        self.brain.clothing.hijab = True
        self.brain.clothing.top = "daster rumah motif bunga"
        self.brain.clothing.bra = True
        self.brain.clothing.cd = True
        
        loc = self.brain.get_location_data()
        
        await self.save_state()
        
        return f"""🎭 **ANORA-V2 - Mode Roleplay Aktif!**

📍 **{loc['nama']}**
{loc['deskripsi']}

👗 **Nova:** {self.brain.clothing.format_nova()}
💭 **Mood:** {self.brain.mood_nova.value}
💪 **Stamina Nova:** {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
💜 **Fase:** {self.relationship.phase.value} (Level {self.relationship.level}/12)
🎭 **Gaya:** {self.emotional.get_current_style().value}

**Yang Bisa Mas Lakuin:**
- Kirim **/statusrp** buat liat status lengkap
- Kirim **/pindah [tempat]** buat ganti lokasi
- Kirim **/intim** kalo mau mulai intim (level 11-12)
- Kirim **/batal** buat balik ke mode chat

💜 Ayo, Mas... Nova udah nunggu dari tadi."""
    
    async def stop(self) -> str:
        """Stop roleplay session"""
        self.is_active = False
        
        if self.intimacy.is_active:
            self.intimacy.end()
        
        await self.save_state()
        
        logger.info(f"Roleplay stopped after {self.message_count} messages")
        return "💜 Roleplay selesai. Kirim /roleplay kalo mau mulai lagi."
    
    async def process(self, pesan_mas: str) -> str:
        """Proses pesan Mas dalam mode roleplay"""
        if not self.is_active:
            return "Roleplay belum aktif. Kirim /roleplay dulu ya, Mas."
        
        self.message_count += 1
        pesan_lower = pesan_mas.lower()
        
        # Update dari pesan Mas
        update_result = self.brain.update_from_message(pesan_mas)
        
        # Cek apakah bisa mulai intim secara natural
        can_start, reason = self.emotional.should_start_intimacy_naturally(self.relationship.level)
        if can_start and not self.intimacy.is_active:
            self.intimacy.start()
            initiation = self.emotional.get_natural_intimacy_initiation(self.relationship.level)
            return initiation
        
        # Handle intimacy mode
        if self.intimacy.is_active:
            # Ganti posisi
            if any(k in pesan_lower for k in ['ganti posisi', 'cowgirl', 'doggy', 'missionary', 'spooning']):
                pos_name = None
                if 'cowgirl' in pesan_lower:
                    pos_name = 'cowgirl'
                elif 'doggy' in pesan_lower:
                    pos_name = 'doggy'
                elif 'missionary' in pesan_lower:
                    pos_name = 'missionary'
                elif 'spooning' in pesan_lower:
                    pos_name = 'spooning'
                
                result = self.intimacy.change_position(pos_name)
                if result:
                    return f"*Nova gerak ganti posisi*\n\n\"{result}\""
            
            # Climax
            if any(k in pesan_lower for k in ['crot', 'keluar', 'climax', 'cum']):
                is_heavy = any(k in pesan_lower for k in ['keras', 'banyak'])
                result = self.intimacy.record_climax("both", is_heavy)
                
                # Update emotional
                self.emotional.arousal = max(0, self.emotional.arousal - 40)
                self.emotional.desire = max(0, self.emotional.desire - 30)
                self.emotional.tension = 0
                
                return f"""*Gerakan makin kencang, plak plak plak*

"Ahhh!! Mas!! udah... udah climax... uhh..."

*tubuh Nova gemeteran hebat*

"Ahh... Mas... hangat banget dalemnya..."

💪 **Stamina Nova:** {self.stamina.nova_current}% | **Mas:** {self.stamina.mas_current}%
💦 **Climax hari ini:** {self.stamina.climax_today}x"""
        
        # Process with AI
        try:
            respons = await self.ai.process(pesan_mas, self.brain, self.stamina)
            respons = self._format_response(respons)
            
            # Tambah notifikasi level naik
            if update_result.get('level_up'):
                level_baru = self.relationship.level
                notifikasi = f"✨ **Level naik ke {level_baru}/12!** ✨\n\n"
                respons = notifikasi + respons
            
            # Simpan ke timeline
            self.brain.tambah_kejadian(
                kejadian=f"Nova: {respons[:50]}",
                pesan_mas=pesan_mas,
                pesan_nova=respons
            )
            
            # Save state
            await self.save_state()
            
            return respons
            
        except Exception as e:
            logger.error(f"AI process error: {e}")
            return self._fallback_response(pesan_mas)
    
    def _format_response(self, text: str) -> str:
        if not text:
            return text
        
        lines = text.split('\n')
        formatted = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('*') and line.endswith('*'):
                formatted.append(f"\n{line}")
            elif line.startswith('"') or line.startswith('“'):
                formatted.append(f"{line}")
            elif '*' in line and ('"' in line or '“' in line):
                match = re.match(r'^\*(.+?)\*\s*["“](.+?)["”]', line)
                if match:
                    formatted.append(f"\n*{match.group(1)}*")
                    formatted.append(f'"{match.group(2)}"')
                else:
                    formatted.append(f"{line}")
            else:
                formatted.append(f"{line}")
        
        result = '\n'.join(formatted)
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()
    
    def _fallback_response(self, pesan_mas: str) -> str:
        style = self.emotional.get_current_style()
        
        if style == EmotionalStyle.COLD:
            return "*Nova diem, gak liat Mas*"
        
        if style == EmotionalStyle.CLINGY:
            return "*Nova muter-muter rambut*\n\n\"Mas... aku kangen. Temenin dong.\""
        
        if style == EmotionalStyle.FLIRTY:
            return "*Nova mendekat, napas mulai berat*\n\n\"Mas... aku pengen banget sama Mas...\""
        
        return "*Nova tersenyum manis*\n\n\"Iya, Mas. Nova dengerin kok.\""
    
    async def get_status(self) -> str:
        """Dapatkan status roleplay lengkap"""
        loc = self.brain.get_location_data()
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        unlock = self.relationship.get_current_unlock()
        
        def bar(value, char="💜"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        conflict_status = self.conflict.get_conflict_summary()
        
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            duration = f"{minutes} menit {seconds} detik"
        else:
            duration = "0 menit"
        
        intimacy_status = ""
        if self.intimacy.is_active:
            intimacy_status = f"""
🔥 **SESI INTIM AKTIF**
- Fase: {self.intimacy.current_phase}
- Posisi: {self.intimacy.current_position}
- Climax: {self.intimacy.climax_count}x
"""
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                 🎭 ANORA-V2 - ROLEPLAY STATUS               ║
╠══════════════════════════════════════════════════════════════╣
║ DURASI: {duration}
║ PESAN: {self.message_count}
║ LEVEL: {self.relationship.level}/12 | FASE: {phase.value.upper()}
║ STYLE: {style.value.upper()}
╠══════════════════════════════════════════════════════════════╣
║ 📍 LOKASI: {loc['nama']}
║    Risk: {loc['risk']}% | Thrill: {loc['thrill']}%
╠══════════════════════════════════════════════════════════════╣
║ 💕 EMOSI:
║    Sayang: {bar(self.emotional.sayang)} {self.emotional.sayang:.0f}%
║    Rindu:  {bar(self.emotional.rindu, '🌙')} {self.emotional.rindu:.0f}%
║    Trust:  {bar(self.emotional.trust, '🤝')} {self.emotional.trust:.0f}%
║    Mood:   {self.emotional.mood:+.0f}
╠══════════════════════════════════════════════════════════════╣
║ 🔥 AROUSAL: {bar(self.emotional.arousal, '🔥')} {self.emotional.arousal:.0f}%
║ 💕 DESIRE:  {bar(self.emotional.desire, '💕')} {self.emotional.desire:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ ⚔️ KONFLIK: {conflict_status}
║    Cemburu: {bar(self.conflict.cemburu, '💢')} {self.conflict.cemburu:.0f}% | Kecewa: {bar(self.conflict.kecewa, '💔')} {self.conflict.kecewa:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ 🔓 UNLOCK:
║    Flirt: {'✅' if unlock.boleh_flirt else '❌'} | Vulgar: {'✅' if unlock.boleh_vulgar else '❌'}
║    Intim: {'✅' if unlock.boleh_intim else '❌'} | Cium: {'✅' if unlock.boleh_cium else '❌'}
╠══════════════════════════════════════════════════════════════╣
║ 💪 STAMINA:
║    Nova: {self.stamina.get_nova_bar()} {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
║    Mas:  {self.stamina.get_mas_bar()} {self.stamina.mas_current}% ({self.stamina.get_mas_status()})
║    Climax hari ini: {self.stamina.climax_today}x
{intimacy_status}
╠══════════════════════════════════════════════════════════════╣
║ 👗 PAKAIAN NOVA: {self.brain.clothing.format_nova()[:40]}
║ 🎭 MOOD: {self.brain.mood_nova.value}
╚══════════════════════════════════════════════════════════════╝
"""


# =============================================================================
# SINGLETON
# =============================================================================

_anora_roleplay: Optional['AnoraRoleplay'] = None


async def get_anora_roleplay() -> AnoraRoleplay:
    global _anora_roleplay
    if _anora_roleplay is None:
        _anora_roleplay = AnoraRoleplay()
        await _anora_roleplay.init()
    return _anora_roleplay


anora_roleplay = None
