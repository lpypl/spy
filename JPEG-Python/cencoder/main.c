#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "jpeg.h"
#include "jpeg-binary-tools.h"

void textBinary2binary(const char *infname, const char *midBinFname, const char *slashBinFname)
{
    bin_str_to_bin_data(infname, midBinFname);
    slashImgData(midBinFname, slashBinFname);
}

void createJPEG(const char *huffman_bin_fname, const char *image_data_bin_fname, const char *outfname, 
            uint16_t width, uint16_t height, uint8_t channel)
{
    FILE *foutp = fopen(outfname, "wb");
    write_SOI_APP0_DQT(foutp);
    write_SOF0(foutp, channel, height, width);
    write_HUFFMAN(foutp, huffman_bin_fname);
    write_SOS(foutp, channel);
    write_IMAGE_DATA(foutp, image_data_bin_fname);
    write_EOI(foutp);
    fclose(foutp);
}

int main(int argc, const char **argv)
{
    if(argc < 2)
    {
        printf("Usage: \
        \n\t%s t2b(text2binary) ...\
        \n\t%s cj(constructJPEG) ...\
        \n\t%s slash ...", argv[0], argv[0], argv[0]);
        return -1;
    }

    if(strcmp("t2b", argv[1]) == 0)
    {
        if (argc != 4)
        {
            printf("Usage:\n\t%s t2b infile outfile\n", argv[0]);
            return -1;
        }
        else
        {
            bin_str_to_bin_data(argv[2], argv[3]);
        }
    }
    else if(strcmp("slash", argv[1]) == 0)
    {
        if (argc != 4)
        {
            printf("Usage:\n\t%s slash infile outfile\n", argv[0]);
            return -1;
        }
        else
        {
            slashImgData(argv[2], argv[3]);
        }
    }
    else if(strcmp("cj", argv[1]) == 0)
    {
        if (argc != 8)
        {
            printf("Usage:\n\t%s cj huffman_bin_file image_data_bin_file outfile width height channel\n", argv[0]);
            return -1;
        }
        else
        {
            createJPEG(argv[2], argv[3], argv[4], atoi(argv[5]), atoi(argv[6]), atoi(argv[7]));
        }
    }
    else 
    {
        printf("Usage: \
        \n\t%s t2b(text2binary) ...\
        \n\t%s cj(constructJPEG) ...\
        \n\t%s slash ...", argv[0], argv[0], argv[0]);
        return -1;
    }

    
}