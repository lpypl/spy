#include <cstdio>
#include <cstdint>
#include <map>
#include <vector>
#include <string>
#include "jpeg.h"
#include "decoder.h"

using namespace std;

//哈夫曼表
vector<map<string, uint8_t>> huffman_tables(4, map<string, uint8_t>());
//记录颜色通道对应的哈夫曼表（ 使用1，2，3 ）
uint8_t channel_huffman_info[4] = {0};
int channel_total = 0;
//
vector<uint8_t> jpeg_data;

//二进制码提供器控制变量
//哪一个vector元素
size_t __next_bit_item = 0;
//哪一位uint8_t
int __next_bit_pos = 7;

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

string generate_code_string(int num, int len)
{
    string arr(len, '0');
    int cur = len - 1;
    while (num && cur >= 0)
    {
        if (num & 0x1)
            arr[cur--] = '1';
        else
            arr[cur--] = '0';
        num >>= 1;
    }

    return arr;
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
        //设初值为-1才能保证第一个编码为0
        int code = -1;
        uint8_t signal;
        for (int layer = 0; layer < 16; layer++)
        {
            for (int ct = 0; ct < huffman_count[layer]; ct++)
            {
                code = (code + 1) << layer_diff;
                signal = getc(infp);

                huffman_tables[huffman_type * 2 + huffman_id].insert({generate_code_string(code, layer+1), signal});
                // printf("%u %u\n", code, signal);
                layer_diff = 0;
            }
            layer_diff++;
        }
        len -= huffman_total;
    }
}

void read_sos(FILE *infp)
{
    //length
    fseek(infp, 2, SEEK_CUR);
    //
    int channel = getc(infp);
    channel_total = channel;
    int id;
    int info;
    while (channel--)
    {
        id = getc(infp);
        info = getc(infp);
        channel_huffman_info[id] = info;
    }
    //tail
    fseek(infp, 3, SEEK_CUR);

    read_jpeg_data(infp);
}

void read_jpeg_data(FILE *infp)
{
    printf("Reading jpeg image data...\n");
    int ch;
    while ((ch = getc(infp)) != -1)
    {
        if (ch == 0xFF)
        {
            // printf("0xff found!\n");
            if ((ch = getc(infp)) == -1)
            {
                goto error_or_eof;
            }

            else if (ch == EOI)
            {
                printf("EOI found\n");
                return;
            }
            else if (ch == 0x00)
            {
                jpeg_data.push_back(0xFF);
            }
        }
        else
        {
            jpeg_data.push_back(ch);
        }
    }
error_or_eof:
    printf("\n******** EOF while reading jpeg data *******\n");
}

/**
 * 提供下一位二进制编码
 */
uint8_t next_bit()
{
    if (__next_bit_pos < 0)
    {
        if (__next_bit_item == jpeg_data.size() - 1)
            throw 1;
        else
        {
            __next_bit_item += 1;
            __next_bit_pos = 7;
        }
    }

    uint8_t bit = (jpeg_data[__next_bit_item] >> __next_bit_pos) & 0x1;
    __next_bit_pos--;
    return bit;
}

// void decode_jpeg_data()
// {
//     uint16_t code;
//     int dc_map_index = 0;
//     int ac_map_index = 0;
//     size_t len_of_signal = 0;
//     try
//     {
//         while (true)
//         {
//             //遍历所有channel
//             for (int channel = 1; channel <= channel_total; channel++)
//             {
//                 //当前使用的哈夫曼表索引
//                 dc_map_index = channel_huffman_info[channel] >> 4;
//                 ac_map_index = 2 + (channel_huffman_info[channel] & 0x0F);

//                 // DC
//                 // 先读一位，避免 00
//                 code = 0;
//                 code |= next_bit();
//                 while (huffman_tables[dc_map_index].find(code) == huffman_tables[dc_map_index].end())
//                 {
//                     code <<= 1;
//                     code |= next_bit();
//                 }
//                 len_of_signal = huffman_tables[dc_map_index][code];
//                 printf("code is %u, %02X\n", code, huffman_tables[dc_map_index][code]);
//                 exit(0);

//             }
//         }
//         printf("DC found: bits is %d\n", next_bit());
//     }
//     catch (int error)
//     {
//         printf("decode_jpeg_data finished!\n");
//     }
// }

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
            read_sos(infp);
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

    printf("%d %02X\n", 1, channel_huffman_info[1]);
    printf("%d %02X\n", 1, channel_huffman_info[2]);
    printf("%d %02X\n", 1, channel_huffman_info[3]);

    // print_image_data();
    print_huffman();
    // decode_jpeg_data();
}

void print_huffman()
{
    // print huffman
    for (int type = 0; type < 2; type++)
    {
        for (int id = 0; id < 2; id++)
        {
            printf("type: %d id:%d\n", type, id);
            for (auto item : huffman_tables[type * 2 + id])
            {
                printf("%s\t %02X\n", item.first.c_str(), item.second);
            }
        }
    }
}

void print_image_data()
{
    printf("image data length is %lu\n", jpeg_data.size());
    for (auto b = jpeg_data.begin(); b != jpeg_data.end(); b++)
    {
        printf("%02X ", *b);
    }
}