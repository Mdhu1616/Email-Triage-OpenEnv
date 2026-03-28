"""
Task definitions and graders for the Email Triage environment.
Defines 3 tasks: easy, medium, and hard with programmatic graders.
"""

from typing import Dict, Callable
from .models import TaskConfig, ActionType, EmailCategory


# Task configurations
TASKS: Dict[str, TaskConfig] = {
    "easy_categorization": TaskConfig(
        task_id="easy_categorization",
        name="Email Categorization Basics",
        description="""
        Task: Categorize 5 simple emails into their correct categories.
        
        You will receive 5 clearly-labeled emails that are easy to classify.
        Categories: work, personal, newsletter
        
        For each email:
        1. Read the email content
        2. Use CATEGORIZE action with the appropriate category
        3. Use ARCHIVE to move to the next email
        
        Success criteria: Correctly categorize at least 4 out of 5 emails.
        """,
        difficulty="easy",
        num_emails=5,
        max_steps=20,
        required_actions=[
            ActionType.CATEGORIZE,
            ActionType.ARCHIVE,
            ActionType.MARK_READ,
            ActionType.SKIP,
        ],
        success_threshold=0.7,
    ),
    
    "medium_triage": TaskConfig(
        task_id="medium_triage",
        name="Email Triage with Spam Detection",
        description="""
        Task: Triage 10 emails including spam detection and priority setting.
        
        You will receive 10 emails, some of which are spam (about 20%).
        You must:
        1. Identify and DELETE spam emails
        2. Categorize legitimate emails
        3. Set appropriate priorities (urgent, high, normal, low)
        4. FLAG urgent emails for follow-up
        
        Categories: work, personal, spam, newsletter, support, billing
        Priorities: urgent, high, normal, low
        
        Success criteria:
        - Catch at least 80% of spam
        - Correctly categorize 70% of emails
        - Flag all urgent emails
        """,
        difficulty="medium",
        num_emails=10,
        max_steps=50,
        required_actions=[
            ActionType.CATEGORIZE,
            ActionType.SET_PRIORITY,
            ActionType.ARCHIVE,
            ActionType.DELETE,
            ActionType.FLAG,
            ActionType.MARK_READ,
            ActionType.SKIP,
        ],
        success_threshold=0.65,
    ),
    
    "hard_inbox_zero": TaskConfig(
        task_id="hard_inbox_zero",
        name="Inbox Zero Challenge",
        description="""
        Task: Achieve inbox zero by processing 20 emails efficiently.
        
        You will receive 20 emails with a mix of:
        - Work emails (some urgent, requiring responses)
        - Personal emails
        - Spam (about 25%)
        - Newsletters
        - Support and billing emails
        
        You must:
        1. DELETE all spam
        2. Categorize all emails correctly
        3. Set priorities for all emails
        4. REPLY to emails that require a response
        5. FLAG urgent items
        6. ARCHIVE or handle all remaining emails
        
        You have limited steps, so work efficiently!
        
        Success criteria:
        - Process all 20 emails
        - 90%+ spam detection
        - 80%+ categorization accuracy
        - All urgent emails flagged or replied to
        - Replies must be substantive (>10 characters)
        """,
        difficulty="hard",
        num_emails=20,
        max_steps=80,
        required_actions=[
            ActionType.CATEGORIZE,
            ActionType.SET_PRIORITY,
            ActionType.ARCHIVE,
            ActionType.DELETE,
            ActionType.REPLY,
            ActionType.FORWARD,
            ActionType.FLAG,
            ActionType.MARK_READ,
            ActionType.SKIP,
        ],
        success_threshold=0.75,
    ),
}


def get_task_config(task_id: str) -> TaskConfig:
    """Get configuration for a specific task."""
    if task_id not in TASKS:
        available = ", ".join(TASKS.keys())
        raise ValueError(f"Unknown task: {task_id}. Available tasks: {available}")
    return TASKS[task_id]


def get_all_tasks() -> Dict[str, TaskConfig]:
    """Get all available task configurations."""
    return TASKS.copy()


