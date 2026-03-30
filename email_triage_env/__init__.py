"""
Email Triage Environment.
"""

from .environment import EmailTriageEnv
from .models import (
    Action,
    ActionType,
    Email,
    EmailCategory,
    EmailPriority,
    Observation,
    Reward,
    EnvironmentState,
    InboxState,
    TaskConfig,
)
from .tasks import TASKS, get_task_config
from .email_generator import generate_task_emails

__all__ = [
    "EmailTriageEnv",
    "Action",
    "ActionType",
    "Email",
    "EmailCategory",
    "EmailPriority",
    "Observation",
    "Reward",
    "EnvironmentState",
    "InboxState",
    "TaskConfig",
    "TASKS",
    "get_task_config",
    "generate_task_emails",
]
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
