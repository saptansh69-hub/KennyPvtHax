#!/bin/bash
set -e

echo "========================================"
echo " KennyPvtHax — Railway Build Script"
echo "========================================"

# --- 1. Build Frontend ---
echo "[1/4] Installing frontend dependencies with npm..."
cd frontend
npm install

echo "[2/4] Building frontend for production..."
# Empty REACT_APP_BACKEND_URL means API calls go to /api/ (same domain)
REACT_APP_BACKEND_URL="" npm run build
cd ..

# --- 2. Copy build to backend/static ---
echo "[3/4] Copying frontend build to backend/static..."
rm -rf backend/static
mkdir -p backend/static
cp -r frontend/build/* backend/static/

# --- 3. Install backend dependencies ---
echo "[4/4] Installing backend Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo "========================================"
echo " Build complete!"
echo "========================================"