"""
Pydantic models for the Email Triage environment.
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass

@dataclass
class RewardComponent:
    name: str
    value: float
    description: str

class EmailPriority(str, Enum):
    """Priority levels for emails."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class EmailCategory(str, Enum):
    """Categories for email classification."""
    WORK = "work"
    PERSONAL = "personal"
    SPAM = "spam"
    NEWSLETTER = "newsletter"
    SUPPORT = "support"
    BILLING = "billing"


class ActionType(str, Enum):
    """Types of actions the agent can take."""
    CATEGORIZE = "categorize"
    SET_PRIORITY = "set_priority"
    ARCHIVE = "archive"
    DELETE = "delete"
    REPLY = "reply"
    FORWARD = "forward"
    FLAG = "flag"
    MARK_READ = "mark_read"
    SKIP = "skip"
    REPORT_PHISHING = "report_phishing"  # New action for phishing detection


class Email(BaseModel):
    """Represents a single email in the inbox."""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(description="Unique identifier for the email")
    sender: str = Field(description="Email sender address")
    sender_name: str = Field(description="Display name of sender")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    timestamp: str = Field(description="ISO timestamp when received")
    is_read: bool = Field(default=False, description="Whether email has been read")
    is_flagged: bool = Field(default=False, description="Whether email is flagged")
    category: Optional[EmailCategory] = Field(default=None, description="Assigned category")
    priority: Optional[EmailPriority] = Field(default=None, description="Assigned priority")
    requires_response: bool = Field(default=False, description="Whether email needs a reply")
    
    # Ground truth for grading (hidden from agent in observations)
    _true_category: Optional[EmailCategory] = None
    _true_priority: Optional[EmailPriority] = None
    _is_spam: bool = False
    _is_phishing: bool = False  # New field for phishing ground truth
    _requires_urgent_action: bool = False


class InboxState(BaseModel):
    """Current state of the inbox."""
    total_emails: int = Field(description="Total number of emails in inbox")
    unread_count: int = Field(description="Number of unread emails")
    uncategorized_count: int = Field(description="Number of emails without category")
    flagged_count: int = Field(description="Number of flagged emails")


class Observation(BaseModel):
    """
    The observation returned to the agent after each step.
    Contains the current email being processed and inbox state.
    """
    current_email: Optional[Email] = Field(
        default=None, 
        description="The email currently being processed"
    )
    inbox_state: InboxState = Field(description="Current state of the inbox")
    emails_processed: int = Field(
        default=0, 
        description="Number of emails processed so far"
    )
    emails_remaining: int = Field(
        default=0,
        description="Number of emails remaining to process"
    )
    step_count: int = Field(default=0, description="Current step number")
    max_steps: int = Field(description="Maximum steps allowed")
    task_description: str = Field(description="Description of the current task")
    available_actions: List[ActionType] = Field(
        description="List of valid actions for current state"
    )


class Action(BaseModel):
    """
    An action taken by the agent.
    """
    action_type: ActionType = Field(description="Type of action to perform")
    category: Optional[EmailCategory] = Field(
        default=None, 
        description="Category to assign (for CATEGORIZE action)"
    )
    priority: Optional[EmailPriority] = Field(
        default=None,
        description="Priority to set (for SET_PRIORITY action)"
    )
    reply_content: Optional[str] = Field(
        default=None,
        description="Reply message content (for REPLY action)"
    )
    forward_to: Optional[str] = Field(
        default=None,
        description="Email address to forward to (for FORWARD action)"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Agent's reasoning for this action"
    )


class RewardComponent(BaseModel):
    """Individual reward component with name and value."""
    name: str = Field(description="Name of the reward component")
    value: float = Field(description="Reward value for this component")
    description: str = Field(default="", description="Description of why this reward was given")


class Reward(BaseModel):
    """
    Reward signal returned after each action.
    Provides both immediate and cumulative feedback with detailed breakdown.
    """
    immediate: float = Field(
        description="Immediate reward for the action (-1.0 to 1.0)"
    )
    cumulative: float = Field(
        description="Cumulative reward over the episode"
    )
    components: List[RewardComponent] = Field(
        default_factory=list,
        description="List of individual reward components"
    )
    breakdown: dict = Field(
        default_factory=dict,
        description="Breakdown of reward components (dict format)"
    )
    feedback: str = Field(
        default="",
        description="Human-readable feedback on the action"
    )


class EnvironmentState(BaseModel):
    """
    Complete internal state of the environment.
    Used for state() method and checkpointing.
    """
    emails: List[Email] = Field(description="All emails in the environment")
    current_email_index: int = Field(default=0, description="Index of current email")
    step_count: int = Field(default=0, description="Number of steps taken")
    max_steps: int = Field(description="Maximum steps allowed")
    done: bool = Field(default=False, description="Whether episode is complete")
    cumulative_reward: float = Field(default=0.0, description="Total reward accumulated")
    task_id: str = Field(description="ID of the current task")
    actions_taken: List[Action] = Field(
        default_factory=list, 
        description="History of actions taken"
    )
    
    # Grading metrics
    correct_categorizations: int = Field(default=0)
    incorrect_categorizations: int = Field(default=0)
    correct_priorities: int = Field(default=0)
    incorrect_priorities: int = Field(default=0)
    spam_caught: int = Field(default=0)
    spam_missed: int = Field(default=0)
    urgent_handled: int = Field(default=0)
    urgent_missed: int = Field(default=0)
    replies_sent: int = Field(default=0)
    quality_replies: int = Field(default=0)


class TaskConfig(BaseModel):
    """Configuration for a specific task."""
    task_id: str = Field(description="Unique task identifier")
    name: str = Field(description="Human-readable task name")
    description: str = Field(description="Detailed task description")
    difficulty: str = Field(description="easy, medium, or hard")
    num_emails: int = Field(description="Number of emails in task")
    max_steps: int = Field(description="Maximum steps allowed")
    required_actions: List[ActionType] = Field(
        description="Actions required to complete task"
    )
    success_threshold: float = Field(
        default=0.7,
        description="Minimum score to consider task successful"
    )
    grading_weights: dict = Field(
        default_factory=dict,
        description="Weights for different scoring criteria"
    )
