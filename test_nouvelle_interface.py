#!/usr/bin/env python
"""
Test de la nouvelle interface des crédits avec séparation payés/non réglés
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Credit, Echeance
from django.db.models import Q

def test_nouvelle_interface():
    """Test de la nouvelle logique de séparation des crédits"""
    print("🧪 Test de la nouvelle interface des crédits")
    print("=" * 60)
    
    # Récupérer tous les crédits avec leurs échéances
    credits = Credit.objects.all().select_related('client', 'agent').prefetch_related('echeances')
    
    print(f"📊 Total des crédits : {credits.count()}")
    
    # Séparer les crédits payés des crédits non réglés
    credits_payes = []
    credits_non_regles = []
    
    for credit in credits:
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
    
    # Calculer les montants
    montant_total_payes = sum(credit.montant_total for credit in credits_payes)
    montant_total_non_regles = sum(credit.montant_total for credit in credits_non_regles)
    
    print(f"\n💰 Montant total payés : {montant_total_payes} DH")
    print(f"💰 Montant total non réglés : {montant_total_non_regles} DH")
    
    # Afficher quelques exemples
    print(f"\n🔍 Exemples de crédits non réglés :")
    for i, credit in enumerate(credits_non_regles[:3]):
        echeances = credit.echeances.all()
        statut_echeances = []
        for echeance in echeances:
            if echeance.est_traitee:
                statut_echeances.append(f"Partie {echeance.numero_partie}: ✅")
            else:
                statut_echeances.append(f"Partie {echeance.numero_partie}: ⏳")
        
        print(f"   {i+1}. {credit.client.nom_complet} - {credit.numero_police}")
        print(f"      Montant: {credit.montant_total} DH")
        print(f"      Échéances: {', '.join(statut_echeances) if statut_echeances else 'Aucune'}")
    
    if credits_payes:
        print(f"\n✅ Exemples de crédits payés :")
        for i, credit in enumerate(credits_payes[:3]):
            echeances = credit.echeances.all()
            print(f"   {i+1}. {credit.client.nom_complet} - {credit.numero_police}")
            print(f"      Montant: {credit.montant_total} DH")
            print(f"      Échéances: {echeances.count()} partie(s) payée(s)")
    
    # Test des filtres
    print(f"\n🔧 Test des filtres :")
    
    # Filtre par statut payés
    credits_payes_filter = []
    for credit in credits:
        echeances = credit.echeances.all()
        if echeances.exists():
            toutes_payees = all(echeance.est_traitee for echeance in echeances)
            if toutes_payees:
                credits_payes_filter.append(credit)
    
    print(f"   Filtre 'payés' : {len(credits_payes_filter)} crédits")
    
    # Filtre par statut non réglés
    credits_non_regles_filter = []
    for credit in credits:
        echeances = credit.echeances.all()
        if echeances.exists():
            toutes_payees = all(echeance.est_traitee for echeance in echeances)
            if not toutes_payees:
                credits_non_regles_filter.append(credit)
        else:
            credits_non_regles_filter.append(credit)
    
    print(f"   Filtre 'non réglés' : {len(credits_non_regles_filter)} crédits")
    
    # Vérification de la cohérence
    total_filtres = len(credits_payes_filter) + len(credits_non_regles_filter)
    print(f"   Total des filtres : {total_filtres}")
    print(f"   Total des crédits : {credits.count()}")
    
    if total_filtres == credits.count():
        print("✅ Cohérence des filtres : OK")
    else:
        print("❌ Cohérence des filtres : Problème détecté")
    
    return True

if __name__ == "__main__":
    try:
        test_nouvelle_interface()
    except Exception as e:
        print(f"\n❌ Erreur lors du test : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
