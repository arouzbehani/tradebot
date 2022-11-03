import math


class Box(object):
    def __init__(self):
        self._TimeStamp = None
        self._Mark = None
        self._Index = None
        self._Price = None

    @property
    def TimeStamp(self):
        return self._TimeStamp

    @TimeStamp.setter
    def TimeStamp(self, value):
        self._TimeStamp = value

    @property
    def Mark(self):
        return self._Mark

    @Mark.setter
    def Mark(self, value):
        self._Mark = value

    @property
    def Index(self):
        return self._Index

    @Index.setter
    def Index(self, value):
        self._Index = value

    @property
    def Price(self):
        return self._Price

    @Price.setter
    def Price(self, value):
        self._Price = value


class Col(object):
    def __init__(self):
        self._Type = None
        self._Max = None
        self._Min = None
        self._High = None
        self._Low = None
        self._CurrentBox = None
        self._Boxes = None
        self._Close = None

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, value):
        self._Type = value

    @property
    def Close(self):
        return self._Close

    @Close.setter
    def Close(self, value):
        self._Close = value

    @property
    def High(self):
        return self._High

    @High.setter
    def High(self, value):
        self._High = value

    @property
    def Low(self):
        return self._Low

    @Low.setter
    def Low(self, value):
        self._Low = value

    @property
    def Max(self):
        return self._Max

    @Max.setter
    def Max(self, value):
        self._Max = value

    @property
    def Min(self):
        return self._Min

    @Min.setter
    def Min(self, value):
        self._Min = value

    @property
    def CurrentBox(self):
        return self._CurrentBox

    @CurrentBox.setter
    def CurrentBox(self, value):
        self._CurrentBox = value

    @property
    def Boxes(self):
        return self._Boxes

    @Boxes.setter
    def Boxes(self, value):
        self._Boxes = value


def GetBox(num, bsize, high):
    i = int(math.trunc(num))
    bn = int(math.trunc((((num - i)) / bsize)))
    if high:
        return (i + (bn * bsize))
    else:
        return (i + (((bn + 1)) * bsize))


def Columns(bsize, r, highs, lows, closes):
    cols = []

    col0 = Col()
    col0.Max = highs[0]
    col0.Min = lows[0]
    col0.High = highs[0]
    col0.Low = lows[0]
    col0.Close = closes[0]

    col0.Type = "O"
    cols.append(col0)
    bn = int(round((((highs[0] - lows[0])) / bsize)))
    cols[0].Boxes = []
    for x in range(0, bn):
        cols[0].Boxes.append("O")
    cols[0].CurrentBox = GetBox(lows[0], bsize, False)
    n = 0
    for i in range(0, len(highs)):
        cols[n].High = highs[i]
        cols[n].Low = lows[i]
        cols[n].Close = closes[i]
        if (cols[n].Type == "O"):
            if (lows[i] < cols[n].CurrentBox):
                bn = abs(int(round((lows[i] - lows[i - 1]) / bsize)))
                for k in range(0, bn):
                    cols[n].Boxes.append("O")
                cols[n].Min = lows[i]
                cols[n].CurrentBox = GetBox(lows[i], bsize, False)
            elif (highs[i] > cols[n].CurrentBox + r * bsize):
                c = Col()
                c.High = highs[i]
                c.Close = closes[i]
                c.Low = lows[i]
                c.Min = cols[n].CurrentBox + 1
                c.Max = cols[n].CurrentBox + r * bsize
                c.CurrentBox = cols[n].CurrentBox+r*bsize
                c.Type = "X"
                cols.append(c)
                n = (n+1)
                cols[n].Boxes = []
                for k in range(0, r):
                    cols[n].Boxes.append("X")
        else:
            if (highs[i] > cols[n].CurrentBox):
                bn = abs(int(round((highs[i] - highs[i - 1]) / bsize)))
                for k in range(0, bn):
                    cols[n].Boxes.append("X")
                cols[n].Max = highs[i]
                cols[n].CurrentBox = GetBox(highs[i], bsize, True)
            elif (lows[i] < cols[n].CurrentBox - r * bsize):
                c = Col()
                c.High = highs[i]
                c.Close = closes[i]
                c.Low = lows[i]
                c.Max = cols[n].CurrentBox + 1
                c.Min = cols[n].CurrentBox - r * bsize
                c.CurrentBox = cols[n].CurrentBox - r * bsize
                c.Type = "O"
                cols.append(c)
                n = (n+1)
                cols[n].Boxes = []
                for k in range(0, r):
                    cols[n].Boxes.append("O")
    return cols


