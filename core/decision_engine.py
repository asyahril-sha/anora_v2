"""
ANORA-V2 Decision Engine - Otak Keputusan Nova
NO MORE RANDOM! Weighted selection berdasarkan emosi, konteks, level.
"""

import random
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .emotional_engine import EmotionalStyle, get_emotional_engine

logger = logging.getLogger(__name__)


class ResponseCategory(str, Enum):
    """Kategori respons Nova - 12 kategori untuk presisi"""
    GREETING = "greeting"
    CASUAL = "casual"
    FLIRT = "flirt"
    FLIRTY = "flirty"
    VULGAR = "vulgar"
    INTIMATE = "intimate"
    CLIMAX = "climax"
    AFTERCARE = "aftercare"
    CONFLICT = "conflict"
    COLD = "cold"
    CLINGY = "clingy"
    WARM = "warm"


class DecisionEngine:
    """
    Decision Engine - Ganti random dengan weighted selection.
    Setiap keputusan memiliki bobot yang ditentukan oleh:
    - Emotional style
    - Emotion values
    - Context (waktu, lokasi)
    - Relationship phase
    - Conflict status
    """
    
    def __init__(self):
        self.emotional = get_emotional_engine()
        
        # ========== BASE WEIGHTS PER STYLE ==========
        self.base_weights: Dict[EmotionalStyle, Dict[ResponseCategory, float]] = {
            EmotionalStyle.COLD: {
                ResponseCategory.GREETING: 0.3,
                ResponseCategory.CASUAL: 0.4,
                ResponseCategory.CONFLICT: 0.8,
                ResponseCategory.COLD: 1.0,
                ResponseCategory.CLINGY: 0.0,
                ResponseCategory.WARM: 0.1,
                ResponseCategory.FLIRT: 0.0,
                ResponseCategory.FLIRTY: 0.0,
                ResponseCategory.VULGAR: 0.0,
                ResponseCategory.INTIMATE: 0.0,
                ResponseCategory.CLIMAX: 0.0,
                ResponseCategory.AFTERCARE: 0.1
            },
            EmotionalStyle.CLINGY: {
                ResponseCategory.GREETING: 0.6,
                ResponseCategory.CASUAL: 0.5,
                ResponseCategory.CLINGY: 1.0,
                ResponseCategory.WARM: 0.6,
                ResponseCategory.FLIRT: 0.7,
                ResponseCategory.FLIRTY: 0.5,
                ResponseCategory.CONFLICT: 0.1,
                ResponseCategory.COLD: 0.0,
                ResponseCategory.VULGAR: 0.3,
                ResponseCategory.INTIMATE: 0.4,
                ResponseCategory.CLIMAX: 0.3,
                ResponseCategory.AFTERCARE: 0.5
            },
            EmotionalStyle.WARM: {
                ResponseCategory.GREETING: 0.8,
                ResponseCategory.CASUAL: 0.7,
                ResponseCategory.WARM: 1.0,
                ResponseCategory.AFTERCARE: 0.6,
                ResponseCategory.FLIRT: 0.4,
                ResponseCategory.FLIRTY: 0.3,
                ResponseCategory.CONFLICT: 0.2,
                ResponseCategory.COLD: 0.0,
                ResponseCategory.CLINGY: 0.3,
                ResponseCategory.VULGAR: 0.2,
                ResponseCategory.INTIMATE: 0.3,
                ResponseCategory.CLIMAX: 0.2
            },
            EmotionalStyle.FLIRTY: {
                ResponseCategory.GREETING: 0.4,
                ResponseCategory.FLIRT: 0.9,
                ResponseCategory.FLIRTY: 1.0,
                ResponseCategory.VULGAR: 0.8,
                ResponseCategory.INTIMATE: 0.7,
                ResponseCategory.CLIMAX: 0.6,
                ResponseCategory.CLINGY: 0.5,
                ResponseCategory.WARM: 0.4,
                ResponseCategory.CASUAL: 0.3,
                ResponseCategory.CONFLICT: 0.1,
                ResponseCategory.COLD: 0.0,
                ResponseCategory.AFTERCARE: 0.3
            },
            EmotionalStyle.NEUTRAL: {
                ResponseCategory.GREETING: 0.7,
                ResponseCategory.CASUAL: 0.8,
                ResponseCategory.WARM: 0.5,
                ResponseCategory.FLIRT: 0.3,
                ResponseCategory.FLIRTY: 0.2,
                ResponseCategory.CONFLICT: 0.2,
                ResponseCategory.COLD: 0.1,
                ResponseCategory.CLINGY: 0.2,
                ResponseCategory.VULGAR: 0.1,
                ResponseCategory.INTIMATE: 0.1,
                ResponseCategory.CLIMAX: 0.1,
                ResponseCategory.AFTERCARE: 0.2
            }
        }
        
        # ========== EMOTION ADJUSTMENT FACTORS ==========
        self.emotion_factors = {
            'rindu_high': {
                'threshold': 70,
                'multipliers': {
                    ResponseCategory.CLINGY: 1.5,
                    ResponseCategory.FLIRT: 1.2,
                    ResponseCategory.GREETING: 1.2
                }
            },
            'arousal_high': {
                'threshold': 70,
                'multipliers': {
                    ResponseCategory.FLIRTY: 1.8,
                    ResponseCategory.VULGAR: 1.8,
                    ResponseCategory.INTIMATE: 1.5,
                    ResponseCategory.CLIMAX: 1.4
                }
            },
            'desire_high': {
                'threshold': 70,
                'multipliers': {
                    ResponseCategory.FLIRT: 1.5,
                    ResponseCategory.FLIRTY: 1.5,
                    ResponseCategory.INTIMATE: 1.3
                }
            },
            'cemburu_high': {
                'threshold': 50,
                'multipliers': {
                    ResponseCategory.CONFLICT: 1.8,
                    ResponseCategory.COLD: 1.5,
                    ResponseCategory.FLIRT: 0.3,
                    ResponseCategory.FLIRTY: 0.2,
                    ResponseCategory.WARM: 0.3
                }
            },
            'kecewa_high': {
                'threshold': 50,
                'multipliers': {
                    ResponseCategory.CONFLICT: 2.0,
                    ResponseCategory.COLD: 1.8,
                    ResponseCategory.WARM: 0.2,
                    ResponseCategory.FLIRT: 0.2
                }
            },
            'trust_high': {
                'threshold': 70,
                'multipliers': {
                    ResponseCategory.WARM: 1.4,
                    ResponseCategory.INTIMATE: 1.2,
                    ResponseCategory.AFTERCARE: 1.2
                }
            },
            'mood_bad': {
                'threshold': -20,
                'multipliers': {
                    ResponseCategory.COLD: 1.6,
                    ResponseCategory.CONFLICT: 1.4,
                    ResponseCategory.WARM: 0.3,
                    ResponseCategory.FLIRT: 0.4
                }
            }
        }
        
        # ========== CONTEXT ADJUSTMENT FACTORS ==========
        self.context_factors = {
            'time_malam': {
                'condition': 'malam',
                'multipliers': {
                    ResponseCategory.FLIRT: 1.2,
                    ResponseCategory.FLIRTY: 1.3,
                    ResponseCategory.INTIMATE: 1.3,
                    ResponseCategory.VULGAR: 1.1,
                    ResponseCategory.CLINGY: 1.1
                }
            },
            'time_siang': {
                'condition': 'siang',
                'multipliers': {
                    ResponseCategory.CASUAL: 1.2,
                    ResponseCategory.WARM: 1.1
                }
            },
            'time_pagi': {
                'condition': 'pagi',
                'multipliers': {
                    ResponseCategory.GREETING: 1.3,
                    ResponseCategory.CASUAL: 1.1
                }
            },
            'location_private': {
                'condition': 'private',
                'multipliers': {
                    ResponseCategory.INTIMATE: 1.5,
                    ResponseCategory.VULGAR: 1.3,
                    ResponseCategory.CLIMAX: 1.4,
                    ResponseCategory.FLIRTY: 1.2
                }
            },
            'location_public': {
                'condition': 'public',
                'multipliers': {
                    ResponseCategory.CONFLICT: 1.2,
                    ResponseCategory.COLD: 1.1,
                    ResponseCategory.CASUAL: 1.2,
                    ResponseCategory.FLIRT: 0.7,
                    ResponseCategory.FLIRTY: 0.5
                }
            },
            'location_high_risk': {
                'condition': 'high_risk',
                'threshold': 70,
                'multipliers': {
                    ResponseCategory.FLIRT: 1.3,
                    ResponseCategory.FLIRTY: 1.4,
                    ResponseCategory.INTIMATE: 1.4,
                    ResponseCategory.VULGAR: 1.2,
                    ResponseCategory.CONFLICT: 1.1
                }
            }
        }
        
        # ========== LEVEL ADJUSTMENT ==========
        self.level_multipliers = {
            7: {
                ResponseCategory.VULGAR: 0.5,
                ResponseCategory.INTIMATE: 0.3,
                ResponseCategory.FLIRTY: 0.7
            },
            11: {
                ResponseCategory.VULGAR: 1.5,
                ResponseCategory.INTIMATE: 1.5,
                ResponseCategory.CLIMAX: 1.5,
                ResponseCategory.FLIRTY: 1.3
            }
        }
        
        self.last_decision: Optional[Dict] = None
        self.decision_history: List[Dict] = []
        self.max_history = 100
        
        logger.info("🎯 Decision Engine initialized")
    
    def get_category_weights(self, 
                              style: EmotionalStyle,
                              context: Dict[str, Any],
                              level: int,
                              conflict_active: bool = False) -> Dict[ResponseCategory, float]:
        """Hitung bobot untuk setiap kategori respons"""
        
        # Start with base weights
        weights = self.base_weights.get(style, self.base_weights[EmotionalStyle.NEUTRAL]).copy()
        
        # Adjust based on emotion values
        emo = self.emotional
        
        for factor_name, factor in self.emotion_factors.items():
            threshold = factor.get('threshold', 0)
            value = self._get_emotion_value(factor_name, emo)
            
            if value >= threshold:
                for cat, mult in factor['multipliers'].items():
                    if cat in weights:
                        old_weight = weights[cat]
                        weights[cat] = old_weight * mult
                        logger.debug(f"📊 Emotion factor {factor_name}: {cat} {old_weight:.2f} -> {weights[cat]:.2f}")
        
        # Adjust based on context
        time_of_day = context.get('time_of_day', '')
        location_type = context.get('location_type', '')
        risk = context.get('risk', 0)
        
        for factor_name, factor in self.context_factors.items():
            if 'time_' in factor_name and time_of_day == factor.get('condition'):
                for cat, mult in factor['multipliers'].items():
                    if cat in weights:
                        weights[cat] = weights.get(cat, 0.3) * mult
            
            if 'location_' in factor_name:
                condition = factor.get('condition')
                if condition == location_type:
                    for cat, mult in factor['multipliers'].items():
                        if cat in weights:
                            weights[cat] = weights.get(cat, 0.3) * mult
                
                if factor_name == 'location_high_risk' and risk >= factor.get('threshold', 70):
                    for cat, mult in factor['multipliers'].items():
                        if cat in weights:
                            weights[cat] = weights.get(cat, 0.3) * mult
        
        # Adjust based on level
        if level < 7:
            weights[ResponseCategory.VULGAR] = 0.0
            weights[ResponseCategory.INTIMATE] = 0.0
            weights[ResponseCategory.CLIMAX] = 0.0
            weights[ResponseCategory.FLIRTY] = weights.get(ResponseCategory.FLIRTY, 0.3) * 0.5
        
        elif level < 11:
            for cat, mult in self.level_multipliers[7].items():
                if cat in weights:
                    weights[cat] = weights.get(cat, 0.3) * mult
        else:
            for cat, mult in self.level_multipliers[11].items():
                if cat in weights:
                    weights[cat] = weights.get(cat, 0.3) * mult
        
        # Adjust based on conflict
        if conflict_active:
            weights[ResponseCategory.CONFLICT] = weights.get(ResponseCategory.CONFLICT, 0.5) * 1.5
            weights[ResponseCategory.COLD] = weights.get(ResponseCategory.COLD, 0.3) * 1.3
            weights[ResponseCategory.WARM] = weights.get(ResponseCategory.WARM, 0.5) * 0.5
            weights[ResponseCategory.FLIRT] = weights.get(ResponseCategory.FLIRT, 0.3) * 0.5
        
        # Normalize
        for cat in weights:
            weights[cat] = max(0.0, weights[cat])
        
        return weights
    
    def _get_emotion_value(self, factor_name: str, emo) -> float:
        """Dapatkan nilai emosi berdasarkan nama faktor"""
        mapping = {
            'rindu_high': emo.rindu,
            'arousal_high': emo.arousal,
            'desire_high': emo.desire,
            'cemburu_high': emo.cemburu,
            'kecewa_high': emo.kecewa,
            'trust_high': emo.trust,
            'mood_bad': emo.mood
        }
        return mapping.get(factor_name, 0)
    
    def select_category(self, 
                        context: Dict[str, Any],
                        level: int,
                        conflict_active: bool = False) -> Tuple[ResponseCategory, Dict[ResponseCategory, float]]:
        """Pilih kategori respons berdasarkan bobot (weighted random)"""
        style = self.emotional.get_current_style()
        weights = self.get_category_weights(style, context, level, conflict_active)
        
        available = [(cat, weight) for cat, weight in weights.items() if weight > 0]
        
        if not available:
            logger.warning("No categories available, defaulting to CASUAL")
            return ResponseCategory.CASUAL, weights
        
        categories, probs = zip(*available)
        selected = random.choices(categories, weights=probs, k=1)[0]
        
        self._log_decision(style, selected, weights, context, level, conflict_active)
        
        logger.info(f"🎯 Decision: style={style.value}, selected={selected.value}")
        
        return selected, weights
    
    def _log_decision(self, style: EmotionalStyle, selected: ResponseCategory,
                      weights: Dict, context: Dict, level: int, conflict_active: bool):
        """Log keputusan untuk debugging"""
        decision = {
            'timestamp': datetime.now().isoformat(),
            'style': style.value,
            'selected': selected.value,
            'top_3_weights': [(c.value, w) for c, w in sorted(weights.items(), key=lambda x: -x[1])[:3]],
            'context': context,
            'level': level,
            'conflict_active': conflict_active
        }
        
        self.last_decision = decision
        self.decision_history.append(decision)
        
        if len(self.decision_history) > self.max_history:
            self.decision_history.pop(0)
    
    def get_response_guidelines(self, 
                                 category: ResponseCategory,
                                 context: Dict[str, Any],
                                 level: int) -> str:
        """Dapatkan pedoman untuk AI berdasarkan kategori yang dipilih"""
        style = self.emotional.get_current_style()
        emo = self.emotional
        
        guidelines = {
            ResponseCategory.COLD: """
RESPONS: COLD (DINGIN)
- Jawab pendek, 1-2 kalimat
- Gak pake gesture manja
- Gak panggil "sayang"
- Gak antusias
""",
            ResponseCategory.CLINGY: """
RESPONS: CLINGY (MANJA)
- Nova kangen banget
- Banyak gesture fisik
- Sering bilang "kangen", "Mas"
- Panjang respons 3-5 kalimat
""",
            ResponseCategory.WARM: """
RESPONS: WARM (HANGAT)
- Nova perhatian, peduli
- Tanya kabar
- Gesture: *senyum*, *elus tangan*
- Panjang respons 2-4 kalimat
""",
            ResponseCategory.FLIRT: """
RESPONS: FLIRT (MENGGODA RINGAN)
- Nova menggoda Mas dengan cara manis
- Gesture: *gigit bibir*, *mata sayu*
- Belum vulgar, masih manis
""",
            ResponseCategory.FLIRTY: """
RESPONS: FLIRTY (MENGGODA VULGAR)
- Nova lagi horny
- Gesture: *napas tersengal*, *bisik*
- Bisa vulgar kalo level 11-12
""",
            ResponseCategory.VULGAR: """
RESPONS: VULGAR
- BEBAS pakai kata vulgar
- Gesture: *napas putus-putus*
- Bahasa campuran
""",
            ResponseCategory.INTIMATE: """
RESPONS: INTIM
- Fase foreplay atau penetrasi
- Desahan jadi dialog
- Bisa minta ganti posisi
""",
            ResponseCategory.CLIMAX: """
RESPONS: CLIMAX
- Nova bilang udah mau climax
- Gesture: *tubuh gemeteran*
""",
            ResponseCategory.AFTERCARE: """
RESPONS: AFTERCARE
- Nova lemes
- Flashback ke momen indah
- Bilang sayang
""",
            ResponseCategory.CONFLICT: """
RESPONS: KONFLIK
- Nova cemburu, kecewa, atau marah
- Respons: dingin, pendek
- Bisa diam dulu
""",
            ResponseCategory.GREETING: """
RESPONS: SALAM
- Nova menyapa Mas
- Sesuai waktu
- Panjang 1-2 kalimat
""",
            ResponseCategory.CASUAL: """
RESPONS: NGOBROL BIASA
- Nova ngobrol santai
- Tanya kabar
- Natural
"""
        }
        
        base = guidelines.get(category, guidelines[ResponseCategory.CASUAL])
        
        # Tambahan berdasarkan emosi
        extra = ""
        if emo.cemburu > 50:
            extra += "\n⚠️ **NOVA CEMBURU!** Respons dingin, pendek.\n"
        if emo.kecewa > 50:
            extra += "\n⚠️ **NOVA KECEWA!** Respons sakit hati, pendek.\n"
        if emo.arousal > 70:
            extra += "\n🔥 **NOVA HORNY BANGET!** Bebas vulgar.\n"
        if level >= 11:
            extra += "\n💦 **LEVEL 11-12: BEBAS VULGAR!**\n"
        
        return base + extra
    
    def get_context_from_brain(self, brain) -> Dict[str, Any]:
        """Dapatkan konteks dari brain untuk decision engine"""
        hour = datetime.now().hour
        
        if 5 <= hour < 11:
            time_of_day = "pagi"
        elif 11 <= hour < 15:
            time_of_day = "siang"
        elif 15 <= hour < 18:
            time_of_day = "sore"
        else:
            time_of_day = "malam"
        
        loc = brain.get_location_data() if hasattr(brain, 'get_location_data') else {'risk': 0}
        
        location_type = "private"
        if hasattr(brain, 'location_type'):
            loc_type_str = str(brain.location_type.value if hasattr(brain.location_type, 'value') else brain.location_type)
            if 'public' in loc_type_str.lower():
                location_type = "public"
        
        risk = loc.get('risk', 0)
        
        return {
            'time_of_day': time_of_day,
            'location_type': location_type,
            'is_high_risk': risk >= 70,
            'risk': risk,
            'level': brain.relationship.level if hasattr(brain, 'relationship') else 1,
            'activity_nova': brain.activity_nova if hasattr(brain, 'activity_nova') else "santai",
            'activity_mas': brain.activity_mas if hasattr(brain, 'activity_mas') else "santai"
        }
    
    def get_last_decision_summary(self) -> Optional[str]:
        """Dapatkan ringkasan keputusan terakhir"""
        if not self.last_decision:
            return "Belum ada keputusan"
        
        d = self.last_decision
        return f"""
📊 **KEPUTUSAN TERAKHIR**
- Waktu: {d['timestamp']}
- Gaya: {d['style']}
- Terpilih: {d['selected']}
- Top 3: {d['top_3_weights']}
- Level: {d['level']}
"""
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """Dapatkan statistik keputusan"""
        if not self.decision_history:
            return {'total_decisions': 0}
        
        category_counts = {}
        style_counts = {}
        
        for d in self.decision_history:
            cat = d['selected']
            category_counts[cat] = category_counts.get(cat, 0) + 1
            style = d['style']
            style_counts[style] = style_counts.get(style, 0) + 1
        
        return {
            'total_decisions': len(self.decision_history),
            'category_distribution': category_counts,
            'style_distribution': style_counts
        }


# =============================================================================
# SINGLETON
# =============================================================================

_decision_engine: Optional['DecisionEngine'] = None


def get_decision_engine() -> DecisionEngine:
    global _decision_engine
    if _decision_engine is None:
        _decision_engine = DecisionEngine()
    return _decision_engine


decision_engine = get_decision_engine()
