#!/usr/bin/env python3
"""
Validation script for the Email Triage environment.
"""

import os
import sys
import json
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import ValidationError

from env import (
    EmailTriageEnv,
    Action,
    ActionType,
    EmailCategory,
    EmailPriority,
    Observation,
    Reward,
    EnvironmentState,
    get_all_tasks,
    grade_episode,
)


class ValidationResult:
    """Track validation results."""
    
    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[str] = []
        self.warnings: List[str] = []
    
    def add_pass(self, test: str):
        self.passed.append(test)
        print(f"  [PASS] {test}")
    
    def add_fail(self, test: str, reason: str = ""):
        msg = f"{test}: {reason}" if reason else test
        self.failed.append(msg)
        print(f"  [FAIL] {msg}")
    
    def add_warning(self, msg: str):
        self.warnings.append(msg)
        print(f"  [WARN] {msg}")
    
    def summary(self) -> bool:
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Passed:   {len(self.passed)}")
        print(f"Failed:   {len(self.failed)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.failed:
            print("\nFailures:")
            for f in self.failed:
                print(f"  - {f}")
        
        if self.warnings:
            print("\nWarnings:")
            for w in self.warnings:
                print(f"  - {w}")
        
        print("="*60)
        return len(self.failed) == 0


def validate_models(result: ValidationResult):
    """Validate Pydantic models are properly defined."""
    print("\n[1] Validating Pydantic Models...")
    
    # Test Action model
    try:
        action = Action(
            action_type=ActionType.CATEGORIZE,
            category=EmailCategory.WORK,
            reasoning="Test action"
        )
        result.add_pass("Action model creation")
    except ValidationError as e:
        result.add_fail("Action model creation", str(e))
    
    # Test invalid action
    try:
        action = Action(action_type="invalid")
        result.add_fail("Action validation", "Should reject invalid action_type")
    except (ValidationError, ValueError):
        result.add_pass("Action validation rejects invalid types")
    
    # Test Observation model
    try:
        from env.models import InboxState
        obs = Observation(
            current_email=None,
            inbox_state=InboxState(
                total_emails=5,
                unread_count=3,
                uncategorized_count=5,
                flagged_count=0
            ),
            emails_processed=0,
            emails_remaining=5,
            step_count=0,
            max_steps=20,
            task_description="Test task",
            available_actions=[ActionType.CATEGORIZE]
        )
        result.add_pass("Observation model creation")
    except ValidationError as e:
        result.add_fail("Observation model creation", str(e))
    
    # Test Reward model
    try:
        reward = Reward(
            immediate=0.5,
            cumulative=1.0,
            breakdown={"test": 0.5},
            feedback="Good job"
        )
        result.add_pass("Reward model creation")
    except ValidationError as e:
        result.add_fail("Reward model creation", str(e))


def validate_environment_interface(result: ValidationResult):
    """Validate environment implements OpenEnv interface."""
    print("\n[2] Validating Environment Interface...")
    
    env = EmailTriageEnv(task_id="easy_categorization")
    
    # Test reset()
    try:
        obs = env.reset(seed=42)
        assert isinstance(obs, Observation), "reset() must return Observation"
        result.add_pass("reset() returns Observation")
    except Exception as e:
        result.add_fail("reset() method", str(e))
        return
    
    # Test state()
    try:
        state = env.state()
        assert isinstance(state, EnvironmentState), "state() must return EnvironmentState"
        result.add_pass("state() returns EnvironmentState")
    except Exception as e:
        result.add_fail("state() method", str(e))
    
    # Test step()
    try:
        action = Action(
            action_type=ActionType.CATEGORIZE,
            category=EmailCategory.WORK
        )
        obs, reward, done, info = env.step(action)
        
        assert isinstance(obs, Observation), "step() must return Observation"
        assert isinstance(reward, Reward), "step() must return Reward"
        assert isinstance(done, bool), "step() must return bool for done"
        assert isinstance(info, dict), "step() must return dict for info"
        
        result.add_pass("step() returns (Observation, Reward, bool, dict)")
    except Exception as e:
        result.add_fail("step() method", str(e))
    
    # Test that environment raises error before reset
    env2 = EmailTriageEnv(task_id="easy_categorization")
    try:
        env2.step(action)
        result.add_fail("step() before reset()", "Should raise RuntimeError")
    except RuntimeError:
        result.add_pass("step() raises error before reset()")
    except Exception as e:
        result.add_fail("step() before reset()", f"Wrong exception: {e}")


def validate_tasks(result: ValidationResult):
    """Validate all tasks are properly configured."""
    print("\n[3] Validating Tasks...")
    
    tasks = get_all_tasks()
    
    if len(tasks) < 3:
        result.add_fail("Minimum tasks", f"Need at least 3 tasks, found {len(tasks)}")
    else:
        result.add_pass(f"Found {len(tasks)} tasks")
    
    difficulties = set()
    for task_id, config in tasks.items():
        # Check required fields
        if not config.task_id:
            result.add_fail(f"Task {task_id}", "Missing task_id")
        if not config.name:
            result.add_fail(f"Task {task_id}", "Missing name")
        if not config.description:
            result.add_fail(f"Task {task_id}", "Missing description")
        if config.difficulty not in ["easy", "medium", "hard"]:
            result.add_fail(f"Task {task_id}", f"Invalid difficulty: {config.difficulty}")
        else:
            difficulties.add(config.difficulty)
        
        result.add_pass(f"Task '{task_id}' is valid")
    
    # Check difficulty range
    if difficulties == {"easy", "medium", "hard"}:
        result.add_pass("Tasks cover easy, medium, hard difficulties")
    else:
        result.add_warning(f"Missing difficulties: {{'easy', 'medium', 'hard'} - {difficulties}}")


def validate_graders(result: ValidationResult):
    """Validate graders produce scores in [0, 1] range."""
    print("\n[4] Validating Graders...")
    
    tasks = get_all_tasks()
    
    for task_id in tasks:
        env = EmailTriageEnv(task_id=task_id)
        obs = env.reset(seed=42)
        
        # Take a few random actions
        for _ in range(5):
            if obs.current_email is None:
                break
            action = Action(
                action_type=ActionType.ARCHIVE,
                reasoning="Test"
            )
            obs, _, done, _ = env.step(action)
            if done:
                break
        
        # Grade
        state = env.state()
        grading = grade_episode(task_id, state)
        
        score = grading.get("score", -1)
        if 0.0 <= score <= 1.0:
            result.add_pass(f"Grader {task_id}: score={score:.3f} in valid range")
        else:
            result.add_fail(f"Grader {task_id}", f"Score {score} not in [0, 1]")
        
        # Check grading has required fields
        if "breakdown" not in grading:
            result.add_warning(f"Grader {task_id} missing 'breakdown' field")
        if "passed" not in grading:
            result.add_warning(f"Grader {task_id} missing 'passed' field")


def validate_reward_function(result: ValidationResult):
    """Validate reward function provides meaningful signals."""
    print("\n[5] Validating Reward Function...")
    
    env = EmailTriageEnv(task_id="easy_categorization")
    obs = env.reset(seed=42)
    
    rewards = []
    
    # Test various actions
    test_actions = [
        Action(action_type=ActionType.CATEGORIZE, category=EmailCategory.WORK),
        Action(action_type=ActionType.ARCHIVE),
        Action(action_type=ActionType.CATEGORIZE, category=EmailCategory.SPAM),
        Action(action_type=ActionType.SKIP),
    ]
    
    for action in test_actions:
        if obs.current_email is None:
            break
        obs, reward, done, _ = env.step(action)
        rewards.append(reward.immediate)
        if done:
            break
    
    # Check for variability in rewards
    unique_rewards = set(rewards)
    if len(unique_rewards) > 1:
        result.add_pass(f"Reward function produces variable signals: {rewards}")
    else:
        result.add_warning(f"Reward function may lack variability: {rewards}")
    
    # Check cumulative tracking
    state = env.state()
    if state.cumulative_reward != 0:
        result.add_pass(f"Cumulative reward tracked: {state.cumulative_reward:.3f}")
    else:
        result.add_warning("Cumulative reward is 0 after actions")


def validate_openenv_yaml(result: ValidationResult):
    """Validate openenv.yaml exists and has required fields."""
    print("\n[6] Validating openenv.yaml...")
    
    yaml_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "openenv.yaml"
    )
    
    if not os.path.exists(yaml_path):
        result.add_fail("openenv.yaml", "File not found")
        return
    
    result.add_pass("openenv.yaml exists")
    
    try:
        import yaml
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
        
        required_fields = ["name", "version", "description", "environment", "tasks"]
        for field in required_fields:
            if field in config:
                result.add_pass(f"openenv.yaml has '{field}' field")
            else:
                result.add_fail(f"openenv.yaml", f"Missing '{field}' field")
        
        # Check tasks
        if "tasks" in config and len(config["tasks"]) >= 3:
            result.add_pass(f"openenv.yaml defines {len(config['tasks'])} tasks")
        else:
            result.add_fail("openenv.yaml tasks", "Need at least 3 tasks defined")
            
    except ImportError:
        result.add_warning("PyYAML not installed, skipping YAML content validation")
    except Exception as e:
        result.add_fail("openenv.yaml parsing", str(e))


def main():
    print("="*60)
    print("OpenEnv Validation: Email Triage Environment")
    print("="*60)
    
    result = ValidationResult()
    
    validate_models(result)
    validate_environment_interface(result)
    validate_tasks(result)
    validate_graders(result)
    validate_reward_function(result)
    validate_openenv_yaml(result)
    
    success = result.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
