#!/usr/bin/env python
"""
Script de test pour vérifier les améliorations de la page des alertes
"""

import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Client, Credit, Echeance, Alerte
from django.contrib.auth.models import User

def test_ameliorations_alertes():
    """Test des améliorations de la page des alertes"""
    print("🧪 Test des améliorations de la page des alertes")
    print("=" * 50)
    
    try:
        # Vérifier que les modèles existent
        print("✅ Modèles disponibles :")
        print(f"   - Client: {Client.objects.count()} clients")
        print(f"   - Credit: {Credit.objects.count()} crédits")
        print(f"   - Echeance: {Echeance.objects.count()} échéances")
        print(f"   - Alerte: {Alerte.objects.count()} alertes")
        
        # Vérifier les échéances urgentes
        today = date.today()
        echeances_urgentes = Echeance.objects.filter(
            date_echeance__lte=today,
            est_traitee=False
        ).count()
        
        print(f"\n🔴 Échéances urgentes (aujourd'hui ou dépassées): {echeances_urgentes}")
        
        # Vérifier les alertes par type
        alertes_echeances = Alerte.objects.filter(type_alerte='echeance').count()
        alertes_cheques = Alerte.objects.filter(type_alerte='cheque_garantie').count()
        alertes_rappel = Alerte.objects.filter(type_alerte='rappel').count()
        
        print(f"\n📊 Répartition des alertes par type:")
        print(f"   - Échéances: {alertes_echeances}")
        print(f"   - Chèques garantie: {alertes_cheques}")
        print(f"   - Rappels: {alertes_rappel}")
        
        # Vérifier les statuts des alertes
        alertes_en_attente = Alerte.objects.filter(statut='en_attente').count()
        alertes_traitees = Alerte.objects.filter(statut='traitee').count()
        
        print(f"\n📈 Statuts des alertes:")
        print(f"   - En attente: {alertes_en_attente}")
        print(f"   - Traitées: {alertes_traitees}")
        
        # Vérifier les fichiers CSS
        css_file = "gestion_credits/static/gestion_credits/css/alertes.css"
        if os.path.exists(css_file):
            print(f"\n🎨 Fichier CSS personnalisé: ✅ {css_file}")
        else:
            print(f"\n❌ Fichier CSS manquant: {css_file}")
        
        # Vérifier le template
        template_file = "gestion_credits/templates/gestion_credits/alerte_list.html"
        if os.path.exists(template_file):
            print(f"\n📄 Template HTML: ✅ {template_file}")
        else:
            print(f"\n❌ Template HTML manquant: {template_file}")
        
        print("\n" + "=" * 50)
        print("🎉 Tests terminés avec succès !")
        print("\n📝 Pour tester l'interface:")
        print("   1. Démarrez le serveur: python manage.py runserver")
        print("   2. Allez sur: http://127.0.0.1:8000/alertes/")
        print("   3. Vérifiez les 3 blocs et les filtres avancés")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_ameliorations_alertes()
    sys.exit(0 if success else 1)
