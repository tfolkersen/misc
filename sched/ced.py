import curses
import curses.textpad
import subprocess

def main():
    print("asd")

def edit(scr, buffer):
    curses.curs_set(2)
    scr.clear()
    pad = curses.textpad.Textbox(scr)
    scr.addstr(buffer)
    buffer = pad.edit()
    return buffer

if __name__ == "__main__":
    print("ced main")

