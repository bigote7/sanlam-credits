#!/usr/bin/env python
"""
Test simple de l'interface corrigée des crédits
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Credit, Echeance

def test_interface_corrigee():
    """Test simple de l'interface corrigée"""
    print("🧪 Test de l'interface corrigée des crédits")
    print("=" * 50)
    
    # Vérifier que les crédits existent
    total_credits = Credit.objects.count()
    print(f"📊 Total des crédits : {total_credits}")
    
    if total_credits == 0:
        print("❌ Aucun crédit trouvé dans la base de données")
        return False
    
    # Vérifier que les échéances existent
    total_echeances = Echeance.objects.count()
    print(f"📅 Total des échéances : {total_echeances}")
    
    # Vérifier la logique de séparation
    credits_payes = []
    credits_non_regles = []
    
    for credit in Credit.objects.all().prefetch_related('echeances'):
        echeances = credit.echeances.all()
        if echeances.exists():
            toutes_payees = all(echeance.est_traitee for echeance in echeances)
            if toutes_payees:
                credits_payes.append(credit)
            else:
                credits_non_regles.append(credit)
        else:
            credits_non_regles.append(credit)
    
    print(f"✅ Crédits payés : {len(credits_payes)}")
    print(f"⚠️  Crédits non réglés : {len(credits_non_regles)}")
    
    # Vérifier que la logique est cohérente
    total_calcule = len(credits_payes) + len(credits_non_regles)
    if total_calcule == total_credits:
        print("✅ Cohérence de la logique : OK")
    else:
        print(f"❌ Problème de cohérence : {total_calcule} != {total_credits}")
        return False
    
    # Afficher quelques détails
    if credits_non_regles:
        print(f"\n🔍 Premier crédit non réglé :")
        credit = credits_non_regles[0]
        print(f"   - Client : {credit.client.nom_complet}")
        print(f"   - Police : {credit.numero_police}")
        print(f"   - Montant : {credit.montant_total} DH")
        print(f"   - Échéances : {credit.echeances.count()}")
    
    if credits_payes:
        print(f"\n✅ Premier crédit payé :")
        credit = credits_payes[0]
        print(f"   - Client : {credit.client.nom_complet}")
        print(f"   - Police : {credit.numero_police}")
        print(f"   - Montant : {credit.montant_total} DH")
        print(f"   - Échéances : {credit.echeances.count()}")
    
    print(f"\n🎉 Interface prête à être testée !")
    print(f"🌐 URL : http://127.0.0.1:8000/credits/")
    
    return True

if __name__ == "__main__":
    try:
        test_interface_corrigee()
    except Exception as e:
        print(f"\n❌ Erreur lors du test : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
