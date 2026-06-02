from optparse import OptionParser
import subprocess
import array
from  array import array

import ROOT
from ROOT import *

import header
from header import WaitForJobs, make_smooth_graph, Inter
import tdrstyle, CMS_lumi

gStyle.SetOptStat(0)
gROOT.SetBatch(kTRUE)

parser = OptionParser()

# parser.add_option('-t', '--tag', metavar='FILE', type='string', action='store',
#                 default   =   'dataBsOff',
#                 dest      =   'tag',
#                 help      =   'Tag ran over')
parser.add_option('-s', '--signals', metavar='FILE', type='string', action='store',
                default   =   'bstar_signalsLH.txt',
                dest      =   'signals',
                help      =   'Text file containing the signal names and their corresponding cross sections')
parser.add_option('-T', '--hideTheory', action="store_true",
                default   =   True,
                dest      =   'hideTheory',
                help      =   'Dont show the theory curve')
parser.add_option('--unblind', action="store_false",
                default   =   True,
                dest      =   'blind',
                help      =   'Only plot observed limit if false')
parser.add_option('--drawIntersection', action="store_true",
                default   =   False,
                dest      =   'drawIntersection',
                help      =   'Draw intersection values')
parser.add_option('-l', '--lumi', metavar='F', type='string', action='store',
                default       =       '101', #137.44
                dest          =       'lumi',
                help          =       'Luminosity option')
parser.add_option('-m', '--mod', metavar='F', type='string', action='store',
                default       =       '',
                dest          =       'mod',
                help          =       'Modification to limit title on y-axis. For example, different handedness of the signal')
parser.add_option('-p', '--particle', type='string', action='store',
                default       =       '#tilde{g}',
                dest          =       'particle',
                help          =       'Name of HSCP. e.g. #tilde{g}')
parser.add_option('-x', '--process', type='string', action='store',
                default       =       'pp#rightarrow#tilde{g}#tilde{g}',
                dest          =       'process',
                help          =       'Name of HSCP. e.g. pp#rightarrow#tilde{g}#tilde{g}')
parser.add_option('-o', '--xsorder', type='string', action='store',
                default       =       'NNLO+NNLL',
                dest          =       'xsorder',
                help          =       'Order of XS calculation. e.g. NNLO+NNLL')
parser.add_option('-d', '--debug', type='int',
                default       =       0,
                dest          =       'debug',
                help          =       'Debug level')

(options, args) = parser.parse_args()

debug = options.debug

# Open signal file
signal_file = open(options.signals,'r')
# Read in names of project spaces as a list of strings and strip whitespace
signal_names = signal_file.readline().split(',')
signal_names = [n.strip() for n in signal_names]
# Read in mass as a list of strings, strip whitespace, and convert to ints
signal_mass = signal_file.readline().split(',')
signal_mass = [float(m.strip())/1000 for m in signal_mass]
# Read in xsecs as a list of strings, strip whitespace, and convert to floats
theory_xsecs = signal_file.readline().split(',')
theory_xsecs = [float(x.strip()) for x in theory_xsecs]
#
signal_xsecs = signal_file.readline().split(',')
signal_xsecs = [float(x.strip()) for x in signal_xsecs]

# Initialize arrays to eventually store the points on the TGraph
x_mass = array('d')
y_limit = array('d')
y_mclimit  = array('d')
y_mclimitlow68 = array('d')
y_mclimitup68 = array('d')
y_mclimitlow95 = array('d')
y_mclimitup95 = array('d')

ZPrimeYMax = 0.4

tdrstyle.setTDRStyle()

iDir = '/opt/sbg/cms/ui6_data1/rhaeberl/CMSSW_11_3_4/src/HSCPLimit/LimitComputation_MassSpectrum/limitTrees_tamas/tst_hybrid_tamas'

