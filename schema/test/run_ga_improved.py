"""
Main GA Orchestrator - IMPROVED VERSION

This runs the improved GA with:
- Real crossover & mutation operators
- Preference-aware initialization
- Tournament selection
- Multi-generational evolution
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
from genetic_algorithm_improved import GASearchImproved


def main():
    print("\n" + "="*80)
    print("TIMETABLE GENERATION - IMPROVED GENETIC ALGORITHM WORKFLOW")
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
    # STEP 2: Initialize the IMPROVED Genetic Algorithm
    # =========================================================================
    print("\n[STEP 2/4] Initializing IMPROVED Genetic Algorithm...")
    
    ga = GASearchImproved(
        time_slots=10,  # 10 time slots per day
        courses=courses,
        preference_bins={
            1: 1,   # Slot 1-3: Morning (bin 1)
            2: 1,
            3: 1,
            4: 2,   # Slot 4-6: Noon (bin 2)
            5: 2,
            6: 2,
            7: 3,   # Slot 7-10: Evening (bin 3)
            8: 3,
            9: 3,
            10: 3
        },
        objective_function_weights=[1.5, 0.4, 0.2],  # IMPROVED: Focus on preferences, less strict stability
        rooms=rooms,
        population_size=30,  # Larger population for better diversity
        generations=20,      # More generations for evolution
        mutation_rate=0.2    # Higher mutation for exploration
    )
    
    print(f"   ✓ GA initialized")
    print(f"      - Courses to schedule: {len(courses)}")
    print(f"      - Rooms available: {len(rooms)}")
    print(f"      - Total course-slots to fill: {sum([c.slots_req for c in courses])}")
    print(f"      - Time slots per day: 10")
    print(f"      - Total time slots available (Mon-Fri): 50")
    print(f"      - Population size: {ga.population_size}")
    print(f"      - Generations: {ga.generations}")
    print(f"      - Mutation rate: {ga.mutation_rate}")
    print(f"      - Objective weights: PTP={ga.objective_function_weights[0]}, RTR={ga.objective_function_weights[1]}, Stability={ga.objective_function_weights[2]}")
    
    # =========================================================================
    # STEP 3: Run the IMPROVED Genetic Algorithm
    # =========================================================================
    print("\n[STEP 3/4] Running IMPROVED Genetic Algorithm...")
    print("   (Multi-generational evolution with crossover & mutation...)\n")
    
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
        schedule_name="GA_Improved_Schedule"
    )
    
    # Display the timetable
    print_timetable(best_timetable)
    
    # Print summary
    print("\n" + "="*80)
    print("✅ IMPROVED WORKFLOW COMPLETE")
    print("="*80)
    print(f"\n📊 RESULTS:")
    print(f"   Schedule ID: {schedule_id}")
    print(f"   Final Fitness Score: {final_fitness:.2f}")
    print(f"   Courses Scheduled: {len(courses)}")
    print(f"   Rooms Used: {len(rooms)}")
    
    print(f"\n📈 FITNESS HISTORY (per generation):")
    for gen, fitness in enumerate(ga.best_fitness_history, 1):
        print(f"   Generation {gen:2d}: {fitness:.2f}")
    
    improvement = ga.best_fitness_history[0] - ga.best_fitness_history[-1]
    print(f"\n   Initial fitness: {ga.best_fitness_history[0]:.2f}")
    print(f"   Final fitness: {ga.best_fitness_history[-1]:.2f}")
    print(f"   Improvement: {improvement:.2f} ({(improvement/ga.best_fitness_history[0]*100):.1f}%)")
    
    print(f"\n📍 Next Steps:")
    print(f"   1. Compare with basic GA: python run_ga.py")
    print(f"   2. Increase generations for better convergence")
    print(f"   3. Adjust objective weights based on priorities")
    print(f"   4. Integrate with React UI for visualization")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
