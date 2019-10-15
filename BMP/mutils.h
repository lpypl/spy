#ifndef _MUTILS_H_
#define _MUTILS_H_

#include <stddef.h>
#include "mbmp.h"

#define msiz(stru, memb) (sizeof(((stru *)0)->memb))
#define printBinary(base, structName, memberName) printBinaryFunc(base, offsetof(structName, memberName), msiz(structName, memberName))


void printBinaryFunc(void *base, uint32_t off, uint32_t len);

void printBihdr(BIHEADER *bihdrp);
void printBfhdr(BFHEADER *bfhdrp);
void printBihdrBinary(BIHEADER *bihdrp);
void printBfhdrBinary(BFHEADER *bfhdrp);
RGB** BMPReaderRead(const BFHEADER *bfhdrp, const BIHEADER *bihdrp, FILE *fp);
void BMPReaderCleanup(RGB** rgbData, const BIHEADER *bihdrp);
int bmp2file(const char *fname, const BFHEADER *bfhdrp, const BIHEADER *bihdrp, RGB **rgbData);
int hideInfo(RGB** rgbData, const BIHEADER *bihdrp, const char *info, uint16_t len);
int readInfo(RGB** rgbData, const BIHEADER *bihdrp);

#endif