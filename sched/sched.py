import calendar
import datetime
import curses
import curses.textpad
import json
import signal
import os
import pathlib
import sys
import ced
import subprocess

editors = ["TEXTPAD", "CED", "VIM"]
editor = editors[0]

_path = pathlib.Path(sys.argv[0]).parent.resolve()
filePrefix = str(_path) + "/data/"

try:
    os.mkdir(filePrefix)
except FileExistsError:
    pass


def handler_SIGINT(signum, frame):
    return

signal.signal(signal.SIGINT, handler_SIGINT)

cal = calendar.Calendar(calendar.SUNDAY)
dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def calGetMonth(year, month):
    #list of list of day numbers, max day
    return [cal.monthdayscalendar(year, month), calendar.monthrange(year, month)[1]]

_today = datetime.date.today()
cursorDate = None
monthDays = None
monthSize = None
monthWidth = None
monthHeight = None
cursorPos = None

def goDate(year, month, day = 1):
    global cursorDate, monthDays, monthSize, monthWidth, monthHeight, cursorPos
    cursorDate = [year, month, day]
    monthDays, monthSize = calGetMonth(cursorDate[0], cursorDate[1])
    monthWidth = len(monthDays[0])
    monthHeight = len(monthDays)

    cursorPos = None

    for y in range(monthHeight):
        if cursorPos:
            break
        for x in range(monthWidth):
            if monthDays[y][x] == cursorDate[2]:
                cursorPos = [y, x]
                break

goDate(_today.year, _today.month, _today.day)

def loadMonth(year, month):
    fileName = f"{filePrefix}{year}-{month}.json"
    try:
        f = open(fileName, "r")

        lines = ""
        for line in f:
            lines += line

        data = json.loads(lines)
        
        f.close()

        return data
    except FileNotFoundError:
        _, maxDay = calGetMonth(year, month)
        return {"content": ["" for i in range(maxDay)]}

def saveMonth(data, year, month):
    fileName = f"{filePrefix}{year}-{month}.json"

    try:
        empty = True
        for text in data["content"]:
            if text != "":
                empty = False
                break

        if not empty:
            f = open(fileName, "w")
            f.write(json.dumps(data))
            f.close()
        else:
            os.remove(fileName)

        return True
    except Exception:
        return False

monthData = loadMonth(cursorDate[0], cursorDate[1])

def drawCalendar(scr):
    curses.curs_set(0)

    height, width = scr.getmaxyx()

    vSeparators = 6
    hSeparators = monthHeight


    cellWidths = [round((width - vSeparators) / 7) for i in range(7)]
    while sum(cellWidths) + vSeparators > width:
        best = cellWidths[0]
        bestIdx = 0
        for i in range(len(cellWidths)):
            if cellWidths[i] >= best:
                best = cellWidths[i]
                bestIdx = i
        cellWidths[bestIdx] -= 1

    cellHeights = [round((height - hSeparators - 1) / monthHeight) for i in range(monthHeight)]
    while sum(cellHeights) + hSeparators + 1 > height:
        best = cellHeights[0]
        bestIdx = 0
        for i in range(len(cellHeights)):
            if cellHeights[i] >= best:
                best = cellHeights[i]
                bestIdx = i
        cellHeights[bestIdx] -= 1

    tasks = []
    for d in range(1, monthSize + 1):
        ts = []
        text = monthData["content"][d - 1]
        for t in text.split("\n"):
            ts.append(t)
        tasks.append(ts)


    #Draw day line
    days = dayNames
    for i in range(len(days)):
        day = days[i]
        y = 0
        x = i + sum(cellWidths[0 : i])
        scr.addstr(y, x, day + " " * (cellWidths[i] - 1))

    #Draw grid
    #Draw H separators
    for i in range(hSeparators):
        y = 1 + i + sum(cellHeights[0 : i])
        scr.addstr(y, 0, " " * width, curses.color_pair(1))

    #Draw V separators
    for i in range(vSeparators):
        x = i + sum(cellWidths[0 : i + 1])
        for y in range(height):
            scr.addstr(y, x, " ", curses.color_pair(1))

    #Draw cells
    for wy in range(len(monthDays)):
        for wx in range(len(monthDays[wy])):
            cellWidth = cellWidths[wx]
            cellHeight = cellHeights[wy]

            sx = wx + sum(cellWidths[0 : wx])
            sy = 2 + wy + sum(cellHeights[0 : wy])

            #Draw number
            dayNumber = monthDays[wy][wx]

            if dayNumber == 0:
                continue

            color = 0
            if dayNumber == cursorDate[2]:
                color = 2

            scr.addstr(sy, sx, str(dayNumber), curses.color_pair(color))

            #Draw tasks
            taskList = tasks[dayNumber - 1]

            remainingTasks = False
            for i in range(len(taskList)):
                t = taskList[i]
                t = t[0 : min(len(t), cellWidth)]

                if i + 2 > cellHeight:
                    remainingTasks = True
                    break
                scr.addstr(sy + i + 1, sx, t)

            if remainingTasks:
                scr.addstr(sy + cellHeight - 1, sx + cellWidth - 3, "...")

    #Draw bottom line
    monthName = calendar.month_name[cursorDate[1]]

    dayIdx = 0
    for week in monthDays:
        for i in range(len(week)):
            if week[i] == cursorDate[2]:
                dayIdx = i
    dayName = dayNames[dayIdx]
    dateLine = f"{monthName} {cursorDate[2]}, {cursorDate[0]} ({dayName})"
    scr.addstr(height - 1, 0, dateLine)


