# Physics Analysis Project

This Python project aims to perform physics analysis using a multi-stage approach. The analysis is divided into three stages: `stage0_analysis.py`, `stage1_analysis.py`, and `stage2_analysis.py`. Each stage has a specific purpose and contributes to the final result.

## Requirements
- Python 3.x
- ROOT (CERN) library (for handling TTRee and histograms)

## Stage 0: Calibration and Cuts (`stage0_analysis.py`)
This stage focuses on calibration and data selection. It processes the ROOT TTRee data, applies calibrations, and performs necessary cuts. The output of this stage is transformed into histograms for further analysis.

To run stage 0 analysis, execute the following command:

```bash
python stage0_analysis.py
```

## Stage 1: Physics Analysis (`stage1_analysis.py`)
Stage 1 is dedicated to the actual physics analysis. It takes the calibrated and cut histograms from stage 0 and applies specific algorithms and calculations to extract meaningful physics quantities. This stage may involve fitting, modeling, or other techniques to obtain the desired results.

To run stage 1 analysis, execute the following command:

```bash
python stage1_analysis.py
```

## Stage 2: Statistical Analysis and Final Result (`stage2_analysis.py`)
The focus of stage 2 is statistical analysis and the production of the final result. It takes the outputs from stage 1 and performs statistical tests, error analysis, or any other relevant statistical techniques. The final result of the analysis is produced in this stage.

To run stage 2 analysis, execute the following command:

```bash
python stage1_analysis.py
```

## Contributing
Contributions to this project are welcome. If you have any suggestions, improvements, or bug fixes, please create an issue or submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
We would like to thank CERN and the ROOT development team for their contributions to the field of physics analysis and providing the necessary tools for this project.
