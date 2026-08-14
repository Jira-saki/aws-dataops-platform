from src.utils.hasher import hash_ip
from src.utils.parser import parse_access_line, parse_audit_line

def test_hash_ip_deterministic():
    ip = "192.168.1.100"
    hash1 = hash_ip(ip)
    hash2 = hash_ip(ip)
    assert hash1 == hash2
    assert len(hash1) == 12

def test_parse_valid_access_line():
    sample = 'senbi-west.work 133.242.18.23 - - [20/Jul/2026:06:25:34 +0900] "GET /index.php?token=xyz HTTP/1.1" 200 4523 "-" "Mozilla/5.0"'
    parsed = parse_access_line(sample)
    assert parsed is not None
    assert parsed["raw_domain"] == "senbi-west.work"
    assert parsed["raw_ip"] == "133.242.18.23"
    assert parsed["request_path"] == "/index.php"
    assert parsed["year"] == "2026"
    assert parsed["status_code"] == 200

def test_parse_corrupted_log_line():
    corrupted = 'CORRUPTED LOG LINE WITHOUT PROPER FORMAT'
    parsed = parse_access_line(corrupted)
    assert parsed is None

def test_parse_audit_line():
    sample = '[2026-08-01 12:00:00] [WARN] File integrity violation detected on /etc/passwd'
    parsed = parse_audit_line(sample, "audit_report_2026-08-01.txt")
    assert parsed is not None
    assert parsed["log_level"] == "WARN"
    assert parsed["source_file"] == "audit_report_2026-08-01.txt"