def ColumnsV2(bsize, r, highs, lows, closes):
    cols = []

    col0 = Col()
    col0.Max = highs[0]
    col0.Min = lows[0]
    col0.High = highs[0]
    col0.Low = lows[0]
    col0.Close = closes[0]

    col0.Type = "O"
    cols.append(col0)
    bn = int(round((((highs[0] - lows[0])) / bsize)))
    cols[0].Boxes = []
    cols[0].CurrentBox = GetBox(lows[0], bsize, False)
    for x in range(0, bn):
        b = Box()
        b.Mark = "O"
        b.Index = 0
        b.Price = cols[0].CurrentBox + x*bsize
        cols[0].Boxes.append(b)
    n = 0
    for i in range(1, len(highs)):
        cols[n].High = highs[i]
        cols[n].Low = lows[i]
        cols[n].Close = closes[i]
        if (cols[n].Type == "O"):
            if (lows[i] < cols[n].CurrentBox):
                bn = abs(int(round((lows[i] - lows[i - 1]) / bsize)))
                cols[n].Min = lows[i]
                cols[n].CurrentBox= GetBox(lows[i], bsize, False)
                for k in range(0, bn):
                    b = Box()
                    b.Mark = "O"
                    b.Index = i
                    b.Price=cols[n].CurrentBox+k*bsize
                    cols[n].Boxes.append(b)
            elif (highs[i] > cols[n].CurrentBox + r * bsize):
                c = Col()
                c.High = highs[i]
                c.Close = closes[i]
                c.Low = lows[i]
                c.Min = cols[n].CurrentBox + 1
                c.Max = cols[n].CurrentBox + r * bsize
                c.CurrentBox = cols[n].CurrentBox+r*bsize
                c.Type = "X"
                cols.append(c)
                n = (n+1)
                cols[n].Boxes = []
                for k in range(0, r):
                    b = Box()
                    b.Mark = "X"
                    b.Index = i
                    b.Price=cols[n].CurrentBox-k*bsize
                    cols[n].Boxes.append(b)
        else:
            if (highs[i] > cols[n].CurrentBox):
                bn = abs(int(round((highs[i] - highs[i - 1]) / bsize)))
                for k in range(0, bn):
                    b = Box()
                    b.Mark = "X"
                    b.Index = i
                    b.Price=cols[n].CurrentBox-k*bsize
                    cols[n].Boxes.append(b)
                cols[n].Max = highs[i]
                cols[n].CurrentBox = GetBox(highs[i], bsize, True)
            elif (lows[i] < cols[n].CurrentBox - r * bsize):
                c = Col()
                c.High = highs[i]
                c.Close = closes[i]
                c.Low = lows[i]
                c.Max = cols[n].CurrentBox + 1
                c.Min = cols[n].CurrentBox - r * bsize
                c.CurrentBox = cols[n].CurrentBox - r * bsize
                c.Type = "O"
                cols.append(c)
                n = (n+1)
                cols[n].Boxes = []
                for k in range(0, r):
                    b = Box()
                    b.Mark = "O"
                    b.Index = i
                    b.Price=cols[n].CurrentBox+k*bsize
                    cols[n].Boxes.append(b)
    return cols
