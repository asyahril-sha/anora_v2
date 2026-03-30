"""
ANORA-V2 Roleplay Integration - Nova
Menyatukan semua sistem roleplay:
- Brain
- Emotional Engine
- Relationship
- Conflict
- Stamina
- Intimacy

Catatan:
File ini sudah dibuat "safe" untuk copy-paste:
- Hindari multiline f-string yang sering kepotong dan bikin SyntaxError
- Semua teks panjang pakai join list atau triple quote yang tertutup rapi
"""

import asyncio
import time
import json
import logging
import re
from typing import Dict, Optional, Tuple
from datetime import datetime

from core.emotional_engine import get_emotional_engine, EmotionalStyle
from core.relationship import get_relationship_manager
from core.conflict_engine import get_conflict_engine
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

    def get_nova_bar(self) -> str:
        filled = int(self.nova_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)

    def get_mas_bar(self) -> str:
        filled = int(self.mas_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)

    def to_dict(self) -> Dict:
        return {
            "nova_current": self.nova_current,
            "mas_current": self.mas_current,
            "climax_today": self.climax_today,
            "last_climax_date": self.last_climax_date,
        }

    def from_dict(self, data: Dict):
        self.nova_current = data.get("nova_current", 100)
        self.mas_current = data.get("mas_current", 100)
        self.climax_today = data.get("climax_today", 0)
        self.last_climax_date = data.get("last_climax_date", datetime.now().date().isoformat())


# =============================================================================
# INTIMACY SESSION (minimal)
# =============================================================================
class IntimacySession:
    def __init__(self, stamina: StaminaSystem):
        self.stamina = stamina
        self.is_active = False
        self.start_time = 0
        self.climax_count = 0
        self.current_phase = "build_up"
        self.current_position = "missionary"

        self.positions = {
            "missionary": "Mas di atas, Nova di bawah",
            "cowgirl": "Nova di atas",
            "doggy": "Nova membelakangi",
            "spooning": "Berbaring miring",
            "standing": "Berdiri",
            "sitting": "Duduk",
        }

    def start(self) -> str:
        self.is_active = True
        self.start_time = time.time()
        self.climax_count = 0
        self.current_phase = "build_up"
        logger.info("🔥 Intimacy session started")
        return "💕 Memulai sesi intim..."

    def end(self) -> str:
        self.is_active = False
        duration = int(time.time() - self.start_time) if self.start_time else 0
        minutes = duration // 60
        logger.info("💤 Intimacy session ended")
        return f"💤 Sesi intim selesai. Durasi: {minutes} menit, climax: {self.climax_count}x"

    def change_position(self, position: Optional[str]) -> Optional[str]:
        if not position:
            return None
        if position in self.positions:
            self.current_position = position
            return f"Ganti posisi: {position} ({self.positions[position]})"
        return None

    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Dict:
        self.climax_count += 1
        self.stamina.record_climax(who, is_heavy)
        self.current_phase = "aftercare"
        return {
            "climax_count": self.climax_count,
            "stamina_nova": self.stamina.nova_current,
            "stamina_mas": self.stamina.mas_current,
        }

    def to_dict(self) -> Dict:
        return {
            "is_active": self.is_active,
            "start_time": self.start_time,
            "climax_count": self.climax_count,
            "current_phase": self.current_phase,
            "current_position": self.current_position,
        }

    def from_dict(self, data: Dict):
        self.is_active = data.get("is_active", False)
        self.start_time = data.get("start_time", 0)
        self.climax_count = data.get("climax_count", 0)
        self.current_phase = data.get("current_phase", "build_up")
        self.current_position = data.get("current_position", "missionary")


