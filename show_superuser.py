#!/usr/bin/env python
"""
Script pour afficher les informations du super utilisateur Django
"""

import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from django.contrib.auth.models import User

def afficher_super_users():
    """Affiche tous les super utilisateurs de la base de données"""
    
    print("=" * 60)
    print("🔍 RECHERCHE DES SUPER UTILISATEURS")
    print("=" * 60)
    
    # Récupérer tous les super utilisateurs
    super_users = User.objects.filter(is_superuser=True)
    
    if not super_users.exists():
        print("❌ Aucun super utilisateur trouvé dans la base de données.")
        print("\n📝 Pour créer un super utilisateur, utilisez :")
        print("   python manage.py createsuperuser")
        return
    
    print(f"✅ {super_users.count()} super utilisateur(s) trouvé(s) :\n")
    
    for i, user in enumerate(super_users, 1):
        print(f"👤 SUPER UTILISATEUR #{i}")
        print("-" * 40)
        print(f"🆔 ID : {user.id}")
        print(f"👤 Nom d'utilisateur : {user.username}")
        print(f"📧 Email : {user.email if user.email else 'Non défini'}")
        print(f"📝 Prénom : {user.first_name if user.first_name else 'Non défini'}")
        print(f"📝 Nom : {user.last_name if user.last_name else 'Non défini'}")
        print(f"✅ Actif : {'Oui' if user.is_active else 'Non'}")
        print(f"🔐 Super utilisateur : {'Oui' if user.is_superuser else 'Non'}")
        print(f"👨‍💼 Staff : {'Oui' if user.is_staff else 'Non'}")
        print(f"📅 Dernière connexion : {user.last_login if user.last_login else 'Jamais'}")
        print(f"📅 Date d'inscription : {user.date_joined}")
        print("-" * 40)
        print()
    
    print("=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print(f"Total des utilisateurs dans la base : {User.objects.count()}")
    print(f"Super utilisateurs : {super_users.count()}")
    print(f"Utilisateurs staff : {User.objects.filter(is_staff=True).count()}")
    print(f"Utilisateurs actifs : {User.objects.filter(is_active=True).count()}")

if __name__ == "__main__":
    try:
        afficher_super_users()
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution : {e}")
        sys.exit(1)

