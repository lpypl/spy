#include "decoder.h"
#include <cstdio>
#include <cstdlib>

int main(int argc, const char **argv)
{
    int skip_count = 0;
    int least_len = 0;
    const char *infile;

    switch (argc)
    {
    case 4:
        least_len = atoi(argv[3]);
    case 3:
        skip_count = atoi(argv[2]);
    case 2:
        infile = argv[1];
        break;
    default:
        printf("Usage:\n\
        \t%s infile [skip_count] [least_len]\n",
               argv[0]);
        return -1;
    }

    read_jpeg(infile, skip_count, least_len);
}