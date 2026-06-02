void ZPrimeTPrime_2DLimit_hybrid()
{
//=========Macro generated from canvas: FinalCurves/FinalCurves
//=========  (Wed May 22 15:13:10 2024) by ROOT version 6.22/09
   TCanvas *FinalCurves = new TCanvas("FinalCurves", "FinalCurves",10,32,700,500);
   gStyle->SetOptStat(0);
   FinalCurves->SetHighLightColor(2);
   FinalCurves->Range(40,2500,1640,7500);
   FinalCurves->SetFillColor(0);
   FinalCurves->SetBorderMode(0);
   FinalCurves->SetBorderSize(2);
   FinalCurves->SetLogz();
   FinalCurves->SetRightMargin(0.15);
   FinalCurves->SetFrameBorderMode(0);
   FinalCurves->SetFrameBorderMode(0);
   
   TH2D *dummy__1 = new TH2D("dummy__1","",10,200,1400,10,3000,7000);
   dummy__1->SetMinimum(1e-05);
   dummy__1->SetMaximum(0.035);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   dummy__1->SetLineColor(ci);
   dummy__1->GetXaxis()->SetTitle("m_{#tau'^{#scale[0.5]{ }2e}} [GeV]");
   dummy__1->GetXaxis()->SetLabelFont(42);
   dummy__1->GetXaxis()->SetTitleOffset(1);
   dummy__1->GetXaxis()->SetTitleFont(42);
   dummy__1->GetYaxis()->SetTitle("m_{Z'} [GeV]");
   dummy__1->GetYaxis()->SetLabelFont(42);
   dummy__1->GetYaxis()->SetTitleFont(42);
   dummy__1->GetZaxis()->SetTitle("Observed cross section limit [pb]");
   dummy__1->GetZaxis()->SetLabelFont(42);
   dummy__1->GetZaxis()->SetTitleOffset(1);
   dummy__1->GetZaxis()->SetTitleFont(42);
   dummy__1->Draw("axis");
   
   TGraph2D *graph2d = new TGraph2D(35);
   graph2d->SetName("upperLimit");
   graph2d->SetTitle("Graph2D;;;");
   graph2d->SetPoint(0,200,3000,7.078316e-05);
   graph2d->SetPoint(1,400,3000,7.892571e-05);
   graph2d->SetPoint(2,600,3000,4.99905e-05);
   graph2d->SetPoint(3,800,3000,4.52632e-05);
   graph2d->SetPoint(4,1000,3000,4.721111e-05);
   graph2d->SetPoint(5,1200,3000,7.711286e-05);
   graph2d->SetPoint(6,1400,3000,0.002126414);
   graph2d->SetPoint(7,200,4000,7.237106e-05);
   graph2d->SetPoint(8,400,4000,7.383691e-05);
   graph2d->SetPoint(9,600,4000,6.960867e-05);
   graph2d->SetPoint(10,800,4000,5.813466e-05);
   graph2d->SetPoint(11,1000,4000,4.480378e-05);
   graph2d->SetPoint(12,1200,4000,4.412332e-05);
   graph2d->SetPoint(13,1400,4000,4.715198e-05);
   graph2d->SetPoint(14,200,5000,7.60257e-05);
   graph2d->SetPoint(15,400,5000,7.203132e-05);
   graph2d->SetPoint(16,600,5000,6.91139e-05);
   graph2d->SetPoint(17,800,5000,7.204392e-05);
   graph2d->SetPoint(18,1000,5000,6.143193e-05);
   graph2d->SetPoint(19,1200,5000,4.572914e-05);
   graph2d->SetPoint(20,1400,5000,4.462756e-05);
   graph2d->SetPoint(21,200,6000,7.653165e-05);
   graph2d->SetPoint(22,400,6000,6.930872e-05);
   graph2d->SetPoint(23,600,6000,6.884342e-05);
   graph2d->SetPoint(24,800,6000,6.861708e-05);
   graph2d->SetPoint(25,1000,6000,6.940983e-05);
   graph2d->SetPoint(26,1200,6000,6.323204e-05);
   graph2d->SetPoint(27,1400,6000,4.581619e-05);
   graph2d->SetPoint(28,200,7000,7.097743e-05);
   graph2d->SetPoint(29,400,7000,5.76363e-05);
   graph2d->SetPoint(30,600,7000,5.482714e-05);
   graph2d->SetPoint(31,800,7000,5.506651e-05);
   graph2d->SetPoint(32,1000,7000,5.674702e-05);
   graph2d->SetPoint(33,1200,7000,5.424558e-05);
   graph2d->SetPoint(34,1400,7000,5.487891e-05);
   graph2d->Draw("colz same");
   
   Double_t _fx1[35] = {
   200,
   200,
   200,
   200,
   200,
   400,
   400,
   400,
   400,
   400,
   600,
   600,
   600,
   600,
   600,
   800,
   800,
   800,
   800,
   800,
   1000,
   1000,
   1000,
   1000,
   1000,
   1200,
   1200,
   1200,
   1200,
   1200,
   1400,
   1400,
   1400,
   1400,
   1400};
   Double_t _fy1[35] = {
   3000,
   4000,
   5000,
   6000,
   7000,
   3000,
   4000,
   5000,
   6000,
   7000,
   3000,
   4000,
   5000,
   6000,
   7000,
   3000,
   4000,
   5000,
   6000,
   7000,
   3000,
   4000,
   5000,
   6000,
   7000,
   3000,
   4000,
   5000,
   6000,
   7000,
   3000,
   4000,
   5000,
   6000,
   7000};
   TGraph *graph = new TGraph(35,_fx1,_fy1);
   graph->SetName("");
   graph->SetTitle("");
   graph->SetFillStyle(1000);
   graph->SetMarkerStyle(4);
   graph->SetMarkerSize(0.75);
   
   TH1F *Graph_Graph1 = new TH1F("Graph_Graph1","",100,80,1520);
   Graph_Graph1->SetMinimum(2600);
   Graph_Graph1->SetMaximum(7400);
   Graph_Graph1->SetDirectory(0);
   Graph_Graph1->SetStats(0);

   ci = TColor::GetColor("#000099");
   Graph_Graph1->SetLineColor(ci);
   Graph_Graph1->GetXaxis()->SetLabelFont(42);
   Graph_Graph1->GetXaxis()->SetTitleOffset(1);
   Graph_Graph1->GetXaxis()->SetTitleFont(42);
   Graph_Graph1->GetYaxis()->SetLabelFont(42);
   Graph_Graph1->GetYaxis()->SetTitleFont(42);
   Graph_Graph1->GetZaxis()->SetLabelFont(42);
   Graph_Graph1->GetZaxis()->SetTitleOffset(1);
   Graph_Graph1->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph1);
   
   graph->Draw("p");
   
   Double_t Graph0_fx2[71] = {
   100,
   226.5949,
   254.2927,
   274.2968,
   289.6845,
   320.4599,
   334.3088,
   391.2434,
   412.7862,
   422.0188,
   442.0228,
   477.4146,
   494.3411,
   527.6811,
   549.7368,
   560.5082,
   571.2796,
   594.3612,
   615.904,
   655.912,
   677.4548,
   689.765,
   709.769,
   729.7731,
   752.8546,
   765.1648,
   788.1098,
   808.2504,
   819.0218,
   834.4095,
   862.1074,
   879.0339,
   907.7576,
   922.1195,
   934.4296,
   949.048,
   967.5132,
   975.9765,
   985.2091,
   994.4417,
   1000.597,
   1012.907,
   1028.201,
   1044.207,
   1060.609,
   1074.458,
   1084.46,
   1086.768,
   1091.384,
   1105.233,
   1112.927,
   1123.699,
   1131.392,
   1137.547,
   1151.677,
   1163.707,
   1176.017,
   1200.637,
   1213.415,
   1229.874,
   1234.49,
   1239.106,
   1251.417,
   1256.86,
   1263.727,
   1268.293,
   1274.498,
   1282.192,
   1282.192,
   100,
   100};
   Double_t Graph0_fy2[71] = {
   3826.473,
   3826.473,
   3839.283,
   3847.823,
   3852.094,
   3869.174,
   3877.714,
   3920.414,
   3937.494,
   3941.764,
   3963.114,
   3993.004,
   4010.084,
   4045.668,
   4074.135,
   4086.945,
   4099.755,
   4129.645,
   4155.265,
   4212.911,
   4240.666,
   4262.016,
   4291.906,
   4321.796,
   4360.227,
   4377.307,
   4417.513,
   4458.437,
   4475.517,
   4509.677,
   4569.458,
   4603.618,
   4680.478,
   4723.179,
   4761.609,
   4817.119,
   4883.305,
   4915.33,
   4940.95,
   4979.38,
   5005,
   5051.971,
   5128.173,
   5217.005,
   5308.172,
   5402.113,
   5476.838,
   5496.053,
   5538.753,
   5632.694,
   5683.934,
   5739.445,
   5790.685,
   5829.115,
   5914.975,
   5995.646,
   6055.427,
   6192.067,
   6276.65,
   6392.759,
   6431.189,
   6482.429,
   6580.64,
   6644.67,
   6738.631,
   6796.954,
   6866.731,
   6930.782,
   10000,
   10000,
   3826.473};
   graph = new TGraph(71,Graph0_fx2,Graph0_fy2);
   graph->SetName("Graph0");
   graph->SetTitle("phenoContour.csv");

   ci = 1179;
   color = new TColor(ci, 0, 0, 1, " ", 0.99);
   graph->SetFillColor(ci);
   graph->SetFillStyle(3005);
   graph->SetLineWidth(2);
   
   TH1F *Graph_Graph02 = new TH1F("Graph_Graph02","phenoContour.csv",100,0,1400.411);
   Graph_Graph02->SetMinimum(3209.121);
   Graph_Graph02->SetMaximum(10617.35);
   Graph_Graph02->SetDirectory(0);
   Graph_Graph02->SetStats(0);

   ci = TColor::GetColor("#000099");
   Graph_Graph02->SetLineColor(ci);
   Graph_Graph02->GetXaxis()->SetLabelFont(42);
   Graph_Graph02->GetXaxis()->SetTitleOffset(1);
   Graph_Graph02->GetXaxis()->SetTitleFont(42);
   Graph_Graph02->GetYaxis()->SetLabelFont(42);
   Graph_Graph02->GetYaxis()->SetTitleFont(42);
   Graph_Graph02->GetZaxis()->SetLabelFont(42);
   Graph_Graph02->GetZaxis()->SetTitleOffset(1);
   Graph_Graph02->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph02);
   
   graph->Draw(" lf");
   
   Double_t _fx3[1] = {
   650};
   Double_t _fy3[1] = {
   5200};
   graph = new TGraph(1,_fx3,_fy3);
   graph->SetName("");
   graph->SetTitle("");
   graph->SetFillStyle(1000);
   graph->SetMarkerStyle(29);
   graph->SetMarkerSize(2);
   
   TH1F *Graph_Graph3 = new TH1F("Graph_Graph3","",100,649.9,651.1);
   Graph_Graph3->SetMinimum(5199.9);
   Graph_Graph3->SetMaximum(5201.1);
   Graph_Graph3->SetDirectory(0);
   Graph_Graph3->SetStats(0);

   ci = TColor::GetColor("#000099");
   Graph_Graph3->SetLineColor(ci);
   Graph_Graph3->GetXaxis()->SetLabelFont(42);
   Graph_Graph3->GetXaxis()->SetTitleOffset(1);
   Graph_Graph3->GetXaxis()->SetTitleFont(42);
   Graph_Graph3->GetYaxis()->SetLabelFont(42);
   Graph_Graph3->GetYaxis()->SetTitleFont(42);
   Graph_Graph3->GetZaxis()->SetLabelFont(42);
   Graph_Graph3->GetZaxis()->SetTitleOffset(1);
   Graph_Graph3->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph3);
   
   graph->Draw("p");
   TLatex *   tex = new TLatex(650,5200,"    Best fit from
 [2205.04473]");
   tex->SetTextFont(63);
   tex->SetTextSize(14);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.12,0.94,"CMS");
