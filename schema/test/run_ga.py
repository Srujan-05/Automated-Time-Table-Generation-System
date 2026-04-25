"""
Main GA Orchestrator

This is the entry point script that coordinates the entire workflow:
1. Load raw data from PostgreSQL (via preprocessor)
2. Run the Genetic Algorithm
3. Save the final optimized timetable back to PostgreSQL
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to sys.path to import schema modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from preprocessor import get_ga_inputs
from save_schedule import save_ga_output, print_timetable
from genetic_algorithm import GASearch


def main():
    print("\n" + "="*80)
    print("TIMETABLE GENERATION - GENETIC ALGORITHM WORKFLOW")
    print("="*80)
    
    # =========================================================================
    # STEP 1: Load GA Inputs from PostgreSQL
    # =========================================================================
    print("\n[STEP 1/4] Loading course requirements from PostgreSQL...")
    try:
        rooms, courses = get_ga_inputs()
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        print("\n   Make sure you ran: python db_setup.py")
        return
    
    # =========================================================================
    # STEP 2: Initialize the Genetic Algorithm
    # =========================================================================
    print("\n[STEP 2/4] Initializing Genetic Algorithm...")
    
    ga = GASearch(
        time_slots=10,  # 10 time slots per day (including 5:35-6:30pm slot from all_years.md)
        courses=courses,
        preference_bins={
            1: 1,   # Slot 1-3: Morning (bin 1) - 8:25-11:30
            2: 1,
            3: 1,
            4: 2,   # Slot 4-6: Noon (bin 2) - 11:35-2:30
            5: 2,
            6: 2,
            7: 3,   # Slot 7-10: Afternoon/Evening (bin 3) - 2:35-6:30
            8: 3,
            9: 3,
            10: 3
        },
        objective_function_weights=[1.0, 0.5, 0.8],  # [PTP, RTR, Stability]
        rooms=rooms,
        population_size=20,  # Larger population for bigger problem
        generations=10,      # More generations for better optimization
        mutation_rate=0.1
    )
    
    print(f"   ✓ GA initialized")
    print(f"      - Courses to schedule: {len(courses)}")
    print(f"      - Rooms available: {len(rooms)}")
    print(f"      - Total course-slots to fill: {sum([c.slots_req for c in courses])}")
    print(f"      - Time slots per day: 10")
    print(f"      - Total time slots available (Mon-Fri): 50")
    print(f"      - Population size: {ga.population_size}")
    print(f"      - Generations: {ga.generations}")
    
    # =========================================================================
    # STEP 3: Run the Genetic Algorithm
    # =========================================================================
    print("\n[STEP 3/4] Running Genetic Algorithm...")
    print("   (This may take a minute...)\n")
    
    best_timetable = ga.run()
    
    if not best_timetable:
        print("\n❌ GA failed to produce a valid timetable")
        return
    
    # =========================================================================
    # STEP 4: Save and Display Results
    # =========================================================================
    print("\n[STEP 4/4] Saving results to PostgreSQL...")
    
    # Calculate final fitness
    final_fitness = ga.fitness(best_timetable)
    
    # Save to database
    schedule_id = save_ga_output(
        best_timetable,
        fitness_score=final_fitness,
        schedule_name="GA_Optimized_Schedule"
    )
    
    # Display the timetable
    print_timetable(best_timetable)
    
    # Print summary
    print("\n" + "="*80)
    print("✅ WORKFLOW COMPLETE")
    print("="*80)
    print(f"\n📊 RESULTS:")
    print(f"   Schedule ID: {schedule_id}")
    print(f"   Final Fitness Score: {final_fitness:.2f}")
    print(f"   Courses Scheduled: {len(courses)}")
    print(f"   Rooms Used: {len(rooms)}")
    
    print(f"\n📍 Next Steps:")
    print(f"   1. Check PostgreSQL 'generated_schedules' table for stored output")
    print(f"   2. Modify db_setup.py to add more courses/rooms for fuller test")
    print(f"   3. Increase population_size and generations for better optimization")
    print(f"   4. Integrate with your React UI for visualization")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
