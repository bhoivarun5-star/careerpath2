
import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studentsystem.settings')
django.setup()

from django.contrib.auth import get_user_model

try:
    User = get_user_model()
    superusers = User.objects.filter(is_superuser=True)
    
    print(f"Found {superusers.count()} superuser(s):")
    for user in superusers:
        print(f"Username: {user.username}, Email: {user.email}")
        
except Exception as e:
    print(f"Error: {e}")
