from pysrc.jpeg import *


def showalways(img, title = "Window Name"):
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

def img2jpegBinaryDataStringFile(fname):
    rgb = cv2.imread(fname)
    ycrcb = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB)

    # y, cr, cb = ycrcb2sample(ycrcb)
    yblocks, yh, yw = data2blocks(ycrcb[:,:,0])
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

    # npMidSignsList = np.array(midSignsList)
    binaryData = midSigns2binaryCode(midSignsList, 'L')

    shouldFill = (len(binaryData)+7)//8 * 8 - len(binaryData)
    print("should fill is", shouldFill)
    binaryData += '0'*shouldFill

    # bin str to file
    fout = open("files/jpeg-data-binary-string.txt", 'w')
    fout.write(binaryData)
    fout.close()

def huffmanTable2BinaryDataStringFile():
    binaryData = huffmanTable2BinaryData(LuminanceDCCoefficientDifferencesTable, ChrominanceDCCoefficientDifferencesTable,
                            acLuminanceTable, acChrominanceTable)
    fout = open("files/jpeg-huffman-binary-string.txt", 'w')
    fout.write(binaryData)
    fout.close()

def img2jpegBinaryDataStringFile_Colorful(fname):
    ycrcb = cv2.cvtColor(cv2.imread(fname), cv2.COLOR_BGR2YCR_CB)

    # 提取颜色通道
    yblocks, yh, yw = data2blocks(ycrcb[:,:,0])
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

    # 中间符号转2进制编码（0-1文本）
    binaryData = midSigns2binaryCode_Colorful(midSignsTupleList)

    # 填充为整数字节
    shouldFill = (len(binaryData)+7)//8 * 8 - len(binaryData)
    print("should fill is", shouldFill)
    binaryData += '0'*shouldFill

    # bin str to file
    fout = open("files/jpeg-data-binary-string.txt", 'w')
    fout.write(binaryData)
    fout.close()

def main():
    img2jpegBinaryDataStringFile_Colorful("Pictures/squirrel.jpg")

if __name__ == "__main__":
    main()