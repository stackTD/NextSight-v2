"""
Zone Management System for NextSight v2

This package provides interactive zone creation, hand-zone intersection detection,
and professional zone visualization for the exhibition demo.
"""

from .zone_manager import ZoneManager
from .zone_creator import ZoneCreator
from .intersection_detector import IntersectionDetector
from .zone_config import Zone, ZoneType, ZoneConfig

__all__ = [
    'ZoneManager',
    'ZoneCreator', 
    'IntersectionDetector',
    'Zone',
    'ZoneType',
    'ZoneConfig'
]