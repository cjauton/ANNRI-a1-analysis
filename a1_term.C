#include <iostream>
#include <TCanvas.h>
#include <TF1.h>
#include <TLegend.h>
#include <TMath.h>
#include <Math/SpecFunc.h>
#include <Rtypes.h>

///////////////////////////////////////////////////////////////////////////////////////

#ifndef numpres 
#define numpres 4 // number of p-wave resonancnes
#endif

#ifndef numsres
#define numsres 4 // number of s-wave resonances
#endif

///////////////////////////////////////////////////////////////////////////////////////

double mn = 939.56542052e6; // neutron mass MeV/c^2
double hbarc = 1.973e-7; // hbarc in eV

double F = 0.; // Final state spin

///////////////////////////////////////////////////////////////////////////////////////

// double I = 5/2.; // 127I

// double Ep [] = {7.55,10.35,13.95,24.63}; // 127I 
// double Jp [] = {1.,1.,2.,1.};
// double Gpn [] = {4.8e-7,1.2e-5,4.8e-6,2.56e-6};
// double Gpg [] = {1.00e-1,9.00e-2,9.92e-2,9.57e-2};

// double Es [] = {-54.188,-39.25,20.38,31.21}; // 127I
// double Js [] = {2.,3.,2.,3.};
// double Gsn [] = {1.16e-1,1.12e-1,1.7e-3,1.714e-2};
// double Gsg [] = {9.98e-1,9.83e-2,9.57e-2,9.465e-2};


// double I = 1/2.; // 111Cd

// double Ep [] = {4.53,6.94}; // 111Cd
// double Jp [] = {1.,2.};
// double Gpn [] = {1.4e-6,8.6e-7};
// double Gpg [] = {1.63e-1,1.43e-1};

// double Es [] = {-4,27.5,69.4}; // 111Cd
// double Js [] = {1.,1.,0.};
// double Gsn [] = {1.0e-3,4.5e-3,4.3e-4};
// double Gsg [] = {6.8e-2,9.6e-2,1.02e-1};


double I = 1/2.; // 113Cd

double Ep [] = {7.0,2.1831e1,4.338e1,4.977e1}; // 113Cd
double Jp [] = {1.,2.,1.,1.};
double Gpn [] = {4.13333e-7,5.68e-6,6.26667e-6,2.0e-5};
double Gpg [] = {1.6e-1,8.20e-2,1.28e-1,1.6e-1};

double Es [] = {0.1787,18.365,63.7,84.91}; // 113Cd
double Js [] = {1.,1.,1.,1.};
double Gsn [] = {6.4e-4,1.88e-4,3.46667e-3,2.98667e-2};
double Gsg [] = {1.135e-1,1.0e-1,1.0e-1,1.0e-1};

///////////////////////////////////////////////////////////////////////////////////////

TCanvas *c1[numpres];
TF1 *a0_fn[numpres];
TF1 *a1x_fn[numpres];
TF1 *a1y_fn[numpres];
TF1 *a10_ratio_fn[numpres];

///////////////////////////////////////////////////////////////////////////////////////

double P(double j1, double j2, double j3, double j4, double j5, double j6, double j7) {
    int two_j1 = static_cast<int>(2*j1);
    int two_j2 = static_cast<int>(2*j2);
    int two_j3 = static_cast<int>(2*j3);
    int two_j4 = static_cast<int>(2*j4);
    int two_j5 = static_cast<int>(2*j5);
    int two_j6 = static_cast<int>(2*j6);
    int two_j7 = static_cast<int>(2*j7);

    double a = TMath::Power(-1,j1+j2+j4+j6+j7);
    double b = TMath::Sqrt((2*j1+1)*(2*j2+1)*(2*j3+1)*(2*j4+1));
    double c = ROOT::Math::wigner_6j(two_j5,two_j3,two_j4,two_j6,two_j2,two_j1);
    double d = ROOT::Math::wigner_6j(two_j5,2*1,2*1,two_j7,two_j1,two_j2);

    return a*3/2*b*c*d;
}

///////////////////////////////////////////////////////////////////////////////////////

