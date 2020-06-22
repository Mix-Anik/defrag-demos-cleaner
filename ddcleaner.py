from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pickle
from security import *
import json
from os import listdir, walk, mkdir, rename, remove
from os.path import isfile, isdir, join, getsize, abspath
import time as t

#=======================================INSTRUCTIONS=====================================================
# Set variable PATH to the path of your defrag demos folder                                             #
# Set variable FORMAT to the same value as 'df_ar_format' has, but remove all tokens except following:  #
# $map | $gt | $phys | $m | $s | $ms | $pl | $plc |                                                     #
# removing all -/+ signs used with them                                                                 #
# Also make sure all tokens are separated with some symbol like "." and format starts with a token      #
#                                                                                                       #
# EXAMPLE: if your df_ar_format = "$map.$-route[$gt.$phys.$-mode]$m.$-s.$-ms($pl.$plc)"                 #
# Then set FORMAT variable to "$map[$gt.$phys]$m.$s.$ms($pl.$plc)"                                      #
#========================================================================================================

#====================Global Variables=========================
TOKENS = ["$map","$ms","$m","$gt","$phys","$s","$plc","$pl"]
version = 1.1

# GUI
# Main
root = Tk()
root.title("Defrag Demos Cleaner v%s" % version)
root.resizable(False, False)
root.geometry("600x230")
root.wm_attributes('-alpha', 0.98)
root.configure(bg="gray30")

# Fields 
formatLabel = ttk.Label(root, text="Format:")
formatLabel.place(x=10, y=9)
formatValue = StringVar()
formatEntry = ttk.Entry(root, textvariable = formatValue)
formatEntry.place(x=10, y=30, height=25, width=240)

pathLabel = ttk.Label(root, text="Demos Path:")
pathLabel.place(x=10, y=59)
pathValue = StringVar()
pathEntry = ttk.Entry(root, textvariable = pathValue)
pathEntry.place(x=10, y=80, height=25, width=240)

#Functions
def run():
    if pathValue.get() == "" or formatValue.get() == "":
        messagebox.showerror("Warning", "Please fill both format and path fields!")
    elif not checkPath():
        messagebox.showerror("Warning", "Invalid Path!")
    elif not checkFormat():
        messagebox.showerror("Warning", "Invalid Format!")
    else:
        if saveCreds.get(): remember(formatValue.get(), pathValue.get())
        progress["value"] = 0
        cleanConsole()
        cleanDemos()

def showHelpFormat():
    messagebox.showinfo("Helper","Enter in FORMAT field same value as your df_ar_format has, but remove all tokens except following: \n" +
     "$map | $gt | $phys | $m | $s | $ms | $pl | $plc \nand all -/+ signs used with them.\n" + 
     "Also make sure all tokens are separated with some symbol like '.' and format starts with a token.\n\n" +
     "EXAMPLE: if your df_ar_format = '$map.$-route[$gt.$phys.$-mode]$m.$-s.$-ms($pl.$plc)'\n" +
     "Then enter in FORMAT field '$map[$gt.$phys]$m.$s.$ms($pl.$plc)'\n\n" +
     "$map|$phys|$m|$s|$ms|$pl are obligatory to have!")

def showHelpPath():
    messagebox.showinfo("Helper","Enter your full path to defrag 'demos' folder\n(e.g. C:/Games/Defrag/defrag/demos)")

def checkPath():
    valid = True
    try: listdir(pathValue.get())
    except FileNotFoundError: valid = False
    return valid

def checkFormat():
    valid = False
    fv = formatValue.get()
    if "$map" in fv and "$phys" in fv and "$m" in fv and "$s" in fv and "$ms" in fv and "$pl" in fv:
        valid = True
    return valid

def deleteRest(demos, bestDemosDict):
    bestDemos = [x[1] for x in bestDemosDict.values()]
    #print(bestDemos)
    for demo in demos:
        if demo not in bestDemos:
            remove(join(pathValue.get(), demo))
    
def remember(pathString, formatString):
    dataFile = open("data.DUMP", "wb")
    textified = json.dumps([pathString, formatString])
    data = encrypt(textified)
    pickle.dump(data, dataFile)
    dataFile.close()

