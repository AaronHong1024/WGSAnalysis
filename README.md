# Whole Genome Sequencing (WGS) Analysis

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub release](https://img.shields.io/github/release/AaronHong1024/WGSAnalysis.svg)](https://github.com/AaronHong1024/WGSAnalysis/releases)

[Enhanced barrier precautions to prevent transmission of Staphylococcus aureus and Carbapenem-resistant organisms in nursing home chronic ventilator units](https://www.cambridge.org/core/journals/infection-control-and-hospital-epidemiology/article/abs/enhanced-barrier-precautions-to-prevent-transmission-of-staphylococcus-aureus-and-carbapenemresistant-organisms-in-nursing-home-chronic-ventilator-units/43FBB459BB569B052DEDF87EA57193FB)

A Workflow for Analyzing Staphylococcus aureus and Carbapenem-Resistant Gram-Negative Bacteria (Acinetobacter baumannii, Pseudomonas aeruginosa, and Klebsiella pneumoniae) in Chronic Ventilator Units in Nursing Homes
## Requirements
The following tools are required for this analysis:

| Tool        | Github Repository                         | Description                    |
|-------------|-------------------------------------------|--------------------------------|
| SPAdes      | https://github.com/ablab/spades           | Genome assembly tool           |
| MLST        | https://github.com/tseemann/mlst          | Multi-Locus Sequence Typing    |
| Snippy      | https://github.com/tseemann/snippy        | SNP detection tool             |


Ensure that all tools are installed and accessible in your system's PATH. It's recommended to use package managers like Conda for easy installation and environment management.

## Data Preparation
1. Download the dataset from the NCBI SRA database using the following link: https://www.ncbi.nlm.nih.gov/sra/PRJNA1163733
2. Organize the data according to the organism type as indicated in the `XUMMR_Illumina_Report.pdf` file.

## Analysis Workflow

### 1. Genome Assembly with SPAdes
Run the SPAdes assembly pipeline:
```bash
python spades_analysis.py
```
The script will prompt for:
- Base path for input directories (containing sample folders with ILLUMINA_DATA)
- Output directory for assembly results
- CPU cores [default: 16]

**Input Structure Expected:**
```
input_directory/
├── Sample1/
│   └── ILLUMINA_DATA/
│       ├── sample1_R1_trimmed.fastq.gz
│       └── sample1_R2_trimmed.fastq.gz
├── Sample2/
│   └── ILLUMINA_DATA/
│       ├── sample2_R1_trimmed.fastq.gz
│       └── sample2_R2_trimmed.fastq.gz
└── ...
```

### 2. SNP Detection with Snippy
Run the Snippy SNP detection pipeline:
```bash
python snippy_analysis.py
```
The script will prompt for:
- Base path for FASTQ files (same as SPAdes input)
- Output directory for SNP analysis results
- Reference genome file path
- CPU cores [default: 16]

### 3. Data Grouping with MLST
Group the dataset using MLST:
```bash
./mlst.sh
python mlst.py
```
- `mlst.sh`: Runs MLST analysis on all samples
- `mlst.py`: Groups samples according to MLST results

### 4. Core SNP Alignment
Generate a core SNP alignment for each MLST group:
```bash
snippy-core [--noref] snippyDir1/ snippyDir2/ snippyDir3/ ...
```


## Output Files

### SPAdes Assembly Output
- `{sample}_assembly/`: Directory containing assembly results for each sample
  - `contigs.fasta`: Assembled contigs
  - `scaffolds.fasta`: Assembled scaffolds
  - `assembly_graph.fastg`: Assembly graph
  - `spades.log`: SPAdes log file
- `spades_analysis.log`: Detailed log of the analysis process

## Citation
>O’Hara LM, Newman M, Lydecker AD, et al. Enhanced barrier precautions to prevent transmission of Staphylococcus aureus and Carbapenem-resistant organisms in nursing home chronic ventilator units. Infection Control & Hospital Epidemiology. Published online 2025:1-8. doi:10.1017/ice.2025.10237
