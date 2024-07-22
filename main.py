import json
import warnings
# import wave
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import math

# Define important variables

# Flags for small functions
animisplaying = False
bbarGrabbed = False
bbarGrabID = 0
bbarStartLength = 0

# Variable that stores the visualized waveform of the imported audio
importaudiovec = [(0, 0), (0, 0)]
importaudiofreq = 1

toolchoice = "p"
pref_firstonionskin = False
pref_beforeonionskin = False
pref_afteronionskin = False

erasersize = 10
canvascontent = [[]]
canvascurrentlist = 0
windowwidth = 1920
windowheight = 1080
fgcolor = "#EEE"
bgcolor = "#111"
linewidth = 7
drawx = 0
drawy = 0
drawdown = False

zoom = 1


# Class setup

# Class for a project
class Project:
    def __init__(self, title, resolution, boards, background, audiopath):
        self.title = str(title)
        self.resolution = resolution
        self.boards = boards
        self.background = background
        self.audiopath = audiopath


# Class for a frame
class Board:
    def __init__(self, get, length):
        self.get = get
        self.length = length


def cerealizator(milk):
    return milk.__dict__


currentboard = 0
project = Project("New Project", (1632, 918), [Board([[]], 1000)], "none", audiopath="NA")


def center_window():
    # thanks xxmbabanexx from stackoverflow
    # get screen width and height
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (windowwidth / 2)
    y = (hs / 2) - (windowheight / 2)
    # set the dimensions of the screen
    root.geometry('%dx%d+%d+%d' % (windowwidth, windowheight, x, y))


# Set up window defaults
# TODO: make customizable
root = Tk()
root.geometry("1920x1080")
root.title('Franimate 24.07.13 - ' + project.audiopath)
#center_window()

# import images
# external image import
imgpen = PhotoImage(file="./icons/pen.png").subsample(4, 4)
imgera = PhotoImage(file="./icons/eraser.png").subsample(4, 4)
imgadd = PhotoImage(file="./icons/add.png").subsample(4, 4)
imgdel = PhotoImage(file="./icons/delete.png").subsample(4, 4)
imgply = PhotoImage(file="./icons/play.png").subsample(4, 4)
imgstp = PhotoImage(file="./icons/stop.png").subsample(4, 4)
imglit = PhotoImage(file="./icons/light.png")


# Menu functions
def open_projectfile():
    pjfilep = filedialog.askopenfilename(filetypes=[('JSON project file', '*.json')])
    pjfile = open(pjfilep, 'r')
    try:
        global project
        # pfd = pjfile dict
        pfd = list(json.load(pjfile).values())
        print((dict(pfd[2][0])).get("get"))
        boardlist = []
        for i in range(len(pfd[2])):
            boardlist.append(Board(dict(pfd[2][i]).get("get"), dict(pfd[2][i]).get("length")))
        print(boardlist)
        project = Project(pfd[0], pfd[1], boardlist, pfd[3], pfd[4])
    except Exception as excodename:
        messagebox.showerror(title="File error", message=str(excodename))
    else:
        messagebox.showinfo(title="Information", message="Loaded")
    pjfile.close()
    screenupdate(0)


def save_projectfile():
    pjfile = filedialog.asksaveasfile(mode='w', filetypes=[('JSON project file', '*.json')])
    if pjfile is None:
        messagebox.showerror(title="File error", message="No file")
    global project
    writefile = "Not saved"
    try:
        writefile = json.dumps(vars(project), default=cerealizator)
    except TypeError as excodename:
        messagebox.showerror(title="File error", message=str(excodename))
    print(writefile)
    pjfile.write(writefile)
    pjfile.close()


def set_audiopath():
    project.audiopath = filedialog.askopenfilename(filetypes=[('Waveform audio', '*.wav')])
    bbar_wave_load()
    bbar_update()

def preference_refresh():
    global pref_afteronionskin
    global pref_firstonionskin
    global pref_beforeonionskin
    pref_firstonionskin = mpref_firstonionskin.get()
    pref_beforeonionskin = mpref_beforeonionskin.get()
    pref_afteronionskin = mpref_afteronionskin.get()
    canvupdate()

# Set up menus
menubar = Menu(root, background='black', foreground='white', activebackground='black', activeforeground='white')
file = Menu(menubar, tearoff=False)
file.add_command(label="Open file", command=lambda: open_projectfile())
file.add_command(label="Select audio path", command=lambda: set_audiopath())
file.add_command(label="Save", command=lambda: save_projectfile())
file.add_command(label="Quit")

