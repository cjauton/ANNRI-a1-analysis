import numpy as np
import ROOT

numch = 32
file_input = "stage0_output_NaI1.root"
numdet = 14

# title = "^{111}Cd 4.5 eV p-wave";
# E_p = 450;
# G_p = 15;

# title = "^{111}Cd 4.5 eV p-wave";
# E_p = 93;
# G_p = 2;

# title = "^{127}I 7.4 eV p-wave";
# E_p = 747;
# G_p = 20;

# title = "^{127}I 10.35 eV p-wave";
# E_p = 1024;
# G_p = 40;

# title = "^{127}I 13.6 eV p-wave";
# E_p = 1375
# G_p = 30

# title = "^{127}I 22.20 eV p-wave";
# E_p = 2223
# G_p = 32

title = "^{127}I 24.20 eV p-wave"
E_p = 2425
G_p = 32

# title = "^{127}I 24.20 eV p-wave";
# E_p = 2701
# G_p = 32;


hEgam_gate_FA = [6637, 6702]  # 127I
hEgam_gate_FE = [6150, 6194]  # 127I
hEgam_gate_FA_bkg = [6777, 7044]  # 127I

hEn = []
hEn_canvas = []
hEgam_canvas = []
hEgam = []
hEgam_bkg = []
hEn_bkg = []
hEn_bkg_sub = []
scale = []

A_LH_x = []
A_LH_y = []
A_LH_y_err = []


N_L_det = []
N_L = [0.0] * 7

N_H_det = []
N_H = [0.0] * 7

A_LH_det = []
dA_LH_det = []
A_LH = [0.0] * 7
dA_LH = [0.0] * 7

det = [1, 2, 3, 6, 7, 9, 10, 11, 13, 15, 17, 18, 19, 25, 26]  # 127I
# det = [1, 2, 3, 6, 7,9,10,11,13,17,18,19,20,26] #111Cd
det_pos = [
    -1,
    1,
    28,
    3,
    -1,
    7,
    6,
    2,
    -1,
    13,
    10,
    11,
    -1,
    9,
    -1,
    15,
    -1,
    -1,
    18,
    17,
    19,
    20,
    -1,
    -1,
    -1,
    -1,
    26,
    -1,
    -1,
    25,
    -1,
    -1,
    -1,
]
theta_det = [71, 90, 109, 72, 90, 90, 90, 109, 71, 90, 108, 144, 36, 36, 144]  # 127I
theta_pos = [
    -1,
    71,
    90,
    109,
    109,
    90,
    71,
    90,
    -1,
    71,
    90,
    109,
    109,
    90,
    71,
    90,
    -1,
    36,
    72,
    108,
    144,
    -1,
    -1,
    -1,
    -1,
    144,
    108,
    72,
    36,
    -1,
    -1,
    -1,
]
# theta_det = [71, 90, 109, 72, 90,90,90,109,71,108,144,72,36,144] #111Cd
cos_theta_det = [ROOT.TMath.Cos(theta * ROOT.TMath.Pi() / 180) for theta in theta_det]
theta = [36, 71, 72, 90, 108, 109, 144]
cos_theta = [0.809017, 0.325568, 0.309017, 0.0, -0.309017, -0.325568, -0.809017]


def get_det_map(file_name: str) -> list[int]:
    """Takes a string of a root file and returns
    a list containing the detector map"""

    file = ROOT.TFile(file_name)
    det_pos_graph = file.Get("det_pos_graph")
    det = []

    for i in range(det_pos_graph.GetN()):
        det.append(det_pos_graph.Eval(i))

    file.Close()

    return det


def get_det_angle(file_name: str) -> list[int]:
    """Takes a string of a root file and returns
    a list containing the detector map"""

    file = ROOT.TFile(file_name)
    det_pos_graph = file.Get("det_pos_graph")
    det_pos = []
    pos_angle = [
        -1,
        71,
        90,
        109,
        109,
        90,
        71,
        90,
        -1,
        71,
        90,
        109,
        109,
        90,
        71,
        90,
        -1,
        36,
        72,
        108,
        144,
        -1,
        -1,
        -1,
        -1,
        144,
        108,
        72,
        36,
        -1,
        -1,
        -1,]
    det_angle = []

    for i in range(det_pos_graph.GetN()):
        det_pos.append(int(det_pos_graph.Eval(i)))
        # print(type(det_pos_graph.Eval(i)))

    file.Close()

    for i in range(numch):
        det_angle.append(pos_angle[det_pos[i]])

    return det_angle


