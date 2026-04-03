"""
Task definitions for the Email Triage environment.
"""

from typing import Dict
from .models import TaskConfig, ActionType
from .email_generator import generate_phishing_email


# =============================================================================
# TASK DEFINITIONS
# =============================================================================

TASKS: Dict[str, TaskConfig] = {
    # -------------------------------------------------------------------------
    # EASY: Simple decision-making with clear success criteria, plus rare edge case
    # -------------------------------------------------------------------------
    "easy_categorization": TaskConfig(
        task_id="easy_categorization",
        name="Email Categorization Basics",
        description="""
TASK: Categorize 5 simple emails into their correct categories.

OBJECTIVE:
You will receive 5 clearly-labeled emails that are easy to classify.
There is no spam in this task - all emails are legitimate.

HIDDEN EDGE CASES:
- 1 email has a sender name that looks like a business but is actually personal.

ADVERSARIAL/AMBIGUOUS:
- 1 email has a subject that could fit two categories.

TEST CASES:
- Email 1: Obvious work
- Email 2: Obvious personal
- Email 3: Obvious newsletter
- Email 4: Personal from a business domain (edge)
- Email 5: Newsletter with ambiguous subject (ambiguous)

AVAILABLE CATEGORIES:
- work: Work-related emails from colleagues or business contacts
- personal: Personal communications from friends and family
- newsletter: Newsletters, digests, and subscription content

REQUIRED ACTIONS:
For each email:
1. Read the email content carefully
2. Use CATEGORIZE action with the appropriate category
3. Use ARCHIVE to move to the next email

SUCCESS CRITERIA:
- Correctly categorize at least 4 out of 5 emails (80%)
- Complete all 5 emails within 20 steps

SCORING:
- Categorization accuracy: 80% weight
- Completion rate: 20% weight
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
        success_threshold=0.70,
        grading_weights={
            "categorization": 0.80,
            "completion": 0.20,
        },
    ),
    # -------------------------------------------------------------------------
    # MEDIUM: Multi-step reasoning, partial credit, adversarial/ambiguous, edge cases
    # -------------------------------------------------------------------------
    "medium_triage": TaskConfig(
        task_id="medium_triage",
        name="Email Triage with Spam Detection",
        description="""
TASK: Triage 10 emails including spam detection and priority setting.

OBJECTIVE:
You will receive 10 emails, some of which are spam (~20%).
You must categorize, prioritize, and handle each appropriately.

HIDDEN EDGE CASES:
- 1 spam email is disguised as a support request.
- 1 legitimate email has a subject similar to common spam.

ADVERSARIAL/AMBIGUOUS:
- 1 email is ambiguous between "work" and "support".
- 1 email is a newsletter with a high-urgency subject.

TEST CASES:
- Email 1: Obvious work
- Email 2: Obvious personal
- Email 3: Obvious spam
- Email 4: Spam disguised as support (edge)
- Email 5: Legitimate with spammy subject (edge)
- Email 6: Ambiguous work/support (ambiguous)
- Email 7: Newsletter, urgent subject (ambiguous)
- Email 8-10: Mix of standard cases

AVAILABLE CATEGORIES:
- work, personal, spam, newsletter, support, billing

PRIORITIES:
- urgent: Requires immediate attention
- high: Important, handle soon
- normal: Standard priority
- low: Can wait

REQUIRED ACTIONS:
1. Identify and DELETE spam emails
2. CATEGORIZE legitimate emails
3. SET_PRIORITY for each email
4. FLAG urgent emails for follow-up
5. ARCHIVE completed emails

SUCCESS CRITERIA:
- Catch at least 80% of spam (delete them)
- Correctly categorize 70% of emails
- Set appropriate priorities
- Flag all truly urgent emails

SCORING:
- Categorization accuracy: 30% weight
- Spam detection: 25% weight
- Priority accuracy: 25% weight
- Completion rate: 20% weight
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
        grading_weights={
            "categorization": 0.30,
            "spam": 0.25,
            "priority": 0.25,
            "completion": 0.20,
        },
    ),
    # -------------------------------------------------------------------------
    # HARD: Real-world complexity, adversarial, ambiguous, rare edge cases
    # -------------------------------------------------------------------------
    "hard_inbox_zero": TaskConfig(
        task_id="hard_inbox_zero",
        name="Inbox Zero Challenge",
        description="""
TASK: Achieve inbox zero by efficiently processing 20 emails.

OBJECTIVE:
This is a challenging, real-world email triage scenario.
You will receive 20 emails with a mix of:
- Work emails (some urgent, some requiring responses)
- Personal emails
- Spam (~25% of inbox)
- Newsletters
- Support and billing emails

HIDDEN EDGE CASES:
- 2 spam emails are highly convincing (from known contacts, realistic content).
- 1 urgent work email is missing the "urgent" keyword.
- 1 billing email requests a reply but is actually spam.

ADVERSARIAL/AMBIGUOUS:
- 2 emails have ambiguous categories (work/personal, support/billing).
- 1 email is a newsletter with a fake urgent request.
- 1 email is a support request with conflicting objectives (urgent but low priority).

TEST CASES:
- Email 1: Obvious work
- Email 2: Obvious personal
- Email 3: Obvious spam
- Email 4: Convincing spam (edge)
- Email 5: Convincing spam (edge)
- Email 6: Urgent work, no "urgent" keyword (edge)
- Email 7: Billing requests reply but is spam (edge)
- Email 8: Ambiguous work/personal (ambiguous)
- Email 9: Ambiguous support/billing (ambiguous)
- Email 10: Newsletter, fake urgent (ambiguous)
- Email 11: Support, urgent but low priority (ambiguous)
- Email 12-20: Mix of standard and tricky cases

COMPLEXITY:
- Some emails are ambiguous and require careful reading
- Multiple urgent items need prioritization decisions
- Time pressure: limited steps means you must work efficiently
- Trade-offs: spending time on detailed replies vs. processing more emails

REQUIRED ACTIONS:
1. DELETE all spam (identify carefully - some are tricky)
2. CATEGORIZE all emails correctly
3. SET_PRIORITY for all emails
4. REPLY to emails that explicitly request a response
   - Replies must be substantive (>50 chars for full credit)
5. FLAG all urgent items
6. ARCHIVE all remaining emails

SUCCESS CRITERIA:
- Process all 20 emails
- 90%+ spam detection accuracy
- 80%+ categorization accuracy
- All urgent emails flagged or replied to
- Meaningful replies to emails needing responses

EFFICIENCY:
You have only 80 steps for 20 emails. Plan your actions carefully.
Typical efficient processing: 3-4 actions per email.

SCORING:
- Categorization accuracy: 25% weight
- Spam detection: 20% weight
- Priority accuracy: 20% weight
- Urgent handling: 20% weight
- Full completion bonus: 15% weight
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
        grading_weights={
            "categorization": 0.25,
            "spam": 0.20,
            "priority": 0.20,
            "urgent": 0.20,
            "completion": 0.15,
        },
    ),
    # -------------------------------------------------------------------------
    # PHISHING DETECTION TASK (for new feature demonstration)
    # -------------------------------------------------------------------------
    "phishing_detection": TaskConfig(
        task_id="phishing_detection",
        name="Phishing Detection Challenge",
        description="""
TASK: Identify and report phishing emails in a batch of 8 emails.

OBJECTIVE:
You will receive 8 emails, including 2 highly realistic phishing attempts.
Your goal is to correctly report phishing emails using the REPORT_PHISHING action, while avoiding false positives.

HIDDEN EDGE CASES:
- 1 phishing email mimics a real sender from your company.
- 1 legitimate email has a suspicious subject but is not phishing.

REQUIRED ACTIONS:
1. Use REPORT_PHISHING for phishing emails
2. CATEGORIZE and ARCHIVE legitimate emails

SUCCESS CRITERIA:
- Correctly report both phishing emails
- No more than 1 false positive
- Process all emails within 20 steps

SCORING:
- Phishing detection: 60% weight
- False positive avoidance: 20% weight
- Completion rate: 20% weight
        """,
        difficulty="hard",
        num_emails=8,
        max_steps=20,
        required_actions=[
            ActionType.REPORT_PHISHING,
            ActionType.CATEGORIZE,
            ActionType.ARCHIVE,
        ],
        success_threshold=0.75,
        grading_weights={
            "phishing": 0.60,
            "false_positive": 0.20,
            "completion": 0.20,
        },
    ),
    "easy_categorization": TaskConfig(
        task_id="easy_categorization",
        name="Email Categorization Basics",
        description="""
TASK: Categorize 5 simple emails into their correct categories.

OBJECTIVE:
You will receive 5 clearly-labeled emails that are easy to classify.
There is no spam in this task - all emails are legitimate.

HIDDEN EDGE CASES:
- 1 email has a sender name that looks like a business but is actually personal.

ADVERSARIAL/AMBIGUOUS:
- 1 email has a subject that could fit two categories.

TEST CASES:
- Email 1: Obvious work
- Email 2: Obvious personal
- Email 3: Obvious newsletter
- Email 4: Personal from a business domain (edge)
- Email 5: Newsletter with ambiguous subject (ambiguous)

AVAILABLE CATEGORIES:
- work: Work-related emails from colleagues or business contacts
- personal: Personal communications from friends and family
- newsletter: Newsletters, digests, and subscription content

REQUIRED ACTIONS:
For each email:
1. Read the email content carefully
2. Use CATEGORIZE action with the appropriate category
3. Use ARCHIVE to move to the next email

SUCCESS CRITERIA:
- Correctly categorize at least 4 out of 5 emails (80%)
- Complete all 5 emails within 20 steps

SCORING:
- Categorization accuracy: 80% weight
- Completion rate: 20% weight
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
        success_threshold=0.70,
        grading_weights={
            "categorization": 0.80,
            "completion": 0.20,
        },
    ),
    # -------------------------------------------------------------------------
    # MEDIUM: Multi-step reasoning, partial credit, adversarial/ambiguous, edge cases
    # -------------------------------------------------------------------------
    "medium_triage": TaskConfig(
        task_id="medium_triage",
        name="Email Triage with Spam Detection",
        description="""
TASK: Triage 10 emails including spam detection and priority setting.

OBJECTIVE:
You will receive 10 emails, some of which are spam (~20%).
You must categorize, prioritize, and handle each appropriately.

HIDDEN EDGE CASES:
- 1 spam email is disguised as a support request.
- 1 legitimate email has a subject similar to common spam.

ADVERSARIAL/AMBIGUOUS:
- 1 email is ambiguous between "work" and "support".
- 1 email is a newsletter with a high-urgency subject.

TEST CASES:
- Email 1: Obvious work
- Email 2: Obvious personal
- Email 3: Obvious spam
- Email 4: Spam disguised as support (edge)
- Email 5: Legitimate with spammy subject (edge)
- Email 6: Ambiguous work/support (ambiguous)
- Email 7: Newsletter, urgent subject (ambiguous)
- Email 8-10: Mix of standard cases

AVAILABLE CATEGORIES:
- work, personal, spam, newsletter, support, billing

PRIORITIES:
- urgent: Requires immediate attention
- high: Important, handle soon
- normal: Standard priority
- low: Can wait

REQUIRED ACTIONS:
1. Identify and DELETE spam emails
2. CATEGORIZE legitimate emails
3. SET_PRIORITY for each email
4. FLAG urgent emails for follow-up
5. ARCHIVE completed emails

SUCCESS CRITERIA:
- Catch at least 80% of spam (delete them)
- Correctly categorize 70% of emails
- Set appropriate priorities
- Flag all truly urgent emails

SCORING:
- Categorization accuracy: 30% weight
- Spam detection: 25% weight
- Priority accuracy: 25% weight
- Completion rate: 20% weight
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
        grading_weights={
            "categorization": 0.30,
            "spam": 0.25,
            "priority": 0.25,
            "completion": 0.20,
        },
    ),
    # -------------------------------------------------------------------------
    # HARD: Real-world complexity, adversarial, ambiguous, rare edge cases
    # -------------------------------------------------------------------------
    "hard_inbox_zero": TaskConfig(
        task_id="hard_inbox_zero",
        name="Inbox Zero Challenge",
        description="""
TASK: Achieve inbox zero by efficiently processing 20 emails.

OBJECTIVE:
This is a challenging, real-world email triage scenario.
You will receive 20 emails with a mix of:
- Work emails (some urgent, some requiring responses)
- Personal emails
- Spam (~25% of inbox)
- Newsletters
- Support and billing emails

HIDDEN EDGE CASES:
- 2 spam emails are highly convincing (from known contacts, realistic content).
- 1 urgent work email is missing the "urgent" keyword.
- 1 billing email requests a reply but is actually spam.

ADVERSARIAL/AMBIGUOUS:
- 2 emails have ambiguous categories (work/personal, support/billing).
- 1 email is a newsletter with a fake urgent request.
- 1 email is a support request with conflicting objectives (urgent but low priority).

TEST CASES:
- Email 1: Obvious work
- Email 2: Obvious personal
- Email 3: Obvious spam
- Email 4: Convincing spam (edge)
- Email 5: Convincing spam (edge)
- Email 6: Urgent work, no "urgent" keyword (edge)
- Email 7: Billing requests reply but is spam (edge)
- Email 8: Ambiguous work/personal (ambiguous)
- Email 9: Ambiguous support/billing (ambiguous)
- Email 10: Newsletter, fake urgent (ambiguous)
- Email 11: Support, urgent but low priority (ambiguous)
- Email 12-20: Mix of standard and tricky cases

COMPLEXITY:
- Some emails are ambiguous and require careful reading
- Multiple urgent items need prioritization decisions
- Time pressure: limited steps means you must work efficiently
- Trade-offs: spending time on detailed replies vs. processing more emails

REQUIRED ACTIONS:
1. DELETE all spam (identify carefully - some are tricky)
2. CATEGORIZE all emails correctly
3. SET_PRIORITY for all emails
4. REPLY to emails that explicitly request a response
   - Replies must be substantive (>50 chars for full credit)
5. FLAG all urgent items
6. ARCHIVE all remaining emails

SUCCESS CRITERIA:
- Process all 20 emails
- 90%+ spam detection accuracy
- 80%+ categorization accuracy
- All urgent emails flagged or replied to
- Meaningful replies to emails needing responses

EFFICIENCY:
You have only 80 steps for 20 emails. Plan your actions carefully.
Typical efficient processing: 3-4 actions per email.

SCORING:
- Categorization accuracy: 25% weight
- Spam detection: 20% weight
- Priority accuracy: 20% weight
- Urgent handling: 20% weight
- Full completion bonus: 15% weight
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
        grading_weights={
            "categorization": 0.25,
            "spam": 0.20,
            "priority": 0.20,
            "urgent": 0.20,
            "completion": 0.15,
        },
    ),
}


