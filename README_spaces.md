# EmailTriage OpenEnv — Hugging Face Space

[![OpenEnv Spec](https://img.shields.io/badge/OpenEnv-v1.0-brightgreen)](https://github.com/openenv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade, research-grade OpenEnv environment for benchmarking LLM agents on real-world email triage, categorization, and response generation.

---

## 🚀 Features
- Multi-component, research-grade reward function
- Realistic, stochastic simulation (latency, noise, edge cases)
- Benchmark-quality tasks (easy, medium, hard) with adversarial/ambiguous scenarios
- FastAPI API and Gradio UI
- Deterministic graders, leaderboard, and plotting
- CLI, config, and environment variable support
- Hugging Face Spaces-ready Dockerfile and health check

---

## 🏗️ Usage

- **API:**
  - `/reset` — Reset environment
  - `/step` — Take action
  - `/state` — Get current state
  - `/health` — Health check
- **Web UI:**
  - Gradio interface (if enabled)
- **CLI:**
  - `python cli.py --task easy_categorization`

---

## 🏆 Why This Matters
- Real-world email triage is a critical productivity and safety challenge
- Enables rigorous, reproducible benchmarking for next-gen AI agents
- Built for OpenEnv and Hugging Face Spaces

---

## 📝 Citation
If you use this environment, please cite the OpenEnv project and this Space.
