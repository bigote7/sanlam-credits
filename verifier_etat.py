#!/usr/bin/env python
"""
Script pour vérifier l'état actuel de la base de données
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Client, Credit, Echeance, Cheque, Alerte, ReportEcheance, ActionLog

def verifier_etat():
    """Vérifier l'état actuel de la base de données"""
    print("🔍 VÉRIFICATION DE L'ÉTAT ACTUEL DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    try:
        # Compter tous les objets
        total_clients = Client.objects.count()
        total_credits = Credit.objects.count()
        total_echeances = Echeance.objects.count()
        total_cheques = Cheque.objects.count()
        total_alertes = Alerte.objects.count()
        total_reports = ReportEcheance.objects.count()
        total_actions = ActionLog.objects.count()
        
        print(f"📊 État actuel :")
        print(f"   - Clients : {total_clients}")
        print(f"   - Crédits : {total_credits}")
        print(f"   - Échéances : {total_echeances}")
        print(f"   - Chèques : {total_cheques}")
        print(f"   - Alertes : {total_alertes}")
        print(f"   - Reports : {total_reports}")
        print(f"   - Actions : {total_actions}")
        
        # Afficher quelques détails
        if total_clients > 0:
            print(f"\n👥 Détails des clients :")
            for client in Client.objects.all()[:5]:  # Afficher les 5 premiers
                print(f"   - {client.nom_complet} (CIN: {client.cin})")
            if total_clients > 5:
                print(f"   ... et {total_clients - 5} autres")
        
        if total_credits > 0:
            print(f"\n💳 Détails des crédits :")
            for credit in Credit.objects.all()[:5]:  # Afficher les 5 premiers
                print(f"   - {credit.numero_police} - {credit.client.nom_complet} - {credit.montant_total} DH")
            if total_credits > 5:
                print(f"   ... et {total_credits - 5} autres")
        
        if total_echeances > 0:
            print(f"\n📅 Détails des échéances :")
            echeances_payees = Echeance.objects.filter(est_traitee=True).count()
            echeances_en_attente = Echeance.objects.filter(est_traitee=False).count()
            print(f"   - Payées : {echeances_payees}")
            print(f"   - En attente : {echeances_en_attente}")
        
        print(f"\n💾 Taille totale estimée : {total_clients + total_credits + total_echeances + total_cheques + total_alertes + total_reports + total_actions} enregistrements")
        
        if total_clients == 0 and total_credits == 0:
            print("\n✅ La base de données est déjà vide !")
        else:
            print(f"\n⚠️  ATTENTION : Il y a des données dans la base")
            print(f"   Pour tout supprimer, exécutez : python supprimer_tout.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la vérification : {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        verifier_etat()
    except Exception as e:
        print(f"\n❌ Erreur fatale : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
