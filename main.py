from tkinter import *
import math
from tkinter import messagebox

# Define important variables
erasersize = 2
canvascontent = [[]]
canvascurrentlist = 0
windowwidth = 1280
windowheight = 720
fgcolor = "#EEE"
bgcolor = "#111"
drawx = 0
drawy = 0
drawdown = False

zoom = 1

#Class setup

#Class for a project
class Project:
    def __init__(self, title, resolution, boards, background):
        self.title = str(title)
        self.resolution = resolution
        self.boards = boards
        self.background = background
# Class for a frame
class Board:
    def __init__(self, get):
        self.get = get

currentboard = 0
project = Project("New Project", (640, 360), [Board([[]]), Board([[]]), Board([[]])], "none")


def centerWindow():
    # thanks xxmbabanexx from stackoverflow
    # get screen width and height
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (windowwidth/2)
    y = (hs/2) - (windowheight/2)
    # set the dimensions of the screen
    root.geometry('%dx%d+%d+%d' % (windowwidth, windowheight, x, y))

# Set up window defaults
# TODO: make customizable
root = Tk()
root.geometry("1280x720")
root.title('Franimate 24.07.09 - ' + project.title)
centerWindow()

#import images
#external image import
imgpen = PhotoImage(file="./icons/pen.png").subsample(4,4)
imgera = PhotoImage(file="./icons/eraser.png").subsample(4,4)
imgadd = PhotoImage(file="./icons/add.png").subsample(4,4)
imgdel = PhotoImage(file="./icons/delete.png").subsample(4,4)

# Set up menus
menubar = Menu(root, background='black', foreground='white', activebackground='black', activeforeground='white')
file = Menu(menubar, tearoff=False)
file.add_command(label="Open project file")
file.add_command(label="Quit")

menubar.add_cascade(label="File", menu=file)

#-------------------------------------------------------------------------------------#
# Events activated by buttons that cannot be placed below

def newBoard():
    project.boards.insert(currentboard + 1, Board([[]]))
    bbarUpdate()

def delBoard():
    global currentboard
    del project.boards[currentboard]
    if(currentboard > len(project.boards) - 1):
        currentboard = len(project.boards) - 1
    bbarUpdate()

def sizepickerupdate(a):
    global erasersize
    erasersize = int(a)

#Canvas code
cframe = Frame(root, bg="black")
canvas = Canvas(cframe, borderwidth=0, relief="solid", bg=bgcolor, highlightthickness=1)

pencircle = canvas.create_oval(-20, -20, 0, 0, outline="black")
background = canvas.create_rectangle(0,0,project.resolution[0],project.resolution[1], outline="", fill="white")

#Left bar code
leftbar = Frame(root,  bg=bgcolor)
penchoice = StringVar()
toolframe = Frame(leftbar, bg=bgcolor)
penpicker = Radiobutton(toolframe, text="Pen", fg=fgcolor, bg=bgcolor, var=penchoice, value="p", selectcolor=bgcolor, image=imgpen, indicatoron=0, borderwidth=5)
eraserpicker = Radiobutton(toolframe, text="Era", fg=fgcolor, bg=bgcolor, var=penchoice, value="e", selectcolor=bgcolor, image=imgera, indicatoron=0, borderwidth=5)
erasersizepicker = Scale(toolframe, from_=1, to=50, bg=bgcolor, command=sizepickerupdate, highlightthickness=0, fg=fgcolor)

#Timeline(secondary canvas) code
bottombar = Frame(root, bg=bgcolor)
bottombuttons = Frame(bottombar, bg=bgcolor)



BTNaddBoard = Button(bottombuttons, image=imgadd, highlightthickness=0, borderwidth=0, bg=bgcolor, command=newBoard)
BTNdelBoard = Button(bottombuttons, image=imgdel, highlightthickness=0, borderwidth=0, bg=bgcolor, command=delBoard)

bottomc = Canvas(bottombar, bg=bgcolor, highlightthickness=0, height=100)

#Final assembly of widgets
leftbar.grid(column=0, row=0, sticky=NSEW)
toolframe.grid(column=0, row=0, sticky=N, padx=6, pady=6)
penpicker.pack(side="top")
eraserpicker.pack(side="top")
erasersizepicker.pack(side="bottom")

cframe.grid(column=1, row=0, sticky=NSEW)
canvas.pack(expand=TRUE, fill=BOTH)

bottombar.grid(column=0, row=1, columnspan=2, sticky="NSEW", ipadx=0, ipady=0)

bottombuttons.grid(sticky="", column=0, row=0, ipadx=10, ipady=2 )
BTNaddBoard.pack()
BTNdelBoard.pack()
bottomc.grid(sticky="EW", column=1, row=0)

#Define canvas drawing events

def drawtouch(e):
    drawmove(e)
def drawlift(e):
    if (penchoice.get() == "p"):
        drawmove(e)
        global canvascurrentlist
        global currentboard
        global project
        project.boards[currentboard].get.append([])
        canvascurrentlist = canvascurrentlist + 1
        global drawdown
        drawdown = False
    elif (penchoice.get() == "e"):
        canvupdate(0)
