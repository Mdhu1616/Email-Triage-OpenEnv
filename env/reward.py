
"""
Advanced Reward function for Email Triage OpenEnv.
Multi-component, research-grade, and hackathon-ready.
"""

from typing import Dict, Any, Optional, Tuple, List
from .models import Action, ActionType, Email, EmailCategory, EmailPriority

class RewardBreakdown:
    def __init__(
        self,
        progress: float,
        efficiency: float,
        penalty_invalid: float,
        penalty_redundancy: float,
        penalty_destructive: float,
    ):
        self.progress = progress
        self.efficiency = efficiency
        self.penalty_invalid = penalty_invalid
        self.penalty_redundancy = penalty_redundancy
        self.penalty_destructive = penalty_destructive

    @property
    def total(self) -> float:
        return (
            self.progress
            + self.efficiency
            + self.penalty_invalid
            + self.penalty_redundancy
            + self.penalty_destructive
        )

    def as_dict(self) -> Dict[str, float]:
        return {
            "progress_reward": self.progress,
            "efficiency_reward": self.efficiency,
            "penalty_invalid_actions": self.penalty_invalid,
            "penalty_redundancy": self.penalty_redundancy,
            "penalty_destructive_actions": self.penalty_destructive,
            "total": self.total,
        }

def compute_reward(
    progress_delta: float,
    steps_taken: int,
    max_steps: int,
    invalid_action: bool,
    redundant_action: bool,
    destructive_action: bool,
) -> RewardBreakdown:
    # Progress reward: proportional to progress
    progress = progress_delta * 1.0

    # Efficiency: fewer steps is better
    efficiency = -0.01 * (steps_taken / max_steps)

    # Penalties
    penalty_invalid = -0.2 if invalid_action else 0.0
    penalty_redundancy = -0.1 if redundant_action else 0.0
    penalty_destructive = -0.5 if destructive_action else 0.0

    return RewardBreakdown(
        progress=progress,
        efficiency=efficiency,
        penalty_invalid=penalty_invalid,
        penalty_redundancy=penalty_redundancy,
        penalty_destructive=penalty_destructive,
    )

# Example usage in your environment:
# reward_breakdown = compute_reward(progress_delta, steps, max_steps, invalid, redundant, destructive)
# reward = reward_breakdown.total
# info = {"reward_breakdown": reward_breakdown.as_dict()}


