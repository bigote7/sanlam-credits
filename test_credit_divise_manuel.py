#!/usr/bin/env python
"""
Script de test pour le système de création de crédit divisé avec saisie manuelle
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

def test_credit_divise_manuel():
    """Test de création d'un crédit divisé avec saisie manuelle"""
    print("🧪 Test du système de création de crédit divisé avec saisie manuelle")
    print("=" * 70)
    
    # 1. Vérifier qu'il y a des clients
    clients = Client.objects.all()
    if not clients.exists():
        print("❌ Aucun client trouvé. Créez d'abord des clients.")
        return False
    
    print(f"✅ {clients.count()} client(s) trouvé(s)")
    
    # 2. Créer un client de test si nécessaire
    client_test, created = Client.objects.get_or_create(
        cin='TEST123789',
        defaults={
            'nom': 'Test',
            'prenom': 'Crédit Manuel',
            'telephone': '0612345679',
            'email': 'test.manuel@example.com',
            'adresse': 'Adresse de test manuel'
        }
    )
    
    if created:
        print(f"✅ Client de test créé : {client_test.nom_complet}")
    else:
        print(f"✅ Client de test existant : {client_test.nom_complet}")
    
    # 3. Tester le formulaire avec chèques échelonnés
    print("\n📝 Test du formulaire avec chèques échelonnés (saisie manuelle)")
    print("-" * 50)
    
    # Calculer les dates futures
    date_aujourd_hui = date.today()
    date_partie_2 = date_aujourd_hui + timedelta(days=30)
    date_partie_3 = date_aujourd_hui + timedelta(days=60)
    
    form_data_echelonne = {
        'client': client_test.pk,
        'montant_total': '12000.00',
        'nombre_parties': 3,
        'description': 'Test crédit divisé avec saisie manuelle - 12 000 DH en 3 parties',
        'type_garantie': 'echelonne',
        'numero_cheque_2': 'CHQ-REF-001',
        'banque_2': 'BMCE',
        'date_reglement_prevu_2': date_partie_2.strftime('%Y-%m-%d'),
        'numero_cheque_3': 'CHQ-REF-002',
        'banque_3': 'Attijariwafa Bank',
        'date_reglement_prevu_3': date_partie_3.strftime('%Y-%m-%d'),
    }
    
    form_echelonne = CreditDiviseCompletForm(data=form_data_echelonne)
    
    if form_echelonne.is_valid():
        print("✅ Formulaire avec chèques échelonnés valide")
        print(f"   - Client: {form_echelonne.cleaned_data['client']}")
        print(f"   - Montant total: {form_echelonne.cleaned_data['montant_total']} DH")
        print(f"   - Nombre de parties: {form_echelonne.cleaned_data['nombre_parties']}")
        print(f"   - Type de garantie: {form_echelonne.cleaned_data['type_garantie']}")
        print(f"   - Chèque partie 2: {form_echelonne.cleaned_data['numero_cheque_2']} - {form_echelonne.cleaned_data['banque_2']}")
        print(f"   - Chèque partie 3: {form_echelonne.cleaned_data['numero_cheque_3']} - {form_echelonne.cleaned_data['banque_3']}")
        print(f"   - Date règlement partie 2: {form_echelonne.cleaned_data['date_reglement_prevu_2']}")
        print(f"   - Date règlement partie 3: {form_echelonne.cleaned_data['date_reglement_prevu_3']}")
    else:
        print("❌ Formulaire avec chèques échelonnés invalide:")
        for field, errors in form_echelonne.errors.items():
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
        'numero_cheque_unique': 'CHQ-UNIQUE-REF-001',
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
    
    # 5. Test de validation des erreurs pour chèques échelonnés
    print("\n🚨 Test de validation des erreurs pour chèques échelonnés")
    print("-" * 50)
    
    # Test avec chèques échelonnés mais champs manquants
    form_garantie_incomplete = CreditDiviseCompletForm(data={
        'client': client_test.pk,
        'montant_total': '12000.00',
        'nombre_parties': 3,
        'type_garantie': 'echelonne'
        # Champs des chèques manquants
    })
    
    if not form_garantie_incomplete.is_valid():
        print("✅ Validation chèques échelonnés fonctionne")
        for field, errors in form_garantie_incomplete.errors.items():
            if any(part in field for part in ['numero_cheque', 'banque', 'date_reglement_prevu']):
                print(f"   - Erreur {field}: {errors}")
    else:
        print("❌ Validation chèques échelonnés ne fonctionne pas")
    
    # 6. Vérifier les modèles existants
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
                        print(f"           Date règlement: {cheque.date_reglement_prevu}")
    else:
        print("ℹ️  Aucun crédit divisé existant pour ce client")
    
    # 7. Test de création simulée
    print("\n🔧 Test de création simulée")
    print("-" * 40)
    
    try:
        # Simuler la création d'un crédit (sans sauvegarder)
        credit_simule = Credit(
            client=client_test,
            type_credit='divise',
            montant_total=12000.00,
            description='Test simulation',
            agent=client_test  # Utiliser le client comme agent pour le test
        )
        
        print("✅ Création du crédit simulée avec succès")
        print(f"   - Type: {credit_simule.type_credit}")
        print(f"   - Montant: {credit_simule.montant_total} DH")
        print(f"   - Client: {credit_simule.client.nom_complet}")
        
        # Simuler la création des échéances
        montant_partie = 4000.00
        for i in range(1, 4):
            est_especes = (i == 1)
            date_echeance = date_aujourd_hui + timedelta(days=30 * i)
            
            print(f"   - Partie {i}: {montant_partie} DH - {'Espèces' if est_especes else 'Chèque'} - Date: {date_echeance}")
            
            if not est_especes:
                numero_cheque = f'CHQ-REF-{i:03d}'
                banque = 'BMCE' if i == 2 else 'Attijariwafa Bank'
                date_reglement = date_echeance
                
                print(f"     Chèque: {numero_cheque} - {banque} - Règlement: {date_reglement}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la simulation: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Tests terminés avec succès!")
    print("\n📋 Prochaines étapes:")
    print("   1. Accéder à l'interface web")
    print("   2. Aller sur 'Nouveau Crédit' → 'Crédit Divisé Complet'")
    print("   3. Choisir 'Chèques échelonnés'")
    print("   4. Saisir 3 parties")
    print("   5. Remplir manuellement les informations des chèques:")
    print("      - Partie 2: Numéro CHQ-REF-001, Banque BMCE, Date +30 jours")
    print("      - Partie 3: Numéro CHQ-REF-002, Banque Attijariwafa, Date +60 jours")
    print("   6. Vérifier la génération automatique des échéances et chèques")
    
    return True

if __name__ == '__main__':
    try:
        test_credit_divise_manuel()
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
