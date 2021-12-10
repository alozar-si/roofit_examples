from ROOT import TH1F, TFile, RooRealVar, TCanvas, RooBreitWigner, RooDataHist, RooFit, RooGaussian, RooFFTConvPdf, RooLandau, kTRUE, RooArgList, RooAddPdf, TLatex, RooPolynomial, kBlack, kRed, kDashed
from numpy import random
# # # # # # # # # # # # # # # # # #
# Source absolute_path/thisroot.bat
# Create convolution PDF and fit.
# # # # # # # # # # # # # # # # # #

# S e t u p   c o m p o n e n t   p d f s 
# ---------------------------------------
M_kaon = RooRealVar("M_kaon", "Kaon mass", 0.493677);
# Construct observable
t = RooRealVar("t","t",M_kaon.getVal()*2+1e-3,1.06)
# Construct BW
mbw = RooRealVar("mbw","mean bw", 1.01944, -20,20)
sbw = RooRealVar("sbw","sigma bw",0.002,0.001,10)
bw = RooBreitWigner("bw", "bw", t, mbw, sbw)
# Construct gauss(t,mg,sg)
mg = RooRealVar("mg","mg",0)
sg = RooRealVar("sg","sg",0.002,0.001,10)
gauss = RooGaussian("gauss","gauss",t,mg,sg)

# C o n s t r u c t   c o n v o l u t i o n   p d f 
# ---------------------------------------
# Set #bins to be used for FFT sampling to 10000
t.setBins(10000,"cache") 

bwxg = RooFFTConvPdf("bwxg", "bw (X) gauss", t, bw, gauss)

# S a m p l e ,   f i t   a n d   p l o t   c o n v o l u t e d   p d f 
# ----------------------------------------------------------------------
# Sample 1000 events in x from gxlx
data2 = bwxg.generate(t,10000)
# Fit gxlx to data
bwxg.fitTo(data2)

# Plot data, landau pdf, landau (X) gauss pdf
frame2 = t.frame(RooFit.Title("bw (x) gauss convolution"))
data2.plotOn(frame2)
bwxg.plotOn(frame2)
#bwxg.plotOn(frame2,RooFit.LineStyle(kDashed), RooFit.Components(
#    "gauss"))
# Draw frame on canvas
c2 = TCanvas("6.2_convolution_bw_x_gauss","6.2_convolution_bw_x_gauss",600,600)
#gPad->SetLeftMargin(0.15)
frame2.GetYaxis().SetTitleOffset(1.4) 
frame2.Draw()
c2.Print("6.2_convolution_bw_x_gauss.pdf")

"""# # # # EXTRA # # # #
# signal - BW x Gauss
# background - constant
# ---------------------------

# Construct the background pdf
a = [0, 0]
a[0] = RooRealVar("a0", "a0", 0.1, -2, 2)
a[1] = RooRealVar("a1", "a1", 0.1, -1, 0.2)
bkg = RooPolynomial("bkg", "bkg", t, RooArgList(a[0]))

# Construct signal+bkg PDF
frac = RooRealVar("frac", "frac", 0.2, 0, 1)
final_model = RooAddPdf("final_model", "final_model", RooArgList(bwxg, bkg), RooArgList(frac))

# Construct final model with amplitude
#m1 = RooRealVar("m1","model amplitude", 10, 0, 100000.0) 
#model_n = RooAddPdf("model_n", "model * m1", RooArgList(model), RooArgList(m1))##

# Sample 1000 events in x from gxlx
data3 = final_model.generate(t,10000)

# Fit model
final_model.fitTo(data3)

# Plot data, landau pdf, landau (X) gauss pdf
frame3 = t.frame(RooFit.Title("landau (x) gauss on constant bkg"))
data3.plotOn(frame3)
final_model.plotOn(frame3)

# Draw frame on canvas
c3 = TCanvas("6.1_conv_and_bkg","6.1_conv_and_bkg",800,600)
#gPad->SetLeftMargin(0.15)
frame3.GetYaxis().SetTitleOffset(1.4) 
frame3.Draw()
c3.Print("6.1_conv_and_bkg.pdf")"""