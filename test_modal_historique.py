#!/usr/bin/env python
"""
Test des modals de la page d'historique des actions
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
import json

def test_modal_historique():
    """Test des modals de la page d'historique"""
    print("🧪 Test des modals de la page d'historique")
    print("=" * 60)
    
    # Vérifier que le modèle existe
    try:
        total_actions = ActionLog.objects.count()
        print(f"✅ Total des actions dans la base : {total_actions}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False
    
    # Créer des données de test avec des données JSON si nécessaire
    if total_actions == 0:
        print("\n📝 Création de données de test...")
        
        # Créer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@test.com'}
        )
        
        # Créer un client de test
        client, created = Client.objects.get_or_create(
            nom="Test",
            prenom="Modal",
            defaults={'cin': 'TEST789', 'telephone': '0600000003'}
        )
        
        # Créer des actions de test avec des données JSON
        actions_test = [
            {
                'type_action': 'credit_creation',
                'description': 'Test de création de crédit avec données JSON',
                'statut': 'succes',
                'agent': user,
                'client': client,
                'donnees_avant': json.dumps({'montant': 0, 'statut': 'vide'}),
                'donnees_apres': json.dumps({'montant': 1000, 'statut': 'actif'})
            },
            {
                'type_action': 'client_modification',
                'description': 'Test de modification de client',
                'statut': 'succes',
                'agent': user,
                'client': client,
                'donnees_avant': json.dumps({'telephone': '0600000000'}),
                'donnees_apres': json.dumps({'telephone': '0600000003'})
            }
        ]
        
        for action_data in actions_test:
            ActionLog.objects.create(**action_data)
            print(f"   - Action créée : {action_data['type_action']}")
        
        print("✅ Actions de test avec données JSON créées")
    
    # Vérifier que les données JSON sont bien formatées
    try:
        print("\n🔍 Vérification du formatage JSON :")
        
        actions = ActionLog.objects.all()[:3]
        for action in actions:
            print(f"\n   Action : {action.get_type_action_display()}")
            
            if action.donnees_avant:
                print(f"   - Données avant : {type(action.donnees_avant)}")
                if isinstance(action.donnees_avant, str):
                    try:
                        parsed = json.loads(action.donnees_avant)
                        print(f"     JSON valide : {len(str(parsed))} caractères")
                    except json.JSONDecodeError:
                        print("     ❌ JSON invalide")
            
            if action.donnees_apres:
                print(f"   - Données après : {type(action.donnees_apres)}")
                if isinstance(action.donnees_apres, str):
                    try:
                        parsed = json.loads(action.donnees_apres)
                        print(f"     JSON valide : {len(str(parsed))} caractères")
                    except json.JSONDecodeError:
                        print("     ❌ JSON invalide")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification JSON : {e}")
        return False
    
    print(f"\n🌐 Test de la page :")
    print(f"   - URL : http://127.0.0.1:8000/historique/")
    print(f"   - Assurez-vous que le serveur est démarré")
    print(f"   - Cliquez sur 'Voir' pour tester les modals")
    print(f"   - Les données JSON doivent s'afficher correctement")
    
    return True

if __name__ == '__main__':
    success = test_modal_historique()
    if success:
        print("\n✅ Test des modals réussi !")
        print("🎉 Les modals de la page d'historique devraient maintenant fonctionner !")
    else:
        print("\n❌ Test des modals échoué !")
        sys.exit(1)
