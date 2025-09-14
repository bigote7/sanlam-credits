#!/usr/bin/env python
"""
Script pour ajouter des actions aux crédits existants qui n'en ont pas
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import ActionLog, Credit, Client, Echeance, Alerte
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json

def ajouter_actions_existantes():
    """Ajouter des actions aux crédits existants qui n'en ont pas"""
    print("🔧 Ajout d'actions aux crédits existants")
    print("=" * 60)
    
    # Récupérer tous les crédits
    credits = Credit.objects.all()
    print(f"📊 Total des crédits trouvés : {credits.count()}")
    
    # Récupérer l'utilisateur admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"👤 Utilisateur admin trouvé : {admin_user.username}")
    except User.DoesNotExist:
        print("❌ Utilisateur admin non trouvé, création d'un utilisateur par défaut")
        admin_user = User.objects.first()
        if not admin_user:
            print("❌ Aucun utilisateur trouvé dans la base")
            return False
    
    actions_crees = 0
    
    for credit in credits:
        print(f"\n🔍 Traitement du crédit : Police {credit.numero_police}")
        
        # Vérifier s'il y a déjà des actions pour ce crédit
        actions_existantes = ActionLog.objects.filter(credit=credit)
        if actions_existantes.exists():
            print(f"   ✅ Actions déjà existantes : {actions_existantes.count()}")
            continue
        
        # Créer une action pour la création du crédit
        try:
            action_creation = ActionLog.objects.create(
                type_action='credit_creation',
                description=f'Crédit créé pour {credit.client.nom_complet} - Police {credit.numero_police} - Montant: {credit.montant_total} DH',
                statut='succes',
                agent=credit.agent if credit.agent else admin_user,
                client=credit.client,
                credit=credit,
                donnees_apres={
                    'numero_police': credit.numero_police,
                    'montant_total': str(credit.montant_total),
                    'type_credit': credit.type_credit,
                    'description': credit.description,
                    'client': credit.client.nom_complet,
                    'date_creation': credit.date_creation.strftime('%Y-%m-%d')
                }
            )
            print(f"   ✅ Action de création ajoutée")
            actions_crees += 1
            
            # Créer des actions pour les échéances
            echeances = credit.echeances.all()
            for echeance in echeances:
                action_echeance = ActionLog.objects.create(
                    type_action='echeance_creation',
                    description=f'Échéance {echeance.numero_partie} créée pour le crédit {credit.numero_police} - Montant: {echeance.montant} DH',
                    statut='succes',
                    agent=credit.agent if credit.agent else admin_user,
                    credit=credit,
                    echeance=echeance,
                    donnees_apres={
                        'numero_partie': echeance.numero_partie,
                        'montant': str(echeance.montant),
                        'date_echeance': str(echeance.date_echeance),
                        'est_especes': echeance.est_especes
                    }
                )
                print(f"   ✅ Action d'échéance {echeance.numero_partie} ajoutée")
                actions_crees += 1
            
            # Créer des actions pour les alertes
            alertes = Alerte.objects.filter(echeance__credit=credit)
            for alerte in alertes:
                action_alerte = ActionLog.objects.create(
                    type_action='alerte_creation',
                    description=f'Alerte créée pour {credit.client.nom_complet} - Type: {alerte.get_type_alerte_display()}',
                    statut='succes',
                    agent=credit.agent if credit.agent else admin_user,
                    credit=credit,
                    echeance=alerte.echeance,
                    donnees_apres={
                        'type_alerte': alerte.type_alerte,
                        'message': alerte.message,
                        'date_alerte': alerte.date_alerte.strftime('%Y-%m-%d'),
                        'date_rappel': alerte.date_rappel.strftime('%Y-%m-%d') if alerte.date_rappel else None
                    }
                )
                print(f"   ✅ Action d'alerte ajoutée")
                actions_crees += 1
                
        except Exception as e:
            print(f"   ❌ Erreur lors de la création des actions : {e}")
            continue
    
    print(f"\n🎉 Résumé :")
    print(f"   - Actions créées : {actions_crees}")
    print(f"   - Total des actions dans la base : {ActionLog.objects.count()}")
    
    return True

if __name__ == '__main__':
    success = ajouter_actions_existantes()
    if success:
        print("\n✅ Actions ajoutées avec succès !")
        print("🎉 Tous les crédits existants ont maintenant des actions associées !")
    else:
        print("\n❌ Échec de l'ajout des actions !")
        sys.exit(1)
