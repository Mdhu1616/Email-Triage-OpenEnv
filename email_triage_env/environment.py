"""
Core Email Triage Environment.
"""

from typing import Tuple, Dict, Any, Optional
import copy

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
from .tasks import TASKS, get_task_config


class EmailTriageEnv:
    """
    Email Triage Environment for training AI agents on email management.
    
    This environment simulates a realistic email inbox where agents must:
    - Categorize emails correctly
    - Prioritize based on urgency
    - Identify and handle spam
    - Respond to emails that require action
    
    Implements the standard interface:
    - step(action) -> (observation, reward, done, info)
    - reset() -> observation
    - state() -> current_state
    """

    def _get_partial_observation(self):
        """Defensive: always return an Observation object, never a dict."""
        obs = self._get_observation()
        if isinstance(obs, dict):
            obs = Observation(**obs)
        return obs
    
    def __init__(self, task_id: str = "easy_categorization"):
        """
        Initialize the environment with a specific task.
        
        Args:
            task_id: ID of the task to run (easy_categorization, medium_triage, hard_inbox_zero)
        """
        self.task_config = get_task_config(task_id)
        self._state: Optional[EnvironmentState] = None
        self._ground_truth: Dict[str, Dict] = {}
        
    def reset(self, seed: Optional[int] = None) -> Observation:
        """
        Reset the environment to initial state.
        
        Args:
            seed: Optional random seed for reproducibility
            
        Returns:
            Initial observation
        """
        if seed is not None:
            import random
            random.seed(seed)
        
        # Generate emails for this task
        emails = generate_task_emails(
            self.task_config.task_id,
            self.task_config.difficulty,
        )
        
        # Store ground truth for grading
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
        )
        
        return self._get_observation()
    
    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """
        Execute an action and return the results.
        
        Args:
            action: The action to take
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        if self._state is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        
        if self._state.done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        
        # Record action
        self._state.actions_taken.append(action)
        self._state.step_count += 1
        
        # Get current email
        current_email = self._get_current_email()
        
        # Process action and calculate reward
        reward_value, feedback, reward_breakdown = self._process_action(action, current_email)
        
        # Update cumulative reward
        self._state.cumulative_reward += reward_value
        
        # Move to next email if action completes current one
        if self._action_completes_email(action):
            self._state.current_email_index += 1
        
        # Check if episode is done
        done = self._check_done()
        self._state.done = done
        
        # Create reward object
        reward = Reward(
            immediate=reward_value,
            cumulative=self._state.cumulative_reward,
            breakdown=reward_breakdown,
            feedback=feedback,
        )
        
        # Get info dict
        info = self._get_info()
        
        obs = self._get_observation()
        # Defensive: if obs is a dict, convert to Observation
        if isinstance(obs, dict):
            obs = Observation(**obs)
        return obs, reward, done, info
    
    def state(self) -> EnvironmentState:
        """
        Return the current internal state.
        
        Returns:
            Complete environment state
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
        """Get the current email being processed."""
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
    
    def _get_available_actions(self, email: Optional[Email]) -> list:
        """Determine available actions for the current state."""
        if email is None:
            return []
        
        return list(self.task_config.required_actions)
    
    def _process_action(
        self, 
        action: Action, 
        email: Optional[Email]
    ) -> Tuple[float, str, Dict]:
        """
        Process an action and return reward information.
        
        Returns:
            Tuple of (reward_value, feedback_string, reward_breakdown)
        """
        if email is None:
            return -0.1, "No email to process.", {"penalty": -0.1}
        
        reward = 0.0
        feedback_parts = []
        breakdown = {}
        
        ground_truth = self._ground_truth.get(email.id, {})
        true_category = ground_truth.get("true_category")
        true_priority = ground_truth.get("true_priority")
        is_spam = ground_truth.get("is_spam", False)
        requires_urgent = ground_truth.get("requires_urgent_action", False)
        
        # Process based on action type
        if action.action_type == ActionType.CATEGORIZE:
            if action.category == true_category:
                reward += 0.3
                feedback_parts.append("Correct categorization!")
                breakdown["categorization"] = 0.3
                self._state.correct_categorizations += 1
            else:
                reward -= 0.2
                feedback_parts.append(f"Incorrect category. Expected {true_category.value}.")
                breakdown["categorization"] = -0.2
                self._state.incorrect_categorizations += 1
            
            # Update email category
            self._state.emails[self._state.current_email_index].category = action.category
        
        elif action.action_type == ActionType.SET_PRIORITY:
            if action.priority == true_priority:
                reward += 0.2
                feedback_parts.append("Correct priority!")
                breakdown["priority"] = 0.2
                self._state.correct_priorities += 1
            else:
                # Penalize more for missing urgent items
                if true_priority == EmailPriority.URGENT:
                    reward -= 0.4
                    feedback_parts.append("Missed URGENT priority!")
                    breakdown["priority"] = -0.4
                else:
                    reward -= 0.1
                    feedback_parts.append(f"Incorrect priority. Expected {true_priority.value}.")
                    breakdown["priority"] = -0.1
                self._state.incorrect_priorities += 1
            
            # Update email priority
            self._state.emails[self._state.current_email_index].priority = action.priority
        
        elif action.action_type == ActionType.DELETE:
            if is_spam:
                reward += 0.4
                feedback_parts.append("Good catch! Spam deleted.")
                breakdown["spam_handling"] = 0.4
                self._state.spam_caught += 1
            else:
                reward -= 0.5
                feedback_parts.append("Deleted a non-spam email!")
                breakdown["spam_handling"] = -0.5
        
        elif action.action_type == ActionType.ARCHIVE:
            if not is_spam and not requires_urgent:
                reward += 0.1
                feedback_parts.append("Email archived.")
                breakdown["archive"] = 0.1
            elif requires_urgent:
                reward -= 0.3
                feedback_parts.append("Archived an urgent email without handling it!")
                breakdown["archive"] = -0.3
                self._state.urgent_missed += 1
            else:
                reward -= 0.1
                feedback_parts.append("Archived spam instead of deleting it.")
                breakdown["archive"] = -0.1
        
        elif action.action_type == ActionType.FLAG:
            if requires_urgent:
                reward += 0.3
                feedback_parts.append("Good! Flagged urgent email.")
                breakdown["flag"] = 0.3
                self._state.urgent_handled += 1
            else:
                reward += 0.05
                feedback_parts.append("Email flagged.")
                breakdown["flag"] = 0.05
            
            self._state.emails[self._state.current_email_index].is_flagged = True
        
        elif action.action_type == ActionType.REPLY:
            if email.requires_response:
                if action.reply_content and len(action.reply_content) > 10:
                    reward += 0.4
                    feedback_parts.append("Good response sent!")
                    breakdown["reply"] = 0.4
                else:
                    reward += 0.1
                    feedback_parts.append("Reply sent, but content was minimal.")
                    breakdown["reply"] = 0.1
            else:
                reward -= 0.1
                feedback_parts.append("Email didn't require a reply.")
                breakdown["reply"] = -0.1
        
        elif action.action_type == ActionType.MARK_READ:
            self._state.emails[self._state.current_email_index].is_read = True
            reward += 0.05
            feedback_parts.append("Marked as read.")
            breakdown["mark_read"] = 0.05
        
        elif action.action_type == ActionType.SKIP:
            # Small penalty for skipping
            reward -= 0.05
            feedback_parts.append("Skipped email.")
            breakdown["skip"] = -0.05
        
        elif action.action_type == ActionType.FORWARD:
            reward += 0.1
            feedback_parts.append("Email forwarded.")
            breakdown["forward"] = 0.1
        
        # Bonus for providing reasoning
        if action.reasoning and len(action.reasoning) > 20:
            reward += 0.05
            breakdown["reasoning_bonus"] = 0.05
        
        # Step penalty to encourage efficiency
        step_penalty = -0.01
        reward += step_penalty
        breakdown["step_penalty"] = step_penalty
        
        return reward, " ".join(feedback_parts), breakdown
    
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
            "difficulty": self.task_config.difficulty,
            "emails_processed": self._state.current_email_index,
            "total_emails": len(self._state.emails),
            "steps_taken": self._state.step_count,
            "max_steps": self._state.max_steps,
            "correct_categorizations": self._state.correct_categorizations,
            "incorrect_categorizations": self._state.incorrect_categorizations,
            "spam_caught": self._state.spam_caught,
            "urgent_handled": self._state.urgent_handled,
        }
    
    def get_final_score(self) -> float:
        """
        Calculate final score for the episode (0.0 to 1.0).
        Used by graders for task evaluation.
        """
        if self._state is None:
            return 0.0
        
        score_components = []
        
        # Categorization accuracy
        total_categorizations = (
            self._state.correct_categorizations + 
            self._state.incorrect_categorizations
        )
        if total_categorizations > 0:
            cat_accuracy = self._state.correct_categorizations / total_categorizations
            score_components.append(("categorization", cat_accuracy, 0.3))
        
        # Priority accuracy
        total_priorities = (
            self._state.correct_priorities + 
            self._state.incorrect_priorities
        )
        if total_priorities > 0:
            priority_accuracy = self._state.correct_priorities / total_priorities
            score_components.append(("priority", priority_accuracy, 0.2))
        
        # Spam handling
        total_spam = self._state.spam_caught + self._state.spam_missed
        if total_spam > 0:
            spam_accuracy = self._state.spam_caught / total_spam
            score_components.append(("spam", spam_accuracy, 0.2))
        
        # Urgent handling
        total_urgent = self._state.urgent_handled + self._state.urgent_missed
        if total_urgent > 0:
            urgent_accuracy = self._state.urgent_handled / total_urgent
            score_components.append(("urgent", urgent_accuracy, 0.2))
        
        # Completion rate
        completion = self._state.current_email_index / len(self._state.emails)
        score_components.append(("completion", completion, 0.1))
        
        # Calculate weighted score
        total_weight = sum(weight for _, _, weight in score_components)
        if total_weight == 0:
            return 0.0
        
        weighted_score = sum(
            score * weight for _, score, weight in score_components
        ) / total_weight
        
        return min(1.0, max(0.0, weighted_score))
