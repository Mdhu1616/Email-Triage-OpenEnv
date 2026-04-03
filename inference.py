#!/usr/bin/env python3
"""OpenEnv RL Challenge compliant inference script."""
import os
import json
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package is required. Run: pip install openai")
    sys.exit(1)

from env import EmailTriageEnv, get_all_tasks, grade_episode

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None or HF_TOKEN.strip() == "":
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


def format_step_line(step: int, action: str, reward: float, done: bool, error: str | None):
    error_value = error if error is not None else "null"
    return f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_value}"


def format_end_line(success: bool, steps: int, rewards: list[float]):
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    return f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}"


def run_inference():
    tasks = get_all_tasks()
    if not tasks:
        raise RuntimeError("No tasks found")

    task_id = list(tasks.keys())[0]
    env_name = "email-triage"

    env = EmailTriageEnv(task_id=task_id)
    obs = env.reset(seed=42)

    print(f"[START] task={task_id} env={env_name} model={MODEL_NAME}")

    done = False
    step = 0
    rewards = []
    success = False

    try:
        while not done:
            step += 1
            prompt = f"Observation: {json.dumps(obs, default=str)}\nAction in JSON format, no extra text."
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an email triage agent. Return action as JSON."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
            )

            content = response.choices[0].message.content.strip()
            action_payload = None
            action_text = "unknown"

            try:
                action_payload = json.loads(content)
                action_text = json.dumps(action_payload, separators=(",", ":"), ensure_ascii=False)
            except Exception as e:
                print(format_step_line(step, action_text, 0.00, False, f"parse_error:{e}"))
                break

            try:
                obs, reward, done, info = env.step(action_payload)
            except Exception as e:
                print(format_step_line(step, action_text, 0.00, True, str(e)))
                break

            rewards.append(float(reward))
            print(format_step_line(step, action_text, float(reward), done, None))

            if step >= tasks[task_id].max_steps:
                break

        grading = grade_episode(task_id, env.state())
        success = bool(grading.get("passed", False))
    except Exception:
        success = False
    finally:
        print(format_end_line(success, step, rewards))


if __name__ == "__main__":
    run_inference()