class TaskGrader:
    """
    Programmatic grader for evaluating agent performance on tasks.
    Produces scores from 0.0 to 1.0 based on clear, deterministic criteria.
    """
    
    def __init__(self, task_id: str):
        self.task_config = get_task_config(task_id)
        self.task_id = task_id
    
    def grade(self, env_state) -> Dict:
        """
        Grade the agent's performance on the task.
        
        Args:
            env_state: The final EnvironmentState from the episode
            
        Returns:
            Dict with score (0.0-1.0) and detailed breakdown
        """
        if self.task_id == "easy_categorization":
            return self._grade_easy(env_state)
        elif self.task_id == "medium_triage":
            return self._grade_medium(env_state)
        elif self.task_id == "hard_inbox_zero":
            return self._grade_hard(env_state)
        else:
            return self._grade_default(env_state)
    
    def _grade_easy(self, state) -> Dict:
        """
        Grade the easy categorization task.
        
        Criteria:
        - 80% weight: Categorization accuracy
        - 20% weight: Completion rate
        """
        total_cat = state.correct_categorizations + state.incorrect_categorizations
        cat_accuracy = state.correct_categorizations / max(1, total_cat)
        
        completion = state.current_email_index / len(state.emails)
        
        score = (cat_accuracy * 0.8) + (completion * 0.2)
        
        return {
            "score": round(score, 3),
            "passed": score >= self.task_config.success_threshold,
            "breakdown": {
                "categorization_accuracy": round(cat_accuracy, 3),
                "completion_rate": round(completion, 3),
            },
            "metrics": {
                "correct_categorizations": state.correct_categorizations,
                "incorrect_categorizations": state.incorrect_categorizations,
                "emails_processed": state.current_email_index,
                "total_emails": len(state.emails),
                "steps_used": state.step_count,
                "max_steps": state.max_steps,
            },
        }
    
    def _grade_medium(self, state) -> Dict:
        """
        Grade the medium triage task.
        
        Criteria:
        - 30% weight: Categorization accuracy
        - 25% weight: Spam detection
        - 25% weight: Priority accuracy
        - 20% weight: Completion rate
        """
        total_cat = state.correct_categorizations + state.incorrect_categorizations
        cat_accuracy = state.correct_categorizations / max(1, total_cat)
        
        total_spam = state.spam_caught + state.spam_missed
        spam_accuracy = state.spam_caught / max(1, total_spam)
        
        total_priority = state.correct_priorities + state.incorrect_priorities
        priority_accuracy = state.correct_priorities / max(1, total_priority)
        
        completion = state.current_email_index / len(state.emails)
        
        score = (
            (cat_accuracy * 0.30) +
            (spam_accuracy * 0.25) +
            (priority_accuracy * 0.25) +
            (completion * 0.20)
        )
        
        return {
            "score": round(score, 3),
            "passed": score >= self.task_config.success_threshold,
            "breakdown": {
                "categorization_accuracy": round(cat_accuracy, 3),
                "spam_detection": round(spam_accuracy, 3),
                "priority_accuracy": round(priority_accuracy, 3),
                "completion_rate": round(completion, 3),
            },
            "metrics": {
                "correct_categorizations": state.correct_categorizations,
                "incorrect_categorizations": state.incorrect_categorizations,
                "spam_caught": state.spam_caught,
                "spam_missed": state.spam_missed,
                "correct_priorities": state.correct_priorities,
                "incorrect_priorities": state.incorrect_priorities,
                "emails_processed": state.current_email_index,
                "total_emails": len(state.emails),
                "steps_used": state.step_count,
                "max_steps": state.max_steps,
            },
        }
    
    def _grade_hard(self, state) -> Dict:
        """
        Grade the hard inbox zero task.
        
        Criteria:
        - 25% weight: Categorization accuracy
        - 20% weight: Spam detection
        - 20% weight: Priority accuracy
        - 20% weight: Urgent handling
        - 15% weight: Full completion (all emails processed)
        """
        total_cat = state.correct_categorizations + state.incorrect_categorizations
        cat_accuracy = state.correct_categorizations / max(1, total_cat)
        
        total_spam = state.spam_caught + state.spam_missed
        spam_accuracy = state.spam_caught / max(1, total_spam)
        
        total_priority = state.correct_priorities + state.incorrect_priorities
        priority_accuracy = state.correct_priorities / max(1, total_priority)
        
        total_urgent = state.urgent_handled + state.urgent_missed
        urgent_accuracy = state.urgent_handled / max(1, total_urgent)
        
        # Full completion bonus - only full credit if ALL emails processed
        full_completion = 1.0 if state.current_email_index >= len(state.emails) else 0.5
        
        score = (
            (cat_accuracy * 0.25) +
            (spam_accuracy * 0.20) +
            (priority_accuracy * 0.20) +
            (urgent_accuracy * 0.20) +
            (full_completion * 0.15)
        )
        
        return {
            "score": round(score, 3),
            "passed": score >= self.task_config.success_threshold,
            "breakdown": {
                "categorization_accuracy": round(cat_accuracy, 3),
                "spam_detection": round(spam_accuracy, 3),
                "priority_accuracy": round(priority_accuracy, 3),
                "urgent_handling": round(urgent_accuracy, 3),
                "completion_bonus": round(full_completion, 3),
            },
            "metrics": {
                "correct_categorizations": state.correct_categorizations,
                "incorrect_categorizations": state.incorrect_categorizations,
                "spam_caught": state.spam_caught,
                "spam_missed": state.spam_missed,
                "correct_priorities": state.correct_priorities,
                "incorrect_priorities": state.incorrect_priorities,
                "urgent_handled": state.urgent_handled,
                "urgent_missed": state.urgent_missed,
                "emails_processed": state.current_email_index,
                "total_emails": len(state.emails),
                "steps_used": state.step_count,
                "max_steps": state.max_steps,
            },
        }
    
    def _grade_default(self, state) -> Dict:
        """Default grading for unknown tasks."""
        completion = state.current_email_index / max(1, len(state.emails))
        normalized_reward = max(0, min(1, (state.cumulative_reward + 5) / 10))
        
        score = (completion * 0.5) + (normalized_reward * 0.5)
        
        return {
            "score": round(score, 3),
            "passed": score >= 0.5,
            "breakdown": {
                "completion": round(completion, 3),
                "normalized_reward": round(normalized_reward, 3),
            },
            "metrics": {
                "cumulative_reward": state.cumulative_reward,
                "emails_processed": state.current_email_index,
                "total_emails": len(state.emails),
            },
        }


def grade_episode(task_id: str, env_state) -> Dict:
    """
    Convenience function to grade an episode.
    
    Args:
        task_id: ID of the task that was run
        env_state: Final EnvironmentState from the episode
        
    Returns:
        Grading result dict with score and breakdown
    """
    grader = TaskGrader(task_id)
    return grader.grade(env_state)
