#include <stdio.h>
#include <stdint.h>



int main()
{
    uint16_t num = 0x1234;
    FILE *fp = fopen("files/endtesttt.bin", "wb");
    write_uint16_bigend(fp, num);
    fclose(fp);
}