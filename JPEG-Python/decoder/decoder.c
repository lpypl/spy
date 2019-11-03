#include <stdio.h>
#include "jpeg.h"
#include <stdint.h>

/**
 * 按大端序读取 uint16_t
 */
uint16_t read_uint16_bigend(FILE *foutp)
{
    uint16_t data = 0;
    data |= getc(foutp) << 8;
    data |= getc(foutp);
}

void skip_segment(FILE *infp)
{
    uint8_t len = read_uint16_bigend(infp);
    len -= 2;
    fseek(infp, len, SEEK_CUR);
}

void read_huffman(FILE *infp)
{
    uint8_t len = read_uint16_bigend(infp);
    len -= 2;
    int ch;
    ch = getc(infp);
    printf("\t%s %d\n", ch>>4?"AC":"DC", ch&0xf);
    len -= 1;

    fseek(infp, len, SEEK_CUR);

}

void read_jpeg(const char *infile)
{
    FILE *infp = fopen(infile, "rb");
    int ch;

    while ((ch = getc(infp)) != -1)
    {
        if (ch != 0xFF)
            continue;

        if ((ch = getc(infp)) == -1)
        {
            printf("\n$$$$$$ 0xFF之后EOF $$$$$$\n");
            return;
        }

        switch (ch)
        {
        case SOI:
            printf("SOI found\n");
            break;
        case DQT:
            printf("DQT found\n");
            skip_segment(infp);
            break;
        case SOF0:
            printf("SOF0 found\n");
            skip_segment(infp);
            break;
        case DHT:
            printf("DHT found\n");
            read_huffman(infp);
            break;
        case SOS:
            printf("SOS found\n");
            skip_segment(infp);
            break;
        case EOI:
            printf("EOI found\n");
            break;
        default:
            //APP0-APP15
            if (ch >> 4 == 0xE)
            {
                printf("APP LABEL %02X found\n", ch);
                skip_segment(infp);
            }
            break;
        }
    }
}

int main(int argc, const char **argv)
{
    if (argc < 2)
    {
        printf("Usage:\n\
        \t%s infile\n",
               argv[0]);
        return -1;
    }
    read_jpeg(argv[1]);
}