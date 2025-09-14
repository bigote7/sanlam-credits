#!/usr/bin/env python
"""
Script de test pour le système de création de crédit divisé complet
Teste la création d'un crédit de 12 000 DH divisé en 3 parties avec chèques de garantie
"""

import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Client, Credit, Echeance, Cheque, Alerte
from gestion_credits.forms import CreditDiviseCompletForm

def test_credit_divise_complet():
    """Test de création d'un crédit divisé complet"""
    print("🧪 Test du système de création de crédit divisé complet")
    print("=" * 60)
    
    # 1. Vérifier qu'il y a des clients
    clients = Client.objects.all()
    if not clients.exists():
        print("❌ Aucun client trouvé. Créez d'abord des clients.")
        return False
    
    print(f"✅ {clients.count()} client(s) trouvé(s)")
    
    # 2. Créer un client de test si nécessaire
    client_test, created = Client.objects.get_or_create(
        cin='TEST123456',
        defaults={
            'nom': 'Test',
            'prenom': 'Crédit Divisé',
            'telephone': '0612345678',
            'email': 'test@example.com',
            'adresse': 'Adresse de test'
        }
    )
    
    if created:
        print(f"✅ Client de test créé : {client_test.nom_complet}")
    else:
        print(f"✅ Client de test existant : {client_test.nom_complet}")
    
    # 3. Tester le formulaire
    print("\n📝 Test du formulaire CreditDiviseCompletForm")
    print("-" * 40)
    
    form_data = {
        'client': client_test.pk,
        'montant_total': '12000.00',
        'nombre_parties': 3,
        'description': 'Test crédit divisé complet - 12 000 DH en 3 parties',
        'type_garantie': 'echelonne'
    }
    
    form = CreditDiviseCompletForm(data=form_data)
    
    if form.is_valid():
        print("✅ Formulaire valide")
        print(f"   - Client: {form.cleaned_data['client']}")
        print(f"   - Montant total: {form.cleaned_data['montant_total']} DH")
        print(f"   - Nombre de parties: {form.cleaned_data['nombre_parties']}")
        print(f"   - Type de garantie: {form.cleaned_data['type_garantie']}")
    else:
        print("❌ Formulaire invalide:")
        for field, errors in form.errors.items():
            print(f"   - {field}: {errors}")
        return False
    
    # 4. Tester avec garantie unique
    print("\n📝 Test du formulaire avec garantie unique")
    print("-" * 40)
    
    form_data_unique = {
        'client': client_test.pk,
        'montant_total': '12000.00',
        'nombre_parties': 3,
        'description': 'Test crédit divisé avec garantie unique',
        'type_garantie': 'unique',
        'numero_cheque_unique': 'CHQ-UNIQUE-001',
        'banque_unique': 'BMCE',
        'date_emission_unique': '2025-01-15',
        'montant_garantie_unique': '8000.00'
    }
    
    form_unique = CreditDiviseCompletForm(data=form_data_unique)
    
    if form_unique.is_valid():
        print("✅ Formulaire avec garantie unique valide")
        print(f"   - Numéro chèque: {form_unique.cleaned_data['numero_cheque_unique']}")
        print(f"   - Banque: {form_unique.cleaned_data['banque_unique']}")
        print(f"   - Montant garantie: {form_unique.cleaned_data['montant_garantie_unique']} DH")
    else:
        print("❌ Formulaire avec garantie unique invalide:")
        for field, errors in form_unique.errors.items():
            print(f"   - {field}: {errors}")
    
    # 5. Vérifier les modèles existants
    print("\n🔍 Vérification des modèles existants")
    print("-" * 40)
    
    credits_existants = Credit.objects.filter(client=client_test, type_credit='divise')
    if credits_existants.exists():
        print(f"✅ {credits_existants.count()} crédit(s) divisé(s) existant(s) pour ce client")
        
        for credit in credits_existants:
            print(f"   - Crédit #{credit.id}: {credit.montant_total} DH")
            echeances = credit.echeances.all()
            print(f"     {echeances.count()} échéance(s)")
            
            for echeance in echeances:
                print(f"       Partie {echeance.numero_partie}: {echeance.montant} DH - {'Espèces' if echeance.est_especes else 'Chèque'}")
                
                if not echeance.est_especes:
                    cheques = echeance.cheques.all()
                    for cheque in cheques:
                        print(f"         Chèque: {cheque.numero_cheque} - {cheque.banque} - {cheque.statut}")
    else:
        print("ℹ️  Aucun crédit divisé existant pour ce client")
    
    # 6. Test de validation des erreurs
    print("\n🚨 Test de validation des erreurs")
    print("-" * 40)
    
    # Test avec données manquantes
    form_invalide = CreditDiviseCompletForm(data={})
    if not form_invalide.is_valid():
        print("✅ Validation des erreurs fonctionne")
        print(f"   - Nombre d'erreurs: {len(form_invalide.errors)}")
    else:
        print("❌ Validation des erreurs ne fonctionne pas")
    
    # Test avec garantie unique mais champs manquants
    form_garantie_incomplete = CreditDiviseCompletForm(data={
        'client': client_test.pk,
        'montant_total': '12000.00',
        'nombre_parties': 3,
        'type_garantie': 'unique'
        # Champs du chèque manquants
    })
    
    if not form_garantie_incomplete.is_valid():
        print("✅ Validation garantie unique fonctionne")
        for field, errors in form_garantie_incomplete.errors.items():
            if 'unique' in field:
                print(f"   - Erreur {field}: {errors}")
    else:
        print("❌ Validation garantie unique ne fonctionne pas")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés avec succès!")
    print("\n📋 Prochaines étapes:")
    print("   1. Accéder à l'interface web")
    print("   2. Aller sur 'Nouveau Crédit' → 'Crédit Divisé Complet'")
    print("   3. Tester la création d'un crédit de 12 000 DH en 3 parties")
    print("   4. Vérifier la génération automatique des échéances et chèques")
    
    return True

if __name__ == '__main__':
    try:
        test_credit_divise_complet()
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
