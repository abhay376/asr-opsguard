"""
System Metrics Collector Module for ASR OpsGuard.
Harvests CPU, Memory, Disk, and System Telemetry via Linux / OS Kernel hooks.
"""

import time
import socket
import platform
import psutil
from datetime import datetime, timezone


class MetricsCollector:
    """Collects deterministic hardware telemetry from host environment."""

    def __init__(self):
        self.hostname = socket.gethostname()
        self.os_type = platform.system()
        self.boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc).isoformat()

    def get_system_uptime(self) -> str:
        """Calculates system uptime human-readable format."""
        uptime_seconds = int(time.time() - psutil.boot_time())
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def collect_metrics(self) -> dict:
        """
        Gathers current CPU, RAM, Disk, and OS metrics.
        Returns a structured dictionary of telemetry.
        """
        # CPU Utilization across all cores
        cpu_pct = psutil.cpu_percent(interval=0.5)

        # Virtual Memory (RAM)
        mem = psutil.virtual_memory()
        mem_pct = mem.percent
        mem_used_gb = round(mem.used / (1024 ** 3), 2)
        mem_total_gb = round(mem.total / (1024 ** 3), 2)

        # Root Partition Disk Utilization
        disk_target = "/" if self.os_type != "Windows" else "C:\\"
        disk = psutil.disk_usage(disk_target)
        disk_pct = disk.percent
        disk_used_gb = round(disk.used / (1024 ** 3), 2)
        disk_total_gb = round(disk.total / (1024 ** 3), 2)

        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "timestamp": timestamp,
            "hostname": self.hostname,
            "os": self.os_type,
            "uptime": self.get_system_uptime(),
            "metrics": {
                "cpu_utilization_pct": cpu_pct,
                "memory_utilization_pct": mem_pct,
                "memory_used_gb": mem_used_gb,
                "memory_total_gb": mem_total_gb,
                "disk_utilization_pct": disk_pct,
                "disk_used_gb": disk_used_gb,
                "disk_total_gb": disk_total_gb
            }
        }
