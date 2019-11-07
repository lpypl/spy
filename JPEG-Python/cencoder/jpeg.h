#ifndef _JPEG_H_
#define _JPEG_H_

#include <stdint.h>
#include <stdio.h>

extern uint8_t SOI_APP0[];
extern uint8_t DQT_LU[];
extern uint8_t DQT_CH[];
extern uint8_t SOS[];
extern uint8_t EOI[];

void write_uint16_bigend(FILE *foutp, uint16_t data);
void write_SOI_APP0_DQT(FILE *foutp);
void write_SOF0(FILE *foutp, uint8_t channel, uint16_t height, uint16_t width);
void write_HUFFMAN(FILE *foutp, const char *infname);
void write_SOS(FILE *foutp, uint8_t channel);
void write_IMAGE_DATA(FILE *foutp, const char *infname);
void write_EOI(FILE *foutp);
#endif