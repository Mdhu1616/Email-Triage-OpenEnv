"""
Email Triage OpenEnv Environment

A real-world simulation environment for training AI agents on email management tasks.
Implements the full OpenEnv specification with typed models, step/reset/state API,
and programmatic graders for evaluation.

Example usage:
    from email_triage_env import EmailTriageEnv, Action, ActionType, EmailCategory
    
    # Create environment with a task
    env = EmailTriageEnv(task_id="easy_categorization")
    
    # Reset to get initial observation
    obs = env.reset(seed=42)
    
    # Take actions
    action = Action(
        action_type=ActionType.CATEGORIZE,
        category=EmailCategory.WORK,
        reasoning="This email is from a colleague about a project"
    )
    obs, reward, done, info = env.step(action)
    
    # Get current state
    state = env.state()
    
    # Grade performance
    from email_triage_env import grade_episode
    result = grade_episode("easy_categorization", state)
    print(f"Score: {result['score']}")
"""

from .models import (
    Email,
    EmailCategory,
    EmailPriority,
    ActionType,
    Action,
    Observation,
    Reward,
    EnvironmentState,
    InboxState,
    TaskConfig,
)

from .environment import EmailTriageEnv

from .tasks import (
    TASKS,
    get_task_config,
    get_all_tasks,
    TaskGrader,
    grade_episode,
)

from .email_generator import (
    generate_email,
    generate_email_batch,
    generate_task_emails,
)

__version__ = "1.0.0"

__all__ = [
    # Environment
    "EmailTriageEnv",
    
    # Models
    "Email",
    "EmailCategory",
    "EmailPriority",
    "ActionType",
    "Action",
    "Observation",
    "Reward",
    "EnvironmentState",
    "InboxState",
    "TaskConfig",
    
    # Tasks and grading
    "TASKS",
    "get_task_config",
    "get_all_tasks",
    "TaskGrader",
    "grade_episode",
    
    # Email generation
    "generate_email",
    "generate_email_batch",
    "generate_task_emails",
]
