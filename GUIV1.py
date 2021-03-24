import tkinter as tk  # python 3
from tkinter import font  as tkfont  # python 3


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Century Gothic', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree, PageFour, PageFive, PageSix, PageSeven, PageEight):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('1920x1080')
        self.bg_image = tk.PhotoImage(file='images/beginscherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button1 = tk.Button(self, text="Go to Page One",
                            command=lambda: controller.show_frame("PageOne"))
        button1.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('1920x1080')
        self.bg_image = tk.PhotoImage(file='images/pincode-check-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)
        # label = tk.Label(self, text="This is page 1", font=controller.title_font)
        # label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button2 = tk.Button(self, text="Go to Page Two",
                            command=lambda: controller.show_frame("PageTwo"))
        button.pack()
        button2.pack()


# Option page
class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('1920x1080')
        self.bg_image = tk.PhotoImage(file='images/Keuzemenu-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)
        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))

        self.wd = tk.PhotoImage(file='images/knoppreset.png')
        withdrawButton = tk.Button(self, image=self.wd, borderwidth=0,
                                   command=lambda: controller.show_frame('PageThree'))

        self.bal = tk.PhotoImage(file='images/balanceknop.png')
        balButton = tk.Button(self, image=self.bal, command=lambda: controller.show_frame("PageFour"), borderwidth=0)

        self.fast = tk.PhotoImage(file='images/fast70knop.png')
        fastButton = tk.Button(self, image=self.fast, command=None, borderwidth=0)

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=None, borderwidth=0)

        button.pack()
        withdrawButton.place(x=1400, y=500)
        balButton.place(x=1400, y=640)
        fastButton.place(x=1400, y=780)
        abortButton.place(x=80, y=780)


# withdraw page
class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('1920x1080')
        self.bg_image = tk.PhotoImage(file='images/pin-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))

        self.tien = tk.PhotoImage(file='images/knop10.png')
        tienButton = tk.Button(self, image=self.tien, command=lambda: controller.show_frame("PageSix"), borderwidth=0)

        self.twintig = tk.PhotoImage(file='images/knop20.png')
        twintigButton = tk.Button(self, image=self.twintig, command=lambda: controller.show_frame("PageSix"),
                                  borderwidth=0)

        self.vijftig = tk.PhotoImage(file='images/knop50.png')
        vijftigButton = tk.Button(self, image=self.vijftig, command=lambda: controller.show_frame("PageSix"),
                                  borderwidth=0)

        self.custom = tk.PhotoImage(file='images/knopcustom.png')
        customButton = tk.Button(self, image=self.custom, command=lambda: controller.show_frame("PageFive"),
                                 borderwidth=0)

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=None, borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: controller.show_frame("PageTwo"), borderwidth=0)

        button.pack()
        tienButton.place(x=1400, y=500)
        twintigButton.place(x=1400, y=640)
        vijftigButton.place(x=1400, y=780)
        customButton.place(x=1400, y=920)

        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)


# Balance page
class PageFour(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('1920x1080')
        self.bg_image = tk.PhotoImage(file='images/Saldo-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)
        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=None, borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: controller.show_frame("PageTwo"), borderwidth=0)

        button.pack()
        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)


# Custom amount
class PageFive(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('1920x1080')
        self.bg_image = tk.PhotoImage(file='images/custom-geld-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=None, borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: controller.show_frame("PageTwo"), borderwidth=0)

        inputbox = tk.Entry(self, font="CenturyGothic 30 bold")

        self.enterImg = tk.PhotoImage(file='images/legeknop.png')
        enterButton = tk.Button(self, text="Enter", font="CenturyGothic 30 bold", command=None, borderwidth=0)

        button.pack()
        inputbox.place(x=730, y=640, width=500, height=100)
        enterButton.place(x=800, y=800)

        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)


# Choice of bills
class PageSix(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('1920x1080')
        self.bg_image = tk.PhotoImage(file='images/biljet-keuze-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=None, borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: controller.show_frame("PageTwo"), borderwidth=0)

        self.test = tk.PhotoImage(file='images/legeknop.png')
        testButton = tk.Button(self, image=self.test, command=lambda: controller.show_frame("PageSeven"), borderwidth=0)

        button.pack()
        testButton.pack()
        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)


# Receipt screen
class PageSeven(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('1920x1080')
        self.bg_image = tk.PhotoImage(file='images/Bonnetjes-scherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))

        self.abort = tk.PhotoImage(file='images/abort knop.png')
        abortButton = tk.Button(self, image=self.abort, command=None, borderwidth=0)

        self.hs = tk.PhotoImage(file='images/homescreenknop.png')
        hsButton = tk.Button(self, image=self.hs, command=lambda: controller.show_frame("PageTwo"), borderwidth=0)

        self.yes = tk.PhotoImage(file='images/yesknop.png')
        yesButton = tk.Button(self, image=self.yes, command=lambda: controller.show_frame("PageEight"), borderwidth=0)

        self.no = tk.PhotoImage(file='images/noknop.png')
        noButton = tk.Button(self, image=self.no, command=lambda: controller.show_frame("PageEight"), borderwidth=0)

        button.pack()
        hsButton.place(x=80, y=640)
        abortButton.place(x=80, y=780)
        yesButton.place(x=1400, y=640)
        noButton.place(x=1400, y=780)


# Endscreen
class PageEight(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry('1920x1080')
        self.bg_image = tk.PhotoImage(file='images/Eindscherm.png')
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0)

        self.timer(controller)

    def timer(self, controller):
        self.after(5000, lambda: controller.show_frame("StartPage"))


if __name__ == "__main__":
    app = SampleApp()
    # app.state('zoomed')
    app.mainloop()
