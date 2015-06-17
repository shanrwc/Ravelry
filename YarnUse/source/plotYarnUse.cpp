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
#include "TGraph.h"
#include "TGraphErrors.h"
#include "TMultiGraph.h"
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

// int countPatterns(string all_patterns)
// {
//   set<string> patts;
//   while (all_patterns.length() > 0)
//   {
//     if (all_patterns.find("-") != string::npos)
//     {
//       patts.insert(all_patterns.substr(0,all_patterns.find(":")));
//       all_patterns = all_patterns.substr(all_patterns.find("-")+1,string::npos);
//     }
//     else
//     {
//       patts.insert(all_patterns);
//       all_patterns = "";
//     }
//   }
//   return((int)patts.size());
// }

// vector<string> getMags(string title)
// {
//   vector<string> seasons;
//   vector<string> years;
//   vector<string> times;
//   if (title.compare("interweave-knits") == 0)
//   {
//     seasons.push_back("spring");
//     seasons.push_back("summer");
//     seasons.push_back("fall");
//     seasons.push_back("winter");

//     years.push_back("2005");
//     years.push_back("2006");
//     // years.push_back("2007");
//     // years.push_back("2008");
//     // years.push_back("2009");
//     // years.push_back("2010");
//     // years.push_back("2011");
//     // years.push_back("2012");
//   }

//   for (int i = 0; i != (int)years.size(); ++i)
//   {
//     for (int j = 0; j != (int)seasons.size(); ++j)
//     {
//       times.push_back(title+"-"+seasons[j]+"-"+years[i]);
//     }
//   }

//   return(times);
// }

//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////

