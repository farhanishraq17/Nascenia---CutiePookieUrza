#!/bin/bash
#SBATCH --job-name=nd-sw-b12
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:a40:1
#SBATCH --exclude=notch294,notch299
#SBATCH -c 6
#SBATCH --mem=40G
#SBATCH -t 08:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/sw-champ-b12.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/sw-champ-b12.out
bash /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/tasks_a800/sw-champ-b12.sh