def checkData():
    if isfile("data.DUMP"):
        dataFile = open("data.DUMP", "rb")
        encrypted = pickle.load(dataFile)
        decrypted = decrypt(encrypted)
        data = json.loads(decrypted)
        formatValue.set(data[0])
        pathValue.set(data[1])
    else:
        formatValue.set("")
        pathValue.set("")
        
def writeToConsole(text):
    consoleText.configure(state=NORMAL)
    consoleText.insert(INSERT, text)
    consoleText.see(END)
    consoleText.configure(state=DISABLED)

def cleanConsole():
    consoleText.configure(state=NORMAL)
    consoleText.delete(1.0, END)
    consoleText.configure(state=DISABLED)

def fillCredits():
    writeToConsole("Quake Demos Cleaner\nVersion: %s\nGithub: /Mix-Anik/defrag-demos-cleaner" % version)
    
def writeStatistics(fails, succeeded, exTime, dSize, dDeleted, dDelSize):
    writeToConsole("\nStatistics:\nValid demos processed - " + str(succeeded) + "\n" +
                   "Invalid demo occurrences - " + str(fails) + "\n" +
                   "Total demos processed - " + str(succeeded + fails) + "\n" +
                   "Demos deleted - " + str(dDeleted) + "\n" +
                   "Processed demos size - " + str(round(dSize, 2)) + "MB\n" +
                   "Memory freed - " + str(round(dDelSize, 2)) + "MB\n" +
                   "Execution time - " + str(round(exTime, 2)) + "s\n")

def dumpLog():
    logText = consoleText.get(1.0, END)
    datetime = t.strftime("%H-%M_%d-%m-%Y", t.localtime())
    file = open("log_"+datetime+".txt", "w", encoding = "UTF-8")
    file.write(logText)
    file.close()

    
#=============Delimiters used in format string================
def getDelimiters():
    delimiters = formatValue.get()
    for token in TOKENS:
        delimiters = delimiters.replace(token, "")  
    delimiters = set(delimiters)
    return delimiters
#=======================Token Array===========================
def getTokenArray():
    tArray = formatValue.get()
    delimiters = getDelimiters()
    for delimiter in delimiters:
        tArray = tArray.replace(delimiter,"#")
    tArray = tArray.split("#")
    return tArray

#======================Demo Cleaning==========================
def cleanDemos():
    # Start timestamp
    startTime = t.time()
    # List of all demos in demos folder
    demos = [f for f in listdir(pathValue.get()) if isfile(join(pathValue.get(), f))]
    # List of all folders created
    folders = [name for name in listdir(pathValue.get()) if isdir(join(pathValue.get(), name))]
    delimiters = getDelimiters()
    tokenArray = getTokenArray()
    bestDemos = {}
    validDemos = []
    amount = len(demos)
    progressIncrement = 100 / amount
    succeeded = 0
    failed = 0
    deleted = 0
    vDemosSize = 0
    iDemosSize = 0
    deletedSize = 0
    
    writeToConsole("Starting cleaning demos at:\n" + pathValue.get() + "\n\n")
    
    for demo in demos:
        writeToConsole("Checking " + demo + "\n")
        dName = demo.strip(".dm_68")
        for delim in delimiters:
            dName = dName.replace(delim, "#")
        dtArray = dName.split("#")
        
        # invalid demo name
        if len(dtArray) < 6:
            iDemosSize += getsize(join(pathValue.get(), demo)) / 1024**2
            writeToConsole("Failure. Invalid demo name!\n")
            progress["value"] += progressIncrement
            root.update()
            failed += 1
            continue
        else: # valid demo name
            vDemosSize += getsize(join(pathValue.get(), demo)) / 1024**2
            validDemos.append(demo)
            mapName = dtArray[tokenArray.index("$map")]
            playerName = dtArray[tokenArray.index("$pl")]
            physics = dtArray[tokenArray.index("$phys")]
            time = int(dtArray[tokenArray.index("$m")]) * 60000 + int(dtArray[tokenArray.index("$s")]) * 1000 + int(dtArray[tokenArray.index("$ms")])
            #print("MAP: " + mapName + "\nPLAYER: " + playerName + "\nPHYSICS: " + physics + "\nTIME: " + str(time))

            if bestOnly.get():
                demoKey = mapName + physics + playerName
                demoValue = [time, demo, mapName]
                if demoKey in bestDemos and time < bestDemos[demoKey][0]:
                    bestDemos[demoKey] = demoValue
                elif demoKey not in bestDemos:
                    bestDemos[demoKey] = demoValue
            else:
                if mapName not in folders:
                    mkdir(pathValue.get()+"/"+mapName)
                    folders.append(mapName)
                    
                rename(pathValue.get()+"/"+demo, pathValue.get()+"/"+mapName+"/"+demo)
            
            writeToConsole("Success!\n")
            progress["value"] += progressIncrement
            succeeded += 1
            
    if bestOnly.get():
        deletedSize = vDemosSize
        for k in bestDemos:
            deletedSize -= getsize(join(pathValue.get(), bestDemos[k][1])) / 1024**2
            if bestDemos[k][2] not in folders:
                mkdir(pathValue.get()+"/"+bestDemos[k][2])
                folders.append(bestDemos[k][2])   
            rename(pathValue.get()+"/"+bestDemos[k][1], pathValue.get()+"/"+bestDemos[k][2]+"/"+bestDemos[k][1])
        deleted = succeeded - len(bestDemos)
        deleteRest(validDemos, bestDemos)
        
    writeToConsole("\nDemos cleaning is completed\n\n")
    executionTime = t.time() - startTime
    writeStatistics(failed, succeeded, executionTime, vDemosSize+iDemosSize, deleted, deletedSize)
    if logging.get(): dumpLog()
        