pref = Menu(menubar)

mpref_firstonionskin = BooleanVar()
mpref_beforeonionskin = BooleanVar()
mpref_afteronionskin = BooleanVar()

pref.add_checkbutton(label="First frame onion", command=preference_refresh, variable=mpref_firstonionskin)
pref.add_checkbutton(label="Previous frame onion", command=preference_refresh, variable=mpref_beforeonionskin)
pref.add_checkbutton(label="Next frame onion", command=preference_refresh, variable=mpref_afteronionskin)

menubar.add_cascade(label="File", menu=file)
menubar.add_cascade(label="Preferences", menu=pref)


# -------------------------------------------------------------------------------------#
# Events activated by buttons that cannot be placed below

def new_board():
    project.boards.insert(currentboard + 1, Board([[]], 1000))
    bbar_update()


def delete_board():
    global currentboard
    del project.boards[currentboard]
    if currentboard > len(project.boards) - 1:
        currentboard = len(project.boards) - 1
    bbar_update()


def stop_playback():
    global animisplaying
    animisplaying = False


def play_playback():
    global animisplaying
    animisplaying = True
    root.after(project.boards[currentboard].length, playLoop)


def playLoop():
    global animisplaying
    if animisplaying:
        print(animisplaying)
        global currentboard
        currentboard = currentboard + 1
        print(str(currentboard) + " and " + str(len(project.boards)))
        if (currentboard < len(project.boards)) & animisplaying:
            root.after(project.boards[currentboard].length, playLoop)
        screenupdate(0)


def sizepickerupdate(a):
    global erasersize
    erasersize = int(a)


def radio_penchoice():
    global toolchoice
    toolchoice = str(penchoice.get())


# Canvas code
cframe = Frame(root, bg="black")
canvas = Canvas(cframe, borderwidth=0, relief="solid", bg=bgcolor, highlightthickness=1)

pencircle = canvas.create_oval(-20, -20, 0, 0, outline="black")
background = canvas.create_rectangle(0, 0, project.resolution[0], project.resolution[1], outline="", fill="white")

# Left bar code
leftbar = Frame(root, bg=bgcolor)
penchoice = StringVar()
toolframe = Frame(leftbar, bg=bgcolor)
penpicker = Radiobutton(toolframe, text="Pen", fg=fgcolor, bg=bgcolor, variable=penchoice, value="p", selectcolor=bgcolor,
                        image=imgpen, indicatoron=False, borderwidth=5, command=radio_penchoice)
eraserpicker = Radiobutton(toolframe, text="Era", fg=fgcolor, bg=bgcolor, variable=penchoice, value="e", selectcolor=bgcolor,
                           image=imgera, indicatoron=False, borderwidth=5, command=radio_penchoice)
erasersizepicker = Scale(toolframe, from_=1, to=50, bg=bgcolor, command=sizepickerupdate, highlightthickness=0,
                         fg=fgcolor)

# Timeline(secondary canvas) code
bottombar = Frame(root, bg=bgcolor)
bottombuttons = Frame(bottombar, bg=bgcolor)

BTNaddBoard = Button(bottombuttons, image=imgadd, highlightthickness=0, borderwidth=0, bg=bgcolor, command=new_board)
BTNdelBoard = Button(bottombuttons, image=imgdel, highlightthickness=0, borderwidth=0, bg=bgcolor, command=delete_board)
BTNplayAnim = Button(bottombuttons, image=imgply, highlightthickness=0, borderwidth=0, bg=bgcolor, command=play_playback)
BTNstopAnim = Button(bottombuttons, image=imgstp, highlightthickness=0, borderwidth=0, bg=bgcolor, command=stop_playback)

bottomc = Canvas(bottombar, bg=bgcolor, highlightthickness=0, height=100, confine=False,
                 scrollregion=canvas.bbox("all"))

# Final assembly of widgets
leftbar.grid(column=0, row=0, sticky=NSEW)
toolframe.grid(column=0, row=0, sticky=N, padx=6, pady=6)
penpicker.pack(side="top")
eraserpicker.pack(side="top")
erasersizepicker.pack(side="bottom")

cframe.grid(column=1, row=0, sticky=NSEW)
canvas.pack(expand=TRUE, fill=BOTH)

bottombar.grid(column=0, row=1, columnspan=2, sticky="NSEW", ipadx=0, ipady=0)