# For each signal
for this_index, this_name in enumerate(signal_names):
    # Setup call for one of the signal
    this_xsec = signal_xsecs[this_index]
    this_mass = signal_mass[this_index]


    this_output = TFile.Open(iDir+'/higgsCombine.{}.HybridNew.all.mH120.root'.format(this_name))
    if not this_output: continue
    this_tree = this_output.Get('limit')

    # Set the mass (x axis)
    x_mass.append(this_mass)
    # Grab the cross section limits (y axis)
    for ievent in range(int(this_tree.GetEntries())):
        this_tree.GetEntry(ievent)

        # Nominal expected
        if this_tree.quantileExpected == 0.5:
            y_mclimit.append(this_tree.limit*this_xsec)
            print("{} has median expected = {} -> limit*XS = {} * {}".format(this_name,this_tree.limit*this_xsec,this_tree.limit,this_xsec))

        # -1 sigma expected
        if round(this_tree.quantileExpected,2) == 0.16:
            y_mclimitlow68.append(this_tree.limit*this_xsec)
            print("{} has -1 sigma expected = {} -> limit*XS = {} * {}".format(this_name,this_tree.limit*this_xsec,this_tree.limit,this_xsec))

        # +1 sigma expected
        if round(this_tree.quantileExpected,2) == 0.84:
            y_mclimitup68.append(this_tree.limit*this_xsec)
            print("{} has +1 sigma expected = {} -> limit*XS = {} * {}".format(this_name,this_tree.limit*this_xsec,this_tree.limit,this_xsec))

        # -2 sigma expected
        if round(this_tree.quantileExpected,3) == 0.025:
            y_mclimitlow95.append(this_tree.limit*this_xsec)
            print("{} has -2 sigma expected = {} -> limit*XS = {} * {}".format(this_name,this_tree.limit*this_xsec,this_tree.limit,this_xsec))

        # +2 sigma expected
        if round(this_tree.quantileExpected,3) == 0.975:
            y_mclimitup95.append(this_tree.limit*this_xsec)
            print("{} has +2 sigma expected = {} -> limit*XS = {} * {}".format(this_name,this_tree.limit*this_xsec,this_tree.limit,this_xsec))

        if (debug > 0) : print("For " + str(this_mass) + " mc_limit is " +str(y_mclimit))

        # Observed (plot only if unblinded)
        if this_tree.quantileExpected == -1:
            if not options.blind:
                if (debug > 0) : print('DEBUG : appending to y_limit')
                if (debug > 0) : print('appending: {} to y_limit'.format(this_tree.limit*this_xsec))
                y_limit.append(this_tree.limit*this_xsec)
                print("{} has observed = {}, limit * xsec -> {} * {}".format(this_name,this_tree.limit*this_xsec,this_tree.limit,this_xsec))
            else:
                y_limit.append(0.0)

# Make Canvas and TGraphs (mostly stolen from other code that formats well)
climits = TCanvas("climits", "climits",700, 600)
climits.SetLogy(True)
climits.SetLeftMargin(.15)
climits.SetBottomMargin(.15)
climits.SetTopMargin(0.1)
climits.SetRightMargin(0.05)

# NOT GENERIC
# if options.hand == 'LH':
#     cstr = 'L'
# elif options.hand == 'RH':
#     cstr = 'R'
# elif options.hand == 'VL':
#     cstr = 'LR'
# else:
#     cstr = ''
cstr = options.mod

gStyle.SetTextFont(42)

# Expected
if (debug > 0) : 
    print('---------DEBUG-----------')
    print('x_mass: {}'.format(x_mass))
    print('len x_mass: {}'.format(len(x_mass)))
    print('y_mclimit: {}'.format(y_mclimit))
    print('y_mclimitlow68: {}'.format(y_mclimitlow68))
    print('y_mclimitup68: {}'.format(y_mclimitup68))
    print('y_mclimitlow95: {}'.format(y_mclimitlow95))
    print('y_mclimitup95: {}'.format(y_mclimitup95))
g_mclimit = TGraph(len(x_mass), x_mass, y_mclimit)
g_mclimit.SetTitle("median_expected_title")
g_mclimit.SetName("median_expected")
g_mclimit.SetMarkerStyle(21)
g_mclimit.SetMarkerColor(1)
g_mclimit.SetLineColor(1)
g_mclimit.SetLineStyle(2)
g_mclimit.SetLineWidth(3)
g_mclimit.SetMarkerSize(0.)

if (len(x_mass) != len(y_mclimit)) :
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("Num of mass point not the same as the num of limit point")
    print("Check your input files, we exit now")
    exit()

