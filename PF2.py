import math


class Box(object):
    def __init__(self):
        self.TimeStamp = None
        self.Mark = None


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


def Columns2(bsize, r, highs, lows, closes, timestamps):
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
        box = Box()
        box.Mark = "O"
        box.TimeStamp = timestamps[0]
        cols[0].Boxes.append(box)
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
                    box_i = Box()
                    box_i.Mark = "O"
                    box_i.TimeStamp = timestamps[i]
                    cols[n].Boxes.append(box_i)
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
                    box_i = Box()
                    box_i.Mark = "X"
                    box_i.TimeStamp = timestamps[i]
                    cols[n].Boxes.append(box_i)
        else:
            if (highs[i] > cols[n].CurrentBox):
                bn = abs(int(round((highs[i] - highs[i - 1]) / bsize)))
                for k in range(0, bn):
                    box_i = Box()
                    box_i.Mark = "X"
                    box_i.TimeStamp = timestamps[i]
                    cols[n].Boxes.append(box_i)
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
                    box_i = Box()
                    box_i.Mark = "O"
                    box_i.TimeStamp = timestamps[i]
                    cols[n].Boxes.append(box_i)
    return cols