def editDate(scr):
    curses.curs_set(2)
    buffer = monthData["content"][cursorDate[2] - 1]

    while True:
        scr.clear()
        scr.addstr(buffer)
        scr.refresh()

        try:
            key = scr.getkey()
        except Exception:
            continue

        if key == "KEY_BACKSPACE":
            buffer = buffer[0 : len(buffer) - 1]
            continue

        if len(key) == 1 and ord(key) == 23:
            break

        buffer += key


    monthData["content"][cursorDate[2] - 1] = buffer



def main(scr):
    global monthData

    #scr.clear, scr.addstr, scr.refresh, scr.getkey

    #curses.init_color(curses.COLOR_BLUE, 376, 251, 1000)
    factor = 1.6
    curses.init_color(curses.COLOR_BLUE, int(376 / factor), int(251 / factor), int(1000 / factor))
    curses.init_color(curses.COLOR_GREEN, 0, 1000, 1000)


    #curses.init_color(curses.COLOR_BLUE, 200, 200, 200)
    #curses.init_color(curses.COLOR_GREEN, 376, 251, 1000)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

    while True:
        scr.clear()
        drawCalendar(scr)
        scr.refresh()

        try:
            key = scr.getkey()
        except Exception:
            continue

        if key.lower() == "q":
            break


        if key == "t":
            _today = datetime.date.today()
            goDate(_today.year, _today.month, _today.day)
            monthData = loadMonth(cursorDate[0], cursorDate[1]) 
            continue

        if key == "a" or key == "d":
            year = cursorDate[0]
            month = cursorDate[1]
            day = cursorDate[2]

            if key == "a":
                month -= 1
            elif key == "d":
                month += 1

            if month <= 0:
                month = 12
                year -= 1
            elif month > 12:
                month = 1
                year += 1

            goDate(year, month, 1)
            monthData = loadMonth(year, month)

        if key == "\n":
            #editDate(scr)

            if editor == "TEXTPAD":
                curses.curs_set(2)
                scr.clear()
                box = curses.textpad.Textbox(scr)
                buffer = monthData["content"][cursorDate[2] - 1]
                scr.addstr(buffer)
                buffer = box.edit()
                curses.curs_set(0)
                monthData["content"][cursorDate[2] - 1] = buffer
                saveMonth(monthData, cursorDate[0], cursorDate[1])
                continue
            elif editor == "CED":
                buffer = monthData["content"][cursorDate[2] - 1]
                buffer = ced.edit(scr, buffer)
                monthData["content"][cursorDate[2] - 1] = buffer
                saveMonth(monthData, cursorDate[0], cursorDate[1])
                continue
            elif editor == "VIM":
                scr.clear()
                scr.refresh()
                subprocess.Popen("clear")
                cmd = f"vim {filePrefix}/temp"
                subprocess.Popen(cmd.split())
                continue


        newCursor = [x for x in cursorPos]
        if key == "KEY_LEFT":
            newCursor[1] -= 1
        elif key == "KEY_RIGHT":
            newCursor[1] += 1
        elif key == "KEY_DOWN":
            newCursor[0] += 1
        elif key == "KEY_UP":
            newCursor[0] -= 1

        if newCursor[0] >= 0 and newCursor[0] < monthHeight and newCursor[1] >= 0 and newCursor[1] < monthWidth:
            #Find new date...
            newDateNumber = monthDays[newCursor[0]][newCursor[1]]
            if newDateNumber != 0:
                goDate(cursorDate[0], cursorDate[1], newDateNumber)
        

curses.wrapper(main)

