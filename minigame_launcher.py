#!/usr/bin/python
import sys
import os
import time
import subprocess
from PyQt4 import QtCore
from PyQt4 import QtGui
from playsound import playsound

from minigame import update_game

class MinigameView(QtGui.QWidget):
    def __init__(self):
        super(MinigameView, self).__init__()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateCtx)
        self.timer.start(100)
        self.lastTime = self.getCurrentTime()
        self.ctx = {
            "assets": []
        }
        self._leftMouseButtonDown = False

        #self.playSound("piano-c")

        self.updateCtx()

    def playSound(self, soundFile):
        soundsDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../sounds")
        soundFilePath = os.path.join(soundsDir, soundFile + ".wav")

        self.player = subprocess.Popen(["mplayer", soundFilePath], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def updateCtx(self):
        currentTime = self.getCurrentTime()
        elapsed = currentTime - self.lastTime

        windowSize = float(min(self.width(), self.height()))
        mousePos = self.mapFromGlobal(QtGui.QCursor.pos())

        self.ctx["elapsed"] = elapsed
        self.ctx["mousePos"] = (mousePos.x() / windowSize, mousePos.y() / windowSize)
        self.ctx["mouseDown"] = self._leftMouseButtonDown

        update_game(self.ctx)

        if "sound" in self.ctx:
            self.playSound(self.ctx["sound"])
            self.ctx.pop("sound")

        self.lastTime = currentTime

        # redraw scene
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)

        painter.fillRect(0, 0, self.width(), self.height(), QtGui.QColor(20,20,20))

        windowSize = min(self.width(), self.height())

        for asset in self.ctx["assets"]:
            if asset["type"] == "rectangle":
                width,height = asset["size"]
                x,y = asset["position"]
                color = asset["color"]

                painter.fillRect(x * windowSize,
                                 y * windowSize,
                                 width * windowSize,
                                 height * windowSize,
                                 QtGui.QColor.fromRgbF(color[0], color[1], color[2]))

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._leftMouseButtonDown = True

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._leftMouseButtonDown = False

    def getCurrentTime(self):
        return int(round(time.time() * 1000))

def main():
    app = QtGui.QApplication(sys.argv)

    w = MinigameView()
    w.resize(800, 800)
    w.move(400, 200)
    w.setWindowTitle('Minigame Launcher')
    w.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
