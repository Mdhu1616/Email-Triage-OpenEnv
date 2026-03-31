"""
Gradio interface for Email Triage environment.
"""

import json
import gradio as gr
from typing import Optional, Tuple, List
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from email_triage_env import (
    EmailTriageEnv,
    Action,
    ActionType,
    EmailCategory,
    EmailPriority,
    Observation,
    get_all_tasks,
    grade_episode,
)


# Global environment instance (per session via gr.State)
def create_env_state():
    return {
        "env": None,
        "task_id": None,
        "history": [],
    }


def get_task_info() -> str:
    """Get formatted information about all available tasks."""
    tasks = get_all_tasks()
    info = "## Available Tasks\n\n"
    
    for task_id, config in tasks.items():
        info += f"### {config.name}\n"
        info += f"- **ID:** `{task_id}`\n"
        info += f"- **Difficulty:** {config.difficulty}\n"
        info += f"- **Emails:** {config.num_emails}\n"
        info += f"- **Max Steps:** {config.max_steps}\n"
        info += f"- **Success Threshold:** {config.success_threshold}\n\n"
        info += f"{config.description}\n\n"
        info += "---\n\n"
    
    return info


def format_observation(obs: Optional[Observation]) -> str:
    """Format observation as readable markdown."""
    if obs is None:
        return "No observation available. Please reset the environment."
    
    if obs.current_email is None:
        return "## Episode Complete\n\nAll emails have been processed!"
    
    email = obs.current_email
    
    md = f"""## Current Email

**From:** {email.sender_name} <{email.sender}>  
**Subject:** {email.subject}  
**Received:** {email.timestamp}  
**Status:** {'Read' if email.is_read else 'Unread'} | {'Flagged' if email.is_flagged else 'Not Flagged'}

### Body
```
{email.body}
```

---

## Inbox Status
- **Total Emails:** {obs.inbox_state.total_emails}
- **Unread:** {obs.inbox_state.unread_count}
- **Uncategorized:** {obs.inbox_state.uncategorized_count}
- **Flagged:** {obs.inbox_state.flagged_count}

## Progress
- **Emails Processed:** {obs.emails_processed} / {obs.emails_remaining + obs.emails_processed}
- **Steps:** {obs.step_count} / {obs.max_steps}

## Available Actions
{', '.join([a.value for a in obs.available_actions])}
"""
    return md


def format_history(history: List[dict]) -> str:
    """Format action history as markdown."""
    if not history:
        return "No actions taken yet."
    
    md = "| Step | Action | Reward | Feedback |\n"
    md += "|------|--------|--------|----------|\n"
    
    for entry in history[-10:]:  # Last 10 entries
        md += f"| {entry['step']} | {entry['action']} | {entry['reward']:.3f} | {entry['feedback'][:50]}... |\n"
    
    return md


def reset_environment(
    task_id: str,
    seed: int,
    state: dict
) -> Tuple[str, str, str, dict]:
    """Reset the environment with selected task."""
    try:
        env = EmailTriageEnv(task_id=task_id)
        obs = env.reset(seed=seed)
        
        state["env"] = env
        state["task_id"] = task_id
        state["history"] = []
        
        task_config = env.task_config
        task_info = f"## Task: {task_config.name}\n\n{task_config.description}"
        
        return (
            format_observation(obs),
            task_info,
            "Environment reset successfully!",
            state
        )
    except Exception as e:
        return (
            f"Error: {str(e)}",
            "",
            f"Failed to reset: {str(e)}",
            state
        )


def take_action(
    action_type: str,
    category: str,
    priority: str,
    reply_content: str,
    reasoning: str,
    state: dict
) -> Tuple[str, str, str, str, dict]:
    """Execute an action in the environment."""
    env = state.get("env")
    if env is None:
        return (
            "Please reset the environment first.",
            "",
            "",
            "No environment loaded.",
            state
        )
    
    try:
        state["history"].append({
            "step": len(state["history"]) + 1,
            "action": action_type,
            "reward": reward.immediate,
            "feedback": reward.feedback,
        })
        # Format results
        obs_md = format_observation(obs)
        history_md = format_history(state["history"])
        # Phishing feedback highlight
        phishing_feedback = ""
        if action_type == "report_phishing":
            if "phishing" in reward.breakdown or "phishing_reported" in reward.breakdown:
                phishing_feedback = "\n**Phishing Detection:** 🛡️ " + reward.feedback
            elif "false_phishing_report" in reward.breakdown:
                phishing_feedback = "\n**Phishing Detection:** ⚠️ " + reward.feedback
        reward_md = f"""## Reward
- **Immediate:** {reward.immediate:.3f}
- **Cumulative:** {reward.cumulative:.3f}

### Feedback
{reward.feedback}{phishing_feedback}

### Breakdown
```json
{json.dumps(reward.breakdown, indent=2)}
```
"""
        # Check if done
        if done:
            final_state = env.state()
            grading = grade_episode(state["task_id"], final_state)
            status = "PASSED" if grading["passed"] else "FAILED"
            reward_md += f"""
---
## Episode Complete!

### Final Score: {grading['score']:.3f} [{status}]

### Breakdown
```json
{json.dumps(grading['breakdown'], indent=2)}
```

### Metrics
```json
{json.dumps(grading['metrics'], indent=2)}
```
"""
        return (
            obs_md,
            history_md,
            reward_md,
            f"Action executed: {action_type}",
            state
        )
    except Exception as e:
        return (
            format_observation(None),
            format_history(state.get("history", [])),
            "",
            f"Error: {str(e)}",
            state
        )