double a0(double *x, double *pars) {
    double Ep  = pars[0]; 
    double Jp  = pars[1];
    double Gpn = pars[2];
    double Gpg = pars[3];
    double Gp  = Gpn+Gpg;
    double kp = sqrt(2*mn*Ep)/hbarc;
    double gp = (2*Jp+1)/2/(2*I+1);

    double a0p = 1/(kp*kp)*TMath::Sqrt(x[0]/Ep)*gp*Gpn*Gpg/4/((x[0]-Ep)*(x[0]-Ep)+Gp*Gp/4);
    double a0s = 0;

    for (int i=0;i<numsres;i++) {
        double Gs  = Gsn[i]+Gsg[i];
        double ks = sqrt(2*mn*TMath::Abs(Es[i]))/hbarc;
        double gs = (2*Js[i]+1)/2/(2*I+1);
        
        a0s = a0s+ 1/(ks*ks)*TMath::Sqrt(TMath::Abs(Es[i])/x[0])*gs*Gsn[i]*Gsg[i]/4/((x[0]-Es[i])*(x[0]-Es[i])+Gs*Gs/4);
    }

    return 1e28*2*TMath::Pi()*(a0s+a0p);
}

///////////////////////////////////////////////////////////////////////////////////////

double a1x(double *x, double *pars) {
    double Ep  = pars[0]; 
    double Jp  = pars[1];
    double Gpn = pars[2];
    double Gpg = pars[3];
    double Gp  = Gpn+Gpg;
    double kp = sqrt(2*mn*Ep)/hbarc;
    double gp = (2*Jp+1)/2/(2*I+1);

    double a1x = 0;

    
    for (int i=0;i<numsres;i++) {
        double Gs  = Gsn[i]+Gsg[i];
        double ks = sqrt(2*mn*TMath::Abs(Es[i]))/hbarc;
        double gs = (2*Js[i]+1)/2/(2*I+1);

        double num = TMath::Power(TMath::Abs(Es[i])/Ep,1/4)*TMath::Sqrt(gs*gp*Gsn[i]*Gsg[i]*Gpn*Gpg)*((x[0]-Es[i])*(x[0]-Ep)+Gs*Gp/4);
        double den = 2*ks*kp*((x[0]-Es[i])*(x[0]-Es[i])+Gs*Gs/4)*((x[0]-Ep)*(x[0]-Ep)+Gp*Gp/4);

        a1x = a1x + num/den*P(Js[i],Jp,1/2.,1/2.,1.,I,F);
    }
   
    return 1e28*2*TMath::Pi()*a1x;
}

///////////////////////////////////////////////////////////////////////////////////////

double a1y(double *x, double *pars) {
    double Ep  = pars[0]; 
    double Jp  = pars[1];
    double Gpn = pars[2];
    double Gpg = pars[3];
    double Gp  = Gpn+Gpg;
    double kp = sqrt(2*mn*Ep)/hbarc;
    double gp = (2*Jp+1)/2/(2*I+1);

    double a1y = 0;
    
    for (int i=0;i<numsres;i++) {
        double Gs  = Gsn[i]+Gsg[i];
        double ks = sqrt(2*mn*TMath::Abs(Es[i]))/hbarc;
        double gs = (2*Js[i]+1)/2/(2*I+1);

        double num = TMath::Power(TMath::Abs(Es[i])/Ep,1/4)*TMath::Sqrt(gs*gp*Gsn[i]*Gsg[i]*Gpn*Gpg)*((x[0]-Es[i])*(x[0]-Ep)+Gs*Gp/4);
        double den = 2*ks*kp*((x[0]-Es[i])*(x[0]-Es[i])+Gs*Gs/4)*((x[0]-Ep)*(x[0]-Ep)+Gp*Gp/4);

        a1y = a1y + num/den*P(Js[i],Jp,1/2.,3/2.,1.,I,F);
    }
   
    return 1e28*2*TMath::Pi()*a1y;
}

///////////////////////////////////////////////////////////////////////////////////////

