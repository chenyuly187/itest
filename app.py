# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import filedialog
import itest
from tkinter.scrolledtext import ScrolledText
import os
import sys
import webbrowser
import settings
from utils.support import get_newest_file_of_path


class RedirectText(object):
    def __init__(self, text_ctrl):
        self.output = text_ctrl

    def write(self, string):
        self.output.insert(END, string)

    def writelines(self, lines):
        self.output.insert(END, lines)


class App:
    def __init__(self, master):
        self.case_file = None
        self.path = None

        font = ('Microsoft YaHei', 8)
        frame = Frame(master, width=900)
        frame.pack()

        self.button_choosefile = Button(frame, font=font, text='选择要执行的用例', width=15, command=self.choose_case_file)
        self.button_choosefile.pack(cnf={"padx": 5, "pady": 5, "side": "left"})

        self.entry_casefile = Entry(frame, cnf={"width": 60}, font=font)
        self.entry_casefile.pack(cnf={"padx": 5, "pady": 5, "side": "left"})

        # self.label_report = Label(frame, font=font, text='报告文件名')
        # self.label_report.pack(cnf={"padx": 5, "pady": 5, "side": "left"})
        # self.entry_report = Entry(frame, cnf={"width": 20}, font=font)
        # self.entry_report.pack(cnf={"padx": 5, "pady": 5, "side": "left"})

        self.button_run = Button(frame, font=font, text='执行', command=self.run, width=8)
        self.button_run.pack(cnf={"padx": 5, "pady": 5, "side": "left"})

        frame1 = Frame(master)
        frame1.pack()

        # self.label_console = Label(frame1, font=font, text='Console:')
        # self.label_console.pack(side=LEFT)

        self.text_console = ScrolledText(frame1, cnf={"width": "120", "height": "20"}, font=font, stat='normal')
        self.text_console.pack(cnf={"padx": 5, "pady": 5, "side": LEFT})

        redir = RedirectText(self.text_console)
        sys.stdout = redir
        sys.stderr = redir

        frame2 = Frame(master)
        frame2.pack()

        self.button_report = Button(frame, font=font, text='查看报告', command=self.report, width=10)
        self.button_report.pack(cnf={"padx": 5, "pady": 5, "side": "left"})

        self.button_log = Button(frame, font=font, text='查看log', command=self.log, width=10)
        self.button_log.pack(cnf={"padx": 5, "pady": 5, "side": "left"})

    def choose_case_file(self):
        self.case_file = filedialog.askopenfilename()
        if self.case_file:
            self.entry_casefile.delete(0, END)
            self.entry_casefile.insert(INSERT, self.case_file)
            self.entry_casefile.insert(INSERT, '\n')

            p = os.path.abspath(os.path.dirname(self.case_file) + os.sep + os.path.pardir)
            if p == os.path.abspath(settings.BASE_DIR):
                self.path = p

    def run(self):
        from importlib import reload
        reload(itest)
        p = self.path if self.path != os.path.abspath(settings.BASE_DIR) else None
        f = os.path.basename(self.case_file)
        r = os.path.splitext(f)[0]
        itest.runwithargs(path=p, case_file=f, reportfile=r)

    def report(self):
        p = self.path if self.path else settings.BASE_DIR
        reportf = get_newest_file_of_path(p+'\\report\\')[0]
        print('打开报告 %s ' % os.path.abspath(p+'\\report\\'+reportf))
        webbrowser.open(p+'\\report\\'+reportf)

    def log(self):
        print('打开日志 %s' % os.path.abspath(settings.BASE_DIR+'\\log\\itest.log'))
        os.popen('notepad %s' % (settings.BASE_DIR+'\\log\\itest.log'))

if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()

