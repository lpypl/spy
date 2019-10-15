#include <stdio.h>
#include <stdint.h>
#include "mbmp.h"
#include "mutils.h"
#include <stdlib.h>
#include <string.h>

void printBinaryFunc(void *base, uint32_t off, uint32_t len)
{
    int i;
    for(i=0; i<len; i++)
    {
        printf("%.2X ", *((uint8_t*)base+off+i));
    }
}

void printBfhdr(BFHEADER *bfhdrp)
{
    printf("\tbfType: %.2s\n", &bfhdrp->bfType);
    printf("\tbfSize: %u\n", bfhdrp->bfSize);
    printf("\tbfReserved1: %x\n", bfhdrp->bfReserved1);
    printf("\tbfReserved2: %x\n", bfhdrp->bfReserved2);
    printf("\tbfOffBits: %u\n", (int)bfhdrp->bfOffBits);
}

void printBfhdrBinary(BFHEADER *bfhdrp)
{
    printf("BMP file header binary:");
    printBinaryFunc(bfhdrp, 0, sizeof(BFHEADER));
    printf("\n");

    printf("bfType bin:");
    printBinary(bfhdrp, BFHEADER, bfType);
    printf("\n");

    printf("bfSize bin:");
    printBinary(bfhdrp, BFHEADER, bfSize);
    printf("\n");

    printf("bfReserved1 bin:");
    printBinary(bfhdrp, BFHEADER, bfReserved1);
    printf("\n");

    printf("bfReserved2 bin:");
    printBinary(bfhdrp, BFHEADER, bfReserved2);
    printf("\n");

    printf("bfOffBits bin:");
    printBinary(bfhdrp, BFHEADER, bfOffBits);
    printf("\n");
}

void printBihdr(BIHEADER *bihdrp)
{
    printf("\tbiSize: %u\n", bihdrp->biSize);
    printf("\tbiWidth: %u\n", bihdrp->biWidth);
    printf("\tbiHeight: %d\n", bihdrp->biHeight);
    printf("\tbiPlanes: %u\n", bihdrp->biPlanes);
    printf("\tbiBitCount: %u\n", bihdrp->biBitCount);
    printf("\tbiCompression: %u\n", bihdrp->biCompression);
    printf("\tbiSizeImage: %u\n", bihdrp->biSizeImage);
    printf("\tbiXPelsPerMeter: %d\n", bihdrp->biXPelsPerMeter);
    printf("\tbiYPelsPerMeter: %d\n", bihdrp->biYPelsPerMeter);
    printf("\tbiClrUsed: %u\n", bihdrp->biClrUsed);
    printf("\tbiClrImportant: %u\n", bihdrp->biClrImportant);
}

void printBihdrBinary(BIHEADER *bihdrp)
{
    printf("BMP info header bin:");
    printBinaryFunc(bihdrp, 0, sizeof(BIHEADER));
    printf("\n");

    printf("biSize bin:");
    printBinary(bihdrp, BIHEADER, biSize);
    printf("\n");

    printf("biWidth bin:");
    printBinary(bihdrp, BIHEADER, biWidth);
    printf("\n");

    printf("biHeight bin:");
    printBinary(bihdrp, BIHEADER, biHeight);
    printf("\n");

    printf("biPlanes bin:");
    printBinary(bihdrp, BIHEADER, biPlanes);
    printf("\n");

    printf("biBitCount bin:");
    printBinary(bihdrp, BIHEADER, biBitCount);
    printf("\n");

    printf("biSizeImage bin:");
    printBinary(bihdrp, BIHEADER, biSizeImage);
    printf("\n");

    printf("biXPelsPerMeter bin:");
    printBinary(bihdrp, BIHEADER, biXPelsPerMeter);
    printf("\n");

    printf("biYPelsPerMeter bin:");
    printBinary(bihdrp, BIHEADER, biYPelsPerMeter);
    printf("\n");

    printf("biClrUsed bin:");
    printBinary(bihdrp, BIHEADER, biClrUsed);
    printf("\n");

    printf("biClrImportant bin:");
    printBinary(bihdrp, BIHEADER, biClrImportant);
    printf("\n");
}

