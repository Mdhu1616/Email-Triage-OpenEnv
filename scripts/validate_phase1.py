#!/usr/bin/env python3
"""
Comprehensive validation script for Email Triage OpenEnv.
Runs all Phase 1 automated validation checks.
"""

import os
import sys
import json
import subprocess
from typing import Dict, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env import EmailTriageEnv, get_all_tasks, grade_episode


class ValidationResult:
    """Track validation results."""

    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[str] = []
        self.warnings: List[str] = []

    def add_pass(self, test: str):
        self.passed.append(test)
        print(f"  ✅ {test}")

    def add_fail(self, test: str, reason: str = ""):
        msg = f"{test}: {reason}" if reason else test
        self.failed.append(msg)
        print(f"  ❌ {msg}")

    def add_warning(self, msg: str):
        self.warnings.append(msg)
        print(f"  ⚠️  {msg}")

    def summary(self) -> Dict:
        return {
            "passed": len(self.passed),
            "failed": len(self.failed),
            "warnings": len(self.warnings),
            "total": len(self.passed) + len(self.failed),
            "success_rate": (len(self.passed) / (len(self.passed) + len(self.failed))) if (len(self.passed) + len(self.failed)) > 0 else 0,
        }


def check_openenv_compliance(result: ValidationResult):
    """Check OpenEnv specification compliance."""
    try:
        from env import EmailTriageEnv

        # Check required interface methods
        env = EmailTriageEnv("easy_categorization")
        required_methods = ["reset", "step", "state"]

        for method in required_methods:
            if not hasattr(env, method):
                result.add_fail(f"OpenEnv compliance - missing method: {method}")
                return

        # Test basic interface
        obs = env.reset(seed=42)
        action = env.models.Action(action_type=env.models.ActionType.SKIP)
        obs, reward, done, info = env.step(action)
        state = env.state()

        if not isinstance(obs, dict) or "current_email" not in obs:
            result.add_fail("OpenEnv compliance - invalid observation format")
            return

        if not hasattr(reward, "immediate") or not hasattr(reward, "cumulative"):
            result.add_fail("OpenEnv compliance - invalid reward format")
            return

        if not isinstance(state, dict):
            result.add_fail("OpenEnv compliance - invalid state format")
            return

        result.add_pass("OpenEnv compliance - interface methods and formats")

    except Exception as e:
        result.add_fail(f"OpenEnv compliance - exception: {e}")


def check_dockerfile(result: ValidationResult):
    """Check Dockerfile exists and is valid."""
    dockerfile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Dockerfile")

    if not os.path.exists(dockerfile_path):
        result.add_fail("Dockerfile - file not found")
        return

    try:
        with open(dockerfile_path, 'r') as f:
            content = f.read()

        # Check for required elements
        required_lines = [
            "FROM python",
            "WORKDIR /app",
            "COPY requirements.txt",
            "RUN pip install",
            "EXPOSE 7860",
            "CMD"
        ]

        missing = []
        for line in required_lines:
            if line not in content:
                missing.append(line)

        if missing:
            result.add_fail(f"Dockerfile - missing required elements: {', '.join(missing)}")
        else:
            result.add_pass("Dockerfile - contains required elements")

    except Exception as e:
        result.add_fail(f"Dockerfile - error reading file: {e}")


def check_baseline_reproduction(result: ValidationResult):
    """Check baseline can be reproduced."""
    try:
        # Run baseline script with dry-run (no API calls)
        baseline_script = os.path.join(os.path.dirname(__file__), "run_baseline.py")

        if not os.path.exists(baseline_script):
            result.add_fail("Baseline reproduction - script not found")
            return

        # Test import and basic functionality
        sys.path.insert(0, os.path.dirname(__file__))
        import run_baseline

        # Check if required functions exist
        if not hasattr(run_baseline, 'create_system_prompt'):
            result.add_fail("Baseline reproduction - missing create_system_prompt function")
            return

        if not hasattr(run_baseline, 'run_episode'):
            result.add_fail("Baseline reproduction - missing run_episode function")
            return

        result.add_pass("Baseline reproduction - script structure valid")

    except Exception as e:
        result.add_fail(f"Baseline reproduction - import error: {e}")


