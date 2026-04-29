"""
Test script to run the full Genetic Algorithm for timetable optimization
"""
import sys
import os
import time

# Add parent directory to path to import GA module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ga.algorithm import GASearch
from test_data import create_test_data


def run_full_ga_test():
    """Run the complete genetic algorithm with test data"""
    
    print("\n" + "="*80)
    print("FULL GENETIC ALGORITHM TEST")
    print("="*80)
    
    # Get test data
    print("\n[SETUP] Loading test data...")
    test_data = create_test_data()
    
    print(f"  - Instructors: {len(test_data['instructors'])}")
    print(f"  - Rooms: {len(test_data['rooms'])}")
    print(f"  - Student Groups: {len(test_data['student_groups'])}")
    print(f"  - Courses: {len(test_data['courses'])}")
    print(f"  - Time Slots: {test_data['time_slots']}")
    print(f"  - Objective Weights: {test_data['objective_function_weights']}")
    
    # Initialize GA
    print("\n[SETUP] Initializing GA Search...")
    ga = GASearch(
        time_slots=test_data['time_slots'],
        courses=test_data['courses'],
        preference_bins=test_data['preference_bins'],
        objective_function_weights=test_data['objective_function_weights'],
        rooms=test_data['rooms'],
        population_size=500,           # Start with small population for testing
        generations=100,              # Max 100 generations
        mutation_rate=0.1
    )
    
    # Run the GA
    print("\n[EXECUTION] Starting GA run...")
    start_time = time.time()
    
    best_timetable, best_fitness = ga.run(
        convergence_threshold=0.1,   # Stop if improvement < 0.1
        min_generations=20,           # At least 3 generations
    )
    
    elapsed_time = time.time() - start_time
    
    # Display results
    print("\n" + "="*80)
    print("GA TEST RESULTS")
    print("="*80)
    
    if best_timetable is None:
        print("✗ GA failed to find a valid solution")
        return False
    
    print(f"✓ GA completed successfully in {elapsed_time:.2f} seconds")
    print(f"\nBest Fitness Found: {best_fitness:.2f}")
    
    # Display the best timetable found
    print("\n" + "-"*80)
    print("BEST TIMETABLE")
    print("-"*80)
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for day in days:
        print(f"\n{day}:")
        day_slots = best_timetable[day]
        for slot in sorted(day_slots.keys()):
            courses_in_slot = day_slots[slot]
            if courses_in_slot:
                course_names = [f"{c.course_id}-{c.session_type}({c.student_grp.name})-{c.room.name}" for c in courses_in_slot]
                print(f"  Slot {slot}: {course_names}")
            else:
                print(f"  Slot {slot}: [empty]")
    
    # Verify constraints
    print("\n" + "-"*80)
    print("CONSTRAINT VERIFICATION")
    print("-"*80)
    
    is_valid = ga.check_constraints(best_timetable, verbose=True)
    
    if is_valid:
        print("\n✓ Best timetable satisfies all constraints!")
    else:
        print("\n✗ Best timetable has constraint violations!")
        return False
    
    # Fitness breakdown
    print("\n" + "-"*80)
    print("FITNESS BREAKDOWN")
    print("-"*80)
    
    ptp_penalty = ga._ptp_objective_function(best_timetable)
    rtr_penalty = ga._rtr_objective_function(best_timetable)
    ctrr_penalty = ga._ctrr_objective_function(best_timetable)
    
    weights = ga.objective_function_weights
    
    print(f"\nPTP (Professor Time Preference) Penalty: {ptp_penalty:.2f}")
    print(f"  Weight: {weights[0]}, Weighted: {weights[0] * ptp_penalty:.2f}")
    
    print(f"\nRTR (Room-to-Room Travel) Penalty: {rtr_penalty:.2f}")
    print(f"  Weight: {weights[1]}, Weighted: {weights[1] * rtr_penalty:.2f}")
    
    print(f"\nCTRR (Course Time-Room Consistency) Penalty: {ctrr_penalty:.2f}")
    print(f"  Weight: {weights[2]}, Weighted: {weights[2] * ctrr_penalty:.2f}")
    
    print(f"\nTotal Fitness: {best_fitness:.2f}")
    
    # Schedule statistics
    print("\n" + "-"*80)
    print("SCHEDULE STATISTICS")
    print("-"*80)
    
    total_courses_scheduled = 0
    total_slots_used = 0
    
    for day in days:
        day_slots = best_timetable[day]
        for slot in day_slots.keys():
            if day_slots[slot]:
                total_slots_used += 1
                total_courses_scheduled += len(day_slots[slot])
    
    total_day_slots = sum(len(best_timetable[day]) for day in days)
    total_possible_slots = total_day_slots
    
    print(f"\nCourses scheduled: {total_courses_scheduled}")
    print(f"Slots used: {total_slots_used}/{total_possible_slots}")
    print(f"Slot utilization: {(total_slots_used / total_possible_slots * 100):.1f}%")
    
    print("\n" + "="*80)
    print("✓ GA TEST COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    success = run_full_ga_test()
    sys.exit(0 if success else 1)
