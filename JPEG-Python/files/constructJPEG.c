#include <stdio.h>
#include "jpeg.h"
#include <stdint.h>

void slashImgData(const char *infname, const char *outfname)
{
    FILE *finp = fopen(infname, "rb");
    FILE *foutp = fopen(outfname, "wb");

    int ch;
    while((ch = getc(finp)) != -1) 
    {
        putc(ch, foutp);
        if(ch == 0xFF)
            putc(0x00, foutp);
    }

    fclose(finp);
    fclose(foutp);
}

void createJPEG(const char *outfname) 
{
    FILE *foutp = fopen(outfname, "wb");
    fwrite(SIO_APP0, sizeof(SIO_APP0), 1, foutp);
    fwrite(DQT_LU, sizeof(DQT_LU), 1, foutp);
    fwrite(DQT_CH, sizeof(DQT_CH), 1, foutp);
    fwrite(SOF0, sizeof(SOF0), 1, foutp);
    
    int sz;
    uint8_t buf[2048];
    FILE *finp = fopen("jpeg-huffman-binary-string.bin", "rb");
    while((sz = fread(buf, 1, 2048, finp)) > 0)
    {
        fwrite(buf, 1, sz, foutp);
    }

    fwrite(SOS, sizeof(SOS), 1, foutp);

    fclose(finp);

    finp = fopen("jpeg-data-binary-string-slash.bin", "rb");
    while((sz = fread(buf, 1, 2048, finp)) > 0)
    {
        fwrite(buf, 1, sz, foutp);
    }

    fwrite(EOI, sizeof(EOI), 1, foutp);

    fclose(finp);
    fclose(foutp);
}

int main()
{
    // slashImgData("jpeg-data-binary-string.bin",
    //     "jpeg-data-binary-string-slash.bin");
    createJPEG("my-first-jpeg.jpeg");
}