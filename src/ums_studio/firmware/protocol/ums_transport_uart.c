#include "ums_transport.h"
#include "stm32f4xx_hal.h"

extern UART_HandleTypeDef huart1;

void ums_tx_bytes(const uint8_t* data, uint16_t len) {
    HAL_UART_Transmit(&huart1, (uint8_t*)data, len, 1000);
}

uint8_t ums_rx_byte(uint8_t* out) {
    if (HAL_UART_Receive(&huart1, out, 1, 1) == HAL_OK) return 1;
    return 0;
}
