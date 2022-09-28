import curses
import random

keys_qwerty = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
keys_dvorak = "`1234567890[]',.pyfgcrl/=\\aoeuidhtns-;qjkxbmwvz"

assert len(keys_qwerty) == len(keys_dvorak)

kbmap = {keys_qwerty[i]: keys_dvorak[i] for i in range(len(keys_qwerty))}

letters = "aoeuidhtns-"


def editBuffer(scr, string, swapLayout = False):
    key = scr.getkey()

    if swapLayout:
        if key in kbmap.keys():
            key = kbmap[key]

    if (key == "KEY_BACKSPACE") or (len(key) == 1 and ord(key) == 127):
        string = string[0 : len(string) - 1]
        return [string, key]

    if key == "\n":
        return [string, key]

    string += key

    return [string, key]



def getChunk(letters, size):
    chunk = ""
    for i in range(size):
        c = letters[random.randint(0, len(letters) - 1)]
        chunk += c
    return chunk

def main(scr):
    #Initialize colors
    #curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    #Get chunk size
    chunkSize = ""
    while True:
        scr.clear()
        scr.addstr("Chunk size: " + chunkSize)
        scr.refresh()

        chunkSize, key = editBuffer(scr, chunkSize, True)

        if key == "\n":
            chunkSize = int(chunkSize)
            break

    #Get letters
    letters = ""
    while True:
        scr.clear()
        scr.addstr("Letters: " + letters)
        scr.refresh()

        letters, key = editBuffer(scr, letters, True)

        if key == "\n":
            break


    #Initialize buffers/problem instance
    line = ""
    chunk = getChunk(letters, chunkSize)

    while True:
        scr.clear()
        scr.addstr(chunk + "\n", curses.color_pair(0))
        colorPair = 2
        if chunk.find(line) != 0:
            colorPair = 1
        scr.addstr(line, curses.color_pair(colorPair))
        scr.refresh()

        line, key = editBuffer(scr, line, True)
        if key == " ":
            line = line[0 : len(line) - 2]


        if line == chunk:
            line = ""
            chunk = getChunk(letters, chunkSize)


curses.wrapper(main)