def get_hist(file_name: str, hist_name: str) -> list[ROOT.TH1]:
    """Takes a string of a root file and a name of a histogram
    and returns a list of histograms"""

    hist = []
    file = ROOT.TFile(file_name)

    for i in range(numch):
        hist.append(file.Get(f"{hist_name}/{hist_name}_d{i}"))
        hist[i].SetDirectory(0)

    file.Close()

    return hist


def calc_scale(hEgam_bkg: list[ROOT.TH1]) -> list[float]:
    """Takes a list of histograms, calculates the scale and
    return the scales as a list"""

    scale = []

    for i in range(numch):
        try:
            num = hEgam_bkg[i].Integral(
                hEgam_bkg[i].GetXaxis().FindBin(hEgam_gate_FA[0]),
                hEgam_bkg[i].GetXaxis().FindBin(hEgam_gate_FA[1]),
            )
            dem = hEgam_bkg[i].Integral(
                hEgam_bkg[i].GetXaxis().FindBin(hEgam_gate_FA_bkg[0]),
                hEgam_bkg[i].GetXaxis().FindBin(hEgam_gate_FA_bkg[1]),
            )
            scale.append(num / dem)
        except ZeroDivisionError:
            scale.append(0)

    return scale


def calc_hEn_sub(hist: list, hist_bkg: list, scale: list[float]) -> list[ROOT.TH1]:
    """Takes 2 lists of histograms and a list of scales and calculates a new
    histogram then returns the histograms as a list"""

    hist_bkg_sub = []
    for i in range(numch):
        hist_bkg_sub.append(hist[i] - hist_bkg[i] * scale[i])
        hist_bkg_sub[i].SetDirectory(0)

    return hist_bkg_sub


