from ROOT import TH1F, RooRealVar, TCanvas, RooDataHist, RooFit, RooGaussian, kTRUE, RooArgList, RooAddPdf, TLatex

hh = TH1F("hh", "The hist", 100, -5, 5)
hh.FillRandom("gaus", 10000)
c = TCanvas("c", "c", 600, 600)
hh.Draw()

#Save data in RooDataHist
x = RooRealVar("x", "x", -5, 5)
data = RooDataHist("data", "dataset with x", RooArgList(x), hh)

xframe = x.frame()
data.plotOn(xframe)

c1 = TCanvas("c1", "c1", 1200, 600)
c1.Divide(2,1)
c1.cd(1)
xframe.Draw()

#Create PDF
mean = RooRealVar("mean","MeanofGaussian",0,-10,10)
sigma = RooRealVar("sigma","WidthofGaussian",3,-10,10)
gauss = RooGaussian("gauss","gauss(x,mean,sigma)",x,mean,sigma)
g1sig = RooRealVar("g1sig","fraction of gauss1", 10, 0, 100000.0) 

# Build signal PDF: f1
signalPDF = RooAddPdf("signalPDF", "g1sig * g1", RooArgList(gauss), RooArgList(g1sig)) 

#mean.setConstant(kTRUE); #fix mean
sigma.setRange(0.1, 3); # change range for sigma
gauss.fitTo(data, RooFit.PrintLevel(-1)); # ffit gauss on data
signalPDF.fitTo(data, RooFit.PrintLevel(-1))
#PrintLevel(-1) almost no output
# Minos(kTRUE)?

mean.Print()
sigma.Print()

#Show parameters on plot
signalPDF.paramOn(xframe, RooFit.Layout(0.55, 0.9, 0.9), 
                                   RooFit.Format("NEU", RooFit.AutoPrecision(1)))
signalPDF.plotOn(xframe)

xframe.Draw()
chi2txt = TLatex()
chi2txt.SetNDC()
chi2txt.DrawLatex(0.13, 0.83, "\chi^2/n.d.f = %0.3f" %xframe.chiSquare()) #Put chi² on plot