# Styling
style = ttk.Style()
style.configure("TButton", foreground = "crimson", background = "gray30", color="green", relief = "flat")
style.configure("TLabel", foreground = "cyan", background = "gray30")
style.configure("TCheckbutton", foreground = "cyan", background = "gray30")
#style.configure("Horizontal.TProgressbar", foreground = "cyan", background = "gray30")

# TODO: fix pictures causing crash due to not being found
# Images
# helpbg = PhotoImage(file="pictures\helpbg.gif")
# runbg = PhotoImage(file="pictures\cleanbg.gif")
# root.iconbitmap("pictures\quakeico.ico")

# Progressbar
progress = ttk.Progressbar(root, orient ="horizontal", length = 600, mode ="determinate")
progress.pack(side=BOTTOM)
progress["maximum"] = 100
progress["value"] = 0

# Check Boxes
saveCreds = IntVar()
bestOnly = IntVar()
logging = IntVar()

checkCreds = ttk.Checkbutton(root, text="Remember",  variable=saveCreds)
checkBest = ttk.Checkbutton(root, text="Best times only",  variable=bestOnly)
checkLog = ttk.Checkbutton(root, text="Dump Log", variable=logging)
checkCreds.place(x=10, y=110)
checkBest.place(x=10, y=130)
checkLog.place(x=10, y=150)

# Log Console
consoleLabel = ttk.Label(root, text="Log Console:")
consoleLabel.place(x=390, y=10)
consoleText = Text(root, width=40, height=10, relief=FLAT, state=DISABLED,
                   background = "gray80", foreground = "firebrick")
consoleText.place(x=260, y=30)

# Buttons
runButton = Button(root, text="Clean", command = lambda : run())
runButton.config(relief=FLAT, background = "gray80", foreground = "firebrick")#, image=runbg)
runButton.place(x=90, y=170,height=25, width=80)

helpFormat = Button(root, text="?", command = lambda : showHelpFormat())
helpFormat.config(relief=GROOVE, background = "gray30", foreground = "red")#, image=helpbg)
helpFormat.place(x=55, y=9,height=20, width=20)

helpPath = Button(root, text="?", command = lambda : showHelpPath())
helpPath.config(relief=GROOVE, background = "gray30", foreground = "red")#, image=helpbg)
helpPath.place(x=80, y=59,height=20, width=20)

#Checking if there are credentials saved
checkData()
fillCredits()
root.mainloop()