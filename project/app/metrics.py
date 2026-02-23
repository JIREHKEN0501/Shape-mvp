from prometheus_client import Counter, Gauge

# -------------------------------
# Counters
# -------------------------------

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests"
)

http_errors_total = Counter(
    "http_errors_total",
    "Total number of HTTP error responses"
)

calibration_executions_total = Counter(
    "calibration_executions_total",
    "Total calibration executions"
)

drift_events_total = Counter(
    "drift_events_total",
    "Total detected drift events"
)

# -------------------------------
# Gauges
# -------------------------------

service_uptime_seconds = Gauge(
    "service_uptime_seconds",
    "Service uptime in seconds"
)
