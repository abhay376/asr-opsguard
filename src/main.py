"""
ASR OpsGuard Main Orchestration Engine.
Runs continuous monitoring loops, evaluates SLA thresholds, dispatches alerts,
and generates structured diagnostic logs.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from collector import MetricsCollector
from aws_service import AWSService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ASR-OpsGuard")


def load_config() -> dict:
    """Loads configuration file from config/config.json or falls back to defaults."""
    config_path = Path(__file__).resolve().parent.parent / "config" / "config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    logger.warning("config.json not found! Falling back to enterprise defaults.")
    return {
        "monitoring": {
            "interval_seconds": 15,
            "cpu_threshold_percent": 80.0,
            "memory_threshold_percent": 85.0,
            "disk_threshold_percent": 90.0,
            "alert_cooldown_seconds": 60
        },
        "aws": {
            "mock_mode": True,
            "region_name": "us-east-1",
            "sns_topic_arn": "arn:aws:sns:us-east-1:123456789012:opsguard-alerts",
            "s3_bucket_name": "opsguard-health-logs",
            "cloudwatch_namespace": "ASR/OpsGuard"
        }
    }


def main():
    logger.info("=" * 60)
    logger.info("  Starting ASR OpsGuard (Cloud Edition)")
    logger.info("  Infrastructure Telemetry & Automated Incident Alerting")
    logger.info("=" * 60)

    config = load_config()
    mon_cfg = config.get("monitoring", {})
    aws_cfg = config.get("aws", {})

    interval = mon_cfg.get("interval_seconds", 15)
    cpu_thresh = mon_cfg.get("cpu_threshold_percent", 80.0)
    mem_thresh = mon_cfg.get("memory_threshold_percent", 85.0)
    disk_thresh = mon_cfg.get("disk_threshold_percent", 90.0)
    cooldown = mon_cfg.get("alert_cooldown_seconds", 60)

    collector = MetricsCollector()
    aws_svc = AWSService(aws_cfg)

    # State tracking to avoid alert storming / fatigue
    last_alert_time = 0
    cycle_count = 0

    try:
        while True:
            cycle_count += 1
            data = collector.collect_metrics()
            metrics = data["metrics"]
            hostname = data["hostname"]

            # Print concise console status
            logger.info(
                f"[Cycle #{cycle_count}] CPU: {metrics['cpu_utilization_pct']}% | "
                f"RAM: {metrics['memory_utilization_pct']}% ({metrics['memory_used_gb']}/{metrics['memory_total_gb']}GB) | "
                f"Disk: {metrics['disk_utilization_pct']}% | Uptime: {data['uptime']}"
            )

            # 1. Stream telemetry to Amazon CloudWatch
            aws_svc.push_cloudwatch_metrics(metrics, hostname)

            # 2. Check for SLA Threshold Breaches
            breaches = []
            if metrics["cpu_utilization_pct"] >= cpu_thresh:
                breaches.append(f"CPU Utilization breached: {metrics['cpu_utilization_pct']}% >= {cpu_thresh}%")
            if metrics["memory_utilization_pct"] >= mem_thresh:
                breaches.append(f"Memory Utilization breached: {metrics['memory_utilization_pct']}% >= {mem_thresh}%")
            if metrics["disk_utilization_pct"] >= disk_thresh:
                breaches.append(f"Disk Utilization breached: {metrics['disk_utilization_pct']}% >= {disk_thresh}%")

            # 3. Handle Alert Dispatch via Amazon SNS
            current_time = time.time()
            if breaches:
                if (current_time - last_alert_time) > cooldown:
                    subject = f"CRITICAL INCIDENT: Infrastructure Breach on {hostname}"
                    body = (
                        f"ASR OpsGuard Automated Health Alert\n"
                        f"-----------------------------------------\n"
                        f"Host: {hostname}\n"
                        f"Timestamp: {data['timestamp']}\n"
                        f"System Uptime: {data['uptime']}\n\n"
                        f"Triggered Violations:\n" + "\n".join(f"  • {b}" for b in breaches) + "\n\n"
                        f"Remediation Checklist:\n"
                        f"  1. SSH into the instance and run 'top' / 'htop' to identify rogue processes.\n"
                        f"  2. Inspect application logs for memory leaks or unhandled loops.\n"
                        f"  3. Check auto-scaling policies if utilization continues to grow."
                    )
                    aws_svc.publish_alert(subject, body)
                    last_alert_time = current_time
                else:
                    logger.info("Threshold breach detected, but suppressed under active alert cooldown.")

            # 4. Hourly / Periodic Log Archival to Amazon S3 (Simulated every 10 cycles for demo)
            if cycle_count % 10 == 0:
                report_name = f"health-report-{int(time.time())}.json"
                aws_svc.archive_log_to_s3(data, report_name)

            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("OpsGuard process terminated gracefully by administrator.")
        sys.exit(0)


if __name__ == "__main__":
    main()