# Observed
if not options.blind:
    print('Not blinded')
    print('---------------DEBUG---------------------')
    print('x_mass: {}'.format(x_mass))
    print('len x_mass: {}'.format(len(x_mass)))
    print('y_limit: {}'.format(y_limit))
    print('y_mclimit: {}'.format(y_mclimit))
    print('y_mclimitlow68: {}'.format(y_mclimitlow68))
    print('y_mclimitup68: {}'.format(y_mclimitup68))
    print('y_mclimitlow95: {}'.format(y_mclimitlow95))
    print('y_mclimitup95: {}'.format(y_mclimitup95))
    g_limit = TGraph(len(x_mass), x_mass, y_limit)
    g_limit.SetTitle("")
    g_limit.SetMarkerStyle(7)
    g_limit.SetMarkerColor(1)
    g_limit.SetLineColor(1)
    g_limit.SetLineWidth(2)
    g_limit.SetMarkerSize(1) #0.5
    if ("tau" in cstr) :
      g_limit.GetXaxis().SetRangeUser(0.1, 1.5)
      g_limit.SetMinimum(5e-6) #0.005
      g_limit.SetMaximum(0.02)
    if ("Prime" in cstr) :
      g_limit.GetXaxis().SetRangeUser(0.8, 3.0)
      g_limit.SetMinimum(5e-6) #0.005
      g_limit.SetMaximum(0.02)
    if ("ZPrime" in cstr) :
      g_limit.GetXaxis().SetRangeUser(3.0, 7.0)
      g_limit.SetMinimum(5e-7) #0.005
      #g_limit.SetMinimum(2e-5) #0.005
      g_limit.SetMaximum(ZPrimeYMax)
      #g_limit.SetMaximum(5e-4)
    else:
      g_limit.GetXaxis().SetRangeUser(0.8, 3.0)
      g_limit.SetMinimum(5e-5) #0.005
      g_limit.SetMaximum(0.2)
else:
    print('Blinded')
    g_mclimit.GetXaxis().SetTitle("m_{"+options.particle+"} [TeV]") 
    g_mclimit.GetYaxis().SetTitle("Cross Section [pb]")
    if ("tau" in cstr) :
      g_mclimit.GetXaxis().SetRangeUser(0.1, 1.5)
      g_mclimit.SetMinimum(5e-6) #0.005
      g_mclimit.SetMaximum(0.02)
    if ("Prime" in cstr) :
      g_mclimit.GetXaxis().SetRangeUser(0.8, 3.0)
      g_mclimit.SetMinimum(5e-6) #0.005
      g_mclimit.SetMaximum(0.02)
    if ("ZPrime" in cstr) :
      g_mclimit.GetXaxis().SetRangeUser(3.0, 7.0)
      g_mclimit.SetMinimum(5e-7) #0.005
      g_mclimit.SetMaximum(ZPrimeYMax)
    else:
      g_mclimit.GetXaxis().SetRangeUser(0.8, 3.0)
      g_mclimit.SetMinimum(5e-5) #0.005
      g_mclimit.SetMaximum(0.2)
# Expected
# g_mclimit = TGraph(len(x_mass), x_mass, y_mclimit)
# g_mclimit.SetTitle("")
# g_mclimit.SetMarkerStyle(21)
# g_mclimit.SetMarkerColor(1)
# g_mclimit.SetLineColor(1)
# g_mclimit.SetLineStyle(2)
# g_mclimit.SetLineWidth(3)
# g_mclimit.SetMarkerSize(0.)
# g_mclimit.GetXaxis().SetTitle("M_{b*} (TeV/c^{2})")
# g_mclimit.GetYaxis().SetTitle("Upper Limit #sigma_{b*_{"+cstr+"}} #times b (pb)")
# g_mclimit.GetYaxis().SetTitleSize(0.03)
# g_mclimit.Draw("l")
# g_mclimit.GetYaxis().SetRangeUser(0., 80.)

# Will later be 1 and 2 sigma expected
'''
nAr = [y_mclimitlow95,y_mclimitlow68,y_mclimitup68,y_mclimitup95]

transposed_arrays = list(zip(*nAr))
sorted_values = [sorted(index_values) for index_values in transposed_arrays]
sorted_values_by_index = list(zip(*sorted_values))
print("Sorted values by index")
print(sorted_values_by_index)

newLimLow95 = array('d')
newLimLow68 = array('d')
newLimUp68 = array('d')
newLimUp95 = array('d')
for i in range(5):
    values = sorted([array[i] for array in nAr])
    a, b, c, d = values
    print("Iteration {}: a = {}, b = {}, c = {}, d = {}".format(i,a,b,c,d))
    newLimLow95.append(a)
    newLimLow68.append(b)
    newLimUp68.append(c)
    newLimUp95.append(d)
'''

