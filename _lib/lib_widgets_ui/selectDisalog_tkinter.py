try:
    from tkinter import *
    title = []
except:
    from Tkinter import *


def accept(chkList, varList, root, selectedItems):
    for i, chk in enumerate(chkList):
        var = varList[i].get()
        if var:
            selectedItems.append(chk.cget("text"))
    root.quit()

def executeDialog(itemList):
    # lst = ["Arnold", "Mantra", "RenderMan"]

    root = Tk()

    windowWidth = root.winfo_reqwidth()
    windowHeight = root.winfo_reqheight()
    positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
    positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)
    root.geometry("+{}+{}".format(positionRight, positionDown))

    selectedItems = []
    chks = []
    vars_ = []
    for i in itemList:
        var = IntVar()
        chk = Checkbutton(root, text=i, variable=var)
        chks.append(chk)
        vars_.append(var)
        chk.pack(side=TOP, anchor="w")

    btn = Button(root, text='ok', command=lambda x=chks, y=vars_, r=root, it=selectedItems: accept(x, y, r, it)).pack(side=LEFT)

    root.mainloop()
    return selectedItems 
    print(selectedItems)

# executeDialog(['sfsfk', 'sdfsfs'])