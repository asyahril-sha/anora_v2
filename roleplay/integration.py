"""
ANORA-V2 Roleplay Integration - FIXED
Tujuan fix:
- Load state konsisten dari DB (tabel khusus + KV)
- Save state konsisten (tidak mismatch key)
- Persist tracker (timeline, clothing, intimacy phase, dll) via save_tracker_state/load_tracker_state
- Kurangi risiko state hilang saat restart

Catatan:
- Respons dinetralkan agar aman, tapi flow aplikasi dan penyimpanan state tetap ada.
"""

import time
import json
import logging
import re
from typing import Dict, Optional, Tuple
from datetime import datetime

from core.emotional_engine import get_emotional_engine
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

    def can_continue(self) -> Tuple[bool, str]:
        self.update_recovery()

        if self.nova_current <= self.exhausted_threshold:
            return False, "Nova sudah lelah, istirahat dulu ya."
        if self.mas_current <= self.exhausted_threshold:
            return False, "Mas sudah lelah, istirahat dulu ya."
        if self.nova_current <= self.tired_threshold:
            return True, "Nova mulai lelah, tapi masih bisa pelan-pelan."
        return True, "Siap lanjut"

    def get_nova_status(self) -> str:
        self.update_recovery()
        if self.nova_current >= 80:
            return "Prima"
        if self.nova_current >= 60:
            return "Cukup"
        if self.nova_current >= 40:
            return "Agak lelah"
        if self.nova_current >= 20:
            return "Lelah"
        return "Kehabisan tenaga"

    def get_mas_status(self) -> str:
        self.update_recovery()
        if self.mas_current >= 80:
            return "Prima"
        if self.mas_current >= 60:
            return "Cukup"
        if self.mas_current >= 40:
            return "Agak lelah"
        if self.mas_current >= 20:
            return "Lelah"
        return "Kehabisan tenaga"

    def get_nova_bar(self) -> str:
        filled = int(self.nova_current / 10)
        return "█" * filled + "░" * (10 - filled)

    def get_mas_bar(self) -> str:
        filled = int(self.mas_current / 10)
        return "█" * filled + "░" * (10 - filled)

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
# INTIMACY SESSION (NETRAL / PLACEHOLDER)
# =============================================================================

class IntimacySession:
    """
    Mengelola sesi intim.
    NOTE: Isi respons dinetralkan. Logika penyimpanan state tetap ada.
    """

    def __init__(self, stamina: StaminaSystem):
        self.stamina = stamina
        self.is_active = False
        self.start_time = 0
        self.climax_count = 0
        self.current_phase = "build_up"
        self.current_position = "missionary"

        self.positions = {
            "missionary": "Posisi 1",
            "cowgirl": "Posisi 2",
            "doggy": "Posisi 3",
            "spooning": "Posisi 4",
            "standing": "Posisi 5",
            "sitting": "Posisi 6",
        }

        self.phases = ["build_up", "foreplay", "penetration", "climax", "aftercare"]

    def start(self) -> str:
        self.is_active = True
        self.start_time = time.time()
        self.climax_count = 0
        self.current_phase = "build_up"
        logger.info("🔥 Intimacy session started")
        return "Memulai sesi..."

    def end(self) -> str:
        self.is_active = False
        duration = int(time.time() - self.start_time) if self.start_time else 0
        minutes = duration // 60
        logger.info(f"💤 Intimacy session ended. Duration: {minutes}m, Climax: {self.climax_count}")
        return f"Sesi selesai. Durasi: {minutes} menit."

    def change_position(self, position: str) -> Optional[str]:
        if position and position in self.positions:
            self.current_position = position
            return f"Ganti posisi jadi {position}: {self.positions[position]}"
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
# ANORA ROLEPLAY - MAIN CLASS
# =============================================================================

