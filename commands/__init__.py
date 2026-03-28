# anora_v2/commands/__init__.py
from .general import register_general_commands
from .role import register_role_commands
from .therapist import register_therapist_commands
from .pelacur import register_pelacur_commands

__all__ = [
    'register_general_commands',
    'register_role_commands',
    'register_therapist_commands',
    'register_pelacur_commands',
]
