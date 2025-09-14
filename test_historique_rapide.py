#!/usr/bin/env python
"""
Test rapide de la page d'historique des actions
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import ActionLog, Credit, Client
from django.contrib.auth.models import User
from datetime import datetime, timedelta

def test_historique_rapide():
    """Test rapide de la page d'historique"""
    print("🧪 Test rapide de la page d'historique")
    print("=" * 50)
    
    # Vérifier que le modèle existe
    try:
        total_actions = ActionLog.objects.count()
        print(f"✅ Total des actions dans la base : {total_actions}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False
    
    # Créer quelques actions de test si aucune n'existe
    if total_actions == 0:
        print("\n📝 Création d'actions de test...")
        
        # Créer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@test.com'}
        )
        
        # Créer un client de test
        client, created = Client.objects.get_or_create(
            nom="Test",
            prenom="Historique",
            defaults={'cin': 'TEST789', 'telephone': '0600000002'}
        )
        
        # Créer des actions de test
        actions_test = [
            {
                'type_action': 'credit_creation',
                'description': 'Test de création de crédit',
                'statut': 'succes',
                'agent': user,
                'client': client
            },
            {
                'type_action': 'client_contact',
                'description': 'Test de contact client',
                'statut': 'succes',
                'agent': user,
                'client': client
            }
        ]
        
        for action_data in actions_test:
            ActionLog.objects.create(**action_data)
            print(f"   - Action créée : {action_data['type_action']}")
        
        print("✅ Actions de test créées")
    
    # Vérifier les statistiques
    try:
        total_actions = ActionLog.objects.count()
        actions_aujourd_hui = ActionLog.objects.filter(
            date_action__date=datetime.now().date()
        ).count()
        
        print(f"\n📊 Statistiques :")
        print(f"   - Total : {total_actions}")
        print(f"   - Aujourd'hui : {actions_aujourd_hui}")
        
        # Vérifier les agents disponibles
        agents_disponibles = User.objects.filter(
            actions_effectuees__isnull=False
        ).distinct().count()
        print(f"   - Agents avec actions : {agents_disponibles}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des statistiques : {e}")
        return False
    
    print(f"\n🌐 Test de la page :")
    print(f"   - URL : http://127.0.0.1:8000/historique/")
    print(f"   - Assurez-vous que le serveur est démarré")
    
    return True

if __name__ == '__main__':
    success = test_historique_rapide()
    if success:
        print("\n✅ Test rapide réussi !")
    else:
        print("\n❌ Test rapide échoué !")
        sys.exit(1)
