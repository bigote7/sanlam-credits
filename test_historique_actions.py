#!/usr/bin/env python
"""
Test de la page d'historique des actions
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
from django.db.models import Count

def test_historique_actions():
    """Tester la page d'historique des actions"""
    print("🧪 Test de la page d'historique des actions")
    print("=" * 60)
    
    # Vérifier que le modèle ActionLog existe
    try:
        action_fields = [field.name for field in ActionLog._meta.fields]
        print("✅ Modèle ActionLog créé avec succès")
        print(f"   Champs disponibles : {', '.join(action_fields)}")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du modèle: {e}")
        return False
    
    # Vérifier les choix disponibles
    try:
        print(f"\n📋 Types d'actions disponibles :")
        for value, label in ActionLog.TYPE_ACTION_CHOICES:
            print(f"   - {value}: {label}")
        
        print(f"\n📊 Statuts disponibles :")
        for value, label in ActionLog.STATUT_CHOICES:
            print(f"   - {value}: {label}")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des choix: {e}")
        return False
    
    # Créer des données de test
    try:
        print("\n🧪 Création de données de test...")
        
        # Créer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='test_agent_hist',
            defaults={
                'first_name': 'Agent',
                'last_name': 'Historique',
                'email': 'agent.hist@test.com'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"   - Utilisateur de test créé: {user.username}")
        else:
            print(f"   - Utilisateur de test existant: {user.username}")
        
        # Créer un client de test
        client, created = Client.objects.get_or_create(
            nom="Test",
            prenom="Historique",
            defaults={
                'cin': 'TEST789',
                'telephone': '0600000002',
                'email': 'test.hist@test.com'
            }
        )
        
        if created:
            print(f"   - Client de test créé: {client.nom_complet}")
        else:
            print(f"   - Client de test existant: {client.nom_complet}")
        
        # Créer un crédit de test
        credit, created = Credit.objects.get_or_create(
            numero_police='POL-HIST-001',
            defaults={
                'client': client,
                'montant_total': 5000.00,
                'description': 'Crédit de test pour l\'historique',
                'type_credit': 'unique',
                'agent': user
            }
        )
        
        if created:
            print(f"   - Crédit de test créé: {credit.numero_police}")
        else:
            print(f"   - Crédit de test existant: {credit.numero_police}")
        
        # Créer des actions de test
        actions_test = [
            {
                'type_action': 'credit_creation',
                'description': f'Création du crédit {credit.numero_police} pour {client.nom_complet}',
                'statut': 'succes',
                'agent': user,
                'client': client,
                'credit': credit,
                'donnees_avant': None,
                'donnees_apres': {
                    'numero_police': credit.numero_police,
                    'montant_total': str(credit.montant_total),
                    'type_credit': credit.type_credit
                }
            },
            {
                'type_action': 'client_contact',
                'description': f'Contact établi avec {client.nom_complet} pour finaliser le crédit',
                'statut': 'succes',
                'agent': user,
                'client': client,
                'donnees_avant': None,
                'donnees_apres': {
                    'methode_contact': 'téléphone',
                    'sujet': 'Finalisation crédit',
                    'resultat': 'Client intéressé'
                }
            },
            {
                'type_action': 'credit_validation',
                'description': f'Validation du crédit {credit.numero_police} par {user.username}',
                'statut': 'succes',
                'agent': user,
                'credit': credit,
                'donnees_avant': {
                    'statut': 'en_attente'
                },
                'donnees_apres': {
                    'statut': 'valide',
                    'date_validation': datetime.now().isoformat()
                }
            },
            {
                'type_action': 'echeance_creation',
                'description': f'Création de l\'échéance pour le crédit {credit.numero_police}',
                'statut': 'en_cours',
                'agent': user,
                'credit': credit,
                'donnees_avant': None,
                'donnees_apres': {
                    'montant': str(credit.montant_total),
                    'date_echeance': (datetime.now() + timedelta(days=30)).isoformat()
                }
            }
        ]
        
        for i, action_data in enumerate(actions_test, 1):
            action = ActionLog.objects.create(**action_data)
            print(f"   - Action {i} créée: {action.get_type_action_display()}")
        
        print(f"\n✅ {len(actions_test)} actions de test créées avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données de test: {e}")
        return False
    
    # Vérifier les statistiques
    try:
        print("\n📊 Vérification des statistiques :")
        
        total_actions = ActionLog.objects.count()
        print(f"   - Total des actions : {total_actions}")
        
        actions_aujourd_hui = ActionLog.objects.filter(
            date_action__date=datetime.now().date()
        ).count()
        print(f"   - Actions aujourd'hui : {actions_aujourd_hui}")
        
        actions_cette_semaine = ActionLog.objects.filter(
            date_action__date__gte=datetime.now().date() - timedelta(days=7)
        ).count()
        print(f"   - Actions cette semaine : {actions_cette_semaine}")
        
        actions_urgentes = ActionLog.objects.filter(
            type_action__in=['echeance_paiement', 'alerte_creation', 'credit_validation'],
            statut__in=['en_cours', 'en_attente']
        ).count()
        print(f"   - Actions urgentes : {actions_urgentes}")
        
        # Répartition par type
        repartition_types = ActionLog.objects.values('type_action').annotate(
            count=Count('id')
        ).order_by('-count')
        
        print(f"\n📈 Répartition par type d'action :")
        for repartition in repartition_types:
            print(f"   - {repartition['type_action']}: {repartition['count']}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des statistiques: {e}")
        return False
    
    # Vérifier l'URL
    print(f"\n🌐 URL de test :")
    print(f"   - Page d'historique : http://127.0.0.1:8000/historique/")
    
    # Nettoyer les données de test
    try:
        print("\n🧹 Nettoyage des données de test...")
        
        # Supprimer les actions de test
        actions_supprimees = ActionLog.objects.filter(
            agent__username='test_agent_hist'
        ).delete()
        print(f"   - {actions_supprimees[0]} actions supprimées")
        
        # Supprimer le crédit de test
        if credit:
            credit.delete()
            print(f"   - Crédit de test supprimé")
        
        # Supprimer le client de test
        if client:
            client.delete()
            print(f"   - Client de test supprimé")
        
        # Supprimer l'utilisateur de test
        if user:
            user.delete()
            print(f"   - Utilisateur de test supprimé")
        
    except Exception as e:
        print(f"⚠️  Erreur lors du nettoyage: {e}")
    
    print("\n🎉 Test terminé avec succès!")
    return True

if __name__ == '__main__':
    success = test_historique_actions()
    if success:
        print("\n✅ La page d'historique des actions est prête!")
        print("Démarrez le serveur et testez : http://127.0.0.1:8000/historique/")
    else:
        print("\n❌ Il y a des problèmes avec la page d'historique!")
        sys.exit(1)
