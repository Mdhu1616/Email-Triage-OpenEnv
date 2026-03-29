#!/usr/bin/env python3
"""
Inference script for Email Triage environment.
Runs baseline inference on all tasks.
"""
import os
import sys
import json
import logging
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

from env import EmailTriageEnv, get_all_tasks, grade_episode

API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME")
HF_TOKEN = os.environ.get("HF_TOKEN")

if not (API_BASE_URL and MODEL_NAME and HF_TOKEN):
    print("Error: API_BASE_URL, MODEL_NAME, and HF_TOKEN must be set as environment variables.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

def run_inference_on_task(task_id: str) -> Dict[str, Any]:
    env = EmailTriageEnv(task_id=task_id)
    obs = env.reset()
    done = False
    total_reward = 0.0
    steps = 0
    while not done:
        # Compose prompt for LLM
        prompt = f"""\nObservation: {json.dumps(obs)}\nWhat action should the agent take? Respond with a JSON action."""
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": "You are an email triage agent."},
                      {"role": "user", "content": prompt}],
            max_tokens=256,
        )
        try:
            action = json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            break
        obs, reward, done, info = env.step(action)
        total_reward += reward.get("score", 0.0)
        steps += 1
        if steps > 100:
            logger.warning("Max steps exceeded, breaking loop.")
            break
    score = grade_episode(env, task_id)
    return {"task_id": task_id, "score": score, "steps": steps, "total_reward": total_reward}

def main():
    results = []
    for task in get_all_tasks():
        logger.info(f"Running inference on task: {task}")
        result = run_inference_on_task(task)
        results.append(result)
    with open("inference_results.json", "w") as f:
        json.dump(results, f, indent=2)
    logger.info("Inference complete. Results saved to inference_results.json.")

if __name__ == "__main__":
    main()
