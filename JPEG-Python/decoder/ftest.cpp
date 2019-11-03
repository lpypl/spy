#include <cstdio>

void write_image_data_to_file(const char *outfile)
{
    FILE *outfp = fopen(outfile, "wb");
    int ch = 0xff;
    for (size_t i = 0; i < 100; i++)
    {
        putc(ch, outfp);
    }
    fclose(outfp);
    printf("image data write to %s\n", outfile);
    
}

int main()
{
    write_image_data_to_file("c-binary-data.bin");
}