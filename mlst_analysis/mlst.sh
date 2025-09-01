#!/bin/bash

# set the directory containing the assembled contigs
directory="Enter your path"

output_base="Enter your path"

for folder in "$directory"/*; do
    if [ -d "$folder" ]; then
        output_dir="$output_base/$(basename "$folder")_mlst_output"

        mlst "$folder"/contigs.fasta > "$output_dir"

    fi
done
