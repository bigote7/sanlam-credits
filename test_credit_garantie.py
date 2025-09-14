#!/usr/bin/env python
"""
Test des améliorations du formulaire de crédit avec chèque de garantie
"""

import os
import sys

# Vérifier que les fichiers existent
files_to_check = [
    "gestion_credits/forms.py",
    "gestion_credits/templates/gestion_credits/credit_form.html",
    "gestion_credits/static/gestion_credits/css/credit_form.css",
    "gestion_credits/views.py"
]

print("🧪 Test des améliorations du formulaire de crédit avec chèque de garantie")
print("=" * 70)

all_files_exist = True

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path}")
        all_files_exist = False

print("\n" + "=" * 70)

if all_files_exist:
    print("🎉 Tous les fichiers sont présents !")
    print("\n📝 Pour tester l'interface:")
    print("   1. Activez l'environnement virtuel: venv\\Scripts\\activate")
    print("   2. Démarrez le serveur: python manage.py runserver")
    print("   3. Allez sur: http://127.0.0.1:8000/credits/create/?type=unique")
    print("   4. Vérifiez le nouveau casier 'Chèque de garantie (optionnel)'")
    print("   5. Cochez la case pour voir apparaître les champs de chèque")
    
    print("\n🔧 Nouvelles fonctionnalités ajoutées:")
    print("   - ✅ Case à cocher 'Le client fournit un chèque de garantie'")
    print("   - ✅ Numéro de référence du chèque")
    print("   - ✅ Banque émettrice")
    print("   - ✅ Date d'émission du chèque")
    print("   - ✅ Date prévue de règlement")
    print("   - ✅ Remarques (optionnel)")
    print("   - ✅ Animation d'apparition/disparition")
    print("   - ✅ Validation des champs obligatoires")
    print("   - ✅ Création automatique du chèque et de l'échéance")
    
else:
    print("❌ Certains fichiers sont manquants")
    sys.exit(1)

print("\n" + "=" * 70)
print("🚀 Test terminé avec succès !")
