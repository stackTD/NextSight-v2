"""
Test process management system implementation - Core logic only
"""

import json
import time
import tempfile
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


# Minimal version for testing without GUI dependencies
@dataclass
class TestProcess:
    """Test version of Process without GUI dependencies"""
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


class TestProcessManager:
    """Test version of ProcessManager without GUI dependencies"""
    
    def __init__(self, config_file: str = "test_processes.json"):
        self.config_file = config_file
        self.processes: Dict[str, TestProcess] = {}
        self.process_counter = 1
        self.active_picks: Dict[str, tuple] = {}  # hand_id -> (process_id, zone_id)
        self.load_processes()
    
    def create_process(self, name: Optional[str] = None) -> TestProcess:
        """Create a new process"""
        process_id = f"process_{self.process_counter}"
        if name is None:
            name = f"Process {self.process_counter}"
        
        process = TestProcess(id=process_id, name=name)
        self.processes[process_id] = process
        self.process_counter += 1
        self.save_processes()
        return process
    
    def delete_process(self, process_id: str) -> bool:
        """Delete a process"""
        if process_id not in self.processes:
            return False
        
        # Clear any active picks for this process
        hands_to_clear = []
        for hand_id, (p_id, _) in self.active_picks.items():
            if p_id == process_id:
                hands_to_clear.append(hand_id)
        
        for hand_id in hands_to_clear:
            del self.active_picks[hand_id]
        
        del self.processes[process_id]
        self.save_processes()
        return True
    
    def associate_zones(self, process_id: str, pick_zone_id: str, drop_zone_id: str) -> bool:
        """Associate pick and drop zones with a process"""
        if process_id not in self.processes:
            return False
        
        process = self.processes[process_id]
        process.pick_zone_id = pick_zone_id
        process.drop_zone_id = drop_zone_id
        self.save_processes()
        return True
    
    def get_process_zone_ids(self, process_id: str) -> tuple:
        """Get pick and drop zone IDs for a process"""
        if process_id not in self.processes:
            return None, None
        
        process = self.processes[process_id]
        return process.pick_zone_id, process.drop_zone_id
    
    def handle_pick_event(self, hand_id: str, zone_id: str) -> bool:
        """Handle a pick event in a zone"""
        process_id = self.get_process_id_for_pick_zone(zone_id)
        if not process_id:
            return False
        
        self.active_picks[hand_id] = (process_id, zone_id)
        return True
    
    def handle_drop_event(self, hand_id: str, zone_id: str) -> bool:
        """Handle a drop event in a zone"""
        if hand_id not in self.active_picks:
            return False
        
        active_process_id, pick_zone_id = self.active_picks[hand_id]
        drop_process_id = self.get_process_id_for_drop_zone(zone_id)
        
        if not drop_process_id:
            return False
        
        if active_process_id == drop_process_id:
            # Correct process - success!
            process = self.processes[active_process_id]
            process.completed_count += 1
            del self.active_picks[hand_id]
            self.save_processes()
            return True
        else:
            # Wrong process - error!
            process = self.processes[active_process_id]
            process.error_count += 1
            del self.active_picks[hand_id]
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
    
    def get_all_processes(self) -> List[TestProcess]:
        """Get all processes"""
        return list(self.processes.values())
    
    def get_process(self, process_id: str) -> Optional[TestProcess]:
        """Get process by ID"""
        return self.processes.get(process_id)
    
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
            print(f"Failed to save processes: {e}")
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
                process = TestProcess(**process_data)
                self.processes[pid] = process
            
            return True
            
        except FileNotFoundError:
            return True
        except Exception as e:
            print(f"Failed to load processes: {e}")
            return False


def test_process_manager_creation():
    """Test basic ProcessManager creation and functionality"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = TestProcessManager(config_file)
        
        # Test creating a process
        process = manager.create_process("Test Process")
        assert process is not None
        assert process.name == "Test Process"
        assert process.id == "process_1"
        assert process.pick_zone_id is None
        assert process.drop_zone_id is None
        
        # Test getting all processes
        processes = manager.get_all_processes()
        assert len(processes) == 1
        assert processes[0].id == process.id
        
        # Test process statistics
        stats = manager.get_statistics()
        assert stats['total_processes'] == 1
        assert stats['total_completed'] == 0
        assert stats['total_errors'] == 0
        
    finally:
        os.unlink(config_file)


def test_process_zone_association():
    """Test associating zones with processes"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = TestProcessManager(config_file)
        
        # Create process
        process = manager.create_process("Test Process")
        
        # Associate zones
        success = manager.associate_zones(process.id, "pick_zone_1", "drop_zone_1")
        assert success
        
        # Check association
        pick_zone_id, drop_zone_id = manager.get_process_zone_ids(process.id)
        assert pick_zone_id == "pick_zone_1"
        assert drop_zone_id == "drop_zone_1"
        
        # Test reverse lookup
        assert manager.get_process_id_for_pick_zone("pick_zone_1") == process.id
        assert manager.get_process_id_for_drop_zone("drop_zone_1") == process.id
        
    finally:
        os.unlink(config_file)


