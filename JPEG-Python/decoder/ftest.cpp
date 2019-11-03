#include <cstdio>
#include <stack>
#include <string>
#include <iostream>

using namespace std;

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

int len_of_int_bin(int num)
{
    if(num == 0)
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
int main()
{
    // write_image_data_to_file("c-binary-data.bin");
    for (int i = -64; i < 64; i++)
    {
        cout << i << "\t" << len_of_int_bin(i) << endl;
    }
}