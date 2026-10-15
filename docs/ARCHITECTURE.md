# Project Documentation: ASR OpsGuard (Cloud Edition)
**Enterprise Cloud Infrastructure Monitoring & Automated Alerting Solution**

---

## 1. Executive Summary & Problem Statement

### 1.1 Context & Problem
In distributed cloud and hybrid environments, unmonitored infrastructure degrades quietly before causing full service outages. System administrators and cloud operations analysts need lightweight, real-time observability over compute resources (CPU spikes, memory saturation, disk exhaustion) without deploying overly complex, expensive enterprise monitoring suites.

### 1.2 The Solution: ASR OpsGuard
**ASR OpsGuard** is a containerized, cloud-integrated infrastructure health monitor. It actively collects Linux server telemetry, checks configurable operational thresholds (e.g., >80% resource saturation), automatically publishes health telemetry to **Amazon CloudWatch**, dispatches instant alert notifications via **Amazon SNS**, and archives structured audit and incident logs to **Amazon S3** for compliance and post-mortem analysis.

---

## 2. High-Level Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │            Host Server / AWS EC2            │
                    │                                              │
                    │   ┌──────────────────────────────────────┐   │
                    │   │       ASR OpsGuard Container         │   │
                    │   │                                      │   │
                    │   │  • Metric Collector (CPU, RAM, Disk) │   │
                    │   │  • Threshold Evaluator Engine        │   │
                    │   │  • AWS Boto3 Integration Layer       │   │
                    │   └──────────────────┬───────────────────┘   │
                    └──────────────────────┼───────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         │ (Normal Telemetry)              │ (Alert on Breach)               │ (Log Archival)
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│ Amazon CloudWatch│             │    Amazon SNS    │             │    Amazon S3     │
│                  │             │                  │             │                  │
│ • Custom Metrics │             │ • Incident Alert │             │ • Daily Health   │
│ • Dashboards     │             │ • Email / SMS    │             │   Audit Logs     │
│ • Trend Analysis │             │   Notifications  │             │ • 30-day Archive │
└──────────────────┘             └──────────────────┘             └──────────────────┘
```

---

## 3. Technology Stack & Cloud Design

| Layer | Technology | Role & Purpose |
| :--- | :--- | :--- |
| **Operating System** | Linux (Ubuntu / Alpine) | Base operating environment for process execution and resource tracking |
| **Runtime Language** | Python 3.10+ | Clean, readable metric collection (`psutil`) and cloud communication |
| **Cloud SDK** | AWS SDK (`boto3`) | Programmatic interface to publish metrics, dispatch alerts, and upload logs |
| **Containerization**| Docker | Ensures platform-agnostic, portable execution across local VMs and cloud |
| **Cloud Compute** | AWS EC2 (t2.micro / t3.micro)| Host instance running on AWS Free Tier |
| **Alerting Service** | Amazon SNS (Simple Notification Service) | Publish/Subscribe broker for sending instant alert emails to administrators |
| **Storage Layer** | Amazon S3 (Simple Storage Service) | Highly durable, object storage for operational reports and audit history |
| **Observability** | Amazon CloudWatch | Time-series metrics engine and operational dashboards |
| **Security & IAM** | AWS IAM (Instance Profile) | Zero hardcoded credentials via role-based temporary STS credentials |

---

## 4. Key Functional Requirements

1. **Telemetry Collection**:
   - Aggregate CPU utilization percentage across all cores.
   - Aggregate Virtual Memory (RAM) percentage and available free memory.
   - Aggregate Root Disk Partition (`/`) space usage and remaining gigabytes.
   - Collect host system uptime, hostname, and operating system details.

2. **Threshold Evaluation & Alerting**:
   - Support dynamic threshold configuration (default: 80% for CPU, 85% for Memory, 85% for Disk).
   - If an operational threshold is violated, trigger an incident alert containing:
     - Metric name and offending value.
     - Timestamp and Hostname / EC2 Instance ID.
     - Suggested troubleshooting checklist.
   - Publish to Amazon SNS topic to immediately alert stakeholders.

3. **Log Archival & Auditing**:
   - Maintain a local structured JSON/CSV diagnostic log.
   - Execute an automated rollover sync pushing diagnostic logs to an Amazon S3 bucket (`s3://asr-opsguard-logs-<account-id>/`).

