'''
changelog tegenover v1: manier van het laden/switchen van frames
'''

import tkinter as tk
import time
import APIconnectV2 as API
import threading
import serial

global arduino2


class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('ABN-MANBRO')
        self._frame = None
        self.switch_frame(StartPage)
        self.geometry('1920x1080')
        self.attributes('-fullscreen', True)
        self.fullScreenState = False
        self.bind("<F11>", self.toggleFullScreen)
        self.bind("<Escape>", self.quitFullScreen)

    def toggleFullScreen(self, event):
        self.fullScreenState = not self.fullScreenState
        self.attributes("-fullscreen", self.fullScreenState)

    def quitFullScreen(self, event):
        self.fullScreenState = False
        self.attributes("-fullscreen", self.fullScreenState)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill="both", expand=1)

    def clockLabel(self):
        def clock():
            hour = time.strftime("%H")
            minute = time.strftime("%M")
            second = time.strftime("%S")

            day = time.strftime("%d")
            month = time.strftime("%B")
            year = time.strftime("%Y")

            Label_tijd.config(text=hour + ":" + minute + ":" + second)
            Label_datum.config(text=day + " " + month + " " + year)
            Label_tijd.after(1000, clock)

        Label_tijd = tk.Label(self, text="", font=('Century Gothic', 34, 'bold'), fg="black", bg="white")
        Label_datum = tk.Label(self, text="", font=('Century Gothic', 20, 'bold'), fg="black", bg="white")
        Label_tijd.place(x=1550, y=80)
        Label_datum.place(x=1550, y=150)

        clock()

    def checkRFID(self):
        if API.rfid():
            self.switch_frame(PageOne)
        else:
            self.switch_frame(PageEight)

    def KeypadOption(self):
        while True:
            keypad = API.arduino2.read()
            keypad = keypad.decode()
            if keypad:
                if keypad == 'A':
                    self.switch_frame(PageThree)
                    return
                if keypad == 'B':
                    self.switch_frame(PageFour)
                    return
                if keypad == 'C':
                    API.amount = 70
                    check = API.fastAmount()
                    if check == 0:
                        self.switch_frame(PageSix)
                    elif check == 1:
                        self.switch_frame(PageEight)
                    elif check == 2:
                        self.switch_frame(PageTwo)
                    return
                if keypad == '*':
                    self.switch_frame(PageEight)
                    return
                print(keypad)

    def KeypadWithdraw(self):
        while True:
            keypad = API.arduino2.read()
            keypad = keypad.decode()
            check = -1
            if keypad:
                if keypad == 'A':
                    API.amount = 10
                    check = API.fastAmount()
                    if check == 0:
                        API.amount = 10
                        self.switch_frame(PageSix)
                    elif check == 1:
                        self.switch_frame(PageEight)
                    elif check == 2:
                        self.switch_frame(PageThree)
                    return
                if keypad == 'B':
                    API.amount = 20
                    check = API.fastAmount()
                    if check == 0:
                        self.switch_frame(PageSix)
                    elif check == 1:
                        self.switch_frame(PageEight)
                    elif check == 2:
                        self.switch_frame(PageThree)
                    return
                if keypad == 'C':
                    API.amount = 50
                    check = API.fastAmount()
                    if check == 0:
                        self.switch_frame(PageSix)
                    elif check == 1:
                        self.switch_frame(PageEight)
                    elif check == 2:
                        self.switch_frame(PageThree)
                    return
                if keypad == 'D':
                    self.switch_frame(PageFive)
                    return
                if keypad == '*':
                    self.switch_frame(PageEight)
                    return
                if keypad == '#':
                    self.switch_frame(PageTwo)
                    return
                print(keypad)

    def KeypadBalance(self):
        while True:
            keypad = API.arduino2.read()
            keypad = keypad.decode()
            if keypad:
                if keypad == '*':
                    self.switch_frame(PageEight)
                    return
                if keypad == '#':
                    self.switch_frame(PageTwo)
                    return
                print(keypad)

    def KeypadBills(self):
        while True:
            keypad = API.arduino2.read()
            keypad = keypad.decode()
            if keypad:
                if keypad == 'A' and checkNotes:
                    check = API.withdraw()
                    if check == 0:
                        API.charityChoice = 0
                        API.sentNotes()
                        self.switch_frame(PageSeven)
                        return
                    else:
                        self.switch_frame(PageEight)
                        return
                if keypad == 'B' and (API.output[4:8] == 'ABNA' or API.output[4:8] == 'THOT'):
                    API.charityChoice = 1
                    API.charity()
                    self.switch_frame(PageSeven)
                    return
                if keypad == '*':
                    self.switch_frame(PageEight)
                    return
                if keypad == '#':
                    self.switch_frame(PageTwo)
                    return
                print(keypad)

    def KeypadReceipt(self):
        while True:
            keypad = API.arduino2.read()
            keypad = keypad.decode()
            if keypad:
                if keypad == 'A' and API.charityChoice == 0:
                    API.printReceipt()
                    self.after(20000, lambda: self.switch_frame(PageEight))
                    return
                if keypad == 'B':
                    self.switch_frame(PageEight)
                if keypad == 'C' and API.output[4:8] == 'ABNA':
                    API.digitalReceipt()
                    self.switch_frame(PageEight)
                    return
                if keypad == 'D' and API.output[4:8] == 'ABNA' and API.charityChoice == 0:
                    API.digitalReceipt()
                    API.printReceipt()
                    self.after(20000, lambda: self.switch_frame(PageEight))
                    return
                if keypad == '*':
                    self.switch_frame(PageEight)
                    return
                if keypad == '#':
                    self.switch_frame(PageTwo)
                    return
                print(keypad)

    def KeypadPincode(self):
        check = API.keypad()
        if check:
            self.switch_frame(PageTwo)
        else:
            self.switch_frame(PageEight)

    def customAmount(self):
        page = API.amountKeypad()
        if page == 0:
            self.switch_frame(PageSix)
        if page == 1:
            self.switch_frame(PageEight)
        if page == 2:
            self.switch_frame(PageTwo)
        if page == 3:
            self.switch_frame(PageEight)

    def logout(self):
        API.APIlogout()
        self.after(5000, lambda: self.switch_frame(StartPage))


