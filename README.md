# MeshGPT
A locally deployed AI chatbot connected to Meshtastic!

> Tested on 8GB Raspberry Pi 5 with connected to [LILYGO T-BEAM](https://lilygo.cc/en-us/products/t-beam) running Meshtastic 2.6.11 stable.

## Getting Started
**1. Setup Meshtastic device**  
Follow [Meshtastic getting started documentation](https://meshtastic.org/docs/getting-started/) for choosing a compatible radio and flashing the Meshtastic firmware.

**2. Clone repo to Raspberry Pi**  
```bash
https://github.com/azroberts8/MeshGPT.git
cd MeshGPT/
```

**3. Create virtual environment and install Python dependencies**  
```bash
python3 -m venv ./venv
source .venv/bin/activate
pip install -r requirements.txt
```

**4. Launch the application**  
```bash
python main.py
```
