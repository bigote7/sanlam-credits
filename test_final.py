#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.forms import CreditDiviseCompletForm
from gestion_credits.models import Client

def test_final():
    """Test final de la création de crédit"""
    
    print("🎯 Test Final - Création de Crédit Divisé")
    print("=" * 60)
    
    # Créer un client de test
    client, created = Client.objects.get_or_create(
        cin='FINAL123',
        defaults={
            'nom': 'Final',
            'prenom': 'Test',
            'telephone': '0612345680',
            'email': 'final@example.com',
            'adresse': 'Adresse finale de test'
        }
    )
    
    if created:
        print(f"✅ Client créé : {client.nom_complet}")
    else:
        print(f"✅ Client existant : {client.nom_complet}")
    
    # Test 1: Garantie unique
    print(f"\n🧪 Test 1: Garantie unique")
    data_unique = {
        'client': client.id,
        'montant_total': '15000.00',
        'nombre_parties': '3',
        'description': 'Test final - Garantie unique',
        'type_garantie': 'unique',
        'numero_cheque_unique': 'CHQ_FINAL_001',
        'banque_unique': 'BMCE',
        'date_emission_unique': '2025-01-15',
        'montant_garantie_unique': '10000.00'
    }
    
    form1 = CreditDiviseCompletForm(data_unique)
    print(f"   - Formulaire valide : {form1.is_valid()}")
    if form1.is_valid():
        print("   - ✅ Garantie unique fonctionne !")
    else:
        print(f"   - ❌ Erreurs : {form1.errors}")
    
    # Test 2: Chèques échelonnés
    print(f"\n🧪 Test 2: Chèques échelonnés")
    data_echelonne = {
        'client': client.id,
        'montant_total': '12000.00',
        'nombre_parties': '3',
        'description': 'Test final - Chèques échelonnés',
        'type_garantie': 'echelonne',
        'numero_cheque_2': 'CHQ_FINAL_002',
        'banque_2': 'Attijariwafa Bank',
        'date_reglement_prevu_2': (date.today() + timedelta(days=30)).isoformat(),
        'besoins_cheque_2': 'Client préfère être contacté le matin',
        'numero_cheque_3': 'CHQ_FINAL_003',
        'banque_3': 'BMCE',
        'date_reglement_prevu_3': (date.today() + timedelta(days=60)).isoformat(),
        'besoins_cheque_3': 'Client disponible l\'après-midi'
    }
    
    form2 = CreditDiviseCompletForm(data_echelonne)
    print(f"   - Formulaire valide : {form2.is_valid()}")
    if form2.is_valid():
        print("   - ✅ Chèques échelonnés fonctionnent !")
        print(f"   - Données nettoyées :")
        for key, value in form2.cleaned_data.items():
            if key.startswith('numero_cheque_') or key.startswith('banque_') or key.startswith('date_reglement_prevu_') or key.startswith('besoins_cheque_'):
                print(f"     * {key}: {value}")
    else:
        print(f"   - ❌ Erreurs : {form2.errors}")
    
    # Test 3: Validation des erreurs
    print(f"\n🧪 Test 3: Validation des erreurs")
    data_invalide = {
        'client': client.id,
        'montant_total': '0.00',  # Montant invalide
        'nombre_parties': '6',    # Nombre de parties invalide
        'description': 'Test validation',
        'type_garantie': 'echelonne'
    }
    
    form3 = CreditDiviseCompletForm(data_invalide)
    print(f"   - Formulaire valide : {form3.is_valid()}")
    if not form3.is_valid():
        print("   - ✅ Validation des erreurs fonctionne !")
        print(f"   - Erreurs détectées : {form3.errors}")
    else:
        print("   - ❌ La validation n'a pas détecté les erreurs !")
    
    print(f"\n🎉 Tests terminés !")
    print(f"📝 Pour tester en ligne : http://127.0.0.1:8000/credits/create/divise/")

if __name__ == '__main__':
    test_final()
