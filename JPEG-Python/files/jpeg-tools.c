#include <stdio.h>
#include <stdint.h>

void bin_str_to_bin_data(const char * str_file, const char *bin_file)
{
    FILE *fpin = fopen(str_file, "r");
    FILE *fpout = fopen(bin_file, "w");

    int ct = 7;
    char buf = 0x00;
    int ch;
    int printct=100;
    while(1)
    {
        if((ch = getc(fpin)) == -1)
        {
            goto end;
        }
        if(ch == '0')
            buf = buf | (0<<ct);
        else
            buf = buf | (1<<ct);
        ct--;
        if(ct < 0)
        {
            putc(buf, fpout);
            ct = 7;
            buf = 0x00;
        }
    }

end:
    fclose(fpin);
    fclose(fpout);
}

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

int main()
{
    // bin_str_to_bin_data("jpeg-huffman-binary-string.txt", "jpeg-huffman-binary-string.bin");
    bin_str_to_bin_data("jpeg-data-binary-string.txt", "jpeg-data-binary-string.bin");
    slashImgData("jpeg-data-binary-string.bin", "jpeg-data-binary-string-slash.bin");
}