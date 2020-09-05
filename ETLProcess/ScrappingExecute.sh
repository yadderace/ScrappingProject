
echo "======================================================"
echo "EJECUCION: Scrapping.py"
echo "INICIO: $(date)"

# Enable conda
source ~/anaconda3/etc/profile.d/conda.sh

# Activating environment
conda activate olxproject

# Running script
python ./Scrapping.py

echo "FINALIZACION: $(date)"