g_mcplus = TGraph(len(x_mass), x_mass, y_mclimitup68)
g_mcminus = TGraph(len(x_mass), x_mass, y_mclimitlow68)

g_mc2plus = TGraph(len(x_mass), x_mass, y_mclimitup95)
g_mc2minus = TGraph(len(x_mass), x_mass, y_mclimitlow95)
'''

print("Creating smooth graph g_mcplus with len(xmass) = {}, x_mass = {}, limits = {}".format(len(x_mass),x_mass,newLimUp68))
g_mcplus = TGraph(len(x_mass), x_mass, newLimUp68)
print("Creating smooth graph g_mcminus with len(xmass) = {}, x_mass = {}, limits = {}".format(len(x_mass),x_mass,newLimLow68))
g_mcminus = TGraph(len(x_mass), x_mass, newLimLow68)

g_mc2plus = TGraph(len(x_mass), x_mass, newLimUp95)
g_mc2minus = TGraph(len(x_mass), x_mass, newLimLow95)
'''
# Theory line
graphWP = ROOT.TGraph()
graphWP.SetTitle("")
graphWP.SetMarkerStyle(23)
graphWP.SetMarkerColor(4)
graphWP.SetMarkerSize(0.5)
graphWP.GetYaxis().SetRangeUser(0., 80.)
graphWP.GetXaxis().SetRangeUser(1.0, 3.0)
graphWP.SetMinimum(0.3e-3) #0.005
graphWP.SetMaximum(100.)
xsecAt1800 = 0
for index,mass in enumerate(signal_mass):
    xsec = theory_xsecs[index]
    graphWP.SetPoint(index,    mass,   xsec    )
    if (mass == 1.8 ) : xsecAt1800 = theory_xsecs[index]

graphWP.SetLineWidth(3)
graphWP.SetLineColor(4)

graphWPFixedAt1800  = ROOT.TGraph()
graphWPFixedAt1800.SetPoint(0, 1.799, xsecAt1800*0.99)
graphWPFixedAt1800.SetPoint(1, 1.8, xsecAt1800)
graphWPFixedAt1800.SetPoint(2, 1.801, xsecAt1800*1.01)


# Theory up and down unnecessary if not splitting PDF uncertainty into shape and norm
#
# # Theory up
graphWPup = ROOT.TGraph()
graphWPup.SetTitle("")
graphWPup.SetMarkerStyle(23)
graphWPup.SetMarkerColor(4)
graphWPup.SetLineColor(4)
graphWPup.SetLineWidth(2)
graphWPup.SetMarkerSize(0.5)

q = 0
for index,mass in enumerate(signal_mass):
    rt_xsec = 1.1*theory_xsecs[index]
    graphWPup.SetPoint(q,    mass ,   rt_xsec    )
    q+=1

# # Theory down
graphWPdown = ROOT.TGraph()

graphWPdown.SetTitle("")
graphWPdown.SetMarkerStyle(23)
graphWPdown.SetMarkerColor(4)
graphWPdown.SetLineColor(4)
graphWPdown.SetLineWidth(2)
graphWPdown.SetMarkerSize(0.5)

q = 0
for index,mass in enumerate(signal_mass):
    rt_xsec = 0.9*theory_xsecs[index]
    graphWPdown.SetPoint(q,    mass ,   rt_xsec    )
    q+=1

graphWPup.SetLineStyle(2 )
graphWPdown.SetLineStyle(2 )
'''
WPunc = make_smooth_graph(graphWPdown, graphWPup)
WPunc.SetFillColor(4)
WPunc.SetFillStyle(3004)
WPunc.SetLineColor(0)
'''

# 2 sigma expected
g_error95 = make_smooth_graph(g_mc2minus, g_mc2plus)

#g_error95 = g_mc2plus
g_error95.SetFillColor(kOrange)
g_error95.SetLineColor(0)

# 1 sigma expected
g_error = make_smooth_graph(g_mcminus, g_mcplus)
#g_error = g_mcplus
g_error.SetFillColor(kGreen+1)
g_error.SetLineColor(0)

if not options.blind:
    g_limit.GetXaxis().SetTitle("m_{"+options.particle+"} [TeV]") 
    g_limit.GetYaxis().SetTitle("Cross Section [pb]")
    g_limit.GetXaxis().SetTitleSize(0.055)
    g_limit.GetYaxis().SetTitleSize(0.05)
    g_limit.Draw('ap')
    g_error95.Draw("lf")
    g_error.Draw("lf")
    g_mclimit.Draw("l")
    g_limit.Draw("lp")
    g_limit.GetYaxis().SetTitleOffset(1.5)
    g_limit.GetXaxis().SetTitleOffset(1.25)

