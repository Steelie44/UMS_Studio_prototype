#ifndef UMS_TRANSPORT_H
#define UMS_TRANSPORT_H

#include <stdint.h>

void ums_tx_bytes(const uint8_t* data, uint16_t len);
uint8_t ums_rx_byte(uint8_t* out);

#endif
