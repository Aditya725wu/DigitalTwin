#!/bin/bash
# DiabetesTwin Installation Script

echo "=========================================="
echo "DiabetesTwin Installation Script"
echo "=========================================="

# Check Python version
echo "[1/5] Checking Python version..."
python3 --version || { echo "Python 3 not found"; exit 1; }

# Setup Backend
echo "[2/5] Setting up Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate  # Use 'venv\Scripts\activate' on Windows
pip install -r requirements.txt
python generate_synthetic_data.py
python train_models.py
cd ..

# Setup Frontend
echo "[3/5] Setting up Web Dashboard..."
cd web-dashboard
npm install
cd ..

# Setup Mobile
echo "[4/5] Setting up Mobile App..."
cd mobile-app
npm install
cd ..

# Create data directories
echo "[5/5] Creating directories..."
mkdir -p data models logs

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "To start the applications:"
echo ""
echo "Backend (FastAPI):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""
echo "Frontend (Next.js):"
echo "  cd web-dashboard"
echo "  npm run dev"
echo ""
echo "Mobile (Expo):"
echo "  cd mobile-app"
echo "  npx expo start"
echo ""