else:
    g_mclimit.GetXaxis().SetTitle("m_{"+options.particle+"} [TeV]") 
    g_mclimit.GetYaxis().SetTitle("Cross Section [pb]")
    g_mclimit.GetXaxis().SetTitleSize(0.055)
    g_mclimit.GetYaxis().SetTitleSize(0.05)
    g_mclimit.Draw("al")
    g_error95.Draw("lf")
    g_error.Draw("lf")
    g_mclimit.Draw("l")
    g_mclimit.GetYaxis().SetTitleOffset(1.5)
    g_mclimit.GetXaxis().SetTitleOffset(1.25)

#Draw theory lines
if not options.hideTheory :
    graphWP.Draw("l")
    graphWPdown.Draw("l")
    graphWPup.Draw("l")

# Finally calculate the intercept
expectedMassLimit,expectedCrossLimit = Inter(g_mclimit,graphWP) #if len(Inter(g_mclimit,graphWP)) > 0 else -1.0
upLimit,upXsectionLim = Inter(g_mcminus,graphWP) if len(Inter(g_mcminus,graphWP)) > 0 else -1.0
lowLimit,lowXsectionLim = Inter(g_mcplus,graphWP) if len(Inter(g_mcplus,graphWP)) > 0 else -1.0

a,expectedCrossLimitAt1800 = Inter(g_mclimit,graphWPFixedAt1800) #if len(Inter(g_mclimit,graphWPFixedAt1800)) > 0 else -1.0
a,upXsectionLimAt1800 = Inter(g_mcminus,graphWPFixedAt1800) if len(Inter(g_mcminus,graphWPFixedAt1800)) > 0 else -1.0
a,lowXsectionLimAt1800 = Inter(g_mcplus,graphWPFixedAt1800) if len(Inter(g_mcplus,graphWPFixedAt1800)) > 0 else -1.0


expLine = TLine(expectedMassLimit,g_mclimit.GetMinimum(),expectedMassLimit,expectedCrossLimit)
expLine.SetLineStyle(2)

## PRINT OUTS
print('Expected mass limit: '+str(round(expectedMassLimit,3)) + ' +'+str(round(upLimit-expectedMassLimit,3)) +' -'+str(round(expectedMassLimit-lowLimit,3)) + ' TeV')
print('Expected xsection limit at excluded mass: '+str(round(expectedCrossLimit,6)) + ' +'+str(round(expectedCrossLimit-upXsectionLim,6)) +' -'+str(round(lowXsectionLim-expectedCrossLimit,6)) + ' pb') 
print('Expected xsection limit @1800GeV: '+str(round(expectedCrossLimitAt1800,6)) + ' +'+str(round(expectedCrossLimitAt1800-upXsectionLimAt1800,6)) +' -'+str(round(lowXsectionLimAt1800-expectedCrossLimitAt1800,6)) + ' pb') 
print('Theory xsection limit @1800GeV: '+str(round(graphWP.Eval(1.8),6)) + ' pb')

if not options.blind:
    obsMassLimit,obsCrossLimit = Inter(g_limit,graphWP) if len(Inter(g_limit,graphWP)) > 0 else -1.0
    print('Observed limit: '+str(obsMassLimit) + ' TeV')

    obsLine = TLine(obsMassLimit,g_mclimit.GetMinimum(),obsMassLimit,obsCrossLimit)
    obsLine.SetLineStyle(2)
    if options.drawIntersection :
        obsLine.Draw()

# Legend and draw
gStyle.SetLegendFont(62)
if ("ZPrime" in cstr) :
    legend = TLegend(0.18, 0.6, 0.55, 0.89, '')
else:
    legend = TLegend(0.5, 0.6, 0.92, 0.89, '')
legend.SetHeader("95% CL Upper Limits")
if not options.blind:
   legend.AddEntry(g_limit, "Observed Limit", "l")
legend.AddEntry(g_error95, "Expected Limit #pm1#sigma, #pm2#sigma","f")
# legend.AddEntry(g_error95, "#pm1#sigma, 2#sigma", "f")
# legend.AddEntry(g_error95, "#pm2#sigma", "f")
tmp = ROOT.TH1D("","",10,0,10)
if not options.hideTheory :
    legend.AddEntry(graphWP, "#sigma^{"+options.xsorder+"}_{th}("+options.process+")#pm1#sigma", "l")  
