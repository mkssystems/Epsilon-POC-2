#!/bin/bash
# Activate migrations (Clean Database Initialization)
flask shell <<EOF
from main import db
db.drop_all()
db.create_all()
EOF

# Run Flask application via Gunicorn
gunicorn -b 0.0.0.0:5000 main:app
