
echo "======================================================"
echo "EJECUCION: Transformation.py"
echo "INICIO: $(date)"

# Enable conda
source ~/anaconda3/etc/profile.d/conda.sh

# Activating environment
conda activate olxproject

# Running script
python ./Transformation.py

echo "FINALIZACION: $(date)"
