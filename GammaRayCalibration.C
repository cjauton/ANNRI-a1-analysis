#include <iostream>
#include <vector>
#include <algorithm>
#include "TH1F.h"
#include "TF1.h"
#include "TSpectrum.h"
#include "TCanvas.h"

void GammaRayCalibration(const std::vector<double>& gammaEnergies, TH1F* histogram) {
    // Find peaks using TSpectrum with initial estimates
    TSpectrum spectrum;
    const int numPeaks = gammaEnergies.size();
    const double resolution = 2.0;  // Resolution parameter for peak finding
    const double threshold = 0.05;  // Threshold parameter for peak finding

    std::vector<double> initialEstimates(gammaEnergies);
    std::sort(initialEstimates.begin(), initialEstimates.end());

    std::vector<int> peakIndices;
    std::vector<double> peakPositions;

    const int numBins = histogram->GetNbinsX();

    for (int i = 0; i < numPeaks; ++i) {
        double initialPosition = initialEstimates[i];
        int binIndex = histogram->GetXaxis()->FindBin(initialPosition);

        // Search for peak in the full range
        double position;
        double height;
        spectrum.Search(histogram, resolution, "nobackground", threshold, false, 3, false, position, height);

        peakIndices.push_back(binIndex);
        peakPositions.push_back(position);
    }

    // Sort peak positions and indices based on positions
    std::vector<int> sortedIndices(numPeaks);
    std::iota(sortedIndices.begin(), sortedIndices.end(), 0);
    std::sort(sortedIndices.begin(), sortedIndices.end(), [&peakPositions](int i, int j) {
        return peakPositions[i] < peakPositions[j];
    });

    std::vector<int> sortedPeakIndices(numPeaks);
    std::transform(sortedIndices.begin(), sortedIndices.end(), sortedPeakIndices.begin(), [&peakIndices](int index) {
        return peakIndices[index];
    });

    // Get the positions of the found peaks
    std::vector<double> pulseHeights(numPeaks);
    for (int i = 0; i < numPeaks; ++i) {
        pulseHeights[i] = histogram->GetBinCenter(sortedPeakIndices[i]);
    }

    // Perform linear fit
    TF1* linearFit = new TF1("linearFit", "[0] + [1]*x", 0, numBins);
    TGraph* graph = new TGraph(numPeaks);
    for (int i = 0; i < numPeaks; ++i) {
        graph->SetPoint(i, pulseHeights[i], gammaEnergies[sortedIndices[i]]);
    }
    graph->Fit(linearFit, "Q");

    // Create new histogram in terms of gamma energy vs. counts
    double minBinCenter = linearFit->Eval(0);
    double maxBinCenter = linearFit->Eval(numBins);
    TH1F* energyHistogram = new TH1F("energyHistogram", "Gamma Energy vs. Counts", numBins, minBinCenter, maxBinCenter);

    for (int i = 1; i <= numBins; ++i) {
        double pulseHeight = histogram->GetBinCenter(i);
        double gammaEnergy = linearFit->Eval(pulseHeight);
        double counts = histogram->GetBinContent(i);
        energyHistogram
