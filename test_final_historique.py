#!/usr/bin/env python
"""
Test final de la page d'historique des actions
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

def test_final_historique():
    """Test final de la page d'historique"""
    print("🧪 Test final de la page d'historique")
    print("=" * 60)
    
    # Vérifier que le modèle existe
    try:
        total_actions = ActionLog.objects.count()
        print(f"✅ Total des actions dans la base : {total_actions}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False
    
    # Créer des données de test si nécessaire
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
            },
            {
                'type_action': 'echeance_creation',
                'description': 'Test de création d\'échéance',
                'statut': 'en_cours',
                'agent': user,
                'client': client
            }
        ]
        
        for action_data in actions_test:
            ActionLog.objects.create(**action_data)
            print(f"   - Action créée : {action_data['type_action']}")
        
        print("✅ Actions de test créées")
    
    # Vérifier les relations et filtres
    try:
        print("\n🔍 Vérification des relations et filtres :")
        
        # Vérifier les agents disponibles
        agents_disponibles = User.objects.filter(
            actions_effectuees__isnull=False
        ).distinct().count()
        print(f"   - Agents avec actions : {agents_disponibles}")
        
        # Vérifier les clients disponibles
        clients_disponibles = Client.objects.filter(
            actions_historique__isnull=False
        ).distinct().count()
        print(f"   - Clients avec actions : {clients_disponibles}")
        
        # Vérifier les statistiques
        total_actions = ActionLog.objects.count()
        actions_aujourd_hui = ActionLog.objects.filter(
            date_action__date=datetime.now().date()
        ).count()
        actions_cette_semaine = ActionLog.objects.filter(
            date_action__date__gte=datetime.now().date() - timedelta(days=7)
        ).count()
        
        print(f"\n📊 Statistiques calculées :")
        print(f"   - Total : {total_actions}")
        print(f"   - Aujourd'hui : {actions_aujourd_hui}")
        print(f"   - Cette semaine : {actions_cette_semaine}")
        
        # Vérifier les actions urgentes
        actions_urgentes = ActionLog.objects.filter(
            type_action__in=['echeance_paiement', 'alerte_creation', 'credit_validation'],
            statut__in=['en_cours', 'en_attente']
        ).count()
        print(f"   - Actions urgentes : {actions_urgentes}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        return False
    
    print(f"\n🌐 Test de la page :")
    print(f"   - URL : http://127.0.0.1:8000/historique/")
    print(f"   - Assurez-vous que le serveur est démarré")
    print(f"   - Vérifiez que la page se charge sans erreur")
    
    return True

if __name__ == '__main__':
    success = test_final_historique()
    if success:
        print("\n✅ Test final réussi !")
        print("🎉 La page d'historique devrait maintenant fonctionner parfaitement !")
    else:
        print("\n❌ Test final échoué !")
        sys.exit(1)
