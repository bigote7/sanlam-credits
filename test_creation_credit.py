#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.forms import CreditDiviseCompletForm
from gestion_credits.models import Client

def test_creation_credit():
    """Tester la création d'un crédit divisé"""
    
    print("🧪 Test de création de crédit divisé")
    print("=" * 50)
    
    # Créer un client de test
    client, created = Client.objects.get_or_create(
        cin='TEST456',
        defaults={
            'nom': 'Test',
            'prenom': 'Crédit',
            'telephone': '0612345679',
            'email': 'credit@example.com',
            'adresse': 'Adresse de test crédit'
        }
    )
    
    if created:
        print(f"✅ Client créé : {client.nom_complet}")
    else:
        print(f"✅ Client existant : {client.nom_complet}")
    
    # Données de test pour un crédit divisé
    data = {
        'client': client.id,
        'montant_total': '12000.00',
        'nombre_parties': '3',
        'description': 'Test crédit divisé avec chèques échelonnés',
        'type_garantie': 'echelonne',
        'numero_cheque_2': 'CHQ002',
        'banque_2': 'BMCE',
        'date_reglement_prevu_2': (date.today() + timedelta(days=30)).isoformat(),
        'besoins_cheque_2': 'Client préfère être contacté le matin',
        'numero_cheque_3': 'CHQ003',
        'banque_3': 'Attijariwafa Bank',
        'date_reglement_prevu_3': (date.today() + timedelta(days=60)).isoformat(),
        'besoins_cheque_3': 'Client disponible l\'après-midi'
    }
    
    print(f"\n📝 Données de test:")
    for key, value in data.items():
        print(f"   - {key}: {value}")
    
    # Créer le formulaire
    form = CreditDiviseCompletForm(data)
    
    print(f"\n🔍 Validation du formulaire:")
    print(f"   - Formulaire valide : {form.is_valid()}")
    
    if form.is_valid():
        print("   - ✅ Formulaire valide !")
        print(f"   - Données nettoyées : {form.cleaned_data}")
        
        # Simuler la création du crédit
        print(f"\n🏗️ Simulation de création du crédit:")
        print(f"   - Client : {form.cleaned_data['client']}")
        print(f"   - Montant total : {form.cleaned_data['montant_total']} DH")
        print(f"   - Nombre de parties : {form.cleaned_data['nombre_parties']}")
        print(f"   - Type de garantie : {form.cleaned_data['type_garantie']}")
        
        if form.cleaned_data['type_garantie'] == 'echelonne':
            print(f"   - Chèques échelonnés :")
            for i in range(2, form.cleaned_data['nombre_parties'] + 1):
                numero = form.cleaned_data.get(f'numero_cheque_{i}')
                banque = form.cleaned_data.get(f'banque_{i}')
                date_reglement = form.cleaned_data.get(f'date_reglement_prevu_{i}')
                besoins = form.cleaned_data.get(f'besoins_cheque_{i}')
                
                print(f"     * Partie {i}: {numero} - {banque} - {date_reglement}")
                if besoins:
                    print(f"       Besoins: {besoins}")
        
        print("\n✅ Test de création réussi !")
        
    else:
        print("   - ❌ Formulaire invalide !")
        print(f"   - Erreurs : {form.errors}")
        print(f"   - Erreurs non-field : {form.non_field_errors()}")

if __name__ == '__main__':
    test_creation_credit()
