import curses
import random

letters = "aoeuidhtns-"
chunkSize = input("chunk size: ")
if chunkSize == "":
    chunkSize = 4
else:
    chunkSize = int(chunkSize)

_letters = input("letters: ")
if _letters != "":
    letters = _letters

def getChunk(letters, size):
    chunk = ""
    for i in range(size):
        c = letters[random.randint(0, len(letters) - 1)]
        chunk += c
    return chunk

def main(scr):
    line = ""
    chunk = getChunk(letters, chunkSize)
    #curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    while True:
        scr.clear()
        scr.addstr(chunk + "\n", curses.color_pair(0))
        colorPair = 2
        if chunk.find(line) != 0:
            colorPair = 1
        scr.addstr(line, curses.color_pair(colorPair))
        scr.refresh()

        key = ""

        while len(key) != 1:
            key = scr.getkey()
            if (len(key) == 1 and ord(key) == 127):
                line = line[0 : len(line) - 1]
                key = ""
                break
            if key == " ":
                line = line[0 : len(line) - 1]
                key = ""
                break

        line += key


        if line == chunk:
            line = ""
            chunk = getChunk(letters, chunkSize)


curses.wrapper(main)
