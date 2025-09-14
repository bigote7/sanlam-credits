#!/usr/bin/env python
"""
Test du champ numero_police ajouté au modèle Credit
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Credit, Client
from django.contrib.auth.models import User

def test_numero_police():
    """Tester le champ numero_police"""
    print("🧪 Test du champ numero_police")
    print("=" * 50)
    
    # Vérifier que le champ existe
    try:
        credit_fields = [field.name for field in Credit._meta.fields]
        if 'numero_police' in credit_fields:
            print("✅ Champ 'numero_police' présent dans le modèle Credit")
        else:
            print("❌ Champ 'numero_police' manquant dans le modèle Credit")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du modèle: {e}")
        return False
    
    # Vérifier les crédits existants
    try:
        credits = Credit.objects.all()
        print(f"📊 Nombre de crédits existants: {credits.count()}")
        
        if credits.count() > 0:
            print("\n🔍 Vérification des numéros de police existants:")
            for credit in credits[:5]:  # Afficher les 5 premiers
                print(f"   - Crédit {credit.id}: {credit.numero_police}")
            
            # Vérifier l'unicité
            numeros = [credit.numero_police for credit in credits]
            if len(numeros) == len(set(numeros)):
                print("✅ Tous les numéros de police sont uniques")
            else:
                print("❌ Il y a des doublons dans les numéros de police")
                return False
        else:
            print("ℹ️  Aucun crédit existant dans la base de données")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des crédits: {e}")
        return False
    
    # Test de création d'un nouveau crédit
    try:
        print("\n🧪 Test de création d'un nouveau crédit...")
        
        # Créer un client de test si nécessaire
        client, created = Client.objects.get_or_create(
            nom="Test",
            prenom="NumeroPolice",
            defaults={
                'cin': 'TEST123',
                'telephone': '0600000000',
                'email': 'test@test.com'
            }
        )
        
        if created:
            print(f"   - Client de test créé: {client.nom_complet}")
        else:
            print(f"   - Client de test existant: {client.nom_complet}")
        
        # Créer un utilisateur de test si nécessaire
        user, created = User.objects.get_or_create(
            username='test_agent',
            defaults={
                'first_name': 'Agent',
                'last_name': 'Test',
                'email': 'agent@test.com'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"   - Utilisateur de test créé: {user.username}")
        else:
            print(f"   - Utilisateur de test existant: {user.username}")
        
        # Créer un crédit de test
        credit = Credit.objects.create(
            client=client,
            numero_police='POL-TEST-001',
            montant_total=1000.00,
            description='Crédit de test pour numero_police',
            type_credit='unique',
            agent=user
        )
        
        print(f"   - Crédit de test créé: {credit.numero_police}")
        
        # Vérifier que le numéro de police est bien enregistré
        credit_refresh = Credit.objects.get(pk=credit.pk)
        if credit_refresh.numero_police == 'POL-TEST-001':
            print("✅ Numéro de police correctement enregistré")
        else:
            print(f"❌ Numéro de police incorrect: {credit_refresh.numero_police}")
            return False
        
        # Nettoyer le crédit de test
        credit.delete()
        print("   - Crédit de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur lors du test de création: {e}")
        return False
    
    print("\n🎉 Tous les tests sont passés avec succès!")
    return True

if __name__ == '__main__':
    success = test_numero_police()
    if success:
        print("\n✅ Le champ numero_police fonctionne correctement!")
    else:
        print("\n❌ Il y a des problèmes avec le champ numero_police!")
        sys.exit(1)
