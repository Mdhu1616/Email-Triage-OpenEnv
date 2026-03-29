#!/usr/bin/env python3
"""
Baseline inference script for Email Triage.
"""

import os
import sys
import json
import argparse
import logging
from typing import Optional, Dict, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

from env import (
    EmailTriageEnv,
    Action,
    ActionType,
    EmailCategory,
    EmailPriority,
    get_all_tasks,
    grade_episode,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# AGENT PROMPTS
# =============================================================================

def create_system_prompt(task_description: str) -> str:
    """Create the system prompt for the baseline agent."""
    return f"""You are an AI assistant trained to efficiently manage emails in an inbox.

TASK:
{task_description}

AVAILABLE ACTIONS:
- CATEGORIZE: Assign a category (work, personal, spam, newsletter, support, billing)
- SET_PRIORITY: Set priority (urgent, high, normal, low)
- DELETE: Remove email (use ONLY for spam)
- ARCHIVE: Archive email and move to next
- REPLY: Send a reply (include reply_content with >50 chars for full credit)
- FORWARD: Forward email (include forward_to address)
- FLAG: Flag for follow-up (use for urgent items)
- MARK_READ: Mark as read
- SKIP: Skip to next email (small penalty)

RESPONSE FORMAT:
You MUST respond with a valid JSON object:
{{
    "action_type": "ACTION_NAME",
    "category": "category_if_categorizing",
    "priority": "priority_if_setting_priority",
    "reply_content": "your reply text if replying",
    "forward_to": "email@example.com if forwarding",
    "reasoning": "brief explanation of your decision"
}}

STRATEGY:
1. First, identify if the email is spam (look for lottery, prince, free prizes, suspicious links)
2. If spam -> DELETE immediately
3. If not spam -> CATEGORIZE correctly
4. Then SET_PRIORITY based on urgency
"""
Baseline evaluation script for EmailTriage OpenEnv
Logs step count, reward trajectory, failure reasons, leaderboard summary
"""
import json
from env.environment import EmailTriageEnv
from env.models import Action, ActionType
from logging_utils import StructuredLogger

logger = StructuredLogger(debug=True)

class BaselineAgent:
    def decide(self, obs):
        # Simple baseline: categorize, delete spam, archive, random priority
        if obs.current_email is None:
            return Action(action_type=ActionType.SKIP)
        if hasattr(obs.current_email, 'is_spam') and obs.current_email.is_spam:
            return Action(action_type=ActionType.DELETE)
        if obs.current_email.category is None:
            return Action(action_type=ActionType.CATEGORIZE, category="work")
        if obs.current_email.priority is None:
            return Action(action_type=ActionType.SET_PRIORITY, priority="normal")
        return Action(action_type=ActionType.ARCHIVE)

def run_episode(task_id, seed):
    env = EmailTriageEnv(task_id=task_id, seed=seed)
    obs = env.reset(seed=seed)
    agent = BaselineAgent()
    trace = []
    done = False
    step = 0
    while not done:
        action = agent.decide(obs)
        obs_before = env.state()
        obs, reward, done, info = env.step(action)
        obs_after = env.state()
        logger.trace_step(step, action, obs, reward, info)
        logger.state_diff(obs_before, obs_after)
        trace.append({
            "step": step,
            "reward": reward,
            "done": done,
            "info": info
        })
        step += 1
        if step > 200:
            logger.log("failure_reason", {"reason": "step_limit_exceeded"}, level="error")
            break
    return trace

def main():
    leaderboard = []
    for task_id in ["easy_categorization", "medium_triage", "hard_inbox_zero"]:
        scores = []
        for run in range(5):
            trace = run_episode(task_id, seed=run)
            final_reward = trace[-1]["reward"] if trace else 0.0
            scores.append(final_reward)
        avg_score = sum(scores) / len(scores)
        leaderboard.append({"task": task_id, "avg_score": avg_score, "scores": scores})
    print("Leaderboard:")
    for entry in leaderboard:
        print(f"{entry['task']}: {entry['avg_score']:.3f} ({entry['scores']})")
    with open("baseline_leaderboard.json", "w") as f:
        json.dump(leaderboard, f, indent=2)

if __name__ == "__main__":
    main()
        # Parse category if provided
        category = None
        if data.get("category"):
            try:
                category = EmailCategory(data["category"].lower())
            except ValueError:
                logger.warning(f"Unknown category: {data['category']}")
        
        # Parse priority if provided
        priority = None
        if data.get("priority"):
            try:
                priority = EmailPriority(data["priority"].lower())
            except ValueError:
                logger.warning(f"Unknown priority: {data['priority']}")
        
        return Action(
            action_type=action_type,
            category=category,
            priority=priority,
            reply_content=data.get("reply_content"),
            forward_to=data.get("forward_to"),
            reasoning=data.get("reasoning"),
        )
    
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.warning(f"Failed to parse action: {e}")
        logger.debug(f"Response was: {response_text[:200]}...")
        return None


# =============================================================================
# EPISODE RUNNER
# =============================================================================

def run_episode(
    client: OpenAI,
    env: EmailTriageEnv,
    model: str = "gpt-4o-mini",
    seed: int = 42,
    verbose: bool = True,
    max_retries: int = 3,
) -> Dict:
    """
    Run a single episode with the LLM agent.
    
    Args:
        client: OpenAI client
        env: EmailTriageEnv instance
        model: Model to use
        seed: Random seed for reproducibility
        verbose: Whether to print progress
        max_retries: Max retries for failed API calls
    
    Returns:
        Dict with episode results and grading
    """
    # Reset environment with seed for reproducibility
    obs = env.reset(seed=seed)
    task_config = env.task_config
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"TASK: {task_config.name}")
        print(f"Difficulty: {task_config.difficulty.upper()}")
        print(f"Emails: {task_config.num_emails} | Max Steps: {task_config.max_steps}")
        print(f"{'='*70}")
    
    # Initialize conversation
    messages = [
        {"role": "system", "content": create_system_prompt(task_config.description)}
    ]
    
    done = False
    step = 0
    total_reward = 0
    action_history = []
    
    while not done and step < task_config.max_steps:
        # Format observation
        obs_text = format_observation_for_llm(obs)
        messages.append({"role": "user", "content": obs_text})
        
        if verbose:
            print(f"\n--- Step {step + 1} ---")
            if obs.current_email:
                print(f"From: {obs.current_email.sender_name}")
                print(f"Subject: {obs.current_email.subject[:50]}...")
        
        # Get LLM response with retries
        action = None
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,  # Low for consistency
                    max_tokens=500,
                )
                
                assistant_message = response.choices[0].message.content
                messages.append({"role": "assistant", "content": assistant_message})
                
                if verbose:
                    print(f"Response: {assistant_message[:100]}...")
                
                action = parse_llm_response(assistant_message)
                if action:
                    break
                    
            except Exception as e:
                logger.warning(f"API error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    logger.error("Max retries exceeded")
        
        # Default to SKIP if parsing fails
        if action is None:
            action = Action(action_type=ActionType.SKIP, reasoning="Failed to parse response")
            if verbose:
                print("Warning: Using SKIP action due to parse failure")
        
        if verbose:
            print(f"Action: {action.action_type.value}")
            if action.reasoning:
                print(f"Reasoning: {action.reasoning[:60]}...")
        
        # Execute action
        try:
            obs, reward, done, info = env.step(action)
            total_reward += reward.immediate
            
            action_history.append({
                "step": step + 1,
                "action": action.action_type.value,
                "reward": reward.immediate,
                "feedback": reward.feedback,
            })
            
            if verbose:
                print(f"Reward: {reward.immediate:+.3f} (total: {reward.cumulative:.3f})")
                print(f"Feedback: {reward.feedback}")
                
        except Exception as e:
            logger.error(f"Environment error: {e}")
            break
        
        step += 1
    
    # Get final state and grade
    final_state = env.state()
    grading_result = grade_episode(task_config.task_id, final_state)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"EPISODE COMPLETE")
        print(f"Final Score: {grading_result['score']:.4f}")
        print(f"Passed: {'YES' if grading_result['passed'] else 'NO'}")
        print(f"Threshold: {grading_result['threshold']}")
        print(f"{'='*70}")
        print("Breakdown:")
        for key, value in grading_result['breakdown'].items():
            print(f"  {key}: {value:.4f}")
    
    return {
        "task_id": task_config.task_id,
        "task_name": task_config.name,
        "difficulty": task_config.difficulty,
        "steps_used": step,
        "max_steps": task_config.max_steps,
        "total_reward": round(total_reward, 4),
        "score": grading_result["score"],
        "passed": grading_result["passed"],
        "threshold": grading_result["threshold"],
        "breakdown": grading_result["breakdown"],
        "metrics": grading_result["metrics"],
        "action_history": action_history,
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run baseline inference on Email Triage OpenEnv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_baseline.py
  python scripts/run_baseline.py --model gpt-4o --seed 123
  python scripts/run_baseline.py --task medium_triage --quiet
  python scripts/run_baseline.py --output results.json
        """,
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Specific task to run (default: run all tasks)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Reduce output verbosity",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file for results JSON",
    )
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it: export OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    # Initialize client
    client = OpenAI(api_key=api_key)
    
    # Get tasks to run
    all_tasks = get_all_tasks()
    if args.task:
        if args.task not in all_tasks:
            print(f"Error: Unknown task '{args.task}'")
            print(f"Available tasks: {list(all_tasks.keys())}")
            sys.exit(1)
        tasks_to_run = [args.task]
    else:
        tasks_to_run = list(all_tasks.keys())
    
    # Header
    print("\n" + "="*70)
    print("EMAIL TRIAGE OPENENV - BASELINE INFERENCE")
    print("="*70)
    print(f"Model: {args.model}")
    print(f"Seed: {args.seed}")
    print(f"Tasks: {', '.join(tasks_to_run)}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70)
    
    # Run episodes
    results: List[Dict] = []
    
    for task_id in tasks_to_run:
        env = EmailTriageEnv(task_id=task_id)
        result = run_episode(
            client=client,
            env=env,
            model=args.model,
            seed=args.seed,
            verbose=not args.quiet,
        )
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("BASELINE RESULTS SUMMARY")
    print("="*70)
    print(f"{'Task':<40} {'Score':<10} {'Status':<10}")
    print("-"*70)
    
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{result['task_name']:<40} {result['score']:.4f}    [{status}]")
    
    avg_score = sum(r["score"] for r in results) / len(results)
    all_passed = all(r["passed"] for r in results)
    
    print("-"*70)
    print(f"{'Average Score:':<40} {avg_score:.4f}    [{'ALL PASS' if all_passed else 'SOME FAIL'}]")
    print("="*70)
    
    # Save results if requested
    if args.output:
        output_data = {
            "metadata": {
                "model": args.model,
                "seed": args.seed,
                "timestamp": datetime.now().isoformat(),
                "openenv_version": "1.0.0",
            },
            "summary": {
                "average_score": round(avg_score, 4),
                "all_passed": all_passed,
                "tasks_run": len(results),
            },
            "results": results,
        }
        
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Exit code
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
