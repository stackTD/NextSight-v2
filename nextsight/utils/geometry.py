"""
Geometric utilities for zone intersection detection
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Point:
    """2D Point with normalized coordinates (0-1)"""
    x: float
    y: float
    
    def to_pixel(self, width: int, height: int) -> Tuple[int, int]:
        """Convert to pixel coordinates"""
        return (int(self.x * width), int(self.y * height))


@dataclass
class Rectangle:
    """Rectangle with normalized coordinates (0-1)"""
    x: float
    y: float
    width: float
    height: float
    
    @property
    def left(self) -> float:
        return self.x
    
    @property
    def right(self) -> float:
        return self.x + self.width
    
    @property
    def top(self) -> float:
        return self.y
    
    @property
    def bottom(self) -> float:
        return self.y + self.height
    
    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.height / 2)
    
    def contains_point(self, point: Point) -> bool:
        """Check if point is inside rectangle"""
        return (self.left <= point.x <= self.right and
                self.top <= point.y <= self.bottom)
    
    def intersects_rectangle(self, other: 'Rectangle') -> bool:
        """Check if this rectangle intersects with another"""
        return not (self.right < other.left or 
                   other.right < self.left or
                   self.bottom < other.top or
                   other.bottom < self.top)
    
    def intersection_area(self, other: 'Rectangle') -> float:
        """Calculate intersection area with another rectangle"""
        if not self.intersects_rectangle(other):
            return 0.0
        
        left = max(self.left, other.left)
        right = min(self.right, other.right)
        top = max(self.top, other.top)
        bottom = min(self.bottom, other.bottom)
        
        return (right - left) * (bottom - top)
    
    def area(self) -> float:
        """Calculate rectangle area"""
        return self.width * self.height


class HandLandmarkProcessor:
    """Process hand landmarks for zone intersection"""
    
    def __init__(self):
        # Key landmark indices from MediaPipe Hands
        self.WRIST = 0
        self.THUMB_TIP = 4
        self.INDEX_TIP = 8
        self.MIDDLE_TIP = 12
        self.RING_TIP = 16
        self.PINKY_TIP = 20
        
        # Palm landmarks for bounding box calculation
        self.PALM_LANDMARKS = [0, 1, 5, 9, 13, 17]  # Wrist and base of fingers
        
        # Fingertip landmarks
        self.FINGERTIP_LANDMARKS = [4, 8, 12, 16, 20]
    
    def extract_hand_points(self, landmarks) -> List[Point]:
        """Extract key points from hand landmarks"""
        points = []
        
        if landmarks is not None:
            for landmark in landmarks:
                points.append(Point(landmark.x, landmark.y))
        
        return points
    
    def get_hand_bounding_box(self, landmarks) -> Optional[Rectangle]:
        """Get bounding box around hand landmarks"""
        if landmarks is None or len(landmarks) == 0:
            return None
        
        points = self.extract_hand_points(landmarks)
        if not points:
            return None
        
        # Find min/max coordinates
        min_x = min(point.x for point in points)
        max_x = max(point.x for point in points)
        min_y = min(point.y for point in points)
        max_y = max(point.y for point in points)
        
        return Rectangle(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y
        )
    
    def get_palm_center(self, landmarks) -> Optional[Point]:
        """Get center point of palm"""
        if landmarks is None:
            return None
        
        points = self.extract_hand_points(landmarks)
        if len(points) < len(self.PALM_LANDMARKS):
            return None
        
        # Calculate average of palm landmarks
        palm_points = [points[i] for i in self.PALM_LANDMARKS if i < len(points)]
        if not palm_points:
            return None
        
        avg_x = sum(point.x for point in palm_points) / len(palm_points)
        avg_y = sum(point.y for point in palm_points) / len(palm_points)
        
        return Point(avg_x, avg_y)
    
    def get_fingertips(self, landmarks) -> List[Point]:
        """Get fingertip positions"""
        if landmarks is None:
            return []
        
        points = self.extract_hand_points(landmarks)
        fingertips = []
        
        for tip_idx in self.FINGERTIP_LANDMARKS:
            if tip_idx < len(points):
                fingertips.append(points[tip_idx])
        
        return fingertips
    
    def calculate_hand_area(self, landmarks) -> float:
        """Calculate approximate hand area using convex hull"""
        if landmarks is None:
            return 0.0
        
        points = self.extract_hand_points(landmarks)
        if len(points) < 3:
            return 0.0
        
        # Convert to numpy array for convex hull calculation
        point_array = np.array([[p.x, p.y] for p in points])
        
        try:
            from scipy.spatial import ConvexHull
            hull = ConvexHull(point_array)
            return hull.volume  # In 2D, volume is actually area
        except:
            # Fallback: use bounding box area
            bbox = self.get_hand_bounding_box(landmarks)
            return bbox.area() if bbox else 0.0


class ZoneIntersectionCalculator:
    """Calculate hand-zone intersections with various methods"""
    
    def __init__(self):
        self.hand_processor = HandLandmarkProcessor()
    
    def point_in_zone_intersection(self, landmarks, zone_rect: Rectangle, 
                                 confidence_threshold: float = 0.7) -> Dict:
        """Check intersection using key points (fast method)"""
        result = {
            'intersecting': False,
            'confidence': 0.0,
            'intersection_points': [],
            'method': 'point_in_zone'
        }
        
        if landmarks is None:
            return result
        
        # Get key points
        palm_center = self.hand_processor.get_palm_center(landmarks)
        fingertips = self.hand_processor.get_fingertips(landmarks)
        
        intersection_points = []
        
        # Check palm center
        if palm_center and zone_rect.contains_point(palm_center):
            intersection_points.append('palm_center')
        
        # Check fingertips
        for i, tip in enumerate(fingertips):
            if zone_rect.contains_point(tip):
                intersection_points.append(f'fingertip_{i}')
        
        # Calculate confidence based on number of intersecting points
        total_points = 1 + len(fingertips)  # palm + fingertips
        confidence = len(intersection_points) / total_points
        
        result.update({
            'intersecting': confidence >= confidence_threshold,
            'confidence': confidence,
            'intersection_points': intersection_points
        })
        
        return result
    
    def bounding_box_intersection(self, landmarks, zone_rect: Rectangle,
                                confidence_threshold: float = 0.5) -> Dict:
        """Check intersection using bounding box overlap (medium accuracy)"""
        result = {
            'intersecting': False,
            'confidence': 0.0,
            'overlap_area': 0.0,
            'method': 'bounding_box'
        }
        
        if landmarks is None:
            return result
        
        # Get hand bounding box
        hand_bbox = self.hand_processor.get_hand_bounding_box(landmarks)
        if hand_bbox is None:
            return result
        
        # Calculate intersection
        if zone_rect.intersects_rectangle(hand_bbox):
            overlap_area = zone_rect.intersection_area(hand_bbox)
            hand_area = hand_bbox.area()
            
            # Confidence based on overlap ratio
            confidence = (overlap_area / hand_area) if hand_area > 0 else 0.0
            
            result.update({
                'intersecting': confidence >= confidence_threshold,
                'confidence': confidence,
                'overlap_area': overlap_area
            })
        
        return result
    
    def hybrid_intersection(self, landmarks, zone_rect: Rectangle,
                          confidence_threshold: float = 0.6) -> Dict:
        """Hybrid method combining point and bounding box detection"""
        result = {
            'intersecting': False,
            'confidence': 0.0,
            'method': 'hybrid',
            'point_result': {},
            'bbox_result': {}
        }
        
        if landmarks is None:
            return result
        
        # Get results from both methods
        point_result = self.point_in_zone_intersection(landmarks, zone_rect, 0.3)
        bbox_result = self.bounding_box_intersection(landmarks, zone_rect, 0.3)
        
        # Combine confidences with weighted average
        point_weight = 0.7  # Favor point-based detection
        bbox_weight = 0.3
        
        combined_confidence = (point_result['confidence'] * point_weight +
                             bbox_result['confidence'] * bbox_weight)
        
        result.update({
            'intersecting': combined_confidence >= confidence_threshold,
            'confidence': combined_confidence,
            'point_result': point_result,
            'bbox_result': bbox_result
        })
        
        return result


def normalize_coordinates(x: float, y: float, width: int, height: int) -> Tuple[float, float]:
    """Convert pixel coordinates to normalized coordinates (0-1)"""
    return (x / width, y / height)


def denormalize_coordinates(x: float, y: float, width: int, height: int) -> Tuple[int, int]:
    """Convert normalized coordinates to pixel coordinates"""
    return (int(x * width), int(y * height))


def create_zone_from_points(start_point: Tuple[float, float], 
                          end_point: Tuple[float, float]) -> Rectangle:
    """Create zone rectangle from two corner points"""
    x1, y1 = start_point
    x2, y2 = end_point
    
    # Ensure correct order
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    
    return Rectangle(left, top, width, height)