def drawmove(e):

    if((penchoice.get() == "p") & (e.x < project.resolution[0] * zoom) & (e.y < project.resolution[1] * zoom)):
        canvascurrentlist = len(project.boards[currentboard].get) - 1
        project.boards[currentboard].get[canvascurrentlist].append((e.x / zoom, e.y / zoom))
        global drawx
        global drawy
        global drawdown
        if(drawdown == False):
            drawdown = True
            drawx = e.x
            drawy = e.y
        elif(math.dist((drawx,drawy), (e.x,e.y)) > 2):
            canvas.create_line((drawx, drawy), (e.x, e.y), width=4*zoom, fill='black', smooth=True)
            drawx = e.x
            drawy = e.y
    elif(penchoice.get() == "e"):
        canvas.moveto(pencircle, e.x - (erasersize*zoom), e.y - (erasersize*zoom))
        l=0
        qdistdebug = 5000
        for i in project.boards[currentboard].get:
            for j in i:
                dist = math.dist((e.x / zoom,e.y / zoom), (j[0], j[1]))
                if dist < erasersize:
                    project.boards[currentboard].get[l] = [(0, 0), (0, 0)]
                    break
                else:
                    if dist < qdistdebug:
                        qdistdebug = dist
            l = l+1
def resetzoom(a):
    global zoom
    zoom = 1
    canvupdate(1)
def screenupdate(a):
    print("se")
    canvupdate(0)
    bbarUpdate()


def canvupdate(a):
    global currentboard
    if(currentboard > len(project.boards) - 1):
        currentboard = len(project.boards) - 1
    canvas.delete("all")
    global background
    background = canvas.create_rectangle(0, 0, project.resolution[0] * zoom, project.resolution[1] * zoom, outline="", fill="white")

    if (zoom == 1):
        for j in range(len(project.boards[0].get) - 1):
            canvas.create_line(project.boards[0].get[j], width=4 * zoom, fill="#EEE")
    else:
        cbo = project.boards[0].get
        for j in range(len(cbo)):
            for i in range(len(cbo[j]) - 1):
                canvas.create_line((cbo[j][i][0] * zoom),(cbo[j][i][1] * zoom),(cbo[j][i + 1][0] * zoom),(cbo[j][i + 1][1] * zoom), width=4*zoom, fill="#EEE")

    if(zoom==1):
        for j in range(len(project.boards[currentboard].get) - 1):
            canvas.create_line(project.boards[currentboard].get[j], width=4*zoom, fill="black")
    else:
        cbo = project.boards[currentboard].get
        for j in range(len(cbo)):
            for i in range(len(cbo[j]) - 1):
                canvas.create_line((cbo[j][i][0] * zoom),(cbo[j][i][1] * zoom),(cbo[j][i + 1][0] * zoom),(cbo[j][i + 1][1] * zoom), width=4*zoom, fill="black")

    global pencircle
    pencircle = canvas.create_oval((erasersize * -2) * zoom, (erasersize * -2) * zoom, 0, 0, outline="red")
def zoomWinOSX(e):
    if(e.delta > 0):
        zoomIn()
    else:
        zoomOut()
    global zoom
    if(abs(zoom - 1) < 0.05):
        zoom = 1
def zoomIn():
    global zoom
    zoom = zoom * 1.1
    canvupdate(0)
def zoomOut():
    global zoom
    zoom = zoom / 1.1
    canvupdate(0)



# Define bottombar drawing events
def bbarUpdate():
    bottomc.delete("all")
    thumbsizedivide = 6
    for i in range(0, len(project.boards)):
        thumbpad = 10
        thumbx = project.resolution[0] / thumbsizedivide
        thumby = project.resolution[1] / thumbsizedivide
        if(currentboard == i):
            bottomc.create_rectangle(((thumbx + thumbpad) * i) + thumbpad, thumbpad, ((thumbx + thumbpad) * (i+1)), thumbpad + thumby, outline="blue", fill="white", width="2")
        else:
            bottomc.create_rectangle(((thumbx + thumbpad) * i) + thumbpad, thumbpad, ((thumbx + thumbpad) * (i+1)), thumbpad + thumby, outline="", fill="white")

def bbarCanvChek(e):
    thumbsizedivide = 6
    for i in range(0, len(project.boards)):
        thumbpad = 10
        thumbx = project.resolution[0] / thumbsizedivide
        thumby = project.resolution[1] / thumbsizedivide
        if((e.x < ((thumbx + thumbpad) * (i+1))) & (e.x > ((thumbx + thumbpad) * i) + thumbpad)):
            global currentboard
            currentboard = i
            screenupdate(0)
#       bottomc.create_rectangle(((thumbx + thumbpad) * i) + thumbpad, thumbpad, ((thumbx + thumbpad) * (i+1)), thumbpad + thumby, outline="", fill="white")


canvas.bind('<MouseWheel>', zoomWinOSX)
canvas.bind('<B1-Motion>', drawmove)
bottomc.bind('<1>', bbarCanvChek)
erasersizepicker.bind('<ButtonRelease-1>', screenupdate)
canvas.bind('<ButtonPress-1>', drawmove)
#bottomc.bind('<ButtonPress-1>', bbarCanvChek())
canvas.bind('<ButtonRelease-1>', drawlift)
root.bind('r', screenupdate)
root.bind('t', resetzoom)

bottombar.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.config(menu=menubar, bg="#111")
screenupdate(0)
root.mainloop()
