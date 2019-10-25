def intToBin8(i):
    return (bin(((1 << 8) - 1) & i)[2:]).zfill(8)

