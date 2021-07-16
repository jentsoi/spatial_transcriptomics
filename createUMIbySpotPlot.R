#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

.libPaths(c("/SFS/user/ctc/tsoij/R/4.0.2", .libPaths()))

suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(viridis)) 

fn <- args[1]
samplename <- gsub('.tsv','',fn)
sampletitle <- unlist(strsplit(samplename,'/'))
sampletitle <- sampletitle[length(sampletitle)]
mapping <- read.delim(fn,stringsAsFactors = F)
mapping %>% ggplot(aes(colNum,rowNum))+geom_raster(aes(fill=log10(counts)))+scale_fill_viridis(discrete=F)+scale_y_reverse(expand = c(0,0))+theme_bw()+scale_x_continuous(expand = c(0,0))+theme(aspect.ratio = 1)+ggtitle(sampletitle)+
  theme(plot.title = element_text(hjust = 0.5))
ggsave(paste0(samplename,'.pdf'),width=4.5,h=3)


