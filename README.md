## Spatial Transcriptomics 

### 1. Parse meta data into mkfastq and spaceranger count scripts

```
python parse_samplesheet.py <sample_sheet_file>
```
<br>

Samplesheet file is tab-delimited with the following required column headers:
- sample
- index
- fastq
- genome
- slide
- area
- image

and optional columns:
- lane (default: all)
- description


Generated output files:

- <sample_sheet_file>_mkfastq_input.csv - simple csv file for mkfastq
- <sample_sheet_file>_<lane>_sample_proc.sh - script to run submit spaceranger commands to hpc


Notes:
- Slide serial.gpr files should be in the same folder as image directory or else an error will be thrown.
- Output directory name for the fastq files are taken from the fastq path, using the string after last '_' split.


### 2. Run generated script to submit spaceranger qsub commands to the HPC

```
./<sample_sheet_file>_<lane>_sample_proc.sh
```

### 3. Run postprocessing scripts

```
./postproc_spaceranger.sh

```
