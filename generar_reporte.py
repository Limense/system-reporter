import json
import re
from datetime import datetime
from collections import Counter

def analizar_logs():
    # Simular logs de un servidor web
    logs = [
        "2025-05-27 19:04:32 INFO 200 GET /api/users 245ms",
        "2025-05-27 19:04:33 ERROR 404 GET /api/missing 12ms", 
        "2025-05-27 19:04:34 INFO 200 POST /api/login 156ms",
        "2025-05-27 19:04:35 WARN 429 GET /api/users 8ms",
        "2025-05-27 19:04:36 INFO 200 GET /api/dashboard 89ms"
    ]
    
    status_codes = Counter()
    endpoints = Counter()
    total_requests = len(logs)
    errors = 0
    
    for log in logs:
        if "ERROR" in log or "404" in log:
            errors += 1
        
        # Extraer código de estado
        status_match = re.search(r'\b(\d{3})\b', log)
        if status_match:
            status_codes[status_match.group(1)] += 1
            
        # Extraer endpoint
        endpoint_match = re.search(r'(GET|POST|PUT|DELETE) (/\S+)', log)
        if endpoint_match:
            endpoints[endpoint_match.group(2)] += 1
    
    return {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_requests": total_requests,
        "error_rate": f"{(errors/total_requests)*100:.1f}%",
        "status_codes": dict(status_codes),
        "top_endpoints": dict(endpoints.most_common(3)),
        "health_status": "🟢 HEALTHY" if errors < 2 else "🔴 UNHEALTHY"
    }

if __name__ == "__main__":
    reporte = analizar_logs()
    with open('log_report.json', 'w') as f:
        json.dump(reporte, f, indent=2)
    print("📊 Reporte de logs generado!")