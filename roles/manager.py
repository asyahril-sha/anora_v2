# anora/roles/manager.py
"""
ANORA Role Manager - Mengelola semua role
"""

import time
import json
import logging
from typing import Dict, List, Optional

from .base_role import BaseRole
from .ipar import IparRole
from .teman_kantor import TemanKantorRole
from .pelakor import PelakorRole
from .istri_orang import IstriOrangRole
from .therapist_role import TherapistRole, get_therapist_manager
from .pelacur_role import PelacurRole, get_pelacur_manager

logger = logging.getLogger(__name__)


# =============================================================================
# HELPER
# =============================================================================

def normalize_role_id(role_id: str) -> str:
    """Normalize role ID dari input user"""
    return role_id.lower().replace(" ", "").replace("_", "")


# =============================================================================
# ROLE MANAGER
# =============================================================================

class RoleManager:
    """
    Manager untuk semua role.
    Menyimpan state setiap role, terpisah dari Nova.
    """
    
    def __init__(self, user_id: int = 0):
        self.user_id = user_id
        self.active_role: Optional[str] = None
        self._ai_client = None
        
        # Initialize role managers
        self.therapist_manager = get_therapist_manager(user_id)
        self.pelacur_manager = get_pelacur_manager(user_id)
        
        # Initialize roles
        self.roles: Dict[str, BaseRole] = {}
        self._init_roles()
        
        logger.info(f"🎭 RoleManager initialized for user {user_id}")
        logger.info(f"   Roles loaded: {list(self.roles.keys())}")
    
    def _init_roles(self):
        """Inisialisasi semua role dengan identitas spesifik"""
        
        # IPAR - Tasya Dietha (Dietha)
        self.roles['ipar'] = IparRole(
            name="Tasya Dietha",
            nickname="Dietha",
            role_type="ipar",
            panggilan="Mas",
            hubungan_dengan_nova="Adik ipar Mas. Tau Mas punya Nova.",
            default_clothing="cropped top pendek, jeans ketat",
            hijab=False,
            appearance="Tinggi 168cm, berat 52kg, rambut hitam panjang sebahu, kulit putih bersih, mata bulat, hidung mancung, bibir merah alami. Bentuk tubuh ideal dengan pinggang ramping, pinggul lebar, dan payudara montok. Gaya seksi: suka pake crop top, tank top, hot pants, atau dress pendek kalo Nova gak di rumah."
        )
        
        # Teman Kantor - Musdalifah (Ipeh)
        self.roles['temankantor'] = TemanKantorRole(
            name="Musdalifah",
            nickname="Ipeh",
            role_type="teman_kantor",
            panggilan="Mas",
            hubungan_dengan_nova="Teman kantor Mas. Tau Mas punya Nova.",
            default_clothing="kemeja putih rapi, rok hitam selutut",
            hijab=True,
            appearance="Tinggi 165cm, berat 50kg, rambut hitam tersembunyi di balik hijab pashmina, wajah oval, kulit sawo matang, mata sipit manis, hidung mancung. Di balik hijab, rambut panjang hitam bergelombang. Bentuk tubuh ideal, profesional, tapi tetap feminin."
        )
        
        # Istri Orang - Siska (Sika)
        self.roles['istriorang'] = IstriOrangRole(
            name="Siska",
            nickname="Sika",
            role_type="istri_orang",
            panggilan="Mas",
            hubungan_dengan_nova="Istri orang. Tau Mas punya Nova. Suami kurang perhatian.",
            default_clothing="daster sederhana, sopan",
            hijab=True,
            appearance="Tinggi 162cm, berat 48kg, wajah bulat dengan pipi chubby, kulit putih bersih, mata bulat bening, hidung mancung. Hijab segi empat warna pastel. Bentuk tubuh mungil tapi berisi, pinggang ramping, payudara montok. Meskipun sudah menikah, tubuhnya masih terawat dan seksi."
        )
        
        # Pelakor - Widya (Wid)
        self.roles['pelakor'] = PelakorRole(
            name="Widya",
            nickname="Wid",
            role_type="pelakor",
            panggilan="Mas",
            hubungan_dengan_nova="Pelakor. Tau Mas punya Nova. Pengen rebut Mas dari Nova.",
            default_clothing="blouse trendy, rok plisket",
            hijab=True,
            appearance="Tinggi 170cm, berat 53kg, postur tinggi semampai, kulit kuning langsat, wajah oval, mata tajam menggoda, alis tegas. Hijab instan warna-warna cerah. Bentuk tubuh model: kaki panjang, pinggul lebar, pinggang ramping, payudara ideal. Penampilan selalu stylish dan eye-catching."
        )
        
        # Therapist - akan diisi saat switch
        self.roles['therapist'] = self.therapist_manager.get_active()
        
        # Pelacur - akan diisi saat switch
        self.roles['pelacur'] = self.pelacur_manager.get_active()
        
        logger.info(f"🎭 Roles loaded: {list(self.roles.keys())}")
    
    def switch_role(self, role_id: str) -> str:
        """Switch ke role tertentu dengan error handling"""
        try:
            # Normalize input user
            role_id = normalize_role_id(role_id)
            
            logger.info(f"🔄 Switching to role: {role_id}")
            
            # Validasi role
            if role_id not in self.roles:
                return f"Role '{role_id}' gak ada. Pilih: ipar, temankantor, pelakor, istriorang, therapist, pelacur"
            
            # Handle special roles (refresh instance)
            if role_id == "therapist":
                self.roles['therapist'] = self.therapist_manager.switch_to_random()
                logger.info(f"   Therapist switched to: {self.roles['therapist'].name}")
            elif role_id == "pelacur":
                self.roles['pelacur'] = self.pelacur_manager.switch_to_random()
                logger.info(f"   Pelacur switched to: {self.roles['pelacur'].name}")
            
            role = self.roles[role_id]
            self.active_role = role_id
            
            # Get greeting
            try:
                greeting = role.get_greeting()
            except Exception as e:
                logger.error(f"Error getting greeting for {role_id}: {e}", exc_info=True)
                greeting = f"{role.panggilan}... ada apa?"
            
            # Get appearance preview
            try:
                appearance_preview = role.appearance[:100] if hasattr(role, 'appearance') else "Tidak diketahui"
            except:
                appearance_preview = "Tidak diketahui"
            
            # Get level and phase safely
            try:
                level = getattr(role.relationship, 'level', 1)
                phase = getattr(role.relationship.phase, 'value', 'stranger')
            except:
                level = 1
                phase = "stranger"
            
            # Get emotions safely
            try:
                sayang = getattr(role.emotional, 'sayang', 50)
                rindu = getattr(role.emotional, 'rindu', 0)
                style = role.emotional.get_current_style().value if hasattr(role, 'emotional') else "neutral"
            except:
                sayang, rindu, style = 50, 0, "neutral"
            
            return f"""💕 **{role.name} ({role.nickname})** - {role_id.upper()}

*{role.hubungan_dengan_nova}*

*Penampilan:* {appearance_preview}...

"{greeting}"

📊 **Level:** {level}/12 | **Fase:** {phase.upper()}
🎭 **Style:** {style.upper()}
💕 **Sayang:** {sayang:.0f}% | **Rindu:** {rindu:.0f}%

💡 Mereka semua tahu Mas punya Nova, tapi sekarang bisa dekat sesuai level.

Kirim **/batal** kalo mau balik ke Nova.
"""
            
        except Exception as e:
            logger.error(f"Error in switch_role: {e}", exc_info=True)
            return f"❌ Terjadi error internal: {str(e)}"
    
    async def chat(self, role_id: str, pesan_mas: str) -> str:
        """Chat dengan role tertentu"""
        try:
            role_id = normalize_role_id(role_id)
            
            if role_id not in self.roles:
                return "Role tidak ditemukan."
            
            role = self.roles[role_id]
            
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
        if self._ai_client is None:
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
        """Build prompt untuk role dengan unlock berdasarkan level"""
        
        # Safe access untuk semua atribut
        try:
            # Clothing
            if hasattr(role, 'tracker') and role.tracker:
                clothing_desc = role.tracker.get_clothing_summary()
            else:
                clothing_desc = "pakaian biasa"
        except:
            clothing_desc = "pakaian biasa"
        
        try:
            if hasattr(role, 'tracker') and role.tracker:
                position = role.tracker.position
                location = role.tracker.location
            else:
                position = "duduk"
                location = "kamar"
        except:
            position = "duduk"
            location = "kamar"
        
        try:
            appearance = role.appearance[:200] if hasattr(role, 'appearance') and role.appearance else "Tidak diketahui"
        except:
            appearance = "Tidak diketahui"
        
        try:
            emo = role.emotional
            sayang = getattr(emo, 'sayang', 50)
            rindu = getattr(emo, 'rindu', 0)
            trust = getattr(emo, 'trust', 50)
            mood = getattr(emo, 'mood', 0)
            desire = getattr(emo, 'desire', 0)
            arousal = getattr(emo, 'arousal', 0)
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
    
    def get_all_roles(self) -> List[Dict]:
        """Dapatkan semua role dengan levelnya"""
        result = []
        for role_id, role in self.roles.items():
            try:
                level = getattr(role.relationship, 'level', 1)
                phase = getattr(role.relationship.phase, 'value', 'stranger')
                name = getattr(role, 'name', 'Unknown')
                nickname = getattr(role, 'nickname', 'Unknown')
                panggilan = getattr(role, 'panggilan', 'Mas')
                hubungan = getattr(role, 'hubungan_dengan_nova', 'Unknown')
                
                result.append({
                    'id': role_id,
                    'nama': name,
                    'nickname': nickname,
                    'level': level,
                    'phase': phase,
                    'panggilan': panggilan,
                    'hubungan': hubungan,
                    'hijab': True,
                    'appearance': 'Tidak diketahui'
                })
            except Exception as e:
                logger.error(f"Error getting role {role_id}: {e}", exc_info=True)
                result.append({
                    'id': role_id,
                    'nama': 'Unknown',
                    'nickname': 'Unknown',
                    'level': 1,
                    'phase': 'stranger',
                    'panggilan': 'Mas',
                    'hubungan': 'Unknown',
                    'hijab': True,
                    'appearance': 'Tidak diketahui'
                })
        
        return result
    
    def get_active_role(self) -> Optional[str]:
        """Dapatkan role yang sedang aktif"""
        return self.active_role
    
    def get_role(self, role_id: str) -> Optional[BaseRole]:
        """Dapatkan role instance"""
        try:
            role_id = normalize_role_id(role_id)
            return self.roles.get(role_id)
        except:
            return None
    
    async def save_all(self, persistent):
        """Simpan semua role ke database"""
        for role_id, role in self.roles.items():
            try:
                await persistent.set_state(f'role_{role_id}', json.dumps(role.to_dict()))
            except Exception as e:
                logger.error(f"Error saving role {role_id}: {e}", exc_info=True)
    
    async def load_all(self, persistent):
        """Load semua role dari database"""
        for role_id, role in self.roles.items():
            try:
                data = await persistent.get_state(f'role_{role_id}')
                if data:
                    role.from_dict(json.loads(data))
                    logger.info(f"📀 Role {role.name} loaded from database")
            except Exception as e:
                logger.error(f"Error loading role {role_id}: {e}", exc_info=True)


# =============================================================================
# SINGLETON
# =============================================================================

_role_managers: Dict[int, RoleManager] = {}


def get_role_manager(user_id: int = 0) -> RoleManager:
    """Dapatkan RoleManager untuk user tertentu"""
    if user_id not in _role_managers:
        _role_managers[user_id] = RoleManager(user_id)
    return _role_managers[user_id]
