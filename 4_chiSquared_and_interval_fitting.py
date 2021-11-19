"""
Example of calculating chi squared and fitting in two different ranges. 
Model stores parameters separetly for different intervals.
To specify intervals use: x.setRange("signal", -5, 5)
By default model will plot last specified interval
"""


from ROOT import TH1F, TFile, RooRealVar, TCanvas, RooDataHist, RooFit, RooGaussian, kTRUE, RooArgList, RooAddPdf, TLatex, RooPolynomial, kBlack, kRed, kDashed
from numpy import random
"""hh = TH1F("hh", "The hist", 100, -5, 5)
hh.FillRandom("gaus", 10000)
baseline = 50
noise = 5
for i in range(hh.GetNbinsX()):
    hh.SetBinContent(i+1, hh.GetBinContent(i+1) +baseline+ random.exponential(noise) // 1)
_file0 = TFile("data.root", "RECREATE")
hh.Write()
_file0.Close()"""
_file0 = TFile("data.root", "READ")
hh = _file0.Get("hh")

#Save data in RooDataHist
x = RooRealVar("x", "x", -5, 5)
data = RooDataHist("data", "dataset with x", RooArgList(x), hh)

xframe = x.frame(RooFit.Title("Fitting a sub range"))
xframe_right = x.frame(RooFit.Title("Fitting full range"))

data.plotOn(xframe)
data.plotOn(xframe_right)

c1 = TCanvas("c1", "c1", 1200, 600)
c1.Divide(2,1)
c1.cd(1)
xframe.Draw()

#Create PDF
mean = RooRealVar("mean","MeanofGaussian",0,-10,10)
sigma = RooRealVar("sigma","WidthofGaussian",3,-10,10)
gauss = RooGaussian("gauss","gauss(x,mean,sigma)",x,mean,sigma)
g1sig = RooRealVar("g1sig","gauss1 amplitude", 10, 0, 100000.0) 

# Build signal PDF: f1
signalPDF = RooAddPdf("signalPDF", "g1sig * g1", RooArgList(gauss), RooArgList(g1sig)) 

# Construct bkg function
bkgPDF = RooPolynomial("bkgPDF", "bkgPDF", x) # flat background

# Construct signal+bkg PDF
f = RooRealVar("f", "f", 0.5, 0, 1)
model = RooAddPdf("model", "model", RooArgList(gauss, bkgPDF), RooArgList(f))

# Construct final model with amplitude
m1 = RooRealVar("m1","model amplitude", 10, 0, 100000.0) 
model_n = RooAddPdf("model_n", "model * m1", RooArgList(model), RooArgList(m1)) 

# Fit full range
# ----------------------------------
#mean.setConstant(kTRUE); #fix mean
sigma.setRange(0.1, 3); # change range for sigma
#gauss.fitTo(data, RooFit.PrintLevel(-1)); # ffit gauss on data
r_full  = model_n.fitTo(data, RooFit.Save(kTRUE), RooFit.PrintLevel(-1))

# Fit partial range 
# ----------------------------------
x.setRange("signal", -2, 2)
r_sig = model_n.fitTo(data,RooFit.Save(kTRUE),RooFit.Range("signal"))
#PrintLevel(-1) almost no output
# Minos(kTRUE)?

mean.Print()
sigma.Print()

#Show parameters on plot
"""signalPDF.paramOn(xframe, RooFit.Layout(0.55, 0.9, 0.9), 
                                   RooFit.Format("NEU", RooFit.AutoPrecision(1)))
signalPDF.plotOn(xframe)"""

model_n.paramOn(xframe, RooFit.Layout(0.65, 0.9, 0.9), 
                                   RooFit.Format("NEU", RooFit.AutoPrecision(1)))
model_n.plotOn(xframe, RooFit.Components(
    "gauss"), RooFit.LineColor(kBlack), RooFit.LineStyle(kDashed))
model_n.plotOn(xframe, RooFit.Components(
    "bkgPDF"), RooFit.LineColor(kRed), RooFit.LineStyle(kDashed))

model_n.plotOn(xframe)

#xframe.GetYaxis().SetTitleOffset(1.4)
xframe.Draw()
chi2txt = TLatex()
chi2txt.SetNDC()
chi2txt.DrawLatex(0.13, 0.83, "\chi^2/n.d.f = %0.3f" %xframe.chiSquare()) #Put chi² on plot

print("Result of fit in signal region")
r_sig.Print()

c1.cd(2)
model_n.paramOn(
    xframe_right, 
    RooFit.Range(""), # or use Range("Full")
    RooFit.Layout(0.65, 0.9, 0.9), 
    RooFit.Format("NEU", RooFit.AutoPrecision(2)))

model_n.plotOn(xframe_right, RooFit.Range(""))
xframe_right.Draw()
chi2txt = TLatex()
chi2txt.SetNDC()
chi2txt.DrawLatex(0.13, 0.83, "\chi^2/n.d.f = %0.3f" %xframe_right.chiSquare()) #Put chi² on plot

print("Result of fit on all data")
r_full.Print()

c1.Print("tmp.pdf")