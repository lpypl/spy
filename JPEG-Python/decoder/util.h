#ifndef _UTIL_H_
#define _UTIL_H_

#include <cstdint>
#include <string>
#include <vector>


using std::string;
using std::vector;
using std::to_string;

uint16_t read_uint16_bigend(FILE *foutp);
string generate_code_string(int num, int len);
int len_of_int_bin(int num);

class BitGenerator
{
private:
    //数据源
    vector<uint8_t> data;
    //哪一个vector元素
    size_t next_bit_item = 0;
    //哪一位uint8_t
    int next_bit_pos = 7;

public:
    BitGenerator(vector<uint8_t> data)
    {
        this->data = data;
    }

    /**
     * 提供下一位二进制编码
     */
    uint8_t next_bit()
    {
        if (next_bit_pos == -1)
        {
            if (next_bit_item == data.size() - 1)
            {
                // printf("end of file binary data....... %ld\n", __next_bit_item);
                throw 1;
            }
            else
            {
                // printf("%ld\n", __next_bit_item);
                next_bit_item += 1;
                next_bit_pos = 7;
            }
        }

        uint8_t bit = (data[next_bit_item] >> next_bit_pos) & 0x1;
        next_bit_pos--;
        return bit;
    }

    /**
     * 提供下一位二进制编码
     */
    string next_bit_string()
    {
        try
        {
            return to_string(next_bit());
        }
        catch (int errornum)
        {
            throw errornum;
        }
    }
};

#endif