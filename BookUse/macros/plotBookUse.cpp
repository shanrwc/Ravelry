#include<stdio.h>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <set>

#include "TROOT.h"
#include "TFile.h"
#include "TStyle.h"
#include "TCanvas.h"
#include "TRandom.h"
#include "TRandom3.h"
#include "TTree.h"
#include "TF1.h"
#include "TF2.h"
#include "TFile.h"
#include "TMath.h"
#include "TH2.h"
#include "TH1.h"
#include "TLorentzVector.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TPaveText.h"
#include "TColor.h"
#include "TGraphErrors.h"
#include "THStack.h"
#include "TLine.h"

using namespace std;

template<typename T>
std::string makeString(T const& value)
{
  std::stringstream sstr;
  sstr << fixed;
  sstr << setprecision(2);
  sstr << value;
  return sstr.str();
}

vector<string> splitString(string phrase)
{
  stringstream ss(phrase);
  string buffer;
  vector<string> pieces;

  while(ss >> buffer)
  {
    pieces.push_back(buffer);
  }

  return(pieces);
}

double makeDouble(string input)
{
  istringstream stm;
  stm.str(input);
  double num;
  stm >> num;

  return(num);
}

int countPatterns(string all_patterns)
{
  set<string> patts;
  while (all_patterns.length() > 0)
  {
    if (all_patterns.find("-") != string::npos)
    {
      patts.insert(all_patterns.substr(0,all_patterns.find("-")));
      all_patterns = all_patterns.substr(all_patterns.find("-")+1,string::npos);
    }
    else
    {
      patts.insert(all_patterns);
      all_patterns = "";
    }
  }
  return((int)patts.size());
}

string convertTitle(string urltitle)
{
  if (urltitle.compare("socks-from-the-toe-up") == 0)
  {
    return("Socks From the Toe Up");
  }
  else if (urltitle.compare("toe-up-socks-for-every-body") == 0)
  {
    return("Toe-Up Socks for Every Body");
  }
  else if (urltitle.compare("sock-innovation") == 0)
  {
    return("Sock Innovation");
  }
  else if (urltitle.compare("knitting-vintage-socks") == 0)
  {
    return("Knitting Vintage Socks");
  }
  else if (urltitle.compare("knitting-on-the-road") == 0)
  {
    return("Knitting on the Road");
  }
  else if (urltitle.compare("the-knitters-book-of-socks") == 0)
  {
    return("The Knitter's Book of Socks");
  }
  else if (urltitle.compare("think-outside-the-sox") == 0)
  {
    return("Think Outside the Sox");
  }
  else if (urltitle.compare("knitted-lace-of-estonia") == 0)
  {
    return("Knitted Lace of Estonia");
  }
  else if (urltitle.compare("victorian-lace-today") == 0)
  {
    return("Victorian Lace Today");
  }  
  else if (urltitle.compare("wendy-knits-lace") == 0)
  {
    return("Wendy Knits Lace");
  }
  else if (urltitle.compare("lace-one-skein-wonders-101-projects-celebrating-the-possibilities-of-lace") == 0)
  {
    return("Lace One-Skein Wonders");
  }
  else if (urltitle.compare("new-vintage-lace") == 0)
  {
    return("New Vintage Lace");
  }
  else if (urltitle.compare("wrapped-in-lace-knitted-heirloom-designs-from-around-the-world") == 0)
  {
    return("Wrapped in Lace");
  }
  else
  {
    return(urltitle);
  }
}

//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////

