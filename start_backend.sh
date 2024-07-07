VENV_DIR="journalling_app_venv"

# Check if the virtual environment directory exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment '$VENV_DIR' already exists."
else
    echo "Creating virtual environment '$VENV_DIR'..."
    # Create a virtual environment
    python3 -m venv $VENV_DIR
    
    echo "Virtual environment '$VENV_DIR' created successfully."
fi

source $VENV_DIR/bin/activate
pip install -r requirements.txt
python run.py