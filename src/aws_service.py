"""
AWS Integration Service Layer for ASR OpsGuard.
Handles dispatching alerts to Amazon SNS, streaming custom metrics to Amazon CloudWatch,
and archiving health audit logs to Amazon S3.

Includes deterministic Mock / Dry-Run mode to prevent any unwanted AWS billing.
"""

import json
import logging
from datetime import datetime, timezone

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AWSService")


class AWSService:
    """Manages AWS interactions with automatic fallback to zero-cost mock mode."""

    def __init__(self, aws_config: dict):
        self.mock_mode = aws_config.get("mock_mode", True)
        self.region = aws_config.get("region_name", "us-east-1")
        self.sns_topic_arn = aws_config.get("sns_topic_arn", "")
        self.s3_bucket = aws_config.get("s3_bucket_name", "opsguard-health-logs")
        self.cw_namespace = aws_config.get("cloudwatch_namespace", "ASR/OpsGuard")

        self.sns_client = None
        self.cw_client = None
        self.s3_client = None

        if not self.mock_mode:
            try:
                import boto3
                self.sns_client = boto3.client("sns", region_name=self.region)
                self.cw_client = boto3.client("cloudwatch", region_name=self.region)
                self.s3_client = boto3.client("s3", region_name=self.region)
                logger.info(f"Connected to AWS Cloud Services in region: {self.region}")
            except Exception as e:
                logger.warning(f"Failed to initialize AWS clients ({e}). Defaulting to safe Mock Mode.")
                self.mock_mode = True
        else:
            logger.info("Operating in SAFE MOCK MODE (Zero AWS cost incurred).")

    def publish_alert(self, subject: str, message: str) -> bool:
        """
        Dispatches critical operational alerts via Amazon SNS.
        """
        if self.mock_mode:
            logger.info(f"[SIMULATED Amazon SNS Alert] Subject: '{subject}'")
            logger.info(f"[SIMULATED Amazon SNS Alert] Content:\n{message}")
            return True

        try:
            response = self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Subject=subject[:100],
                Message=message
            )
            logger.info(f"Published alert to Amazon SNS: MessageId={response.get('MessageId')}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish alert to Amazon SNS: {e}")
            return False

    def push_cloudwatch_metrics(self, metrics: dict, hostname: str) -> bool:
        """
        Streams custom infrastructure metrics to Amazon CloudWatch.
        """
        metric_data = [
            {
                "MetricName": "CPUUtilization",
                "Dimensions": [{"Name": "Hostname", "Value": hostname}],
                "Value": metrics["cpu_utilization_pct"],
                "Unit": "Percent"
            },
            {
                "MetricName": "MemoryUtilization",
                "Dimensions": [{"Name": "Hostname", "Value": hostname}],
                "Value": metrics["memory_utilization_pct"],
                "Unit": "Percent"
            },
            {
                "MetricName": "DiskUtilization",
                "Dimensions": [{"Name": "Hostname", "Value": hostname}],
                "Value": metrics["disk_utilization_pct"],
                "Unit": "Percent"
            }
        ]

        if self.mock_mode:
            logger.info(f"[SIMULATED Amazon CloudWatch] Streamed 3 metrics to namespace '{self.cw_namespace}' for host '{hostname}'")
            return True

        try:
            self.cw_client.put_metric_data(
                Namespace=self.cw_namespace,
                MetricData=metric_data
            )
            logger.info(f"Successfully streamed metrics to CloudWatch namespace '{self.cw_namespace}'")
            return True
        except Exception as e:
            logger.error(f"Failed to push metrics to CloudWatch: {e}")
            return False

    def archive_log_to_s3(self, log_payload: dict, filename: str) -> bool:
        """
        Archives diagnostic audit reports directly to an Amazon S3 Bucket.
        """
        payload_bytes = json.dumps(log_payload, indent=2).encode("utf-8")
        s3_key = f"audit-logs/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}/{filename}"

        if self.mock_mode:
            logger.info(f"[SIMULATED Amazon S3] Uploaded diagnostic report to s3://{self.s3_bucket}/{s3_key}")
            return True

        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=payload_bytes,
                ContentType="application/json"
            )
            logger.info(f"Archived report to Amazon S3: s3://{self.s3_bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to archive log to S3: {e}")
            return False
