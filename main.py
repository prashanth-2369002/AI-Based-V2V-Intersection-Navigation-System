"""
Main entry point for the AI-Based V2V Negotiation System
Demonstrates the complete simulation workflow
"""

import sys
import argparse

from simulation import SimulationEngine
from visualizer import SimulationVisualizer
import config


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="AI-Based V2V Negotiation System for Intersection Navigation"
    )
    parser.add_argument(
        '--scenario',
        type=str,
        default='scenario_1',
        choices=list(config.SCENARIOS.keys()),
        help='Simulation scenario to run'
    )
    parser.add_argument(
        '--time-steps',
        type=int,
        default=config.SIMULATION_TIME_STEPS,
        help='Number of simulation time steps'
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        default=True,
        help='Generate visualization plots'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        default=True,
        help='Save results to file'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='Enable debug mode'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("AI-BASED V2V NEGOTIATION SYSTEM FOR INTERSECTION NAVIGATION")
    print("=" * 70)
    print()
    print(f"Scenario: {args.scenario}")
    print(f"Scenario Description: {config.SCENARIOS[args.scenario]['name']}")
    print(f"Time Steps: {args.time_steps}")
    print(f"Debug Mode: {args.debug}")
    print()

    # Run simulation
    try:
        engine = SimulationEngine(scenario=args.scenario)
        results = engine.run_simulation()

        # Save results if requested
        if args.save:
            results_file = engine.save_results()
            print(f"\nResults saved to: {results_file}")

        # Generate visualizations if requested
        if args.visualize:
            print("\nGenerating visualizations...")
            visualizer = SimulationVisualizer()
            visualizer.generate_all_plots(results)
            visualizer.print_summary(results)

        print("\n" + "=" * 70)
        print("SIMULATION COMPLETED SUCCESSFULLY")
        print("=" * 70)

        return 0

    except Exception as e:
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
