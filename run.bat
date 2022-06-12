echo "Installing depedencies..."
pip install -r requirements.txt

echo "Initialize App Config..."
set CONFIG_PATH=D:\ARC\photobooth\config.yaml

echo "Starting Python Photobooth Service..."
python main.py

pause