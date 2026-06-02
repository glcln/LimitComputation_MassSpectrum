#include <iostream>
#include <TFile.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TMath.h>
#include <vector>

using namespace TMath;
using namespace std;

void plot_graph()
{
    // x-section for stau308 in [pb]
    float K1C1 = 0.0006948431;
    float K2C2 = 0.0006952972;
    float K1C2 = 0.0006727561;
    float K1C1_codeChanged = 0.0006852916;

    float mass = 0.308; // [TeV]

    // ----------
    TH1F *h_K1C1 = new TH1F("h_K1C1", "h_K1C1", 1, 0.3075, 0.3085);
    h_K1C1->SetMarkerStyle(20);
    h_K1C1->SetMarkerColor(kRed);
    h_K1C1->SetBinContent(1, K1C1);
    h_K1C1->GetXaxis()->SetTitle("mass [TeV]");
    h_K1C1->GetYaxis()->SetTitle("Cross Section [pb]");
    h_K1C1->SetAxisRange(0.00001,0.01,"Y");

    TH1F *h_K2C2 = new TH1F("h_K2C2", "h_K2C2", 1, 0.3075, 0.3085);
    h_K2C2->SetMarkerStyle(21);
    h_K2C2->SetMarkerColor(kBlue);
    h_K2C2->SetBinContent(1, K2C2);

    TH1F *h_K1C2 = new TH1F("h_K1C2", "h_K1C2", 1, 0.3075, 0.3085);
    h_K1C2->SetMarkerStyle(22);
    h_K1C2->SetMarkerColor(kGreen);
    h_K1C2->SetBinContent(1, K1C2);

    TH1F *h_K1C1_codeChanged = new TH1F("h_K1C1_codeChanged", "h_K1C1_codeChanged", 1, 0.3075, 0.3085);
    h_K1C1_codeChanged->SetMarkerStyle(23);
    h_K1C1_codeChanged->SetMarkerColor(kBlack);
    h_K1C1_codeChanged->SetBinContent(1, K1C1_codeChanged);
    // ----------


    TCanvas *c = new TCanvas("c", "c", 800, 600);
    h_K1C1->Draw("P");
    h_K2C2->Draw("same P");
    h_K1C2->Draw("same P");
    h_K1C1_codeChanged->Draw("same P");

    TLegend *leg = new TLegend(0.6, 0.6, 0.9, 0.9);
    leg->AddEntry(h_K1C1, "K1C1", "P");
    leg->AddEntry(h_K2C2, "K2C2", "P");
    leg->AddEntry(h_K1C2, "K1C2", "P");
    leg->AddEntry(h_K1C1_codeChanged, "K1C1_codeChanged", "P");
    leg->SetBorderSize(0);
    leg->SetFillStyle(0);
    leg->Draw();

    c->SetLogy();
    c->SaveAs("Compare_stau308_CLS.root");

    return;
}

void Compare_stau308_CLS()
{
    plot_graph();
}