class RewardCalculator:
    """
    Calculates rewards for actions in the Email Triage environment.
    
    Reward range: approximately -1.0 to +1.0 per step
    
    The reward function is designed to:
    1. Provide positive signals for correct actions
    2. Penalize mistakes proportionally to their severity
    3. Guide the agent toward efficient, accurate email processing
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the reward calculator.
        
        Args:
            config: Optional custom reward configuration
        """
        self.config = config or REWARD_CONFIG.copy()
    
    def calculate(
        self,
        action: Action,
        email: Optional[Email],
        ground_truth: Dict,
        state_metrics: Dict,
    ) -> Tuple[float, str, Dict, List[RewardComponent]]:
        """
        Calculate reward for an action.
        
        Args:
            action: The action taken by the agent
            email: The current email (may be None)
            ground_truth: Dict with true_category, true_priority, is_spam, requires_urgent_action
            state_metrics: Current state metrics (step_count, etc.)
            
        Returns:
            Tuple of (total_reward, feedback_string, breakdown_dict, components_list)
        """
        if email is None:
            return self._no_email_reward()
        
        components: List[RewardComponent] = []
        feedback_parts: List[str] = []
        
        true_category = ground_truth.get("true_category")
        true_priority = ground_truth.get("true_priority")
        is_spam = ground_truth.get("is_spam", False)
        requires_urgent = ground_truth.get("requires_urgent_action", False)
        requires_response = email.requires_response
        
        # Process based on action type
        if action.action_type == ActionType.CATEGORIZE:
            reward, feedback, comp = self._reward_categorize(
                action, true_category, is_spam
            )
            components.extend(comp)
            feedback_parts.append(feedback)
        
        elif action.action_type == ActionType.SET_PRIORITY:
            reward, feedback, comp = self._reward_priority(
                action, true_priority, requires_urgent
            )
            components.extend(comp)
            feedback_parts.append(feedback)
        
        elif action.action_type == ActionType.DELETE:
            reward, feedback, comp = self._reward_delete(is_spam)
            components.extend(comp)
            feedback_parts.append(feedback)
        
        elif action.action_type == ActionType.ARCHIVE:
            reward, feedback, comp = self._reward_archive(
                is_spam, requires_urgent, requires_response
            )
            components.extend(comp)
            feedback_parts.append(feedback)
        
        elif action.action_type == ActionType.FLAG:
            reward, feedback, comp = self._reward_flag(requires_urgent)
            components.extend(comp)
            feedback_parts.append(feedback)
        
        elif action.action_type == ActionType.REPLY:
            reward, feedback, comp = self._reward_reply(
                action, requires_response
            )
            components.extend(comp)
            feedback_parts.append(feedback)
        
        elif action.action_type == ActionType.FORWARD:
            reward, feedback, comp = self._reward_forward(action)
            components.extend(comp)
            feedback_parts.append(feedback)
        
        elif action.action_type == ActionType.MARK_READ:
            reward, feedback, comp = self._reward_mark_read()
            components.extend(comp)
            feedback_parts.append(feedback)
        
        elif action.action_type == ActionType.SKIP:
            reward, feedback, comp = self._reward_skip()
            components.extend(comp)
            feedback_parts.append(feedback)
        
        else:
            reward, feedback, comp = self._invalid_action()
            components.extend(comp)
            feedback_parts.append(feedback)
        
        # Add reasoning bonus
        if action.reasoning and len(action.reasoning) > 20:
            bonus = self.config["reasoning_bonus"]
            components.append(RewardComponent(
                name="reasoning_bonus",
                value=bonus,
                description="Bonus for providing detailed reasoning"
            ))
        
        # Add step penalty
        step_penalty = self.config["step_penalty"]
        components.append(RewardComponent(
            name="step_penalty",
            value=step_penalty,
            description="Per-step cost to encourage efficiency"
        ))
        
        # Calculate total reward
        total_reward = sum(c.value for c in components)
        
        # Clamp to reasonable range
        total_reward = max(-1.0, min(1.0, total_reward))
        
        # Build breakdown dict
        breakdown = {c.name: c.value for c in components}
        
        return total_reward, " ".join(feedback_parts), breakdown, components
    
    def _no_email_reward(self) -> Tuple[float, str, Dict, List[RewardComponent]]:
        """Reward when there's no email to process."""
        penalty = self.config["no_email"]
        return (
            penalty,
            "No email to process.",
            {"no_email": penalty},
            [RewardComponent(
                name="no_email",
                value=penalty,
                description="No email available to process"
            )]
        )
    
    def _reward_categorize(
        self,
        action: Action,
        true_category: Optional[EmailCategory],
        is_spam: bool,
    ) -> Tuple[float, str, List[RewardComponent]]:
        """Calculate reward for categorization action."""
        components = []
        
        if action.category == true_category:
            reward = self.config["correct_categorization"]
            components.append(RewardComponent(
                name="correct_categorization",
                value=reward,
                description=f"Correctly categorized as {true_category.value}"
            ))
            return reward, "Correct categorization!", components
        else:
            # Partial credit for close categories
            penalty = self.config["incorrect_categorization"]
            
            # Less penalty if spam vs non-spam confusion
            if is_spam and action.category == EmailCategory.SPAM:
                reward = self.config["correct_categorization"] * 0.5
                components.append(RewardComponent(
                    name="partial_categorization",
                    value=reward,
                    description="Identified spam category (partial credit)"
                ))
                return reward, "Identified as spam (partial credit).", components
            
            components.append(RewardComponent(
                name="incorrect_categorization",
                value=penalty,
                description=f"Wrong category. Expected {true_category.value if true_category else 'unknown'}."
            ))
            expected = true_category.value if true_category else "unknown"
            return penalty, f"Incorrect category. Expected {expected}.", components
    
    def _reward_priority(
        self,
        action: Action,
        true_priority: Optional[EmailPriority],
        requires_urgent: bool,
    ) -> Tuple[float, str, List[RewardComponent]]:
        """Calculate reward for priority setting action."""
        components = []
        
        if action.priority == true_priority:
            # Extra reward for correctly identifying urgent
            if true_priority == EmailPriority.URGENT:
                reward = self.config["correct_urgent_priority"]
                components.append(RewardComponent(
                    name="correct_urgent_priority",
                    value=reward,
                    description="Correctly identified URGENT priority"
                ))
                return reward, "Correct! Identified as URGENT.", components
            else:
                reward = self.config["correct_priority"]
                components.append(RewardComponent(
                    name="correct_priority",
                    value=reward,
                    description=f"Correctly set priority to {true_priority.value}"
                ))
                return reward, "Correct priority!", components
        else:
            # Heavy penalty for missing urgent
            if requires_urgent and action.priority != EmailPriority.URGENT:
                penalty = self.config["missed_urgent"]
                components.append(RewardComponent(
                    name="missed_urgent",
                    value=penalty,
                    description="Failed to identify URGENT email"
                ))
                return penalty, "MISSED URGENT email!", components
            else:
                # Partial credit for close priorities
                priority_order = [
                    EmailPriority.LOW,
                    EmailPriority.NORMAL,
                    EmailPriority.HIGH,
                    EmailPriority.URGENT
                ]
                
                if action.priority and true_priority:
                    distance = abs(
                        priority_order.index(action.priority) - 
                        priority_order.index(true_priority)
                    )
                    # Less penalty for close priorities
                    base_penalty = self.config["incorrect_priority"]
                    adjusted = base_penalty * (0.5 + 0.5 * distance / 3)
                else:
                    adjusted = self.config["incorrect_priority"]
                
                components.append(RewardComponent(
                    name="incorrect_priority",
                    value=adjusted,
                    description=f"Wrong priority. Expected {true_priority.value if true_priority else 'unknown'}."
                ))
                expected = true_priority.value if true_priority else "unknown"
                return adjusted, f"Incorrect priority. Expected {expected}.", components
    
    def _reward_delete(
        self,
        is_spam: bool,
    ) -> Tuple[float, str, List[RewardComponent]]:
        """Calculate reward for delete action."""
        components = []
        
        if is_spam:
            reward = self.config["spam_deleted"]
            components.append(RewardComponent(
                name="spam_deleted",
                value=reward,
                description="Correctly deleted spam email"
            ))
            return reward, "Good catch! Spam deleted.", components
        else:
            penalty = self.config["deleted_non_spam"]
            components.append(RewardComponent(
                name="deleted_non_spam",
                value=penalty,
                description="Deleted legitimate email (severe penalty)"
            ))
            return penalty, "ERROR: Deleted a legitimate email!", components
    
    def _reward_archive(
        self,
        is_spam: bool,
        requires_urgent: bool,
        requires_response: bool,
    ) -> Tuple[float, str, List[RewardComponent]]:
        """Calculate reward for archive action."""
        components = []
        
        if requires_urgent:
            penalty = self.config["archived_urgent"]
            components.append(RewardComponent(
                name="archived_urgent",
                value=penalty,
                description="Archived urgent email without handling"
            ))
            return penalty, "Archived urgent email without action!", components
        elif is_spam:
            penalty = self.config["archived_spam"]
            components.append(RewardComponent(
                name="archived_spam",
                value=penalty,
                description="Archived spam instead of deleting"
            ))
            return penalty, "Should delete spam, not archive.", components
        elif requires_response:
            # Small penalty for archiving without reply
            penalty = self.config["archived_spam"] * 0.5
            components.append(RewardComponent(
                name="archived_needs_reply",
                value=penalty,
                description="Archived email that needed a reply"
            ))
            return penalty, "This email needed a reply.", components
        else:
            reward = self.config["correct_archive"]
            components.append(RewardComponent(
                name="correct_archive",
                value=reward,
                description="Correctly archived email"
            ))
            return reward, "Email archived.", components
    
    def _reward_flag(
        self,
        requires_urgent: bool,
    ) -> Tuple[float, str, List[RewardComponent]]:
        """Calculate reward for flag action."""
        components = []
        
        if requires_urgent:
            reward = self.config["urgent_flagged"]
            components.append(RewardComponent(
                name="urgent_flagged",
                value=reward,
                description="Correctly flagged urgent email"
            ))
            return reward, "Good! Flagged urgent email.", components
        else:
            # Neutral - flagging non-urgent is fine but not rewarded much
            reward = 0.02
            components.append(RewardComponent(
                name="flag_neutral",
                value=reward,
                description="Flagged email (neutral)"
            ))
            return reward, "Email flagged.", components
    
    def _reward_reply(
        self,
        action: Action,
        requires_response: bool,
    ) -> Tuple[float, str, List[RewardComponent]]:
        """Calculate reward for reply action."""
        components = []
        
        if requires_response:
            # Check reply quality
            content = action.reply_content or ""
            if len(content) > 50:
                reward = self.config["quality_reply"]
                components.append(RewardComponent(
                    name="quality_reply",
                    value=reward,
                    description="Sent quality reply to email needing response"
                ))
                return reward, "Excellent reply sent!", components
            elif len(content) > 10:
                reward = self.config["basic_reply"]
                components.append(RewardComponent(
                    name="basic_reply",
                    value=reward,
                    description="Sent basic reply (could be more detailed)"
                ))
                return reward, "Reply sent, but could be more detailed.", components
            else:
                reward = self.config["basic_reply"] * 0.3
                components.append(RewardComponent(
                    name="minimal_reply",
                    value=reward,
                    description="Reply too short"
                ))
                return reward, "Reply too short.", components
        else:
            penalty = self.config["unnecessary_reply"]
            components.append(RewardComponent(
                name="unnecessary_reply",
                value=penalty,
                description="Email didn't need a reply"
            ))
            return penalty, "This email didn't require a reply.", components
    
    def _reward_forward(
        self,
        action: Action,
    ) -> Tuple[float, str, List[RewardComponent]]:
        """Calculate reward for forward action."""
        components = []
        
        if action.forward_to:
            reward = self.config["forward_correct"]
            components.append(RewardComponent(
                name="forward_correct",
                value=reward,
                description="Email forwarded successfully"
            ))
            return reward, f"Email forwarded to {action.forward_to}.", components
        else:
            penalty = self.config["invalid_action"]
            components.append(RewardComponent(
                name="invalid_forward",
                value=penalty,
                description="Forward without recipient"
            ))
            return penalty, "Forward requires a recipient.", components
    
    def _reward_mark_read(self) -> Tuple[float, str, List[RewardComponent]]:
        """Calculate reward for mark read action."""
        reward = self.config["mark_read"]
        return (
            reward,
            "Marked as read.",
            [RewardComponent(
                name="mark_read",
                value=reward,
                description="Marked email as read"
            )]
        )
    
    def _reward_skip(self) -> Tuple[float, str, List[RewardComponent]]:
        """Calculate reward for skip action."""
        penalty = self.config["skip_penalty"]
        return (
            penalty,
            "Skipped email.",
            [RewardComponent(
                name="skip_penalty",
                value=penalty,
                description="Skipped email without processing"
            )]
        )
    
    def _invalid_action(self) -> Tuple[float, str, List[RewardComponent]]:
        """Penalty for invalid action."""
        penalty = self.config["invalid_action"]
        return (
            penalty,
            "Invalid action.",
            [RewardComponent(
                name="invalid_action",
                value=penalty,
                description="Action type not recognized"
            )]
        )
    
    def calculate_completion_bonus(
        self,
        metrics: Dict,
        task_difficulty: str,
    ) -> Tuple[float, List[RewardComponent]]:
        """
        Calculate bonus rewards for task completion.
        
        Args:
            metrics: Dict with categorization, spam, priority accuracy
            task_difficulty: easy, medium, or hard
            
        Returns:
            Tuple of (bonus_total, components_list)
        """
        components = []
        
        # Task completion bonus
        components.append(RewardComponent(
            name="completion_bonus",
            value=self.config["task_completion_bonus"],
            description="Bonus for completing the task"
        ))
        
        # Perfect categorization bonus
        cat_accuracy = metrics.get("categorization_accuracy", 0)
        if cat_accuracy >= 0.95:
            components.append(RewardComponent(
                name="perfect_categorization",
                value=self.config["perfect_categorization_bonus"],
                description="Perfect categorization accuracy"
            ))
        
        # Perfect spam detection bonus
        spam_accuracy = metrics.get("spam_accuracy", 0)
        if spam_accuracy >= 0.95:
            components.append(RewardComponent(
                name="perfect_spam_detection",
                value=self.config["perfect_spam_detection_bonus"],
                description="Perfect spam detection"
            ))
        
        # Difficulty multiplier
        multiplier = {"easy": 1.0, "medium": 1.2, "hard": 1.5}.get(task_difficulty, 1.0)
        
        total = sum(c.value for c in components) * multiplier
        return total, components
