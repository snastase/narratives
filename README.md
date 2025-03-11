# Narratives  
### fMRI data for evaluating models of naturalistic language comprehension

![Alt text](https://upload.wikimedia.org/wikipedia/commons/a/a0/Orphant_Annie_Book_%E2%80%93_Title_page.jpg?raw=true&s=100 "The Orphant Annie Book")  
<sub><sup>Ethel Franklin Betts (1908), from The Orphant Annie Book, by James Whitcomb Riley ([wikimedia](https://commons.wikimedia.org/wiki/File:Orphant_Annie_Book_%E2%80%93_Title_page.jpg))</sup></sub>

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![OpenNeuro](https://img.shields.io/badge/Data-OpenNeuro-teal)](https://openneuro.org/datasets/ds002345)
[![DataLad](https://img.shields.io/badge/Data-DataLad-orange)](http://datasets.datalad.org/?dir=/labs/hasson/narratives)

This repository accompanies the public release of the "Narratives" data collection and the corresponding data descriptor paper currently in preparation. The "Narratives" collection comprises fMRI data collected while participants listened to 27 spoken story stimuli ranging from ~3 minutes to ~56 minutes for a total of ~4.6 hours of unique stimuli. The collection currently includes 345 unique subjects participating in a total of 891 functional scans with accompanying anatomical data. Data were collected over the course of roughly seven years, from October, 2011 to September, 2018. All participants provided informed, written consent prior to data collection in accordance with experimental procedures approved by Princeton University Institutional Review Board. Slides for a presentation of this dataset at SfN 2019 are available on [Google Slides](https://docs.google.com/presentation/d/1KNViRGPHFf53PJLTM-1B1ZguHXSPWR2nppkLWNLSuy8/edit?usp=sharing). The raw BIDS-compliant data can be accessed via [**OpenNeuro**](https://openneuro.org/datasets/ds002345) and [**DataLad**](http://datasets.datalad.org/?dir=/labs/hasson/narratives).

#### Authors
Correspondence: Samuel A. Nastase ([sam.nastase@gmail.com](mailto:sam.nastase@gmail.com))

If you find this dataset useful, please cite the following:

Nastase, S. A., Liu, Y.-F., Hillman, H., Zadbood, A., Hasenfratz, L., Keshavarzian, N., Chen, J., Honey, C. J., Yeshurun, Y., Regev, M., Nguyen, M., Chang, C. H. C., Baldassano, C., Lositsky, O., Simony, E., Chow, M. A., Leong, Y. C., Brooks, P. P., Micciche, E., Choe, G., Goldstein, A., Vanderwal, T., Halchenko, Y. O., Norman, K. A., & Hasson, U. (2021). The “Narratives” fMRI dataset for evaluating models of naturalistic language comprehension. *Scientific Data*, *8*, 250. [`DOI`](https://doi.org/10.1038/s41597-021-01033-3)

#### Code
This repository contains both scripts used to prepare the data for sharing (`staging/`) and scripts used to analyze the BIDS-formatted data (`code/`). For example, in the `staging` directory, you can find scripts for compiling data and metadata, environment files specifying the Python software stack (e.g. `environment.yml`), and example stimulus presentation scripts (e.g. `story_presentation.py`). The following list summarizes the scripts from the `code/` directory used to process the "Narratives" data with brief descriptions (roughly in orer of execution):

* `compile_metadata.py`: Compile dictionaries containing metadata and filenames for each subject (`subject_meta.json`) and task (`task_meta.json`).
* `brain_masks.py`: Create brain masks for data in MNI space and fsaverage6 space.
* `roi_masks.py`: Create early auditory cortex ROI masks based on multimodal cortical parcellation.
* `run_pydeface.py`: Run PyDeface to anonymize (de-face) each subject’s anatomical image(s).
* `run_mriqc.sh`: Run participant-level MRIQC on BIDS-formatted data for one subject.
* `slurm_mriqc.sh`: Submit Slurm job array to run MRIQC on many subjects in parallel.
* `run_mriqc_group`.sh: Run group-level MRIQC to summarize participant-level MRIQC outputs.
* `run_fmriprep.sh`: Run fMRIPrep on BIDS-formatted data for one subject.
* `slurm_fmriprep.sh`: Submit Slurm job array to run fMRIPrep on many subjects in parallel.
* `run_smoothing.py`: Run spatial smoothing using AFNI’s 3dBlurToFWHM and SurfSmooth for one subject.
* `slurm_smoothing.sh`: Submit Slurm job array to run spatial smoothing on many subjects in parallel.
* `extract_confounds.py`: Extract confound variables from fMRIPrep outputs for use with AFNI’s 3dTproject.
* `run_regression.py`: Run confound regression using AFNI’s 3dTproject for one subject.
* `slurm_regression.py`: Submit Slurm job array to run confound regression on many subjects in parallel.
* `run_isc.py`: Run whole-brain vertex-wise leave-one-out intersubject correlation (ISC) analysis on smoothed surface data across all subjects in each story.
* `roi_average.py`: Average non-smoothed time series across vertices within early auditory cortex ROI.
* `roi_isc.py`: Compute leave-one-out ISC for early auditory cortex ROI.
* `roi_lags.py`: Compute ISC for early auditory cortex ROI at lags ranging from -30 to +30 TRs.
* `exclude_scans.py`: Compile dictionary (`scan_exclude.json`) for excluding scans based on ISC in early auditory cortex ROI with `exclude_scan` function.
* `get_demog.py`: Summarize demographic information (age, sex) based on participants.tsv file
* `get_words.py`: Summarize the number of words (including missing and unknown) across all stimuli.
* `get_tsnr.py`: Estimate tSNR using AFNI’s 3dTstat and compute median tSNR across all scans.
* `get_fwhm.py`: Estimate intrinsic smoothness using AFNI’s 3dFWHMx for one subject.
* `slurm_fwhm.py`: Submit Slurm job array to run smoothness estimation on many subjects in parallel.
* `plot_stim.py`: Plot audio waveform for Pie Man stimulus with example voxel time series (Figure 1).
* `plot_qc.py`: Plot tSNR and FD from MRIQC, as well as intrinsic smoothness (Figure 2).
* `plot_isc.py`: Plot ISC and lagged ISC for the early auditory cortex ROI (Figure 3).
* `gifti_io.py`: Helper functions for reading and writing GIfTI surface files in Python.

#### Acknowledgments
We thank Leigh Nystrom, Mark Pinsk, Garrett McGrath, and the administrative staff at the Scully Center for the Neuroscience of Mind and Behavior and the Princeton Neuroscience Institute, as well as Elizabeth McDevitt, Anne Mennen, and members of Pygers support group. We thank Franklin Feingold for assistance in data sharing, as well as Chris Gorgolewski, Tal Yarkoni, Satrajit S. Ghosh, Avital Hahamy, Mohamed Amer, Indranil Sur, Xiao Lin, and Ajay Divarakian for helpful feedback on the data and analysis. This work was supported by the National Institutes of Health (NIH) grants R01-MH094480 (U.H.), DP1-HD091948 (U.H.), R01-MH112566 (U.H.), R01-MH112357 (K.A.N., U.H), T32-MH065214 (K.A.N), by the Defense Advanced Research Projects Agency (DARPA) Brain-to-Brain Seedling contract number FA8750-18-C-0213 (U.H.), and by the Intel Corporation. The views, opinions, and/or conclusions contained in this paper are those of the authors and should not be interpreted as representing the official views or policies, either expressed or implied of the NIH, DARPA, or Intel.
