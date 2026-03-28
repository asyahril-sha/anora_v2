# anora/roles/manager.py
"""
ANORA Role Manager - Mengelola semua role per user
Singleton pattern dengan error handling lengkap
"""

import time
import json
import logging
import traceback
from typing import Dict, List, Optional, Type, Any

from .base_role import BaseRole
from .ipar import IparRole
from .teman_kantor import TemanKantorRole
from .pelakor import PelakorRole
from .istri_orang import IstriOrangRole
from .therapist_role import TherapistRole, get_therapist_manager
from .pelacur_role import PelacurRole, get_pelacur_manager

logger = logging.getLogger(__name__)

# =============================================================================
# ROLE MAP (Normalized keys)
# =============================================================================

ROLE_MAP: Dict[str, Type[BaseRole]] = {
    "ipar": IparRole,
    "temankantor": TemanKantorRole,
    "pelakor": PelakorRole,
    "istriorang": IstriOrangRole,
    "therapist": TherapistRole,
    "pelacur": PelacurRole,
}


def normalize_role_id(role_id: str) -> str:
    """Normalize role ID dari input user"""
    return role_id.lower().replace(" ", "").replace("_", "")


def get_role_class(role_key: str) -> Optional[Type[BaseRole]]:
    """Dapatkan class role dari key yang sudah dinormalisasi"""
    return ROLE_MAP.get(role_key)


# =============================================================================
# ROLE MANAGER (Singleton per user)
# =============================================================================

