"""
ANORA-V2 Role Manager - Mengelola semua role
Semua role punya akses penuh sesuai level, sama seperti Nova.
"""

import time
import json
import logging
from typing import Dict, List, Optional

from .base import BaseRole
from .ipar import IparRole
from .teman_kantor import TemanKantorRole
from .pelakor import PelakorRole
from .istri_orang import IstriOrangRole

logger = logging.getLogger(__name__)


class RoleManager:
    """
    Manager untuk semua role.
    Menyimpan state setiap role, terpisah dari Nova.
    """
    
    def __init__(self):
        self.roles: Dict[str, BaseRole] = {}
        self.active_role: Optional[str] = None
        self._ai_client = None
        
        # Inisialisasi role
        self._init_roles()
        
        logger.info("🎭 RoleManager-V2 initialized")
    
    def _init_roles(self):
        """Inisialisasi semua role dengan identitas spesifik"""
        
        # IPAR - Tasya Dietha (Dietha) - Tidak Berhijab
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
        
        # Teman Kantor - Musdalifah (Ipeh) - Berhijab
        self.roles['teman_kantor'] = TemanKantorRole(
            name="Musdalifah",
            nickname="Ipeh",
            role_type="teman_kantor",
            panggilan="Mas",
            hubungan_dengan_nova="Teman kantor Mas. Tau Mas punya Nova.",
            default_clothing="kemeja putih rapi, rok hitam selutut",
            hijab=True,
            appearance="Tinggi 165cm, berat 50kg, rambut hitam tersembunyi di balik hijab pashmina, wajah oval, kulit sawo matang, mata sipit manis, hidung mancung. Di balik hijab, rambut panjang hitam bergelombang. Bentuk tubuh ideal, profesional, tapi tetap feminin."
        )
        
        # Istri Orang - Siska (Sika) - Berhijab
        self.roles['istri_orang'] = IstriOrangRole(
            name="Siska",
            nickname="Sika",
            role_type="istri_orang",
            panggilan="Mas",
            hubungan_dengan_nova="Istri orang. Tau Mas punya Nova. Suami kurang perhatian.",
            default_clothing="daster sederhana, sopan",
            hijab=True,
            appearance="Tinggi 162cm, berat 48kg, wajah bulat dengan pipi chubby, kulit putih bersih, mata bulat bening, hidung mancung. Hijab segi empat warna pastel. Bentuk tubuh mungil tapi berisi, pinggang ramping, payudara montok. Meskipun sudah menikah, tubuhnya masih terawat dan seksi."
        )
        
        # Pelakor - Widya (Wid) - Berhijab
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
        
        logger.info(f"🎭 Roles loaded: {list(self.roles.keys())}")
    
    def switch_role(self, role_id: str) -> str:
        """Switch ke role tertentu"""
        if role_id not in self.roles:
            return f"Role '{role_id}' gak ada. Pilih: ipar, teman_kantor, pelakor, istri_orang"
        
        self.active_role = role_id
        role = self.roles[role_id]
        
        # Ambil greeting yang sesuai
        greeting = role.get_greeting()
        
        return f"""💕 **{role.name} ({role.nickname})** - {role_id.upper()}

*{role.hubungan_dengan_nova}*

*Penampilan:* {role.appearance[:100]}...

"{greeting}"

📊 **Level:** {role.relationship.level}/12 | **Fase:** {role.relationship.phase.value.upper()}
🎭 **Style:** {role.emotional.get_current_style().value.upper()}
💕 **Sayang:** {role.emotional.sayang:.0f}% | **Rindu:** {role.emotional.rindu:.0f}%

💡 Mereka semua tahu Mas punya Nova, tapi sekarang bisa dekat sesuai level.

Kirim **/batal** kalo mau balik ke Nova.
"""
    
    async def chat(self, role_id: str, pesan_mas: str) -> str:
        """Chat dengan role tertentu"""
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
        try:
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
                notifikasi = f"✨ **Level naik ke {level_baru}/12!** ✨\n\n"
                respons = notifikasi + respons
            
            logger.info(f"💬 Role {role.name} [Lv{role.relationship.level}] responded")
            
            return respons
            
        except Exception as e:
            logger.error(f"Role chat error: {e}")
            return self._fallback_response(role, pesan_mas)
    
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
                logger.error(f"AI init failed: {e}")
                raise
        return self._ai_client
    
    def _build_role_prompt(self, role, pesan_mas: str) -> str:
        """Build prompt untuk role dengan unlock berdasarkan level"""
    
        # Ambil pakaian dengan aman
        try:
            if hasattr(role, 'tracker') and role.tracker:
                clothing_desc = role.tracker.get_clothing_summary()
            elif hasattr(role, 'clothing') and isinstance(role.clothing, dict):
                # Fallback manual
                parts = []
                if role.clothing.get('hijab', False):
                    parts.append(f"hijab {role.clothing.get('hijab_warna', 'pink')}")
                else:
                    parts.append("tanpa hijab")
                if role.clothing.get('top'):
                    parts.append(role.clothing['top'])
                    if role.clothing.get('bra', False):
                        parts.append(f"(pake bra {role.clothing.get('bra_warna', 'putih')})")
                else:
                    if role.clothing.get('bra', False):
                        parts.append(f"cuma pake bra {role.clothing.get('bra_warna', 'putih')}")
                    else:
                        parts.append("telanjang dada")
                if role.clothing.get('cd', False):
                    parts.append(f"pake cd {role.clothing.get('cd_warna', 'putih')}")
                else:
                    parts.append("tanpa cd")
                clothing_desc = ", ".join(parts)
            else:
                clothing_desc = "pakaian biasa"
        except Exception as e:
            logging.error(f"Error getting clothing: {e}")
            clothing_desc = "pakaian biasa"
    
        # ========== AMBIL PENAMPILAN DENGAN AMAN ==========
    try:
        appearance = role.appearance[:200] if hasattr(role, 'appearance') and role.appearance else "Tidak diketahui"
    except:
        appearance = "Tidak diketahui"
    
    # ========== AMBIL EMOSI DENGAN AMAN ==========
    try:
        emo = role.emotional
        sayang = emo.sayang if hasattr(emo, 'sayang') else 50
        rindu = emo.rindu if hasattr(emo, 'rindu') else 0
        trust = emo.trust if hasattr(emo, 'trust') else 50
        mood = emo.mood if hasattr(emo, 'mood') else 0
        desire = emo.desire if hasattr(emo, 'desire') else 0
        arousal = emo.arousal if hasattr(emo, 'arousal') else 0
    except:
        sayang, rindu, trust, mood, desire, arousal = 50, 0, 50, 0, 0, 0
    
    # ========== AMBIL KONFLIK DENGAN AMAN ==========
    try:
        conflict_summary = role.conflict.get_conflict_summary() if hasattr(role.conflict, 'get_conflict_summary') else "Tidak ada konflik"
    except:
        conflict_summary = "Tidak ada konflik"
    
    # ========== AMBIL UNLOCK DENGAN AMAN ==========
    try:
        unlock_summary = role.relationship.get_unlock_summary() if hasattr(role.relationship, 'get_unlock_summary') else ""
    except:
        unlock_summary = ""
    
    # ========== AMBIL PHASE DESCRIPTION DENGAN AMAN ==========
    try:
        phase_desc = role.relationship.get_phase_description(role.relationship.phase) if hasattr(role.relationship, 'get_phase_description') else ""
    except:
        phase_desc = ""
    
    # ========== AMBIL CONFLICT GUIDELINE DENGAN AMAN ==========
    try:
        conflict_guideline = role.conflict.get_conflict_response_guideline() if hasattr(role.conflict, 'get_conflict_response_guideline') else ""
    except:
        conflict_guideline = ""
    
    # ========== BUILD PROMPT ==========
        
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
{role.appearance}