# =============================================================================
# ROLEPLAY MAIN
# =============================================================================
class AnoraRoleplay:
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

    async def init(self):
        """Load state from DB (optional)"""
        try:
            from memory.persistent import get_anora_persistent
            persistent = await get_anora_persistent()

            stamina_data = await persistent.get_state("stamina")
            if stamina_data:
                self.stamina.from_dict(json.loads(stamina_data))

            intimacy_data = await persistent.get_state("intimacy")
            if intimacy_data:
                self.intimacy.from_dict(json.loads(intimacy_data))
        except Exception as e:
            logger.warning(f"Could not load roleplay state: {e}")

        logger.info("✅ AnoraRoleplay-V2 ready")

    async def save_state(self):
        try:
            from memory.persistent import get_anora_persistent
            persistent = await get_anora_persistent()

            await persistent.set_state("stamina", json.dumps(self.stamina.to_dict(), ensure_ascii=False))
            await persistent.set_state("intimacy", json.dumps(self.intimacy.to_dict(), ensure_ascii=False))

            self.last_save = time.time()
        except Exception as e:
            logger.error(f"Error saving roleplay state: {e}", exc_info=True)

    async def start(self) -> str:
        self.is_active = True
        self.start_time = time.time()
        self.message_count = 0
        self.intimacy.is_active = False

        # Simpan segera
        await self.save_state()

        loc = self.brain.get_location_data()
        text = "\n".join([
            "🎭 ANORA-V2 - Mode Roleplay Aktif!",
            "",
            f"📍 {loc.get('nama','')}",
            f"{loc.get('deskripsi','')}",
            "",
            f"👗 Nova: {self.brain.clothing.format_nova() if hasattr(self.brain, 'clothing') else '-'}",
            f"💜 Fase: {self.relationship.phase.value} (Level {self.relationship.level}/12)",
            f"🎭 Gaya: {self.emotional.get_current_style().value}",
            "",
            "Kirim pesan apa aja untuk mulai.",
        ])
        return text

    async def stop(self) -> str:
        self.is_active = False
        if self.intimacy.is_active:
            self.intimacy.end()
        await self.save_state()
        return "💜 Roleplay selesai. Kirim /roleplay kalau mau mulai lagi."

    async def process(self, pesan_mas: str) -> str:
        """Proses pesan Mas dalam mode roleplay"""
        if not self.is_active:
            return "Roleplay belum aktif. Kirim /roleplay dulu ya."

        self.message_count += 1
        pesan_lower = (pesan_mas or "").lower().strip()

        # Update brain state
        try:
            self.brain.update_from_message(pesan_mas)
        except Exception as e:
            logger.warning(f"brain.update_from_message error: {e}")

        # Intimacy quick handling (safe)
        if self.intimacy.is_active:
            for k in ["cowgirl", "doggy", "missionary", "spooning", "standing", "sitting"]:
                if k in pesan_lower:
                    result = self.intimacy.change_position(k)
                    if result:
                        await self.save_state()
                        return f"*Nova menyesuaikan posisi*\n\n\"{result}\""

            if any(k in pesan_lower for k in ["climax", "selesai", "cukup"]):
                is_heavy = any(k in pesan_lower for k in ["keras", "banyak"])
                self.intimacy.record_climax("both", is_heavy)

                # Turunkan emosi sedikit
                try:
                    self.emotional.arousal = max(0, self.emotional.arousal - 40)
                    self.emotional.desire = max(0, self.emotional.desire - 30)
                    self.emotional.tension = 0
                except Exception:
                    pass

                await self.save_state()
                # INI BAGIAN YANG DULU BIKIN SYNTAX ERROR: sekarang aman pakai join
                return "\n".join([
                    "*Gerakan makin cepat*",
                    "",
                    "\"...\"",
                    "",
                    f"Stamina Nova: {self.stamina.nova_current}% | Mas: {self.stamina.mas_current}%",
                    f"Climax hari ini: {self.stamina.climax_today}x",
                ])

        # AI response
        try:
            respons = await self.ai.process(pesan_mas, self.brain, self.stamina)
            respons = self._format_response(respons)

            # notifikasi level naik, dibuat aman
            # (kalau kamu memang punya flag level_up di update brain/relationship, kamu bisa sambungin di sini)
            # contoh:
            # level_baru = self.relationship.level
            # respons = f"Level naik ke {level_baru}/12!\n\n" + respons

            await self.save_state()
            return respons

        except Exception as e:
            logger.error(f"AI process error: {e}", exc_info=True)
            return "*Nova tersenyum*\n\n\"Iya, Mas...\""

    def _format_response(self, text: str) -> str:
        if not text:
            return text

        lines = text.split("\n")
        formatted = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            formatted.append(line)

        result = "\n".join(formatted)
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result.strip()


# =============================================================================
# SINGLETON
# =============================================================================
_anora_instance = None
_lock = asyncio.Lock()

async def get_anora_roleplay():
    global _anora_instance

    if _anora_instance is None:
        async with _lock:
            if _anora_instance is None:
                _anora_instance = AnoraRoleplay()
                await _anora_instance.init()

    return _anora_instance
