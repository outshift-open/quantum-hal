"""
Protocol Buffer Constants

This module defines expected string values for proto message fields that should
contain specific values as per the HAL API specification.

These constants correspond to the proto definitions in:
- proto/hal/adapters/common/v1/common.proto
"""

# HealthCheckResponse.message expected values
# From: hal.adapters.common.v1.HealthCheckResponse
HEALTH_CHECK_UP = "UP"
HEALTH_CHECK_DOWN = "DOWN"
VALID_HEALTH_CHECK_STATUSES = {HEALTH_CHECK_UP, HEALTH_CHECK_DOWN}

# ResourceHealthCheckResponse.message expected values
# From: hal.adapters.common.v1.ResourceHealthCheckResponse
RESOURCE_HEALTH_UP = "UP"
RESOURCE_HEALTH_DOWN = "DOWN"
RESOURCE_HEALTH_DEGRADED = "DEGRADED"
VALID_RESOURCE_HEALTH_STATUSES = {
    RESOURCE_HEALTH_UP,
    RESOURCE_HEALTH_DOWN,
    RESOURCE_HEALTH_DEGRADED
}
