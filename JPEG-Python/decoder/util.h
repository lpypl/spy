#ifndef _UTIL_H_
#define _UTIL_H_

#include <cstdint>
#include <string>

using std::string;

uint16_t read_uint16_bigend(FILE *foutp);
string generate_code_string(int num, int len);
int len_of_int_bin(int num);

#endif