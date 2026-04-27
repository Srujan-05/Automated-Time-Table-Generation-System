"""
Test the MOEA (NSGA-II) implementation.
"""
import sys
import time
from tests.test_data import create_test_data  # adjust import as needed
from ga.moea import MOEAGASearch
import time
start = time.time()


def test_moea():
    data = create_test_data()

    moea = MOEAGASearch(
        time_slots=data['time_slots'],
        courses=data['courses'],
        preference_bins=data['preference_bins'],
        objective_function_weights=data['objective_function_weights'],  # kept for compatibility, not used in MOEA fitness
        rooms=data['rooms'],
        population_size=10,
        generations=5,
        mutation_rate=0.1
    )

    print("=" * 80)
    print("TESTING MOEA (NSGA-II)")
    print("=" * 80)

    start = time.time()
    pareto_set, pareto_fitness = moea.run(generations=10)
    elapsed = time.time() - start

    print(f"\nDone in {elapsed:.2f} seconds")
    print(f"Pareto front size: {len(pareto_set)}")
    print("\nPareto front fitness vectors (PTP, RTR, CTRR):")
    for i, vec in enumerate(pareto_fitness):
        print(f"  {i+1}: {vec}")

    # Optional: display the first Pareto timetable
    if pareto_set:
        print("\nExample Pareto timetable (first individual):")
        tt = pareto_set[0]
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            print(f"  {day}:")
            for slot in sorted(tt[day].keys()):
                courses = tt[day][slot]
                if courses:
                    names = [f"{c.course_id}-{c.session_type}({c.student_grp.name})" for c in courses]
                    print(f"    Slot {slot}: {names}")
    
    print(f"Parallel MOEA took {time.time()-start:.2f} seconds")

if __name__ == "__main__":
    test_moea()