from ROOT import RooRealVar, RooPoisson, RooGaussian, RooExponential, RooLinearVar, RooAddPdf, RooStats, RooArgSet, RooFit, RooArgList, RooAbsData
from ROOT import TCanvas
from ROOT import kDashed, kRed, kGreen, RooDataSet, RooConstVar, RooProdPdf, RooMsgService, kTRUE, TLegend

lowRange = 0.
highRange = 200.
 
# make a RooRealVar for the observables
invMass = RooRealVar("invMass", "M_inv", lowRange, highRange, "GeV");

isolation = RooRealVar("isolation", "isolation", 0.-0.5, 20.+0.5, "GeV");
isolation.setBins(21)
# --------------------------------------
# make 2-d model for Z including the invariant mass
# distribution and an isolation distribution which we want to
# unfold from QCD.

# mass model for Z
mZ = RooRealVar("mZ", "Z Mass", 91.2, lowRange, highRange);
sigmaZ = RooRealVar("sigmaZ", "Width of Gaussian", 2, 0, 10, "GeV");
mZModel = RooGaussian("mZModel", "Z+jets Model", invMass, mZ, sigmaZ);
# we know Z mass
mZ.setConstant();
# we leave the width of the Z free during the fit in this example.

# isolation model for Z.  Only used to generate toy MC.
# the exponential is of the form exp(c*x).  If we want
# the isolation to decay an e-fold every R GeV, we use
# c = -1/R.
zIsolDecayConst = RooConstVar("zIsolDecayConst", "z isolation decay  constant", 1);
#zIsolationModel = RooExponential("zIsolationModel", "z isolation model", isolation, zIsolDecayConst);
zIsolationModel = RooPoisson("zIsolationModel", "z isolation model", isolation, zIsolDecayConst)
# make the combined Z model
zModel = RooProdPdf("zModel", "2-d model for Z", RooArgSet(mZModel, zIsolationModel));

# --------------------------------------
# make QCD model

# mass model for QCD.
# the exponential is of the form exp(c*x).  If we want
# the mass to decay an e-fold every R GeV, we use
# c = -1/R.
# We can leave this parameter free during the fit.
qcdMassDecayConst = RooRealVar("qcdMassDecayConst", "Decay const for QCD mass spectrum", -0.01, -100, 100, "1/GeV");
qcdMassModel = RooExponential("qcdMassModel", "qcd Mass Model", invMass, qcdMassDecayConst);


# isolation model for QCD.  Only used to generate toy MC
# the exponential is of the form exp(c*x).  If we want
# the isolation to decay an e-fold every R GeV, we use
# c = -1/R.
qcdIsolDecayConst = RooConstVar("qcdIsolDecayConst", "Et resolution constant", -.1);
qcdIsolationModel = RooExponential("qcdIsolationModel", "QCD isolation model", isolation, qcdIsolDecayConst);

#qcdIsolationSigma = RooRealVar("qcdIsolationSigma", "Width of qcd isolation", 5, 0, 20);
#qcdIsolationMean = RooRealVar("qcdIsolationSigma", "Mean of qcd isolation", 9, 0, 20);
#qcdIsolationModel = RooGaussian("qcdIsolationModel", "qcdIsolationModel", isolation, qcdIsolationMean, qcdIsolationSigma)
# make the 2-d model
qcdModel = RooProdPdf("qcdModel", "2-d model for QCD", RooArgSet(qcdMassModel, qcdIsolationModel));

# --------------------------------------
# combined model

# These variables represent the number of Z or QCD events
# They will be fitted.
zYield = RooRealVar("zYield", "fitted yield for Z", 50, 0., 1000);
qcdYield = RooRealVar("qcdYield", "fitted yield for QCD", 500, 0., 1000);

# now make the combined model
print("make full model")
model = RooAddPdf("model", "z+qcd background models", RooArgList(zModel, qcdModel), RooArgList(zYield, qcdYield));

# interesting for debugging and visualizing the model
model.graphVizTree("fullModel.dot")

""" ADD DATA """
nEvents = 1000;
 
# make the toy data
print("make data set and import to workspace")
data = model.generate(RooArgSet(invMass, isolation), nEvents)

""" Do SPLOT """
print("Calculate sWeights")

# fit the model to the data.
model.fitTo(data, RooFit.Extended())

