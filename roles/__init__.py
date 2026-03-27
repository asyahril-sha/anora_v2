# anora/roles/__init__.py
"""
ANORA Roles Package
"""

from .base_role import BaseRole
from .ipar import IparRole
from .teman_kantor import TemanKantorRole
from .pelakor import PelakorRole
from .istri_orang import IstriOrangRole
from .therapist_role import TherapistRole, get_therapist_manager
from .pelacur_role import PelacurRole, get_pelacur_manager
from .manager import RoleManager, get_role_manager, normalize_role_id

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
    'normalize_role_id',
]
