"""
Process Management System for NextSight v2
Manages processes with associated pick and drop zones
"""

import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
import logging

from nextsight.zones.zone_config import Zone, ZoneType


@dataclass
class Process:
    """Data class representing a process with pick and drop zones"""
    
    id: str
    name: str
    pick_zone_id: Optional[str] = None
    drop_zone_id: Optional[str] = None
    created_at: float = 0.0
    active: bool = True
    completed_count: int = 0
    error_count: int = 0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()


class ProcessManager(QObject):
    """Manages processes and their associated pick/drop zones"""
    
    # Signals
    process_created = pyqtSignal(object)  # Process
    process_deleted = pyqtSignal(str)     # process_id
    process_updated = pyqtSignal(object)  # Process
    process_completed = pyqtSignal(str, str)  # process_id, message
    process_error = pyqtSignal(str, str)      # process_id, error_message
    status_message = pyqtSignal(str, str)     # message, color ('green' or 'red')
    
    def __init__(self, config_file: str = "processes.json"):
        super().__init__()
        
        self.config_file = config_file
        self.processes: Dict[str, Process] = {}
        self.process_counter = 1
        
        # Track ongoing operations
        self.active_picks: Dict[str, Tuple[str, str]] = {}  # hand_id -> (process_id, zone_id)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Process Manager initialized")
        
        # Load existing processes
        self.load_processes()
    
    def create_process(self, name: Optional[str] = None) -> Process:
        """Create a new process"""
        process_id = f"process_{self.process_counter}"
        if name is None:
            name = f"Process {self.process_counter}"
        
        process = Process(
            id=process_id,
            name=name
        )
        
        self.processes[process_id] = process
        self.process_counter += 1
        
        self.logger.info(f"Created process: {process.name} ({process.id})")
        self.process_created.emit(process)
        self.save_processes()
        
        return process
    
    def delete_process(self, process_id: str) -> bool:
        """Delete a process and return list of associated zone IDs to delete"""
        if process_id not in self.processes:
            return False
        
        process = self.processes[process_id]
        
        # Clear any active picks for this process
        hands_to_clear = []
        for hand_id, (p_id, _) in self.active_picks.items():
            if p_id == process_id:
                hands_to_clear.append(hand_id)
        
        for hand_id in hands_to_clear:
            del self.active_picks[hand_id]
        
        # Remove from processes
        del self.processes[process_id]
        
        self.logger.info(f"Deleted process: {process.name} ({process.id})")
        self.process_deleted.emit(process_id)
        self.save_processes()
        
        return True
    
    def get_process_zone_ids(self, process_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Get pick and drop zone IDs for a process"""
        if process_id not in self.processes:
            return None, None
        
        process = self.processes[process_id]
        return process.pick_zone_id, process.drop_zone_id
    
    def associate_zones(self, process_id: str, pick_zone_id: str, drop_zone_id: str) -> bool:
        """Associate pick and drop zones with a process"""
        if process_id not in self.processes:
            return False
        
        process = self.processes[process_id]
        process.pick_zone_id = pick_zone_id
        process.drop_zone_id = drop_zone_id
        
        self.logger.info(f"Associated zones with {process.name}: pick={pick_zone_id}, drop={drop_zone_id}")
        self.process_updated.emit(process)
        self.save_processes()
        
        return True
    
    def handle_pick_event(self, hand_id: str, zone_id: str) -> bool:
        """Handle a pick event in a zone"""
        # Find which process this zone belongs to
        process_id = self.get_process_id_for_pick_zone(zone_id)
        if not process_id:
            return False
        
        # Track this pick
        self.active_picks[hand_id] = (process_id, zone_id)
        
        self.logger.info(f"Pick event: {hand_id} picked from {zone_id} (process {process_id})")
        return True
    
    def handle_drop_event(self, hand_id: str, zone_id: str) -> bool:
        """Handle a drop event in a zone"""
        # Check if this hand has an active pick
        if hand_id not in self.active_picks:
            return False
        
        active_process_id, pick_zone_id = self.active_picks[hand_id]
        
        # Find which process this drop zone belongs to
        drop_process_id = self.get_process_id_for_drop_zone(zone_id)
        
        if not drop_process_id:
            return False
        
        # Check if drop is in the correct process
        if active_process_id == drop_process_id:
            # Correct process - success!
            process = self.processes[active_process_id]
            process.completed_count += 1
            
            success_message = f"OK: {process.name} completed"
            self.logger.info(f"Process completed: {success_message}")
            self.status_message.emit(success_message, "green")
            self.process_completed.emit(active_process_id, success_message)
            
            # Clear the active pick
            del self.active_picks[hand_id]
            
            self.process_updated.emit(process)
            self.save_processes()
            return True
        else:
            # Wrong process - error!
            process = self.processes[active_process_id]
            process.error_count += 1
            
            error_message = "NG: Wrong process"
            self.logger.warning(f"Process error: {error_message} (picked from {active_process_id}, dropped in {drop_process_id})")
            self.status_message.emit(error_message, "red")
            self.process_error.emit(active_process_id, error_message)
            
            # Clear the active pick
            del self.active_picks[hand_id]
            
            self.process_updated.emit(process)
            self.save_processes()
            return False
    
    def get_process_id_for_pick_zone(self, zone_id: str) -> Optional[str]:
        """Find which process a pick zone belongs to"""
        for process_id, process in self.processes.items():
            if process.pick_zone_id == zone_id:
                return process_id
        return None
    
    def get_process_id_for_drop_zone(self, zone_id: str) -> Optional[str]:
        """Find which process a drop zone belongs to"""
        for process_id, process in self.processes.items():
            if process.drop_zone_id == zone_id:
                return process_id
        return None
    
    def get_all_processes(self) -> List[Process]:
        """Get all processes"""
        return list(self.processes.values())
    
    def get_process(self, process_id: str) -> Optional[Process]:
        """Get process by ID"""
        return self.processes.get(process_id)
    
    def get_process_by_name(self, name: str) -> Optional[Process]:
        """Get process by name"""
        for process in self.processes.values():
            if process.name == name:
                return process
        return None
    
    def clear_hand_tracking(self, hand_id: str) -> bool:
        """Clear hand tracking when hand exits frame"""
        if hand_id in self.active_picks:
            process_id, zone_id = self.active_picks[hand_id]
            del self.active_picks[hand_id]
            self.logger.info(f"Cleared hand tracking for {hand_id} (was in process {process_id})")
            return True
        return False
    
    def get_active_picks_info(self) -> Dict[str, Dict]:
        """Get information about active picks"""
        info = {}
        for hand_id, (process_id, zone_id) in self.active_picks.items():
            process = self.processes.get(process_id)
            info[hand_id] = {
                'process_id': process_id,
                'process_name': process.name if process else 'Unknown',
                'pick_zone_id': zone_id
            }
        return info
    
    def get_next_process_number(self) -> int:
        """Get the next process number to be used"""
        return self.process_counter
    
    def save_processes(self) -> bool:
        """Save processes to file"""
        try:
            data = {
                'process_counter': self.process_counter,
                'processes': {pid: asdict(process) for pid, process in self.processes.items()}
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to save processes: {e}")
            return False
    
    def load_processes(self) -> bool:
        """Load processes from file"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            self.process_counter = data.get('process_counter', 1)
            
            processes_data = data.get('processes', {})
            self.processes = {}
            
            for pid, process_data in processes_data.items():
                process = Process(**process_data)
                self.processes[pid] = process
            
            self.logger.info(f"Loaded {len(self.processes)} processes from {self.config_file}")
            return True
            
        except FileNotFoundError:
            self.logger.info(f"No existing process configuration found at {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load processes: {e}")
            return False
    
    def clear_all_processes(self) -> bool:
        """Clear all processes"""
        process_ids = list(self.processes.keys())
        
        for process_id in process_ids:
            self.delete_process(process_id)
        
        self.active_picks.clear()
        self.process_counter = 1
        
        self.logger.info("All processes cleared")
        self.save_processes()
        return True
    
    def get_statistics(self) -> Dict:
        """Get process statistics"""
        total_processes = len(self.processes)
        total_completed = sum(p.completed_count for p in self.processes.values())
        total_errors = sum(p.error_count for p in self.processes.values())
        active_picks = len(self.active_picks)
        
        return {
            'total_processes': total_processes,
            'total_completed': total_completed,
            'total_errors': total_errors,
            'active_picks': active_picks,
            'success_rate': (total_completed / (total_completed + total_errors)) * 100 if (total_completed + total_errors) > 0 else 0.0
        }