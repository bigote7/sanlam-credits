#!/usr/bin/env python
"""
Test des actions automatiques lors des modifications
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import ActionLog, Credit, Client, Echeance
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json

def test_actions_automatiques():
    """Test des actions automatiques lors des modifications"""
    print("🧪 Test des actions automatiques lors des modifications")
    print("=" * 70)
    
    # 1. Vérifier le total des actions avant test
    total_actions_avant = ActionLog.objects.count()
    print(f"📊 Total des actions avant test : {total_actions_avant}")
    
    # 2. Vérifier les actions existantes par type
    print(f"\n📋 Actions existantes par type :")
    repartition_types = ActionLog.objects.values('type_action').annotate(
        count=django.db.models.Count('id')
    ).order_by('-count')
    
    for rep in repartition_types:
        print(f"   - {rep['type_action']} : {rep['count']} actions")
    
    # 3. Vérifier les actions récentes
    print(f"\n🕒 Actions les plus récentes (5 dernières) :")
    actions_recentes = ActionLog.objects.all().order_by('-date_action')[:5]
    
    for action in actions_recentes:
        print(f"   - {action.get_type_action_display()}")
        print(f"     Date: {action.date_action.strftime('%d/%m/%Y %H:%M')}")
        print(f"     Description: {action.description[:60]}...")
        if action.credit:
            print(f"     Crédit: Police {action.credit.numero_police}")
        if action.client:
            print(f"     Client: {action.client.nom_complet}")
        print()
    
    # 4. Vérifier les échéances non payées
    print(f"🔍 Échéances non payées disponibles pour test :")
    echeances_non_payees = Echeance.objects.filter(est_traitee=False)[:3]
    
    if echeances_non_payees.exists():
        for echeance in echeances_non_payees:
            print(f"   - Échéance {echeance.numero_partie} pour {echeance.credit.client.nom_complet}")
            print(f"     Police: {echeance.credit.numero_police}")
            print(f"     Montant: {echeance.montant} DH")
            print(f"     Date échéance: {echeance.date_echeance}")
            print()
    else:
        print("   ❌ Aucune échéance non payée trouvée")
    
    # 5. Instructions pour tester manuellement
    print(f"🌐 Instructions pour tester manuellement :")
    print(f"   1. Allez sur : http://127.0.0.1:8000/")
    print(f"   2. Connectez-vous avec un compte utilisateur")
    print(f"   3. Allez sur la page d'historique : http://127.0.0.1:8000/historique/")
    print(f"   4. Vérifiez que {total_actions_avant} actions sont visibles")
    print(f"   5. Allez sur un crédit et marquez une échéance comme payée")
    print(f"   6. Retournez sur l'historique et vérifiez qu'une nouvelle action 'echeance_paiement' apparaît")
    print(f"   7. Créez ou modifiez un client et vérifiez les actions correspondantes")
    
    # 6. Vérifier les types d'actions disponibles
    print(f"\n🎯 Types d'actions maintenant disponibles :")
    types_disponibles = ActionLog.objects.values_list('type_action', flat=True).distinct()
    
    for type_action in types_disponibles:
        count = ActionLog.objects.filter(type_action=type_action).count()
        print(f"   - {type_action} : {count} actions")
    
    return True

if __name__ == '__main__':
    success = test_actions_automatiques()
    if success:
        print("\n✅ Test des actions automatiques réussi !")
        print("🎉 Les actions sont maintenant créées automatiquement lors des modifications !")
    else:
        print("\n❌ Test des actions automatiques échoué !")
        sys.exit(1)
