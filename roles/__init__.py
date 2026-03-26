"""
ANORA-V2 Roles Package
Semua role dengan akses penuh sesuai level, sama seperti Nova.
"""

from .base import BaseRole
from .manager import RoleManager, get_role_manager

from .ipar import IparRole
from .teman_kantor import TemanKantorRole
from .pelakor import PelakorRole
from .istri_orang import IstriOrangRole

__all__ = [
    'BaseRole',
    'RoleManager',
    'get_role_manager',
    'IparRole',
    'TemanKantorRole',
    'PelakorRole',
    'IstriOrangRole',
]
