from jpeg import *
import os
import itertools
import sys
from tempfile import TemporaryDirectory

npmidsignlist = []

def huffmanTable2BinaryDataStringFile(outfile):
    binaryData = huffmanTable2BinaryData(LuminanceDCCoefficientDifferencesTable,
                                         ChrominanceDCCoefficientDifferencesTable,
                                         acLuminanceTable, acChrominanceTable)
    # fout = open("files/jpeg-huffman-binary-string.txt", 'w')
    fout = open(outfile, 'w')
    fout.write(binaryData)
    fout.close()

def hideInfoInVal(val, infoVal):

    assert val not in (-1, 0, 1)

    if val > 0:

        if infoVal & 0x01 == 0:
            val &= 0b1111_1110
        else:
            val |= 0b0000_0001

    elif val < 0:
        valbak = abs(val)
        if infoVal & 0x01 == 0:
            valbak &= 0b1111_1110
        else:
            valbak |= 0b0000_0001

        val = -valbak
    return val


# -5      11111011
# -4      11111100
# -3      11111101
# -2      11111110
# -1      11111111
# 0       00000000
# 1       00000001
# 2       00000010
# 3       00000011
# 4       00000100
# 5       00000101

# -5      010
# -4      011
# -3      00
# -2      01
# -1      0
# 0       -
# 1       1
# 2       10
# 3       11
# 4       100
# 5       101

