import heapq
from collections import defaultdict
import time
from src.search.heuristic import heuristic
from src.search.goal import is_goal_state, check_goal_progress
from src.core.actions import MoveJigBetweenRacks, LoadJigToBeluga, UnloadJigFromBeluga, SendJigToProduction, ReturnEmptyJigFromFactory, ProcessNextFlight

class PriorityQueue:
    """A priority queue implementation for the A* search."""
    
    def __init__(self):
        self.elements = []
        self.entry_count = 0  # Used to break ties consistently
    
    def is_empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        # Add entry_count to break ties and ensure FIFO behavior for equal priorities
        heapq.heappush(self.elements, (priority, self.entry_count, item))
        self.entry_count += 1
    
    def get(self):
        # Return the item, discarding priority and entry_count
        return heapq.heappop(self.elements)[2]

def get_all_possible_actions(state, instance_data):
    """Generate all possible actions from the current state."""
    actions = []
    
    # 1. Generate MoveJigBetweenRacks actions
    for from_rack_id, jigs in state.rack_jigs.items():
        if not jigs:
            continue
        
        # Check jigs at the edges
        for jig_id in [jigs[0], jigs[-1]] if len(jigs) > 0 else []:
            if jig_id not in jigs:
                continue  # Skip if jig not found (shouldn't happen)
            
            # Try moving to each other rack
            for to_rack_id in state.rack_jigs.keys():
                if from_rack_id != to_rack_id:
                    action = MoveJigBetweenRacks(jig_id, from_rack_id, to_rack_id)
                    if state.is_valid_action(action, instance_data):
                        actions.append(action)
    
    # 2. Generate SendJigToProduction actions
    production_schedule = []
    for line in instance_data.get('production_lines', []):
        production_schedule.extend(line.get('schedule', []))
    
    for rack_id, jigs in state.rack_jigs.items():
        if not jigs:
            continue
        
        # Check jigs at factory-side edge (here we assume the first jig is factory-side)
        if len(jigs) > 0:
            jig_id = jigs[0]  # Factory-side jig
            
            # Check if jig is in production schedule and still loaded
            loaded, part_id = state.jig_status.get(jig_id, (False, ""))
            if jig_id in production_schedule and loaded:
                action = SendJigToProduction(jig_id, rack_id)
                if state.is_valid_action(action, instance_data):
                    actions.append(action)
    
    # 3. Generate ReturnEmptyJigFromFactory actions
    for jig_id in state.factory_jigs:
        # Check if jig is empty
        loaded, _ = state.jig_status.get(jig_id, (False, ""))
        if not loaded:
            # Try returning to each rack
            for rack_id in state.rack_jigs.keys():
                action = ReturnEmptyJigFromFactory(jig_id, rack_id)
                if state.is_valid_action(action, instance_data):
                    actions.append(action)
    
    # 4. Generate ProcessNextFlight action if not at the last flight
    if state.current_flight_idx < len(instance_data.get('flights', [])) - 1:
        action = ProcessNextFlight()
        if state.is_valid_action(action, instance_data):
            actions.append(action)
    
    # 5. Generate LoadJigToBeluga and UnloadJigFromBeluga actions 
    for jig_id in state.beluga_jigs:
        # Check if jig is loaded
        loaded, _ = state.jig_status.get(jig_id, (False, ""))
        if loaded:
            # Unload from Beluga
            action = UnloadJigFromBeluga(jig_id)
            if state.is_valid_action(action, instance_data):
                actions.append(action)
        else:
            # Load to Beluga
            action = LoadJigToBeluga(jig_id)
            if state.is_valid_action(action, instance_data):
                actions.append(action)
    
    return actions

def astar_search(initial_state, instance_data, max_iterations=10000, time_limit=60):
    """
    Perform A* search to find the optimal plan.
    
    Args:
        initial_state: The starting state
        instance_data: The problem instance data
        max_iterations: Maximum number of iterations (default: 10000)
        time_limit: Time limit in seconds (default: 60)
    
    Returns:
        List of actions forming the plan, or None if no plan found
    """
    print("Starting A* search...")
    start_time = time.time()
    
    # Initialize data structures
    open_set = PriorityQueue()
    open_set.put(initial_state, 0)
    
    came_from = {}  # Maps state -> (previous_state, action)
    cost_so_far = {initial_state: 0}
    
    iterations = 0
    states_explored = 0
    
    # Main A* search loop
    while not open_set.is_empty() and iterations < max_iterations:
        iterations += 1
        
        # Check time limit
        if time.time() - start_time > time_limit:
            print(f"Time limit of {time_limit} seconds reached. Aborting search.")
            return None
        
        # Get the state with lowest estimated total cost
        current_state = open_set.get()
        states_explored += 1
        
        # Check for goal state
        if is_goal_state(current_state, instance_data):
            print(f"Goal reached after {iterations} iterations!")
            print(f"Total states explored: {states_explored}")
            print(f"Search time: {time.time() - start_time:.2f} seconds")
            
            # Reconstruct the plan
            return reconstruct_plan(came_from, current_state)
        
        # Print progress every 100 iterations
        if iterations % 100 == 0:
            progress = check_goal_progress(current_state, instance_data)
            print(f"Iteration {iterations}: Flights: {progress['flights_progress']}, Parts: {progress['parts_progress']}")
        
        # Generate all possible actions
        for action in get_all_possible_actions(current_state, instance_data):
            # Get resulting state
            next_state = current_state.get_next_state(action, instance_data)
            if next_state is None:
                continue  # Invalid action/state
            
            # Calculate cost
            new_cost = cost_so_far[current_state] + 1  # Uniform cost
            
            # If state is new or we found a better path
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                # Calculate priority using heuristic
                priority = new_cost + heuristic(next_state, instance_data)
                open_set.put(next_state, priority)
                came_from[next_state] = (current_state, action)
    
    # If we got here, search failed
    print(f"Search failed after {iterations} iterations.")
    print(f"Total states explored: {states_explored}")
    print(f"Search time: {time.time() - start_time:.2f} seconds")
    return None

def reconstruct_plan(came_from, goal_state):
    """
    Reconstruct the plan by working backwards from the goal state.
    """
    actions = []
    current_state = goal_state
    
    while current_state in came_from:
        previous_state, action = came_from[current_state]
        actions.append(action)
        current_state = previous_state
    
    # Reverse the list since we worked backwards
    actions.reverse()
    return actions