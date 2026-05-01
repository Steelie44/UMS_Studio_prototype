#include "ums_state.h"
#include "ums_protocol.h"
#include <stdio.h>

static uint16_t seq = 1;

void ums_send_state(float x, float y, float z, float f, float s) {
    char buf[128];
    int n = snprintf(buf, sizeof(buf), "{\"X\":%.3f,\"Y\":%.3f,\"Z\":%.3f,\"F\":%.1f,\"S\":%.1f}", x, y, z, f, s);
    ums_protocol_send(UMS_TYPE_STATE, seq++, (uint8_t*)buf, n);
}

void ums_send_event(const char* json) {
    uint16_t len = 0;
    while (json[len]) len++;
    ums_protocol_send(UMS_TYPE_EVENT, seq++, (const uint8_t*)json, len);
}
