#!/bin/bash -e

## Run post-processing in sample folder

# Collect web summaries

mkdir -p html_summary

for sample in *; do
    if [ -e "$sample/outs/web_summary.html" ]; then
        cp $sample/outs/web_summary.html html_summary/$sample.web_summary.html
    fi
done

# Create umi matrix files, heatmap, and delete bam files

module load samtools
module load R/4.0.2
scripts=$(pwd)
mkdir -p umi_matrix

for sample in *; do
    if [ -e "$sample/outs/possorted_genome_bam.bam" ]; then
    echo "processing sample "$sample
    echo "creating umi matrix..."
    samtools view $sample/outs/possorted_genome_bam.bam | python $scripts/countCB.py - $sample/outs/spatial/tissue_positions_list.csv umi_matrix/$sample.tsv
    echo "Storing umi matrix in umi_matrix/"$sample.tsv

    echo "creating heatmap plot..."
    Rscript $scripts/createUMIbySpotPlot.R umi_matrix/$sample.tsv
    echo "done"

    rm $sample/outs/possorted_genome_bam.bam
    rm $sample/outs/possorted_genome_bam.bam.bai

    fi
done

