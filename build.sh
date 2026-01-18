#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Create upload directories
mkdir -p app/static/uploads/items
mkdir -p app/static/uploads/avatars

# Create database tables
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized')"