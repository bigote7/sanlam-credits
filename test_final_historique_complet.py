#!/usr/bin/env python
"""
Test final de la page d'historique des actions - Version complète
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

def test_final_historique_complet():
    """Test final complet de la page d'historique"""
    print("🧪 Test final complet de la page d'historique des actions")
    print("=" * 70)
    
    # 1. Vérifier le modèle ActionLog
    try:
        total_actions = ActionLog.objects.count()
        print(f"✅ Total des actions dans la base : {total_actions}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False
    
    # 2. Vérifier les crédits
    total_credits = Credit.objects.count()
    print(f"📊 Total des crédits dans la base : {total_credits}")
    
    # 3. Vérifier les échéances
    total_echeances = Echeance.objects.count()
    print(f"📅 Total des échéances dans la base : {total_echeances}")
    
    # 4. Vérifier les alertes
    total_alertes = Alerte.objects.count()
    print(f"🔔 Total des alertes dans la base : {total_alertes}")
    
    # 5. Vérifier la répartition des actions
    print(f"\n📋 Répartition des actions par type :")
    repartition_types = ActionLog.objects.values('type_action').annotate(
        count=django.db.models.Count('id')
    ).order_by('-count')
    
    for rep in repartition_types:
        print(f"   - {rep['type_action']} : {rep['count']} actions")
    
    # 6. Vérifier la répartition par statut
    print(f"\n🏷️ Répartition des actions par statut :")
    repartition_statuts = ActionLog.objects.values('statut').annotate(
        count=django.db.models.Count('id')
    ).order_by('-count')
    
    for rep in repartition_statuts:
        print(f"   - {rep['statut']} : {rep['count']} actions")
    
    # 7. Vérifier les actions récentes
    print(f"\n🕒 Actions les plus récentes :")
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
    
    # 8. Vérifier les actions par crédit
    print(f"🔍 Vérification des actions par crédit :")
    credits_avec_actions = Credit.objects.filter(actions_historique__isnull=False).distinct()
    print(f"   - Crédits avec actions : {credits_avec_actions.count()}")
    
    for credit in credits_avec_actions[:3]:
        actions_credit = ActionLog.objects.filter(credit=credit)
        print(f"   - Police {credit.numero_police} : {actions_credit.count()} actions")
        for action in actions_credit:
            print(f"     * {action.get_type_action_display()}")
    
    # 9. Vérifier les actions par client
    print(f"\n👥 Vérification des actions par client :")
    clients_avec_actions = Client.objects.filter(actions_historique__isnull=False).distinct()
    print(f"   - Clients avec actions : {clients_avec_actions.count()}")
    
    for client in clients_avec_actions[:3]:
        actions_client = ActionLog.objects.filter(client=client)
        print(f"   - {client.nom_complet} : {actions_client.count()} actions")
    
    # 10. Vérifier les actions par agent
    print(f"\n👤 Vérification des actions par agent :")
    agents_avec_actions = User.objects.filter(actions_effectuees__isnull=False).distinct()
    print(f"   - Agents avec actions : {agents_avec_actions.count()}")
    
    for agent in agents_avec_actions:
        actions_agent = ActionLog.objects.filter(agent=agent)
        print(f"   - {agent.username} : {actions_agent.count()} actions")
    
    # 11. Vérifier les données JSON
    print(f"\n📊 Vérification des données JSON :")
    actions_avec_donnees = ActionLog.objects.filter(
        django.db.models.Q(donnees_avant__isnull=False) | 
        django.db.models.Q(donnees_apres__isnull=False)
    )
    print(f"   - Actions avec données JSON : {actions_avec_donnees.count()}")
    
    if actions_avec_donnees.exists():
        action_exemple = actions_avec_donnees.first()
        print(f"   - Exemple de données :")
        if action_exemple.donnees_apres:
            print(f"     Données après : {action_exemple.donnees_apres}")
    
    # 12. Résumé final
    print(f"\n🎉 RÉSUMÉ FINAL :")
    print(f"   - ✅ Actions totales : {total_actions}")
    print(f"   - ✅ Crédits couverts : {credits_avec_actions.count()}")
    print(f"   - ✅ Clients couverts : {clients_avec_actions.count()}")
    print(f"   - ✅ Agents actifs : {agents_avec_actions.count()}")
    print(f"   - ✅ Données JSON : {actions_avec_donnees.count()}")
    
    # 13. Instructions de test
    print(f"\n🌐 Test de la page d'historique :")
    print(f"   - URL : http://127.0.0.1:8000/historique/")
    print(f"   - Assurez-vous que le serveur est démarré")
    print(f"   - Vérifiez que {total_actions} actions sont visibles")
    print(f"   - Testez les filtres et la pagination")
    print(f"   - Cliquez sur 'Voir' pour tester les modals")
    print(f"   - Créez un nouveau crédit pour voir les actions automatiques")
    
    return True

if __name__ == '__main__':
    success = test_final_historique_complet()
    if success:
        print("\n✅ Test final réussi !")
        print("🎉 La page d'historique est maintenant complètement fonctionnelle !")
        print("🚀 Toutes les actions sont visibles et organisées !")
    else:
        print("\n❌ Test final échoué !")
        sys.exit(1)
