"""
Plotting script for EmailTriage OpenEnv benchmark results.
Generates leaderboard tables and reward trajectory plots.
"""
import json
import matplotlib.pyplot as plt
import argparse

def plot_leaderboard(input_file):
    with open(input_file) as f:
        data = json.load(f)
    tasks = [entry['task'] for entry in data]
    avg_scores = [entry['avg_score'] for entry in data]
    plt.figure(figsize=(8, 4))
    plt.bar(tasks, avg_scores, color=['#4F8EF7', '#F7B64F', '#4FF7B6'])
    plt.ylim(0, 1)
    plt.title('Leaderboard: Average Score by Task')
    plt.ylabel('Average Score')
    plt.xlabel('Task')
    plt.tight_layout()
    plt.show()

def plot_reward_trajectory(trace_file):
    with open(trace_file) as f:
        trace = json.load(f)
    rewards = [step['reward'] for step in trace]
    plt.figure(figsize=(10, 4))
    plt.plot(rewards, marker='o')
    plt.title('Reward Trajectory')
    plt.xlabel('Step')
    plt.ylabel('Reward')
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Plot OpenEnv benchmark results')
    parser.add_argument('--input', type=str, required=True, help='Leaderboard JSON file')
    parser.add_argument('--trace', type=str, help='Trace JSON file (optional)')
    args = parser.parse_args()
    plot_leaderboard(args.input)
    if args.trace:
        plot_reward_trajectory(args.trace)

if __name__ == '__main__':
    main()
