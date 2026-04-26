#!/usr/bin/env python3
"""
Simple test to check if the genetic algorithm module can be imported
"""

print("Starting import test...")

try:
    print("Attempting to import GASearch...")
    from ga.algorithm import GASearch
    print("✓ GASearch imported successfully")
    
    print("\nAttempting to create test data...")
    from test_data import create_test_data
    print("✓ Test data module imported successfully")
    
    print("\nCreating test data...")
    data = create_test_data()
    print(f"✓ Test data created: {len(data['courses'])} courses, {len(data['rooms'])} rooms")
    
    print("\nInitializing GASearch...")
    ga = GASearch(
        time_slots=data['time_slots'],
        courses=data['courses'][:2],  # Start with just 2 courses
        preference_bins=data['preference_bins'],
        objective_function_weights=data['objective_function_weights'],
        rooms=data['rooms'],
        population_size=1,
        generations=1,
        mutation_rate=0.1
    )
    print("✓ GASearch initialized")
    
    print("\nAttempting to create one timetable...")
    timetable = ga._generate_random_timetable()
    if timetable:
        print("✓ Timetable generated successfully")
        print(f"  - Monday slots: {len(timetable['Monday'])} slots")
    else:
        print("✗ Failed to generate timetable (returned None)")
    
    print("\n✓ All basic tests passed!")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
