#!/bin/bash
# build.sh for Student-chatbot deployment

echo "🚀 Starting build process..."

# Exit immediately if any command fails
set -e

echo "📦 Installing dependencies with Poetry..."
poetry install --no-interaction

# If your project needs to compile/install specific packages
# echo "🔧 Installing additional system dependencies (if any)..."
# apt-get update && apt-get install -y [your-packages]

echo "🏗️ Building the project..."
poetry build || echo "Note: poetry build not required, continuing..."

# If you need to run database migrations
# echo "🗄️ Running database migrations..."
# poetry run python manage.py migrate  # Django example
# OR for FastAPI with Alembic:
# poetry run alembic upgrade head

# If you need to collect static files (for Django)
# echo "📁 Collecting static files..."
# poetry run python manage.py collectstatic --noinput

# If you need to run tests
# echo "🧪 Running tests..."
# poetry run pytest

echo "✅ Build completed successfully!"