"""
Email Triage OpenEnv Environment

A real-world simulation environment for training AI agents on email management tasks.
Implements the OpenEnv specification with typed models, programmatic graders, and
reproducible baselines.

OpenEnv Interface:
    - step(action) -> (observation, reward, done, info)
    - reset() -> observation  
    - state() -> current_state

Example:
    >>> from env import EmailTriageEnv, Action, ActionType, EmailCategory
    >>> 
    >>> # Create environment
    >>> env = EmailTriageEnv(task_id="easy_categorization")
    >>> 
    >>> # Reset to get initial observation
    >>> obs = env.reset(seed=42)
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
