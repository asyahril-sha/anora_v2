# anora/roles/__init__.py
"""
ANORA Roles Package
Semua role dengan engine sendiri
"""

from .base_role import BaseRole
from .ipar_role import IparRole
from .teman_kantor_role import TemanKantorRole
from .pelakor_role import PelakorRole
from .istri_orang_role import IstriOrangRole
from .therapist_role import TherapistRole, get_therapist_manager
from .pelacur_role import PelacurRole, get_pelacur_manager
from .role_manager import RoleManager, get_role_manager

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
    'get_therapist_manager',
    'get_pelacur_manager',
]
