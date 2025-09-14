#!/usr/bin/env python
"""
Script pour migrer les données de SQLite vers MySQL
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from django.contrib.auth.models import User
from gestion_credits.models import Client, Credit, Reglement, ChequeGarantie, Alerte

def migrate_to_mysql():
    print("🔄 Migration vers MySQL en cours...")
    
    try:
        # 1. Créer les tables dans MySQL
        print("📋 Création des tables dans MySQL...")
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate'])
        
        # 2. Créer un superutilisateur
        print("👤 Création du superutilisateur...")
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@sanlam.ma',
                password='admin123',
                first_name='Admin',
                last_name='Sanlam'
            )
            print("✅ Superutilisateur créé: admin/admin123")
        else:
            print("✅ Superutilisateur existe déjà")
        
        # 3. Créer un utilisateur agent
        print("👤 Création de l'utilisateur agent...")
        if not User.objects.filter(username='agent').exists():
            User.objects.create_user(
                username='agent',
                email='agent@sanlam.ma',
                password='password123',
                first_name='Agent',
                last_name='Test',
                is_staff=True,
                is_active=True
            )
            print("✅ Utilisateur agent créé: agent/password123")
        else:
            print("✅ Utilisateur agent existe déjà")
        
        # 4. Créer des données de test
        print("📊 Création des données de test...")
        
        # Clients
        clients_data = [
            {
                'nom': 'Alaoui',
                'prenom': 'Ahmed',
                'cin': 'AB123456',
                'telephone': '0612345678',
                'email': 'ahmed.alaoui@email.com',
                'adresse': '123 Rue Mohammed V, Taza'
            },
            {
                'nom': 'Benali',
                'prenom': 'Fatima',
                'cin': 'CD789012',
                'telephone': '0623456789',
                'email': 'fatima.benali@email.com',
                'adresse': '456 Avenue Hassan II, Taza'
            },
            {
                'nom': 'Chraibi',
                'prenom': 'Omar',
                'cin': 'EF345678',
                'telephone': '0634567890',
                'email': 'omar.chraibi@email.com',
                'adresse': '789 Boulevard Mohammed VI, Taza'
            }
        ]
        
        clients = []
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                cin=client_data['cin'],
                defaults=client_data
            )
            if created:
                print(f"✅ Client créé: {client.nom_complet}")
            clients.append(client)
        
        # Crédits
        agent_user = User.objects.get(username='agent')
        credits_data = [
            {
                'client': clients[0],
                'numero_police': 'POL-2024-001',
                'type_credit': 'unique',
                'montant_total': Decimal('50000.00'),
                'description': 'Crédit unique pour achat véhicule'
            },
            {
                'client': clients[1],
                'numero_police': 'POL-2024-002',
                'type_credit': 'divise',
                'montant_total': Decimal('75000.00'),
                'description': 'Crédit divisé pour travaux maison'
            },
            {
                'client': clients[2],
                'numero_police': 'POL-2024-003',
                'type_credit': 'unique',
                'montant_total': Decimal('30000.00'),
                'description': 'Crédit unique pour équipement'
            }
        ]
        
        credits = []
        for credit_data in credits_data:
            credit, created = Credit.objects.get_or_create(
                numero_police=credit_data['numero_police'],
                defaults={
                    **credit_data,
                    'agent': agent_user,
                    'reste_a_payer': credit_data['montant_total']
                }
            )
            if created:
                print(f"✅ Crédit créé: {credit.numero_police}")
            credits.append(credit)
        
        # Règlements
        reglements_data = [
            {
                'credit': credits[0],
                'montant': Decimal('20000.00'),
                'date_reglement': date.today(),
                'mode_paiement': 'especes',
                'statut': None,
                'commentaire': 'Paiement initial en espèces'
            },
            {
                'credit': credits[0],
                'montant': Decimal('30000.00'),
                'date_reglement': date.today() - timedelta(days=5),
                'mode_paiement': 'cheque',
                'statut': 'verse',
                'commentaire': 'Chèque encaissé'
            },
            {
                'credit': credits[1],
                'montant': Decimal('25000.00'),
                'date_reglement': date.today(),
                'mode_paiement': 'especes',
                'statut': None,
                'commentaire': 'Premier paiement'
            },
            {
                'credit': credits[1],
                'montant': Decimal('25000.00'),
                'date_reglement': date.today() - timedelta(days=3),
                'mode_paiement': 'cheque',
                'statut': 'non_verse',
                'commentaire': 'Chèque en attente'
            },
            {
                'credit': credits[2],
                'montant': Decimal('30000.00'),
                'date_reglement': date.today() - timedelta(days=10),
                'mode_paiement': 'especes',
                'statut': None,
                'commentaire': 'Paiement complet'
            }
        ]
        
        for reglement_data in reglements_data:
            reglement, created = Reglement.objects.get_or_create(
                credit=reglement_data['credit'],
                montant=reglement_data['montant'],
                date_reglement=reglement_data['date_reglement'],
                defaults={
                    **reglement_data,
                    'agent': agent_user
                }
            )
            if created:
                print(f"✅ Règlement créé: {reglement.montant} DH")
        
        # Chèques de garantie
        cheques_data = [
            {
                'credit': credits[0],
                'numero': 'CHQ-001',
                'montant': Decimal('50000.00'),
                'banque': 'Attijariwafa Bank',
                'date_emission': date.today() - timedelta(days=30),
                'date_echeance': date.today() + timedelta(days=5),
                'commentaire': 'Chèque de garantie principal'
            },
            {
                'credit': credits[1],
                'numero': 'CHQ-002',
                'montant': Decimal('50000.00'),
                'banque': 'BMCE Bank',
                'date_emission': date.today() - timedelta(days=15),
                'date_echeance': date.today() + timedelta(days=2),
                'commentaire': 'Chèque de garantie divisé'
            },
            {
                'credit': credits[1],
                'numero': 'CHQ-003',
                'montant': Decimal('25000.00'),
                'banque': 'Crédit du Maroc',
                'date_emission': date.today() - timedelta(days=10),
                'date_echeance': date.today() - timedelta(days=2),
                'commentaire': 'Chèque en retard'
            }
        ]
        
        for cheque_data in cheques_data:
            cheque, created = ChequeGarantie.objects.get_or_create(
                credit=cheque_data['credit'],
                numero=cheque_data['numero'],
                defaults=cheque_data
            )
            if created:
                print(f"✅ Chèque créé: {cheque.numero}")
        
        # Alertes
        alertes_data = [
            {
                'echeance': None,
                'type_alerte': 'cheque_garantie',
                'message': 'Chèque CHQ-001 à échéance dans 5 jours',
                'date_alerte': date.today(),
                'date_rappel': date.today() + timedelta(days=5),
                'agent': agent_user
            },
            {
                'echeance': None,
                'type_alerte': 'cheque_garantie',
                'message': 'Chèque CHQ-002 à échéance dans 2 jours',
                'date_alerte': date.today(),
                'date_rappel': date.today() + timedelta(days=2),
                'agent': agent_user
            },
            {
                'echeance': None,
                'type_alerte': 'cheque_garantie',
                'message': 'Chèque CHQ-003 en retard de 2 jours',
                'date_alerte': date.today(),
                'date_rappel': date.today() - timedelta(days=2),
                'agent': agent_user
            }
        ]
        
        for alerte_data in alertes_data:
            alerte, created = Alerte.objects.get_or_create(
                message=alerte_data['message'],
                date_alerte=alerte_data['date_alerte'],
                defaults=alerte_data
            )
            if created:
                print(f"✅ Alerte créée: {alerte.message}")
        
        print("\n🎉 Migration vers MySQL terminée avec succès !")
        print("\n📊 Résumé des données migrées :")
        print(f"- Utilisateurs: {User.objects.count()}")
        print(f"- Clients: {Client.objects.count()}")
        print(f"- Crédits: {Credit.objects.count()}")
        print(f"- Règlements: {Reglement.objects.count()}")
        print(f"- Chèques de garantie: {ChequeGarantie.objects.count()}")
        print(f"- Alertes: {Alerte.objects.count()}")
        
        print("\n🔑 Comptes de connexion :")
        print("Administrateur: admin/admin123")
        print("Agent: agent/password123")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {str(e)}")
        print("Vérifiez que MySQL est démarré et que la base de données 'sanlam_credits_db' existe.")

if __name__ == '__main__':
    migrate_to_mysql()
