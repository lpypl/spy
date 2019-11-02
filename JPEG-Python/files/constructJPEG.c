#include <stdio.h>
#include <stdint.h>
#include "jpeg.h"

void createJPEG1(const char *outfname)
{
    FILE *foutp = fopen(outfname, "wb");
    write_SOI_APP0_DQT(foutp);
    write_SOF0(foutp, 3, 1279, 1920);
    write_HUFFMAN(foutp, "jpeg-huffman-binary-string.bin");
    write_SOS(foutp, 3);
    write_IMAGE_DATA(foutp, "jpeg-data-binary-string-slash.bin");
    write_EOI(foutp);
    fclose(foutp);
}

int main()
{
    createJPEG1("my-first-jpeg-new.jpeg");
}