RGB** BMPReaderRead(const BFHEADER *bfhdrp, const BIHEADER *bihdrp, FILE *fp)
{

    if (fseek(fp, bfhdrp->bfOffBits, 0) != 0)
    {
        //printf("Seeking to bmp data zone failed!\n");
        return NULL;
    }

    //printf("Seeking to bmp data zone succeed!\n");

    RGB **rgbData;
    if( (rgbData = malloc(sizeof(RGB *) * bihdrp->biHeight)) == NULL)
    {
        return NULL;
    }

    int bmpLineLen = (bihdrp->biWidth*bihdrp->biBitCount / 8 + 3)/4 * 4;
    uint32_t *bmpLineData = malloc(sizeof(uint8_t) * bmpLineLen);

    for (int i = 0; i < bihdrp->biHeight; i++)
    {
        fread(bmpLineData, sizeof(uint8_t) * bmpLineLen, 1, fp);
        rgbData[i] = malloc(sizeof(RGB) * bihdrp->biWidth);
        memcpy(rgbData[i], bmpLineData, sizeof(RGB) * bihdrp->biWidth);
    }
    // printf("All RGB data Read!\n");

    return rgbData;
}

void BMPReaderCleanup(RGB** rgbData, const BIHEADER *bihdrp)
{
    for (int i = 0; i < bihdrp->biHeight; i++)
    {
        free(rgbData[i]);
    }

    free(rgbData);
}

int bmp2file(const char *fname, const BFHEADER *bfhdrp, const BIHEADER *bihdrp, RGB **rgbData)
{
    FILE * newBMP = fopen(fname, "wb");
    fwrite(bfhdrp, sizeof(*bfhdrp), 1, newBMP);
    fwrite(bihdrp, sizeof(*bihdrp), 1, newBMP);

    int bmpLineLen = (bihdrp->biWidth*bihdrp->biBitCount / 8 + 3)/4 * 4;

    for (int i = 0; i < bihdrp->biHeight; i++)
    {
        // allign
        fwrite(rgbData[i], sizeof(RGB) * bihdrp->biWidth, 1, newBMP);
        int padCount = bmpLineLen - sizeof(RGB)*bihdrp->biWidth;
        while(padCount--)
        {
            fwrite("\0\0\0\0", padCount, 1, newBMP);
        }
    }

    fclose(newBMP);
}

int hideInfo(RGB** rgbData, const BIHEADER *bihdrp, const char *info, uint16_t len)
{
    int index = 0;

    for (int r=0; r<bihdrp->biHeight; r++)
    {
        for (int b=0; b<3 * bihdrp->biWidth; b++)
        {
            if (index < 16)
            {
                if((len>>index)&0x0001)
                {
                    ((uint8_t *)(rgbData[r]))[b] |= 0x01;
                    printf("(1, %.2X)", ((uint8_t *)(rgbData[r]))[b]);
                }   
                else
                {
                    ((uint8_t *)(rgbData[r]))[b] &= 0xfe;
                    printf("(0, %.2X)", ((uint8_t *)(rgbData[r]))[b]);
                } 
                    
            }
            else
            {
                // which char (index-16) / 8
                // which bit (index-16) % 8
                if((index-16)/8 > len-1)
                    return 0;

                if((info[(index-16)/8]>>((index-16)%8))&0x0001)
                {
                    ((uint8_t *)(rgbData[r]))[b] |= 0x01;
                    printf("(1, %.2X)", ((uint8_t *)(rgbData[r]))[b]);
                }
                else
                {
                    ((uint8_t *)(rgbData[r]))[b] &= 0xfe;
                    printf("(0, %.2X)", ((uint8_t *)(rgbData[r]))[b]);
                } 
                    
            }

            index++;
        }
    }
}

int readInfo(RGB** rgbData, const BIHEADER *bihdrp)
{
    int index = 0;
    uint16_t len = 0;
    uint8_t *info =  NULL;

    for (int r=0; r<bihdrp->biHeight; r++)
    {
        for (int b=0; b<3 * bihdrp->biWidth; b++)
        {
            if (index < 16)
            {
                if((((uint8_t *)(rgbData[r]))[b])&0x0001)
                {
                    len |= (0x01<<index);
                }
                    
                else 
                {
                    len &= ~(0x01<<index);
                }
            }
            else
            {
                // which char (index-16) / 8
                // which bit (index-16) % 8
                if (info == NULL)
                {
                    info = malloc(len+1);
                    info[len] = '\0';
                }

                if((index-16)/8 > len-1)
                    goto end;

                if((((uint8_t *)(rgbData[r]))[b])&0x0001)
                {
                    info[(index-16)/8] |= (0x01<<(index-16)%8);
                }
                else 
                {
                    info[(index-16)/8] &= ~(0x01<<(index-16)%8);
                }
            }

            index++;
        }
    }

end:
    printf("getInfo: length is: %d, info is: %s\n", len, info);
    free(info);
}