else:
    legend.AddEntry(tmp,"","")

legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.SetLineColor(0)

legend.Draw("same")


if ("ZPrime" in cstr) :
    legendDecoratorXLimits = (0.195, 0.258)
else:
    legendDecoratorXLimits = (0.517, 0.588)

# this is to fake the green+yellow band in the legend
tmpcolor = g_error.GetFillColor()
tmpline = ROOT.TLine()
tmpline.SetLineColor(tmpcolor)
if options.hideTheory :
    tmLineWidth = 22  if options.blind else 15
    tmpyposition = 0.75 if options.blind else 0.713
else :
    tmLineWidth = 22  if options.blind else 15
    tmpyposition = 0.75 if options.blind else 0.713
tmpline.SetLineWidth(tmLineWidth)
tmpline.DrawLineNDC(legendDecoratorXLimits[0],tmpyposition,legendDecoratorXLimits[1],tmpyposition)


# legend line for median point
tmpline.SetLineColor(1)
tmpline.SetLineWidth(3)
tmpline.SetLineStyle(2)
tmpline.DrawLineNDC(legendDecoratorXLimits[0],tmpyposition,legendDecoratorXLimits[1],tmpyposition)


# legend lines for theory
tmpyposition = 0.66 if options.blind else 0.65
tmpline.SetLineColor(4)
tmpline.SetLineStyle(2)
tmpline.SetLineWidth(2)
if not options.hideTheory :
    tmpline.DrawLineNDC(legendDecoratorXLimits[0],tmpyposition,legendDecoratorXLimits[1],tmpyposition)

tmpyposition = 0.64 if options.blind else 0.625
tmpline.SetLineColor(4)
tmpline.SetLineStyle(2)
tmpline.SetLineWidth(2)
if not options.hideTheory :
    tmpline.DrawLineNDC(legendDecoratorXLimits[0],tmpyposition,legendDecoratorXLimits[1],tmpyposition)


###### intersection line
tmpline.SetLineColor(1)
tmpline.SetLineWidth(1)
tmpline.SetLineStyle(2)
tmpline.SetLineColor(ROOT.kGray+2)
if options.drawIntersection:
    tmpline.DrawLine(expectedMassLimit,0,expectedMassLimit,expectedCrossLimit)

text1 = ROOT.TLatex()
# text1.SetNDC()
text1.SetTextFont(43)
text1.SetTextSize(14)
text1.SetTextColor(ROOT.kGray+2)
text1.SetTextAngle(90)
if options.drawIntersection:
    text1.DrawLatex(expectedMassLimit-0.005,0, "   %0.2f TeV"%(expectedMassLimit))

text2 = ROOT.TLatex()
# text2.SetNDC()
text2.SetTextFont(43)
text2.SetTextSize(14)
text2.SetTextColor(1)
text2.SetTextAngle(90)
if not options.blind and options.drawIntersection:
    text2.DrawLatex(obsMassLimit-0.005,0, "   %0.2f TeV"%(obsMassLimit))




#############################



