import tkinter as tk
import time
import serial
# import database_python as db
# import arduino_python as ap
# import arduino_keypad as ak
import accountshi as acc
import threading
import hashlib


class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('ABN-MANBRO')
        self._frame = None
        self.switch_frame(StartPage)
        self.geometry('1920x1080')

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
        acc.rfid()
        self.switch_frame(PageOne)

    def KeypadWithdraw(self):
        ser = serial.Serial("COM3", 9600, timeout=1)
        while True:
            keypad = ser.read()
            keypad = keypad.decode()
            if keypad:
                if keypad == 'A':
                    self.switch_frame(PageThree)
                if keypad == 'B':
                    self.switch_frame(PageFour)
                if keypad == 'C':
                    self.switch_frame(PageSix)
                print(keypad)
                return

    def KeypadPincode(self):
        if acc.keypad():
            self.switch_frame(PageTwo)


# start page
class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/beginscherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button1 = tk.Button(self, text="Go to Page One",
                            command=lambda: master.switch_frame(PageOne))
        button1.pack()

        self.x = threading.Thread(target=master.checkRFID)
        self.x.start()


# pincode-check
class PageOne(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/pincode-check-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        tk.Button(self, text="Page 2",
                  command=lambda: master.switch_frame(PageTwo)).pack()

        self.x = threading.Thread(target=master.KeypadPincode)
        self.x.start()


# option page
class PageTwo(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/Keuzemenu-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button = tk.Button(self, text="Go to the start page", command=lambda: master.switch_frame(StartPage))

        self.wd = tk.PhotoImage(file='images/withdrawknop.png')
        withdrawButton = tk.Button(self, image=self.wd, borderwidth=0,
                                   command=lambda: master.switch_frame(PageThree))

        self.bal = tk.PhotoImage(file='images/balanceknop.png')
        balButton = tk.Button(self, image=self.bal, command=lambda: master.switch_frame(PageFour), borderwidth=0)

        self.fast = tk.PhotoImage(file='images/fast70knop.png')
        fastButton = tk.Button(self, image=self.fast, command=None, borderwidth=0)

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        button.pack()
        withdrawButton.place(x=1400, y=500)
        balButton.place(x=1400, y=640)
        fastButton.place(x=1400, y=780)
        abortButton.place(x=80, y=780)

        self.x = threading.Thread(target=master.KeypadWithdraw)
        self.x.start()


# withdraw page
class PageThree(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/pin-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button = tk.Button(self, text="Go to the start page", command=lambda: master.switch_frame(StartPage))

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

        button.pack()
        tienButton.place(x=1400, y=500)
        twintigButton.place(x=1400, y=640)
        vijftigButton.place(x=1400, y=780)
        customButton.place(x=1400, y=920)

        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)


# Balance page
class PageFour(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/Saldo-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        # self.balance = db.getBalance()
        # balanceBox = tk.Entry(self, textvariable=self.balance, font=('Century Gothic', 30, 'bold'), fg='black')
        # balanceBox.insert("end", self.balance)
        # balanceBox.config(state='readonly')

        button = tk.Button(self, text="Go to the start page", command=lambda: master.switch_frame(StartPage))

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: master.switch_frame(PageTwo), borderwidth=0)

        # balanceBox.place(x=1100, y=500)
        button.pack()
        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)


# custom amount page
class PageFive(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/custom-geld-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button = tk.Button(self, text="Go to the start page", command=lambda: master.switch_frame(StartPage))

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: master.switch_frame(PageTwo), borderwidth=0)

        inputbox = tk.Entry(self, font="CenturyGothic 30 bold")

        enterButton = tk.Button(self, text="Enter", font="CenturyGothic 30 bold", command=None, borderwidth=0)

        button.pack()
        inputbox.place(x=730, y=640, width=500, height=100)
        enterButton.place(x=800, y=800)

        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)


# Choice of bills
class PageSix(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/biljet-keuze-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button = tk.Button(self, text="Go to the start page", command=lambda: master.switch_frame(StartPage))

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: master.switch_frame(PageTwo), borderwidth=0)

        testButton = tk.Button(self, text="Ga naar het bonnetjes scherm",
                               command=lambda: master.switch_frame(PageSeven))

        button.pack()
        testButton.pack()
        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)


# Receipt screen
class PageSeven(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/Bonnetjes-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button = tk.Button(self, text="Go to the start page", command=lambda: master.switch_frame(StartPage))

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: master.switch_frame(PageTwo), borderwidth=0)

        self.yes = tk.PhotoImage(file='images/yesknop.png')
        yesButton = tk.Button(self, image=self.yes, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        self.no = tk.PhotoImage(file='images/noknop.png')
        noButton = tk.Button(self, image=self.no, command=lambda: master.switch_frame(PageEight), borderwidth=0)

        button.pack()
        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)
        yesButton.place(x=1400, y=640)
        noButton.place(x=1400, y=780)


# Endscreen
class PageEight(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.bg_image = tk.PhotoImage(file='images/Eindscherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        self.after(3000, lambda: master.switch_frame(StartPage))


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
