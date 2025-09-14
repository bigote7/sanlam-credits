#!/usr/bin/env python
"""
Script pour créer un crédit de 12 000 DH pour Hiba Layachi
divisé en 3 parties avec chèques de garantie
"""

import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Client, Credit, Echeance, Cheque, Alerte
from django.contrib.auth.models import User

def create_credit_hiba():
    """Créer le crédit pour Hiba Layachi selon les spécifications"""
    
    print("🏗️  Création du crédit pour Hiba Layachi...")
    
    # Vérifier si l'utilisateur agent existe
    try:
        agent = User.objects.get(username='agent_sanlam')
    except User.DoesNotExist:
        print("❌ Utilisateur 'agent_sanlam' non trouvé. Création...")
        agent = User.objects.create_user(
            username='agent_sanlam',
            email='agent@sanlam.ma',
            password='sanlam123',
            first_name='Agent',
            last_name='Sanlam'
        )
        print("✅ Utilisateur 'agent_sanlam' créé")
    
    # Vérifier si le client Hiba Layachi existe
    try:
        client = Client.objects.get(cin='Z363524')
        print(f"✅ Client existant trouvé : {client.nom_complet}")
    except Client.DoesNotExist:
        print("❌ Client Hiba Layachi non trouvé. Création...")
        client = Client.objects.create(
            nom='Layachi',
            prenom='Hiba',
            cin='Z363524',
            telephone='+212612345678',
            email='hiba.layachi@email.com',
            adresse='123 Rue Hassan II, Casablanca'
        )
        print(f"✅ Client créé : {client.nom_complet}")
    
    # Créer le crédit de 12 000 DH divisé en 3 parties
    credit = Credit.objects.create(
        client=client,
        type_credit='divise',
        montant_total=12000.00,
        description='Crédit personnel divisé en 3 parties avec chèques de garantie',
        agent=agent
    )
    print(f"✅ Crédit créé : {credit.montant_total} DH divisé en 3 parties")
    
    # Supprimer les échéances existantes si elles existent
    credit.echeances.all().delete()
    
    # Créer les 3 échéances
    echeances_data = [
        {
            'numero_partie': 1,
            'montant': 4000.00,
            'date_echeance': date.today() + timedelta(days=30),
            'est_especes': True,
            'description': 'Paiement initial en espèces'
        },
        {
            'numero_partie': 2,
            'montant': 4000.00,
            'date_echeance': date.today() + timedelta(days=60),
            'est_especes': False,
            'description': 'Chèque de garantie'
        },
        {
            'numero_partie': 3,
            'montant': 4000.00,
            'date_echeance': date.today() + timedelta(days=90),
            'est_especes': False,
            'description': 'Chèque de garantie'
        }
    ]
    
    for echeance_data in echeances_data:
        echeance = Echeance.objects.create(
            credit=credit,
            numero_partie=echeance_data['numero_partie'],
            montant=echeance_data['montant'],
            date_echeance=echeance_data['date_echeance'],
            est_especes=echeance_data['est_especes'],
            commentaire=echeance_data['description']
        )
        
        # Créer l'alerte pour l'échéance
        Alerte.objects.create(
            echeance=echeance,
            type_alerte='echeance',
            message=f'Échéance {echeance.numero_partie} pour {client.nom_complet} - {echeance_data["description"]}',
            date_alerte=date.today(),
            date_rappel=echeance.date_rappel,
            agent=agent
        )
        
        # Si ce n'est pas en espèces, créer un chèque de garantie
        if not echeance_data['est_especes']:
            cheque = Cheque.objects.create(
                echeance=echeance,
                numero_cheque=f'CHQ-{credit.id}-{echeance.numero_partie}',
                banque='Banque Populaire',
                date_emission=date.today(),
                date_reglement_prevu=echeance_data['date_echeance'],
                statut='garantie',
                montant=echeance_data['montant'],
                remarques=f'Chèque de garantie pour la partie {echeance.numero_partie} - {echeance_data["description"]}'
            )
            
            # Créer une alerte spécifique pour le chèque de garantie
            Alerte.objects.create(
                echeance=echeance,
                type_alerte='cheque_garantie',
                message=f'Contacter {client.nom_complet} pour règlement du chèque de garantie (Partie {echeance.numero_partie})',
                date_alerte=date.today(),
                date_rappel=echeance_data['date_echeance'],
                agent=agent
            )
            
            print(f"✅ Chèque de garantie créé : {cheque.numero_cheque} - {cheque.montant} DH")
        
        print(f"✅ Échéance {echeance.numero_partie} créée : {echeance.montant} DH - {echeance_data['date_echeance']} - {'Espèces' if echeance_data['est_especes'] else 'Chèque'}")
    
    print("\n🎉 Crédit créé avec succès !")
    print(f"📊 Résumé :")
    print(f"   • Client : {client.nom_complet}")
    print(f"   • Montant total : {credit.montant_total} DH")
    print(f"   • Type : Crédit divisé en 3 parties")
    print(f"   • Partie 1 : 4 000 DH en espèces ({echeances_data[0]['date_echeance']})")
    print(f"   • Partie 2 : 4 000 DH par chèque de garantie ({echeances_data[1]['date_echeance']})")
    print(f"   • Partie 3 : 4 000 DH par chèque de garantie ({echeances_data[2]['date_echeance']})")
    print(f"\n🔗 URL du crédit : http://127.0.0.1:8000/credits/{credit.pk}/")
    print(f"🔑 Connexion : agent_sanlam / sanlam123")

if __name__ == '__main__':
    create_credit_hiba()
