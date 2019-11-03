#include <cstdio>
#include <cstdint>
#include <map>
#include <vector>
#include "jpeg.h"

using namespace std;

//哈夫曼表
vector<map<uint16_t, uint8_t>> huffman_tables(4, map<uint16_t, uint8_t>());

/**
 * 按大端序读取 uint16_t
 */
uint16_t read_uint16_bigend(FILE *foutp)
{
    uint16_t data = 0;
    data |= getc(foutp) << 8;
    data |= getc(foutp);

    return data;
}

void skip_segment(FILE *infp)
{
    uint8_t len = read_uint16_bigend(infp);
    len -= 2;
    fseek(infp, len, SEEK_CUR);
}

void print_binary(int orinum, size_t len, uint8_t signal)
{
    int arr[len];
    int num = orinum;
    for (size_t i = 0; i < len; i++)
    {
        arr[i] = 0;
    }

    size_t cur = len - 1;
    while (num && cur >= 0)
    {
        if (num & 0x1)
            arr[cur--] = 1;
        else
            arr[cur--] = 0;
        num >>= 1;
    }

    printf("%d\t%02X\t", orinum, signal);

    for (size_t i = 0; i < len; i++)
    {
        printf("%d", arr[i]);
    }
    printf("\n");
}

void read_huffman(FILE *infp)
{
    uint8_t len = read_uint16_bigend(infp);
    //减去长度本身的长度
    len -= 2;

    int ch;
    int huffman_type;
    int huffman_id;
    int huffman_count[16] = {0};
    int huffman_total = 0;

    while (len > 0)
    {

        ch = getc(infp);
        --len;
        huffman_type = ch >> 4;
        huffman_id = ch & 0xf;
        printf("\t%s %d\n", huffman_type ? "AC" : "DC", huffman_id);

        huffman_total = 0;
        for (int i = 0; i < 16; i++)
        {
            huffman_count[i] = getc(infp);
            huffman_total += huffman_count[i];
        }

        len -= 16;

        printf("huffman total is %d\n", huffman_total);

        // fseek(infp, huffman_total, SEEK_CUR);
        int layer_diff = 0;
        int code = 0;
        uint8_t signal;
        for (int layer = 0; layer < 16; layer++)
        {
            for (int ct = 0; ct < huffman_count[layer]; ct++)
            {
                code = (code + 1) << layer_diff;
                signal = getc(infp);
                // print_binary(code, layer+1, signal);
                huffman_tables[huffman_type * 2 + huffman_id].insert({code, signal});
                layer_diff = 0;
            }
            layer_diff++;
        }
        len -= huffman_total;
    }
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

    for (int type = 0; type < 2; type++)
    {
        for (int id = 0; id < 2; id++)
        {
            printf("type: %d id:%d\n", type, id);
            for(auto item : huffman_tables[type*2+id])
            {
                printf("%d\t %02X\n", item.first, item.second);
            }
        }
    }
}