# start page
class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/beginscherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)
        API.startArduino()

        self.x = threading.Thread(target=master.checkRFID)
        self.x.start()


# pincode-check
class PageOne(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/pincode-check-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)
        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        abortButton.place(x=80, y=780)

        self.x = threading.Thread(target=master.KeypadPincode)
        self.x.start()


# option page
class PageTwo(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/Keuzemenu-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        self.wd = tk.PhotoImage(file='images/withdrawknop.png')
        withdrawButton = tk.Button(self, image=self.wd, borderwidth=0,
                                   command=lambda: master.switch_frame(PageThree))

        self.bal = tk.PhotoImage(file='images/balanceknop.png')
        balButton = tk.Button(self, image=self.bal, command=lambda: master.switch_frame(PageFour), borderwidth=0)

        self.fast = tk.PhotoImage(file='images/fast70knop.png')
        fastButton = tk.Button(self, image=self.fast, command=lambda: master.switch_frame(PageSix), borderwidth=0)

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        withdrawButton.place(x=1400, y=500)
        balButton.place(x=1400, y=640)
        fastButton.place(x=1400, y=780)
        abortButton.place(x=80, y=780)

        self.x = threading.Thread(target=master.KeypadOption)
        self.x.start()


# withdraw page
class PageThree(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/pin-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        self.tien = tk.PhotoImage(file='images/knop10.png')
        tienButton = tk.Button(self, image=self.tien, command=lambda: master.switch_frame(PageSix), borderwidth=0)

        self.twintig = tk.PhotoImage(file='images/knop20.png')
        twintigButton = tk.Button(self, image=self.twintig, command=lambda: master.switch_frame(PageSix),
                                  borderwidth=0)

        self.vijftig = tk.PhotoImage(file='images/knop50.png')
        vijftigButton = tk.Button(self, image=self.vijftig, command=lambda: master.switch_frame(PageSix),
                                  borderwidth=0)

        self.custom = tk.PhotoImage(file='images/knopcustom.png')
        customButton = tk.Button(self, image=self.custom, command=lambda: master.switch_frame(PageFive),
                                 borderwidth=0)

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: master.switch_frame(PageTwo), borderwidth=0)

        tienButton.place(x=1400, y=500)
        twintigButton.place(x=1400, y=640)
        vijftigButton.place(x=1400, y=780)
        customButton.place(x=1400, y=920)

        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)

        self.x = threading.Thread(target=master.KeypadWithdraw)
        self.x.start()


