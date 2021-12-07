from ROOT import TH1F, TFile, RooRealVar, TCanvas, RooDataHist, RooFit, RooGaussian, kTRUE, kFALSE, RooArgList, RooAddPdf, TLatex, RooPolynomial, kBlack, kRed, kDashed
from numpy import random

###################
# Fit in two different ranges different background functions
# Signal - gauss, background - constant or first polynomial or squar root function
###################

## Generation of data sample
"""hh = TH1F("hh", "The hist", 100, -5, 5)
hh.FillRandom("gaus", 10000)
baseline = 50
noise = 5
for i in range(hh.GetNbinsX()):
    hh.SetBinContent(i+1, hh.GetBinContent(i+1) + (0.1*i*i) // 1 + baseline+ random.exponential(noise) // 1)
_file0 = TFile("data_gaus_quad.root", "RECREATE")
hh.Write()
_file0.Close()"""
_file0 = TFile("data_gaus_quad.root", "READ")
hh = _file0.Get("hh")

#Save data in RooDataHist
x = RooRealVar("x", "x", -5, 5)
data = RooDataHist("data", "dataset with x", RooArgList(x), hh)

xframe = x.frame(RooFit.Title("Fitting a sub range"))
xframe_right = x.frame(RooFit.Title("Fitting full range"))

# Create canvas before any drawing of the frames.
# ------------------
c1 = TCanvas("c1", "c1", 1200, 600)
c1.Divide(2,1)
c1.cd(1)

# Plot data on frame
# ------------------
data.plotOn(xframe)
data.plotOn(xframe_right)

# Construct signal PDF
mean = RooRealVar("mean","MeanofGaussian",0,-1,1)
sigma = RooRealVar("sigma","WidthofGaussian",1,0.01,5)
gauss = RooGaussian("gauss","gauss(x,mean,sigma)",x,mean,sigma)

# Construct the background pdf
a0 = RooRealVar("a0", "a0", 0.03, -1, 1)
a1 = RooRealVar("a1", "a1", 0.3, -1, 1)
bkg_constant = RooPolynomial("bkg_constant", "bkg_constant", x) 
bkg_lin = RooPolynomial("bkg_lin", "bkg_lin", x, RooArgList(a0))
bkg_quad = RooPolynomial("bkg_quad", "bkg_quad", x, RooArgList(a1, a0))

# Construct signal+bkg PDF
f = RooRealVar("f", "f", 0.6, 0, 1)
model = RooAddPdf("model", "model", RooArgList(gauss, bkg_quad), RooArgList(f))

# Construct final model with amplitude
m1 = RooRealVar("m1","model amplitude", 15000, 0, 100000.0) 
model_n = RooAddPdf("model_n", "model * m1", RooArgList(model), RooArgList(m1))


# Fit partial range 
# ----------------------------------
x.setRange("signal", -2, 2)
r_sig = model_n.fitTo(data,RooFit.Save(kTRUE),RooFit.Range("signal"))

# Plot partial range
# By default it plots latest fit
# -------------------
model_n.paramOn(
    xframe,
    RooFit.Range("signal"),
    RooFit.Layout(0.65, 0.9, 0.9), 
    RooFit.Format("NEU", RooFit.AutoPrecision(1)))

model_n.plotOn(
    xframe,
    RooFit.Range("signal"),
    RooFit.Components("gauss"),
    RooFit.LineColor(kBlack),
    RooFit.LineStyle(kDashed))
    
model_n.plotOn(
    xframe,
    RooFit.Range("signal"),
    RooFit.Components("bkg_quad"),
    RooFit.LineColor(kRed),
    RooFit.LineStyle(kDashed))

model_n.plotOn(
    xframe,
    RooFit.Range("signal")
    )

# Plot frame on pad
c1.cd(1)
xframe.Draw()
chi2txt = TLatex()
chi2txt.SetNDC()
chi2txt.DrawLatex(0.13, 0.83, "\chi^2/n.d.f = %0.3f" %xframe.chiSquare()) #Put chi² on plot

# Fit full range
# ----------------------------------
#mean.setConstant(kTRUE); #fix mean
#sigma.setRange(0.1, 3); # change range for sigma
x.setRange("Full", -5, 5)
r_full = model_n.fitTo(data, RooFit.Save(kTRUE), RooFit.PrintLevel(-1), RooFit.Range("Full"))

# Plot full range
# ------------------
model_n.paramOn(
    xframe_right, 
    RooFit.Range("Full"), # or use Range("Full")
    RooFit.Layout(0.65, 0.9, 0.9), 
    RooFit.Format("NEU", RooFit.AutoPrecision(2)))

model_n.plotOn(xframe_right,
    RooFit.Range(""),
    RooFit.Components(
    "gauss"),
    RooFit.LineColor(kBlack),
    RooFit.LineStyle(kDashed))
    
model_n.plotOn(xframe_right,
    RooFit.Range(""),
    RooFit.Components(
    "bkg_quad"),
    RooFit.LineColor(kRed),
    RooFit.LineStyle(kDashed))

model_n.plotOn(
    xframe_right,
    RooFit.Range("Full"))

# Plot frame on pad
c1.cd(2)
xframe_right.Draw()
chi2txt_2 = TLatex()
chi2txt_2.SetNDC()
chi2txt_2.DrawLatex(0.13, 0.73, "\chi^2/n.d.f = %0.3f" %xframe_right.chiSquare()) #Put chi² on plot


c1.Print("5.3_quad.pdf")

#_file0.Close()
r_full.Print()