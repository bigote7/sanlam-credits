#!/usr/bin/env python
"""
Test simple de vérification des actions
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import ActionLog, Echeance

def test_verification():
    """Test simple de vérification"""
    print("🧪 Test de vérification des actions")
    print("=" * 50)
    
    # Vérifier l'état actuel
    total_actions = ActionLog.objects.count()
    actions_paiement = ActionLog.objects.filter(type_action='echeance_paiement').count()
    
    print(f"📊 Total des actions : {total_actions}")
    print(f"💰 Actions de paiement : {actions_paiement}")
    
    # Trouver une échéance non payée
    echeance = Echeance.objects.filter(est_traitee=False).first()
    
    if echeance:
        print(f"\n🔍 Échéance non payée trouvée :")
        print(f"   - Client : {echeance.credit.client.nom_complet}")
        print(f"   - Police : {echeance.credit.numero_police}")
        print(f"   - Partie : {echeance.numero_partie}")
        print(f"   - Montant : {echeance.montant} DH")
        print(f"   - Date échéance : {echeance.date_echeance}")
    else:
        print("❌ Aucune échéance non payée trouvée")
    
    return True

if __name__ == "__main__":
    test_verification()
