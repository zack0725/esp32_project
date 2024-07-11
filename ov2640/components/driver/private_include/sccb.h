#ifndef __SCCB_H__
#define __SCCB_H__
#include <stdint.h>
int SCCB_Init(int pin_sda, int pin_scl);
uint8_t SCCB_Probe();
uint8_t SCCB_Read(uint8_t slv_addr, uint8_t reg);
uint8_t SCCB_Write(uint8_t slv_addr, uint8_t reg, uint8_t data);
uint8_t SCCB_Read16(uint8_t slv_addr, uint16_t reg);
uint8_t SCCB_Write16(uint8_t slv_addr, uint16_t reg, uint8_t data);
#endif