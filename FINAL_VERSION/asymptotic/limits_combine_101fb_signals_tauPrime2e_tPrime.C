void limits_combine_101fb_signals_tauPrime2e_tPrime()
{
//=========Macro generated from canvas: climits/climits
//=========  (Wed Dec 11 12:28:06 2024) by ROOT version 6.22/09
   TCanvas *climits = new TCanvas("climits", "climits",0,0,700,600);
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(0);
   climits->SetHighLightColor(2);
   climits->Range(0.4011,-6.021442,2.9751,-1.218695);
   climits->SetFillColor(0);
   climits->SetBorderMode(0);
   climits->SetBorderSize(2);
   climits->SetLogy();
   climits->SetTickx(1);
   climits->SetTicky(1);
   climits->SetLeftMargin(0.15);
   climits->SetRightMargin(0.05);
   climits->SetBottomMargin(0.15);
   climits->SetFrameBorderMode(0);
   climits->SetFrameBorderMode(0);
   
   Double_t observed_fx1[7] = {
   0.4,
   0.5,
   1,
   1.4,
   1.8,
   2.2,
   2.6};
   Double_t observed_fy1[7] = {
   0.0004444012,
   0.0001421057,
   5.357684e-05,
   5.3077e-05,
   5.008227e-05,
   4.755428e-05,
   4.812661e-05};
   TGraph *graph = new TGraph(7,observed_fx1,observed_fy1);
   graph->SetName("observed");
   graph->SetTitle("observed_title");
   graph->SetFillStyle(1000);
   graph->SetLineWidth(2);
   graph->SetMarkerStyle(7);
   
   TH1F *Graph_observed1 = new TH1F("Graph_observed1","observed_title",100,0.18,2.82);
   Graph_observed1->SetMinimum(5e-06);
   Graph_observed1->SetMaximum(0.02);
   Graph_observed1->SetDirectory(0);
   Graph_observed1->SetStats(0);
   Graph_observed1->SetLineWidth(2);
   Graph_observed1->SetMarkerStyle(20);
   Graph_observed1->SetMarkerSize(0.9);
   Graph_observed1->GetXaxis()->SetTitle("m_{#tau'^{#scale[0.5]{ }2e}} [TeV]");
   Graph_observed1->GetXaxis()->SetRange(24,101);
   Graph_observed1->GetXaxis()->SetLabelFont(42);
   Graph_observed1->GetXaxis()->SetLabelOffset(0.015);
   Graph_observed1->GetXaxis()->SetLabelSize(0.05);
   Graph_observed1->GetXaxis()->SetTitleSize(0.055);
   Graph_observed1->GetXaxis()->SetTitleOffset(1.25);
   Graph_observed1->GetXaxis()->SetTitleFont(42);
   Graph_observed1->GetYaxis()->SetTitle("Cross Section [pb]");
   Graph_observed1->GetYaxis()->SetLabelFont(42);
   Graph_observed1->GetYaxis()->SetLabelOffset(0.015);
   Graph_observed1->GetYaxis()->SetLabelSize(0.05);
   Graph_observed1->GetYaxis()->SetTitleSize(0.05);
   Graph_observed1->GetYaxis()->SetTickLength(0.02);
   Graph_observed1->GetYaxis()->SetTitleOffset(1.5);
   Graph_observed1->GetYaxis()->SetTitleFont(42);
   Graph_observed1->GetZaxis()->SetLabelFont(42);
   Graph_observed1->GetZaxis()->SetLabelOffset(0.015);
   Graph_observed1->GetZaxis()->SetLabelSize(0.05);
   Graph_observed1->GetZaxis()->SetTitleSize(0.065);
   Graph_observed1->GetZaxis()->SetTitleOffset(1.1);
   Graph_observed1->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_observed1);
   
   graph->Draw("ap");
   
   Double_t Graph0_fx2[16] = {
   0.4,
   0.5,
   1,
   1.4,
   1.8,
   2.2,
   2.6,
   2.6,
   2.6,
   2.6,
   2.2,
   1.8,
   1.4,
   1,
   0.5,
   0.4};
   Double_t Graph0_fy2[16] = {
   0.0004444239,
   0.0003166484,
   0.0001915539,
   0.0001699957,
   0.0001552257,
   0.0001458002,
   0.0001467103,
   0.0001467103,
   1.413474e-05,
   1.413474e-05,
   1.423434e-05,
   1.535394e-05,
   1.790678e-05,
   2.313069e-05,
   6.967457e-05,
   0.0001120243};
   graph = new TGraph(16,Graph0_fx2,Graph0_fy2);
   graph->SetName("Graph0");
   graph->SetTitle("Graph");

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#ffcc00");
   graph->SetFillColor(ci);
   graph->SetFillStyle(1000);
   graph->SetLineColor(0);
   graph->SetMarkerStyle(20);
   graph->SetMarkerSize(0.9);
   
   TH1F *Graph_Graph02 = new TH1F("Graph_Graph02","Graph",100,0.18,2.82);
   Graph_Graph02->SetMinimum(1.272126e-05);
   Graph_Graph02->SetMaximum(0.0004874529);
   Graph_Graph02->SetDirectory(0);
   Graph_Graph02->SetStats(0);
   Graph_Graph02->SetLineWidth(2);
   Graph_Graph02->SetMarkerStyle(20);
   Graph_Graph02->SetMarkerSize(0.9);
   Graph_Graph02->GetXaxis()->SetLabelFont(42);
   Graph_Graph02->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph02->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph02->GetXaxis()->SetTitleSize(0.065);
   Graph_Graph02->GetXaxis()->SetTitleOffset(1.1);
   Graph_Graph02->GetXaxis()->SetTitleFont(42);
   Graph_Graph02->GetYaxis()->SetLabelFont(42);
   Graph_Graph02->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph02->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph02->GetYaxis()->SetTitleSize(0.065);
   Graph_Graph02->GetYaxis()->SetTickLength(0.02);
   Graph_Graph02->GetYaxis()->SetTitleOffset(1.1);
   Graph_Graph02->GetYaxis()->SetTitleFont(42);
   Graph_Graph02->GetZaxis()->SetLabelFont(42);
   Graph_Graph02->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph02->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph02->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph02->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph02->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph02);
   
   graph->Draw("lf");
   
   Double_t Graph1_fx3[16] = {
   0.4,
   0.5,
   1,
   1.4,
   1.8,
   2.2,
   2.6,
   2.6,
   2.6,
   2.6,
   2.2,
   1.8,
   1.4,
   1,
   0.5,
   0.4};
   Double_t Graph1_fy3[16] = {
   0.0003144675,
   0.0002146338,
   0.0001142182,
   0.0001071564,
   9.906698e-05,
   9.343379e-05,
   9.420933e-05,
   9.420933e-05,
   2.506118e-05,
   2.506118e-05,
   2.476963e-05,
   2.678683e-05,
   3.007779e-05,
   3.652235e-05,
   9.607038e-05,
   0.0001508749};
   graph = new TGraph(16,Graph1_fx3,Graph1_fy3);
   graph->SetName("Graph1");
   graph->SetTitle("Graph");

   ci = TColor::GetColor("#00cc00");
   graph->SetFillColor(ci);
   graph->SetFillStyle(1000);
   graph->SetLineColor(0);
   graph->SetMarkerStyle(20);
   graph->SetMarkerSize(0.9);
   
   TH1F *Graph_Graph13 = new TH1F("Graph_Graph13","Graph",100,0.18,2.82);
   Graph_Graph13->SetMinimum(2.229267e-05);
   Graph_Graph13->SetMaximum(0.0003434373);
   Graph_Graph13->SetDirectory(0);
   Graph_Graph13->SetStats(0);
   Graph_Graph13->SetLineWidth(2);
   Graph_Graph13->SetMarkerStyle(20);
   Graph_Graph13->SetMarkerSize(0.9);
   Graph_Graph13->GetXaxis()->SetLabelFont(42);
   Graph_Graph13->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph13->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph13->GetXaxis()->SetTitleSize(0.065);
   Graph_Graph13->GetXaxis()->SetTitleOffset(1.1);
   Graph_Graph13->GetXaxis()->SetTitleFont(42);
   Graph_Graph13->GetYaxis()->SetLabelFont(42);
   Graph_Graph13->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph13->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph13->GetYaxis()->SetTitleSize(0.065);
   Graph_Graph13->GetYaxis()->SetTickLength(0.02);
   Graph_Graph13->GetYaxis()->SetTitleOffset(1.1);
   Graph_Graph13->GetYaxis()->SetTitleFont(42);
   Graph_Graph13->GetZaxis()->SetLabelFont(42);
   Graph_Graph13->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph13->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph13->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph13->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph13->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph13);
   
   graph->Draw("lf");
   
   Double_t median_expected_fx4[7] = {
   0.4,
   0.5,
   1,
   1.4,
   1.8,
   2.2,
   2.6};
   Double_t median_expected_fy4[7] = {
   0.0002156258,
   0.000141561,
   6.299423e-05,
   5.590408e-05,
   5.104688e-05,
   4.794727e-05,
   4.824656e-05};
   graph = new TGraph(7,median_expected_fx4,median_expected_fy4);
   graph->SetName("median_expected");
   graph->SetTitle("median_expected_title");
   graph->SetFillStyle(1000);
   graph->SetLineStyle(2);
   graph->SetLineWidth(3);
   graph->SetMarkerStyle(21);
   graph->SetMarkerSize(0);
   
   TH1F *Graph_median_expected4 = new TH1F("Graph_median_expected4","median_expected_title",100,0.18,2.82);
   Graph_median_expected4->SetMinimum(3.117942e-05);
   Graph_median_expected4->SetMaximum(0.0002323936);
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
   
   Double_t observed_fx5[7] = {
   0.4,
   0.5,
   1,
   1.4,
   1.8,
   2.2,
   2.6};
   Double_t observed_fy5[7] = {
   0.0004444012,
   0.0001421057,
   5.357684e-05,
   5.3077e-05,
   5.008227e-05,
   4.755428e-05,
   4.812661e-05};
   graph = new TGraph(7,observed_fx5,observed_fy5);
   graph->SetName("observed");
   graph->SetTitle("observed_title");
   graph->SetFillStyle(1000);
   graph->SetLineWidth(2);
   graph->SetMarkerStyle(7);
   
   TH1F *Graph_Graph_observed15 = new TH1F("Graph_Graph_observed15","observed_title",100,0.18,2.82);
   Graph_Graph_observed15->SetMinimum(5e-06);
   Graph_Graph_observed15->SetMaximum(0.02);
   Graph_Graph_observed15->SetDirectory(0);
   Graph_Graph_observed15->SetStats(0);
   Graph_Graph_observed15->SetLineWidth(2);
   Graph_Graph_observed15->SetMarkerStyle(20);
   Graph_Graph_observed15->SetMarkerSize(0.9);
   Graph_Graph_observed15->GetXaxis()->SetTitle("m_{#tau'^{#scale[0.5]{ }2e}} [TeV]");
   Graph_Graph_observed15->GetXaxis()->SetRange(24,101);
   Graph_Graph_observed15->GetXaxis()->SetLabelFont(42);
   Graph_Graph_observed15->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph_observed15->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph_observed15->GetXaxis()->SetTitleSize(0.055);
   Graph_Graph_observed15->GetXaxis()->SetTitleOffset(1.25);
   Graph_Graph_observed15->GetXaxis()->SetTitleFont(42);
   Graph_Graph_observed15->GetYaxis()->SetTitle("Cross Section [pb]");
   Graph_Graph_observed15->GetYaxis()->SetLabelFont(42);
   Graph_Graph_observed15->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph_observed15->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph_observed15->GetYaxis()->SetTitleSize(0.05);
   Graph_Graph_observed15->GetYaxis()->SetTickLength(0.02);
   Graph_Graph_observed15->GetYaxis()->SetTitleOffset(1.5);
   Graph_Graph_observed15->GetYaxis()->SetTitleFont(42);
   Graph_Graph_observed15->GetZaxis()->SetLabelFont(42);
   Graph_Graph_observed15->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph_observed15->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph_observed15->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph_observed15->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph_observed15->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph_observed15);
   
   graph->Draw("lp");
   
   Double_t _fx6[7] = {
   0.4,
   0.5,
   1,
   1.4,
   1.8,
   2.2,
   2.6};
   Double_t _fy6[7] = {
   0.0544,
   0.025,
   0.0006553,
   7.477e-05,
   1.056e-05,
   1.67e-06,
   2.913e-07};
   graph = new TGraph(7,_fx6,_fy6);
   graph->SetName("");
   graph->SetTitle("");
   graph->SetFillStyle(1000);
   graph->SetLineColor(4);
   graph->SetLineWidth(3);
   graph->SetMarkerColor(4);
   graph->SetMarkerStyle(23);
   graph->SetMarkerSize(0.5);
   
   TH1F *Graph_Graph6 = new TH1F("Graph_Graph6","",100,0.18,2.82);
   Graph_Graph6->SetMinimum(0.0003);
   Graph_Graph6->SetMaximum(100);
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
   
   graph->Draw("l");
   
   Double_t _fx7[7] = {
   0.4,
   0.5,
   1,
   1.4,
   1.8,
   2.2,
   2.6};
   Double_t _fy7[7] = {
   0.04896,
   0.0225,
   0.00058977,
   6.7293e-05,
   9.504e-06,
   1.503e-06,
   2.6217e-07};
   graph = new TGraph(7,_fx7,_fy7);
   graph->SetName("");
   graph->SetTitle("");
   graph->SetFillStyle(1000);
   graph->SetLineColor(4);
   graph->SetLineStyle(2);
   graph->SetLineWidth(2);
   graph->SetMarkerColor(4);
   graph->SetMarkerStyle(23);
   graph->SetMarkerSize(0.5);
   
   TH1F *Graph_Graph7 = new TH1F("Graph_Graph7","",100,0.18,2.82);
   Graph_Graph7->SetMinimum(2.35953e-07);
   Graph_Graph7->SetMaximum(0.05385597);
   Graph_Graph7->SetDirectory(0);
   Graph_Graph7->SetStats(0);
   Graph_Graph7->SetLineWidth(2);
   Graph_Graph7->SetMarkerStyle(20);
   Graph_Graph7->SetMarkerSize(0.9);
   Graph_Graph7->GetXaxis()->SetLabelFont(42);
   Graph_Graph7->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph7->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph7->GetXaxis()->SetTitleSize(0.065);
   Graph_Graph7->GetXaxis()->SetTitleOffset(1.1);
   Graph_Graph7->GetXaxis()->SetTitleFont(42);
   Graph_Graph7->GetYaxis()->SetLabelFont(42);
   Graph_Graph7->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph7->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph7->GetYaxis()->SetTitleSize(0.065);
   Graph_Graph7->GetYaxis()->SetTickLength(0.02);
   Graph_Graph7->GetYaxis()->SetTitleOffset(1.1);
   Graph_Graph7->GetYaxis()->SetTitleFont(42);
   Graph_Graph7->GetZaxis()->SetLabelFont(42);
   Graph_Graph7->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph7->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph7->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph7->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph7->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph7);
   
   graph->Draw("l");
   
   Double_t _fx8[7] = {
   0.4,
   0.5,
   1,
   1.4,
   1.8,
   2.2,
   2.6};
   Double_t _fy8[7] = {
   0.05984,
   0.0275,
   0.00072083,
   8.2247e-05,
   1.1616e-05,
   1.837e-06,
   3.2043e-07};
   graph = new TGraph(7,_fx8,_fy8);
   graph->SetName("");
   graph->SetTitle("");
   graph->SetFillStyle(1000);
   graph->SetLineColor(4);
   graph->SetLineStyle(2);
   graph->SetLineWidth(2);
   graph->SetMarkerColor(4);
   graph->SetMarkerStyle(23);
   graph->SetMarkerSize(0.5);
   
   TH1F *Graph_Graph8 = new TH1F("Graph_Graph8","",100,0.18,2.82);
   Graph_Graph8->SetMinimum(2.88387e-07);
   Graph_Graph8->SetMaximum(0.06582397);
   Graph_Graph8->SetDirectory(0);
   Graph_Graph8->SetStats(0);
   Graph_Graph8->SetLineWidth(2);
   Graph_Graph8->SetMarkerStyle(20);
   Graph_Graph8->SetMarkerSize(0.9);
   Graph_Graph8->GetXaxis()->SetLabelFont(42);
   Graph_Graph8->GetXaxis()->SetLabelOffset(0.015);
   Graph_Graph8->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph8->GetXaxis()->SetTitleSize(0.065);
   Graph_Graph8->GetXaxis()->SetTitleOffset(1.1);
   Graph_Graph8->GetXaxis()->SetTitleFont(42);
   Graph_Graph8->GetYaxis()->SetLabelFont(42);
   Graph_Graph8->GetYaxis()->SetLabelOffset(0.015);
   Graph_Graph8->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph8->GetYaxis()->SetTitleSize(0.065);
   Graph_Graph8->GetYaxis()->SetTickLength(0.02);
   Graph_Graph8->GetYaxis()->SetTitleOffset(1.1);
   Graph_Graph8->GetYaxis()->SetTitleFont(42);
   Graph_Graph8->GetZaxis()->SetLabelFont(42);
   Graph_Graph8->GetZaxis()->SetLabelOffset(0.015);
   Graph_Graph8->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph8->GetZaxis()->SetTitleSize(0.065);
   Graph_Graph8->GetZaxis()->SetTitleOffset(1.1);
   Graph_Graph8->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph8);
   
   graph->Draw("l");
   TLine *line = new TLine(1.47217,-1111,1.47217,5.252374e-05);
   line->SetLineStyle(2);
   line->Draw();
   
   TLegend *leg = new TLegend(0.5,0.6,0.92,0.89,NULL,"brNDC");
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
   entry=leg->AddEntry("observed","Observed Limit","l");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("Graph0","Expected Limit #pm1#sigma, #pm2#sigma","f");

   ci = TColor::GetColor("#ffcc00");
   entry->SetFillColor(ci);
   entry->SetFillStyle(1000);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("","#sigma^{NNLO+NNLL}_{th}(pp#rightarrow#tau'^{#scale[0.5]{ }2e}#tau'^{#scale[0.5]{ }2e})#pm1#sigma","l");
   entry->SetLineColor(4);
   entry->SetLineStyle(1);
   entry->SetLineWidth(3);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   leg->Draw();
   line = new TLine(0.517,0.71,0.588,0.71);

   ci = TColor::GetColor("#00cc00");
   line->SetLineColor(ci);
   line->SetLineWidth(15);
   line->SetNDC();
   line->Draw();
   line = new TLine(0.517,0.71,0.588,0.71);
   line->SetLineStyle(2);
   line->SetLineWidth(3);
   line->SetNDC();
   line->Draw();
   line = new TLine(0.517,0.648,0.588,0.648);
   line->SetLineColor(4);
   line->SetLineStyle(2);
   line->SetLineWidth(2);
   line->SetNDC();
   line->Draw();
   line = new TLine(0.517,0.625,0.588,0.625);
   line->SetLineColor(4);
   line->SetLineStyle(2);
   line->SetLineWidth(2);
   line->SetNDC();
   line->Draw();
   line = new TLine(1.462317,0,1.462317,5.511803e-05);

   ci = TColor::GetColor("#666666");
   line->SetLineColor(ci);
   line->SetLineStyle(2);
   line->Draw();
   TLatex *   tex = new TLatex(1.457317,0,"  1.46 TeV");

   ci = TColor::GetColor("#666666");
   tex->SetTextColor(ci);
   tex->SetTextFont(43);
   tex->SetTextSize(14);
   tex->SetTextAngle(90);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(1.52217,0,"  1.47 TeV");
   tex->SetTextFont(43);
   tex->SetTextSize(14);
   tex->SetTextAngle(90);
   tex->SetLineWidth(2);
   tex->Draw();
   
   TH1F *observed_copy__1 = new TH1F("observed_copy__1","observed_title",100,0.18,2.82);
   observed_copy__1->SetMinimum(5e-06);
   observed_copy__1->SetMaximum(0.02);
   observed_copy__1->SetDirectory(0);
   observed_copy__1->SetStats(0);
   observed_copy__1->SetLineWidth(2);
   observed_copy__1->SetMarkerStyle(20);
   observed_copy__1->SetMarkerSize(0.9);
   observed_copy__1->GetXaxis()->SetTitle("m_{#tau'^{#scale[0.5]{ }2e}} [TeV]");
   observed_copy__1->GetXaxis()->SetRange(24,101);
   observed_copy__1->GetXaxis()->SetLabelFont(42);
   observed_copy__1->GetXaxis()->SetLabelOffset(0.015);
   observed_copy__1->GetXaxis()->SetLabelSize(0.05);
   observed_copy__1->GetXaxis()->SetTitleSize(0.055);
   observed_copy__1->GetXaxis()->SetTitleOffset(1.25);
   observed_copy__1->GetXaxis()->SetTitleFont(42);
   observed_copy__1->GetYaxis()->SetTitle("Cross Section [pb]");
   observed_copy__1->GetYaxis()->SetLabelFont(42);
   observed_copy__1->GetYaxis()->SetLabelOffset(0.015);
   observed_copy__1->GetYaxis()->SetLabelSize(0.05);
   observed_copy__1->GetYaxis()->SetTitleSize(0.05);
   observed_copy__1->GetYaxis()->SetTickLength(0.02);
   observed_copy__1->GetYaxis()->SetTitleOffset(1.5);
   observed_copy__1->GetYaxis()->SetTitleFont(42);
   observed_copy__1->GetZaxis()->SetLabelFont(42);
   observed_copy__1->GetZaxis()->SetLabelOffset(0.015);
   observed_copy__1->GetZaxis()->SetLabelSize(0.05);
   observed_copy__1->GetZaxis()->SetTitleSize(0.065);
   observed_copy__1->GetZaxis()->SetTitleOffset(1.1);
   observed_copy__1->GetZaxis()->SetTitleFont(42);
   observed_copy__1->Draw("sameaxis");
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
      tex = new TLatex(0.3,0.96,"");
tex->SetNDC();
   tex->SetTextAlign(13);
   tex->SetTextFont(52);
   tex->SetTextSize(0.0608);
   tex->SetLineWidth(2);
   tex->Draw();
   climits->Modified();
   climits->cd();
   climits->SetSelected(climits);
}
