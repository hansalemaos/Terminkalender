from datetime import datetime
from time import localtime
from time import sleep
from win10toast import ToastNotifier
import kthread
import os
from tkinter import *
import sys
toaster = ToastNotifier()


class Terminkalender:
    def __init__(self):
        self.dead = False
        self.text_auf_editbutton = "Edit"
        self.buttonschrift = "Helvetica 16 bold"
        self.root = Tk(className='Terminkalender')
        self.haupframe_wo_alles_ist = Frame(self.root)
        self.seconds_before_and_after_to_display = 900
        self.sleeptime = 1
        self.canvas_im_hauptframe = Canvas(self.haupframe_wo_alles_ist)
        self.button_edit = Button(
            self.canvas_im_hauptframe,
            text=self.text_auf_editbutton,
            command=lambda: self.open_termin_file(),
            font=self.buttonschrift,
        )
        self.t = kthread.KThread(target=self.check_dates_inf, name="checkinf")
        self.t.start()


    def open_termin_file(self):
        os.popen(r"termine.txt")

    def read_txt_file(self):
        with open("termine.txt", mode="r", encoding="utf-8") as f:
            data = [x.strip() for x in f.readlines()]
        return data

    def mainloop(self):
        self.haupframe_wo_alles_ist.pack(fill=BOTH, expand=1)
        self.canvas_im_hauptframe.pack(side=LEFT, fill=BOTH, expand=1)
        self.button_edit.pack()
        self.root.protocol("WM_DELETE_WINDOW", self.onexit)
        self.root.mainloop()

    def onexit(self):
        try:
            self.root.quit()
        except Exception as Fehler:
            print(Fehler)
        self.dead = True
        try:
            self.t.terminate()
        except Exception as Fehler:
            print(Fehler)
        sys.exit()

    def check_dates_inf(self):
        while not self.dead:
            try:
                self.check_dates()
            finally:
                pass


    def check_dates(self):
        zeitmeldung = [zeit.split("_", maxsplit=1) for zeit in self.read_txt_file()]
        alldatestocheck = []
        for alltermine in zeitmeldung:
            try:
                allezeiten = [
                    [
                        int(x.strip().lstrip("0"))
                        for x in re.findall(r"\d+", alltermine[0])
                    ][:6]
                ]
                for einzelne_zeit in allezeiten:
                    day, month, year, hour, minute, second = einzelne_zeit
                    datumadden = datetime(year, month, day, hour, minute, second)
                    alldatestocheck.append((datumadden, alltermine[1]))
            except Exception as Fehler:
                print(Fehler)
        for einzelner_event in alldatestocheck:
            aktuellesdatum = datetime(
                localtime().tm_year,
                localtime().tm_mon,
                localtime().tm_mday,
                localtime().tm_hour,
                localtime().tm_min,
                localtime().tm_sec,
            )
            differenz = aktuellesdatum - einzelner_event[0]
            if abs(differenz.total_seconds()) < self.seconds_before_and_after_to_display:
                toaster.show_toast(
                    str(einzelner_event[0]),
                    einzelner_event[1],
                    icon_path=None,
                    duration=5,
                    threaded=True,
                )
        if not self.dead:
            sleep(self.sleeptime)
if __name__ == "__main__":
    Termin = Terminkalender()
    Termin.mainloop()
