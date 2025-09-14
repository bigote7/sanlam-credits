#!/usr/bin/env python
"""
Script pour créer des données d'exemple pour l'application Sanlam Crédits
Inclut l'exemple des 4 parties avec 3 chèques de garantie
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
from gestion_credits.models import Client, Credit, Echeance, Cheque, Alerte

def create_sample_data():
    """Créer des données d'exemple"""
    print("Création des données d'exemple...")
    
    # Créer un utilisateur agent si il n'existe pas
    agent, created = User.objects.get_or_create(
        username='agent_sanlam',
        defaults={
            'first_name': 'Agent',
            'last_name': 'Sanlam',
            'email': 'agent@sanlam.ma',
            'is_staff': True
        }
    )
    if created:
        agent.set_password('sanlam123')
        agent.save()
        print(f"Utilisateur agent créé: {agent.username}")
    
    # Créer des clients d'exemple
    clients_data = [
        {
            'nom': 'Alaoui',
            'prenom': 'Ahmed',
            'cin': 'AB123456',
            'telephone': '0612345678',
            'email': 'ahmed.alaoui@email.com',
            'adresse': '123 Rue Hassan II, Casablanca'
        },
        {
            'nom': 'Benjelloun',
            'prenom': 'Fatima',
            'cin': 'CD789012',
            'telephone': '0623456789',
            'email': 'fatima.benjelloun@email.com',
            'adresse': '456 Avenue Mohammed V, Rabat'
        },
        {
            'nom': 'Tazi',
            'prenom': 'Karim',
            'cin': 'EF345678',
            'telephone': '0634567890',
            'email': 'karim.tazi@email.com',
            'adresse': '789 Boulevard Al Massira, Marrakech'
        }
    ]
    
    clients = []
    for client_data in clients_data:
        client, created = Client.objects.get_or_create(
            cin=client_data['cin'],
            defaults=client_data
        )
        if created:
            print(f"Client créé: {client.nom_complet}")
        clients.append(client)
    
    # Créer l'exemple principal : crédit divisé en 4 parties (12 000 DH)
    print("\nCréation de l'exemple principal : crédit divisé en 4 parties...")
    
    credit_principal = Credit.objects.create(
        client=clients[0],  # Ahmed Alaoui
        type_credit='divise',
        montant_total=Decimal('12000.00'),
        description='Crédit immobilier pour achat appartement',
        agent=agent
    )
    print(f"Crédit principal créé: {credit_principal}")
    
    # Créer les 4 échéances
    echeances_data = [
        {
            'numero_partie': 1,
            'montant': Decimal('3000.00'),
            'date_echeance': date(2025, 1, 1),
            'est_especes': True,
            'commentaire': 'Première partie en espèces'
        },
        {
            'numero_partie': 2,
            'montant': Decimal('3000.00'),
            'date_echeance': date(2025, 4, 1),
            'est_especes': False,
            'commentaire': 'Chèque de garantie - non encaissé'
        },
        {
            'numero_partie': 3,
            'montant': Decimal('3000.00'),
            'date_echeance': date(2025, 7, 1),
            'est_especes': False,
            'commentaire': 'Chèque de garantie'
        },
        {
            'numero_partie': 4,
            'montant': Decimal('3000.00'),
            'date_echeance': date(2025, 10, 1),
            'est_especes': False,
            'commentaire': 'Chèque de garantie'
        }
    ]
    
    for echeance_data in echeances_data:
        echeance = Echeance.objects.create(
            credit=credit_principal,
            **echeance_data
        )
        
        # Créer l'alerte pour chaque échéance
        Alerte.objects.create(
            echeance=echeance,
            type_alerte='echeance',
            message=f'Échéance {echeance.numero_partie} pour {echeance.credit.client.nom_complet}',
            date_alerte=date.today(),
            date_rappel=echeance.date_rappel,
            agent=agent
        )
        
        # Si ce n'est pas en espèces, créer un chèque de garantie
        if not echeance.est_especes:
            Cheque.objects.create(
                echeance=echeance,
                numero_cheque=f'CHQ-{credit_principal.id}-{echeance.numero_partie}',
                banque='Banque Populaire',
                date_emission=date.today(),
                montant=echeance.montant
            )
            
            # Pour la partie 2 (non encaissée), créer une alerte spéciale
            if echeance.numero_partie == 2:
                Alerte.objects.create(
                    echeance=echeance,
                    type_alerte='rappel',
                    message=f'Appeler {echeance.credit.client.nom_complet} pour paiement en espèces (chèque non encaissé)',
                    date_alerte=date.today(),
                    date_rappel=date(2025, 4, 1),
                    agent=agent
                )
        
        print(f"Échéance {echeance.numero_partie} créée: {echeance.montant} DH - {echeance.date_echeance}")
    
    # Créer des crédits uniques d'exemple
    print("\nCréation de crédits uniques d'exemple...")
    
    credit_unique_1 = Credit.objects.create(
        client=clients[1],  # Fatima Benjelloun
        type_credit='unique',
        montant_total=Decimal('5000.00'),
        description='Crédit personnel - 3 mois',
        duree_mois=3,
        agent=agent
    )
    
    # Créer l'échéance pour le crédit unique
    echeance_unique = Echeance.objects.create(
        credit=credit_unique_1,
        numero_partie=1,
        montant=Decimal('5000.00'),
        date_echeance=credit_unique_1.date_echeance,
        est_especes=True,
        commentaire='Crédit unique - paiement en espèces'
    )
    
    # Créer l'alerte
    Alerte.objects.create(
        echeance=echeance_unique,
        type_alerte='echeance',
        message=f'Échéance de paiement pour {credit_unique_1.client.nom_complet}',
        date_alerte=date.today(),
        date_rappel=echeance_unique.date_rappel,
        agent=agent
    )
    
    print(f"Crédit unique créé: {credit_unique_1} - Échéance: {credit_unique_1.date_echeance}")
    
    # Créer un crédit avec date exacte
    credit_unique_2 = Credit.objects.create(
        client=clients[2],  # Karim Tazi
        type_credit='unique',
        montant_total=Decimal('8000.00'),
        description='Crédit voiture - date exacte',
        date_echeance=date(2025, 6, 15),
        agent=agent
    )
    
    # Créer l'échéance
    echeance_unique_2 = Echeance.objects.create(
        credit=credit_unique_2,
        numero_partie=1,
        montant=Decimal('8000.00'),
        date_echeance=credit_unique_2.date_echeance,
        est_especes=True,
        commentaire='Crédit voiture - paiement en espèces'
    )
    
    # Créer l'alerte
    Alerte.objects.create(
        echeance=echeance_unique_2,
        type_alerte='echeance',
        message=f'Échéance de paiement pour {credit_unique_2.client.nom_complet}',
        date_alerte=date.today(),
        date_rappel=echeance_unique_2.date_rappel,
        agent=agent
    )
    
    print(f"Crédit avec date exacte créé: {credit_unique_2} - Échéance: {credit_unique_2.date_echeance}")
    
    # Créer quelques échéances en retard pour tester
    print("\nCréation d'échéances en retard pour test...")
    
    echeance_retard = Echeance.objects.create(
        credit=credit_principal,
        numero_partie=5,
        montant=Decimal('1500.00'),
        date_echeance=date.today() - timedelta(days=5),
        est_especes=False,
        commentaire='Échéance en retard pour test'
    )
    
    # Créer l'alerte de retard
    Alerte.objects.create(
        echeance=echeance_retard,
        type_alerte='retard',
        message=f'PAIEMENT EN RETARD pour {echeance_retard.credit.client.nom_complet}',
        date_alerte=date.today(),
        date_rappel=date.today(),
        agent=agent
    )
    
    print(f"Échéance en retard créée: {echeance_retard}")
    
    print("\n" + "="*50)
    print("DONNÉES D'EXEMPLE CRÉÉES AVEC SUCCÈS!")
    print("="*50)
    print(f"Utilisateur: {agent.username} / Mot de passe: sanlam123")
    print(f"Clients créés: {len(clients)}")
    print(f"Crédits créés: {Credit.objects.count()}")
    print(f"Échéances créées: {Echeance.objects.count()}")
    print(f"Chèques créés: {Cheque.objects.count()}")
    print(f"Alertes créées: {Alerte.objects.count()}")
    print("\nExemple principal créé:")
    print("- Client: Ahmed Alaoui")
    print("- Crédit: 12 000 DH divisé en 4 parties")
    print("- Partie 1: 3 000 DH en espèces (01/01/2025)")
    print("- Partie 2: 3 000 DH chèque garantie (01/04/2025) - non encaissé")
    print("- Partie 3: 3 000 DH chèque garantie (01/07/2025)")
    print("- Partie 4: 3 000 DH chèque garantie (01/10/2025)")
    print("\nVous pouvez maintenant vous connecter et tester l'application!")

if __name__ == '__main__':
    create_sample_data()
