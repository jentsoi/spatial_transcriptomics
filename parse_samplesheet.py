#!/usr/bin/env python

import sys,os

def openFileRead(sampleSheetFile):
    try:
        f=open(sampleSheetFile,'r')
    except IOError:
        print('Error: File not found\n')
        sys.exit(1)
    return f

def openFileWrite(outputFile):
    try:
        f=open(outputFile,'w+')
    except IOError:
        print('Error: Cannot write file\n')
        sys.exit(1)
    return f

def main():
    sampleSheetFile = sys.argv[1]

    try:
        sampleSheetFileName = sys.argv[2]
    except: 
        sampleSheetFileName=sampleSheetFile.rsplit('/',1)[1].rsplit('.',1)[0]
        print(sampleSheetFileName)

    lane = '*'
    description = 'NA'
    requiredVals = ['sample','index','fastq','genome','slide','area','image']
    slideAreaValues = ['A1','B1','C1','D1']
    genomeValues = ['GRCh38','mm10','GRCh38_mm10']
    genomePath= '/10X_genome/'
    genomeDict = {
        'GRCh38': genomePath+'refdata-gex-GRCh38-2020-A',
        'mm10': genomePath+'refdata-gex-mm10-2020-A',
        'GRCh38_mm10': genomePath+'refdata-gex-GRCh38-and-mm10-2020-A'
    }

    if not os.path.exists('data'): os.makedirs('data')

    outputDir = '/data/'
    

    # open files
    f = openFileRead(sampleSheetFile)
        
    # check sample sheet headers
    header = f.readline().rstrip().split('\t')
    headerCheck = ([x for x in requiredVals if x not in header])
    if len(headerCheck) > 0: 
        missingItems = ' '.join(headerCheck)
        print('Error: Missing column(s) in file: {}\n'.format(missingItems))
        sys.exit(1)
    
    # parse sample sheet data
    sampleNum = 0
    seqDirInput = {}
    seqDirCmds = {}
    slideDict = {}
    dataList = []
    errorNum = 0

    for line in f:
        sampleNum = sampleNum + 1
        values = line.rstrip().split('\t')
        valueOrder = ([header.index(x) for x in requiredVals])
        sample,index,fastq,genome,slide,area,image = [values[x] for x in valueOrder]

        if 'lane' in header: lane = values[header.index('lane')]
        if 'description'in header: description = values[header.index('description')]
        dataList.append([sample,index,fastq,genome,slide,area,image,lane,description])
        
        # check values are valid
        if sample.replace('-','').replace('_','').isalnum() is False:
            print('Invalid characters in sample name at sample #{}<br>'.format(sampleNum))
            errorNum = errorNum +1
        if any([x == '' for x in [sample,lane,index,fastq,description,genome,slide,area,image]]):
            print('Error: Missing values(s) at sample #{}<br>'.format(sampleNum))
            errorNum = errorNum +1
        if area not in slideAreaValues:
            print('Error: Invalid slide area at sample #{}<br>'.format(sampleNum))
            errorNum = errorNum +1
        if genome not in genomeValues:
            print('Error: Invalid genome at sample #{}<br>'.format(sampleNum))
            errorNum = errorNum +1
    
        # check if file and directories exist:
        if os.path.isdir(fastq) == False:
            print('Error: Invalid fastq directory location at sample #{}<br>'.format(sampleNum))
            errorNum = errorNum +1 
        if os.path.isfile(image) == False:
            print('Error: Invalid image location at sample #{}<br>'.format(sampleNum))
            errorNum = errorNum +1
        gprfile = '{}/{}.gpr'.format(image.rsplit('/',1)[0],slide)
        if os.path.isfile(gprfile) == False:
            print('Error: Please place slide gpr file in same directory as image for sample #{}<br>'.format(sampleNum))
            errorNum = errorNum +1

        # check slide and area is unique
        if slide not in slideDict: slideDict[slide]=[]
        if area in slideDict[slide]:
            print('Error: Duplicate slide and area at sample #{}<br>'.format(sampleNum))
            errorNum = errorNum +1
        else: slideDict[slide].append(area)
    
    if(errorNum > 0):
        sys.exit(1)

    for item in dataList:
        sample,index,fastq,genome,slide,area,image,lane,description=item
        slide_loc = image.rsplit('/',1)[0]+'/'+slide

        output = fastq.rsplit('/',1)[1].rsplit('_',1)[1]
        if output not in seqDirInput:

            # create input csv file
            mkfastqInputFile = outputDir+sampleSheetFileName+'_mkfastq_input_'+output+'.csv'
            mkfastqInput = openFileWrite(mkfastqInputFile)
            mkfastqInput.write('Lane,Sample,Index'+'\n')
            seqDirInput[output]=mkfastqInput

            # create command sh file
            qsubCommandListFile = '{}{}_{}_sample_proc.sh'.format(outputDir,sampleSheetFileName,output)
            print(qsubCommandListFile)
            qsubCommandList = openFileWrite(qsubCommandListFile)
            seqDirCmds[output]=qsubCommandList

            seqDirCmds[output].write('#!/bin/bash\n\n')
            # seqDirCmds[output].write('mkdir -p spaceranger_fastq\n')
            # seqDirCmds[output].write('mkdir -p spaceranger_output\n\n')

            cmd = 'qsub $(pwd)/spaceranger/1_spaceranger_mkfastq.sh -d {} -i {} -o {}'.format(fastq,mkfastqInputFile,output)
            seqDirCmds[output].write('cmd=\"{}\"\n'.format(cmd))
            seqDirCmds[output].write('output=$(exec $cmd)\n')
            seqDirCmds[output].write("job_id=$(echo $output | awk '{ if($(NF)==\"submitted\") print $3 }')\n")
            seqDirCmds[output].write('echo "spaceranger mkfastq job ID $job_id submitted"\n\n')

        seqDirInput[output].write(','.join([lane,sample,index])+'\n')
        
        # write space ranger count commands
        
        genomeFull = genomeDict[genome]
        qsubCountCommand = 'qsub -hold_jid $job_id $(pwd)/spaceranger/2_spaceranger_count.sh -d {0}/outs/fastq_path -i {1} -g {2} -o {3} -t {4} -s {5} -a {6} -f {7}.gpr -b'.format(output,sample,genomeFull,sample,image,slide,area,slide_loc)
        if description != 'NA': qsubCountCommand = qsubCountCommand+ ' -e '+ description
        seqDirCmds[output].write(qsubCountCommand+'\n')
        
    print('Output Files:<br>')
    fastqDirs = '<br>'.join([x+'/outs/fastq_path' for x in seqDirInput])

    print('<br>simple csv files for mkfastq:<br>')
    for mkfastqInput in seqDirInput.values():
        print(mkfastqInput.name)
        mkfastqInput.close()

    print('<br><br>processing scripts:<br>')
    for cmdFile in seqDirCmds.values():
        print(cmdFile.name)
        cmdFile.close()

    print('<br><br>Fastq output directories:<br>{}<br>'.format(fastqDirs))

if __name__ == '__main__':
  main()                                 

