'''
Only signal implemented
'''

from ROOT import TLatex, TFile, TCanvas, TF1, TH1, gROOT, TString, TMath, gStyle, TRatioPlot, TGraphErrors, TLegend, TGraph
from ROOT import RooRealVar, RooGaussian, RooAddPdf, RooGenericPdf, RooFit, RooArgList, RooDataHist, RooArgSet, RooDataSet
from ROOT import kRed, kBlack, kBlue, kGreen, kTRUE, kDashed, kDotted, kFALSE, gSystem, RooSimultaneous, RooCategory, RooProduct
import numpy as np

from ROOT import RooMsgService, RooProdPdf, RooRealSumPdf, RooEffProd, RooFormulaVar, RooEfficiency
RooMsgService.instance().setGlobalKillBelow(RooFit.WARNING)

fit_min = 0.988
fit_max = 1.065
fit_min_Segmented = fit_min
fit_max_Segmented = fit_max

# Create basic model
Mkk = RooRealVar("Mkk", "Mkk", fit_min, fit_max)
mean1 = RooRealVar("mean1","Mean of Gaussian 1",1.01944, 1.01, 1.03)
sigma1 = RooRealVar("sigma1","Width of Gaussian 1", 0.00222, 0.0001, 0.01)
gauss1 = RooGaussian("gauss1","gauss1(Mkk,mean1,sigma1)",Mkk,mean1,sigma1)

#Signal and bkg model
sigShapePdf = gauss1
bkgShapePdf = None

#Efficinecy
efficiency = RooRealVar("efficiency", "efficiency", 0.67, -1, 1)
nSig = RooRealVar("nSig","nSig", 1000.0,-10.0,1000000.0)
nSigpass = RooFormulaVar("nSigpass","nSig * efficiency", RooArgList(nSig,efficiency) )
nSigfail = RooFormulaVar("nSigfail","nSig * (1.0 - efficiency)", RooArgList(nSig,efficiency) )

#Pass
componentspass = RooArgList(sigShapePdf) #,bkgShapePdf);
yieldspass = RooArgList (nSigpass) #, nBkgpass);
sumpass = RooAddPdf("sumpass","fixed extended sum pdf", componentspass, yieldspass)

#Fail
componentsfail = RooArgList(sigShapePdf)#,bkgShapePdf );
yieldsfail = RooArgList(nSigfail)#, nBkgfail );
sumfail = RooAddPdf("sumfail","fixed extended sum pdf", componentsfail, yieldsfail);

#Creates category
myFitCat = RooCategory("myFitCat", "Category: pass or fail")
myFitCat.defineType("fail", 1)
myFitCat.defineType("pass", 0)

#Create PDF for simultaneous fit
totalPdf = RooSimultaneous("totalPdf","totalPdf", myFitCat)
totalPdf.addPdf(sumpass,"pass")
totalPdf.addPdf(sumfail,"fail")

#Generate data and combine
#For combining binned data look rf_combine_binned_data.py
data_pass = gauss1.generate(RooArgSet(Mkk), 6000)
data_fail = gauss1.generate(RooArgSet(Mkk), 4000)
combData = RooDataSet( "combData", "combined data",RooArgSet(Mkk),RooFit.Index(myFitCat),RooFit.Import("pass", data_pass),RooFit.Import("fail",data_fail))

#FIT
totalPdf.fitTo(combData)

#PLOT
sampleSet = RooArgSet(myFitCat)
frame1 = Mkk.frame(RooFit.Bins(50), RooFit.Title("Passed sample"))

# Plot all data tagged as passed sample
combData.plotOn(frame1, RooFit.Cut("myFitCat==myFitCat::pass"))
totalPdf.plotOn(frame1, RooFit.Slice(myFitCat, "pass"), RooFit.ProjWData(sampleSet, combData), RooFit.LineStyle(kDashed))
totalPdf.paramOn(frame1, RooFit.Layout(0.55, 0.9, 0.9), RooFit.Format("NEU", RooFit.AutoPrecision(1)))

# The same plot for the failled sample slice
frame2 = Mkk.frame(RooFit.Bins(50), RooFit.Title("Failed sample"))
combData.plotOn(frame2, RooFit.Cut("myFitCat==myFitCat::fail"))
totalPdf.plotOn(frame2, RooFit.Slice(myFitCat, "fail"),RooFit.ProjWData(sampleSet, combData))
#simPdf.plotOn(frame2, RooFit.Slice(myFitCat, "fail"), RooFit.ProjWData(sampleSet, combData), RooFit.LineStyle(kDashed))
 
c = TCanvas("simultaneouspdf", "simultaneouspdf", 800, 400)
c.Divide(2)
c.cd(1)
frame1.Draw()
c.cd(2)
frame2.Draw()