4. **Security Best Practice (IAM Roles)**:
   - Absolutely no access keys or secret keys hardcoded in code or Docker images.
   - In AWS: Utilize IAM Instance Profile attached directly to EC2.
   - Locally: Support AWS CLI profile credentials (`~/.aws/credentials`) or a safe dry-run/mock mode for testing without an AWS account.

---

## 5. Directory & Repository Structure

```text
asr-opsguard/
├── README.md                  # Public GitHub repository documentation
├── docs/                      # Architectural & interview reference guides
│   ├── ARCHITECTURE.md        # Deep dive into components and data flow
│   └── INTERVIEW_QA.md        # Deloitte-tailored technical Q&A guide
├── config/
│   └── config.example.json    # Metric thresholds and AWS configuration parameters
├── src/
│   ├── __init__.py
│   ├── collector.py           # System metric harvesting (CPU, RAM, Disk)
│   ├── aws_service.py         # AWS SNS, CloudWatch, and S3 integration handlers
│   └── main.py                # Main operational loop and threshold evaluator
├── Dockerfile                 # Multi-stage/lightweight Docker configuration
├── docker-compose.yml         # Local orchestration & testing configuration
├── requirements.txt           # Python dependencies (boto3, psutil)
└── .gitignore                 # Standard Python/Docker/AWS ignore rules
```

---

## 6. Deloitte Interview Guide (Common Questions & Model Answers)

### Q1: "Can you explain the end-to-end flow of ASR OpsGuard?"
> **Your Answer:**  
> *"OpsGuard runs as a containerized agent on a Linux server or EC2 instance. Every scheduled cycle (e.g., 60 seconds), the collector reads hardware counters via the Linux kernel. It evaluates these against configurable thresholds. If CPU, RAM, or Disk utilization crosses critical limits (like 80%), it constructs an incident payload and invokes Amazon SNS to dispatch urgent email alerts. Concurrently, it streams the raw time-series metrics into Amazon CloudWatch for visual dashboarding, and bundles audit logs into Amazon S3 for historical compliance."*

### Q2: "How did you manage AWS credentials securely?"
> **Your Answer:**  
> *"I followed the AWS Well-Architected Framework and the principle of least privilege. I avoided hardcoding Access Keys or Secret Keys in the code or Dockerfile. When deployed on AWS EC2, the container utilizes an attached IAM Role (Instance Profile) with policies strictly limited to `sns:Publish`, `s3:PutObject`, and `cloudwatch:PutMetricData`. The AWS SDK (`boto3`) automatically discovers and rotates temporary STS credentials under the hood."*

### Q3: "Why did you choose Amazon SNS instead of writing a custom email script with SMTP?"
> **Your Answer:**  
> *"Using Amazon SNS decouples the alerting pipeline from the application. If the team decides tomorrow to route alerts to Slack, PagerDuty, SMS, or an automated AWS Lambda remediation script, we only add a subscription in SNS without modifying or redeploying any application code. It's also fully managed and highly available."*

### Q4: "Why containerize it with Docker?"
> **Your Answer:**  
> *"Containerization ensures environmental parity. It packages Python, the OS dependencies, and monitoring libraries into an immutable image. It guarantees that OpsGuard runs identically on my local Linux testing environment as it does on an AWS EC2 Amazon Linux or Ubuntu instance, without 'it works on my machine' issues."*

### Q5: "What challenges did you face and how did you resolve them?"
> **Your Answer:**  
> *"One initial challenge was 'alert fatigue'—if CPU spiked to 85% for 10 consecutive seconds, we didn't want 10 duplicate alert emails. I implemented a cooldown / state-tracking mechanism so an alert triggers once on threshold breach, and only notifies again if the state returns to normal or persists beyond a sustained evaluation window."*