# Balance page
class PageFour(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/Saldo-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        API.balance()

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: master.switch_frame(PageTwo), borderwidth=0)

        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)

        self.x = threading.Thread(target=master.KeypadBalance)
        self.x.start()


# custom amount page
class PageFive(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/custom-geld-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: master.switch_frame(PageTwo), borderwidth=0)

        enterButton = tk.Button(self, text="Enter [A]", font="CenturyGothic 30 bold",
                                command=lambda: master.switch_frame(PageSix), borderwidth=0)

        enterButton.place(x=850, y=800)

        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)

        self.x = threading.Thread(target=master.customAmount)
        self.x.start()


# Choice of bills
class PageSix(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/biljet-keuze-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: master.switch_frame(PageTwo), borderwidth=0)

        global checkNotes

        checkNotes = API.bills()
        if checkNotes:
            notesButton = tk.Button(self, text=API.notes, font="CenturyGothic 28 bold", command=None, borderwidth=5,
                                    bg='#009D96', fg='white', highlightbackground="white")
            notesButton.place(x=1200, y=640)
        if API.output[4:8] == 'ABNA' or API.output[4:8] == 'THOT':
            charityButton1 = tk.Button(self, text="Donate to Diergaarde blijdorp [B]", font="CenturyGothic 22 bold",
                                       command=None, borderwidth=5,
                                       bg='#009D96', fg='white', highlightbackground="white")
            charityButton1.place(x=1200, y=780)

        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)

        self.x = threading.Thread(target=master.KeypadBills)
        self.x.start()


# Receipt screen
class PageSeven(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        API.transactionNo()
        self.bg_image = tk.PhotoImage(file='images/Bonnetjes-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)
        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: master.switch_frame(PageTwo), borderwidth=0)

        self.yes = tk.PhotoImage(file='images/yesknop.png')
        yesButton = tk.Button(self, image=self.yes, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.no = tk.PhotoImage(file='images/noknop.png')
        noButton = tk.Button(self, image=self.no, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        if API.output[4:8] == 'ABNA':
            self.online = tk.PhotoImage(file='images/onlineknop.png')
            onlineButton = tk.Button(self, image=self.online, command=lambda: master.switch_frame(PageEight),
                                     borderwidth=0)
            onlineButton.place(x=1400, y=780)
            if API.charityChoice == 0:
                self.physDig = tk.PhotoImage(file='images/physicaldigital.png')
                physDigButton = tk.Button(self, image=self.physDig, command=lambda: master.switch_frame(PageEight),
                                          borderwidth=0)
                physDigButton.place(x=1400, y=920)

        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)

        if API.charityChoice == 0:
            yesButton.place(x=1400, y=500)

        noButton.place(x=1400, y=640)

        self.x = threading.Thread(target=master.KeypadReceipt)
        self.x.start()


# Endscreen
class PageEight(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/Eindscherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)
        API.endArduino()
        self.x = threading.Thread(target=master.logout())
        self.x.start()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
