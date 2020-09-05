
echo "======================================================"
echo "EJECUCION: ModelConstruction.py"
echo "INICIO: $(date)"

# Enable conda
source ~/anaconda3/etc/profile.d/conda.sh

# Activating environment
conda activate olxproject

# Running script
python ./ModelConstruction.py

echo "FINALIZACION: $(date)"
