import sys
import random
import time

def point_contains_rect(mousePos, rect):
    mouseX, mouseY = mousePos
    rectX, rectY = rect["position"]
    rectWidth, rectHeight = rect["size"]
    return rectX < mouseX and rectY < mouseY and mouseX < rectX + rectWidth and mouseY < rectY + rectHeight

def scale_color(color, scale):
    return tuple(map(lambda channel: min(channel * scale, 1), color))

def get_pattern(count):
    pattern = []
    for i in range(count):
        pattern.append(random.randint(0,3))
    print pattern
    return pattern

class Minigame(object):
    def update(self, ctx):
        status = ctx["status"]

        if "state" not in ctx: # initialize game
            ctx["state"] = {
                "pattern" : get_pattern(3),
                "clicks" : [],
                "lastColorIndexToDemo" : None
            }

        unit = 1 / 7.0

        playing = status == "playing"
        if playing:
            patternElapsed = ctx["currentTime"] - ctx["startTime"]
            demoingIndex = patternElapsed / 1000
        demoing = playing and demoingIndex < len(ctx["state"]["pattern"])
        if demoing: # figure out which color to play
            colorIndexToDemo = ctx["state"]["pattern"][demoingIndex]
            highlightDemoColor = patternElapsed - demoingIndex * 1000 < 800

        assets = []
        colors = [(1,1,0), (1,0,1), (1,0,0), (0,1,1)]
        possibleSounds = ["piano-bb", "piano-c", "piano-eb", "piano-g"]
        possibleSound = None
        possibleIndex = None
        for i in range(4):
            row = i / 2
            column = i % 2

            rect = {
                "type" : "rectangle",
                "position" : [unit+unit*3*column, unit+unit*3*row],
                "size" : [unit*2, unit*2]
            }


            # figure out the color
            if not playing: # no user input or demoing yet
                rect["color"] = scale_color(colors[i], 0.4)
            elif point_contains_rect(ctx["mousePos"], rect) and not demoing:
                rect["color"] = colors[i]
                possibleSound = possibleSounds[i]
                possibleIndex = i
            elif demoing and i == colorIndexToDemo:
                if highlightDemoColor:
                    rect["color"] = colors[i]
                else:
                    rect["color"] = scale_color(colors[i], 0.4)
                possibleSound = possibleSounds[i]
            else:
                rect["color"] = scale_color(colors[i], 0.4)
            assets.append(rect)
        ctx["assets"] = assets

        if demoing and colorIndexToDemo != ctx["state"]["lastColorIndexToDemo"] and playing:
            ctx["sound"] = possibleSound
            ctx["state"]["lastColorIndexToDemo"] = colorIndexToDemo

        if ctx["mousePress"] and not demoing and playing: # press
            if possibleSound is not None and possibleIndex is not None:
                ctx["sound"] = possibleSound
                ctx["state"]["clicks"].append(possibleIndex)

                fail = False
                for i,clickIndex in enumerate(ctx["state"]["clicks"]):
                    if clickIndex != ctx["state"]["pattern"][i]:
                        fail = True
                if fail:
                    ctx["status"] = "failure"
                elif len(ctx["state"]["pattern"]) == len(ctx["state"]["clicks"]):
                    ctx["status"] = "success"
