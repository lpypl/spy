#include "jpeg.h"
#include <stdio.h>

uint8_t SOI_APP0[] = {
    0xFF, 0xD8, //SOI 
    0xFF, 0xE0, //APP0
    0x00, 0x10, //length
    0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x01, 
    0x01, 0x2C, 0x01, 0x2C, 0x00, 0x00};

uint8_t DQT_LU[] =
{
    0xFF, 0xDB, //DQT 
    0x00, 0x43, //length
    0x00, //高位：精度， 低位：量化表ID
    //zig-zag 排序的量化表
    0x10, 0xb, 0xc, 0xe, 0xc, 0xa, 0x10, 0xe, 
    0xd, 0xe, 0x12, 0x11, 0x10, 0x13, 0x18, 0x28, 
    0x1a, 0x18, 0x16, 0x16, 0x18, 0x31, 0x23, 0x25, 
    0x1d, 0x28, 0x3a, 0x33, 0x3d, 0x3c, 0x39, 0x33, 
    0x38, 0x37, 0x40, 0x48, 0x5c, 0x4e, 0x40, 0x44, 
    0x57, 0x45, 0x37, 0x38, 0x50, 0x6d, 0x51, 0x57, 
    0x5f, 0x62, 0x67, 0x68, 0x67, 0x3e, 0x4d, 0x71, 
    0x79, 0x70, 0x64, 0x78, 0x5c, 0x65, 0x67, 0x63, 
};


uint8_t DQT_CH[] = 
{
    0xFF, 0xDB, //DQT
    0x00, 0x43, //length
    0x01, //高位：精度， 低位：量化表ID
    //zig-zag 排序的量化表
    0x11, 0x12, 0x12, 0xe, 0x15, 0x18, 0x2f, 0x1a, 
    0xd, 0x18, 0x2f, 0x1a, 0x10, 0x42, 0x63, 0x63, 
    0x63, 0x18, 0x38, 0x42, 0x63, 0x63, 0x63, 0x63, 
    0x63, 0x28, 0x63, 0x63, 0x63, 0x63, 0x39, 0x63, 
    0x63, 0x63, 0x63, 0x63, 0x63, 0x63, 0x63, 0x63, 
    0x63, 0x45, 0x63, 0x38, 0x63, 0x63, 0x63, 0x63, 
    0x63, 0x63, 0x63, 0x63, 0x63, 0x63, 0x63, 0x63, 
    0x63, 0x63, 0x63, 0x63, 0x63, 0x63, 0x63, 0x63,
};

uint8_t EOI[] = {
    0xFF, 0xD9
};

/**
 * 按大端序将 uint16_t 写入二进制文件
 */ 
void write_uint16_bigend(FILE *foutp, uint16_t data)
{
    putc(data >> 8, foutp);
    putc(data, foutp);
}

void write_SOI_APP0_DQT(FILE *foutp)
{
    fwrite(SOI_APP0, sizeof(SOI_APP0), 1, foutp);
    fwrite(DQT_LU, sizeof(DQT_LU), 1, foutp);
    fwrite(DQT_CH, sizeof(DQT_CH), 1, foutp);
}

void write_SOF0(FILE *foutp, uint8_t channel, uint16_t height, uint16_t width)
{
    uint16_t len_of_SOF0 = 2 + 1 + 2 + 2 + 1 + (3 * channel);
    //SOF0
    putc(0xFF, foutp);
    putc(0xC0, foutp);
    //len
    write_uint16_bigend(foutp, len_of_SOF0);
    //精度！！！！！！！！！！！！！
    putc(0x08, foutp);
    //height
    write_uint16_bigend(foutp, height);
    //width
    write_uint16_bigend(foutp, width);
    //channel
    putc(channel, foutp);

    if (channel == 1)
    {
        putc(0x01, foutp);
        putc(0x11, foutp);
        putc(0x00, foutp);
    }
    else if (channel == 3)
    {
        //channel 1
        putc(0x01, foutp); //channel id
        putc(0x11, foutp); //采样因子 高4位：水平采样因子。低4位：垂直采样因子
        putc(0x00, foutp); //当前分量使用的量化表ID

        //channel 2
        putc(0x02, foutp); //channel id
        putc(0x11, foutp); //采样因子 高4位：水平采样因子。低4位：垂直采样因子
        putc(0x01, foutp); //当前分量使用的量化表ID

        //channel 3
        putc(0x03, foutp); //channel id
        putc(0x11, foutp); //采样因子 高4位：水平采样因子。低4位：垂直采样因子
        putc(0x01, foutp); //当前分量使用的量化表ID
    }
}

void write_HUFFMAN(FILE *foutp, const char *infname)
{
    int sz;
    uint8_t buf[1024];
    FILE *finp = fopen(infname, "rb");
    while((sz = fread(buf, 1, 2048, finp)) > 0)
    {
        fwrite(buf, sz, 1, foutp);
    }
    fclose(finp);
}


void write_SOS(FILE *foutp, uint8_t channel)
{
    uint16_t len_of_SOS = 2 + 1 + (2 * channel) + 3;
    //SOS header
    putc(0xFF, foutp);
    putc(0xDA, foutp);
    //len of sos
    write_uint16_bigend(foutp, len_of_SOS);
    //channel count
    putc(channel, foutp);

    //channel info
    if (channel == 1)
    {
        putc(0x01, foutp);
        putc(0x00, foutp);
    }
    else if (channel == 3)
    {
        //channel 1
        putc(0x01, foutp);
        //高4位：直流分量使用的哈夫曼编码树编号
        //低4位：交流分量使用的哈夫曼树编号
        putc(0x00, foutp); 

        //channel 2
        putc(0x02, foutp);
        putc(0x11, foutp);

        //channel 3
        putc(0x03, foutp);
        putc(0x11, foutp);
    }

    //some data
    putc(0x00, foutp);
    putc(0x3F, foutp);
    putc(0x00, foutp);
}

void write_IMAGE_DATA(FILE *foutp, const char *infname)
{
    int sz;
    int bufsize = 1024;
    uint8_t buf[bufsize];
    FILE *finp = fopen(infname, "rb");
    while((sz = fread(buf, 1, bufsize, finp)) > 0)
    {
        fwrite(buf, 1, sz, foutp);
    }
    fclose(finp);
}


void write_EOI(FILE *foutp)
{
    fwrite(EOI, sizeof(EOI), 1, foutp);
}