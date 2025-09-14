#!/usr/bin/env python
"""
Test simple des améliorations des alertes
"""

import os
import sys

# Vérifier que les fichiers existent
files_to_check = [
    "gestion_credits/views.py",
    "gestion_credits/templates/gestion_credits/alerte_list.html",
    "gestion_credits/static/gestion_credits/css/alertes.css",
    "gestion_credits/templates/gestion_credits/base.html"
]

print("🧪 Vérification des améliorations des alertes")
print("=" * 50)

all_files_exist = True

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path}")
        all_files_exist = False

print("\n" + "=" * 50)

if all_files_exist:
    print("🎉 Tous les fichiers sont présents !")
    print("\n📝 Pour tester l'interface:")
    print("   1. Activez l'environnement virtuel: venv\\Scripts\\activate")
    print("   2. Démarrez le serveur: python manage.py runserver")
    print("   3. Allez sur: http://127.0.0.1:8000/alertes/")
    print("   4. Vérifiez les 3 blocs et les filtres avancés")
else:
    print("❌ Certains fichiers sont manquants")
    sys.exit(1)
