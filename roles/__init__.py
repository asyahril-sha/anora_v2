# anora/roles/__init__.py

"""
ANORA-V2 Roles Package
Semua role dengan akses penuh sesuai level, sama seperti Nova.
"""

from .therapist_role import TherapistRole, get_random_therapist
from .pelacur_role import PelacurRole
from .base_role import BaseRole
from .ipar_role import IparRole
from .teman_kantor_role import TemanKantorRole
from .istri_orang_role import IstriOrangRole
from .role_manager import RoleManager, get_role_manager

__all__ = [
    'BaseRole',
    'TherapistRole',
    'PelacurRole',
    'IparRole',
    'TemanKantorRole',
    'IstriOrangRole',
    'RoleManager',
    'get_role_manager',
    'get_random_therapist',
]
