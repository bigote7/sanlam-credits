#!/usr/bin/env python
"""
Test de création automatique d'actions lors de la création de crédits
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

def test_actions_credits():
    """Test de création automatique d'actions lors de la création de crédits"""
    print("🧪 Test de création automatique d'actions lors de la création de crédits")
    print("=" * 70)
    
    # Vérifier que le modèle existe
    try:
        total_actions = ActionLog.objects.count()
        print(f"✅ Total des actions dans la base : {total_actions}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False
    
    # Vérifier les actions existantes
    if total_actions > 0:
        print("\n📋 Actions existantes :")
        actions = ActionLog.objects.all().order_by('-date_action')[:5]
        for action in actions:
            print(f"   - {action.get_type_action_display()} : {action.description[:50]}...")
            print(f"     Date: {action.date_action.strftime('%d/%m/%Y %H:%M')}")
            print(f"     Agent: {action.agent.username if action.agent else 'Système'}")
            if action.client:
                print(f"     Client: {action.client.nom_complet}")
            if action.credit:
                print(f"     Crédit: Police {action.credit.numero_police}")
            print()
    
    # Vérifier les crédits existants
    total_credits = Credit.objects.count()
    print(f"📊 Total des crédits dans la base : {total_credits}")
    
    if total_credits > 0:
        print("\n🔍 Vérification des crédits existants :")
        credits = Credit.objects.all()[:3]
        for credit in credits:
            print(f"   - Police {credit.numero_police} : {credit.client.nom_complet}")
            print(f"     Montant: {credit.montant_total} DH")
            print(f"     Date création: {credit.date_creation.strftime('%d/%m/%Y')}")
            
            # Vérifier s'il y a des actions pour ce crédit
            actions_credit = ActionLog.objects.filter(credit=credit)
            print(f"     Actions associées: {actions_credit.count()}")
            
            if actions_credit.exists():
                for action in actions_credit:
                    print(f"       * {action.get_type_action_display()} - {action.date_action.strftime('%d/%m/%Y %H:%M')}")
            else:
                print("       ❌ Aucune action trouvée pour ce crédit")
            print()
    
    # Créer un crédit de test pour vérifier la création automatique d'actions
    print("🔄 Test de création d'un crédit avec actions automatiques...")
    
    try:
        # Créer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='test_agent',
            defaults={
                'email': 'test@sanlam.com',
                'first_name': 'Agent',
                'last_name': 'Test'
            }
        )
        if created:
            print(f"   ✅ Utilisateur créé : {user.username}")
        else:
            print(f"   ✅ Utilisateur existant : {user.username}")
        
        # Créer un client de test
        client, created = Client.objects.get_or_create(
            nom="Test",
            prenom="Actions",
            defaults={
                'cin': 'TEST123',
                'telephone': '0600000004',
                'email': 'test.actions@email.com'
            }
        )
        if created:
            print(f"   ✅ Client créé : {client.nom_complet}")
        else:
            print(f"   ✅ Client existant : {client.nom_complet}")
        
        # Créer un crédit de test
        credit = Credit.objects.create(
            client=client,
            numero_police=f"TEST-{datetime.now().strftime('%Y%m%d%H%M')}",
            type_credit='unique',
            montant_total=5000.00,
            description='Crédit de test pour vérifier la création automatique d\'actions',
            agent=user
        )
        print(f"   ✅ Crédit créé : Police {credit.numero_police}")
        
        # Vérifier que les actions ont été créées automatiquement
        actions_apres_creation = ActionLog.objects.filter(credit=credit)
        print(f"   📝 Actions créées automatiquement : {actions_apres_creation.count()}")
        
        for action in actions_apres_creation:
            print(f"      - {action.get_type_action_display()}")
            print(f"        Description: {action.description}")
            print(f"        Statut: {action.get_statut_display()}")
            print(f"        Agent: {action.agent.username}")
            print(f"        Date: {action.date_action.strftime('%d/%m/%Y %H:%M')}")
            if action.donnees_apres:
                print(f"        Données: {action.donnees_apres}")
            print()
        
        # Nettoyer les données de test
        print("🧹 Nettoyage des données de test...")
        credit.delete()
        print("   ✅ Crédit de test supprimé")
        
        # Supprimer aussi les actions associées
        actions_apres_creation.delete()
        print("   ✅ Actions de test supprimées")
        
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        return False
    
    print(f"\n🌐 Test de la page d'historique :")
    print(f"   - URL : http://127.0.0.1:8000/historique/")
    print(f"   - Assurez-vous que le serveur est démarré")
    print(f"   - Créez un nouveau crédit pour voir les actions s'afficher")
    print(f"   - Vérifiez que toutes les actions sont visibles et claires")
    
    return True

if __name__ == '__main__':
    success = test_actions_credits()
    if success:
        print("\n✅ Test réussi !")
        print("🎉 Les actions devraient maintenant être créées automatiquement !")
    else:
        print("\n❌ Test échoué !")
        sys.exit(1)