# =============================================================================
# TASK UTILITY FUNCTIONS
# =============================================================================

def get_task_config(task_id: str) -> TaskConfig:
    """
    Get configuration for a specific task.
    
    Args:
        task_id: One of "easy_categorization", "medium_triage", "hard_inbox_zero"
        
    Returns:
        TaskConfig object with all task parameters
        
    Raises:
        ValueError: If task_id is not recognized
    """
    if task_id not in TASKS:
        available = ", ".join(TASKS.keys())
        raise ValueError(f"Unknown task: {task_id}. Available tasks: {available}")
    return TASKS[task_id]


def get_all_tasks() -> Dict[str, TaskConfig]:
    """Get all available task configurations."""
    return TASKS.copy()


def list_tasks() -> list:
    """List all available task IDs."""
    return list(TASKS.keys())


# =============================================================================
# PROGRAMMATIC GRADERS
# =============================================================================

class TaskGrader:
    """
    Programmatic grader for evaluating agent performance on tasks.
    
    Produces deterministic scores from 0.0 to 1.0 based on clear criteria.
    Each task has specific grading weights defined in its configuration.
    """
    
    def __init__(self, task_id: str):
        """
        Initialize grader for a specific task.
        
        Args:
            task_id: The task to grade
        """
        self.task_config = get_task_config(task_id)
        self.task_id = task_id
    
    def grade(self, env_state) -> Dict:
        """
        Grade the agent's performance on the task.
        
        Args:
            env_state: The final EnvironmentState from the episode
            
        Returns:
            Dict containing:
                - score: Float from 0.0 to 1.0
                - passed: Boolean indicating if success threshold met
                - breakdown: Dict of individual scoring components
                - metrics: Dict of raw performance metrics
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
        Grade the EASY categorization task.
        
        Criteria:
        - 80% weight: Categorization accuracy
        - 20% weight: Completion rate
        """
        # Calculate categorization accuracy
        total_cat = state.correct_categorizations + state.incorrect_categorizations
        cat_accuracy = state.correct_categorizations / max(1, total_cat)
        
        # Calculate completion rate
        total_emails = len(state.emails)
        completion = state.current_email_index / max(1, total_emails)
        
        # Weighted score
        score = (cat_accuracy * 0.80) + (completion * 0.20)
        
        return {
            "score": round(score, 4),
            "passed": score >= self.task_config.success_threshold,
            "threshold": self.task_config.success_threshold,
            "breakdown": {
                "categorization_accuracy": round(cat_accuracy, 4),
                "completion_rate": round(completion, 4),
            },
            "weights": {
                "categorization": 0.80,
                "completion": 0.20,
            },
            "metrics": {
                "correct_categorizations": state.correct_categorizations,
                "incorrect_categorizations": state.incorrect_categorizations,
                "emails_processed": state.current_email_index,
                "total_emails": total_emails,
                "steps_used": state.step_count,
                "max_steps": state.max_steps,
            },
        }
    
    def _grade_medium(self, state) -> Dict:
        """
        Grade the MEDIUM triage task.
        
        Criteria:
        - 30% weight: Categorization accuracy
        - 25% weight: Spam detection
        - 25% weight: Priority accuracy
        - 20% weight: Completion rate
        """
        # Categorization accuracy
        total_cat = state.correct_categorizations + state.incorrect_categorizations
        cat_accuracy = state.correct_categorizations / max(1, total_cat)
        
        # Spam detection accuracy
        total_spam = state.spam_caught + state.spam_missed
        spam_accuracy = state.spam_caught / max(1, total_spam) if total_spam > 0 else 1.0
        
        # Priority accuracy
        total_priority = state.correct_priorities + state.incorrect_priorities
        priority_accuracy = state.correct_priorities / max(1, total_priority)
        
        # Completion rate
        total_emails = len(state.emails)
        completion = state.current_email_index / max(1, total_emails)
        
        # Weighted score
        score = (
            (cat_accuracy * 0.30) +
            (spam_accuracy * 0.25) +
            (priority_accuracy * 0.25) +
            (completion * 0.20)
        )
        
        return {
            "score": round(score, 4),
            "passed": score >= self.task_config.success_threshold,
            "threshold": self.task_config.success_threshold,
            "breakdown": {
                "categorization_accuracy": round(cat_accuracy, 4),
                "spam_detection": round(spam_accuracy, 4),
                "priority_accuracy": round(priority_accuracy, 4),
                "completion_rate": round(completion, 4),
            },
            "weights": {
                "categorization": 0.30,
                "spam": 0.25,
                "priority": 0.25,
                "completion": 0.20,
            },
            "metrics": {
                "correct_categorizations": state.correct_categorizations,
                "incorrect_categorizations": state.incorrect_categorizations,
                "spam_caught": state.spam_caught,
                "spam_missed": state.spam_missed,
                "correct_priorities": state.correct_priorities,
                "incorrect_priorities": state.incorrect_priorities,
                "emails_processed": state.current_email_index,
                "total_emails": total_emails,
                "steps_used": state.step_count,
                "max_steps": state.max_steps,
            },
        }
    
    def _grade_hard(self, state) -> Dict:
        """
        Grade the HARD inbox zero task.
        
        Criteria:
        - 25% weight: Categorization accuracy
        - 20% weight: Spam detection
        - 20% weight: Priority accuracy
        - 20% weight: Urgent handling
        - 15% weight: Full completion bonus
        """
        total_emails = len(state.emails)
        
        # Categorization accuracy
        total_cat = state.correct_categorizations + state.incorrect_categorizations
        cat_accuracy = state.correct_categorizations / max(1, total_cat)
        
        # Spam detection accuracy
        total_spam = state.spam_caught + state.spam_missed
        spam_accuracy = state.spam_caught / max(1, total_spam) if total_spam > 0 else 1.0
        
        # Priority accuracy
        total_priority = state.correct_priorities + state.incorrect_priorities
        priority_accuracy = state.correct_priorities / max(1, total_priority)
        
        # Urgent handling accuracy
        total_urgent = state.urgent_handled + state.urgent_missed
        urgent_accuracy = state.urgent_handled / max(1, total_urgent) if total_urgent > 0 else 1.0
        
        # Full completion bonus - binary: full credit only if ALL emails processed
        full_completion = 1.0 if state.current_email_index >= total_emails else 0.0
        
        # Weighted score
        score = (
            (cat_accuracy * 0.25) +
            (spam_accuracy * 0.20) +
            (priority_accuracy * 0.20) +
            (urgent_accuracy * 0.20) +
            (full_completion * 0.15)
        )
        
        return {
            "score": round(score, 4),
            "passed": score >= self.task_config.success_threshold,
            "threshold": self.task_config.success_threshold,
            "breakdown": {
                "categorization_accuracy": round(cat_accuracy, 4),
                "spam_detection": round(spam_accuracy, 4),
                "priority_accuracy": round(priority_accuracy, 4),
                "urgent_handling": round(urgent_accuracy, 4),
                "completion_bonus": round(full_completion, 4),
            },
            "weights": {
                "categorization": 0.25,
                "spam": 0.20,
                "priority": 0.20,
                "urgent": 0.20,
                "completion": 0.15,
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
                "replies_sent": state.replies_sent,
                "quality_replies": state.quality_replies,
                "emails_processed": state.current_email_index,
                "total_emails": total_emails,
                "steps_used": state.step_count,
                "max_steps": state.max_steps,
            },
        }
    
    def _grade_default(self, state) -> Dict:
        """Default grading fallback for unknown tasks."""
        total_emails = len(state.emails)
        completion = state.current_email_index / max(1, total_emails)
        normalized_reward = max(0, min(1, (state.cumulative_reward + 5) / 10))
        
        score = (completion * 0.5) + (normalized_reward * 0.5)
        
        return {
            "score": round(score, 4),
            "passed": score >= 0.5,
            "threshold": 0.5,
            "breakdown": {
                "completion": round(completion, 4),
                "normalized_reward": round(normalized_reward, 4),
            },
            "metrics": {
                "cumulative_reward": state.cumulative_reward,
                "emails_processed": state.current_email_index,
                "total_emails": total_emails,
            },
        }


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def grade_episode(task_id: str, env_state) -> Dict:
    """
    Convenience function to grade an episode.
    
    Args:
        task_id: ID of the task that was run
        env_state: Final EnvironmentState from the episode
        
    Returns:
        Grading result dict with score, passed, breakdown, and metrics
        
    Example:
        >>> result = grade_episode("easy_categorization", env.state())
        >>> print(f"Score: {result['score']:.2f}")
        >>> print(f"Passed: {result['passed']}")
    """
    grader = TaskGrader(task_id)
    return grader.grade(env_state)