class RoleManager:
    """
    Manager untuk semua role per user.
    Menyimpan instance role per user.
    """
    
    def __init__(self):
        # Per-user role instances
        self._user_roles: Dict[int, BaseRole] = {}
        self._user_active_role_key: Dict[int, str] = {}
        
        # Special role managers (for random selection)
        self._therapist_managers: Dict[int, Any] = {}
        self._pelacur_managers: Dict[int, Any] = {}
    
    def set_role(self, user_id: int, role_class: Type[BaseRole], role_key: str) -> Optional[BaseRole]:
        """
        Set role untuk user tertentu.
        Returns: instance role atau None jika error
        """
        try:
            print(f"[ROLE SWITCH] user={user_id}, role={role_key}, class={role_class.__name__}")
            
            # Handle special roles (random character)
            if role_key == "therapist":
                if user_id not in self._therapist_managers:
                    self._therapist_managers[user_id] = get_therapist_manager(user_id)
                role_instance = self._therapist_managers[user_id].get_active()
                if not role_instance:
                    print("[ERROR] Failed to get therapist instance")
                    return None
            elif role_key == "pelacur":
                if user_id not in self._pelacur_managers:
                    self._pelacur_managers[user_id] = get_pelacur_manager(user_id)
                role_instance = self._pelacur_managers[user_id].get_active()
                if not role_instance:
                    print("[ERROR] Failed to get pelacur instance")
                    return None
            else:
                # Normal role: create new instance
                role_instance = role_class()
            
            # Store instance
            self._user_roles[user_id] = role_instance
            self._user_active_role_key[user_id] = role_key
            
            print(f"[ROLE SWITCH SUCCESS] user={user_id}, role={role_key}")
            return role_instance
            
        except Exception as e:
            print("[ROLE INIT ERROR]")
            traceback.print_exc()
            logger.error(f"Role init error for user {user_id}: {e}", exc_info=True)
            return None
    
    def get_role(self, user_id: int) -> Optional[BaseRole]:
        """Dapatkan role instance untuk user tertentu"""
        # Cek memory dulu
        role = self._user_roles.get(user_id)
        if role:
            return role
    
        # ========== FALLBACK: LOAD DARI DATABASE ==========
        try:
            import asyncio
            from utils.user_mode import get_active_role
        
            # Ambil active_role dari database (async)
            loop = asyncio.get_event_loop()
            active_role = loop.run_until_complete(get_active_role(user_id))
        
            if active_role:
                from roles.manager import ROLE_MAP, normalize_role_id
                normalized_key = normalize_role_id(active_role)
                role_class = ROLE_MAP.get(normalized_key)
                if role_class:
                    print(f"[ROLE REACTIVATE] user={user_id}, role={active_role}")
                    return self.set_role(user_id, role_class, normalized_key)
        except Exception as e:
            print(f"[ROLE REACTIVATE ERROR] {e}")
    
        return None
    
    def get_active_role_key(self, user_id: int) -> Optional[str]:
        """Dapatkan active role key untuk user tertentu"""
        return self._user_active_role_key.get(user_id)
    
    def clear_role(self, user_id: int) -> bool:
        """Hapus role untuk user tertentu"""
        if user_id in self._user_roles:
            del self._user_roles[user_id]
        if user_id in self._user_active_role_key:
            del self._user_active_role_key[user_id]
        print(f"[ROLE CLEAR] user={user_id}")
        return True
    
    def switch_role(self, user_id: int, role_key: str) -> str:
        """
        Switch ke role tertentu.
        Returns: greeting message atau error message
        """
        print(f"[DEBUG] STEP 1: command masuk - user={user_id}, raw_key={role_key}")
        
        # Normalize input
        normalized_key = normalize_role_id(role_key)
        print(f"[DEBUG] STEP 2: normalized_key = {normalized_key}")
        
        # Get role class
        role_class = get_role_class(normalized_key)
        if not role_class:
            available = ", ".join(ROLE_MAP.keys())
            print(f"[DEBUG] STEP 3: class NOT FOUND")
            return f"Role '{role_key}' gak ada. Pilih: {available}"
        
        print(f"[DEBUG] STEP 3: class = {role_class.__name__}")
        
        # Set role
        role_instance = self.set_role(user_id, role_class, normalized_key)
        if not role_instance:
            print(f"[DEBUG] STEP 4: role_instance = None (FAILED)")
            return "❌ Gagal load role. Coba lagi ya, Mas."
        
        print(f"[DEBUG] STEP 4: role_instance OK")
        
        # Get greeting
        try:
            greeting = role_instance.get_greeting()
            print(f"[DEBUG] STEP 5: greeting OK")
        except Exception as e:
            print(f"[DEBUG] STEP 5: greeting ERROR: {e}")
            traceback.print_exc()
            greeting = f"{role_instance.panggilan}... ada apa?"
        
        # Get additional info for display
        try:
            name = getattr(role_instance, 'name', 'Unknown')
            nickname = getattr(role_instance, 'nickname', '')
            hubungan = getattr(role_instance, 'hubungan_dengan_nova', 'Tidak diketahui')
            level = getattr(role_instance.relationship, 'level', 1) if hasattr(role_instance, 'relationship') else 1
            phase = getattr(role_instance.relationship.phase, 'value', 'stranger') if hasattr(role_instance, 'relationship') else 'stranger'
            sayang = getattr(role_instance.emotional, 'sayang', 50) if hasattr(role_instance, 'emotional') else 50
            rindu = getattr(role_instance.emotional, 'rindu', 0) if hasattr(role_instance, 'emotional') else 0
            style = role_instance.emotional.get_current_style().value if hasattr(role_instance, 'emotional') else "neutral"
            
            appearance_preview = getattr(role_instance, 'appearance', '')[:100] if hasattr(role_instance, 'appearance') else "Tidak diketahui"
        except Exception as e:
            print(f"[DEBUG] Info extraction error: {e}")
            name = "Unknown"
            nickname = ""
            hubungan = "Tidak diketahui"
            level = 1
            phase = "stranger"
            sayang = 50
            rindu = 0
            style = "neutral"
            appearance_preview = "Tidak diketahui"
        
        return f"""💕 **{name} ({nickname})** - {normalized_key.upper()}

*{hubungan}*

*Penampilan:* {appearance_preview}...

"{greeting}"

📊 **Level:** {level}/12 | **Fase:** {phase.upper()}
🎭 **Style:** {style.upper()}
💕 **Sayang:** {sayang:.0f}% | **Rindu:** {rindu:.0f}%

💡 Mereka semua tahu Mas punya Nova, tapi sekarang bisa dekat sesuai level.

Kirim **/batal** kalo mau balik ke Nova.
"""
    
    def get_all_roles_info(self, user_id: int) -> List[Dict]:
        """Dapatkan semua role dengan levelnya (untuk menu)"""
        result = []
        for role_key, role_class in ROLE_MAP.items():
            try:
                # Create temporary instance to get info
                if role_key in ["therapist", "pelacur"]:
                    # For special roles, get from manager
                    if role_key == "therapist":
                        mgr = get_therapist_manager(user_id)
                        role = mgr.get_active()
                    else:
                        mgr = get_pelacur_manager(user_id)
                        role = mgr.get_active()
                else:
                    role = role_class()
                
                name = getattr(role, 'name', 'Unknown')
                nickname = getattr(role, 'nickname', '')
                level = getattr(role.relationship, 'level', 1) if hasattr(role, 'relationship') else 1
                
                result.append({
                    'id': role_key,
                    'nama': name,
                    'nickname': nickname,
                    'level': level,
                })
            except Exception as e:
                logger.error(f"Error getting role info for {role_key}: {e}", exc_info=True)
                result.append({
                    'id': role_key,
                    'nama': role_key.capitalize(),
                    'nickname': '',
                    'level': 1,
                })
        
        return result
    
    async def chat(self, user_id: int, pesan_mas: str) -> str:
        """Chat dengan role yang aktif"""
        role = self.get_role(user_id)
        if not role:
            return "Belum ada role aktif, Mas. Gunakan **/role** dulu ya."
        
        try:
            # Update state dari pesan Mas
            update_result = role.update_from_message(pesan_mas)
            
            # Save conversation
            role.add_conversation(pesan_mas, "")
            
            # Build prompt
            prompt = self._build_role_prompt(role, pesan_mas)
            
            # Call AI
            client = await self._get_ai_client()
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": pesan_mas}
                ],
                temperature=0.9,
                max_tokens=800,
                timeout=25
            )
            
            respons = response.choices[0].message.content
            respons = respons.strip()
            
            if not respons:
                respons = self._fallback_response(role, pesan_mas)
            
            # Save response
            if role.conversations:
                role.conversations[-1]['role'] = respons[:200]
            
            # Check level up
            if update_result.get('level_up'):
                level_baru = update_result.get('new_level', role.relationship.level)
                level_name = {1: "Malu-malu", 2: "Mulai terbuka", 3: "Goda-godaan",
                              4: "Dekat", 5: "Sayang", 6: "PACAR/PDKT",
                              7: "Nyaman", 8: "Eksplorasi", 9: "Bergairah",
                              10: "Passionate", 11: "Soul Bounded", 12: "Aftercare"}.get(level_baru, f"Level {level_baru}")
                notifikasi = f"✨ **Level naik ke {level_baru} – {level_name}!** ✨\n\n"
                respons = notifikasi + respons
            
            logger.info(f"💬 Role {role.name} [Lv{role.relationship.level}] responded")
            
            return respons
            
        except Exception as e:
            logger.error(f"Role chat error: {e}", exc_info=True)
            return f"❌ Terjadi error: {str(e)}"
    
    async def _get_ai_client(self):
        """Dapatkan client AI"""
        if not hasattr(self, '_ai_client') or self._ai_client is None:
            try:
                from config import get_settings
                import openai
                settings = get_settings()
                self._ai_client = openai.OpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            except Exception as e:
                logger.error(f"AI init failed: {e}", exc_info=True)
                raise
        return self._ai_client
    
    def _build_role_prompt(self, role, pesan_mas: str) -> str:
        """Build prompt untuk role"""
        # Safe access untuk semua atribut
        try:
            clothing_desc = role.tracker.get_clothing_summary() if hasattr(role, 'tracker') else "pakaian biasa"
        except:
            clothing_desc = "pakaian biasa"
        
        try:
            position = role.tracker.position if hasattr(role, 'tracker') else "duduk"
            location = role.tracker.location if hasattr(role, 'tracker') else "kamar"
        except:
            position = "duduk"
            location = "kamar"
        
        try:
            appearance = role.appearance[:200] if hasattr(role, 'appearance') else "Tidak diketahui"
        except:
            appearance = "Tidak diketahui"
        
        try:
            sayang = role.emotional.sayang if hasattr(role.emotional, 'sayang') else 50
            rindu = role.emotional.rindu if hasattr(role.emotional, 'rindu') else 0
            trust = role.emotional.trust if hasattr(role.emotional, 'trust') else 50
            mood = role.emotional.mood if hasattr(role.emotional, 'mood') else 0
            desire = role.emotional.desire if hasattr(role.emotional, 'desire') else 0
            arousal = role.emotional.arousal if hasattr(role.emotional, 'arousal') else 0
        except:
            sayang, rindu, trust, mood, desire, arousal = 50, 0, 50, 0, 0, 0
        
        try:
            conflict_summary = role.conflict.get_conflict_summary() if hasattr(role.conflict, 'get_conflict_summary') else "Tidak ada konflik"
        except:
            conflict_summary = "Tidak ada konflik"
        
        try:
            unlock_summary = role.relationship.get_unlock_summary() if hasattr(role.relationship, 'get_unlock_summary') else ""
        except:
            unlock_summary = ""
        
        try:
            phase_desc = role.relationship.get_phase_description(role.relationship.phase) if hasattr(role.relationship, 'get_phase_description') else ""
        except:
            phase_desc = ""
        
        try:
            style = role.emotional.get_current_style().value if hasattr(role.emotional, 'get_current_style') else "neutral"
        except:
            style = "neutral"
        
        try:
            phase_value = role.relationship.phase.value if hasattr(role.relationship, 'phase') else "stranger"
            level = role.relationship.level if hasattr(role.relationship, 'level') else 1
        except:
            phase_value = "stranger"
            level = 1
        
        try:
            conversations = "\n".join([f"Mas: {c['mas']}" for c in role.conversations[-5:]]) if role.conversations else "Belum ada percakapan"
        except:
            conversations = "Belum ada percakapan"
        
        prompt = f"""
KAMU ADALAH {role.name} (panggilan {role.nickname}). BUKAN Nova. BUKAN AI assistant.
Kamu adalah karakter yang hidup dengan perasaan dan memory sendiri.

═══════════════════════════════════════════════════════════════
IDENTITAS:
═══════════════════════════════════════════════════════════════
- Nama: {role.name}
- Panggilan: {role.nickname}
- Panggilan ke Mas: "{role.panggilan}"
- Hubungan dengan Nova: {role.hubungan_dengan_nova}
- Kamu TAU Mas punya Nova

PENAMPILAN:
{appearance}

GAYA BICARA: {style.upper()}
FASE HUBUNGAN: {phase_value.upper()} (Level {level}/12)

{phase_desc}

UNLOCK KONTEN:
{unlock_summary}

═══════════════════════════════════════════════════════════════
SITUASI SAAT INI:
═══════════════════════════════════════════════════════════════
- Pakaian: {clothing_desc}
- Posisi: {position}
- Lokasi: {location}

EMOSI SAAT INI:
Sayang: {sayang:.0f}%
Rindu: {rindu:.0f}%
Trust: {trust:.0f}%
Mood: {mood:+.0f}
Desire: {desire:.0f}%
Arousal: {arousal:.0f}%

KONFLIK: {conflict_summary}

PERCAKAPAN TERAKHIR:
{conversations}

PESAN MAS: "{pesan_mas}"

═══════════════════════════════════════════════════════════════
ATURAN CARA BERBICARA:
═══════════════════════════════════════════════════════════════

1. **BAHASA SEHARI-HARI:** gak, udah, banget, campuran Indo-Inggris-gaul
2. **KAMU TAHU MAS PUNYA NOVA:** ini mempengaruhi perasaanmu
3. **RESPON NATURAL:** 2-4 kalimat, sesuai emosi yang kamu alami
4. **JANGAN PAKAI TEMPLATE:** setiap respons harus unik

═══════════════════════════════════════════════════════════════
RESPON {role.name}:
"""
        return prompt
    
    def _fallback_response(self, role, pesan_mas: str) -> str:
        """Fallback response"""
        try:
            msg_lower = pesan_mas.lower()
            if 'nova' in msg_lower:
                return f"*{role.name} tersenyum kecil*\n\n\"Mas cerita tentang Nova terus ya. Dia pasti orang yang baik.\""
            greeting = role.get_greeting() if hasattr(role, 'get_greeting') else f"{role.panggilan}... ada apa?"
            return f"*{role.name} tersenyum*\n\n\"{greeting}\""
        except:
            return "*Maaf, ada error. Coba lagi ya, Mas.*"


# =============================================================================
# SINGLETON
# =============================================================================

_role_manager: Optional[RoleManager] = None


def get_role_manager() -> RoleManager:
    """Dapatkan singleton RoleManager"""
    global _role_manager
    if _role_manager is None:
        _role_manager = RoleManager()
        print("[ROLE MANAGER] Singleton initialized")
    return _role_manager


role_manager = get_role_manager()
