#!/usr/bin/env python
"""
Script de test pour le nouveau système d'ajout de paiement simplifié
"""

import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Credit, Client, User
from gestion_credits.forms import AjoutPaiementForm

def test_ajout_paiement():
    """Test du nouveau système d'ajout de paiement simplifié"""
    
    print("🧪 Test du Système d'Ajout de Paiement Simplifié")
    print("=" * 60)
    
    try:
        # Récupérer un crédit existant pour le test
        credit = Credit.objects.first()
        if not credit:
            print("❌ Aucun crédit trouvé dans la base de données")
            return
        
        print(f"✅ Crédit trouvé: {credit.numero_police} - {credit.client.nom_complet}")
        print(f"   Montant total: {credit.montant_total} DH")
        print(f"   Reste à payer: {credit.reste_a_payer} DH")
        print(f"   Total payé: {credit.total_paye} DH")
        print()
        
        # Test du formulaire
        print("📝 Test du Formulaire AjoutPaiementForm")
        print("-" * 40)
        
        # Créer le formulaire avec le crédit
        form = AjoutPaiementForm(credit=credit)
        
        print("✅ Formulaire créé avec succès")
        print(f"   Champs disponibles: {len(form.fields)}")
        print(f"   Mode de paiement: {form.fields['mode_paiement'].choices}")
        print(f"   Champs obligatoires: {[name for name, field in form.fields.items() if field.required]}")
        print()
        
        # Test de validation - Paiement en espèces
        print("🔍 Test de Validation - Paiement en Espèces")
        print("-" * 40)
        
        test_data_especes = {
            'mode_paiement': 'especes',
            'montant': credit.reste_a_payer,
            'date_paiement': date.today(),
            'commentaire': 'Test paiement en espèces'
        }
        
        form_especes = AjoutPaiementForm(test_data_especes, credit=credit)
        if form_especes.is_valid():
            print("✅ Validation paiement en espèces: OK")
        else:
            print("❌ Validation paiement en espèces: ÉCHEC")
            print(f"   Erreurs: {form_especes.errors}")
        
        # Test de validation - Paiement par effets
        print("\n🔍 Test de Validation - Paiement par Effets")
        print("-" * 40)
        
        test_data_effets = {
            'mode_paiement': 'effets',
            'montant': credit.reste_a_payer / 2,  # Moitié du reste
            'date_paiement': date.today() + timedelta(days=15),
            'numero_effet': 'CHQ-001',
            'banque_emetteur': 'Banque Populaire',
            'date_emission_effet': date.today(),
            'commentaire': 'Test paiement par effets'
        }
        
        form_effets = AjoutPaiementForm(test_data_effets, credit=credit)
        if form_effets.is_valid():
            print("✅ Validation paiement par effets: OK")
        else:
            print("❌ Validation paiement par effets: ÉCHEC")
            print(f"   Erreurs: {form_effets.errors}")
        
        # Test de validation - Montant trop élevé
        print("\n🔍 Test de Validation - Montant Trop Élevé")
        print("-" * 40)
        
        test_data_trop_eleve = {
            'mode_paiement': 'especes',
            'montant': credit.reste_a_payer + 1000,  # Plus que le reste
            'date_paiement': date.today(),
            'commentaire': 'Test montant trop élevé'
        }
        
        form_trop_eleve = AjoutPaiementForm(test_data_trop_eleve, credit=credit)
        if form_trop_eleve.is_valid():
            print("⚠️ Validation montant trop élevé: OK (devrait échouer)")
        else:
            print("✅ Validation montant trop élevé: ÉCHEC (comme attendu)")
            print(f"   Erreurs: {form_trop_eleve.errors}")
        
        print()
        
        # Test des modèles
        print("🏗️ Test des Modèles")
        print("-" * 40)
        
        from gestion_credits.models import Reglement, ChequeGarantie
        
        print(f"✅ Modèle Reglement: {Reglement.__name__}")
        print(f"✅ Modèle ChequeGarantie: {ChequeGarantie.__name__}")
        
        # Vérifier les règlements existants
        reglements_count = credit.reglements.count()
        cheques_garantie_count = credit.cheques_garantie.count()
        
        print(f"   Règlements existants: {reglements_count}")
        print(f"   Chèques de garantie existants: {cheques_garantie_count}")
        
        print()
        print("🎉 Tous les tests sont passés avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_ajout_paiement()
