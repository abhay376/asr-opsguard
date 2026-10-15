# ASR OpsGuard (Cloud Edition)
### Enterprise Infrastructure Telemetry & Automated Cloud Alerting Solution

[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20SNS%20%7C%20S3%20%7C%20CloudWatch-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?logo=python)](https://www.python.org/)

---

## 📌 Project Overview
**ASR OpsGuard** is a lightweight, containerized infrastructure health monitoring and alerting system tailored for cloud environments. It actively monitors host system health (CPU, RAM, Disk utilization, and system uptime), evaluates metric streams against customizable SLA thresholds, and integrates with AWS native services:
- **Amazon SNS**: Immediate incident alerting to on-call engineers via Email/SMS.
- **Amazon CloudWatch**: Publishes real-time custom time-series metrics.
- **Amazon S3**: Automates archival of daily system health diagnostic logs.

---

## 🏗️ Architecture
`
[ Host Server / EC2 ]
         │
  [ ASR OpsGuard Container ]
         │  (Collects CPU, RAM, Disk, Uptime)
         ├── Evaluates Thresholds (>80% Warning / Critical)
         │
         ├── AWS Boto3 Integration Layer
         │     ├── Normal Stream ──────> Amazon CloudWatch (Metrics & Dashboards)
         │     ├── Threshold Breach ───> Amazon SNS (Instant Email/SMS Alerts)
         │     └── Daily Rollover ─────> Amazon S3 (Audit & Diagnostic Logs)
`

---

## 🚀 Key Features
- **Deterministic Resource Monitoring**: Gathers real-time CPU, RAM, and Disk metrics via system kernel hooks.
- **Alert Fatigue Prevention**: Built-in state tracking and cooldown prevents spamming repetitive emails during ongoing incidents.
- **Cloud-Native Security (IAM)**: Operates with IAM instance profile roles (no hardcoded API keys or secret credentials).
- **Standalone Mock Mode**: Full local execution capability for offline testing and demos without requiring an active AWS bill.
- **Dockerized Portability**: Deploys in seconds on any Linux distribution or cloud VM.

---

## 🛠️ Quick Start

### 1. Clone & Configure
`ash
git clone https://github.com/<your-username>/asr-opsguard.git
cd asr-opsguard
cp config/config.example.json config/config.json
`

### 2. Run with Docker
`ash
docker build -t asr-opsguard:latest .
docker run -d --name opsguard asr-opsguard:latest
`

---

## 📖 Detailed Documentation
- [Architecture & Design Specifications](docs/ARCHITECTURE.md)
- [Deloitte Interview Preparation Guide](docs/ARCHITECTURE.md#6-deloitte-interview-guide-common-questions--model-answers)
