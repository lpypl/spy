#ifndef _DECODER_H_
#define _DECODER_H_
#include <map>
#include <vector>
#include <stdint.h>
#include <string>

extern std::vector<std::map<std::string, uint8_t>> huffman_tables;
void read_jpeg(const char *infile, int skip_count, int least_len);
void print_huffman();
void read_jpeg_data(FILE *infp);
void read_sos(FILE *infp);
void read_huffman(FILE *infp);
void print_binary(int orinum, size_t len, uint8_t signal);
void skip_segment(FILE *infp);
uint16_t read_uint16_bigend(FILE *foutp);
void print_image_data();
void write_image_data_to_file(const char *outfile);

#endif