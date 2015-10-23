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

#include "TSQLServer.h"
#include "TSQLResult.h"
#include "TSQLRow.h"

using namespace std;

/////////////////////////////////////////////////////////////////////////////

template<typename T>
std::string makeString(T const& value)
{
  std::stringstream sstr;
  sstr << fixed;
  sstr << setprecision(2);
  sstr << value;
  return sstr.str();
}

double makeDouble(string input)
{
  istringstream stm;
  stm.str(input);
  double num;
  stm >> num;

  return(num);
}

///////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

void plotProjTimes(string passwd)
{
  gStyle->SetOptStat(0);

  //establish connection with database
  TSQLServer *db = TSQLServer::Connect("mysql://localhost/Ravelry_Projects","root",passwd.c_str());
  TSQLRow *row;
  TSQLResult *result;

  //set up map of maps to loop over
  map < string, map< string, string> > project_types;
  map<string, string> all_hats;
  all_hats.insert(pair<string,string>("Tweed Beret","2005-11-15"));
  all_hats.insert(pair<string,string>("Sweet Honey Beret","2007-11-20"));
  all_hats.insert(pair<string,string>("Nantes Hat","2010-11-15"));
  project_types.insert(pair<string,map<string,string> >("Hats",all_hats));

  map<string,string> all_socks;
  all_socks.insert(pair<string,string>("Cable Rib Socks","2005-02-21"));
  all_socks.insert(pair<string,string>("Knotty or Knice Socks","2008-08-18"));
  all_socks.insert(pair<string,string>("Border Socks","2011-08-15"));
  project_types.insert(pair<string,map<string,string> >("Socks",all_socks));

  map<string,string> all_shawls;
  all_shawls.insert(pair<string,string>("Icarus Shawl","2006-05-15"));
  all_shawls.insert(pair<string,string>("Fountain Pen Shawl","2009-05-18"));
  all_shawls.insert(pair<string,string>("Rose Lace Stole","2011-05-16"));
  project_types.insert(pair<string,map<string,string> >("Shawls",all_shawls));

  //Now, start looping
  map<string, map<string,string> >::iterator iter;
  for (iter = project_types.begin(); iter != project_types.end(); ++iter)
  {
    //Set up TCanvas for results
    string label = iter->first;
    map<string,string> patterns = iter->second;

    TCanvas* canvas = new TCanvas((label+"_timedist").c_str(),(label+"timedist").c_str(),14,33,600,600);
    canvas->SetFillColor(0);
    canvas->SetTitle(label.c_str());
    canvas->SetLeftMargin(0.15);
    canvas->SetBottomMargin(0.14);

    TLegend* leg = new TLegend(0.45,0.65,0.9,0.9);
    leg->SetFillColor(0);
    leg->SetTextSize(0.025);

    //Now loop over individual patterns
    map<string,string>::iterator it;
    int counter = 0;
    for (it = patterns.begin(); it != patterns.end(); ++it)
    {
      //Set up histogram
      string label2 = label + "_"+makeString(counter);
      TH1D* hist = new TH1D(label2.c_str(),label2.c_str(),10,0,4000);
      hist->SetTitle("");
      hist->SetLineWidth(2);
      hist->SetLineColor(counter+2);
      hist->GetXaxis()->SetTitleSize(0.05);
      hist->GetXaxis()->SetTitle("Days since Publication");
      hist->GetXaxis()->SetTitleOffset(1.2);
      hist->GetYaxis()->SetTitleSize(0.06);
      hist->GetYaxis()->SetTitle("Projects Started");
      hist->GetYaxis()->SetTitleOffset(1.0);
      if (label.find("Hats") != string::npos) hist->GetYaxis()->SetRangeUser(0,100);
      if (label.find("Socks") != string::npos) hist->GetYaxis()->SetRangeUser(0,200);
      if (label.find("Shawls") != string::npos) hist->GetYaxis()->SetRangeUser(0,500);

      //Fill histogram with your data
      string sql = "SELECT DATEDIFF(projects.start_date,'"+it->second+"') FROM projects,patterns WHERE start_date IS NOT NULL AND projects.pattern_id = patterns.id AND patterns.name = '"+it->first+"'";
      //      cout << sql << endl;
      result = db->Query(sql.c_str());
      if (result == 0) continue;

      int nRows = result->GetRowCount();
      int nFields = result->GetFieldCount();

      for (int i = 0; i != nRows; ++i)
      {
	row = result->Next();
	for (int j = 0; j != nFields; ++j)
	{
	  hist->Fill(makeDouble(row->GetField(j)));
	}
      }//closes for-loop over rows

      if (counter == 0) 
      {
	hist->Draw("E1");
      }
      else
      {
	hist->Draw("E1 same");
      }

      leg->AddEntry(hist,(it->first+" "+it->second).c_str(),"f");

      counter++;
    }//closes loop over patterns map

    //Pretty up and print out the TCanvas
    leg->Draw();

    TLatex* tex = new TLatex();
    tex->SetTextSize(0.05);
    tex->SetNDC();
    tex->DrawLatex(0.42,0.91,(label).c_str());

    string name = "data/"+label + "_timedist.eps";
    canvas->Print(name.c_str());

  }//closes loop over project_types map
}//closes main function
