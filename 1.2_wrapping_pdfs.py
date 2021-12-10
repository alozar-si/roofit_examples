import ROOT
#--------------------------------------------------------
# WORKING EXAMPLE

# Create observables
x = ROOT.RooRealVar("x", "x", -10, 10)
 
# Create Gaussian
sigma = ROOT.RooRealVar("sigma", "sigma", 2, 0.1, 10)
mean = ROOT.RooRealVar("mean", "mean", 0, -10, 10)
gauss = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

data = gauss.generate(x, 10000)

frame = x.frame(ROOT.RooFit.Title("No function"))
data.plotOn(frame)
gauss.fitTo(data)
gauss.plotOn(frame)

c = ROOT.TCanvas()
frame.Draw()

#--------------------------------------------------------
# NOT WORKING EXAMPLE
def get_pdf():
    # Create observables
    f_x = ROOT.RooRealVar("x", "x", -10, 10)
    # Create Gaussian
    f_sigma = ROOT.RooRealVar("f_sigma", "f_sigma", 2, 0.1, 10)
    f_mean = ROOT.RooRealVar("f_mean", "f_mean", 0, -10, 10)
    f_gauss = ROOT.RooGaussian("f_gauss", "f_gauss", f_x, f_mean, f_sigma)
    return f_x, f_gauss, f_sigma, f_mean

x2, gauss2, a, b = get_pdf()
gauss2.generate(x2, 1000)

#--------------------------------------------------------
# Correct solution is using classes
class pdf():
    def __init__(self, observable=None) -> None:
        if observable == None:
            self.x = ROOT.RooRealVar("x", "x", -10, 10)
        else:
            self.x = observable
        # Create Gaussian
        self.sigma = ROOT.RooRealVar("sigma", "sigma", 2, 0.1, 10)
        self.mean = ROOT.RooRealVar("mean", "mean", 0, -10, 10)
        self.gauss = ROOT.RooGaussian("gauss", "gauss", self.x, self.mean, self.sigma)
        pass

gaus_pdf = pdf()
data = gaus_pdf.gauss.generate(gaus_pdf.x, 1000)