from jpeg import *
import os
import itertools
import sys
from tempfile import TemporaryDirectory

npmidsignlist = []

def showalways(img, title="Window Name"):
    """
    显示图片
    :param img: img
    :param title: title
    :return:
    """
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def testSampleAndDct():
    """
    测试子采样并量化一个图片后再逆量化并恢复图像
    :return:
    """
    rgb = cv2.imread('./Pictures/Koala.bmp')
    ycrcb = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB)

    y, cr, cb = ycrcb2sample(ycrcb)
    yblocks, yh, yw = data2blocks(y)
    crblocks, crh, crw = data2blocks(cr)
    cbblocks, cbh, cbw = data2blocks(cb)

    tyblocks = yblocks[:]
    for i in range(len(yblocks)):
        tyblocks[i] = quantifyBlock(yblocks[i], 'L')
        tyblocks[i] = inverseQuantifyBlock(tyblocks[i], 'L')
    newy = blocks2data(tyblocks, yh, yw)

    tcrblocks = crblocks[:]
    for i in range(len(crblocks)):
        tcrblocks[i] = quantifyBlock(crblocks[i], 'C')
        tcrblocks[i] = inverseQuantifyBlock(tcrblocks[i], 'C')
    newcr = blocks2data(tcrblocks, crh, crw)

    tcbblocks = cbblocks[:]
    for i in range(len(cbblocks)):
        tcbblocks[i] = quantifyBlock(cbblocks[i], 'C')
        tcbblocks[i] = inverseQuantifyBlock(tcbblocks[i], 'C')
    newcb = blocks2data(tcbblocks, cbh, cbw)

    showalways(y)
    showalways(newy)

    newycrcb = sample2ycrcb(newy, newcr, newcb)
    showalways(newycrcb)
    newrgb = cv2.cvtColor(newycrcb, cv2.COLOR_YCR_CB2RGB)
    showalways(newrgb)


def img2jpegBinaryDataStringFile_Gray(outfile):
    rgb = cv2.imread(outfile)
    ycrcb = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB)

    # 之前考虑了采样
    # y, cr, cb = ycrcb2sample(ycrcb)
    yblocks, yh, yw = data2blocks(ycrcb[:, :, 0])
    tyblocks = yblocks[:]
    for i in range(len(yblocks)):
        tyblocks[i] = quantifyBlock(yblocks[i], 'L')

    zigList = [zigzagOrder(blk) for blk in tyblocks]
    # npzigList = np.array(zigList)

    # 差分 DC
    diffZigList = diffBlocksDC(zigList)
    # npdiffzigList = np.array(diffZigList)

    midSignsList = []
    for zigblock in diffZigList:
        midSignsList.append(zigzag2midSigns(zigblock))

    binaryData = midSigns2binaryCode(midSignsList, 'L')

    shouldFill = (len(binaryData) + 7) // 8 * 8 - len(binaryData)
    print("should fill is", shouldFill)
    binaryData += '0' * shouldFill

    # bin str to file
    fout = open("files/jpeg-data-binary-string.txt", 'w')
    fout.write(binaryData)
    fout.close()


def huffmanTable2BinaryDataStringFile(outfile):
    binaryData = huffmanTable2BinaryData(LuminanceDCCoefficientDifferencesTable,
                                         ChrominanceDCCoefficientDifferencesTable,
                                         acLuminanceTable, acChrominanceTable)
    # fout = open("files/jpeg-huffman-binary-string.txt", 'w')
    fout = open(outfile, 'w')
    fout.write(binaryData)
    fout.close()


npsignsList = []
npsignsList2 = []


def hideInfoInAC(info, midSignsTupleList, SKIP_COUNT, LEAST_LEN):
    info = str.encode(info)
    info_length = len(info)
    infoList = []
    for i in range(16):
        infoList.append((info_length >> (15 - i)) & 0x01)
    for char in info:
        for i in range(8):
            infoList.append((char >> (7 - i)) & 0x01)

    signsList = list(itertools.chain(*midSignsTupleList))
    global npsignsList, npsignsList2
    npsignsList = np.array(signsList)

    skip_count = SKIP_COUNT

    for iter_list in range(len(signsList)):
        for iter_signs in range(1, len(signsList[iter_list])):

            zero_len = signsList[iter_list][iter_signs][0]
            val = signsList[iter_list][iter_signs][1]

            if val != 0 and val != 1 and len(bin(abs(val))) - 2 >= LEAST_LEN and val > 0:

                if skip_count != 0:
                    skip_count -= 1

                else:
                    skip_count = SKIP_COUNT

                    print(val, end=', ')

                    if infoList[0] & 0x01 == 0:
                        val &= 0b1111_1110
                    else:
                        val |= 0b0000_0001

                    signsList[iter_list][iter_signs] = (zero_len, val)

                    print(val)

                    infoList = infoList[1:]
                    if len(infoList) == 0:
                        print("信息隐藏完毕")
                        npsignsList2 = np.array(signsList)
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

    midSignsTupleList = []
    for i in range(len(ydiffZigList)):
        midSignsTupleList.append((zigzag2midSigns(ydiffZigList[i]),
                                  zigzag2midSigns(cbdiffZigList[i]),
                                  zigzag2midSigns(crdiffZigList[i])))

    if info != None:
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


import sys
import os.path

def main():

    PREFIX = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))+ "/"
    lpy_encoder = PREFIX + "cencoder/lpy_jpeg_encoder"
    jpeg_in_file = "../Pictures/squirrel.jpg"
    jpeg_out_file = "../Pictures/lpy-jpeg.jpeg"
    info = None
    SKIP_COUNT = 0
    LEAST_LEN = 0

    if len(sys.argv) not in (3, 4, 5, 6, 7):
        print("Usage: %s infile outfile [info] [skip] [min_len]" % sys.argv[0])
        sys.exit(-1)
    elif len(sys.argv) == 3:
        jpeg_in_file = sys.argv[1]
        jpeg_out_file = sys.argv[2]
    elif len(sys.argv) == 4:
        jpeg_in_file = sys.argv[1]
        jpeg_out_file = sys.argv[2]
        info = sys.argv[3]
    elif len(sys.argv) == 5:
        jpeg_in_file = sys.argv[1]
        jpeg_out_file = sys.argv[2]
        info = sys.argv[3]
        SKIP_COUNT = int(sys.argv[4])
    elif len(sys.argv) == 6:
        jpeg_in_file = sys.argv[1]
        jpeg_out_file = sys.argv[2]
        info = sys.argv[3]
        SKIP_COUNT = int(sys.argv[4])
        LEAST_LEN = int(sys.argv[5])

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