class AnoraRoleplay:
    """Roleplay Nova yang integrated dengan engine dan persistence"""

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
        """
        FIX: Load state dari DB dengan cara yang konsisten.
        - emotional/relationship/conflict/complete/tracker: dari tabel khusus (persistent.py)
        - stamina/intimacy: dari KV (anora_state_v2)
        """
        try:
            from memory.persistent import get_anora_persistent
            persistent = await get_anora_persistent()

            # Load via tabel khusus (konsisten)
            await persistent.load_complete_state(self.brain)
            await persistent.load_emotional_state(self.emotional)
            await persistent.load_relationship_state(self.relationship)
            await persistent.load_conflict_state(self.conflict)

            # Load tracker jika method tersedia (kamu perlu patch persistent.py)
            if hasattr(persistent, "load_tracker_state"):
                await persistent.load_tracker_state(self.brain)

            # Load stamina + intimacy via KV
            stamina_data = await persistent.get_state("stamina")
            if stamina_data:
                self.stamina.from_dict(json.loads(stamina_data))

            intimacy_data = await persistent.get_state("intimacy")
            if intimacy_data:
                self.intimacy.from_dict(json.loads(intimacy_data))

            # Sync wrapper setelah load
            try:
                self.brain._sync_all()
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"Could not load roleplay state: {e}")

        logger.info("✅ AnoraRoleplay-V2 ready")

    async def save_state(self):
        """
        FIX: Save state konsisten:
        - stamina/intimacy: KV
        - emotional/relationship/conflict/complete/current: tabel khusus
        - tracker: KV (via save_tracker_state) jika tersedia
        """
        try:
            from memory.persistent import get_anora_persistent
            persistent = await get_anora_persistent()

            # KV
            await persistent.set_state("stamina", json.dumps(self.stamina.to_dict(), ensure_ascii=False))
            await persistent.set_state("intimacy", json.dumps(self.intimacy.to_dict(), ensure_ascii=False))

            # Tabel khusus
            await persistent.save_emotional_state(self.emotional)
            await persistent.save_relationship_state(self.relationship)
            await persistent.save_conflict_state(self.conflict)

            await persistent.save_complete_state(self.brain)
            await persistent.save_current_state(self.brain)

            # Tracker (butuh patch persistent.py)
            if hasattr(persistent, "save_tracker_state"):
                await persistent.save_tracker_state(self.brain)

            self.last_save = time.time()

        except Exception as e:
            logger.error(f"Error saving roleplay state: {e}")

    async def start(self) -> str:
        """Mulai roleplay session (reset session state)"""
        self.is_active = True
        self.start_time = time.time()
        self.message_count = 0
        self.intimacy.is_active = False

        # Reset minimal state awal (sesuai desain kamu)
        from core.brain import LocationType, LocationDetail, Activity, Mood

        self.brain.location_type = LocationType.KOST_NOVA
        self.brain.location_detail = LocationDetail.KOST_KAMAR
        self.brain.activity_nova = Activity.SANTAl
        self.brain.activity_mas = "baru datang"
        self.brain.mood_mas = Mood.NETRAL

        loc = self.brain.get_location_data()

        # Simpan segera
        await self.save_state()

        return (
            f"""🎭 **ANORA-V2 - Mode Roleplay Aktif!**

📍 **{loc['nama']}**
{loc['deskripsi']}

👗 **Nova:** {self.brain.clothing.format_nova()}
💜 **Fase:** {self.relationship.phase.value} (Level {self.relationship.level}/12)
🎭 **Gaya:** {self.emotional.get_current_style().value}
"""
        ).strip()

    async def stop(self) -> str:
        """Stop roleplay session"""
        self.is_active = False

        if self.intimacy.is_active:
            self.intimacy.end()

        await self.save_state()
        logger.info(f"Roleplay stopped after {self.message_count} messages")
        return "💜 Roleplay selesai. Kirim /roleplay kalau mau mulai lagi."

    async def process(self, pesan_mas: str) -> str:
        """Proses pesan Mas dalam mode roleplay"""
        if not self.is_active:
            return "Roleplay belum aktif. Kirim /roleplay dulu ya."

        self.message_count += 1
        pesan_lower = (pesan_mas or "").lower().strip()

        # Update brain dari pesan
        update_result = self.brain.update_from_message(pesan_mas)

        # Jika intimacy aktif: handle basic commands (netral)
        if self.intimacy.is_active:
            if any(k in pesan_lower for k in ["cowgirl", "doggy", "missionary", "spooning", "standing", "sitting"]):
                pos_name = None
                for k in ["cowgirl", "doggy", "missionary", "spooning", "standing", "sitting"]:
                    if k in pesan_lower:
                        pos_name = k
                        break
                result = self.intimacy.change_position(pos_name)
                if result:
                    await self.save_state()
                    return f"*Nova menyesuaikan posisi*\n\n\"{result}\""

            if any(k in pesan_lower for k in ["climax", "selesai", "cukup"]):
                is_heavy = any(k in pesan_lower for k in ["keras", "banyak"])
                self.intimacy.record_climax("both", is_heavy)

                # update emosi setelah event
                self.emotional.arousal = max(0, self.emotional.arousal - 40)
                self.emotional.desire = max(0, self.emotional.desire - 30)
                self.emotional.tension = 0

                await self.save_state()
                return (
                    "*Nova menarik napas, lalu menenangkan diri*\n\n"
                    f"💪 **Stamina Nova:** {self.stamina.nova_current}% | **Mas:** {self.stamina.mas_current}%
"
                    f"🧾 **Catatan hari ini:** {self.stamina.climax_today}x"
                )

        # Proses dengan AI
        try:
            respons = await self.ai.process(pesan_mas, self.brain, self.stamina)
            respons = self._format_response(respons)

            # Notifikasi level naik (kalau ada)
            if update_result.get("level_up"):
                level_baru = self.relationship.level
                respons = f"✨ **Level naik ke {level_baru}/12!** ✨
