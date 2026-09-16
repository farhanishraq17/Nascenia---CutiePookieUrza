#!/bin/bash
#SBATCH --job-name=nd-final-analysis
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --gres=gpu:1
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 04:00:00
#SBATCH --dependency=afterany:1795701:1795702
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-final-analysis.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-final-analysis.out
# waits for dec-A and dec-B so the scoreboard, phase-2 audit and pooled-MBR gate all see
# the E07/E13/E23/E12 records those two jobs are writing.
bash /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/final_analysis.sh
