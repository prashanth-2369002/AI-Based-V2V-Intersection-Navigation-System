"""
Visualization module for simulation results
Generates real-time plots and trajectory visualizations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
from typing import Dict, List, Tuple
import os

import config


class SimulationVisualizer:
    """Visualizes simulation data and results"""

    def __init__(self, output_dir: str = config.OUTPUT_GRAPHS_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_trajectories(self, results: Dict, filename: str = "trajectories.png") -> str:
        """Plot vehicle trajectories on the intersection"""
        fig, ax = plt.subplots(figsize=(12, 12))

        # Draw intersection
        intersection = patches.Rectangle(
            (config.INTERSECTION_CENTER[0] - config.INTERSECTION_SIZE/2,
             config.INTERSECTION_CENTER[1] - config.INTERSECTION_SIZE/2),
            config.INTERSECTION_SIZE,
            config.INTERSECTION_SIZE,
            linewidth=2,
            edgecolor='red',
            facecolor='lightyellow',
            alpha=0.3
        )
        ax.add_patch(intersection)

        # Draw RSU
        ax.plot(config.RSU_POSITION[0], config.RSU_POSITION[1],
                'g*', markersize=20, label='RSU')

        # Plot vehicle trajectories
        colors = plt.cm.Set3(np.linspace(0, 1, len(results['vehicle_trajectories'])))

        for (vehicle_id, traj_data), color in zip(results['vehicle_trajectories'].items(), colors):
            trajectory = traj_data['trajectory']
            if len(trajectory) > 1:
                xs, ys = zip(*trajectory)
                ax.plot(xs, ys, color=color, linewidth=2, label=vehicle_id)
                ax.plot(xs[0], ys[0], 'o', color=color, markersize=8)  # Start
                ax.plot(xs[-1], ys[-1], 's', color=color, markersize=8)  # End

        ax.set_xlim(0, config.GRID_SIZE)
        ax.set_ylim(0, config.GRID_SIZE)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        ax.set_xlabel('X Position (pixels)')
        ax.set_ylabel('Y Position (pixels)')
        ax.set_title(f'Vehicle Trajectories - {results["scenario"]}')

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Saved: {filepath}")
        return filepath

    def plot_communication_delay(self, results: Dict,
                                filename: str = "communication_delay.png") -> str:
        """Plot communication delays over time"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # V2V Statistics
        v2v_stats = results['communication_statistics']['v2v']
        ax1.bar(['Sent', 'Received', 'Lost'],
               [v2v_stats['total_messages_sent'],
                v2v_stats['total_messages_received'],
                v2v_stats['total_messages_sent'] - v2v_stats['total_messages_received']])
        ax1.set_ylabel('Number of Messages')
        ax1.set_title('V2V Communication Summary')
        ax1.grid(True, alpha=0.3, axis='y')

        # V2I Statistics
        v2i_stats = results['communication_statistics']['v2i']
        ax2.bar(['Sent', 'Received', 'Lost'],
               [v2i_stats['total_messages_sent'],
                v2i_stats['total_messages_received'],
                v2i_stats['total_messages_sent'] - v2i_stats['total_messages_received']])
        ax2.set_ylabel('Number of Messages')
        ax2.set_title('V2I Communication Summary')
        ax2.grid(True, alpha=0.3, axis='y')

        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Saved: {filepath}")
        return filepath

    def plot_velocity_profile(self, results: Dict,
                             filename: str = "velocity_profile.png") -> str:
        """Plot velocity profiles for all vehicles"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()

        trajectories = results['vehicle_trajectories']
        for idx, (vehicle_id, traj_data) in enumerate(trajectories.items()):
            ax = axes[idx] if idx < len(axes) else None
            if ax is None:
                break

            velocities = traj_data['velocity_history']
            time_steps = range(len(velocities))

            ax.plot(time_steps, velocities, linewidth=2)
            ax.fill_between(time_steps, velocities, alpha=0.3)
            ax.set_xlabel('Time Step')
            ax.set_ylabel('Velocity (pixels/sec)')
            ax.set_title(f'Velocity Profile - {vehicle_id}')
            ax.grid(True, alpha=0.3)

        # Hide unused subplots
        for idx in range(len(trajectories), len(axes)):
            axes[idx].set_visible(False)

        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Saved: {filepath}")
        return filepath

    def plot_collision_risk_analysis(self, results: Dict,
                                    filename: str = "collision_risk.png") -> str:
        """Plot collision risk analysis"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        collision_data = results['collision_analysis']
        events = collision_data.get('collision_events', [])

        if events:
            vehicles_a = [e['vehicle_a'] for e in events]
            risk_scores = [e['risk_score'] for e in events]

            ax1.scatter(range(len(events)), risk_scores, s=100, alpha=0.6)
            ax1.axhline(y=0.5, color='r', linestyle='--', label='Risk Threshold')
            ax1.set_xlabel('Event Index')
            ax1.set_ylabel('Risk Score')
            ax1.set_title('Collision Risk Events Over Time')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 1)

            # Risk distribution
            ax2.hist(risk_scores, bins=10, edgecolor='black', alpha=0.7)
            ax2.set_xlabel('Risk Score')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Collision Risk Score Distribution')
            ax2.grid(True, alpha=0.3, axis='y')
        else:
            ax1.text(0.5, 0.5, 'No collision events detected', ha='center', va='center')
            ax2.text(0.5, 0.5, 'No collision events detected', ha='center', va='center')

        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Saved: {filepath}")
        return filepath

    def plot_predicted_vs_actual_trajectory(self, results: Dict,
                                          filename: str = "predicted_vs_actual.png") -> str:
        """Plot predicted vs actual trajectory for each vehicle"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()

        trajectories = results['vehicle_trajectories']
        
        for idx, (vehicle_id, traj_data) in enumerate(trajectories.items()):
            if idx >= 4:
                break
            
            ax = axes[idx]
            actual_trajectory = traj_data['trajectory']
            
            if len(actual_trajectory) < 2:
                continue

            xs_actual, ys_actual = zip(*actual_trajectory)
            
            # Plot actual trajectory
            ax.plot(xs_actual, ys_actual, 'b-', linewidth=2, label='Actual Path', marker='o', markersize=3)
            ax.plot(xs_actual[0], ys_actual[0], 'go', markersize=10, label='Start')
            ax.plot(xs_actual[-1], ys_actual[-1], 'rs', markersize=10, label='End')

            # Draw intersection
            intersection = patches.Rectangle(
                (config.INTERSECTION_CENTER[0] - config.INTERSECTION_SIZE/2,
                 config.INTERSECTION_CENTER[1] - config.INTERSECTION_SIZE/2),
                config.INTERSECTION_SIZE,
                config.INTERSECTION_SIZE,
                linewidth=2,
                edgecolor='red',
                facecolor='lightyellow',
                alpha=0.2
            )
            ax.add_patch(intersection)

            # Generate predicted trajectory from actual data points
            if len(actual_trajectory) > 1:
                # Use first few points to predict remaining trajectory
                pred_start_idx = min(20, len(actual_trajectory) // 3)
                if pred_start_idx < len(actual_trajectory):
                    start_pos = actual_trajectory[pred_start_idx]
                    
                    # Calculate average velocity from first few points
                    if pred_start_idx > 0:
                        vel_x = (actual_trajectory[pred_start_idx][0] - actual_trajectory[0][0]) / (pred_start_idx * config.TIME_STEP_DURATION)
                        vel_y = (actual_trajectory[pred_start_idx][1] - actual_trajectory[0][1]) / (pred_start_idx * config.TIME_STEP_DURATION)
                        
                        # Predict future trajectory
                        pred_trajectory = [start_pos]
                        current_x, current_y = start_pos
                        for step in range(50):
                            current_x += vel_x * config.TIME_STEP_DURATION
                            current_y += vel_y * config.TIME_STEP_DURATION
                            pred_trajectory.append((current_x, current_y))
                        
                        xs_pred, ys_pred = zip(*pred_trajectory)
                        ax.plot(xs_pred, ys_pred, 'r--', linewidth=2, label='Predicted Path', alpha=0.7, marker='x', markersize=4)

            ax.set_xlim(0, config.GRID_SIZE)
            ax.set_ylim(0, config.GRID_SIZE)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best')
            ax.set_title(f'{vehicle_id}: Predicted vs Actual Trajectory')
            ax.set_xlabel('X Position (pixels)')
            ax.set_ylabel('Y Position (pixels)')

        # Hide unused subplots
        for idx in range(len(trajectories), len(axes)):
            axes[idx].set_visible(False)

        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Saved: {filepath}")
        return filepath

    def plot_performance_metrics(self, results: Dict,
                                filename: str = "performance_metrics.png") -> str:
        """Plot key performance metrics"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

        metrics = results['performance_metrics']
        rsu_stats = results['rsu_statistics']

        # Successful Crossings
        ax1.bar(['Successful', 'Total'],
               [metrics['successful_crossings'], len(results['vehicle_trajectories'])])
        ax1.set_ylabel('Count')
        ax1.set_title('Vehicle Crossing Success Rate')
        ax1.grid(True, alpha=0.3, axis='y')

        # RSU Decisions
        ax2.bar(['Vehicles Managed', 'Vehicles Crossed'],
               [rsu_stats['total_vehicles_managed'], rsu_stats['vehicles_crossed']])
        ax2.set_ylabel('Count')
        ax2.set_title('RSU Management Statistics')
        ax2.grid(True, alpha=0.3, axis='y')

        # Wait Time
        ax3.bar(['Total Wait Time'],
               [metrics['total_wait_time']])
        ax3.set_ylabel('Time (seconds)')
        ax3.set_title('Total Wait Time')
        ax3.grid(True, alpha=0.3, axis='y')

        # Collision Detections
        collision_count = len(results['collision_analysis'].get('collision_events', []))
        ax4.bar(['Collision Events', 'Avoided'],
               [collision_count, metrics['total_collisions_avoided']])
        ax4.set_ylabel('Count')
        ax4.set_title('Collision Detection & Avoidance')
        ax4.grid(True, alpha=0.3, axis='y')

        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Saved: {filepath}")
        return filepath

    def generate_all_plots(self, results: Dict) -> List[str]:
        """Generate all visualization plots"""
        plots = []

        print("Generating visualizations...")
        plots.append(self.plot_trajectories(results))
        plots.append(self.plot_communication_delay(results))
        plots.append(self.plot_velocity_profile(results))
        plots.append(self.plot_collision_risk_analysis(results))
        plots.append(self.plot_predicted_vs_actual_trajectory(results))
        plots.append(self.plot_performance_metrics(results))

        return plots

    def print_summary(self, results: Dict) -> None:
        """Print text summary of results"""
        print("\n" + "="*60)
        print("SIMULATION SUMMARY")
        print("="*60)
        print(f"Scenario: {results['scenario']}")
        print(f"Simulation Time: {results['simulation_time']:.2f} seconds")
        print(f"Total Steps: {results['total_steps']}")

        print("\nVehicle Statistics:")
        for vehicle_id, traj_data in results['vehicle_trajectories'].items():
            print(f"  {vehicle_id}:")
            print(f"    - Distance Traveled: {traj_data['total_distance']:.2f} pixels")
            print(f"    - Type: {traj_data['vehicle_type']}")
            print(f"    - Crossing Completed: {traj_data['crossing_completed']}")

        print("\nRSU Statistics:")
        rsu_stats = results['rsu_statistics']
        print(f"  - Total Vehicles Managed: {rsu_stats['total_vehicles_managed']}")
        print(f"  - Vehicles Crossed: {rsu_stats['vehicles_crossed']}")
        print(f"  - Total Decisions: {rsu_stats['total_decisions']}")
        print(f"  - Collision Detections: {rsu_stats['collision_detections']}")
        print(f"  - Avg Decision Time: {rsu_stats['avg_processing_time']*1000:.2f} ms")

        print("\nCommunication Statistics:")
        v2v = results['communication_statistics']['v2v']
        v2i = results['communication_statistics']['v2i']
        print(f"  V2V:")
        print(f"    - Messages Sent: {v2v['total_messages_sent']}")
        print(f"    - Messages Received: {v2v['total_messages_received']}")
        print(f"    - Loss Rate: {v2v['message_loss_rate']:.2%}")
        print(f"  V2I:")
        print(f"    - Messages Sent: {v2i['total_messages_sent']}")
        print(f"    - Messages Received: {v2i['total_messages_received']}")
        print(f"    - Loss Rate: {v2i['message_loss_rate']:.2%}")

        print("\n" + "="*60)
