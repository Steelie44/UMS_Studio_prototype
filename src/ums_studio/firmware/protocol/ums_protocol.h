#ifndef UMS_PROTOCOL_H
#define UMS_PROTOCOL_H

#include <stdint.h>

#define UMS_SYNC_1 0xAA
#define UMS_SYNC_2 0x55

#define UMS_TYPE_MOVE    0x01
#define UMS_TYPE_ARC     0x02
#define UMS_TYPE_DWELL   0x03
#define UMS_TYPE_SPINDLE 0x04
#define UMS_TYPE_COOLANT 0x05
#define UMS_TYPE_SYSTEM  0x06

#define UMS_TYPE_OK      0x10
#define UMS_TYPE_ERR     0x11
#define UMS_TYPE_STATE   0x12
#define UMS_TYPE_EVENT   0x13

typedef struct {
    uint8_t type;
    uint16_t seq;
    uint8_t payload[256];
    uint16_t payload_len;
} ums_packet_t;

void ums_protocol_init(void);
uint8_t ums_protocol_feed(uint8_t b, ums_packet_t* out);
uint16_t ums_crc16(const uint8_t* data, uint16_t len);
void ums_protocol_send(uint8_t type, uint16_t seq, const uint8_t* payload, uint16_t len);

#endif
