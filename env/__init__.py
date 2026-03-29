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
from .tasks import get_task_config, get_all_tasks, grade_episode
from .email_generator import generate_task_emails
from .reward import RewardCalculator

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
    "get_task_config",
    "get_all_tasks",
    "grade_episode",
    "generate_task_emails",
    "RewardCalculator",
]
    >>> 
    >>> # Take an action
    >>> action = Action(
    ...     action_type=ActionType.CATEGORIZE,
    ...     category=EmailCategory.WORK,
    ...     reasoning="Work email from colleague"
    ... )
    >>> obs, reward, done, info = env.step(action)
    >>> 
    >>> # Get final score
    >>> result = grade_episode("easy_categorization", env.state())
    >>> print(f"Score: {result['score']:.2f}")
"""

__version__ = "1.0.0"
__author__ = "OpenEnv"
__license__ = "MIT"

# Core environment
from .environment import EmailTriageEnv

# Models
from .models import (
    # Enums
    EmailPriority,
    EmailCategory,
    ActionType,
    # Data models
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
from .email_generator import (
    generate_email,
    generate_email_batch,
    generate_task_emails,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Core
    "EmailTriageEnv",
    # Enums
    "EmailPriority",
    "EmailCategory", 
    "ActionType",
    # Models
    "Email",
    "InboxState",
    "Observation",
    "Action",
    "Reward",
    "RewardComponent",
    "EnvironmentState",
    "TaskConfig",
    # Tasks
    "TASKS",
    "get_task_config",
    "get_all_tasks",
    "list_tasks",
    "TaskGrader",
    "grade_episode",
    # Rewards
    "RewardCalculator",
    "REWARD_CONFIG",
    # Generation
    "generate_email",
    "generate_email_batch",
    "generate_task_emails",
]
