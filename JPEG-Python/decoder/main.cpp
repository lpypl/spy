#include "decoder.h"
#include <stdio.h>

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
    // print_huffman();
}