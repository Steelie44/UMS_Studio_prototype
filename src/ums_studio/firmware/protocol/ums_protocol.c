#include "ums_protocol.h"
#include "ums_transport.h"

static uint8_t state = 0;
static uint8_t length = 0;
static uint8_t type = 0;
static uint16_t seq = 0;
static uint8_t buf[256];
static uint16_t pos = 0;
static uint16_t payload_len = 0;
static uint16_t crc_recv = 0;

void ums_protocol_init(void) {
    state = 0;
    length = 0;
    type = 0;
    seq = 0;
    pos = 0;
    payload_len = 0;
    crc_recv = 0;
}

uint16_t ums_crc16(const uint8_t* data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000) crc = (crc << 1) ^ 0x1021;
            else crc <<= 1;
        }
    }
    return crc;
}

uint8_t ums_protocol_feed(uint8_t b, ums_packet_t* out) {
    switch (state) {
        case 0:
            if (b == UMS_SYNC_1) state = 1;
            break;
        case 1:
            if (b == UMS_SYNC_2) state = 2;
            else state = 0;
            break;
        case 2:
            length = b;
            if (length < 5) {
                state = 0;
                break;
            }
            pos = 0;
            state = 3;
            break;
        case 3:
            type = b;
            state = 4;
            break;
        case 4:
            seq = (uint16_t)b << 8;
            state = 5;
            break;
        case 5:
            seq |= b;
            payload_len = length - 5;
            state = payload_len == 0 ? 7 : 6;
            break;
        case 6:
            if (pos < payload_len) {
                buf[pos++] = b;
                if (pos == payload_len) state = 7;
            }
            break;
        case 7:
            crc_recv = (uint16_t)b << 8;
            state = 8;
            break;
        case 8:
            {
                uint8_t header[6] = {UMS_SYNC_1, UMS_SYNC_2, length, type, (uint8_t)(seq >> 8), (uint8_t)seq};
                uint8_t crc_data[261];
                uint16_t crc_calc = 0;

                crc_recv |= b;
                for (uint8_t i = 0; i < 6; i++) crc_data[i] = header[i];
                for (uint16_t i = 0; i < pos; i++) crc_data[6 + i] = buf[i];
                crc_calc = ums_crc16(crc_data, 6 + pos);

                if (crc_calc == crc_recv) {
                    out->type = type;
                    out->seq = seq;
                    out->payload_len = pos;
                    for (uint16_t i = 0; i < pos; i++) out->payload[i] = buf[i];
                    state = 0;
                    return 1;
                }
                state = 0;
            }
            break;
    }
    return 0;
}

void ums_protocol_send(uint8_t type, uint16_t seq, const uint8_t* payload, uint16_t len) {
    uint8_t header[6] = {UMS_SYNC_1, UMS_SYNC_2, (uint8_t)(len + 5), type, (uint8_t)(seq >> 8), (uint8_t)seq};
    uint8_t crc_data[261];
    uint16_t crc = 0;

    if (len > 250) return;

    for (uint8_t i = 0; i < 6; i++) crc_data[i] = header[i];
    for (uint16_t i = 0; i < len; i++) crc_data[6 + i] = payload[i];
    crc = ums_crc16(crc_data, 6 + len);

    ums_tx_bytes(header, 6);
    ums_tx_bytes(payload, len);
    uint8_t c[2] = {(uint8_t)(crc >> 8), (uint8_t)crc};
    ums_tx_bytes(c, 2);
}
