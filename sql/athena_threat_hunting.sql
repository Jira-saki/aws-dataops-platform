-- ==============================================================================
-- AWS Athena DataSecOps & Threat Hunting Query Suite
-- Target Database: dataops_lakehouse_prod
-- Partition Strategy: year/month/day via Glue Partition Projection
-- ==============================================================================

-- 1. Threat Detection: Sensitive File Probing & Reconnaissance Scanning
-- ตรวจจับ Actor ที่พยายามสแกนหาไฟล์ Configuration, Dotfiles หรือ Admin Panel
SELECT 
    tenant_id,
    user_masked_id,
    request_path,
    http_method,
    status_code,
    COUNT(*) AS scan_attempts,
    MIN(timestamp) AS first_attempt_utc,
    MAX(timestamp) AS last_attempt_utc
FROM dataops_lakehouse_prod.xserver_access_logs
WHERE (year = '2026' AND month = '08')
  AND (
      request_path LIKE '%/.env%'
      OR request_path LIKE '%/wp-config%'
      OR request_path LIKE '%/phpmyadmin%'
      OR request_path LIKE '%/etc/passwd%'
      OR status_code IN (401, 403, 404)
  )
GROUP BY tenant_id, user_masked_id, request_path, http_method, status_code
HAVING COUNT(*) >= 1
ORDER BY scan_attempts DESC;

-- 2. Brute Force & Rate Limit Violations
-- ตรวจจับพฤติกรรมระดมยิง POST เข้าสู่ Endpoint พิเศษ (เช่น wp-login.php, /api/auth)
SELECT 
    tenant_id,
    user_masked_id,
    request_path,
    COUNT(*) AS post_request_count,
    COUNT(CASE WHEN status_code = 403 THEN 1 END) AS forbidden_count
FROM dataops_lakehouse_prod.xserver_access_logs
WHERE http_method = 'POST'
  AND request_path LIKE '%login%'
GROUP BY tenant_id, user_masked_id, request_path
ORDER BY post_request_count DESC;

-- 3. Dead Letter Queue Monitoring (DLQ Hygiene)
-- ตรวจเช็กจำนวน Payload ที่ Regex Parsing ล้มเหลวเพื่อนำไปปรับปรุง Signature
SELECT 
    source_file,
    error_reason,
    COUNT(*) AS failed_records_count
FROM dataops_lakehouse_prod.dead_letter_queue
GROUP BY source_file, error_reason;
