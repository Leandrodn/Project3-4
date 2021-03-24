import tkinter as tk
import time

root = tk.Tk()
root.geometry('1920x1080')


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
        Label_datum.after(1000, clock)

    Label_tijd = tk.Label(self, text="", font=('Century Gothic', 34, 'bold'), fg="black", bg="white")
    Label_datum = tk.Label(self, text="", font=('Century Gothic', 20, 'bold'), fg="black", bg="white")
    Label_tijd.place(x=1550, y=80)
    Label_datum.place(x=1550, y=150)

    clock()


clockLabel()

root.mainloop()
