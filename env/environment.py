"""
Core Email Triage Environment.
"""

from typing import Tuple, Dict, Any, Optional
import copy
import random

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
from .email_generator import generate_task_emails
from .tasks import get_task_config
from .reward import RewardCalculator


class EmailTriageEnv:
    """
    Email Triage Environment for training AI agents on email management.
    
    This environment simulates a realistic email inbox where agents must:
    - Categorize emails correctly
    - Prioritize based on urgency
    - Identify and handle spam
    - Respond to emails that require action
    
    Implements the OpenEnv interface:
    - step(action) -> (observation, reward, done, info)
    - reset() -> observation
    - state() -> current_state
    
    Example:
        >>> env = EmailTriageEnv(task_id="easy_categorization")
        >>> obs = env.reset(seed=42)
        >>> action = Action(action_type=ActionType.CATEGORIZE, category=EmailCategory.WORK)
        >>> obs, reward, done, info = env.step(action)
    """
    
    def __init__(self, task_id: str = "easy_categorization"):
        """
        Initialize the environment with a specific task.
        
        Args:
            task_id: ID of the task to run. Available tasks:
                - easy_categorization: 5 emails, basic classification
                - medium_triage: 10 emails with spam and priorities
                - hard_inbox_zero: 20 emails, full triage with replies
        """
        self.task_config = get_task_config(task_id)
        self._state: Optional[EnvironmentState] = None
        self._ground_truth: Dict[str, Dict] = {}
        self._reward_calculator = RewardCalculator()
        self._seed: Optional[int] = None
        
    def reset(self, seed: Optional[int] = None) -> Observation:
        """
        Reset the environment to initial state.
        
        Args:
            seed: Optional random seed for reproducibility.
                  Using the same seed guarantees identical email generation.
            
        Returns:
            Initial observation containing the first email and inbox state.
        """
        # Set seed for reproducibility
        if seed is not None:
            self._seed = seed
            random.seed(seed)
        elif self._seed is not None:
            random.seed(self._seed)
        
        # Generate emails for this task
        emails = generate_task_emails(
            self.task_config.task_id,
            self.task_config.difficulty,
        )
        
        # Store ground truth for grading (not exposed to agent)
        self._ground_truth = {}
        for email in emails:
            self._ground_truth[email.id] = {
                "true_category": email._true_category,
                "true_priority": email._true_priority,
                "is_spam": email._is_spam,
                "requires_urgent_action": email._requires_urgent_action,
            }
        
        # Initialize state
        self._state = EnvironmentState(
            emails=emails,
            current_email_index=0,
            step_count=0,
            max_steps=self.task_config.max_steps,
            done=False,
            cumulative_reward=0.0,
            task_id=self.task_config.task_id,
            actions_taken=[],
            correct_categorizations=0,
            incorrect_categorizations=0,
            correct_priorities=0,
            incorrect_priorities=0,
            spam_caught=0,
            spam_missed=0,
            urgent_handled=0,
            urgent_missed=0,
            replies_sent=0,
            quality_replies=0,
        )
        
        return self._get_observation()
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        Execute an action and return the results.
        Now includes stochastic latency, incomplete info, rare events, and advanced reward.
        """
        import time
        from .reward import compute_reward
        if self._state is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        if self._state.done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")

        # --- Stochastic latency ---
        latency = random.uniform(0.05, 0.2)
        time.sleep(latency)

        # --- Incomplete info simulation (5% chance) ---
        incomplete_info = random.random() < 0.05
        if incomplete_info:
            obs = self._get_partial_observation()
        else:
            obs = self._get_observation()

        # --- Rare event simulation (1% chance) ---
        rare_event = random.random() < 0.01
        if rare_event:
            self._trigger_rare_event()

        # Record action
        self._state.actions_taken.append(action)
        self._state.step_count += 1

        # Get current email and ground truth
        current_email = self._get_current_email_with_truth()
        ground_truth = self._ground_truth.get(current_email.id, {}) if current_email else {}

        # --- Reward calculation (advanced, multi-component) ---
        progress_delta = self._compute_progress_delta()
        invalid_action = self._is_invalid_action(action, current_email)
        redundant_action = self._is_redundant_action(action)
        destructive_action = self._is_destructive_action(action, current_email)

        reward_breakdown = compute_reward(
            progress_delta=progress_delta,
            steps_taken=self._state.step_count,
            max_steps=self._state.max_steps,
            invalid_action=invalid_action,
            redundant_action=redundant_action,
            destructive_action=destructive_action,
        )
        reward = reward_breakdown.total

        # Update cumulative reward
        self._state.cumulative_reward += reward

        # Move to next email if action completes current one
        if self._action_completes_email(action):
            self._state.current_email_index += 1

        # Check if episode is done
        done = self._check_done()
        self._state.done = done

        # Info dict with reward breakdown and simulation details
        info = {
            "reward_breakdown": reward_breakdown.as_dict(),
            "latency": latency,
            "incomplete_info": incomplete_info,
            "rare_event": rare_event,
        }

        return obs, reward, done, info

    def _get_partial_observation(self):
        """Return an observation with some fields hidden (simulate incomplete info)."""
        obs = self._get_observation()
        if obs.current_email:
            obs.current_email.body = "[REDACTED]"  # Example: hide email body
        return obs

    def _trigger_rare_event(self):
        """Simulate a rare edge-case event (e.g., email corruption, urgent escalation)."""
        if self._state and self._state.emails:
            idx = random.randint(0, len(self._state.emails) - 1)
            self._state.emails[idx].is_urgent = True

    def _compute_progress_delta(self) -> float:
        """Compute progress made since last step (customize as needed)."""
        return 1.0 / max(1, len(self._state.emails))

    def _is_invalid_action(self, action, email) -> bool:
        """Return True if the action is invalid for the current state/email."""
        return email and email.is_spam and action.action_type == ActionType.REPLY

    def _is_redundant_action(self, action) -> bool:
        """Return True if the action is a repeat of the previous action."""
        if len(self._state.actions_taken) < 2:
            return False
        return self._state.actions_taken[-1] == self._state.actions_taken[-2]

    def _is_destructive_action(self, action, email) -> bool:
        """Return True if the action is destructive (e.g., deleting non-spam)."""
        return email and not email.is_spam and action.action_type == ActionType.DELETE
    
    def state(self) -> EnvironmentState:
        """
        Return the current internal state.
        
        This provides full access to the environment state for:
        - Checkpointing and restoration
        - Debugging and analysis
        - Grading at episode end
        
        Returns:
            Complete environment state (deep copy to prevent mutation)
            
        Raises:
            RuntimeError: If environment not initialized
        """
        if self._state is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        return copy.deepcopy(self._state)
    
    def _get_observation(self) -> Observation:
        """Construct observation from current state."""
        current_email = self._get_current_email()
        
        # Calculate inbox state
        emails = self._state.emails
        inbox_state = InboxState(
            total_emails=len(emails),
            unread_count=sum(1 for e in emails if not e.is_read),
            uncategorized_count=sum(1 for e in emails if e.category is None),
            flagged_count=sum(1 for e in emails if e.is_flagged),
        )
        
        # Determine available actions based on current email
        available_actions = self._get_available_actions(current_email)
        
        return Observation(
            current_email=current_email,
            inbox_state=inbox_state,
            emails_processed=self._state.current_email_index,
            emails_remaining=len(emails) - self._state.current_email_index,
            step_count=self._state.step_count,
            max_steps=self._state.max_steps,
            task_description=self.task_config.description,
            available_actions=available_actions,
        )
    
    def _get_current_email(self) -> Optional[Email]:
        """Get the current email being processed (without ground truth)."""
        if self._state.current_email_index >= len(self._state.emails):
            return None
        
        email = self._state.emails[self._state.current_email_index]
        
        # Return a copy without ground truth fields
        return Email(
            id=email.id,
            sender=email.sender,
            sender_name=email.sender_name,
            subject=email.subject,
            body=email.body,
            timestamp=email.timestamp,
            is_read=email.is_read,
            is_flagged=email.is_flagged,
            category=email.category,
            priority=email.priority,
            requires_response=email.requires_response,
        )
    
    def _get_current_email_with_truth(self) -> Optional[Email]:
        """Get the current email with ground truth intact."""
        if self._state.current_email_index >= len(self._state.emails):
            return None
        return self._state.emails[self._state.current_email_index]
    
    def _get_available_actions(self, email: Optional[Email]) -> list:
        """Determine available actions for the current state."""
        if email is None:
            return []
        return list(self.task_config.required_actions)
    
    def _update_metrics(
        self,
        action: Action,
        email: Optional[Email],
        ground_truth: Dict,
    ) -> None:
        """Update state metrics based on action taken."""
        if email is None:
            return
        
        true_category = ground_truth.get("true_category")
        true_priority = ground_truth.get("true_priority")
        is_spam = ground_truth.get("is_spam", False)
        requires_urgent = ground_truth.get("requires_urgent_action", False)
        
        if action.action_type == ActionType.CATEGORIZE:
            if action.category == true_category:
                self._state.correct_categorizations += 1
            else:
                self._state.incorrect_categorizations += 1
            # Update email
            self._state.emails[self._state.current_email_index].category = action.category
        
        elif action.action_type == ActionType.SET_PRIORITY:
            if action.priority == true_priority:
                self._state.correct_priorities += 1
            else:
                self._state.incorrect_priorities += 1
            # Update email
            self._state.emails[self._state.current_email_index].priority = action.priority
        
        elif action.action_type == ActionType.DELETE:
            if is_spam:
                self._state.spam_caught += 1
            else:
                self._state.spam_missed += 1
        
        elif action.action_type == ActionType.FLAG:
            if requires_urgent:
                self._state.urgent_handled += 1
            self._state.emails[self._state.current_email_index].is_flagged = True
        
        elif action.action_type == ActionType.REPLY:
            self._state.replies_sent += 1
            if action.reply_content and len(action.reply_content) > 50:
                self._state.quality_replies += 1
        
        elif action.action_type == ActionType.MARK_READ:
            self._state.emails[self._state.current_email_index].is_read = True
        
        elif action.action_type == ActionType.ARCHIVE:
            if requires_urgent:
                self._state.urgent_missed += 1
    
    def _action_completes_email(self, action: Action) -> bool:
        """Check if an action completes processing of current email."""
        completing_actions = {
            ActionType.ARCHIVE,
            ActionType.DELETE,
            ActionType.REPLY,
            ActionType.FORWARD,
            ActionType.SKIP,
        }
        return action.action_type in completing_actions
    
    def _check_done(self) -> bool:
        """Check if the episode is complete."""
        # Done if all emails processed
        if self._state.current_email_index >= len(self._state.emails):
            return True
        
        # Done if max steps reached
        if self._state.step_count >= self._state.max_steps:
            return True
        
        return False
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional info dict."""
        return {
            "task_id": self.task_config.task_id,
            "task_name": self.task_config.name,
            "difficulty": self.task_config.difficulty,
            "emails_processed": self._state.current_email_index,
            "total_emails": len(self._state.emails),
            "steps_taken": self._state.step_count,
            "max_steps": self._state.max_steps,
            "correct_categorizations": self._state.correct_categorizations,
            "incorrect_categorizations": self._state.incorrect_categorizations,
            "correct_priorities": self._state.correct_priorities,
            "incorrect_priorities": self._state.incorrect_priorities,
            "spam_caught": self._state.spam_caught,
            "spam_missed": self._state.spam_missed,
            "urgent_handled": self._state.urgent_handled,
            "urgent_missed": self._state.urgent_missed,
            "replies_sent": self._state.replies_sent,
            "quality_replies": self._state.quality_replies,
        }
    
    def get_final_score(self) -> float:
        """
        Calculate final score for the episode (0.0 to 1.0).
        
        This is a convenience method. For detailed grading,
        use the grade_episode function from tasks.py.
        
        Returns:
            Float score between 0.0 and 1.0
        """
        if self._state is None:
            return 0.0
        
        from .tasks import grade_episode
        result = grade_episode(self.task_config.task_id, self._state)
        return result["score"]
    
    @property
    def task_id(self) -> str:
        """Get the current task ID."""
        return self.task_config.task_id
    
    @property
    def difficulty(self) -> str:
        """Get the current task difficulty."""
        return self.task_config.difficulty
    
    @property
    def is_done(self) -> bool:
        """Check if the current episode is done."""
        return self._state.done if self._state else False
