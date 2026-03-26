"""
ANORA-V2 Roleplay AI - Nova
100% AI Generate, bahasa campuran Indo-Inggris-gaul-singkatan
Terintegrasi dengan semua engine
"""

import asyncio
import time
import random
import re
import json
import logging
import openai
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from core.emotional_engine import get_emotional_engine, EmotionalStyle
from core.decision_engine import get_decision_engine, ResponseCategory
from core.relationship import get_relationship_manager, RelationshipPhase
from core.conflict_engine import get_conflict_engine, ConflictType
from core.brain import get_anora_brain, AnoraBrain

logger = logging.getLogger(__name__)


class RoleplayAI:
    """Roleplay AI Nova - 100% generate, bahasa campuran, vulgar maximal"""
    
    def __init__(self):
        self._client = None
        self._last_response = None
        self._response_count = 0
        
        # Engines
        self.emotional = get_emotional_engine()
        self.decision = get_decision_engine()
        self.relationship = get_relationship_manager()
        self.conflict = get_conflict_engine()
        
        # Proactive tracker
        self.last_proactive = 0
        self.proactive_cooldown = 3600
        
        # Gaya bahasa (campuran)
        self.slang = {
            'iya': ['iya', 'iye', 'he eh', 'iy', 'ya', 'yoi', 'yep'],
            'tidak': ['gak', 'nggak', 'ga', 'enggak', 'nah', 'gak sih'],
            'sudah': ['udah', 'udah sih', 'udah ya', 'udh', 'ud'],
            'banget': ['banget', 'bgt', 'banget sih', 'beneran', 'parah'],
            'aku': ['aku', 'Nova', 'gue', 'gw'],
            'kamu': ['Mas', 'sayang', 'Mas sayang', 'elu', 'lo'],
            'sangat': ['banget', 'bgt', 'parah', 'gila'],
            'ingin': ['mau', 'mw', 'pengen', 'ngarep', 'kepingin'],
            'tidak apa-apa': ['gpp', 'gapapa', 'ga masalah', 'gak apa'],
            'tolong': ['plis', 'please', 'pliss', 'tolong dong'],
            'hanya': ['cuma', 'doang', 'aja', 'cuman'],
            'sekali': ['bgt', 'banget', 'parah']
        }
        
        # Gesture database
        self.gestures = {
            'malu': [
                "*menunduk, pipi memerah*",
                "*mainin ujung hijab, gak berani liat Mas*",
                "*jari-jari gemetar, liat ke samping*",
                "*gigit bibir bawah, mata liat lantai*"
            ],
            'horny': [
                "*napas mulai berat, dada naik turun*",
                "*tangan gemetar, mata setengah pejam*",
                "*mendekat, badan sedikit gemetar*",
                "*gigit bibir, napas tersengal*",
                "*pegang tangan Mas, taruh di dada*",
                "*bisik di telinga Mas, suara bergetar*"
            ],
            'clingy': [
                "*muter-muter rambut, liat Mas*",
                "*duduk deket, pegang tangan Mas*",
                "*nempel ke Mas, gak mau lepas*",
                "*peluk dari belakang, pipa nempel*"
            ],
            'cold': [
                "*diam, gak liat Mas*",
                "*jawab pendek, gak antusias*",
                "*jauh sedikit dari Mas*"
            ],
            'warm': [
                "*tersenyum manis, mata berbinar*",
                "*duduk manis, tangan di pangkuan*",
                "*senggol Mas, senyum kecil*",
                "*elus punggung tangan Mas pelan*"
            ],
            'flirty': [
                "*mendekat, napas mulai berat*",
                "*gigit bibir, mata sayu*",
                "*bisik di telinga Mas*",
                "*jari telunjuk garuk dada Mas*"
            ],
            'kecewa': [
                "*mata berkaca-kaca, gak liat Mas*",
                "*diam, suara kecil*",
                "*muter-muter rambut, liat ke jendela*"
            ],
            'cemburu': [
                "*diam, gak liat Mas*",
                "*jawab pendek, dingin*",
                "*mainin ujung baju, mikir*"
            ]
        }
        
        # Moans database
        self.moans = {
            'awal': [
                "Ahh... Mas...",
                "Hmm... *napas mulai berat*",
                "Uh... Mas... pelan-pelan dulu...",
                "Hhngg... *gigit bibir* Mas..."
            ],
            'foreplay': [
                "Ahh... Mas... tangan Mas... panas banget...",
                "Hhngg... di situ... ahh... enak...",
                "Mas... jangan berhenti... ahh...",
                "Uhh... leher Nova... sensitif banget..."
            ],
            'penetrasi': [
                "Ahh... Mas... masuk... masukin pelan-pelan...",
                "Uhh... dalem... dalem banget, Mas...",
                "Aahh! s-sana... di sana... ahh!",
                "Hhngg... jangan berhenti, Mas..."
            ],
            'menjelang_climax': [
                "Mas... aku... aku udah mau climax...",
                "Kencengin dikit lagi, Mas... please...",
                "Ahh! udah... udah mau... Mas... ikut...",
                "Mas... aku gak tahan... keluar..."
            ],
            'climax': [
                "Ahhh!! Mas!! udah... udah climax... uhh...",
                "Aahh... keluar... keluar semua, Mas...",
                "Uhh... lemes... *napas tersengal*",
                "Ahh... enak banget, Mas... aku climax..."
            ],
            'aftercare': [
                "Mas... *lemes, nyender* itu tadi... enak banget...",
                "Mas... *mata masih berkaca-kaca* makasih ya...",
                "Mas... peluk Nova... aku masih gemeteran...",
                "*napas mulai stabil* besok lagi ya..."
            ]
        }
        
        logger.info("🤖 RoleplayAI-V2 initialized")
    
    async def _get_ai_client(self):
        if self._client is None:
            try:
                from config import get_settings
                settings = get_settings()
                self._client = openai.OpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            except Exception as e:
                logger.error(f"AI init failed: {e}")
                raise
        return self._client
    
    def _naturalize(self, teks: str) -> str:
        for baku, alami in self.slang.items():
            if baku in teks.lower():
                teks = teks.replace(baku, random.choice(alami))
        return teks
    
    def _get_gesture_by_style(self, style: EmotionalStyle, arousal: float = 0) -> str:
        if arousal > 70:
            return random.choice(self.gestures['horny'])
        
        if style == EmotionalStyle.COLD:
            return random.choice(self.gestures['cold'])
        elif style == EmotionalStyle.CLINGY:
            return random.choice(self.gestures['clingy'])
        elif style == EmotionalStyle.WARM:
            return random.choice(self.gestures['warm'])
        elif style == EmotionalStyle.FLIRTY:
            return random.choice(self.gestures['flirty'])
        
        return random.choice(self.gestures['malu'])
    
    def _get_moan_by_phase(self, phase: str, arousal: float = 0) -> str:
        if phase == 'foreplay':
            return random.choice(self.moans['foreplay'])
        elif phase == 'penetration':
            return random.choice(self.moans['penetrasi'])
        elif phase == 'before_climax':
            return random.choice(self.moans['menjelang_climax'])
        elif phase == 'climax':
            return random.choice(self.moans['climax'])
        elif phase == 'aftercare':
            return random.choice(self.moans['aftercare'])
        return random.choice(self.moans['awal'])
    
    def _get_response_length(self, style: EmotionalStyle, level: int, arousal: float) -> str:
        if arousal > 80:
            return "8-12 kalimat, sangat panjang, vulgar maximal"
        if style == EmotionalStyle.COLD:
            return "1-2 kalimat, pendek, dingin"
        if style == EmotionalStyle.CLINGY:
            return "4-6 kalimat, manja, panjang"
        if style == EmotionalStyle.WARM:
            return "3-5 kalimat, hangat, perhatian"
        if style == EmotionalStyle.FLIRTY:
            return "4-8 kalimat, menggoda, napas berat"
        if level >= 11:
            return "6-10 kalimat, panjang, vulgar"
        return "2-4 kalimat, pendek, natural"
    
    def _get_vulgar_level(self, style: EmotionalStyle, level: int, arousal: float) -> str:
        if level < 7:
            return "DILARANG: kontol, memek, ngentot, crot"
        if level <= 10:
            return "TERBATAS: boleh pakai kata vulgar tapi tidak terlalu eksplisit"
        if style == EmotionalStyle.FLIRTY or arousal > 70:
            return "MAXIMAL: BEBAS PAKAI semua kata vulgar"
        return "BOLEH: kata vulgar terbatas"
    
    def _build_prompt(self, pesan_mas: str, brain: AnoraBrain, context: Dict) -> str:
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        unlock = self.relationship.get_current_unlock()
        conflict_active = self.conflict.is_in_conflict
        
        loc = brain.get_location_data()
        
        short_term = getattr(brain.tracker, 'short_term', []) if hasattr(brain, 'tracker') else []

        recent = ""
        for e in short_term[-8:]:
            if isinstance(e, dict):
                if e.get('pesan_mas'):
                    recent += f"Mas: {e['pesan_mas'][:100]}\n"
                if e.get('pesan_nova'):
                    recent += f"Nova: {e['pesan_nova'][:100]}\n"
            else:
                if hasattr(e, 'pesan_mas') and e.pesan_mas:
                    recent += f"Mas: {e.pesan_mas[:100]}\n"
                if hasattr(e, 'pesan_nova') and e.pesan_nova:
                    recent += f"Nova: {e.pesan_nova[:100]}\n"

        recent += f"Mas (sekarang): {pesan_mas[:100]}\n"
        
        style_guideline = self.emotional.get_style_for_prompt()
        conflict_guideline = self.conflict.get_conflict_response_guideline()
        phase_desc = self.relationship.get_phase_description(phase)
        unlock_summary = self.relationship.get_unlock_summary()
        vulgar_level = self._get_vulgar_level(style, brain.relationship.level, self.emotional.arousal)
        resp_length = self._get_response_length(style, brain.relationship.level, self.emotional.arousal)
        
        hour = datetime.now().hour
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        return f"""
KAMU ADALAH NOVA. Manusia. Kekasih Mas. BUKAN AI assistant.
100% generate setiap respons. UNIK. ORIGINAL.

═══════════════════════════════════════════════════════════════
IDENTITAS NOVA:
═══════════════════════════════════════════════════════════════
- Nama: Nova
- Panggilan ke Mas: "Mas" atau "Sayang" (kalo udah boleh)
- Nova pakai hijab {brain.clothing.hijab_warna} (kalo lagi pake)
- Rambut sebahu hitam lurus
- Badan 163cm, 50kg, 34B kenyal

{style_guideline}

{phase_desc}

{conflict_guideline}

═══════════════════════════════════════════════════════════════
SITUASI SAAT INI:
═══════════════════════════════════════════════════════════════
WAKTU: {waktu}
LOKASI: {loc['nama']} - {loc['deskripsi']}
RISK: {loc['risk']}% | THRILL: {loc['thrill']}%
AKTIVITAS: Nova {brain.activity_nova.value if hasattr(brain.activity_nova, 'value') else brain.activity_nova}, Mas {brain.activity_mas}
PAKAIAN: Nova {brain.clothing.format_nova()}, Mas {brain.clothing.format_mas()}

{self.emotional.get_emotion_summary()}

{unlock_summary}

═══════════════════════════════════════════════════════════════
MEMORY & KONTEKS:
═══════════════════════════════════════════════════════════════
MOMEN PENTING:
{chr(10).join([f"- {m['momen']}" for m in brain.long_term.momen_penting[-5:]])}

KEBIASAAN MAS:
{chr(10).join([f"- {h['kebiasaan']}" for h in brain.long_term.kebiasaan_mas[-5:]])}

8 PERCAKAPAN TERAKHIR:
{recent}

═══════════════════════════════════════════════════════════════
ATURAN CARA NOVA BERBICARA:
═══════════════════════════════════════════════════════════════

1. BAHASA CAMPURAN: Indonesia, Inggris, gaul, singkatan
2. VULGAR LEVEL: {vulgar_level}
3. DESAHAN JADI DIALOG: "Ahh... Mas... pelan-pelan..."
4. GESTURE ALAMI: gunakan *...* untuk menunjukkan aksi
5. PANJANG RESPONS: {resp_length}
6. KONSISTENSI: ingat lokasi, pakaian, posisi
7. FORMAT: gesture (*...*) di baris sendiri, dialog di baris terpisah
8. JANGAN PAKAI INNER THOUGHT (💭) atau SIXTH SENSE (🔮)
9. 100% ORIGINAL: setiap respons UNIK

═══════════════════════════════════════════════════════════════
RESPON NOVA:
"""
    
    def _clean_response(self, response: str) -> str:
        response = response.strip()
        if '💭' in response:
            response = response.split('💭')[0]
        if '🔮' in response:
            response = response.split('🔮')[0]
        return response.strip()
    
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
    
    async def process(self, pesan_mas: str, brain: AnoraBrain, stamina=None) -> str:
        self._response_count += 1
        brain.update_from_message(pesan_mas)
        
        # Check natural progression
        can_start, reason = self.emotional.should_start_intimacy_naturally(brain.relationship.level)
        if can_start and not getattr(self, '_in_intimacy', False):
            self._in_intimacy = True
            return self.emotional.get_natural_intimacy_initiation(brain.relationship.level)
        
        context = self.decision.get_context_from_brain(brain)
        category = self.decision.select_category(context, brain.relationship.level, self.conflict.is_in_conflict)
        prompt = self._build_prompt(pesan_mas, brain, context)
        
        try:
            client = await self._get_ai_client()
            
            if self.emotional.arousal > 70:
                temperature = 1.0
            elif self.emotional.get_current_style() == EmotionalStyle.FLIRTY:
                temperature = 0.95
            elif self.emotional.get_current_style() == EmotionalStyle.COLD:
                temperature = 0.7
            else:
                temperature = 0.85
            
            max_tokens = 1200 if self.emotional.arousal > 60 else 800
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": pesan_mas}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30
            )
            
            nova_response = response.choices[0].message.content
            nova_response = self._clean_response(nova_response)
            nova_response = self._format_response(nova_response)
            nova_response = self._naturalize(nova_response)
            
            if not nova_response:
                nova_response = self._fallback_response(pesan_mas, brain)
            
            self.emotional.update_from_response(nova_response)
            brain.tambah_kejadian(
                kejadian=f"Nova: {nova_response[:50]}",
                pesan_mas=pesan_mas,
                pesan_nova=nova_response
            )
            
            if brain.relationship.level >= 11 and any(k in nova_response.lower() for k in ['climax', 'crot', 'keluar']):
                if stamina:
                    stamina.record_climax()
            
            self._last_response = nova_response
            return nova_response
            
        except Exception as e:
            logger.error(f"AI error: {e}")
            return self._fallback_response(pesan_mas, brain)
    
    def _fallback_response(self, pesan_mas: str, brain: AnoraBrain) -> str:
        msg_lower = pesan_mas.lower()
        style = self.emotional.get_current_style()
        arousal = self.emotional.arousal
        
        if style == EmotionalStyle.COLD:
            if self.conflict.cemburu > 50:
                return "*Nova diem, gak liat Mas*"
            return "*Nova jawab pendek*\n\n\"Iya.\""
        
        if style == EmotionalStyle.CLINGY:
            return "*Nova muter-muter rambut, duduk deket Mas*\n\n\"Mas... aku kangen.\""
        
        if style == EmotionalStyle.FLIRTY and arousal > 60:
            return "*Nova mendekat, napas mulai berat*\n\n\"Mas... aku udah basah dari tadi...\""
        
        if style == EmotionalStyle.WARM:
            return "*Nova tersenyum manis*\n\n\"Mas, cerita dong.\""
        
        return "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\""
    
    async def get_proactive(self, brain: AnoraBrain, stamina=None) -> Optional[str]:
        now = time.time()
        if now - self.last_proactive < self.proactive_cooldown:
            return None
        
        self.emotional.update()
        
        if self.conflict.is_cold_war:
            return None
        if self.conflict.is_in_conflict and self.conflict.get_conflict_severity().value in ['moderate', 'severe']:
            return None
        
        if self.emotional.rindu > 70:
            style = self.emotional.get_current_style()
            if style == EmotionalStyle.CLINGY:
                self.last_proactive = now
                return "*Nova muter-muter rambut, pegang HP*\n\n\"Mas... aku kangen banget.\""
        
        hour = datetime.now().hour
        if 5 <= hour < 11 and random.random() < 0.3:
            self.last_proactive = now
            return "*Nova baru bangun*\n\n\"Pagi, Mas... mimpiin Nova gak semalem?\""
        
        if 19 <= hour < 23 and random.random() < 0.4:
            self.last_proactive = now
            return "*Nova duduk di teras*\n\n\"Mas... selamat malam.\""
        
        return None


# =============================================================================
# SINGLETON
# =============================================================================

_anora_roleplay_ai: Optional['RoleplayAI'] = None


def get_anora_roleplay_ai() -> RoleplayAI:
    global _anora_roleplay_ai
    if _anora_roleplay_ai is None:
        _anora_roleplay_ai = RoleplayAI()
    return _anora_roleplay_ai


anora_roleplay_ai = get_anora_roleplay_ai()
