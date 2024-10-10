# Virus Analysis
A Workflow for Analyzing Staphylococcus aureus and Carbapenem-Resistant Gram-Negative Bacteria (Acinetobacter baumannii, Pseudomonas aeruginosa, and Klebsiella pneumoniae) in Chronic Ventilator Units in Nursing Homes
## Requirements
The following tools are required for this analysis:

| Tool        | Github Repository                         |
|-------------|-------------------------------------------|
| Snakemake   | https://github.com/snakemake/snakemake    |
| Spades      | https://github.com/ablab/spades           |
| Mlst        | https://github.com/tseemann/mlst          |
| Snippy      | https://github.com/tseemann/snippy        |
| veryfasttree| https://github.com/citiususc/veryfasttree |
| TreeCluster | https://github.com/niemasd/TreeCluster    |

Ensure that all tools are installed and accessible in your system's PATH. It's recommended to use package managers like Conda for easy installation and environment management.

## Data Preparation
1. Download the dataset from the NCBI SRA database using the following link: https://www.ncbi.nlm.nih.gov/sra/PRJNA1163733
2. Organize the data according to the organism type as indicated in the `XUMMR_Illumina_Report.pdf file`.
## Genome Assembly
Assemble the dataset using the Snakemake workflow with both Snippy and Spades:
```
cd snippy_snakemake
nohup snakemake --cluster "sbatch -A {cluster.account} -q {cluster.qos} -c {cluster.cpus-per-task} -N {cluster.Nodes}  -t {cluster.runtime} --mem {cluster.mem} -J {cluster.jobname} --mail-type={cluster.mail_type} --mail-user={cluster.mail}" --cluster-config cluster.json --jobs 100 --latency-wait 120 &
```
```
cd spades_snakemake
nohup snakemake --cluster "sbatch -A {cluster.account} -q {cluster.qos} -c {cluster.cpus-per-task} -N {cluster.Nodes}  -t {cluster.runtime} --mem {cluster.mem} -J {cluster.jobname} --mail-type={cluster.mail_type} --mail-user={cluster.mail}" --cluster-config cluster.json --jobs 100 --latency-wait 120 &
```
- Note: Modify the cluster parameters according to your HPC scheduler and resource availability.
- Background Execution: The nohup command allows the process to continue running in the background even if the terminal session is closed.
## Data Grouping
Group the dataset using MLST:
```
./mlst.sh
python mlst.py
```
- mlst.sh: Runs MLST analysis on all samples.
- mlst.py: Groups samples according to MLST results. 
## SNP Alignment with Snippy
Generate a core SNP alignment for each MLST group:
```
snippy-core [--noref] snippyDir1/ snippyDir2/ snippyDir3/ ...
```

## Phylogenetic Analysis
### Constructing the Phylogenetic Tree
Use VeryFastTree to build the phylogenetic tree:
```
./VeryFastTree -threads 16 -gtr core.full.aln > tree.nwk
```
### Clustering the Phylogenetic Tree
Cluster the phylogenetic tree using TreeCluster:
```
TreeCluster.py -i <input tree> -t 0.01 > <output clusters>
```