\n" + respons

            # Simpan ke timeline
            self.brain.tambah_kejadian(
                kejadian=f"Nova: {respons[:50]}",
                pesan_mas=pesan_mas,
                pesan_nova=respons,
            )

            await self.save_state()
            return respons

        except Exception as e:
            logger.error(f"AI process error: {e}")
            await self.save_state()
            return self._fallback_response()

    def _format_response(self, text: str) -> str:
        if not text:
            return text

        lines = text.split("\n")
        formatted = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("*") and line.endswith("*"):
                formatted.append(f"\n{line}")
            elif line.startswith('"') or line.startswith("“"):
                formatted.append(line)
            elif "*" in line and ('"' in line or "“" in line):
                match = re.match(r"^\*(.+?)\*\s*[\"“](.+?)[\"”]$", line)
                if match:
                    formatted.append(f"\n*{match.group(1)}*")
                    formatted.append(f"\"{match.group(2)}\"")
                else:
                    formatted.append(line)
            else:
                formatted.append(line)

        result = "\n".join(formatted)
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result.strip()

    def _fallback_response(self) -> str:
        style = self.emotional.get_current_style().value.lower()
        if style == "cold":
            return "*Nova diam sebentar*"
        if style == "clingy":
            return "*Nova mendekat*\n\n\"Mas... temenin Nova ya.\""
        if style == "flirty":
            return "*Nova tersenyum*\n\n\"Mas... Nova di sini.\""
        return "*Nova tersenyum manis*\n\n\"Iya, Mas. Nova dengerin kok.\""

    async def get_status(self) -> str:
        loc = self.brain.get_location_data()
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
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
            intimacy_status = (
                "\n🔥 **SESI AKTIF**
"
                f"- Fase: {self.intimacy.current_phase}\n"
                f"- Posisi: {self.intimacy.current_position}\n"
                f"- Climax: {self.intimacy.climax_count}x\n"
            )

        return (
            "╔══════════════════════════════════════════════════════════════╗
"
            "║ 🎭 ANORA-V2 - ROLEPLAY STATUS ║
"
            "╠══════════════════════════════════════════════════════════════╣
"
            f"║ DURASI: {duration}\n"
            f"║ PESAN: {self.message_count}\n"
            f"║ LEVEL: {self.relationship.level}/12 | FASE: {phase.value.upper()}\n"
            f"║ STYLE: {style.value.upper()}\n"
            "╠══════════════════════════════════════════════════════════════╣
"
            f"║ 📍 LOKASI: {loc['nama']}\n"
            f"║ Risk: {loc['risk']}% | Thrill: {loc['thrill']}%\n"
            "╠══════════════════════════════════════════════════════════════╣
"
            f"║ ⚔️ KONFLIK: {conflict_status}\n"
            "╠══════════════════════════════════════════════════════════════╣
"
            "║ 💪 STAMINA:\n"
            f"║ Nova: {self.stamina.get_nova_bar()} {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
"
            f"║ Mas:  {self.stamina.get_mas_bar()} {self.stamina.mas_current}% ({self.stamina.get_mas_status()})
"
            f"║ Catatan hari ini: {self.stamina.climax_today}x\n"
            f"{intimacy_status}"
            "╚══════════════════════════════════════════════════════════════╝
"
        )


# =============================================================================
# SINGLETON
# =============================================================================

_anora_roleplay: Optional["AnoraRoleplay"] = None

async def get_anora_roleplay() -> AnoraRoleplay:
    global _anora_roleplay
    if _anora_roleplay is None:
        _anora_roleplay = AnoraRoleplay()
        await _anora_roleplay.init()
    return _anora_roleplay

anora_roleplay = None
