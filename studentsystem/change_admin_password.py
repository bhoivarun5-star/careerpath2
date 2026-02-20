
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
    try:
        user = User.objects.get(username='admin')
        user.set_password('ChangeMe123!')
        user.save()
        print(f"Successfully changed password for user '{user.username}' to 'ChangeMe123!'.")
    except User.DoesNotExist:
        print("User 'admin' does not exist.")
except Exception as e:
    print(f"Error: {e}")