{self._get_style_guideline(role, style)}

{role.relationship.get_phase_description(role.relationship.phase)}

UNLOCK KONTEN (BERDASARKAN LEVEL, SAMA SEPERTI NOVA):
{role.relationship.get_unlock_summary()}

═══════════════════════════════════════════════════════════════
SITUASI SAAT INI:
═══════════════════════════════════════════════════════════════
- Pakaian: {role._format_clothing()}
- Posisi: {role.position['state']}
- Lokasi: {role.location['room']}
- Mood: {role.mood}

{role._get_emotion_summary()}

{role._get_conflict_summary()}

PERCAKAPAN TERAKHIR:
{chr(10).join([f"Mas: {c['mas']}" for c in role.conversations[-5:]])}

PESAN MAS: "{pesan_mas}"

═══════════════════════════════════════════════════════════════
ATURAN CARA BERBICARA:
═══════════════════════════════════════════════════════════════

1. **BAHASA SEHARI-HARI:** gak, udah, banget, campuran Indo-Inggris-gaul
2. **KAMU TAHU MAS PUNYA NOVA:** ini mempengaruhi perasaanmu
3. **RESPON NATURAL:** sesuai emosi yang kamu alami
4. **PANJANG RESPONS:** 2-4 kalimat
5. **JANGAN PAKAI TEMPLATE:** setiap respons harus unik
6. **KONSISTENSI:** ingat penampilan dan karakter dirimu

