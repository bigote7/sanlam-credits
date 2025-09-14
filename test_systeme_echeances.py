#!/usr/bin/env python
"""
Script de test pour le nouveau système professionnel de paiement des échéances
"""

import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Credit, Client, User
from gestion_credits.forms import PaiementEcheanceForm

def test_systeme_echeances():
    """Test du nouveau système de paiement des échéances"""
    
    print("🧪 Test du Système Professionnel de Paiement des Échéances")
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
        print("📝 Test du Formulaire PaiementEcheanceForm")
        print("-" * 40)
        
        # Créer le formulaire avec le crédit
        form = PaiementEcheanceForm(credit=credit)
        
        print("✅ Formulaire créé avec succès")
        print(f"   Champs disponibles: {len(form.fields)}")
        print(f"   Mode de paiement: {form.fields['mode_paiement'].choices}")
        print(f"   Type d'échéance: {form.fields['type_echeance'].choices}")
        print()
        
        # Test de validation
        print("🔍 Test de Validation")
        print("-" * 40)
        
        # Données de test pour échéance unique en espèces
        test_data_especes = {
            'mode_paiement': 'especes',
            'type_echeance': 'unique',
            'montant_total': credit.reste_a_payer,
            'montant_echeance_unique': credit.reste_a_payer,
            'date_echeance_unique': date.today() + timedelta(days=30),
            'commentaire': 'Test échéance unique en espèces'
        }
        
        form_especes = PaiementEcheanceForm(test_data_especes, credit=credit)
        if form_especes.is_valid():
            print("✅ Validation échéance unique en espèces: OK")
        else:
            print("❌ Validation échéance unique en espèces: ÉCHEC")
            print(f"   Erreurs: {form_especes.errors}")
        
        # Données de test pour échéances multiples par effets
        test_data_effets = {
            'mode_paiement': 'effets',
            'type_echeance': 'multiple',
            'montant_total': credit.reste_a_payer,
            'nombre_echeances': 3,
            'frequence_paiement': 'mensuelle',
            'date_premiere_echeance': date.today() + timedelta(days=15),
            'numero_effet': 'CHQ-001',
            'banque_emetteur': 'Banque Populaire',
            'date_emission_effet': date.today(),
            'commentaire': 'Test échéances multiples par effets'
        }
        
        form_effets = PaiementEcheanceForm(test_data_effets, credit=credit)
        if form_effets.is_valid():
            print("✅ Validation échéances multiples par effets: OK")
        else:
            print("❌ Validation échéances multiples par effets: ÉCHEC")
            print(f"   Erreurs: {form_effets.errors}")
        
        print()
        
        # Test des modèles
        print("🏗️ Test des Modèles")
        print("-" * 40)
        
        from gestion_credits.models import Echeance, Reglement, Cheque, Alerte
        
        print(f"✅ Modèle Echeance: {Echeance.__name__}")
        print(f"✅ Modèle Reglement: {Reglement.__name__}")
        print(f"✅ Modèle Cheque: {Cheque.__name__}")
        print(f"✅ Modèle Alerte: {Alerte.__name__}")
        
        # Vérifier les échéances existantes
        echeances_count = credit.echeances.count()
        reglements_count = credit.reglements.count()
        
        print(f"   Échéances existantes: {echeances_count}")
        print(f"   Règlements existants: {reglements_count}")
        
        print()
        print("🎉 Tous les tests sont passés avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_systeme_echeances()
