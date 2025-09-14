#!/usr/bin/env python
"""
Script pour supprimer TOUS les clients et crédits de la base de données
⚠️  ATTENTION : Cette action est IRRÉVERSIBLE !
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Client, Credit, Echeance, Cheque, Alerte, ReportEcheance, ActionLog

def supprimer_tout():
    """Supprimer tous les clients et crédits"""
    print("🚨 ATTENTION : SUPPRESSION COMPLÈTE DE LA BASE DE DONNÉES")
    print("=" * 60)
    print("⚠️  Cette action va supprimer :")
    print("   - TOUS les clients")
    print("   - TOUS les crédits")
    print("   - TOUTES les échéances")
    print("   - TOUS les chèques")
    print("   - TOUTES les alertes")
    print("   - TOUS les reports d'échéances")
    print("   - TOUT l'historique des actions")
    print("=" * 60)
    
    # Demander confirmation
    confirmation = input("Êtes-vous SÛR de vouloir continuer ? (tapez 'SUPPRIMER' pour confirmer) : ")
    
    if confirmation != "SUPPRIMER":
        print("❌ Suppression annulée")
        return False
    
    # Deuxième confirmation
    confirmation2 = input("DERNIÈRE CHANCE : Êtes-vous VRAIMENT sûr ? (tapez 'OUI JE SUIS SUR') : ")
    
    if confirmation2 != "OUI JE SUIS SUR":
        print("❌ Suppression annulée")
        return False
    
    print("\n🗑️  Début de la suppression...")
    
    try:
        # Compter avant suppression
        total_clients = Client.objects.count()
        total_credits = Credit.objects.count()
        total_echeances = Echeance.objects.count()
        total_cheques = Cheque.objects.count()
        total_alertes = Alerte.objects.count()
        total_reports = ReportEcheance.objects.count()
        total_actions = ActionLog.objects.count()
        
        print(f"📊 Avant suppression :")
        print(f"   - Clients : {total_clients}")
        print(f"   - Crédits : {total_credits}")
        print(f"   - Échéances : {total_echeances}")
        print(f"   - Chèques : {total_cheques}")
        print(f"   - Alertes : {total_alertes}")
        print(f"   - Reports : {total_reports}")
        print(f"   - Actions : {total_actions}")
        
        # Supprimer dans l'ordre pour éviter les erreurs de clés étrangères
        print("\n🗑️  Suppression des échéances...")
        Echeance.objects.all().delete()
        
        print("🗑️  Suppression des chèques...")
        Cheque.objects.all().delete()
        
        print("🗑️  Suppression des alertes...")
        Alerte.objects.all().delete()
        
        print("🗑️  Suppression des reports d'échéances...")
        ReportEcheance.objects.all().delete()
        
        print("🗑️  Suppression de l'historique des actions...")
        ActionLog.objects.all().delete()
        
        print("🗑️  Suppression des crédits...")
        Credit.objects.all().delete()
        
        print("🗑️  Suppression des clients...")
        Client.objects.all().delete()
        
        # Vérifier après suppression
        print("\n✅ Après suppression :")
        print(f"   - Clients : {Client.objects.count()}")
        print(f"   - Crédits : {Credit.objects.count()}")
        print(f"   - Échéances : {Echeance.objects.count()}")
        print(f"   - Chèques : {Cheque.objects.count()}")
        print(f"   - Alertes : {Alerte.objects.count()}")
        print(f"   - Reports : {ReportEcheance.objects.count()}")
        print(f"   - Actions : {ActionLog.objects.count()}")
        
        print("\n🎉 SUPPRESSION TERMINÉE AVEC SUCCÈS !")
        print("🗑️  Tous les clients et crédits ont été supprimés")
        print("⚠️  La base de données est maintenant vide")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la suppression : {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        supprimer_tout()
    except KeyboardInterrupt:
        print("\n\n❌ Suppression interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