# 理论上说，若在经行程编码之后的中间符号的AC值中隐藏信息，只要最终变换后的数值非0，即可正常进行编码和解码
# 要求非0是因为AC编码表中不存在 除（0/0）和（F/0）之外的其他（X/0）信源
# 若使用 1 和 -1 可能会使AC变为0， 而行程编码之后， 除EOB和ZRL之外，不应该出现AC为0的情况
# 因此要求系数 not in (-1, 0, 1)
# 负数末位置0或置1，相当于其绝对值置0或置1，然后再加负号
def hideInfoInAC(info, midSignsTupleList, SKIP_COUNT, LEAST_LEN):

    # 将 info 和 info_length 逐位存入infoList
    info = str.encode(info)
    info_length = len(info)
    infoList = []
    for i in range(16):
        infoList.append((info_length >> (15 - i)) & 0x01)
    for char in info:
        for i in range(8):
            infoList.append((char >> (7 - i)) & 0x01)


    # tuple 是用来区分Y、Cb、Cr的，隐藏信息是无需考虑颜色分量
    # 去除 tuple，便于操作
    # 去除 tuple，得到包含所有 8x8 block 的 list
    signsList = list(itertools.chain(*midSignsTupleList))

    # 跳过加密信息位置计数
    # 可以选择每隔多少个位置（满足其他隐藏条件的位置）实际隐藏一位
    # 可以作为一个加密参数
    skip_count = SKIP_COUNT

    for iter_list in range(len(signsList)):
        # 从 1 开始，跳过 DC
        for iter_signs in range(1, len(signsList[iter_list])):

            zero_len = signsList[iter_list][iter_signs][0]
            val = signsList[iter_list][iter_signs][1]

            # LEAST作为一个筛选条件，表示只在二进制编码位数大于某个值的情况下
            # 才在该位置进行信息隐藏（配合SKIP_COUNT使用）
            if val not in (-1, 0, 1) and len(bin(abs(val))) - 2 >= LEAST_LEN:

                if skip_count != 0:
                    skip_count -= 1

                else:
                    skip_count = SKIP_COUNT

                    # 根据要隐藏的信息修改AC值
                    # print(val, end=', ')
                    val = hideInfoInVal(val, infoList[0])

                    signsList[iter_list][iter_signs] = (zero_len, val)
                    # print(val)

                    # 去掉刚才完成隐藏的那一位信息
                    # 并检查是否已经隐藏完毕
                    infoList = infoList[1:]
                    if len(infoList) == 0:
                        print("信息隐藏完毕")
                        return [(signsList[i * 3], signsList[i * 3 + 1], signsList[i * 3 + 2]) \
                                for i in range(len(signsList) // 3)]

    print("信息隐藏未完成")
    sys.exit(-1)


def img2jpegBinaryDataStringFile_Colorful(imname, txtname, info, SKIP_COUNT, LEAST_LEN):
    ycrcb = cv2.cvtColor(cv2.imread(imname), cv2.COLOR_BGR2YCR_CB)

    # 提取颜色通道
    yblocks, yh, yw = data2blocks(ycrcb[:, :, 0])
    crblocks, crh, crw = data2blocks(ycrcb[:, :, 1])
    cbblocks, cbh, cbw = data2blocks(ycrcb[:, :, 2])

    # 离散余弦变换 并 量化
    for i in range(len(yblocks)):
        yblocks[i] = quantifyBlock(yblocks[i], 'L')
    for i in range(len(cbblocks)):
        cbblocks[i] = quantifyBlock(cbblocks[i], 'C')
    for i in range(len(crblocks)):
        crblocks[i] = quantifyBlock(crblocks[i], 'C')

    # z字型排列
    yzigList = [zigzagOrder(blk) for blk in yblocks]
    cbzigList = [zigzagOrder(blk) for blk in cbblocks]
    crzigList = [zigzagOrder(blk) for blk in crblocks]

    # 差分 DC
    ydiffZigList = diffBlocksDC(yzigList)
    cbdiffZigList = diffBlocksDC(cbzigList)
    crdiffZigList = diffBlocksDC(crzigList)

    # 转中间符号
    midSignsTupleList = []
    for i in range(len(ydiffZigList)):
        midSignsTupleList.append((zigzag2midSigns(ydiffZigList[i]),
                                  zigzag2midSigns(cbdiffZigList[i]),
                                  zigzag2midSigns(crdiffZigList[i])))

    if info != None:
        print("hiding infomation...")
        midSignsTupleList = hideInfoInAC(info, midSignsTupleList, SKIP_COUNT, LEAST_LEN)

    global npmidsignlist
    npmidsignlist = np.array(midSignsTupleList)

    # 中间符号转2进制编码（0-1文本）
    binaryData = midSigns2binaryCode_Colorful(midSignsTupleList)

    # 填充为整数字节
    shouldFill = (len(binaryData) + 7) // 8 * 8 - len(binaryData)
    # print("should fill is", shouldFill)
    binaryData += '0' * shouldFill

    # bin str to file
    fout = open(txtname, 'w')
    fout.write(binaryData)
    fout.close()

    return ycrcb.shape

def main():

    PREFIX = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))+ "/"
    DIR_PATH = os.path.dirname(os.path.realpath(__file__)) + "/"
    lpy_encoder = DIR_PATH + "lpy-jpeg-encoder"
    jpeg_in_file = None
    jpeg_out_file = None
    info = None
    SKIP_COUNT = 0
    LEAST_LEN = 0

    if len(sys.argv) >= 6:
        LEAST_LEN = int(sys.argv[5])
    if len(sys.argv) >= 5:
        SKIP_COUNT = int(sys.argv[4])
    if len(sys.argv) >= 4:
        info = sys.argv[3]
    if len(sys.argv) >= 3:
        jpeg_out_file = sys.argv[2]
        jpeg_in_file = sys.argv[1]
    else:
        print("Usage: %s infile outfile [info] [skip] [min_len]" % sys.argv[0])
        sys.exit(-1)    
        

    with TemporaryDirectory() as TMPDIR:
        # lpy_encoder = "../cencoder/lpy_jpeg_encoder"
        huffman_txt = TMPDIR + "huffman.txt"
        huffman_bin = TMPDIR + "huffman.bin"
        jpeg_data_txt = TMPDIR + "jpeg-data.txt"
        jpeg_data_bin = TMPDIR + "jpeg-data.bin"
        jpeg_data_slash_bin = TMPDIR + "jpeg-data-slash.bin"

        # 哈夫曼表转换为0-1文件
        print("creating huffman txt file...")
        huffmanTable2BinaryDataStringFile(huffman_txt)
        # 图片数据转换为0-1文件
        print("creating jpeg image data txt file...")
        height, width, channel = img2jpegBinaryDataStringFile_Colorful(jpeg_in_file, jpeg_data_txt, info, SKIP_COUNT, LEAST_LEN)

        # 哈夫曼0-1文件转换为二进制文件
        print("creating huffman binary file...")
        os.system('%s %s %s %s' % (lpy_encoder, 't2b', huffman_txt, huffman_bin))
        # jpeg 0-1文件转换为二进制文件
        print("creating jpeg image data binary file...")
        os.system('%s %s %s %s' % (lpy_encoder, 't2b', jpeg_data_txt, jpeg_data_bin))
        # 对jpeg 二进制文件进行转义(0xFF后添加0x00)
        print("slashing jpeg image data binary file...")
        os.system('%s %s %s %s' % (lpy_encoder, 'slash', jpeg_data_bin, jpeg_data_slash_bin))
        # 生成jpeg图像
        print("generating jpeg image...")
        os.system('%s %s %s %s %s %s %s %s' % (
        lpy_encoder, 'cj', huffman_bin, jpeg_data_slash_bin, jpeg_out_file, width, height, channel))

        print("done!")

if __name__ == "__main__":
    main()