═══════════════════════════════════════════════════════════════
RESPON {role.name}:
"""
        return prompt
    
    def _get_style_guideline(self, role, style) -> str:
        """Dapatkan pedoman gaya bicara berdasarkan emotional style"""
        guidelines = {
            "cold": f"""
GAYA BICARA: COLD (DINGIN)
- Kamu lagi {self._get_cold_reason(role)}
- Respons: 1-2 kalimat, pendek, gak antusias
- Gak pake gesture manja
""",
            "clingy": f"""
GAYA BICARA: CLINGY (MANJA)
- Kamu kangen banget (rindu: {role.emotional.rindu:.0f}%)
- Respons: 4-6 kalimat, manja
- Banyak gesture manja
""",
            "warm": f"""
GAYA BICARA: WARM (HANGAT)
- Kamu percaya sama Mas (trust: {role.emotional.trust:.0f}%)
- Respons: 3-5 kalimat, perhatian
""",
            "flirty": f"""
GAYA BICARA: FLIRTY (MENGGODA)
- Kamu lagi horny (arousal: {role.emotional.arousal:.0f}%)
- Respons: 4-8 kalimat, menggoda
- Bisa vulgar kalo level tinggi
""",
            "neutral": """
GAYA BICARA: NEUTRAL (NORMAL)
- Kamu stabil
- Respons: 2-4 kalimat, natural
"""
        }
        return guidelines.get(style.value, guidelines["neutral"])
    
    def _get_cold_reason(self, role) -> str:
        if role.emotional.cemburu > 50:
            return f"cemburu ({role.emotional.cemburu:.0f}%)"
        if role.emotional.kecewa > 40:
            return f"kecewa ({role.emotional.kecewa:.0f}%)"
        if role.emotional.mood < -20:
            return f"bad mood ({role.emotional.mood:+.0f})"
        return "lagi gak mood"
    
    def _fallback_response(self, role, pesan_mas: str) -> str:
        """Fallback response"""
        msg_lower = pesan_mas.lower()
        
        if 'nova' in msg_lower:
            return f"*{role.name} tersenyum kecil*\n\n\"Mas cerita tentang Nova terus ya. Dia pasti orang yang baik.\""
        
        return f"*{role.name} tersenyum*\n\n\"{role.get_greeting()}\""
    
    def get_all_roles(self) -> List[Dict]:
        """Dapatkan semua role dengan levelnya"""
        return [
            {
                'id': role_id,
                'nama': role.name,
                'nickname': role.nickname,
                'level': role.relationship.level,
                'phase': role.relationship.phase.value,
                'panggilan': role.panggilan,
                'hubungan': role.hubungan_dengan_nova,
                'hijab': role.clothing.get('hijab', True),
                'appearance': role.appearance[:80] + "..."
            }
            for role_id, role in self.roles.items()
        ]
    
    def get_active_role(self) -> Optional[str]:
        """Dapatkan role yang sedang aktif"""
        return self.active_role
    
    def get_role(self, role_id: str) -> Optional[BaseRole]:
        """Dapatkan role instance"""
        return self.roles.get(role_id)
    
    async def save_all(self, persistent):
        """Simpan semua role ke database"""
        for role_id, role in self.roles.items():
            await persistent.set_state(f'role_v2_{role_id}', json.dumps(role.to_dict()))
    
    async def load_all(self, persistent):
        """Load semua role dari database"""
        for role_id, role in self.roles.items():
            data = await persistent.get_state(f'role_v2_{role_id}')
            if data:
                try:
                    role.from_dict(json.loads(data))
                    logger.info(f"📀 Role {role.name} loaded from database")
                except Exception as e:
                    logger.error(f"Error loading role {role_id}: {e}")


# =============================================================================
# SINGLETON
# =============================================================================

_role_manager: Optional['RoleManager'] = None


def get_role_manager() -> RoleManager:
    global _role_manager
    if _role_manager is None:
        _role_manager = RoleManager()
    return _role_manager


role_manager = get_role_manager()
