#!/usr/bin/bash

sample_id=$1

current_dir=`pwd`
d=`dirname $0`
cd $d/..
pipeline_home=`pwd`
cd $current_dir
sample_sheet_home=/data/khanlab/projects/pipeline_production/sample_sheets
processed_data_home=/data/khanlab/projects/pipeline_production/processed_DATA

if [ ! -z $sample_id ];then
	samples=( $sample_id )
else
	echo "usage: $0 [sample_id]"
	echo
	echo "Example 1: process specific sample"
	echo "   $0 RH4_Ent6_H3K27ac_HiChIP_HH3JVBGX7"
	echo
	exit
fi

module load python/3.6

#type=`python $pipeline_home/scripts/sampleToYaml.py -s $sample_id -o ${sample_id}.yaml -c /data/khanlab/projects/ChIP_seq/manage_samples/ChIP_seq_samples_hc.xlsx`
#res_str=`python $pipeline_home/scripts/sampleToYaml.py -s $sample_id -o ${sample_id}.yaml -c /data/khanlab/projects/ChIP_seq/manage_samples/ChIP_seq_samples_hc.xlsx`
res_str=`python $pipeline_home/scripts/sampleToYaml.py -s $sample_id -o ${sample_id}.yaml`
IFS=$'\n' read -rd '' -a res <<< "$res_str"
type=${res[0]}
genome_str=${res[1]}
IFS=',' read -rd '' -a genomes <<< "$genome_str"
echo $type
echo $genome_str
yaml_file=$sample_sheet_home/$type/${sample_id}.yaml
if [[ "$type" == "hic" || "$type" == "chipseq" || "$type" == "rnaseq" ]];then
	echo "mv ${sample_id}.yaml $yaml_file"
	mv ${sample_id}.yaml $yaml_file
	for genome in "${genomes[@]}";do
		g_nos=`echo $genome | sed 's/ //g'`
		echo perl $pipeline_home/launch.pl -t $type -w $processed_data_home/$g_nos/$type -s $yaml_file -g $g_nos
		perl $pipeline_home/launch.pl -t $type -w $processed_data_home/$g_nos/$type -s $yaml_file -g $g_nos
	done
else
	echo "Error: Sample sheet generation failed: $sample_id. Reason: $type"  #|mutt -s 'Gryderlab Pipeline Status' `whoami`@case.edu
fi

