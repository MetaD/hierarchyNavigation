#!/bin/tcsh

3dDeconvolve -nodata 395 1              \
    -num_stimts 2                       \
    -polort A                           \
    -stim_times 1 design_0/real_stimulus_0.txt 'GAM'  \
    -stim_label 1 design_0/stim0                 \
    -stim_times 2 design_0/real_stimulus_1.txt 'GAM'  \
    -stim_label 2 design_0/stim1                 \
    -x1D X.xmat.1D -xjpeg X.jpg         \
    -x1D_uncensored X.nocensor.xmat.1D