def get_A_LH_det(
    hist: list[ROOT.TH1], energy: float, width: float
) -> tuple[list[float], list[float]]:
    """Takes a list of histograms and returns a list of
    A_LH_det and its error dA_LH_det"""

    N_L_det = []
    N_H_det = []
    A_LH_det = []
    dA_LH_det = []

    for i in range(numch):
        energy_bin = hist[i].FindBin(energy)
        width_bin = int(width // hist[i].GetBinWidth(energy_bin))
        N_L_det.append(hist[i].Integral(energy_bin - width_bin, energy_bin - 1))
        N_H_det.append(hist[i].Integral(energy_bin, energy_bin + width_bin))
        try:
            A_LH_det.append(calc_A_LH(N_L_det[i], N_H_det[i]))
            dA_LH_det.append(calc_dA_LH(N_L_det[i], N_H_det[i]))
        except ZeroDivisionError:
            A_LH_det.append(-33)
            dA_LH_det.append(-33)
    return A_LH_det, dA_LH_det


def get_A_LH_angle(
    hist: list[ROOT.TH1], det_angle: list[int], energy: float, width: float
) -> tuple[list[float], list[float]]:
    """Takes a list of histograms and returns a list of A_LH_det
    and its error dA_LH_det"""

    angle_list = [36, 71, 72, 90, 108, 109, 144]
    N_L_angle = [0] * len(angle_list)
    N_H_angle = [0] * len(angle_list)
    A_LH_angle = []
    dA_LH_angle = []

    for i in range(numch):
        energy_bin = hist[i].FindBin(energy)
        width_bin = int(width // hist[i].GetBinWidth(energy_bin))
        N_L = hist[i].Integral(energy_bin - width_bin, energy_bin - 1)
        N_H = hist[i].Integral(energy_bin, energy_bin + width_bin)

        for j in range(len(angle_list)):
            if angle_list[j] == det_angle[i]:
                N_L_angle[j] = N_L_angle[j] + N_L
                N_H_angle[j] = N_H_angle[j] + N_H

    for j in range(len(angle_list)):
        try:
            A_LH_angle.append(calc_A_LH(N_L_angle[j], N_H_angle[j]))
            dA_LH_angle.append(calc_dA_LH(N_L_angle[j], N_H_angle[j]))
        except ZeroDivisionError:
            A_LH_angle.append(-33)
            dA_LH_angle.append(-33)

    return A_LH_angle, dA_LH_angle


def calc_A_LH(N_L: float, N_H: float) -> float:
    """Takes two floats N_L and N_H and returns A_LH"""

    return (N_L - N_H) / (N_L + N_H)


def calc_dA_LH(N_L: float, N_H: float) -> float:
    """Takes two floats N_L and N_H and returns dA_LH"""

    return (
        2
        * ROOT.TMath.Sqrt((N_L * N_L * N_H + N_L * N_H * N_H))
        / (N_L + N_H)
        / (N_L + N_H)
    )


# file_input = ROOT.TFile(file_name)

ROOT.gStyle.SetOptFit(1)

# hEn = get_hist(input_file,"hEn_gated_FA")
# hEn_bkg = get_hist(input_file,"hEn_gated_FA_bkg")
# hEgam = get_hist(input_file,"hEgam")

hist_canvas = []


# def draw_hists(hist: list[ROOT.TH1], energy: float, width: float) -> None:

#     global hist_canvas
#     hist_canvas = []

#     for i in range(len(hist)):

#         hist_canvas.append(ROOT.TCanvas(f"hEn_d{i}", "My Graph", 800, 600))
#         hist[i].GetXaxis().SetRange(energy - 6 * width, energy + 6 * width)
#         hist[i].Draw("E1")
#         hist_canvas[i].Update()


for ch in range(numch):
    hEn.append(file_input.Get(f"hEn_gated_FA/hEn_gated_FA_d{ch}"))
    hEn_bkg.append(file_input.Get(f"hEn_gated_FA_bkg/hEn_gated_FA_bkg_d{ch}"))
    hEgam.append(file_input.Get(f"hEgam/hEgam_d{ch}"))
    hEgam[ch].GetXaxis().SetRangeUser(6500, 7100)

    hEgam_canvas.append(ROOT.TCanvas(f"hEgam_d{ch}", "My Graph", 800, 600))
    hEgam[ch].Draw("E1")
    # hEgam_bkg.append(hEgam[ch].ShowBackground(50,"same"))

    hEgam_canvas[ch].Update()

    try:
        num = hEgam_bkg[ch].Integral(
            hEgam_bkg[ch].GetXaxis().FindBin(hEgam_gate_FA[0]),
            hEgam_bkg[ch].GetXaxis().FindBin(hEgam_gate_FA[1]),
        )
        dem = hEgam_bkg[ch].Integral(
            hEgam_bkg[ch].GetXaxis().FindBin(hEgam_gate_FA_bkg[0]),
            hEgam_bkg[ch].GetXaxis().FindBin(hEgam_gate_FA_bkg[1]),
        )
        scale.append(num / dem)
    except ZeroDivisionError:
        scale.append(0)

    # print(f"det{det[i]} scale = {scale[i]}")

    hEn_bkg_sub.append(hEn[ch] - hEn_bkg[ch] * scale[ch])

    hEn[ch].SetDirectory(0)
    hEgam[ch].SetDirectory(0)
    hEn_bkg[ch].SetDirectory(0)
    hEgam_bkg[ch].SetDirectory(0)

    hEn_canvas.append(ROOT.TCanvas(f"hEn_d{ch}", "My Graph", 800, 600))

    hEn[ch].GetXaxis().SetRange(E_p - 6 * G_p, E_p + 6 * G_p)
    hEn[ch].Draw("E1")
    hEn_bkg_sub[ch].SetLineColor(ROOT.kRed)
    hEn_bkg_sub[ch].Draw("E1 same")

    hEn_canvas[ch].Update()

    N_L_det.append(hEn_bkg_sub[ch].Integral(E_p - G_p, E_p - 1))
    N_H_det.append(hEn_bkg_sub[ch].Integral(E_p, E_p + G_p))
    # print(f"det = {det[i]}, N_H_det = {N_H_det[i]}, N_L_det = {N_L_det[i]}")
    try:
        A_LH_det.append((N_L_det[ch] - N_H_det[ch]) / (N_L_det[ch] + N_H_det[ch]))
        dA_LH_det.append(
            2
            * ROOT.TMath.Sqrt(
                (
                    N_L_det[ch] * N_L_det[ch] * N_H_det[ch]
                    + N_L_det[ch] * N_H_det[ch] * N_H_det[ch]
                )
            )
            / (N_L_det[ch] + N_H_det[ch])
            / (N_L_det[ch] + N_H_det[ch])
        )
    except ZeroDivisionError:
        # continue
        A_LH_det.append(0)
        dA_LH_det.append(0)

    # print(f"det{det[i]}, angle_det = {theta_det[i]},
    # A_LH_det = {A_LH_det[i]}, dA_LH_det = {dA_LH_det[i]}")

    for j in range(len(theta)):
        for k in range(len(det_pos)):
            if ch == det_pos[k]:
                if theta_pos[k] == theta[j]:
                    N_L[j] += N_L_det[ch]
                    N_H[j] += N_H_det[ch]

for j in range(len(theta)):
    try:
        A_LH[j] = (N_L[j] - N_H[j]) / (N_L[j] + N_H[j])
        dA_LH[j] = (
            2
            * ROOT.TMath.Sqrt((N_L[j] * N_L[j] * N_H[j] + N_L[j] * N_H[j] * N_H[j]))
            / (N_L[j] + N_H[j])
            / (N_L[j] + N_H[j])
        )
        A_LH_x.append(cos_theta[j])
        A_LH_y.append(A_LH[j])
        A_LH_y_err.append(dA_LH[j])

    except ZeroDivisionError:
        continue

graph = ROOT.TGraphErrors(
    len(A_LH_x),
    np.array(A_LH_x, dtype=np.double),
    np.array(A_LH_y, dtype=np.double),
    np.zeros_like(np.array(A_LH_x, dtype=np.double)),
    np.array(A_LH_y_err, dtype=np.double),
)
graph.SetMarkerStyle(20)
graph.GetXaxis().SetTitle("cos#theta_{#gamma}")
graph.GetYaxis().SetTitle("A_{LH}")
graph.SetTitle(title)

graph_det = ROOT.TGraphErrors(
    numdet, np.array(cos_theta_det), np.array(A_LH_det), 0, np.array(dA_LH_det)
)
graph_det.SetMarkerStyle(20)
graph_det.SetMarkerColor(ROOT.kBlue)
graph_det.GetXaxis().SetTitle("cos#theta_{#gamma}")
graph_det.GetYaxis().SetTitle("A_{LH}")
graph_det.SetTitle(title)

c1 = ROOT.TCanvas("c1", "My Graph", 800, 600)


fitFunc = ROOT.TF1("fitFunc", "[0]*x + [1]")
graph.Fit(fitFunc, "Q")

ROOT.gStyle.SetOptFit(1)

graph.Draw("AP")


# file_input.Close()

c1.Update()


file_output = ROOT.TFile("A_LH.root", "RECREATE")
file_output.mkdir("hEn_gated_FAFE_bkg_sub/")
file_output.mkdir("hEgam_canvas/")

for i in range(numch):
    file_output.cd("hEn_gated_FAFE_bkg_sub/")
    hEn_bkg_sub[i].Write()

    file_output.cd("hEgam_canvas/")
    hEgam_canvas[i].Write()

file_output.cd()
c1.Write()

file_output.Close()

# canvas = []
# for i in range(len(hEn_sub)):
#     canvas.append(ROOT.TCanvas(f"hEn_d{i}", "My Graph", 800, 600))
#     hEn_sub[i].Draw("E1")
#     canvas[i].Update()

# if __name__=="__main__":

#     input_file = "stage0_output_NaI_1.root"
#     E_p = 13.6
#     G_p = 0.5

#     det_angle = get_det_angle(input_file)

#     hEn = get_hist(input_file,"hEn_gated_FA")
#     hEn_bkg = get_hist(input_file,"hEn_gated_FA_bkg")
#     hEgam = get_hist(input_file,"hEgam")

#     scale = calc_scale(hEn_bkg)

#     hEn_sub = calc_hEn_sub(hEn, hEn_bkg, scale)

#     A_LH_det, dA_LH_det = get_A_LH_det(hEn_sub, E_p, G_p)
#     A_LH_angle, dA_LH_det = get_A_LH_angle(hEn_sub, det_angle, E_p, G_p)
#     print(A_LH_det)
#     print(A_LH_angle)