bottombuttons.grid(sticky="", column=0, row=0, ipadx=10, ipady=2)
BTNaddBoard.pack()
BTNdelBoard.pack()
BTNplayAnim.pack()
BTNstopAnim.pack()
bottomc.grid(sticky="EW", column=1, row=0)


# Define canvas drawing events


# Update canvas or memory
def screenupdate(a):
    canvupdate(0)
    bbar_update()


def canvupdate(*_):
    global currentboard
    if currentboard > len(project.boards) - 1:
        currentboard = len(project.boards) - 1
    canvas.delete("all")
    global background
    background = canvas.create_rectangle(0, 0, project.resolution[0] * zoom, project.resolution[1] * zoom, outline="",
                                         fill="white")

    if pref_firstonionskin: draw_frame(0, "#EEE")
    if pref_beforeonionskin & (currentboard > 0): draw_frame(currentboard - 1, "#EEE")
    if pref_afteronionskin & ((len(project.boards) - 1) > currentboard): draw_frame(currentboard + 1, "#EEE")
    draw_frame(currentboard, "black")

    global pencircle
    pencircle = canvas.create_oval((erasersize * -2) * zoom, (erasersize * -2) * zoom, 0, 0, outline="red")


def draw_frame(fra, clr):
    if zoom == 1:
        for j in range(len(project.boards[fra].get) - 1):
            # Sanity check because sometimes the 'tuple index' goes out of range
            if len(project.boards[fra].get[j]) < 4:
                warnings.warn("Tuple index at " + str(project.boards[fra].get[j]))
                return
            canvas.create_line(project.boards[fra].get[j], width=linewidth * zoom, fill=clr)
    else:
        cbo = project.boards[fra].get
        for j in range(len(cbo)):
            for i in range(len(cbo[j]) - 1):
                canvas.create_line((cbo[j][i][0] * zoom), (cbo[j][i][1] * zoom), (cbo[j][i + 1][0] * zoom),
                                   (cbo[j][i + 1][1] * zoom), width=linewidth * zoom, fill=clr)


# Small events that are bound to keys
def drawtouch(e):
    drawmove(e)


def drawlift(e):
    if toolchoice == "p":
        drawmove(e)
        global canvascurrentlist
        global currentboard
        global project
        project.boards[currentboard].get.append([])
        canvascurrentlist = canvascurrentlist + 1
        global drawdown
        drawdown = False
    elif toolchoice == "e":
        canvupdate(0)


def drawmove(e):
    global canvascurrentlist
    if (toolchoice == "p") & (e.x < project.resolution[0] * zoom) & (e.y < project.resolution[1] * zoom):
        canvascurrentlist = len(project.boards[currentboard].get) - 1
        project.boards[currentboard].get[canvascurrentlist].append((e.x / zoom, e.y / zoom))
        global drawx
        global drawy
        global drawdown
        if not drawdown:
            drawdown = True
            drawx = e.x
            drawy = e.y
        elif math.dist((drawx, drawy), (e.x, e.y)) > 2:
            canvas.create_line((drawx, drawy), (e.x, e.y), width=linewidth * zoom, fill='black', smooth=True)
            drawx = e.x
            drawy = e.y
    elif toolchoice == "e":
        canvas.moveto(pencircle, e.x - (erasersize * zoom), e.y - (erasersize * zoom))
        l = 0
        qdistdebug = 5000
        for i in project.boards[currentboard].get:
            for j in i:
                dist = math.dist((e.x / zoom, e.y / zoom), (j[0], j[1]))
                if dist < erasersize:
                    project.boards[currentboard].get[l] = [(0, 0), (0, 0)]
                    break
                else:
                    if dist < qdistdebug:
                        qdistdebug = dist
            l = l + 1


def resetzoom(a):
    global zoom
    zoom = 1
    canvupdate(1)


def zoom_winosx(e):
    if e.delta > 0:
        zoom_in()
    else:
        zoom_out()
    global zoom
    if abs(zoom - 1) < 0.05:
        zoom = 1


def zoom_in():
    global zoom
    zoom = zoom * 1.1
    canvupdate(0)


def zoom_out():
    global zoom
    zoom = zoom / 1.1
    canvupdate(0)


