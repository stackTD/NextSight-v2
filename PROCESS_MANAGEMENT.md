# NextSight v2 - Process Management System

This document describes the comprehensive process management system implemented for NextSight v2.

## Overview

The Process Management System enables users to create and manage pick-and-drop workflows with automated validation and tracking. Each process consists of a pick zone and a drop zone, and the system enforces correct workflow execution while providing real-time feedback.

## Key Features

### 1. Process Creation and Management
- Create named processes through the UI
- Automatic zone creation flow (Pick Zone → Drop Zone)
- Process listing with status indicators
- Process deletion with automatic zone cleanup

### 2. Zone Integration
- Each process has exactly one pick zone and one drop zone
- Process-specific zone naming (e.g., "Pick Zone 1", "Drop Zone 1")
- Integration with existing zone management system
- Visual zone creation with mouse interaction

### 3. Workflow Validation
- **Success Case**: Hand picks from Pick Zone N and drops in Drop Zone N
  - Shows "OK: Process N completed" in green
- **Error Case**: Hand picks from Pick Zone N and drops in different zone
  - Shows "NG: Wrong process" in red
- Hand consistency enforcement (same hand must complete pick-drop sequence)

### 4. Real-time Status Display
- Color-coded process completion messages in status bar
- Process statistics (completed operations, errors, success rate)
- Active picks tracking
- Visual feedback for zone interactions

### 5. Control Panel Integration
- Mode dropdown: "Detection" (default) and "Processes"
- "Create Process +" button in Processes mode
- Process list with delete functionality
- Seamless switching between detection and process management

## Architecture

### Core Components

#### ProcessManager (`nextsight/core/process_manager.py`)
- Core process logic and state management
- Pick/drop event handling and validation
- Statistics tracking and persistence
- Process-zone association management

#### ProcessManagementWidget (`nextsight/ui/process_widget.py`)
- Process creation and listing UI
- Process deletion with confirmation
- Status indicators for zone configuration

#### EnhancedControlPanel (`nextsight/ui/control_panel.py`)
- Mode switching (Detection/Processes)
- Integrated process management interface
- Maintains backward compatibility with detection controls

#### Status Bar Integration (`nextsight/ui/status_bar.py`)
- Process completion message display
- Color-coded feedback (green/red)
- Automatic message timeout

### Integration Points

1. **Zone Manager Integration**
   - Custom zone naming for processes
   - Process-specific zone creation flow
   - Zone deletion coordination

2. **Application Integration**
   - Process creation workflow
   - Zone creation completion handling
   - Signal routing between components

3. **Detection System Integration**
   - Pick/drop event generation from zone intersections
   - Hand tracking consistency
   - Gesture-based interaction detection

## Usage Workflow

### Creating a Process

1. Switch to "Processes" mode in the control panel dropdown
2. Click "Create Process +" button
3. Enter process name (optional - defaults to "Process N")
4. System prompts to create pick zone
5. Click and drag on camera view to create pick zone
6. System automatically prompts to create drop zone
7. Click and drag on camera view to create drop zone
8. Process creation complete with confirmation message

### Using a Process

1. Ensure hand detection is active
2. Hand performs pick gesture in Pick Zone N
3. System tracks the pick operation
4. Hand moves to Drop Zone N and performs drop gesture
5. System validates correct process and shows success message
6. If wrong drop zone is used, system shows error message

### Managing Processes

- **View Processes**: Switch to "Processes" mode to see all processes
- **Process Status**: Each process shows zone configuration status
- **Delete Process**: Click "Delete" button on any process
- **Statistics**: View completion counts and error rates

## Technical Implementation

### Process Data Model

```python
@dataclass
class Process:
    id: str                    # Unique identifier (e.g., "process_1")
    name: str                  # User-friendly name
    pick_zone_id: str         # Associated pick zone ID
    drop_zone_id: str         # Associated drop zone ID
    created_at: float         # Creation timestamp
    active: bool              # Process active status
    completed_count: int      # Successful completions
    error_count: int          # Error count
```

### Event Flow

1. **Zone Intersection Detection** → Pick/Drop Events
2. **Process Manager** → Validates process logic
3. **Status Messages** → User feedback
4. **Statistics Update** → Performance tracking

### Configuration Persistence

- Processes saved to `processes.json`
- Automatic loading on application start
- Process counter persistence for unique naming

## Error Handling

### Validation Scenarios

- **No Active Pick**: Drop event without preceding pick (ignored)
- **Wrong Process**: Pick from Process A, drop in Process B (error)
- **Hand Consistency**: Different hand completes pick-drop sequence (error)
- **Zone Deletion**: Associated zones deleted when process is deleted

### Error Messages

- User-friendly error dialogs for creation failures
- Status bar messages for workflow violations
- Logging for debugging and monitoring

## Testing

### Unit Tests
- Process creation and deletion
- Zone association logic
- Pick/drop validation
- Statistics calculation
- Persistence functionality

### Integration Tests
- Complete workflow scenarios
- Multi-process operations
- Hand consistency tracking
- Complex error cases

### Demo Scripts
- `demo_process_management.py`: Comprehensive functionality demonstration
- `test_process_integration.py`: End-to-end workflow validation

## Performance Considerations

- Efficient zone lookup by process ID
- Minimal memory footprint for process tracking
- Fast validation algorithms
- Optimized UI updates

## Future Enhancements

- Process templates and cloning
- Advanced workflow patterns (multi-step processes)
- Performance analytics and reporting
- Integration with external systems
- Process scheduling and automation

## API Reference

### ProcessManager Methods

- `create_process(name: str) -> Process`
- `delete_process(process_id: str) -> bool`
- `associate_zones(process_id: str, pick_zone_id: str, drop_zone_id: str) -> bool`
- `handle_pick_event(hand_id: str, zone_id: str) -> bool`
- `handle_drop_event(hand_id: str, zone_id: str) -> bool`
- `get_statistics() -> Dict`

### Signals

- `process_created(Process)`
- `process_deleted(str)`
- `process_completed(str, str)`
- `process_error(str, str)`
- `status_message(str, str)`

---

This process management system provides a robust foundation for workflow automation and validation in computer vision applications.