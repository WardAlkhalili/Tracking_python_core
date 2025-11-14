#! /bin/bash
cd /var/www/Tracking_python_core
source venv/bin/activate
nohup python3 manage.py runserver 0.0.0.0:8080
