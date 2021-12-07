from ROOT import TH1F, RooGenericPdf, TFile, RooRealVar, TCanvas, RooDataHist, RooFit, RooGaussian, kTRUE, RooArgList, RooAddPdf, TLatex, kBlack, kRed, kDashed

"""
# Generating data
hh = TH1F("hh", "The hist", 100, -5, 5)
hh.FillRandom("gaus", 10000)
baseline = 50
noise = 5
for i in range(hh.GetNbinsX()):
    hh.SetBinContent(i+1, hh.GetBinContent(i+1) + (sqrt((i - 10) * heaviside(i-10, 0)) * baseline) // 1 + random.exponential(noise) // 1)
"""

_file0 = TFile("data_gaus_sqrt.root", "READ")
hh = _file0.Get("hh")

#Save data in RooDataHist
x = RooRealVar("x", "x", -5, 5)
data = RooDataHist("data", "dataset with x", RooArgList(x), hh)

# Create canvas before any drawing of the frames.
# ------------------
c1 = TCanvas("c1", "c1", 1800, 600)
c1.Divide(3,1)
c1.cd(1)

xframe = x.frame(RooFit.Title("Fitting partial range"))
xframe_center = x.frame(RooFit.Title("Fitting full range"))
xframe_right = x.frame(RooFit.Title("Fitting simple model"))

# Plot data on frame
# ------------------
data.plotOn(xframe)
data.plotOn(xframe_center)
data.plotOn(xframe_right)

# Construct signal PDF
mean = RooRealVar("mean","MeanofGaussian",0,-1,1)
sigma = RooRealVar("sigma","WidthofGaussian",1,0.01,5)
gauss = RooGaussian("gauss","gauss(x,mean,sigma)",x,mean,sigma)

# Construct the background pdf
x0 = RooRealVar("x0", "x0", -4, -4.5, -2)
x0.setConstant(kTRUE)
# Function with clipping
bkg_sqrt_arg = RooGenericPdf("bkg_sqrt_arg", "argument for sqrt", "(x >= x0)*(x - x0)", RooArgList(x, x0))
bkg_sqrt = RooGenericPdf("bkg_sqrt", "custom PDF build", "sqrt(bkg_sqrt_arg)", RooArgList(bkg_sqrt_arg))
# Function without clipping
bkg_sqrt_simple = RooGenericPdf("bkg_sqrt_simple", "custom PDF build", "sqrt(x - x0)", RooArgList(x, x0))

# Construct signal+bkg PDF
f = RooRealVar("f", "f", 0.1, 0, 1)
model = RooAddPdf("model", "model", RooArgList(gauss, bkg_sqrt), RooArgList(f))

# Model without clipping
model_simple = RooAddPdf("model_simple", "model_simple", RooArgList(gauss, bkg_sqrt_simple), RooArgList(f))

# Model with amplitude
m1 = RooRealVar("m1","model amplitude", 15000, 0, 100000.0) 
model_n = RooAddPdf("model_n", "model * m1", RooArgList(model), RooArgList(m1))

# Fit simple model
# ----------------
r_simple = model_simple.fitTo(data, RooFit.Save(kTRUE))

# Plot simple model
# -----------------
model_simple.paramOn(
    xframe_right,
    RooFit.Layout(0.65, 0.9, 0.9), 
    RooFit.Format("NEU", RooFit.AutoPrecision(1)))

model_simple.plotOn(
    xframe_right,
    RooFit.Components("gauss"),
    RooFit.LineColor(kBlack),
    RooFit.LineStyle(kDashed))
    
model_simple.plotOn(
    xframe_right,
    RooFit.Components("bkg_sqrt"),
    RooFit.LineColor(kRed),
    RooFit.LineStyle(kDashed))

model_simple.plotOn(
    xframe_right
    )

# Plot frame
c1.cd(3)
xframe_right.Draw()

# Fit partial range 
# ----------------------------------
x.setRange("signal", -3.9, 5)
r_sig = model.fitTo(data,RooFit.Save(kTRUE),RooFit.Range("signal")) #, RooFit.NormRange("signal")

# Plot partial range
# -------------------
model.paramOn(
    xframe,
    RooFit.Range("signal"),
    RooFit.Layout(0.65, 0.9, 0.9), 
    RooFit.Format("NEU", RooFit.AutoPrecision(1)))

model.plotOn(
    xframe,
    RooFit.Range("signal"),
    RooFit.Components("gauss"),
    RooFit.LineColor(kBlack),
    RooFit.LineStyle(kDashed))
    
model.plotOn(
    xframe,
    RooFit.Range("signal"),
    RooFit.Components("bkg_sqrt"),
    RooFit.LineColor(kRed),
    RooFit.LineStyle(kDashed))

model.plotOn(
    xframe,
    RooFit.Range("signal")
    )

# Plot frame
c1.cd(1)
xframe.Draw()

# Fit full range
# ----------------------------------
x.setRange("Full", -5, 5)
r_full = model.fitTo(data, RooFit.Save(kTRUE), RooFit.PrintLevel(-1), RooFit.Range("Full"))

# Plot full range
# ------------------
model.paramOn(
    xframe_center, 
    RooFit.Range("Full"), # or use Range("Full")
    RooFit.Layout(0.65, 0.9, 0.9), 
    RooFit.Format("NEU", RooFit.AutoPrecision(2)))

model.plotOn(xframe_center,
    RooFit.Range(""),
    RooFit.Components(
    "gauss"),
    RooFit.LineColor(kBlack),
    RooFit.LineStyle(kDashed))
    
model.plotOn(xframe_center,
    RooFit.Range(""),
    RooFit.Components(
    "bkg_sqrt"),
    RooFit.LineColor(kRed),
    RooFit.LineStyle(kDashed))

model.plotOn(
    xframe_center,
    RooFit.Range("Full"))

# Plot frame on pad
c1.cd(2)
xframe_center.Draw()