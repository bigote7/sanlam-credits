#!/usr/bin/env python
"""
Script de test pour vérifier que le formulaire CreditDiviseCompletForm fonctionne
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.forms import CreditDiviseCompletForm
from gestion_credits.models import Client

def test_form_credit_divise():
    """Tester le formulaire de crédit divisé"""
    
    print("🧪 Test du formulaire CreditDiviseCompletForm")
    print("=" * 50)
    
    # Créer un client de test si nécessaire
    client, created = Client.objects.get_or_create(
        cin='TEST123',
        defaults={
            'nom': 'Test',
            'prenom': 'Client',
            'telephone': '0612345678',
            'email': 'test@example.com',
            'adresse': 'Adresse de test'
        }
    )
    
    if created:
        print(f"✅ Client de test créé : {client.nom_complet}")
    else:
        print(f"✅ Client de test existant : {client.nom_complet}")
    
    # Test 1: Formulaire vide
    print("\n📝 Test 1: Formulaire vide")
    form1 = CreditDiviseCompletForm()
    print(f"   - Formulaire valide : {form1.is_valid()}")
    print(f"   - Champs disponibles : {list(form1.fields.keys())}")
    
    # Test 2: Formulaire avec données valides (garantie unique)
    print("\n📝 Test 2: Garantie unique")
    data_unique = {
        'client': client.id,
        'montant_total': '12000.00',
        'nombre_parties': '3',
        'description': 'Test crédit divisé',
        'type_garantie': 'unique',
        'numero_cheque_unique': 'CHQ001',
        'banque_unique': 'BMCE',
        'date_emission_unique': '2025-01-15',
        'montant_garantie_unique': '8000.00'
    }
    
    form2 = CreditDiviseCompletForm(data_unique)
    print(f"   - Formulaire valide : {form2.is_valid()}")
    if not form2.is_valid():
        print(f"   - Erreurs : {form2.errors}")
    
    # Test 3: Formulaire avec données valides (chèques échelonnés)
    print("\n📝 Test 3: Chèques échelonnés")
    data_echelonne = {
        'client': client.id,
        'montant_total': '12000.00',
        'nombre_parties': '3',
        'description': 'Test crédit divisé échelonné',
        'type_garantie': 'echelonne',
        'numero_cheque_2': 'CHQ002',
        'banque_2': 'Attijariwafa Bank',
        'date_reglement_prevu_2': '2025-02-15',
        'besoins_cheque_2': 'Client préfère être contacté le matin',
        'numero_cheque_3': 'CHQ003',
        'banque_3': 'BMCE',
        'date_reglement_prevu_3': '2025-03-15',
        'besoins_cheque_3': 'Client disponible l\'après-midi'
    }
    
    form3 = CreditDiviseCompletForm(data_echelonne)
    print(f"   - Formulaire valide : {form3.is_valid()}")
    if not form3.is_valid():
        print(f"   - Erreurs : {form3.errors}")
    
    # Test 4: Vérifier les champs dynamiques
    print("\n📝 Test 4: Champs dynamiques")
    form4 = CreditDiviseCompletForm()
    champs_dynamiques = [f for f in form4.fields.keys() if f.startswith('numero_cheque_') or f.startswith('banque_') or f.startswith('date_reglement_prevu_') or f.startswith('besoins_cheque_')]
    print(f"   - Champs dynamiques trouvés : {champs_dynamiques}")
    
    print("\n✅ Tests terminés !")

if __name__ == '__main__':
    test_form_credit_divise()
