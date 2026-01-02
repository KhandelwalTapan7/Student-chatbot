Write-Host "🚀 Starting build process..."

# Create venv if not exists
if (!(Test-Path "venv")) {
    python -m venv venv
}

# Activate venv
.\venv\Scripts\Activate.ps1

Write-Host "📦 Installing dependencies..."
pip install -r requirements.txt

Write-Host "📚 Downloading NLTK data..."
python download_nltk.py

Write-Host "▶️ Starting application..."
python app.py

Write-Host "✅ Build completed successfully!"