void plotBookUse(string type = "socks")
{
  gStyle->SetOptStat(0);
  gStyle->SetPalette(1);

  //Loop over input files of RAW data
  //For each, create TH1D filled with count data
  //Make histogram(s) pretty.

  vector<string> inputFiles;
  if (type.compare("socks") == 0)
  {
    inputFiles.push_back("socks-from-the-toe-up");
    inputFiles.push_back("toe-up-socks-for-every-body");
    inputFiles.push_back("sock-innovation");
    inputFiles.push_back("knitting-vintage-socks");
    inputFiles.push_back("knitting-on-the-road");
    inputFiles.push_back("the-knitters-book-of-socks");
    inputFiles.push_back("think-outside-the-sox");
  }
  else if (type.compare("lace") == 0)
  {
    inputFiles.push_back("knitted-lace-of-estonia");
    inputFiles.push_back("victorian-lace-today");
    inputFiles.push_back("wendy-knits-lace");
    inputFiles.push_back("lace-one-skein-wonders-101-projects-celebrating-the-possibilities-of-lace");
inputFiles.push_back("new-vintage-lace");
    inputFiles.push_back("wrapped-in-lace-knitted-heirloom-designs-from-around-the-world");
  }

  //Histograms that will be bar graphs
  TH1D* histAvg = new TH1D("bar_avgProjs","bar_avgProjs",(int)inputFiles.size(),0,(int)inputFiles.size());
  TH1D* histPatt = new TH1D("bar_avgPatt","bar_avgPatt",(int)inputFiles.size(),0,(int)inputFiles.size());
  TH1D* histUsed = new TH1D("bar_Used","bar_Used",(int)inputFiles.size(),0,(int)inputFiles.size());

  //Make file for latex table
  ofstream outfile;
  outfile.open("book_usage.txt");
  outfile << fixed << setprecision(3);
  outfile << "\\begin{tabular}{|c|c|c|c|}" << endl;
  outfile << "\\hline" << endl;
  outfile << "Title & Average Projects & Average Patterns & Fraction Used\\\\" << endl;
  outfile << "\\hline" << endl;

  for (int nFile = 0; nFile != (int)inputFiles.size(); ++nFile)
  {
    //set ints to store some numbers
    int nPatterns = 0;
    int nProjects = 0;
    int nUsers = 0;
    int nUniqueUses = 0;

    //Make histogram
    TH1D* histo1 = new TH1D((inputFiles[nFile]+"-proj").c_str(),(inputFiles[nFile]+"-proj").c_str(),60,-0.5,59.5);
    TH1D* histo2 = new TH1D((inputFiles[nFile]+"-patt").c_str(),(inputFiles[nFile]+"-patt").c_str(),30,-0.5,29.5);

    ifstream infile (("../data/"+inputFiles[nFile]+"_RAW.txt").c_str());
    string line;

    if (infile.is_open())
    {
      while (infile.good())
      {
	getline(infile,line);

	vector<string> pieces = splitString(line);
	if ((int)pieces.size() < 2) continue;

	if (pieces[0].find("NPATTERNS:") != string::npos)
	{
	  nPatterns = int(makeDouble(pieces[1]));
	}
	else if (pieces[0].find("NPROJECTS:") != string::npos)
	{
	  nProjects = int(makeDouble(pieces[1]));
	}
	else if (pieces[0].compare("NUSERS:") == 0)
	{
	  nUsers = int(makeDouble(pieces[1]));
	}
	else if (pieces[0].compare("COUNT:") == 0)
	{
	  histo1->Fill(makeDouble(pieces[2]));
	  double temp = countPatterns(pieces[3]);
	  histo2->Fill(temp);
	  nUniqueUses += temp;
	}
	
      }//closes while loop over infile's goodness
    }//closes if-statement over infile's openness

    //Check that you have the inputs you need
    if (nPatterns == 0 || nProjects == 0 || nUsers == 0 || histo1->Integral() < nUsers)
    {
      cout << "Input file " << inputFiles[nFile] << " doesn't have full information!" << endl;
      cout << nPatterns << " " << nProjects << " " << nUsers << " " << histo1->Integral() << endl;
      return;
    }

    //Calculate averages
    double avgProjs = double(nProjects)/nUsers;
    double usage = double(nUniqueUses)/nUsers;
    if (fabs(usage-histo2->GetMean()) > 0.01)
    {
      cout << "usage doesn't match histogram mean!" << endl;
    }

    //Write stuff to table
    outfile << convertTitle(inputFiles[nFile]) << " & " << avgProjs << " & " << usage << " & " << usage/nPatterns <<"\\\\" << endl;

    //Fill bar graphs
    histAvg->GetXaxis()->SetBinLabel(nFile+1,convertTitle(inputFiles[nFile]).c_str());
    histAvg->SetBinContent(nFile+1,avgProjs);
    histAvg->SetBinError(nFile+1,sqrt(nProjects)/nUsers);
    histPatt->GetXaxis()->SetBinLabel(nFile+1,convertTitle(inputFiles[nFile]).c_str());
    histPatt->SetBinContent(nFile+1,usage);
    histPatt->SetBinError(nFile+1,sqrt(nUniqueUses)/nUsers);
    histUsed->GetXaxis()->SetBinLabel(nFile+1,convertTitle(inputFiles[nFile]).c_str());
    histUsed->SetBinContent(nFile+1,usage/nPatterns);
    histUsed->SetBinError(nFile+1,sqrt(nUniqueUses)/(nUsers*nPatterns));

    //Make histogram pretty
    TCanvas* pad = new TCanvas(inputFiles[nFile].c_str(),(convertTitle(inputFiles[nFile])).c_str(),14,33,800,400);
    pad->SetFillColor(0);
    pad->SetTitle((convertTitle(inputFiles[nFile])).c_str());
    pad->Divide(2,1);

    pad->cd(1);
    gPad->SetLeftMargin(0.15);
    gPad->SetBottomMargin(0.14);
    histo1->SetTitle("");
    histo1->SetLineWidth(2);
    histo1->SetLineColor(kAzure - 3);
    histo1->SetLineColor(kAzure - 3);
    histo1->GetXaxis()->SetTitleSize(0.05);
    histo1->GetXaxis()->SetTitle("Projects per User");
    histo1->GetXaxis()->SetTitleOffset(1.2);
    histo1->GetYaxis()->SetTitleSize(0.05);
    histo1->GetYaxis()->SetTitle("Users");
    histo1->GetYaxis()->SetTitleOffset(1.3);
    histo1->Draw();

    TLatex* header = new TLatex();
    header->SetTextSize(0.05);
    header->SetNDC();
    string head = convertTitle(inputFiles[nFile]);
    header->DrawLatex(0.2,0.91,head.c_str());

    TPaveText* pave1 = new TPaveText(0.5,0.65,0.8,0.8,"NDC");
    pave1->SetFillColor(0);
    pave1->AddText(("Average Projects: "+makeString(avgProjs)).c_str());
    pave1->Draw();

    pad->cd(2);
    gPad->SetLeftMargin(0.15);
    gPad->SetBottomMargin(0.14);
    histo2->SetTitle("");
    histo2->SetLineWidth(2);
    histo2->SetLineColor(kGreen + 2);
    histo2->SetLineColor(kGreen + 2);
    histo2->GetXaxis()->SetTitleSize(0.05);
    histo2->GetXaxis()->SetTitle("Patterns per User");
    histo2->GetXaxis()->SetTitleOffset(1.2);
    histo2->GetYaxis()->SetTitleSize(0.05);
    histo2->GetYaxis()->SetTitle("Users");
    histo2->GetYaxis()->SetTitleOffset(1.3);
    histo2->Draw();

    TPaveText* pave2 = new TPaveText(0.5,0.65,0.8,0.8,"NDC");
    pave2->SetFillColor(0);
    pave2->AddText(("Average Patterns: "+makeString(usage)).c_str());
    pave2->AddText(("Fraction Used: "+makeString(usage/nPatterns)).c_str());
    pave2->Draw();

    string name = "plots/"+inputFiles[nFile]+"_dist.png";
    pad->Print(name.c_str());
  }//closes loop over input files

  //Now pretty up the bar graphs
  TCanvas* canvas = new TCanvas("bar_graphs","bar graphs",14,33,550,1600);
  canvas->SetFillColor(0);
  canvas->SetTitle("Averages");
  canvas->Divide(1,3);

  canvas->cd(1);
  gPad->SetLeftMargin(0.3);
  gPad->SetBottomMargin(0.14);
  gPad->SetGrid();
  histAvg->SetTitle("");
  histAvg->SetLabelSize(0.06);
  histAvg->SetFillColor(kAzure - 3);
  histAvg->SetLineColor(kBlack);
  histAvg->GetXaxis()->SetLabelSize(0.08);
  histAvg->GetYaxis()->SetTitleSize(0.065);
  histAvg->GetYaxis()->SetTitle("Average Projects");
  histAvg->GetYaxis()->SetTitleOffset(1.00);
  histAvg->Draw("hbar2 E1");

  canvas->cd(2);
  gPad->SetLeftMargin(0.3);
  gPad->SetBottomMargin(0.14);
  gPad->SetGrid();
  histPatt->SetTitle("");
  histPatt->SetLabelSize(0.06);
  histPatt->SetLineColor(kGreen + 2);
  histPatt->SetFillColor(kGreen + 2);
  histPatt->GetXaxis()->SetLabelSize(0.08);
  histPatt->GetYaxis()->SetTitleSize(0.065);
  histPatt->GetYaxis()->SetTitle("Average Patterns");
  histPatt->GetYaxis()->SetTitleOffset(1.00);
  histPatt->Draw("hbar2");

  canvas->cd(3);
  gPad->SetLeftMargin(0.3);
  gPad->SetBottomMargin(0.14);
  gPad->SetGrid();
  histUsed->SetTitle("");
  histUsed->SetLabelSize(0.06);
  histUsed->SetFillColor(kGreen + 3);
  histUsed->SetLineColor(kGreen + 3);
  histUsed->GetXaxis()->SetLabelSize(0.08);
  histUsed->GetYaxis()->SetTitleSize(0.065);
  histUsed->GetYaxis()->SetTitle("Fraction Used");
  histUsed->GetYaxis()->SetTitleOffset(1.00);
  histUsed->Draw("hbar2");

  string name = "plots/averages_"+type+".png";
  canvas->Print(name.c_str());

  //close what needs closing
  outfile << "\\hline" << endl;
  outfile << "\\end{tabular}" << endl;
  outfile.close();
}//closes main function

