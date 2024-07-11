#ifndef _CONVERSIONS_YUV_H_
#define _CONVERSIONS_YUV_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

void yuv2rgb(uint8_t y, uint8_t u, uint8_t v, uint8_t *r, uint8_t *g, uint8_t *b);

#ifdef __cplusplus
}
#endif

#endif /* _CONVERSIONS_YUV_H_ */