#!/bin/bash
#SBATCH --job-name=nasc-probe
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn008
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:05:00
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/probe.out
hostname
nvidia-smi --query-gpu=index,name,memory.total --format=csv