def check_tasks_and_graders(result: ValidationResult):
    """Check tasks and graders are properly implemented."""
    try:
        tasks = get_all_tasks()

        if len(tasks) < 3:
            result.add_fail(f"Tasks and graders - only {len(tasks)} tasks found, need at least 3")
            return

        # Test each task
        for task_id, task_config in tasks.items():
            try:
                env = EmailTriageEnv(task_id)
                obs = env.reset(seed=42)

                # Run a few steps
                for _ in range(min(5, task_config.max_steps)):
                    action = env.models.Action(action_type=env.models.ActionType.SKIP)
                    obs, reward, done, info = env.step(action)
                    if done:
                        break

                # Test grading
                final_state = env.state()
                grading_result = grade_episode(task_id, final_state)

                required_keys = ["score", "passed", "threshold", "breakdown", "metrics"]
                missing_keys = [k for k in required_keys if k not in grading_result]

                if missing_keys:
                    result.add_fail(f"Tasks and graders - {task_id} missing grading keys: {missing_keys}")
                elif not isinstance(grading_result["score"], (int, float)):
                    result.add_fail(f"Tasks and graders - {task_id} invalid score type")
                else:
                    result.add_pass(f"Tasks and graders - {task_id} valid")

            except Exception as e:
                result.add_fail(f"Tasks and graders - {task_id} error: {e}")

    except Exception as e:
        result.add_fail(f"Tasks and graders - general error: {e}")


def check_hf_space_deployment(result: ValidationResult):
    """Check HF Space deployment readiness."""
    try:
        # Check for HF Space directory
        hf_space_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hf-space")

        if not os.path.exists(hf_space_dir):
            result.add_warning("HF Space deployment - hf-space directory not found")
            return

        # Check for app.py in hf-space
        app_py = os.path.join(hf_space_dir, "app.py")
        if not os.path.exists(app_py):
            result.add_fail("HF Space deployment - app.py not found in hf-space")
            return

        # Check for requirements.txt in hf-space
        req_txt = os.path.join(hf_space_dir, "requirements.txt")
        if not os.path.exists(req_txt):
            result.add_fail("HF Space deployment - requirements.txt not found in hf-space")
            return

        result.add_pass("HF Space deployment - directory structure valid")

    except Exception as e:
        result.add_fail(f"HF Space deployment - error: {e}")


def main():
    print("\n" + "="*80)
    print("EMAIL TRIAGE OPENENV - PHASE 1 VALIDATION")
    print("="*80)
    print("Running automated validation checks...")
    print()

    result = ValidationResult()

    # Run all checks
    check_openenv_compliance(result)
    check_dockerfile(result)
    check_baseline_reproduction(result)
    check_tasks_and_graders(result)
    check_hf_space_deployment(result)

    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)

    summary = result.summary()
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Warnings: {summary['warnings']}")
    print(".1f")

    if result.failed:
        print("\n❌ FAILED CHECKS:")
        for fail in result.failed:
            print(f"  • {fail}")

    if result.warnings:
        print("\n⚠️  WARNINGS:")
        for warn in result.warnings:
            print(f"  • {warn}")

    # Overall result
    if summary['failed'] == 0:
        print("\n🎉 ALL PHASE 1 CHECKS PASSED!")
        print("Your project is ready for automated validation.")
        exit_code = 0
    else:
        print(f"\n❌ {summary['failed']} CHECK(S) FAILED")
        print("Fix the issues above before submission.")
        exit_code = 1

    # Save detailed results
    output_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "openenv_version": "1.0.0",
        },
        "summary": summary,
        "passed": result.passed,
        "failed": result.failed,
        "warnings": result.warnings,
    }

    with open("validation_results.json", "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nDetailed results saved to: validation_results.json")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())