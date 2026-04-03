#!/usr/bin/env python3
"""
Variance analysis script for Email Triage environment.
Runs baseline multiple times to check score consistency and variance.
"""

import os
import sys
import json
import argparse
import statistics
from typing import List, Dict
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

from env import EmailTriageEnv, get_all_tasks, grade_episode


def run_single_episode(env: EmailTriageEnv, seed: int) -> Dict:
    """Run a single episode with a simple baseline agent."""
    obs = env.reset(seed=seed)
    done = False
    step = 0
    total_reward = 0

    while not done and step < env.task_config.max_steps:
        # Simple baseline: categorize work, set normal priority, archive
        if obs.current_email is None:
            action = env.models.Action(action_type=env.models.ActionType.SKIP)
        elif obs.current_email.category is None:
            action = env.models.Action(
                action_type=env.models.ActionType.CATEGORIZE,
                category=env.models.EmailCategory.WORK
            )
        elif obs.current_email.priority is None:
            action = env.models.Action(
                action_type=env.models.ActionType.SET_PRIORITY,
                priority=env.models.EmailPriority.NORMAL
            )
        else:
            action = env.models.Action(action_type=env.models.ActionType.ARCHIVE)

        obs, reward, done, info = env.step(action)
        total_reward += reward.immediate
        step += 1

    # Grade the episode
    final_state = env.state()
    grading_result = grade_episode(env.task_config.task_id, final_state)

    return {
        "seed": seed,
        "score": grading_result["score"],
        "passed": grading_result["passed"],
        "steps": step,
        "total_reward": round(total_reward, 4),
    }


def analyze_variance(results: List[Dict], task_name: str) -> Dict:
    """Analyze variance in results."""
    scores = [r["score"] for r in results]
    passes = [r["passed"] for r in results]

    return {
        "task": task_name,
        "runs": len(results),
        "mean_score": round(statistics.mean(scores), 4),
        "median_score": round(statistics.median(scores), 4),
        "std_dev": round(statistics.stdev(scores), 4) if len(scores) > 1 else 0.0,
        "min_score": round(min(scores), 4),
        "max_score": round(max(scores), 4),
        "pass_rate": round(sum(passes) / len(passes), 4),
        "coefficient_of_variation": round(statistics.stdev(scores) / statistics.mean(scores), 4) if len(scores) > 1 and statistics.mean(scores) > 0 else 0.0,
        "scores": scores,
        "passes": passes,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze score variance across multiple runs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/analyze_variance.py --runs 20
  python scripts/analyze_variance.py --task easy_categorization --runs 10
  python scripts/analyze_variance.py --output variance_results.json
        """,
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=10,
        help="Number of runs per task (default: 10)",
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Specific task to analyze (default: all tasks)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file for results JSON",
    )

    args = parser.parse_args()

    # Get tasks to analyze
    all_tasks = get_all_tasks()
    if args.task:
        if args.task not in all_tasks:
            print(f"Error: Unknown task '{args.task}'")
            print(f"Available tasks: {list(all_tasks.keys())}")
            sys.exit(1)
        tasks_to_analyze = [args.task]
    else:
        tasks_to_analyze = list(all_tasks.keys())

    print("\n" + "="*80)
    print("EMAIL TRIAGE ENVIRONMENT - VARIANCE ANALYSIS")
    print("="*80)
    print(f"Tasks: {', '.join(tasks_to_analyze)}")
    print(f"Runs per task: {args.runs}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80)

    # Run analysis
    variance_results = []

    for task_id in tasks_to_analyze:
        print(f"\nAnalyzing {task_id}...")
        env = EmailTriageEnv(task_id=task_id)
        results = []

        for run in range(args.runs):
            seed = run  # Use run number as seed for reproducibility
            result = run_single_episode(env, seed)
            results.append(result)
            print(f"  Run {run + 1:2d}: Score {result['score']:.4f} {'PASS' if result['passed'] else 'FAIL'}")

        analysis = analyze_variance(results, task_id)
        variance_results.append(analysis)

        print(f"\n  Summary for {task_id}:")
        print(f"    Mean Score: {analysis['mean_score']:.4f}")
        print(f"    Std Dev: {analysis['std_dev']:.4f}")
        print(f"    Pass Rate: {analysis['pass_rate']:.1%}")
        print(f"    Coeff of Variation: {analysis['coefficient_of_variation']:.4f}")

    # Overall summary
    print("\n" + "="*80)
    print("OVERALL VARIANCE SUMMARY")
    print("="*80)
    print(f"{'Task':<25} {'Mean':<8} {'StdDev':<8} {'Pass%':<8} {'CV':<8}")
    print("-"*80)

    for result in variance_results:
        print(f"{result['task']:<25} {result['mean_score']:<8.4f} {result['std_dev']:<8.4f} {result['pass_rate']:<8.1%} {result['coefficient_of_variation']:<8.4f}")

    # Check variance thresholds
    print("\n" + "="*80)
    print("VARIANCE ASSESSMENT")
    print("="*80)

    all_low_variance = True
    for result in variance_results:
        cv = result['coefficient_of_variation']
        std_dev = result['std_dev']

        if cv > 0.1 or std_dev > 0.05:  # Thresholds for acceptable variance
            print(f"⚠️  {result['task']}: HIGH VARIANCE (CV={cv:.4f}, StdDev={std_dev:.4f})")
            all_low_variance = False
        else:
            print(f"✅ {result['task']}: Low variance (CV={cv:.4f}, StdDev={std_dev:.4f})")

    if all_low_variance:
        print("\n🎉 All tasks show acceptable score variance!")
        exit_code = 0
    else:
        print("\n⚠️  Some tasks show high variance - investigate reproducibility issues")
        exit_code = 1

    # Save results if requested
    if args.output:
        output_data = {
            "metadata": {
                "runs_per_task": args.runs,
                "timestamp": datetime.now().isoformat(),
                "openenv_version": "1.0.0",
            },
            "summary": {
                "all_low_variance": all_low_variance,
                "tasks_analyzed": len(variance_results),
            },
            "results": variance_results,
        }

        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())