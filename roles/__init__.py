# anora/roles/__init__.py
"""
ANORA Roles Package
Semua role dengan engine sendiri
"""

from .base import BaseRole
from .ipar import IparRole
from .teman_kantor import TemanKantorRole
from .pelakor import PelakorRole
from .istri_orang import IstriOrangRole
from .therapist_role import TherapistRole
from .pelacur_role import PelacurRole
from .manager import RoleManager, get_role_manager

__all__ = [
    'BaseRole',
    'IparRole',
    'TemanKantorRole',
    'PelakorRole',
    'IstriOrangRole',
    'TherapistRole',
    'PelacurRole',
    'RoleManager',
    'get_role_manager',
]
]
