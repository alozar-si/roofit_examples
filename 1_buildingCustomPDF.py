'''
Example of custom gaussian function using ratio of sigma1 and sigma2
'''

from ROOT import TLatex, TFile, TCanvas, TF1, TH1, TH1F, TH2F, gROOT, TString, TMath, gStyle, TRatioPlot, TGraphErrors, TLegend, TGraph
from ROOT import RooRealVar, RooGaussian, RooAddPdf, RooGenericPdf, RooFit, RooArgList, RooDataHist, RooArgSet, RooDataSet
from ROOT import kRed, kBlack, kBlue, kGreen, kTRUE, kDashed, kDotted, kFALSE, gSystem
from ROOT import RooMsgService, RooCategory, RooSimultaneous, RooProdPdf, gPad, RooPolynomial, RooFormulaVar
from ROOT.std import map as std_map

from array import array
import numpy as np

fit_min = 1.0
fit_max = 1.04
#First Gaussian PDF
Mkk = RooRealVar("Mkk", "Mkk", fit_min, fit_max)
mean1 = RooRealVar("mean1","Mean of Gaussian 1",1.01944, 1.01, 1.03)
sigma1 = RooRealVar("sigma1","Width of Gaussian 1", 0.00222, 0.0001, 0.01)
gauss1 = RooGaussian("gauss1","gauss1(Mkk,mean1,sigma1)",Mkk,mean1,sigma1)

# Second Gaussian PDF
mean2 = RooRealVar("mean2","Mean of Gaussian 2",1.02052, 1.0, 1.1);
sigma2 = RooRealVar("sigma2","Width of Gaussian 2", 0.0072, 0.001, 1);

gauss2 = RooGaussian("gauss2","gauss1(Mkk,mean2,sigma2)",Mkk,mean2,sigma2);
r2 = RooRealVar("r2","ratio of width of gaussian 2", 3.2, 0, 10);

customGaussR = RooGenericPdf("customGaussR", "custom PDF build", "1/(sigma1*r2) * exp(- (Mkk - mean2)**2 / (2 * (sigma1*r2) ** 2))", RooArgList(Mkk,mean2,sigma1,r2))

# faster method:
r_sigma2 = RooFormulaVar("r_sigma2","sigma1 * r2", RooArgList(sigma1,r2) )
gauss2R = RooGaussian("gauss2R","gauss1(Mkk,mean2,sigma2)",Mkk,mean2,r_sigma2)

toyDataCustom = customGaussR.generate(RooArgSet(Mkk), 100000)
toyData = gauss2.generate(RooArgSet(Mkk), 100000)
toyDataR = gauss2R.generate(RooArgSet(Mkk), 100000)

c = TCanvas("c", "c", 800, 800)
frame1 = Mkk.frame(RooFit.Bins(50), RooFit.Title("Comparison of PDFs"))

# Plot all data tagged as passed sample
toyData.plotOn(frame1)
toyDataR.plotOn(frame1)
toyDataCustom.plotOn(frame1)
#totalPdf.paramOn(frame1, RooFit.Layout(0.55, 0.9, 0.9), RooFit.Format("NEU", RooFit.AutoPrecision(1)))
frame1.Draw()