def get_current_state(state: dict) -> str:
    """Get current environment state as JSON."""
    env = state.get("env")
    if env is None:
        return "No environment loaded."
    
    try:
        env_state = env.state()
        return json.dumps(env_state.model_dump(), indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"


# Build Gradio interface
def create_interface():
    tasks = get_all_tasks()
    task_choices = list(tasks.keys())
    
    with gr.Blocks() as demo:
        
        gr.Markdown("""
# Email Triage OpenEnv Environment

A real-world simulation for training AI agents on email management tasks.
Implements the full [OpenEnv](https://github.com/openenv) specification.

## Quick Start
1. Select a task and click **Reset Environment**
2. Read the current email observation
3. Choose an action and fill in required fields
4. Click **Take Action** to execute
5. Repeat until the episode is complete
        """)
        
        # State
        state = gr.State(create_env_state)
        
        with gr.Row():
            # Left column: Controls
            with gr.Column(scale=1):
                gr.Markdown("## Controls")
                
                task_dropdown = gr.Dropdown(
                    choices=task_choices,
                    value=task_choices[0],
                    label="Select Task"
                )
                
                seed_input = gr.Number(
                    value=42,
                    label="Random Seed",
                    precision=0
                )
                
                reset_btn = gr.Button("Reset Environment", variant="primary")
                
                gr.Markdown("---")
                gr.Markdown("### Action")
                
                action_dropdown = gr.Dropdown(
                    choices=[a.value for a in ActionType],
                    value=ActionType.CATEGORIZE.value,
                    label="Action Type"
                )
                
                category_dropdown = gr.Dropdown(
                    choices=["None"] + [c.value for c in EmailCategory],
                    value="None",
                    label="Category (for CATEGORIZE)"
                )
                
                priority_dropdown = gr.Dropdown(
                    choices=["None"] + [p.value for p in EmailPriority],
                    value="None",
                    label="Priority (for SET_PRIORITY)"
                )
                
                reply_input = gr.Textbox(
                    label="Reply Content (for REPLY)",
                    lines=3
                )
                
                reasoning_input = gr.Textbox(
                    label="Reasoning (optional)",
                    lines=2
                )
                
                action_btn = gr.Button("Take Action", variant="secondary")
                
                status_output = gr.Textbox(
                    label="Status",
                    interactive=False
                )
            
            # Right column: Observations
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.Tab("Observation"):
                        obs_output = gr.Markdown("Click 'Reset Environment' to start.")
                    
                    with gr.Tab("Task Info"):
                        task_output = gr.Markdown(get_task_info())
                    
                    with gr.Tab("History"):
                        history_output = gr.Markdown("No actions taken yet.")
                    
                    with gr.Tab("Reward"):
                        reward_output = gr.Markdown("Take an action to see rewards.")
                    
                    with gr.Tab("State (JSON)"):
                        state_output = gr.Code(
                            label="Environment State",
                            language="json"
                        )
                        refresh_state_btn = gr.Button("Refresh State")
        
        # Event handlers
        reset_btn.click(
            fn=reset_environment,
            inputs=[task_dropdown, seed_input, state],
            outputs=[obs_output, task_output, status_output, state]
        )
        
        action_btn.click(
            fn=take_action,
            inputs=[
                action_dropdown,
                category_dropdown,
                priority_dropdown,
                reply_input,
                reasoning_input,
                state
            ],
            outputs=[obs_output, history_output, reward_output, status_output, state]
        )
        
        refresh_state_btn.click(
            fn=get_current_state,
            inputs=[state],
            outputs=[state_output]
        )
        
        gr.Markdown("""
---
## API Usage

This environment can also be used programmatically:

```python
from email_triage_env import EmailTriageEnv, Action, ActionType, EmailCategory

env = EmailTriageEnv(task_id="easy_categorization")
obs = env.reset(seed=42)

action = Action(
    action_type=ActionType.CATEGORIZE,
    category=EmailCategory.WORK
)
obs, reward, done, info = env.step(action)

# Get final score
from email_triage_env import grade_episode
result = grade_episode("easy_categorization", env.state())
print(f"Score: {result['score']}")
```

---
*Tagged with `openenv` for the OpenEnv ecosystem*
        """)
    
    return demo


# Health check endpoint
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft()
    )
