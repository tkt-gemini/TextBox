import pyperclip, pygame as pg

class Label:
    def __init__(self, fontName:str, txtSize:int, color = "black") -> None:
        self._text = ""
        self._txtColor = pg.Color(color)
        self.font = pg.font.Font(pg.font.match_font(fontName) if fontName.lower() in pg.font.get_fonts() else fontName, txtSize)

        self.txtSurf = self.font.render(self._text, True, self.txtColor)
        self.box = pg.Surface((self.txtSurf.get_width(), self.getSize()[1]), pg.SRCALPHA)

    def getSize(self, txt = ""):
        return (self.font.size(txt)[0], self.font.get_linesize())

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, v):
        self._text = v
        self.txtSurf = self.font.render(self._text, True, self.txtColor)
        self.box = pg.Surface((self.txtSurf.get_width(), self.getSize()[1]), pg.SRCALPHA)

    @property
    def txtColor(self):
        return self._txtColor.r, self._txtColor.b, self._txtColor.g

    @property
    def surface(self):
        self.box.blit(self.txtSurf, self.txtSurf.get_rect(bottomleft = self.box.get_rect().bottomleft))
        return self.box

class TextBox:
    doc = ""
    cursorPos = 0
    linePos = 0
    docLineBreak = ""
    lstTxtLineBreak = []
    lstCursorPos:list[tuple[int, int]] = [(0, 0)]
    lstCursorLineBreak:dict[int, tuple[int, int]] = {0: (0, 0)}
    timeDelayCursor = 500
    stateBox = False
    stateCursor = False

    def __init__(self, sizeBox:tuple[int, int], initial:str = "", border:int = 10):
        self.initial = initial
        self.borderBox = pg.Surface(sizeBox).convert_alpha()
        self.textBox = pg.Surface(tuple(s - border for s in sizeBox)).convert_alpha()
        self.label = Label("consolas", 14)
        self.sizeCursor = (1, self.label.getSize()[1])
        self.lastTime = pg.time.get_ticks()

    def hiddenCursor(self):
        if pg.time.get_ticks() - self.lastTime >= self.timeDelayCursor:
            self.stateCursor = False if self.stateCursor and True not in pg.key.get_pressed() else True
            self.lastTime = pg.time.get_ticks()

    def setCursorLineBreak(self):
        line = 0
        self.lstCursorPos = [(0, 0)]
        self.lstCursorLineBreak = {0: (0, 0)}
        for txt in self.lstTxtLineBreak:
            if txt in ["\n", "\ns", "\nt"]:
                if txt == "\nt": del self.lstCursorPos[-1]
                line += 1
                self.lstCursorPos.append((0, self.lstCursorPos[-1][1] + self.label.getSize()[1]))
                self.lstCursorLineBreak.update({line: (0, self.lstCursorPos[-1][1] + self.label.getSize()[1])})
            else:
                self.lstCursorPos.append((self.lstCursorPos[-1][0] + self.label.getSize(txt)[0], self.lstCursorPos[-1][1]))
                self.lstCursorLineBreak[line] = self.lstCursorPos[-1]
        
        self.linePos = self.lstCursorPos[self.cursorPos][1]

    def setLineBreak(self):
        self.docLineBreak = ""
        self.lstTxtLineBreak = []

        for txt in self.doc:
            splitLine = (self.docLineBreak + txt).splitlines()
            if self.label.getSize(splitLine[-1])[0] >= self.textBox.get_width():
                _split = splitLine[-1].split()
                if len(_split) == 1:
                    self.docLineBreak += f"\n{txt}"
                    self.lstTxtLineBreak += ["\nt", txt]
                else:
                    self.docLineBreak = f"{self.docLineBreak[:-len(_split[-1])]}\n{_split[-1]}"
                    self.lstTxtLineBreak = self.lstTxtLineBreak[:-len(_split[-1])] + ["\ns"] + [t for t in _split[-1]]
            else:
                self.docLineBreak += txt
                self.lstTxtLineBreak += [txt]

        self.setCursorLineBreak()

    def event(self, event):
        if self.stateBox:
            pg.key.set_repeat(500, 25)
            if event.type == pg.KEYDOWN:
                self.processKey(event.key)
                self.stateCursor = True
            elif event.type == pg.TEXTINPUT:
                self.handleTextinput(event.text)
                self.setLineBreak()
            else:
                self.stateCursor = False
        else: pg.key.set_repeat()

    def handleTextinput(self, text:str):
        self.doc = self.doc[:self.cursorPos] + text + self.doc[self.cursorPos:]
        self.cursorPos += len(text)

    def processKey(self, key:int):
        mod = pg.key.get_mods()
        K_name = f"_processK{pg.key.name(key).capitalize()}"
        CtrlK_name = f"_processKMCtrl_{pg.key.name(key).capitalize()}"
        TextK_name = f"_processKT{pg.key.name(key).capitalize()}"

        if hasattr(self, K_name):
            getattr(self, K_name)()
        elif hasattr(self, TextK_name):
            getattr(self, TextK_name)()
            self.setLineBreak()
        elif (mod & pg.KMOD_CTRL) and hasattr(self, CtrlK_name):
            getattr(self, CtrlK_name)()
            self.setLineBreak()

    def _processKUp(self):
        if self.linePos > 0:
            self.linePos -= self.label.getSize()[1]
            try:
                self.cursorPos = self.lstCursorPos.index((self.lstCursorPos[self.cursorPos][0], self.linePos))
            except ValueError:
                self.cursorPos = self.lstCursorPos.index(self.lstCursorLineBreak[self.linePos//self.label.getSize()[1]])

    def _processKDown(self):
        if self.linePos < self.lstCursorPos[-1][1]:
            self.linePos += self.label.getSize()[1]
            try:
                self.cursorPos = self.lstCursorPos.index((self.lstCursorPos[self.cursorPos][0], self.linePos))
            except ValueError:
                self.cursorPos = self.lstCursorPos.index(self.lstCursorLineBreak[self.linePos//self.label.getSize()[1]])

    def _processKRight(self):
        self.cursorPos = min(self.cursorPos + 1, len(self.doc))

    def _processKLeft(self):
        self.cursorPos = max(0, self.cursorPos - 1)

    def _processKTReturn(self):
        self.handleTextinput("\n")

    def _processKTBackspace(self):
        if self.cursorPos > 0:
            self.doc = self.doc[:self.cursorPos - 1] + self.doc[self.cursorPos:]
            self.cursorPos -= 1

    def _processKTDelete(self):
        if self.cursorPos < len(self.doc):
            self.doc = self.doc[:self.cursorPos] + self.doc[self.cursorPos + 1:]

    def _processKMCtrl_V(self):
        self.handleTextinput(pyperclip.paste())

    @property
    def surface(self) -> pg.Surface:
        self.borderBox.fill(self.textBoxColor)
        self.textBox.fill(self.textBoxColor)
        self.hiddenCursor()

        if self.doc == "": self.docLineBreak = self.initial
        for i, txt in enumerate(self.docLineBreak.splitlines()):
            self.label.text = txt
            self.textBox.blit(self.label.surface, (0, self.label.getSize()[1]*i))

        pg.draw.rect(self.textBox, self.label.txtColor, (self.lstCursorPos[self.cursorPos], (self.sizeCursor))) if self.stateCursor else None
        self.borderBox.blit(self.textBox, self.textBox.get_rect(center = self.borderBox.get_rect().center))
        return self.borderBox

    @property
    def textBoxColor(self):
        return tuple(255 - c for c in self.label.txtColor)
