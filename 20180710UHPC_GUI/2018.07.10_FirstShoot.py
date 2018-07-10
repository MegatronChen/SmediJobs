__author__ = 'MC_SMEDI'

# 2018.07.10 First try

import PIL
from tkinter import *
from tkinter.messagebox import *
from scipy import optimize



class UHPC_Calculation:
    def __init__(self, parent=None):
        self.InputLabels = ["bf'(mm)", "hf'(mm)", "bw(mm)", "hf(mm)", "bf(mm)", "h(mm)", "UHPC-ud", "Ap(mm^2)", "fpd(MPa)",
                            "As(mm^2)", "fsd(MPa)", "asp(mm)", "futud(MPa)", "Ec(MPa)"]
        self.InputDefaultValue = [1220, 120, 100, 120, 800, 850, 1.5e-3, 2363, 1260,
                                  2455, 330, 65, 4.74, 50000]
        self.InputValueSet = [None] * len(self.InputLabels)

        self.InputZone = Frame(parent)
        self.InputZone.pack(side=TOP, expand=YES, fill=BOTH)

        self.ResultZone = Frame(parent).pack(side=TOP, expand=YES, fill=X, pady=5)
        self.CalcuX = Button(self.ResultZone, text='截面受压区高度', command=self.calculate_x).pack(side=LEFT,expand=YES, fill=X)
        self.CalcuMu = Button(self.ResultZone, text='截面抗弯承载力', command=self.calculate_x).pack(side=RIGHT,expand=YES, fill=X)

        row = 0
        for Input in self.InputLabels:
            lab = Label(self.InputZone, text=Input, relief=RIDGE, width=20)
            ent = Entry(self.InputZone, relief=SUNKEN, width=20)
            lab.grid(row=row, column=0)
            ent.grid(row=row, column=1)
            # lab = Label(self.InputZone, text=Input, relief=RIDGE)
            # ent = Entry(self.InputZone, relief=SUNKEN)
            # lab.grid(row=row, column=0, sticky=NSEW)
            # ent.grid(row=row, column=1, sticky=NSEW)
            self.InputValueSet[row] = DoubleVar()
            ent.config(textvariable=self.InputValueSet[row])
            self.InputValueSet[row].set(self.InputDefaultValue[row])
            row += 1

    def UnitsTransform(self):
        self.ParaForCal = dict(zip(self.InputLabels,self.InputValueSet))
        for label in self.ParaForCal:
            if label == "UHPC-ud":
                self.ParaForCal[label] = self.ParaForCal[label].get()
            elif ("mm" in label) and ("mm^2" not in label):
                self.ParaForCal[label] = self.ParaForCal[label].get() / 1e3
            elif ("mm^2" in label):
                self.ParaForCal[label] = self.ParaForCal[label].get() / 1e6
            elif ("MPa" in label):
                self.ParaForCal[label] = self.ParaForCal[label].get() * 1e6
            else:
                showerror('Units Transform error!','The {0} can not be transformed correctly! Please check!'.format(self.ParaForCal[label]))
        return self.ParaForCal


    def calculate_x(self):
        self.ParaForCal = self.UnitsTransform()
        hf1 = self.ParaForCal["hf'(mm)"]
        bf1 = self.ParaForCal["bf'(mm)"]
        bw = self.ParaForCal["bw(mm)"]
        hf = self.ParaForCal["hf(mm)"]
        bf = self.ParaForCal["bf(mm)"]
        h = self.ParaForCal["h(mm)"]
        eu = self.ParaForCal["UHPC-ud"]
        Ap = self.ParaForCal["Ap(mm^2)"]
        fpd = self.ParaForCal["fpd(MPa)"]
        As = self.ParaForCal["As(mm^2)"]
        fsd = self.ParaForCal["fsd(MPa)"]
        asp = self.ParaForCal["asp(mm)"]
        fud = self.ParaForCal["futud(MPa)"]
        Ec = self.ParaForCal["Ec(MPa)"]

        def AxisEquationOuter(x):
            Fcf = hf1 * bf1 * (x-hf1/3) / (h-x) * 3 * eu * Ec
            Fcw = x * bw * 2/3 * x / (h-x) * 3 * eu * Ec
            Fts = Ap * fpd + As * fsd
            Ftc = 0.9 * fud * (hf * (bf-bw) + (h-x) * bw * 0.9)
            AxisEquationError = (Fcf+Fcw) - (Fts+Ftc)
            return AxisEquationError

        def AxisEquationInner(x):
            Fcf = 2/3 * x / (h-x) * 3 * eu * Ec
            Fcw = 0
            Fts = Ap * fpd + As * fsd
            Ftc = 0.9 * fud * (hf * (bf-bw) + (h-x) * bw * 0.9)
            AxisEquationError = (Fcf+Fcw) - (Fts+Ftc)
            return AxisEquationError

        Outer_x = optimize.fsolve(AxisEquationOuter, 0.2*h)
        Inner_x = optimize.fsolve(AxisEquationInner, 0.2*h)

        if Outer_x >= hf1:
            self.x = Outer_x[0]
            showinfo('受压区高度计算结果','受压区位于腹板内；\n受压区高度为:{0:>5.1f}mm'.format(1000*self.x))
        else:
            if Inner_x <= hf1:
                self.x = Inner_x[0]
                showinfo('受压区高度计算结果','受压区位于上翼缘内；\n受压区高度为:{0:>5.1f}mm'.format(1000*self.x))
            else:
                showerror('x error!', '受压区高度的计算有误，请重新检查输入！')




if __name__ == '__main__':
    root = Tk()
    root.iconbitmap(r'SMEDI.ico')

    ProgramTitle = Label(root, text='SMEDI UHPC Capacity Calculator\nVersion1.0')
    TitleFont = ('times',12,'bold')
    ProgramTitle.config(font=TitleFont)
    ProgramTitle.config(height=5, width=30)
    ProgramTitle.pack(side=TOP, expand=YES, fill=X, pady=8)

    thread1 = UHPC_Calculation(root)

    root.mainloop()