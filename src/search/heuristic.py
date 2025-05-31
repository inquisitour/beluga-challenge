def heuristic(state, instance_data):
    """
    Calculate a heuristic estimate of steps needed to reach the goal.
    This is an admissible heuristic for the A* search.
    """
    # Count how many steps needed at minimum to reach the goal
    cost = 0
    
    # Get flights and production schedule info
    flights = instance_data.get('flights', [])
    flights_remaining = max(0, len(flights) - state.current_flight_idx - 1)
    
    # Collect production schedule
    production_schedule = []
    for line in instance_data.get('production_lines', []):
        production_schedule.extend(line.get('schedule', []))
    
    # 1. Estimate cost for unloading incoming jigs from current flight
    if state.current_flight_idx < len(flights):
        current_flight = flights[state.current_flight_idx]
        incoming_jigs = current_flight.get('incoming', [])
        # Each incoming jig needs to be unloaded (1 action)
        cost += len(incoming_jigs)
    
    # 2. Estimate cost for required production
    parts_to_produce = []
    for jig_id in production_schedule:
        # Only count parts that haven't been produced yet
        loaded, part_id = state.jig_status.get(jig_id, (False, ""))
        if loaded and part_id and part_id not in state.produced_parts:
            parts_to_produce.append(part_id)
    
    # Each part needs at least 1 step to send to production
    cost += len(parts_to_produce)
    
    # 3. Estimate cost for loading outgoing jigs to remaining flights
    total_outgoing_jigs = 0
    for i in range(state.current_flight_idx, len(flights)):
        total_outgoing_jigs += len(flights[i].get('outgoing', []))
    
    # Each outgoing jig requires at least 1 step to load
    cost += total_outgoing_jigs
    
    # 4. Estimate for remaining flight processing
    cost += flights_remaining
    
    # 5. Add estimate for jig swaps needed (very simplified)
    # For each part in the production schedule that's blocked by another jig
    # add a cost of 2 (1 for the swap, 1 for the move to production)
    blocked_jigs_estimate = 0
    for rack_id, jigs in state.rack_jigs.items():
        for i, jig_id in enumerate(jigs):
            # If jig is not at an edge and it's in the production schedule
            if i > 0 and i < len(jigs) - 1 and jig_id in production_schedule:
                blocked_jigs_estimate += 2
    
    cost += blocked_jigs_estimate
    
    return cost