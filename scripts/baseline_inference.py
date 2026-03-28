#!/usr/bin/env python3
"""
Baseline inference script for the Email Triage OpenEnv environment.
Uses the OpenAI API to run a model against all tasks and produce reproducible scores.

Usage:
    export OPENAI_API_KEY=your_key_here
    python scripts/baseline_inference.py

Or with specific options:
    python scripts/baseline_inference.py --model gpt-4o-mini --seed 42 --task easy_categorization
"""

import os
import sys
import json
import argparse
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI

from email_triage_env import (
    EmailTriageEnv,
    Action,
    ActionType,
    EmailCategory,
    EmailPriority,
    get_all_tasks,
    grade_episode,
)


def create_system_prompt(task_description: str) -> str:
    """Create the system prompt for the agent."""
    return f"""You are an AI assistant trained to manage emails efficiently.

Your task: {task_description}

You will receive observations about the current email and must respond with actions.

Available action types:
- CATEGORIZE: Assign a category (work, personal, spam, newsletter, support, billing)
- SET_PRIORITY: Set priority (urgent, high, normal, low)
- DELETE: Remove email (use for spam)
- ARCHIVE: Archive email (marks as processed)
- REPLY: Send a reply (include reply_content)
- FORWARD: Forward email (include forward_to)
- FLAG: Flag for follow-up
- MARK_READ: Mark as read
- SKIP: Skip to next email

Respond with a JSON object containing:
{{
    "action_type": "ACTION_TYPE",
    "category": "category_if_categorizing",
    "priority": "priority_if_setting",
    "reply_content": "reply_text_if_replying",
    "reasoning": "brief explanation of your decision"
}}

Think step by step:
1. Read the email carefully
2. Identify if it's spam (delete it)
3. Determine the category
4. Assess urgency/priority
5. Decide if a response is needed
6. Take appropriate action(s)

Be efficient - use minimal steps to process each email."""


def format_observation(obs) -> str:
    """Format the observation for the LLM."""
    if obs.current_email is None:
        return "No more emails to process. Episode complete."
    
    email = obs.current_email
    return f"""
Current Email:
- From: {email.sender_name} <{email.sender}>
- Subject: {email.subject}
- Body: {email.body}
- Received: {email.timestamp}
- Read: {email.is_read}
- Flagged: {email.is_flagged}
- Current Category: {email.category}
- Current Priority: {email.priority}

Inbox Status:
- Total emails: {obs.inbox_state.total_emails}
- Unread: {obs.inbox_state.unread_count}
- Uncategorized: {obs.inbox_state.uncategorized_count}

Progress:
- Emails processed: {obs.emails_processed}
- Remaining: {obs.emails_remaining}
- Steps: {obs.step_count}/{obs.max_steps}

Available actions: {[a.value for a in obs.available_actions]}
"""


def parse_action(response_text: str) -> Optional[Action]:
    """Parse the LLM response into an Action object."""
    try:
        # Try to extract JSON from the response
        text = response_text.strip()
        
        # Handle markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        data = json.loads(text)
        
        # Parse action type
        action_type_str = data.get("action_type", "").upper()
        action_type = ActionType(action_type_str.lower())
        
        # Parse category if provided
        category = None
        if data.get("category"):
            try:
                category = EmailCategory(data["category"].lower())
            except ValueError:
                pass
        
        # Parse priority if provided
        priority = None
        if data.get("priority"):
            try:
                priority = EmailPriority(data["priority"].lower())
            except ValueError:
                pass
        
        return Action(
            action_type=action_type,
            category=category,
            priority=priority,
            reply_content=data.get("reply_content"),
            forward_to=data.get("forward_to"),
            reasoning=data.get("reasoning"),
        )
    
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Failed to parse action: {e}")
        print(f"Response was: {response_text[:200]}...")
        return None


