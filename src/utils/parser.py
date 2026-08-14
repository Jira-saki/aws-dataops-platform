import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

ACCESS_LOG_REGEX = re.compile(
    r"^(?P<domain>\S+)\s+(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+"
    r'"(?P<method>\S+)\s+(?P<path>\S+)\s+\S+"\s+(?P<status>\d{3})\s+(?P<bytes>\S+)\s+'
    r'"(?P<referer>[^"]*)"\s+"(?P<user_agent>[^"]*)"'
)

AUDIT_LOG_REGEX = re.compile(
    r"^\[(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+\[(?P<level>\w+)\]\s+(?P<message>.*)$"
)

def parse_access_time(time_str: str) -> Tuple[str, str, str, str]:
    """Parse '20/Jul/2026:06:25:34 +0900' to ISO timestamp and (year, month, day)."""
    try:
        clean_time = time_str.split()[0]
        dt = datetime.strptime(clean_time, "%d/%b/%Y:%H:%M:%S")
        return dt.isoformat(), f"{dt.year:04d}", f"{dt.month:02d}", f"{dt.day:02d}"
    except Exception:
        now = datetime.utcnow()
        return time_str, f"{now.year:04d}", f"{now.month:02d}", f"{now.day:02d}"

def parse_access_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse single access log line."""
    match = ACCESS_LOG_REGEX.match(line.strip())
    if not match:
        return None
    
    data = match.groupdict()
    iso_time, year, month, day = parse_access_time(data["time"])
    clean_path = data["path"].split("?")[0]
    
    return {
        "raw_domain": data["domain"],
        "raw_ip": data["ip"],
        "timestamp": iso_time,
        "year": year,
        "month": month,
        "day": day,
        "http_method": data["method"],
        "request_path": clean_path,
        "status_code": int(data["status"]),
        "response_bytes": int(data["bytes"]) if data["bytes"].isdigit() else 0,
        "referer": data["referer"],
        "user_agent": data["user_agent"],
    }

def parse_audit_line(line: str, filename: str) -> Optional[Dict[str, Any]]:
    """Parse security audit log line."""
    line_clean = line.strip()
    if not line_clean:
        return None
        
    match = AUDIT_LOG_REGEX.match(line_clean)
    if match:
        data = match.groupdict()
        dt = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
        return {
            "source_file": filename,
            "timestamp": dt.isoformat(),
            "year": f"{dt.year:04d}",
            "month": f"{dt.month:02d}",
            "day": f"{dt.day:02d}",
            "log_level": data["level"].upper(),
            "message": data["message"],
            "raw_line": line_clean
        }
    
    now = datetime.utcnow()
    return {
        "source_file": filename,
        "timestamp": now.isoformat(),
        "year": f"{now.year:04d}",
        "month": f"{now.month:02d}",
        "day": f"{now.day:02d}",
        "log_level": "INFO",
        "message": line_clean,
        "raw_line": line_clean
    }