def test_process_pick_drop_logic():
    """Test process pick and drop event handling"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = TestProcessManager(config_file)
        
        # Create process and associate zones
        process = manager.create_process("Test Process")
        manager.associate_zones(process.id, "pick_zone_1", "drop_zone_1")
        
        # Test pick event
        success = manager.handle_pick_event("hand_1", "pick_zone_1")
        assert success
        
        # Check active picks
        active_picks = manager.get_active_picks_info()
        assert "hand_1" in active_picks
        assert active_picks["hand_1"]["process_id"] == process.id
        
        # Test correct drop event
        success = manager.handle_drop_event("hand_1", "drop_zone_1")
        assert success
        
        # Check statistics - should have one completion
        stats = manager.get_statistics()
        assert stats['total_completed'] == 1
        assert stats['total_errors'] == 0
        
        # Check active picks cleared
        active_picks = manager.get_active_picks_info()
        assert "hand_1" not in active_picks
        
    finally:
        os.unlink(config_file)


def test_process_wrong_drop_logic():
    """Test process error handling for wrong drop"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = TestProcessManager(config_file)
        
        # Create two processes
        process1 = manager.create_process("Process 1")
        process2 = manager.create_process("Process 2")
        
        manager.associate_zones(process1.id, "pick_zone_1", "drop_zone_1")
        manager.associate_zones(process2.id, "pick_zone_2", "drop_zone_2")
        
        # Pick from process 1
        manager.handle_pick_event("hand_1", "pick_zone_1")
        
        # Drop in process 2 (wrong process)
        success = manager.handle_drop_event("hand_1", "drop_zone_2")
        assert not success  # Should return False for wrong process
        
        # Check statistics - should have one error
        stats = manager.get_statistics()
        assert stats['total_completed'] == 0
        assert stats['total_errors'] == 1
        
    finally:
        os.unlink(config_file)


def test_process_deletion():
    """Test process deletion"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = TestProcessManager(config_file)
        
        # Create process
        process = manager.create_process("Test Process")
        manager.associate_zones(process.id, "pick_zone_1", "drop_zone_1")
        
        # Start a pick
        manager.handle_pick_event("hand_1", "pick_zone_1")
        
        # Delete process
        success = manager.delete_process(process.id)
        assert success
        
        # Check process is gone
        assert manager.get_process(process.id) is None
        assert len(manager.get_all_processes()) == 0
        
        # Check active picks cleared
        active_picks = manager.get_active_picks_info()
        assert "hand_1" not in active_picks
        
    finally:
        os.unlink(config_file)


def test_process_persistence():
    """Test saving and loading processes"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        # Create manager and processes
        manager1 = TestProcessManager(config_file)
        process1 = manager1.create_process("Process 1")
        process2 = manager1.create_process("Process 2")
        
        manager1.associate_zones(process1.id, "pick_1", "drop_1")
        manager1.associate_zones(process2.id, "pick_2", "drop_2")
        
        # Create new manager instance (should load from file)
        manager2 = TestProcessManager(config_file)
        
        # Check processes loaded
        processes = manager2.get_all_processes()
        assert len(processes) == 2
        
        # Check process counter continued correctly
        process3 = manager2.create_process("Process 3")
        assert process3.id == "process_3"
        
    finally:
        os.unlink(config_file)


if __name__ == "__main__":
    print("Running core process management tests...")
    
    test_process_manager_creation()
    print("✓ Process manager creation test passed")
    
    test_process_zone_association()
    print("✓ Process zone association test passed")
    
    test_process_pick_drop_logic()
    print("✓ Process pick/drop logic test passed")
    
    test_process_wrong_drop_logic()
    print("✓ Process wrong drop logic test passed")
    
    test_process_deletion()
    print("✓ Process deletion test passed")
    
    test_process_persistence()
    print("✓ Process persistence test passed")
    
    print("\nAll core process management tests completed successfully!")