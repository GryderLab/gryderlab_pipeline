import re
import requests
import os,subprocess
import pandas as pd
import yaml
import sys
import argparse

def main(args):

    #User input:
    #1. sample_id
    
    sample_id = args.sample
    out_file = args.out    
    masterfile_dir="/data/Clinomics/MasterFiles"
    master_files = ["Sequencing_Tracking_Master_db.txt","ClinOmics_Sequencing_Master_File_db.txt","SequencingMasterFile_OutsidePatients_db.txt"]
    hic_master_file="/data/khanlab/projects/HiC/manage_samples/HiC_sample_sheet.xlsx"
    chipseq_master_file="/data/khanlab/projects/ChIP_seq/manage_samples/ChIP_seq_samples.xlsx"
    #sample information from Young's master file
    sample_file = "Sample_" + sample_id
    master_sample = {"SampleFiles":sample_file}
    sample = {"SampleFiles":sample_file}
    default_genome="hg19"
    xeno_genome="mm10"
    #columns = ["Type of sequencing","Matched normal","Matched RNA-seq"]
    for master_file in master_files:
        file = masterfile_dir + "/" + master_file        
        master_df = pd.read_csv(file, sep='\t', encoding = "ISO-8859-1")
        master_df['Sample_ID'] = master_df['Library ID'] + '_' + master_df['FCID']
        master_df = master_df.loc[master_df['Sample_ID'] == sample_id]
        master_df = master_df.reset_index(drop=True)
        if master_df['Sample_ID'].count() > 0:
            for column in master_df:
                master_sample[column] = str(master_df[column][0])
            break
    if 'Sample_ID' not in master_sample.keys():
        print(sample_id + " not found in Khanlab master files\n")
        sys.exit(1)
    #HiC sample
    if master_sample["Type of sequencing"] == "C-il":
        df = pd.read_excel(hic_master_file)
        df = df.loc[df['Amplified_Sample_Library_Name'] == master_sample['Library ID']]
        df = df.reset_index(drop=True)
        if df['Amplified_Sample_Library_Name'].count() > 0:
            for column in df:
                sample[column] = str(df[column][0])
            fo = open(out_file,"w")
            fo.write(yaml.dump({"samples":{sample_id : sample}}))
            fo.close()
            print("hic")
        #else:
        #    sys.stderr.write(sample_id + " not found in Khanlab master files\n")
    #ChIPseq sample
    if master_sample["Type of sequencing"] == "C-il" and 'Amplified_Sample_Library_Name' not in sample:
        df = pd.read_excel(chipseq_master_file)
        df = df.loc[df['Amplified_Sample_Library_Name'] == master_sample['Library ID']]
        df = df.reset_index(drop=True)
        if df['Amplified_Sample_Library_Name'].count() > 0:
            for column in df:
                sample[column] = str(df[column][0])
            fo = open(out_file,"w")
            fo.write(yaml.dump({"samples":{sample_id : sample}}))
            fo.close()
            print("chipseq")
        else:
            sys.stderr.write(sample_id + " not found in HiC/Chipseq master files\n")
    if 'Amplified_Sample_Library_Name' not in sample:
       if "SampleRef" in master_sample:
            master_sample["Genome"] = master_sample["SampleRef"]
            del master_sample["SampleRef"]
       else:
            master_sample["Genome"] = default_genome
       if master_sample["Type"].find("xeno") >=0:
            master_sample["Xenograft"] = "yes"
            master_sample["XenograftGenome"] = xeno_genome
       master_sample["SampleCaptures"] = master_sample["Enrichment step"]
       del master_sample["Enrichment step"]
       fo = open(out_file,"w")
       fo.write(yaml.dump({"samples":{sample_id : master_sample}}))
       fo.close()
       print("rnaseq")       
    
parser = argparse.ArgumentParser(description='Generate YAML sample sheet.')
parser.add_argument("--sample", "-s", metavar="SAMPLE_ID", help="Sample ID (Library_id)_(FCID)")
parser.add_argument("--out", "-o", metavar="OUTPUT", help="Output YAML file")
args = parser.parse_args()

main(args)