#!/bin/bash
set -euo pipefail

echo "=== [1/4] Installing backend Python dependencies ==="
pip install --no-cache-dir -r requirements.txt

echo "=== [2/4] Installing frontend dependencies ==="
cd frontend
npm ci

echo "=== [3/4] Building frontend ==="
# Empty REACT_APP_BACKEND_URL => API calls go to /api on the same origin
DISABLE_ESLINT_PLUGIN=true REACT_APP_BACKEND_URL="" npm run build
cd ..

echo "=== [4/4] Copying build into backend/static ==="
rm -rf backend/static
mkdir -p backend/static
cp -r frontend/build/. backend/static/

echo "=== Build complete ==="
