#!/bin/bash

# Current directory
current_directory=$(pwd)

# create a new directory to store the filtered contigs
for folder in */; do

    original_fasta="${current_directory}/${folder}contigs.fasta"
    new_fasta="${current_directory}/${folder}contigs_filtered.fasta"

    if [ -f "$original_fasta" ]; then

        awk 'BEGIN {RS=">"; FS="\n"; ORS=""} 
        NR > 1 {seq = ""; for (i=2; i<=NF; i++) seq = seq $i; if(length(seq) >= 1000) print ">" $1 "\n" seq "\n"}' "$original_fasta" > "$new_fasta"
    fi
done

# 打印完成的消息
echo "Filtering complete."