double a10_ratio(double *x, double *pars) {
    double Ep  = pars[0]; 
    double Jp  = pars[1];
    double Gpn = pars[2];
    double Gpg = pars[3];
    double Gp  = Gpn+Gpg;
    double kp = sqrt(2*mn*Ep)/hbarc;
    double gp = (2*Jp+1)/2/(2*I+1);

    double a10_ratio = 0;
    
    for (int i=0;i<numsres;i++) {
        if (Jp==Js[i]){
        double Gs  = Gsn[i]+Gsg[i];
        double ks = sqrt(2*mn*TMath::Abs(Es[i]))/hbarc;
        double gs = (2*Js[i]+1)/2/(2*I+1);

        double num = -2*TMath::Sqrt(Gsn[i]/Gpn)*((x[0]-Es[i])+Gsg[i]/Gpg*(x[i]-Ep));
        double den = ((x[0]-Ep)*(x[0]-Ep)+Gp*Gp/4);

        a10_ratio = a10_ratio + num/den;
        }
    }
   
    return a10_ratio;
}

///////////////////////////////////////////////////////////////////////////////////////

void a1_term() {

    TCanvas* canvas = new TCanvas("canvas", "Canvas", 800, 600);
    canvas->Divide(2, 2); // Divide into 2x2 sub-pads

    for(int i=0;i<numpres;i++){

        canvas->cd(i+1);

        std::cout << "Drawing Resonance #" << i+1 << std::endl;
        // std::cout << "P(1,2,1/2,1/2,5/2,2) = " << P(2.,1.,1/2.,1/2.,1.,5/2.,2.) << std::endl;
        // std::cout << "P(1,2,1/2,1/2,5/2,2) = " << P(2.,1.,1/2.,3/2.,1.,5/2.,2.) << std::endl;

        // c1[i] = new TCanvas(Form("res%d",i), "a1 term", 800, 600);
        // c1[i]->SetGrid();
        // c1[i]->SetLeftMargin(0.12);

        a0_fn[i] = new TF1(Form("%.2f eV p-wave, F=%.f;Neutron Energy [eV];Cross Section [Barns]",Ep[i],F), a0, Ep[i]-10*Gpg[i], Ep[i]+10*Gpg[i],4);
        a0_fn[i]->SetParameters(Ep[i],Jp[i],Gpn[i],Gpg[i]);
        a0_fn[i]->SetLineColor(kBlack);
        a0_fn[i]->SetNpx(3000);
        a0_fn[i]->SetLineWidth(4);
        a0_fn[i]->Draw();
        


        double min = a0_fn[i]->Eval(Ep[i]);
        min = -1*min/4;
        a0_fn[i]->SetMinimum(min);

        a1x_fn[i] = new TF1("a1x term", a1x, Ep[i]-10*Gpg[i], Ep[i]+10*Gpg[i],4);
        a1x_fn[i]->SetParameters(Ep[i],Jp[i],Gpn[i],Gpg[i]);
        a1x_fn[i]->SetLineColor(kRed);
        a1x_fn[i]->SetLineStyle(kDashDotted);
        a1x_fn[i]->SetNpx(3000);
        a1x_fn[i]->SetLineWidth(4);
        a1x_fn[i]->Draw("SAME");
        
        a1y_fn[i] = new TF1("a1y term", a1y, Ep[i]-10*Gpg[i], Ep[i]+10*Gpg[i],4);
        a1y_fn[i]->SetParameters(Ep[i],Jp[i],Gpn[i],Gpg[i]);
        a1y_fn[i]->SetLineColor(kBlue);
        a1y_fn[i]->SetLineStyle(kDashDotted);
        a1y_fn[i]->SetNpx(3000);
        a1y_fn[i]->SetLineWidth(4);
        a1y_fn[i]->Draw("SAME");

        // a10_ratio_fn[i] = new TF1("a10/a0p term", a10_ratio, Ep[i]-10*Gpg[i], Ep[i]+10*Gpg[i],4);
        // a10_ratio_fn[i]->SetParameters(Ep[i],Jp[i],Gpn[i],Gpg[i]);
        // a10_ratio_fn[i]->SetLineColor(kGreen);
        // a10_ratio_fn[i]->SetLineStyle(kDashDotted);
        // a10_ratio_fn[i]->SetNpx(3000);
        // a10_ratio_fn[i]->SetLineWidth(4);
        // a10_ratio_fn[i]->Draw("SAME");

        // Add a legend
        TLegend *legend = new TLegend(0.7, 0.7, 0.9, 0.9);
        legend->AddEntry(a0_fn[i], "a0", "l");
        legend->AddEntry(a1x_fn[i], "a1x", "l");
        legend->AddEntry(a1y_fn[i], "a1y", "l");
        legend->Draw();

    }
}
