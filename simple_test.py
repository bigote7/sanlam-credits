#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.forms import CreditDiviseCompletForm

# Test simple du formulaire
form = CreditDiviseCompletForm()
print("Champs du formulaire:")
for field_name, field in form.fields.items():
    print(f"  - {field_name}: {type(field).__name__}")

print(f"\nTotal des champs: {len(form.fields)}")
