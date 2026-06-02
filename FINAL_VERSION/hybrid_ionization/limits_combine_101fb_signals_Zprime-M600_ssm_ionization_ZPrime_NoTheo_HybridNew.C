void limits_combine_101fb_signals_Zprime-M600_ssm_ionization_ZPrime_NoTheo_HybridNew()
{
//=========Macro generated from canvas: climits/climits
//=========  (Tue Jul  2 13:47:32 2024) by ROOT version 6.22/09
   TCanvas *climits = new TCanvas("climits", "climits",0,0,700,600);
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(0);
   climits->SetHighLightColor(2);
   climits->Range(2.228,-7.481648,7.268,0.3891387);
   climits->SetFillColor(0);
   climits->SetBorderMode(0);
   climits->SetBorderSize(2);
   climits->SetLogy();
   climits->SetTickx(1);
   climits->SetTicky(1);
   climits->SetLeftMargin(0.15);
   climits->SetRightMargin(0.05);
   climits->SetBottomMargin(0.15);
   climits->SetFrameLineWidth(2);
   climits->SetFrameBorderMode(0);
   climits->SetFrameLineWidth(2);
   climits->SetFrameBorderMode(0);
   
   Double_t Graph0_fx1[5] = {
   3,
   4,
   5,
   6,
   7};
   Double_t Graph0_fy1[5] = {
   4.99905e-05,
   6.960867e-05,
   6.91139e-05,
   6.884342e-05,
   5.482714e-05};
   TGraph *graph = new TGraph(5,Graph0_fx1,Graph0_fy1);
   graph->SetName("Graph0");
   graph->SetTitle("");
   graph->SetFillStyle(1000);
   graph->SetLineWidth(2);
   graph->SetMarkerStyle(7);
   
   TH1F *Graph_Graph01 = new TH1F("Graph_Graph01","",100,2.6,7.4);
   Graph_Graph01->SetMinimum(5e-07);
   Graph_Graph01->SetMaximum(0.4);
   Graph_Graph01->SetDirectory(0);
   Graph_Graph01->SetStats(0);
   Graph_Graph01->SetLineWidth(2);
   Graph_Graph01->SetMarkerStyle(20);
   Graph_Graph01->SetMarkerSize(0.9);
   Graph_Graph01->GetXaxis()->SetTitle("m_{Z'_{SSM}} [TeV]");
   Graph_Graph01->GetXaxis()->SetRange(9,92);
   Graph_Graph01->GetXaxis()->SetLabelFont(42);
   Graph_Graph01->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph01->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph01->GetXaxis()->SetTitleSize(0.055);
   Graph_Graph01->GetXaxis()->SetTitleOffset(1.25);
   Graph_Graph01->GetXaxis()->SetTitleFont(42);
   Graph_Graph01->GetYaxis()->SetTitle("Cross Section [pb]");
   Graph_Graph01->GetYaxis()->SetLabelFont(42);
   Graph_Graph01->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph01->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph01->GetYaxis()->SetTitleSize(0.05);
   Graph_Graph01->GetYaxis()->SetTickLength(0.02);
   Graph_Graph01->GetYaxis()->SetTitleOffset(1.5);
   Graph_Graph01->GetYaxis()->SetTitleFont(42);
   Graph_Graph01->GetZaxis()->SetLabelFont(42);
   Graph_Graph01->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph01->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph01->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph01->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph01->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph01);
   
   graph->Draw("ap");
   
   Double_t Graph1_fx2[12] = {
   3,
   4,
   5,
   6,
   7,
   7,
   7,
   7,
   6,
   5,
   4,
   3};
   Double_t Graph1_fy2[12] = {
   9.319116e-05,
   0.0001565315,
   0.0001567784,
   0.000146848,
   0.000108087,
   0.000108087,
   3.892822e-05,
   3.892822e-05,
   4.194925e-05,
   4.183637e-05,
   4.163305e-05,
   3.707633e-05};
   graph = new TGraph(12,Graph1_fx2,Graph1_fy2);
   graph->SetName("Graph1");
   graph->SetTitle("Graph");

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#ffcc00");
   graph->SetFillColor(ci);
   graph->SetFillStyle(1000);
   graph->SetLineColor(0);
   graph->SetMarkerStyle(20);
   graph->SetMarkerSize(0.9);
   
   TH1F *Graph_Graph12 = new TH1F("Graph_Graph12","Graph",100,2.6,7.4);
   Graph_Graph12->SetMinimum(2.510612e-05);
   Graph_Graph12->SetMaximum(0.0001687487);
   Graph_Graph12->SetDirectory(0);
   Graph_Graph12->SetStats(0);
   Graph_Graph12->SetLineWidth(2);
   Graph_Graph12->SetMarkerStyle(20);
   Graph_Graph12->SetMarkerSize(0.9);
   Graph_Graph12->GetXaxis()->SetLabelFont(42);
   Graph_Graph12->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph12->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph12->GetXaxis()->SetTitleSize(0.065);
   Graph_Graph12->GetXaxis()->SetTitleOffset(1.1);
   Graph_Graph12->GetXaxis()->SetTitleFont(42);
   Graph_Graph12->GetYaxis()->SetLabelFont(42);
   Graph_Graph12->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph12->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph12->GetYaxis()->SetTitleSize(0.065);
   Graph_Graph12->GetYaxis()->SetTickLength(0.02);
   Graph_Graph12->GetYaxis()->SetTitleOffset(1.1);
   Graph_Graph12->GetYaxis()->SetTitleFont(42);
   Graph_Graph12->GetZaxis()->SetLabelFont(42);
   Graph_Graph12->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph12->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph12->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph12->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph12->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph12);
   
   graph->Draw("lf");
   
   Double_t Graph2_fx3[12] = {
   3,
   4,
   5,
   6,
   7,
   7,
   7,
   7,
   6,
   5,
   4,
   3};
   Double_t Graph2_fy3[12] = {
   6.03917e-05,
   8.178113e-05,
   8.342371e-05,
   8.097624e-05,
   6.123453e-05,
   6.123453e-05,
   4.041405e-05,
   4.041405e-05,
   4.523099e-05,
   4.386034e-05,
   4.237621e-05,
   3.753061e-05};
   graph = new TGraph(12,Graph2_fx3,Graph2_fy3);
   graph->SetName("Graph2");
   graph->SetTitle("Graph");

   ci = TColor::GetColor("#00cc00");
   graph->SetFillColor(ci);
   graph->SetFillStyle(1000);
   graph->SetLineColor(0);
   graph->SetMarkerStyle(20);
   graph->SetMarkerSize(0.9);
   
   TH1F *Graph_Graph23 = new TH1F("Graph_Graph23","Graph",100,2.6,7.4);
   Graph_Graph23->SetMinimum(3.294129e-05);
   Graph_Graph23->SetMaximum(8.801302e-05);
   Graph_Graph23->SetDirectory(0);
   Graph_Graph23->SetStats(0);
   Graph_Graph23->SetLineWidth(2);
   Graph_Graph23->SetMarkerStyle(20);
   Graph_Graph23->SetMarkerSize(0.9);
   Graph_Graph23->GetXaxis()->SetLabelFont(42);
   Graph_Graph23->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph23->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph23->GetXaxis()->SetTitleSize(0.065);
   Graph_Graph23->GetXaxis()->SetTitleOffset(1.1);
   Graph_Graph23->GetXaxis()->SetTitleFont(42);
   Graph_Graph23->GetYaxis()->SetLabelFont(42);
   Graph_Graph23->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph23->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph23->GetYaxis()->SetTitleSize(0.065);
   Graph_Graph23->GetYaxis()->SetTickLength(0.02);
   Graph_Graph23->GetYaxis()->SetTitleOffset(1.1);
   Graph_Graph23->GetYaxis()->SetTitleFont(42);
   Graph_Graph23->GetZaxis()->SetLabelFont(42);
   Graph_Graph23->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph23->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph23->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph23->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph23->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph23);
   
   graph->Draw("lf");
   
   Double_t median_expected_fx4[5] = {
   3,
   4,
   5,
   6,
   7};
   Double_t median_expected_fy4[5] = {
   4.142877e-05,
   4.846631e-05,
   5.031465e-05,
   5.101434e-05,
   4.294095e-05};
   graph = new TGraph(5,median_expected_fx4,median_expected_fy4);
   graph->SetName("median_expected");
   graph->SetTitle("median_expected_title");
   graph->SetFillStyle(1000);
   graph->SetLineStyle(2);
   graph->SetLineWidth(3);
   graph->SetMarkerStyle(21);
   graph->SetMarkerSize(0);
   
   TH1F *Graph_median_expected4 = new TH1F("Graph_median_expected4","median_expected_title",100,2.6,7.4);
   Graph_median_expected4->SetMinimum(4.047021e-05);
   Graph_median_expected4->SetMaximum(5.19729e-05);
   Graph_median_expected4->SetDirectory(0);
   Graph_median_expected4->SetStats(0);
   Graph_median_expected4->SetLineWidth(2);
   Graph_median_expected4->SetMarkerStyle(20);
   Graph_median_expected4->SetMarkerSize(0.9);
   Graph_median_expected4->GetXaxis()->SetLabelFont(42);
   Graph_median_expected4->GetXaxis()->SetLabelOffset(0.015);
   Graph_median_expected4->GetXaxis()->SetLabelSize(0.05);
   Graph_median_expected4->GetXaxis()->SetTitleSize(0.065);
   Graph_median_expected4->GetXaxis()->SetTitleOffset(1.1);
   Graph_median_expected4->GetXaxis()->SetTitleFont(42);
   Graph_median_expected4->GetYaxis()->SetLabelFont(42);
   Graph_median_expected4->GetYaxis()->SetLabelOffset(0.015);
   Graph_median_expected4->GetYaxis()->SetLabelSize(0.05);
   Graph_median_expected4->GetYaxis()->SetTitleSize(0.065);
   Graph_median_expected4->GetYaxis()->SetTickLength(0.02);
   Graph_median_expected4->GetYaxis()->SetTitleOffset(1.1);
   Graph_median_expected4->GetYaxis()->SetTitleFont(42);
   Graph_median_expected4->GetZaxis()->SetLabelFont(42);
   Graph_median_expected4->GetZaxis()->SetLabelOffset(0.015);
   Graph_median_expected4->GetZaxis()->SetLabelSize(0.05);
   Graph_median_expected4->GetZaxis()->SetTitleSize(0.065);
   Graph_median_expected4->GetZaxis()->SetTitleOffset(1.1);
   Graph_median_expected4->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_median_expected4);
   
   graph->Draw("l");
   
   Double_t Graph0_fx5[5] = {
   3,
   4,
   5,
   6,
   7};
   Double_t Graph0_fy5[5] = {
   4.99905e-05,
   6.960867e-05,
   6.91139e-05,
   6.884342e-05,
   5.482714e-05};
   graph = new TGraph(5,Graph0_fx5,Graph0_fy5);
   graph->SetName("Graph0");
   graph->SetTitle("");
   graph->SetFillStyle(1000);
   graph->SetLineWidth(2);
   graph->SetMarkerStyle(7);
   
   TH1F *Graph_Graph_Graph015 = new TH1F("Graph_Graph_Graph015","",100,2.6,7.4);
   Graph_Graph_Graph015->SetMinimum(5e-07);
   Graph_Graph_Graph015->SetMaximum(0.4);
   Graph_Graph_Graph015->SetDirectory(0);
   Graph_Graph_Graph015->SetStats(0);
   Graph_Graph_Graph015->SetLineWidth(2);
   Graph_Graph_Graph015->SetMarkerStyle(20);
   Graph_Graph_Graph015->SetMarkerSize(0.9);
   Graph_Graph_Graph015->GetXaxis()->SetTitle("m_{Z'_{SSM}} [TeV]");
   Graph_Graph_Graph015->GetXaxis()->SetRange(9,92);
   Graph_Graph_Graph015->GetXaxis()->SetLabelFont(42);
   Graph_Graph_Graph015->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph_Graph015->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph_Graph015->GetXaxis()->SetTitleSize(0.055);
   Graph_Graph_Graph015->GetXaxis()->SetTitleOffset(1.25);
   Graph_Graph_Graph015->GetXaxis()->SetTitleFont(42);
   Graph_Graph_Graph015->GetYaxis()->SetTitle("Cross Section [pb]");
   Graph_Graph_Graph015->GetYaxis()->SetLabelFont(42);
   Graph_Graph_Graph015->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph_Graph015->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph_Graph015->GetYaxis()->SetTitleSize(0.05);
   Graph_Graph_Graph015->GetYaxis()->SetTickLength(0.02);
   Graph_Graph_Graph015->GetYaxis()->SetTitleOffset(1.5);
   Graph_Graph_Graph015->GetYaxis()->SetTitleFont(42);
   Graph_Graph_Graph015->GetZaxis()->SetLabelFont(42);
   Graph_Graph_Graph015->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph_Graph015->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph_Graph015->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph_Graph015->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph_Graph015->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph_Graph015);
   
   graph->Draw("lp");
   
   TLegend *leg = new TLegend(0.18,0.6,0.55,0.89,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextFont(62);
   leg->SetLineColor(0);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(0);
   TLegendEntry *entry=leg->AddEntry("NULL","95% CL Upper Limits","h");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("Graph0","Observed Limit","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("Graph1","Expected Limit #pm1#sigma, #pm2#sigma","f");

   ci = TColor::GetColor("#ffcc00");
   entry->SetFillColor(ci);
   entry->SetFillStyle(1000);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("","","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   leg->Draw();
   TLine *line = new TLine(0.195,0.713,0.258,0.713);

   ci = TColor::GetColor("#00cc00");
   line->SetLineColor(ci);
   line->SetLineWidth(15);
   line->SetNDC();
   line->Draw();
   line = new TLine(0.195,0.713,0.258,0.713);
   line->SetLineStyle(2);
   line->SetLineWidth(3);
   line->SetNDC();
   line->Draw();
   line = new TLine(5.2,0,5.2,0.4);

   ci = TColor::GetColor("#666666");
   line->SetLineColor(ci);
   line->SetLineStyle(3);
   line->Draw();
   TLatex *   tex = new TLatex(5.23,0.36,"Best fit from ");
   tex->SetTextAlign(13);

   ci = TColor::GetColor("#666666");
   tex->SetTextColor(ci);
   tex->SetTextFont(43);
   tex->SetTextSize(14);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(5.23,0.24,"Giudice, McCullough, and Teresi (2022)");
   tex->SetTextAlign(13);

   ci = TColor::GetColor("#666666");
   tex->SetTextColor(ci);
   tex->SetTextFont(43);
   tex->SetTextSize(14);
   tex->SetLineWidth(2);
   tex->Draw();
   
   Double_t _fx3001[1] = {
   5.2};
   Double_t _fy3001[1] = {
   0.002302158};
   Double_t _felx3001[1] = {
   0.045};
   Double_t _fely3001[1] = {
   7.194245e-05};
   Double_t _fehx3001[1] = {
   0.045};
   Double_t _fehy3001[1] = {
   0.0007913669};
   TGraphAsymmErrors *grae = new TGraphAsymmErrors(1,_fx3001,_fy3001,_felx3001,_fehx3001,_fely3001,_fehy3001);
   grae->SetName("");
   grae->SetTitle("");

   ci = TColor::GetColor("#cccccc");
   grae->SetFillColor(ci);
   grae->SetFillStyle(1000);
   grae->SetMarkerStyle(20);
   grae->SetMarkerSize(0.05);
   
   TH1F *Graph_Graph3001 = new TH1F("Graph_Graph3001","",100,5.146,5.254);
   Graph_Graph3001->SetMinimum(0.002143885);
   Graph_Graph3001->SetMaximum(0.003179856);
   Graph_Graph3001->SetDirectory(0);
   Graph_Graph3001->SetStats(0);
   Graph_Graph3001->SetLineWidth(2);
   Graph_Graph3001->SetMarkerStyle(20);
   Graph_Graph3001->SetMarkerSize(0.9);
   Graph_Graph3001->GetXaxis()->SetLabelFont(42);
   Graph_Graph3001->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph3001->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph3001->GetXaxis()->SetTitleSize(0.065);
   Graph_Graph3001->GetXaxis()->SetTitleOffset(1.1);
   Graph_Graph3001->GetXaxis()->SetTitleFont(42);
   Graph_Graph3001->GetYaxis()->SetLabelFont(42);
   Graph_Graph3001->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph3001->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph3001->GetYaxis()->SetTitleSize(0.065);
   Graph_Graph3001->GetYaxis()->SetTickLength(0.02);
   Graph_Graph3001->GetYaxis()->SetTitleOffset(1.1);
   Graph_Graph3001->GetYaxis()->SetTitleFont(42);
   Graph_Graph3001->GetZaxis()->SetLabelFont(42);
   Graph_Graph3001->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph3001->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph3001->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph3001->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph3001->GetZaxis()->SetTitleFont(42);
   grae->SetHistogram(Graph_Graph3001);
   
   grae->Draw("p2");
   line = new TLine(5.155,0.002302158,5.245,0.002302158);
   line->Draw();
   
   Double_t _fx6[1] = {
   5.2};
   Double_t _fy6[1] = {
   0.008561151};
   graph = new TGraph(1,_fx6,_fy6);
   graph->SetName("");
   graph->SetTitle("");
   graph->SetFillStyle(1000);
   graph->SetMarkerStyle(5);
   graph->SetMarkerSize(1.5);
   
   TH1F *Graph_Graph6 = new TH1F("Graph_Graph6","",100,5.1,6.3);
   Graph_Graph6->SetMinimum(0.007705036);
   Graph_Graph6->SetMaximum(1.108561);
   Graph_Graph6->SetDirectory(0);
   Graph_Graph6->SetStats(0);
   Graph_Graph6->SetLineWidth(2);
   Graph_Graph6->SetMarkerStyle(20);
   Graph_Graph6->SetMarkerSize(0.9);
   Graph_Graph6->GetXaxis()->SetLabelFont(42);
   Graph_Graph6->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph6->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph6->GetXaxis()->SetTitleSize(0.065);
   Graph_Graph6->GetXaxis()->SetTitleOffset(1.1);
   Graph_Graph6->GetXaxis()->SetTitleFont(42);
   Graph_Graph6->GetYaxis()->SetLabelFont(42);
   Graph_Graph6->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph6->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph6->GetYaxis()->SetTitleSize(0.065);
   Graph_Graph6->GetYaxis()->SetTickLength(0.02);
   Graph_Graph6->GetYaxis()->SetTitleOffset(1.1);
   Graph_Graph6->GetYaxis()->SetTitleFont(42);
   Graph_Graph6->GetZaxis()->SetLabelFont(42);
   Graph_Graph6->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph6->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph6->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph6->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph6->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph6);
   
   graph->Draw("p");
      tex = new TLatex(5.3,0.008561151,"ATLAS Observed Limit (w/ #Alpha #times #varepsilon = 1%)");
   tex->SetTextAlign(12);

   ci = TColor::GetColor("#666666");
   tex->SetTextColor(ci);
   tex->SetTextFont(43);
   tex->SetTextSize(14);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(5.3,0.002302158,"ATLAS Expected Limit #pm1#sigma");
   tex->SetTextAlign(12);

   ci = TColor::GetColor("#666666");
   tex->SetTextColor(ci);
   tex->SetTextFont(43);
   tex->SetTextSize(14);
   tex->SetLineWidth(2);
   tex->Draw();
   
   TH1F *Graph_copy = new TH1F("Graph_copy","",100,2.6,7.4);
   Graph_copy->SetMinimum(5e-07);
   Graph_copy->SetMaximum(0.4);
   Graph_copy->SetDirectory(0);
   Graph_copy->SetStats(0);
   Graph_copy->SetLineWidth(2);
   Graph_copy->SetMarkerStyle(20);
   Graph_copy->SetMarkerSize(0.9);
   Graph_copy->GetXaxis()->SetTitle("m_{Z'_{SSM}} [TeV]");
   Graph_copy->GetXaxis()->SetRange(9,92);
   Graph_copy->GetXaxis()->SetLabelFont(42);
   Graph_copy->GetXaxis()->SetLabelOffset(0.015);
   Graph_copy->GetXaxis()->SetLabelSize(0.05);
   Graph_copy->GetXaxis()->SetTitleSize(0.055);
   Graph_copy->GetXaxis()->SetTitleOffset(1.25);
   Graph_copy->GetXaxis()->SetTitleFont(42);
   Graph_copy->GetYaxis()->SetTitle("Cross Section [pb]");
   Graph_copy->GetYaxis()->SetLabelFont(42);
   Graph_copy->GetYaxis()->SetLabelOffset(0.015);
   Graph_copy->GetYaxis()->SetLabelSize(0.05);
   Graph_copy->GetYaxis()->SetTitleSize(0.05);
   Graph_copy->GetYaxis()->SetTickLength(0.02);
   Graph_copy->GetYaxis()->SetTitleOffset(1.5);
   Graph_copy->GetYaxis()->SetTitleFont(42);
   Graph_copy->GetZaxis()->SetLabelFont(42);
   Graph_copy->GetZaxis()->SetLabelOffset(0.015);
   Graph_copy->GetZaxis()->SetLabelSize(0.05);
   Graph_copy->GetZaxis()->SetTitleSize(0.065);
   Graph_copy->GetZaxis()->SetTitleOffset(1.1);
   Graph_copy->GetZaxis()->SetTitleFont(42);
   Graph_copy->Draw("sameaxis");
      tex = new TLatex(0.95,0.915,"101 fb^{-1} (13 TeV)");
tex->SetNDC();
   tex->SetTextAlign(31);
   tex->SetTextFont(42);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.15,0.915,"CMS");
tex->SetNDC();
   tex->SetTextFont(61);
   tex->SetTextSize(0.08);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.3,0.96," ");
tex->SetNDC();
   tex->SetTextAlign(23);
   tex->SetTextFont(52);
   tex->SetTextSize(0.0608);
   tex->SetLineWidth(2);
   tex->Draw();
   climits->Modified();
   climits->cd();
   climits->SetSelected(climits);
}
