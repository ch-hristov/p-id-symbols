from typing import List
from PIL import Image


class VisualObject:
    def __init__(self, start_xy: List[float], end_xy: List[float]):
        self.start_xy = start_xy
        self.end_xy = end_xy

    def get_category(self):
        pass

    def get_label(self):
        pass


class OtherLine:
    def __init__(self, start_xy: List[float], end_xy: List[float], isOne: int):
        self.start_xy = start_xy
        self.end_xy = end_xy
        self.isOne = isOne


class Table:
    def __init__(self):
        self.lines = []


class Word(VisualObject):
    def __init__(self, word_id: str, start_xy: List[int], end_xy: List[int], text: str, value: int):
        VisualObject.__init__(self, start_xy, end_xy)
        self.word_id = word_id
        self.text = text
        self.value = value

    def __repr__(self) -> str:
        return str(self.word_id)


class Link:
    def __init__(self, source: str, items: List[str]):
        self.source = source
        self.targets = items


class PID:

    def get_word_crop_by_index(self, i):
        img = Image.open(self.path)
        word = self.words[i]

        x, y = word.start_xy
        x1, y1 = word.end_xy

        crop_target = min(x, x1), min(y, y1), max(x, x1) + 1, max(y, y1)+1

        output = img.crop(crop_target)

        return output

    def get_symbol_crop_by_index(self, i):
        img = Image.open(self.path)
        symbol = self.symbols[i]

        x, y = symbol.start_xy
        x1, y1 = symbol.end_xy

        crop_target = min(x, x1), min(y, y1), max(x, x1) + 1, max(y, y1)+1

        output = img.crop(crop_target)

        return output

    def get_line_crop_by_id(self, idx):
        img = Image.open(self.path)
        symbol = [ops for ops in self.lines if ops.line_id == idx]

        x, y = symbol[0].start_xy
        x1, y1 = symbol[0].end_xy

        crop_target = min(x, x1), min(y, y1), max(x, x1) + 1, max(y, y1)+1
        output = img.crop(crop_target)

        return output

    def get_symbol_crop_by_id(self, idx):
        img = Image.open(self.path)
        symbol = [ops for ops in self.symbols if ops.symbol_id == idx]

        x, y = symbol[0].start_xy
        x1, y1 = symbol[0].end_xy

        crop_target = min(x, x1), min(y, y1), max(x, x1) + 1, max(y, y1)+1
        output = img.crop(crop_target)

        return output

    def get_line_crop_by_index(self, i):
        img = Image.open(self.path)
        line = self.lines[i]

        x, y = line.start_xy
        x1, y1 = line.end_xy

        crop_target = (min(x, x1), min(y, y1), max(x, x1) + 1, max(y, y1)+1)

        output = img.crop(crop_target)
        return output

    def __init__(self):
        self.symbols: List[Symbol] = []
        self.lines: List[Line] = []
        self.words: List[Word] = []
        self.table: Table = []
        self.links = []
        self.details = []
        self.otherLines = []
        self.path = ''
        self.id = ''
        self.width = -1
        self.height = -1

    def __repr__(self) -> str:
        return 'Symbols: {0}, Lines: {1}, Words: {2}, Table: {3}'.format(len(self.symbols),
                                                                         len(self.lines),
                                                                         len(self.words),
                                                                         len(self.table))


class Symbol(VisualObject):
    def __init__(self, symbol_id: str, rect_start_xy: List[int], rect_end_xy: List[int], label: str, pid: PID):
        VisualObject.__init__(self, rect_start_xy, rect_end_xy)
        self.symbol_id = symbol_id
        self.label = label
        self.pid = pid

    def __repr__(self) -> str:
        return str(self.symbol_id)

    def get_category(self):
        return self.label

    def get_label(self):
        return self.label


class Line(VisualObject):
    def __init__(self, line_id: str, start_xy: List[float], end_xy: List[float], tag: str, types: str, pid: PID):
        VisualObject.__init__(self, start_xy, end_xy)
        self.line_id = line_id
        self.types = types
        self.tag = tag
        self.pid = pid

    def __repr__(self) -> str:
        return str(self.line_id)

    def get_category(self):
        return self.types

    def get_label(self):
        if self.types == 'solid':
            return 0
        if self.types == 'dashed':
            return 1
        return 2
