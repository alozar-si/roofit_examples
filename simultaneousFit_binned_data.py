'''
Simultaneus fit of binned data imported from two TH1 histograms
NOTE sigma is shared between failed and passed sample
'''

from ROOT import TLatex, TFile, TCanvas, TF1, TH1, TH1F, TH2F, gROOT, TString, TMath, gStyle, TRatioPlot, TGraphErrors, TLegend, TGraph
from ROOT import RooRealVar, RooGaussian, RooAddPdf, RooGenericPdf, RooFit, RooArgList, RooDataHist, RooArgSet, RooDataSet
from ROOT import kRed, kBlack, kBlue, kGreen, kTRUE, kDashed, kDotted, kFALSE, gSystem
from ROOT import RooMsgService, RooCategory, RooSimultaneous, RooProdPdf, gPad, RooPolynomial
from ROOT.std import map as std_map

from array import array
import numpy as np

 
# Create model for physics sample
# -------------------------------------------------------------
 
# Create observables
x = RooRealVar("x", "x", -5.05, 5.05)
y = RooRealVar("y", "y", 0, 1)
# Construct signal pdf
mean = RooRealVar("mean", "mean", 0, -5, 5)
sigma = RooRealVar("sigma", "sigma", 0.3, 0.1, 10)
gx = RooGaussian("gx", "gx", x, mean, sigma)
 
# Construct background pdf
a0 = RooRealVar("a0", "a0", -0.1, -1, 1)
a1 = RooRealVar("a1", "a1", 0.004, -1, 1)
px = RooPolynomial("px", "px", x, RooArgList(a0, a1), 1)
 
# Construct composite pdf
f = RooRealVar("f", "f", 0.2, 0., 1.)
model = RooAddPdf("model", "model", RooArgList(gx, px), RooArgList(f))
 
# Create model for control sample
# --------------------------------------------------------------
 
# Construct signal pdf.
# NOTE that sigma is shared with the signal sample model
mean_ctl = RooRealVar("mean_ctl", "mean_ctl", -3, -5, 5)
gx_ctl = RooGaussian("gx_ctl", "gx_ctl", x, mean_ctl, sigma)
 
# Construct the background pdf
a0_ctl = RooRealVar("a0_ctl", "a0_ctl", -0.1, -1, 1)
a1_ctl = RooRealVar("a1_ctl", "a1_ctl", 0.5, -0.1, 1)
px_ctl = RooPolynomial(
    "px_ctl", "px_ctl", x, RooArgList(a0_ctl, a1_ctl), 1)
f_ctl = RooRealVar("f_ctl", "f_ctl", 0.5, 0., 1.)
model_ctl = RooAddPdf("model_ctl", "model_ctl", RooArgList(gx_ctl, px_ctl), RooArgList(f_ctl))

# Generate binned data samples
# ---------------------------------------------------------------
data1 = TH1F("data1", "data1", 101, -5-0.05, 5+0.05)
data2 = TH1F("data2", "data2", 101, -5-0.05, 5+0.05)
dataCombined = TH2F("dataCombined", "dataCombined", 101, -5-0.05, 5+0.05, 2, 0, 1)
data1.FillRandom("gaus", 1000)
data2.FillRandom("gaus", 10000)

# Add some backgound
for i in range(data1.GetNbinsX()):
    data1.SetBinContent(i+1, data1.GetBinContent(i+1) + i + 5)
    data2.SetBinContent(i+1, data2.GetBinContent(i+1) + 1.5*i + 10)



# Construct category
# ---------------------------------------------------------------
myCat = RooCategory("myCat", "PID pass/fail category")
myCat.defineType("passed", 1)
myCat.defineType("failed", 0)

# Convert binned data into RooDataHist
# ---------------------------------------------------------------
map_data = std_map("std::string, TH1*")()
map_data.insert(("failed", data1))
map_data.insert(("passed", data2))
combined = RooDataHist("combined", "combined", RooArgList(x), myCat, map_data)

# 1. Construct a simultaneous pdf using category sample as index
# ---------------------------------------------------------------
simPdf = RooSimultaneous("simPdf", "simultaneous pdf", myCat)
 
# Associate model with the physics state and model_ctl with the control
# state
simPdf.addPdf(model, "failed")
simPdf.addPdf(model_ctl, "passed")


# FIT
# ---------------------------------------------------------------
# 2. Fit model to data
simPdf.fitTo(combined)

# 3. Create frame
frame1 = x.frame(RooFit.Bins(30), RooFit.Title("Passed sample"))
frame2 = x.frame(RooFit.Bins(30), RooFit.Title("Failed sample"))

# 4. Put data on frame
combined.plotOn(frame1, RooFit.Cut("myCat==myCat::passed"))
combined.plotOn(frame2, RooFit.Cut("myCat==myCat::failed"))

sampleSet = RooArgSet(myCat)
# 5. Put model on frame
# put one component
simPdf.plotOn(frame1, RooFit.Slice(myCat, "passed"), RooFit.Components(
    "px_ctl"), RooFit.ProjWData(sampleSet, combined), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed))
# put one component
simPdf.plotOn(frame1, RooFit.Slice(myCat, "passed"), RooFit.Components(
    "gx_ctl"), RooFit.ProjWData(sampleSet, combined), RooFit.LineColor(kBlack), RooFit.LineStyle(kDashed))
# put whole model
simPdf.plotOn(frame2, RooFit.Slice(myCat, "failed"), RooFit.ProjWData(sampleSet, combined), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed))
simPdf.paramOn(frame2, RooFit.Layout(0.55, 0.9, 0.9), RooFit.Format("NEU", RooFit.AutoPrecision(1)))

c = TCanvas("c", "c", 1000, 600)
c.Divide(2)
c.cd(1)
frame1.Draw()
c.cd(2)
frame2.Draw()
