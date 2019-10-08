#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#include "mutils.h"
#include "mbmp.h"


int readInfoFromBMP();
int revealInfoToBMP();
void errorExit(const char *msg);

int main(int argc, const char **argv)
{
    char msg[100]; 

    if(argc == 1)
    {
        sprintf(msg, "Usage:\n\t%s [reveal|read] [argument]", argv[0]);
        errorExit(msg);
    }

    if (!strcmp(argv[1], "reveal"))
    {
        if (argc != 5)
        {
            sprintf(msg, "Usage:\n\t%s reveal src dest info", argv[0]);
            errorExit(msg);
        }
        revealInfoToBMP(argv[2], argv[3], argv[4]);
    }
    else if(!strcmp(argv[1], "read"))
    {
        if (argc != 3)
        {
            sprintf(msg, "Usage:\n\t%s read src", argv[0]);
            errorExit(msg);
        }
        readInfoFromBMP(argv[2]);
    }

    
}

void errorExit(const char *msg)
{
    printf("\n%s\n", msg);
    exit(-1);
}


int readInfoFromBMP(const char *src)
{
    FILE *fp;
    BFHEADER bfhdr;
    BIHEADER bihdr;

    if ((fp = fopen(src, "rb")) == NULL)
    {
        printf("BMP file load failed!\n");
        return 1;
    }
    if (fread(&bfhdr, sizeof(bfhdr), 1, fp) < 1)
    {
        printf("Reading BMP file header failed!\n");
        return 1;
    }

    printf("BMP file header:\n");
    printBfhdr(&bfhdr);

    if (fread(&bihdr, sizeof(bihdr), 1, fp) < 1)
    {
        printf("Reading BMP info header failed!\n");
        return 1;
    }

    printf("BMP info header:\n");
    printBihdr(&bihdr);

    // read bmp data
    RGB **rgbData = BMPReaderRead(&bfhdr, &bihdr, fp);
    if (!rgbData)
    {
        printf("read failed!\n");
    }

    readInfo(rgbData, &bihdr);

    BMPReaderCleanup(rgbData, &bihdr);
    fclose(fp);
}

int revealInfoToBMP(const char *src, const char *dest, const char *info)
{
    FILE *fp;
    BFHEADER bfhdr;
    BIHEADER bihdr;

    if ((fp = fopen(src, "rb")) == NULL)
    {
        printf("BMP file load failed!\n");
        return 1;
    }
    if (fread(&bfhdr, sizeof(bfhdr), 1, fp) < 1)
    {
        printf("Reading BMP file header failed!\n");
        return 1;
    }

    printf("BMP file header:\n");
    printBfhdr(&bfhdr);

    if (fread(&bihdr, sizeof(bihdr), 1, fp) < 1)
    {
        printf("Reading BMP info header failed!\n");
        return 1;
    }

    printf("BMP info header:\n");
    printBihdr(&bihdr);

    // read bmp data
    RGB **rgbData = BMPReaderRead(&bfhdr, &bihdr, fp);
    if (!rgbData)
    {
        printf("read failed!\n");
    }

    // reveal information

    revealInfo(rgbData, &bihdr, info, strlen(info));
    bmp2file(dest, &bfhdr, &bihdr, rgbData);

    printf("%s wrote!\n", dest);

    BMPReaderCleanup(rgbData, &bihdr);
    fclose(fp);
}