def run_episode(
    client: OpenAI,
    env: EmailTriageEnv,
    model: str = "gpt-4o-mini",
    seed: int = 42,
    verbose: bool = True,
) -> dict:
    """
    Run a single episode with the LLM agent.
    
    Returns:
        Dict with episode results and grading
    """
    # Reset environment
    obs = env.reset(seed=seed)
    task_config = env.task_config
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Starting task: {task_config.name}")
        print(f"Difficulty: {task_config.difficulty}")
        print(f"Emails: {task_config.num_emails}, Max steps: {task_config.max_steps}")
        print(f"{'='*60}\n")
    
    # Create conversation history
    messages = [
        {"role": "system", "content": create_system_prompt(task_config.description)}
    ]
    
    done = False
    step = 0
    total_reward = 0
    
    while not done and step < task_config.max_steps:
        # Format current observation
        obs_text = format_observation(obs)
        messages.append({"role": "user", "content": obs_text})
        
        if verbose:
            print(f"\n--- Step {step + 1} ---")
            if obs.current_email:
                print(f"Email from: {obs.current_email.sender_name}")
                print(f"Subject: {obs.current_email.subject[:50]}...")
        
        # Get LLM response
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,  # Low temperature for consistency
                max_tokens=300,
            )
            
            assistant_message = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_message})
            
            if verbose:
                print(f"Agent response: {assistant_message[:100]}...")
            
        except Exception as e:
            print(f"API error: {e}")
            break
        
        # Parse action
        action = parse_action(assistant_message)
        
        if action is None:
            # Default to skip if parsing fails
            action = Action(action_type=ActionType.SKIP, reasoning="Failed to parse")
            if verbose:
                print("Failed to parse action, skipping...")
        
        if verbose:
            print(f"Action: {action.action_type.value}")
            if action.reasoning:
                print(f"Reasoning: {action.reasoning[:50]}...")
        
        # Execute action
        try:
            obs, reward, done, info = env.step(action)
            total_reward += reward.immediate
            
            if verbose:
                print(f"Reward: {reward.immediate:.3f} (cumulative: {reward.cumulative:.3f})")
                print(f"Feedback: {reward.feedback}")
            
        except Exception as e:
            print(f"Environment error: {e}")
            break
        
        step += 1
    
    # Get final state and grade
    final_state = env.state()
    grading_result = grade_episode(task_config.task_id, final_state)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Episode Complete!")
        print(f"Final Score: {grading_result['score']:.3f}")
        print(f"Passed: {grading_result['passed']}")
        print(f"Breakdown: {json.dumps(grading_result['breakdown'], indent=2)}")
        print(f"{'='*60}\n")
    
    return {
        "task_id": task_config.task_id,
        "task_name": task_config.name,
        "difficulty": task_config.difficulty,
        "steps_used": step,
        "max_steps": task_config.max_steps,
        "total_reward": total_reward,
        "score": grading_result["score"],
        "passed": grading_result["passed"],
        "breakdown": grading_result["breakdown"],
        "metrics": grading_result["metrics"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run baseline inference on Email Triage environment"
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
        action="store_true",
        help="Reduce output verbosity",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for results JSON",
    )
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY=your_key_here")
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
    
    # Run episodes
    results = []
    print(f"\nRunning baseline inference with model: {args.model}")
    print(f"Seed: {args.seed}")
    print(f"Tasks: {tasks_to_run}\n")
    
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
    print("\n" + "="*60)
    print("BASELINE RESULTS SUMMARY")
    print("="*60)
    print(f"Model: {args.model}")
    print(f"Seed: {args.seed}")
    print("-"*60)
    
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{result['task_name']:<35} {result['score']:.3f} [{status}]")
    
    avg_score = sum(r["score"] for r in results) / len(results)
    print("-"*60)
    print(f"{'Average Score:':<35} {avg_score:.3f}")
    print("="*60)
    
    # Save results if requested
    if args.output:
        output_data = {
            "model": args.model,
            "seed": args.seed,
            "average_score": avg_score,
            "results": results,
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
