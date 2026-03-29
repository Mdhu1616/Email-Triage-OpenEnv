"""
CLI for Email Triage environment.
"""
import argparse
import json
import os
from env.environment import EmailTriageEnv
from env.models import Action

def main():
    parser = argparse.ArgumentParser(description="EmailTriage CLI")
    parser.add_argument("--task", type=str, default="easy_categorization", help="Task ID (easy_categorization, medium_triage, hard_inbox_zero)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--config", type=str, help="Path to config file (optional)")
    parser.add_argument("--env", action="store_true", help="Print environment state after each step")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Config file support
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config) as f:
            config = json.load(f)

    # Env var support
    task_id = os.environ.get("EMAIL_TASK_ID", args.task)
    seed = int(os.environ.get("EMAIL_SEED", args.seed))

    env = EmailTriageEnv(task_id=task_id, seed=seed)
    obs = env.reset(seed=seed)
    print("Initial observation:", obs)

    done = False
    while not done:
        action_json = input("Enter action as JSON (or 'exit'): ")
        if action_json.strip().lower() == "exit":
            break
        try:
            action = Action(**json.loads(action_json))
        except Exception as e:
            print("Invalid action format:", e)
            continue
        obs, reward, done, info = env.step(action)
        print("Observation:", obs)
        print("Reward:", reward)
        print("Info:", info)
        if args.env:
            print("State:", env.state())
        if done:
            print("Episode complete.")

if __name__ == "__main__":
    main()