tex->SetNDC();
   tex->SetTextFont(61);
   tex->SetTextSize(0.0675);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.65,0.94,"101 fb^{-1} (13 TeV)");
tex->SetNDC();
   tex->SetTextFont(52);
   tex->SetTextSize(0.0485);
   tex->SetLineWidth(2);
   tex->Draw();
   
   TH2D *dummy_copy__2 = new TH2D("dummy_copy__2","",10,200,1400,10,3000,7000);
   dummy_copy__2->SetMinimum(1e-05);
   dummy_copy__2->SetMaximum(0.035);
   dummy_copy__2->SetDirectory(0);

   ci = TColor::GetColor("#000099");
   dummy_copy__2->SetLineColor(ci);
   dummy_copy__2->GetXaxis()->SetTitle("m_{#tau'^{#scale[0.5]{ }2e}} [GeV]");
   dummy_copy__2->GetXaxis()->SetLabelFont(42);
   dummy_copy__2->GetXaxis()->SetTitleOffset(1);
   dummy_copy__2->GetXaxis()->SetTitleFont(42);
   dummy_copy__2->GetYaxis()->SetTitle("m_{Z'} [GeV]");
   dummy_copy__2->GetYaxis()->SetLabelFont(42);
   dummy_copy__2->GetYaxis()->SetTitleFont(42);
   dummy_copy__2->GetZaxis()->SetTitle("Observed cross section limit [pb]");
   dummy_copy__2->GetZaxis()->SetLabelFont(42);
   dummy_copy__2->GetZaxis()->SetTitleOffset(1);
   dummy_copy__2->GetZaxis()->SetTitleFont(42);
   dummy_copy__2->Draw("sameaxis");
   FinalCurves->Modified();
   FinalCurves->cd();
   FinalCurves->SetSelected(FinalCurves);
}