# The sPlot technique requires that we fix the parameters
# of the model that are not yields after doing the fit.
#
# This *could* be done with the lines below, however this is taken care of
# by the RooStats::SPlot constructor (or more precisely the AddSWeight
# method).
#
# RooRealVar* sigmaZ = ws->var("sigmaZ");
# RooRealVar* qcdMassDecayConst = ws->var("qcdMassDecayConst");
# sigmaZ->setConstant();
# qcdMassDecayConst->setConstant();

RooMsgService.instance().setSilentMode(kTRUE)

print("\n\n------------------------------------------\nThe dataset before creating sWeights:\n")
data.Print()

RooMsgService.instance().setGlobalKillBelow(RooFit.ERROR)

# Now we use the SPlot class to add SWeights to our data set
# based on our model and our yield variables
sData = RooStats.SPlot("sData", "An SPlot", data, model, RooArgList(zYield, qcdYield));

print("\n\nThe dataset after creating sWeights:\n")
data.Print()

# Check that our weights have the desired properties

print("\n\n------------------------------------------\n")
print("Check SWeights:", "Yield of Z is\t" , zYield.getVal() , ".  From sWeights it is ", sData.GetYieldFromSWeight("zYield"))

print("Yield of QCD is\t" , qcdYield.getVal() , ".  From sWeights it is ", sData.GetYieldFromSWeight("qcdYield"))
        

for i in range(10):
    print("z Weight for event ", i, sData.GetSWeight(i, "zYield"), "  qcd Weight", sData.GetSWeight(i, "qcdYield"), "  Total Weight", sData.GetSumOfEventSWeight(i))
        

# import this new dataset with sWeights
RooMsgService.instance().setGlobalKillBelow(RooFit.INFO)

""" Make plots """
cdata = TCanvas("sPlot", "sPlot demo", 1200, 900);
cdata.Divide(3, 3);

# do this to set parameters back to their fitted values.
model.fitTo(data, RooFit.Extended());

# plot invMass for data with full model and individual components overlaid
#  TCanvas* cdata = new TCanvas();
cdata.cd(1);
frame = invMass.frame();
data.plotOn(frame);
model.plotOn(frame, RooFit.Name("FullModel"));
model.plotOn(frame, RooFit.Components("zModel"), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed), RooFit.Name("ZModel"));
model.plotOn(frame, RooFit.Components("qcdModel"), RooFit.LineStyle(kDashed), RooFit.LineColor(kGreen), RooFit.Name("QCDModel"));

leg = TLegend(0.11, 0.5, 0.5, 0.8);
leg.AddEntry(frame.findObject("FullModel"), "Full model", "L");
leg.AddEntry(frame.findObject("ZModel"), "Z model", "L");
leg.AddEntry(frame.findObject("QCDModel"), "QCD model", "L");
leg.SetBorderSize(0);
leg.SetFillStyle(0);

frame.SetTitle("Fit of model to discriminating variable");
frame.Draw();
leg.DrawClone();

# Now use the sWeights to show isolation distribution for Z and QCD.
# The SPlot class can make this easier, but here we demonstrate in more
# detail how the sWeights are used.  The SPlot class should make this
# very easy and needs some more development.

# Plot isolation for Z component.
# Do this by plotting all events weighted by the sWeight for the Z component.
# The SPlot class adds a new variable that has the name of the corresponding
# yield + "_sw".
cdata.cd(2);

# create weighted data set
dataw_z = RooDataSet(data.GetName(), data.GetTitle(), data, data.get(), "0.01", "zYield_sw")

frame2 = isolation.frame();
# Since the data are weighted, we use SumW2 to compute the errors.
dataw_z.plotOn(frame2, RooFit.DataError(RooAbsData.SumW2));

frame2.SetTitle("Isolation distribution with s weights to project out Z");
frame2.Draw();

# Plot isolation for QCD component.
# Eg. plot all events weighted by the sWeight for the QCD component.
# The SPlot class adds a new variable that has the name of the corresponding
# yield + "_sw".
cdata.cd(3);
dataw_qcd = RooDataSet(data.GetName(), data.GetTitle(), data, data.get(), "qcdYield_sw>0");
frame3 = isolation.frame();
dataw_qcd.plotOn(frame3, RooFit.DataError(RooAbsData.SumW2));
model.plotOn(frame3, RooFit.Components("qcdIsolationModel"))
frame3.SetTitle("Isolation distribution with s weights to project out QCD");
frame3.Draw();

cdata.cd(4)
frame4 = isolation.frame()
data.plotOn(frame4)
model.plotOn(frame4, RooFit.Components("qcdIsolationModel"), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed))
frame4.Draw()

cdata.Print("SPlot_py.pdf");