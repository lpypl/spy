#include <cstdint>
#include <cstdio>
#include <string>

using std::string;

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

/**
 * 生成二进制码字符串
 */
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

/**
 * 返回按照jpeg编码规则时的编码长度
 */
int len_of_int_bin(int num)
{
    if (num == 0)
        return 1;

    num = abs(num);
    string bin;
    while (num != 0)
    {
        bin.push_back((num % 2) + 0x30);
        num /= 2;
    }
    return bin.size();
}