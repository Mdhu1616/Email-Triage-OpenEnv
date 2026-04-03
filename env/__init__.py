"""
Email Triage Environment.
"""

# Version info


# Core environment
from .environment import EmailTriageEnv

# Models
from .models import (
    EmailPriority,
    EmailCategory,
    ActionType,
    Email,
    InboxState,
    Observation,
    Action,
    Reward,
    RewardComponent,
    EnvironmentState,
    TaskConfig,
)

# Tasks and grading
from .tasks import (
    TASKS,
    get_task_config,
    get_all_tasks,
    list_tasks,
    TaskGrader,
    grade_episode,
)

# Reward system
from .reward import (
    RewardCalculator,
    REWARD_CONFIG,
)

# Email generation
from .email_generator import generate_task_emails

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "EmailTriageEnv",
    "EmailPriority",
    "EmailCategory",
    "ActionType",
    "Email",
    "InboxState",
    "Observation",
    "Action",
    "Reward",
    "RewardComponent",
    "EnvironmentState",
    "TaskConfig",
    "TASKS",
    "get_task_config",
    "get_all_tasks",
    "list_tasks",
    "TaskGrader",
    "grade_episode",
    "RewardCalculator",
    "REWARD_CONFIG",
    "generate_email",
    "generate_email_batch",
    "generate_task_emails",
]