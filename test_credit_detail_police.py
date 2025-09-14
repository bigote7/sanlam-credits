#!/usr/bin/env python
"""
Test de l'affichage du numéro de police dans la page de détail du crédit
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanlam_credits.settings')
django.setup()

from gestion_credits.models import Credit, Client
from django.contrib.auth.models import User

def test_credit_detail_police():
    """Tester l'affichage du numéro de police dans la page de détail"""
    print("🧪 Test de l'affichage du numéro de police dans la page de détail")
    print("=" * 70)
    
    # Vérifier qu'il y a des crédits avec des numéros de police
    try:
        credits = Credit.objects.all()
        print(f"📊 Nombre de crédits dans la base : {credits.count()}")
        
        if credits.count() == 0:
            print("ℹ️  Aucun crédit dans la base de données")
            return False
        
        # Afficher les crédits avec leurs numéros de police
        print("\n🔍 Crédits disponibles avec leurs numéros de police :")
        for credit in credits:
            print(f"   - Crédit ID {credit.id}: {credit.numero_police}")
            print(f"     Client: {credit.client.nom_complet}")
            print(f"     Montant: {credit.montant_total} DH")
            print(f"     Type: {credit.type_credit}")
            print()
        
        # Vérifier que tous les crédits ont un numéro de police
        credits_sans_police = [c for c in credits if not c.numero_police or c.numero_police == '0000']
        if credits_sans_police:
            print("⚠️  Crédits sans numéro de police valide :")
            for credit in credits_sans_police:
                print(f"   - Crédit ID {credit.id}: {credit.numero_police}")
        else:
            print("✅ Tous les crédits ont un numéro de police valide")
        
        # Vérifier l'unicité des numéros de police
        numeros = [credit.numero_police for credit in credits]
        if len(numeros) == len(set(numeros)):
            print("✅ Tous les numéros de police sont uniques")
        else:
            print("❌ Il y a des doublons dans les numéros de police")
            # Trouver les doublons
            from collections import Counter
            doublons = [num for num, count in Counter(numeros).items() if count > 1]
            print(f"   Doublons trouvés : {doublons}")
            return False
        
        # Test de création d'un crédit de test si nécessaire
        print("\n🧪 Test de création d'un crédit de test...")
        
        # Créer un client de test si nécessaire
        client, created = Client.objects.get_or_create(
            nom="Test",
            prenom="DetailPolice",
            defaults={
                'cin': 'TEST456',
                'telephone': '0600000001',
                'email': 'test2@test.com'
            }
        )
        
        if created:
            print(f"   - Client de test créé: {client.nom_complet}")
        else:
            print(f"   - Client de test existant: {client.nom_complet}")
        
        # Créer un utilisateur de test si nécessaire
        user, created = User.objects.get_or_create(
            username='test_agent_detail',
            defaults={
                'first_name': 'Agent',
                'last_name': 'Detail',
                'email': 'agent2@test.com'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"   - Utilisateur de test créé: {user.username}")
        else:
            print(f"   - Utilisateur de test existant: {user.username}")
        
        # Créer un crédit de test
        credit_test = Credit.objects.create(
            client=client,
            numero_police='POL-DETAIL-001',
            montant_total=2500.00,
            description='Crédit de test pour vérifier l\'affichage du numéro de police',
            type_credit='unique',
            agent=user
        )
        
        print(f"   - Crédit de test créé: {credit_test.numero_police}")
        print(f"   - URL de détail: /credits/{credit_test.pk}/")
        
        # Vérifier que le numéro de police est bien enregistré
        credit_refresh = Credit.objects.get(pk=credit_test.pk)
        if credit_refresh.numero_police == 'POL-DETAIL-001':
            print("✅ Numéro de police correctement enregistré")
        else:
            print(f"❌ Numéro de police incorrect: {credit_refresh.numero_police}")
            return False
        
        # Nettoyer le crédit de test
        credit_test.delete()
        print("   - Crédit de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
    
    print("\n🎉 Tous les tests sont passés avec succès!")
    return True

def show_credit_urls():
    """Afficher les URLs des crédits pour tester l'affichage"""
    print("\n🌐 URLs des crédits pour tester l'affichage :")
    print("=" * 50)
    
    try:
        credits = Credit.objects.all()[:5]  # Limiter aux 5 premiers
        for credit in credits:
            print(f"   - Crédit {credit.numero_police}: http://127.0.0.1:8000/credits/{credit.pk}/")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des URLs: {e}")

if __name__ == '__main__':
    success = test_credit_detail_police()
    if success:
        print("\n✅ L'affichage du numéro de police est prêt!")
        show_credit_urls()
    else:
        print("\n❌ Il y a des problèmes avec l'affichage du numéro de police!")
        sys.exit(1)