# Bottom bar-specific events
def bbar_update():
    bottomc.delete("all")
    thumbsizedivide = 6
    currentx = 10
    for i in range(0, len(project.boards)):
        thumbpad = 10
        thumbx = project.boards[i].length / thumbsizedivide
        thumby = 20
        if currentboard == i:
            bottomc.create_rectangle(currentx, thumbpad, currentx + thumbx, thumby + thumbpad, outline="blue",
                                     fill="white", width="3")
        else:
            bottomc.create_rectangle(currentx, thumbpad, currentx + thumbx, thumby + thumbpad, outline="", fill="white")
        currentx = currentx + thumbx + thumbpad

    # Renders audio, unused because of broken input from the bbarWaveLoad function
    # bottomc.create_line(importaudiovec, width=1, fill="white", smooth=True)


def bbar_wave_load():
    """
    if (project.audiopath != "NA"):
        global importaudiofreq
        global importaudiovec
        wavefile = None
        wavebytes = None
        try:
            wavefile = wave.open(project.audiopath, mode="rb")
        except Exception as exccode:
            print("Failed to load audio with " + exccode)
        if wavefile == None:
            return
        wavebytes = wavefile.readframes(9223372036854775808)
        # importaudiovec for storing audio
        importaudiofreq = wavefile.getframerate()
        importaudiovec = []

        qresolution = 5000
        offset = (10, 40) # below this line is magic number hell, don't ask me what these do
        audiox = (1000 / importaudiofreq) / (12 * wavefile.getnchannels())

        for i in range(round(len(wavebytes) / qresolution)):
            iavxpos = (i * qresolution) * audiox
            iavypos = float(wavebytes[int(i * qresolution)]) * 0.1
            importaudiovec.append((iavxpos + offset[0], iavypos + offset[1]))
        print(len(importaudiovec))
        print("j")
        print(importaudiovec[len(importaudiovec) - 1])
        root.title('Franimate 24.07.13 - ' + project.audiopath)
    """

    global importaudiovec
    # importaudiovec = file.open(project.audiopath) TODO: Load audio files


#        for i in range(int(len(wavebytes) / qresolution)):
#            offset = (10, 40)
#
#            importaudiovec.append((((i * audiox) + offset[0]), wavebytes[int(i / qresolution)] * 0.1 + offset[1]))

def bbar_grab(e):
    global bbarGrabbed
    if bbarGrabbed:
        global bbarStartLength
        project.boards[bbarGrabID].length = int(abs((bottomc.canvasx(e.x) - bbarStartLength) * 6))
        bbar_update()


def bbar_release(*_):
    global bbarGrabbed
    bbarGrabbed = False


def bbar_canvas_check(e):
    currentx = 10
    thumbsizedivide = 6
    thumbpad = 10
    relativecanvasmousex = bottomc.canvasx(e.x)

    for i in range(0, len(project.boards)):
        thumbx = project.boards[i].length / thumbsizedivide
        thumby = 20
        if (relativecanvasmousex > currentx) & (relativecanvasmousex < currentx + thumbx) & (e.y < thumby + thumbpad):
            global currentboard
            currentboard = i
            screenupdate(0)
        elif (relativecanvasmousex > currentx + thumbx) & (relativecanvasmousex < currentx + thumbx + thumbpad) & (
                e.y < thumby + thumbpad):
            print("Grab!")
            global bbarGrabbed
            global bbarGrabID
            global bbarStartLength
            bbarGrabID = i
            bbarGrabbed = True
            bbarStartLength = currentx
        currentx = currentx + thumbx + thumbpad
    if e.x > (bottomc.winfo_width() - 20):
        bottomc.xview_scroll(1, UNITS)
    if e.x < 20:
        bottomc.xview_scroll(-1, UNITS)


# Define bottombar drawing events


# Commonly customized keybinds like undo/redo/play/swapframe

def set_penchoice(f):
    global toolchoice
    toolchoice = f


root.bind('1', lambda event: set_penchoice("p"))
root.bind('2', lambda event: set_penchoice("e"))

# Standard required keybinds like click and zoom

canvas.bind('<MouseWheel>', zoom_winosx)
canvas.bind('<B1-Motion>', drawmove)
bottomc.bind('<B1-Motion>', bbar_grab)
bottomc.bind('<ButtonRelease-1>', bbar_release)
bottomc.bind('<Button>', bbar_canvas_check)
erasersizepicker.bind('<ButtonRelease-1>', screenupdate)
canvas.bind('<ButtonPress-1>', drawmove)
# bottomc.bind('<ButtonPress-1>', bbar_canvas_check())
canvas.bind('<ButtonRelease-1>', drawlift)
root.bind('r', screenupdate)
root.bind('t', resetzoom)

bottombar.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.config(menu=menubar, bg="#111")
screenupdate(0)
root.mainloop()