void plotYarnUse()
{
  gStyle->SetOptStat(0);
  //  gStyle->SetPalette(1);

  //Make list of patterns to analyze
  vector<string> patterns;
  //  patterns.push_back("sheltand-border-shawl");
  patterns.push_back("elizabeth-shawl-3");


  //For each, read in data from file and fill histogram(s)
  for (int nPat = 0; nPat != (int)patterns.size(); ++nPat)
  {
    //Declare histogram(s)
    TH1D* unw = 0;
    TH1D* yw = 0;//new TH1D((patterns[nPat]+"_yweighted").c_str(),(patterns[nPat]+"_yweighted").c_str(),100,0,1000);

    //Open text file
    ifstream infile (("data/"+patterns[nPat]+"_yarnusage.txt").c_str());
    string line;

    string name;
    string yarnW;
    double minyardage; 
    double maxyardage;
    double minused = 0;
    double maxused = 0;

    if (infile.is_open())
    {
      while (infile.good())
      {
	getline(infile,line);
	vector<string> pieces = splitString(line);

	if ((int)pieces.size() < 2) continue;

	if (line.find("NAME: ") != string::npos) name = pieces[1];
	else if (line.find("WEIGHT: ") != string::npos) yarnW = line.substr(8,line.length());
	else if (line.find("MIN_YARDAGE: ") != string::npos) minyardage = makeDouble(pieces[1]);
	else if (line.find("MAX_YARDAGE: ") != string::npos) maxyardage = makeDouble(pieces[1]);
	else if (line.find("MINIMUM: ") != string::npos) minused = makeDouble(pieces[1]);
	else if (line.find("MAXIMUM: ") != string::npos) maxused = makeDouble(pieces[1]); 

	if (minused != 0 && maxused != 0 && unw == 0 && yw == 0)
	{
	  double nbins = int((maxused - minused)/50) + 1;
	  unw = new TH1D((patterns[nPat]+"_unweighted").c_str(),(patterns[nPat]+"_unweighted").c_str(),nbins,int(minused/10)*10,int(maxused/10)*10+10);
	  yw = new TH1D((patterns[nPat]+"_yarnweight").c_str(),(patterns[nPat]+"_yarnweight").c_str(),nbins,int(minused/10)*10,int(maxused/10)*10+10);
	}

	if (line.find("ENTRY: ") != string::npos && unw != 0)
	{
	  //	  cout << pieces[1] << endl;
	  unw->Fill(makeDouble(pieces[1]));
	  yw->Fill(makeDouble(pieces[1]),makeDouble(pieces[2]));
	}	
      }//closes while-loop over file's goodness
    }//closes if-statement over file's openness

    //Make pretty plots
    TCanvas* pad = new TCanvas((patterns[nPat]+"_plots").c_str(),(patterns[nPat]+"_plots").c_str(),14,33,600,600);
    pad->SetFillColor(0);
    pad->SetTitle((patterns[nPat]+"_plots").c_str());
    //    pad->Divide(2,2);
    pad->SetBottomMargin(0.14);
    pad->SetLeftMargin(0.2);

    unw->SetTitle("");
    unw->SetLineWidth(3);
    unw->SetLineColor(kAzure-3);
    unw->GetXaxis()->SetTitleSize(0.05);
    unw->GetXaxis()->SetTitleOffset(1.2);
    unw->GetXaxis()->SetTitle("Yarn Used [m]");
    unw->GetYaxis()->SetTitleSize(0.05);
    unw->GetYaxis()->SetTitleOffset(1.35);
    unw->GetYaxis()->SetTitle("Projects");
    unw->Draw();

    TLine* line1 = new TLine(minyardage,0,minyardage,0.75*unw->GetMaximum());
    line1->SetLineWidth(2);
    line1->SetLineColor(kRed+1);
    line1->Draw();

    TLine* line2 = new TLine(maxyardage,0,maxyardage,0.75*unw->GetMaximum());
    line2->SetLineWidth(2);
    line2->SetLineColor(kRed+1);
    line2->Draw();

    TPaveText* text = new TPaveText(0.2,0.92,0.8,0.98,"NDC");
    text->SetFillColor(0);
    text->SetBorderSize(0);
    text->AddText("Unweighted");
    text->Draw();
  }//closes for-loop over patterns




  // //Set up tmultigraphs and tlegends
  // TMultiGraph* Gtotal = new TMultiGraph();
  // TMultiGraph* Gprojs = new TMultiGraph();
  // TMultiGraph* Gpatts = new TMultiGraph();
  // TMultiGraph* Gusers = new TMultiGraph();

  // TLegend* Ltotal = new TLegend(0.7,0.75,0.9,0.9);
  // TLegend* Lprojs = new TLegend(0.7,0.75,0.9,0.9);
  // TLegend* Lpatts = new TLegend(0.7,0.75,0.9,0.9);
  // TLegend* Lusers = new TLegend(0.7,0.75,0.9,0.9);

  // for (int nMag = 0; nMag != (int)inputMags.size(); ++nMag)
  // {
  //   vector<string> inputs = getMags(inputMags[nMag]);

  //   int vsize = (int)inputs.size();
  //   double xs [vsize] ;
  //   double tprojs [vsize];
  //   double nprojs [vsize];
  //   double npatts [vsize];
  //   double users [vsize];

  //   vector<double> coords = getXCoords(inputs);
  //   for (int i = 0; i != (int)coords.size(); ++i)
  //   {
  //     xs[i] = coords[i];
  //   }

  //   for (int nIss = 0; nIss != (int)inputs.size(); ++nIss)
  //   {
  //     //set ints to store some numbers
  //     int nPatterns = 0;
  //     int nProjects = 0;
  //     int nUsers = 0;
  //     int nUniqueUses = 0;
      
  //     ifstream infile (("../data/"+inputs[nIss]+"_RAW.txt").c_str());
  //     string line;
      
  //     if (infile.is_open())
  //     {
  // 	while (infile.good())
  // 	{
  // 	  getline(infile,line);
	  
  // 	  vector<string> pieces = splitString(line);
  // 	  if ((int)pieces.size() < 2) continue;
	  
  // 	  if (pieces[0].find("NPATTERNS:") != string::npos)
  // 	  {
  // 	    nPatterns = int(makeDouble(pieces[1]));
  // 	  }
  // 	  else if (pieces[0].find("NPROJECTS:") != string::npos)
  // 	  {
  // 	    nProjects = int(makeDouble(pieces[1]));
  // 	  }
  // 	  else if (pieces[0].compare("NUSERS:") == 0)
  // 	  {
  // 	    nUsers = int(makeDouble(pieces[1]));
  // 	  }
  // 	  else if (pieces[0].compare("COUNT:") == 0)
  // 	  {
  // 	    double temp = countPatterns(pieces[2]);
  // 	    nUniqueUses += temp;
  // 	  }
	  
  // 	}//closes while loop over infile's goodness
  //     }//closes if-statement over infile's openness

  //     //Check that you have the inputs you need
  //     if (nPatterns == 0 || nProjects == 0 || nUsers == 0 )
  //     {
  // 	cout << "Input file " << inputs[nIss] << " doesn't have full information!" << endl;
  // 	cout << nPatterns << " " << nProjects << " " << nUsers << endl;
  // 	return;
  //     }

  //     //Calculate averages
  //     double avgProjs = double(nProjects)/nUsers;
  //     double avgPatts = double(nUniqueUses)/nUsers;
  //     double usage = avgPatts/nPatterns;

  //     //Fill arrays
  //     tprojs[nIss] = nProjects;
  //     nprojs[nIss] = avgProjs;
  //     npatts[nIss] = avgPatts;
  //     users[nIss] = nUsers;

  //     //Write stuff to table
  //     outfile << convertTitle(inputs[nIss]) << " & " << nProjects << "&" << avgProjs << " & " << avgPatts << " & " << usage <<"\\\\" << endl;
  //   }//closes loop over magazine issues

  //   //Now make graphs and add to TMultigraphs and TLegends
  //   TGraph* gtotal = new TGraph(vsize,xs,tprojs);
  //   gtotal->SetTitle("");
  //   gtotal->SetMarkerStyle(markers[nMag]);
  //   gtotal->SetMarkerColor(colors[nMag]);
  //   gtotal->SetLineColor(colors[nMag]);
  //   Gtotal->Add(gtotal);
  //   Ltotal->AddEntry(gtotal,convertTitle(inputMags[nMag]).c_str(),"p");

  //   TGraph* gprojs = new TGraph(vsize,xs,nprojs);
  //   gprojs->SetTitle("");
  //   gprojs->SetMarkerStyle(markers[nMag]);
  //   gprojs->SetMarkerColor(colors[nMag]);
  //   gprojs->SetLineColor(colors[nMag]);
  //   Gprojs->Add(gprojs);
  //   Lprojs->AddEntry(gprojs,convertTitle(inputMags[nMag]).c_str(),"p");

  //   TGraph* gpatts = new TGraph(vsize,xs,npatts);
  //   gpatts->SetTitle("");
  //   gpatts->SetMarkerStyle(markers[nMag]);
  //   gpatts->SetMarkerColor(colors[nMag]);
  //   gpatts->SetLineColor(colors[nMag]);
  //   Gpatts->Add(gpatts);
  //   Lpatts->AddEntry(gpatts,convertTitle(inputMags[nMag]).c_str(),"p");

  //   TGraph* gusers = new TGraph(vsize,xs,users);
  //   gusers->SetTitle("");
  //   gusers->SetMarkerStyle(markers[nMag]);
  //   gusers->SetMarkerColor(colors[nMag]);
  //   gusers->SetLineColor(colors[nMag]);
  //   Gusers->Add(gusers);
  //   Lusers->AddEntry(gusers,convertTitle(inputMags[nMag]).c_str(),"p");

  // }//closes loop over input magazines

  // //Pretty up those tmultigraphs
  // TCanvas* pad = new TCanvas("maguse_graphs","Graphs of Magazine use",14,33,1200,1200);
  // pad->SetFillColor(0);
  // pad->SetTitle("Magazine use");
  // pad->Divide(2,2);

  // TLine* line1 = new TLine(29,0,29,11000);
  // line1->SetLineWidth(2);

  // pad->cd(1);
  // gPad->SetLeftMargin(0.15);
  // gPad->SetBottomMargin(0.14);
  // Gtotal->Draw("apl");
  // Gtotal->GetXaxis()->SetTitleSize(0.05);
  // Gtotal->GetXaxis()->SetTitle("Time [months since Jan. 2005]");
  // Gtotal->GetXaxis()->SetTitleOffset(1.2);
  // Gtotal->GetYaxis()->SetTitleSize(0.06);
  // Gtotal->GetYaxis()->SetTitle("Total Projects");
  // Gtotal->GetYaxis()->SetTitleOffset(1.0);
  // Ltotal->Draw();
  // line1->Draw();

  // TLine* line2 = new TLine(29,1.05,29,1.3);
  // line2->SetLineWidth(2);  
  // pad->cd(2);
  // gPad->SetLeftMargin(0.15);
  // gPad->SetBottomMargin(0.14);
  // Gprojs->Draw("apl");
  // Gprojs->GetXaxis()->SetTitleSize(0.05);
  // Gprojs->GetXaxis()->SetTitle("Time [months since Jan. 2005]");
  // Gprojs->GetXaxis()->SetTitleOffset(1.2);
  // Gprojs->GetYaxis()->SetTitleSize(0.06);
  // Gprojs->GetYaxis()->SetTitle("Average Projects");
  // Gprojs->GetYaxis()->SetTitleOffset(1.0);
  // Lprojs->Draw();
  // line2->Draw();

  // TLine* line3 = new TLine(29,1.02,29,1.15);
  // line3->SetLineWidth(2);  
  // pad->cd(3);
  // gPad->SetLeftMargin(0.15);
  // gPad->SetBottomMargin(0.14);
  // Gpatts->Draw("apl");
  // Gpatts->GetXaxis()->SetTitleSize(0.05);
  // Gpatts->GetXaxis()->SetTitle("Time [months since Jan. 2005]");
  // Gpatts->GetXaxis()->SetTitleOffset(1.2);
  // Gpatts->GetYaxis()->SetTitleSize(0.06);
  // Gpatts->GetYaxis()->SetTitle("Average Patterns");
  // Gpatts->GetYaxis()->SetTitleOffset(1.0);
  // Lpatts->Draw();
  // line3->Draw();

  // TLine* line4 = new TLine(29,0.02,29,0.055);
  // line4->SetLineWidth(2);  
  // pad->cd(4);
  // gPad->SetLeftMargin(0.15);
  // gPad->SetBottomMargin(0.14);
  // Gusers->Draw("apl");
  // Gusers->GetXaxis()->SetTitleSize(0.05);
  // Gusers->GetXaxis()->SetTitle("Time [months since Jan. 2005]");
  // Gusers->GetXaxis()->SetTitleOffset(1.2);
  // Gusers->GetYaxis()->SetTitleSize(0.06);
  // Gusers->GetYaxis()->SetTitle("Total Users");
  // Gusers->GetYaxis()->SetTitleOffset(1.0);
  // Lusers->Draw();
  // line4->Draw();

  // string name = "plots/magazine_use_graphs_4.png";
  // pad->Print(name.c_str());

  // //close what needs closing
  // outfile << "\\hline" << endl;
  // outfile << "\\end{tabular}" << endl;
  // outfile.close();
}//closes main function