# ZPrime pheno best fit line
if ("ZPrime" in cstr) :
    tmpline.SetLineColor(1)
    tmpline.SetLineWidth(1)
    tmpline.SetLineStyle(3)
    tmpline.SetLineColor(ROOT.kGray+2)
    tmpline.DrawLine(5.2,0,5.2, ZPrimeYMax )

    text1.SetTextAngle(0)
    # text1.DrawLatex(5.2-0.005,1.4e-4, "Best fit from 10.1007/JHEP08(2022)012")
    text1.SetTextAlign(13)
    text1.DrawLatex(5.2+0.03 ,ZPrimeYMax*0.9, "Best fit from ")
    text1.DrawLatex(5.2+0.03 ,ZPrimeYMax*0.6, "Giudice, McCullough, and Teresi (2022)")


    # All numbers from https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/SUSY-2018-42/
    # XS numbers from table 5:
    # Acceptance numbers are from Aux table 05: https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/SUSY-2018-42/tabaux_05.pdf
    #    For masses > 400 GeV, the acc is >90%
    # Efficiency numbers are from Aux table 13: https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/SUSY-2018-42/tabaux_13.pdf
    #    Range from 0.001 @ 300 GeV to 0.042 @ 1 TeV

    ATLASLumi = 139000
    ATLASATimesE = 0.01 #assumed
    ATLASExpectedXS = 3.2/ATLASLumi/ATLASATimesE # (exp S95 for most significant excess region) / (atlas lumi) / (assumed 1% A*e)
    ATLASObservedXS = 11.9/ATLASLumi/ATLASATimesE # (exp S95 for most significant excess region) / (atlas lumi) / (assumed 1% A*e)

    markerExp = ROOT.TGraphAsymmErrors()
    markerExp.SetPoint(0,5.2,
        ATLASExpectedXS
        )
    markerExp.SetPointError(0,
        0.045,0.045, #x unc
        0.1/139000/0.01, #negative unc
        1.1/139000/0.01, #positive unc
        )
    #markerExp.SetMarkerStyle(72)
    markerExp.SetMarkerSize(0.05)
    #markerExp.SetMarkerColor(ROOT.kBlack)
    #markerExp.SetLineWidth(2)
    markerExp.SetFillColor(ROOT.kGray)
    markerExp.Draw("P2")
    markerExpLine = ROOT.TLine()
    markerExpLine.SetLineColor(1)
    markerExpLine.SetLineWidth(1)
    markerExpLine.SetLineStyle(1)
    markerExpLine.DrawLine(5.2-0.045,ATLASExpectedXS,5.2+0.045, ATLASExpectedXS )

    markerObs = ROOT.TGraph()
    markerObs.SetPoint(0,5.2,
        ATLASObservedXS
        )
    markerObs.SetMarkerStyle(5)
    markerObs.SetMarkerSize(1.5)
    markerObs.SetMarkerColor(ROOT.kBlack)
    markerObs.Draw("P")



    # ATLAS MCP: https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/EXOT-2018-54/fig_08.png
    # @600 GeV, their limit from DY+PF production is 0.0001372 pb

    # markerMCPObs = ROOT.TGraph()
    # markerMCPObs.SetPoint(0,5.2,
    #     0.0001372
    #     )
    # markerMCPObs.SetMarkerStyle(22)
    # markerMCPObs.SetMarkerSize(1.5)
    # markerMCPObs.SetMarkerColor(ROOT.kBlack)
    # markerMCPObs.Draw("P")


    textATLAS = ROOT.TLatex()
    # textATLAS.SetNDC()
    textATLAS.SetTextFont(43)
    textATLAS.SetTextSize(14)
    textATLAS.SetTextAlign(12)
    textATLAS.SetTextColor(ROOT.kGray+2)
    # textATLAS.SetTextAngle(90)
    textATLAS.DrawLatex(5.2+0.1,ATLASObservedXS, "ATLAS Observed Limit (w/ #Alpha #times #varepsilon = 1%)")
    textATLAS.DrawLatex(5.2+0.1,ATLASExpectedXS, "ATLAS Expected Limit #pm1#sigma")

    # textATLAS.DrawLatex()


# text1 = ROOT.TLatex()
# text1.SetNDC()
# text1.SetTextFont(42)
# text1.DrawLatex(0.17,0.88, "#scale[1.0]{CMS, L = "+options.lumi+" fb^{-1} at  #sqrt{s} = 13 TeV}")

# TPT.Draw()
climits.RedrawAxis()
climits.SetTickx(1)
climits.SetTicky(1)

if not options.blind :
    CMS_lumi.extraText = ' '
else:
    #CMS_lumi.extraText = 'Internal'
    CMS_lumi.extraText = ''

CMS_lumi.lumiTextSize     = 0.5

CMS_lumi.cmsTextSize      = 0.8
CMS_lumi.CMS_lumi(climits, 1, 11)
climits.SaveAs("hybrid_ionization/limits_combine_"+options.lumi.replace('.','p')+"fb_"+options.signals[options.signals.find('/')+1:options.signals.find('.')]+'_'+cstr+"_NoTheo_HybridNew.pdf")
climits.SaveAs("hybrid_ionization/limits_combine_"+options.lumi.replace('.','p')+"fb_"+options.signals[options.signals.find('/')+1:options.signals.find('.')]+'_'+cstr+"_NoTheo_HybridNew.root")
climits.SaveAs("hybrid_ionization/limits_combine_"+options.lumi.replace('.','p')+"fb_"+options.signals[options.signals.find('/')+1:options.signals.find('.')]+'_'+cstr+"_NoTheo_HybridNew.C")
