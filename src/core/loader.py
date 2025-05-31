import json
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, FrozenSet

def load_instance(file_path: str) -> Dict:
    """Load a Beluga problem instance from a JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Print basic instance information for verification
    print(f"Loaded instance with {len(data.get('racks', []))} racks")
    print(f"Number of jigs: {len(data.get('jigs', {}).keys())}")
    print(f"Number of flights: {len(data.get('flights', []))}")
    
    return data

def extract_initial_state_data(instance_data: Dict) -> Dict:
    """Extract relevant information for initial state creation."""
    initial_data = {}
    
    # Extract rack information
    initial_data['racks'] = {}
    for rack in instance_data.get('racks', []):
        rack_id = rack.get('name')  # Changed from 'id' to 'name'
        initial_data['racks'][rack_id] = {
            'size': rack.get('size'),
            'jigs': rack.get('jigs', []),
            # Need to determine which racks are factory_side and beluga_side
            # For simplicity, assuming racks are accessible from both sides
            'factory_side': True,
            'beluga_side': True
        }
    
    # Extract jig information
    initial_data['jigs'] = {}
    for jig_id, jig_data in instance_data.get('jigs', {}).items():  # Changed structure
        initial_data['jigs'][jig_id] = {
            'type': jig_data.get('type'),
            'loaded': not jig_data.get('empty', False),  # Note the inversion: 'empty' -> 'loaded'
            'part': jig_id if not jig_data.get('empty', False) else None  # Each loaded jig carries a part with the same ID
        }
    
    # Extract flight information
    initial_data['flights'] = []
    for flight in instance_data.get('flights', []):
        initial_data['flights'].append({
            'id': flight.get('name'),  # Changed from 'id' to 'name'
            'incoming': flight.get('incoming', []),
            'outgoing': flight.get('outgoing', []),
            # No arrival_time in this instance format, so using the index
            'arrival_time': None
        })
    
    # Extract production schedule from production lines
    initial_data['production_schedule'] = []
    for line in instance_data.get('production_lines', []):
        initial_data['production_schedule'].extend(line.get('schedule', []))
    
    # Other relevant info
    initial_data['beluga'] = {
        'trailers': [trailer.get('name') for trailer in instance_data.get('trailers_beluga', [])]
    }
    initial_data['factory'] = {
        'trailers': [trailer.get('name') for trailer in instance_data.get('trailers_factory', [])],
        'hangars': instance_data.get('hangars', [])
    }
    
    # Add jig_types information
    initial_data['jig_types'] = instance_data.get('jig_types', {})
    
    return initial_data

if __name__ == "__main__":
    # Test the loading function
    instance_data = load_instance("problem_4_s46_j23_r2_oc51_f6.json")
    initial_state_data = extract_initial_state_data(instance_data)
    print("Successfully extracted initial state data!")