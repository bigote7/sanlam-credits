# Système de Création de Crédit Divisé Complet

## Vue d'ensemble

Ce système permet de créer des crédits divisés avec une gestion complète des chèques de garantie directement lors de la création du crédit. Il remplace l'ancien système en deux étapes par un processus unifié et plus intuitif.

**🆕 NOUVEAUTÉ : Saisie manuelle des dates d'application et numéros de référence des chèques**

## Fonctionnalités principales

### 1. Création unifiée
- **Une seule page** pour créer le crédit et configurer toutes les échéances
- **Génération automatique** des échéances, chèques de garantie et alertes
- **Validation en temps réel** des données saisies

### 2. Types de garantie
- **Chèque de garantie unique** : Un seul chèque pour toutes les parties
- **Chèques échelonnés** : Un chèque différent pour chaque partie avec **saisie manuelle complète**

### 3. Configuration automatique
- **Première partie** : Toujours en espèces (obligatoire)
- **Parties suivantes** : Garanties par chèques selon le type choisi
- **Échéances** : Espacement automatique de 30 jours
- **Alertes** : Création automatique pour chaque échéance et chèque

### 4. 🆕 Saisie manuelle des chèques échelonnés
- **Numéro de référence** : Saisie manuelle pour chaque chèque
- **Banque émettrice** : Saisie manuelle pour chaque chèque
- **Date de règlement prévue** : **Saisie manuelle** pour rappels personnalisés
- **Validation obligatoire** : Tous les champs sont requis pour les chèques

## Architecture technique

### Modèles utilisés
- `Credit` : Informations du crédit (type_credit = 'divise')
- `Echeance` : Échéances de paiement
- `Cheque` : Chèques de garantie avec statut et dates
- `Alerte` : Alertes automatiques pour rappels

### Nouveaux formulaires
- `CreditDiviseCompletForm` : Formulaire principal de création avec champs dynamiques
- `EcheanceAvecChequeForm` : Formulaire pour échéances avec chèques

### Nouvelles vues
- `credit_create_divise_complet` : Vue de création complète

## Procédure de création

### 1. Accès à la page
- Menu principal → "Nouveau Crédit" → "Crédit Divisé Complet"
- Ou directement via l'URL : `/credits/create/divise/`

### 2. Informations du client
- **Sélection** : Client existant dans la liste déroulante
- **Création** : Lien vers la création d'un nouveau client
- **Validation** : Client obligatoire

### 3. Détails du crédit
- **Montant total** : Montant en dirhams (obligatoire)
- **Nombre de parties** : Entre 1 et 5 (obligatoire)
- **Description** : Informations optionnelles sur le crédit

### 4. Type de garantie
- **Chèque unique** : Un seul chèque pour toutes les parties
  - Numéro de référence du chèque
  - Banque émettrice
  - Date d'émission
  - Montant de la garantie
- **Chèques échelonnés** : Un chèque par partie avec **saisie manuelle complète**
  - **Numéro de référence** : Saisie manuelle pour chaque partie
  - **Banque émettrice** : Saisie manuelle pour chaque partie
  - **Date de règlement prévue** : **Saisie manuelle** pour rappels personnalisés

### 5. 🆕 Interface dynamique pour chèques échelonnés
- **Génération automatique** des champs selon le nombre de parties
- **Validation en temps réel** des informations saisies
- **Interface intuitive** avec cartes séparées pour chaque chèque
- **Champs obligatoires** clairement identifiés

### 6. Génération automatique
- **Échéances** : Créées avec espacement de 30 jours
- **Chèques** : Créés avec les informations manuelles saisies
- **Alertes** : Générées pour chaque échéance et chèque

## Exemple concret : Crédit de 12 000 DH

### Configuration
- **Montant total** : 12 000 DH
- **Nombre de parties** : 3
- **Type de garantie** : Chèques échelonnés

### Saisie manuelle des chèques
1. **Partie 1** : 4 000 DH en espèces (date : automatique)
2. **Partie 2** : 4 000 DH par chèque de garantie
   - **Numéro de référence** : CHQ-REF-001 (saisi manuellement)
   - **Banque émettrice** : BMCE (saisi manuellement)
   - **Date de règlement prévue** : 15/02/2025 (saisi manuellement)
3. **Partie 3** : 4 000 DH par chèque de garantie
   - **Numéro de référence** : CHQ-REF-002 (saisi manuellement)
   - **Banque émettrice** : Attijariwafa Bank (saisi manuellement)
   - **Date de règlement prévue** : 15/03/2025 (saisi manuellement)

### Résultat automatique
- **Échéances** : Générées automatiquement
- **Chèques** : Créés avec les informations manuelles
- **Alertes** : Générées aux dates de règlement prévues

## Interface utilisateur

### Design Bootstrap 5
- **Responsive** : Adaptation mobile et desktop
- **Validation visuelle** : Affichage des erreurs en temps réel
- **Sections conditionnelles** : Affichage/masquage selon le type de garantie

### 🆕 Interface dynamique
- **Champs générés automatiquement** selon le nombre de parties
- **Cartes séparées** pour chaque chèque de garantie
- **Validation contextuelle** selon le type de garantie choisi
- **Feedback immédiat** sur les erreurs de saisie

### Navigation intuitive
- **Guide de création** : Étapes clairement expliquées
- **Résumé de configuration** : Aperçu avant validation
- **Boutons d'action** : Créer ou annuler

## Validation et sécurité

### Validation côté client (JavaScript)
- Montant total > 0
- Nombre de parties entre 1 et 5
- **Champs obligatoires** selon le type de garantie
- **Validation des dates** de règlement prévues

### Validation côté serveur (Django)
- Intégrité des données
- Relations entre modèles
- **Validation des champs manuels** des chèques
- Gestion des erreurs

## Gestion des erreurs

### Types d'erreurs gérées
- **Données manquantes** : Champs obligatoires non remplis
- **Validation métier** : Montants, dates, etc.
- **Erreurs de base de données** : Contraintes, relations
- **🆕 Validation des chèques** : Numéros, banques, dates manquants

### Messages d'erreur
- **Clairs et précis** : Indication du problème
- **Contextuels** : Affichage à côté du champ concerné
- **Validation en temps réel** : Feedback immédiat
- **🆕 Messages spécifiques** pour chaque type de garantie

## Tests et validation

### Script de test
- `test_credit_divise_manuel.py` : Tests automatisés pour la saisie manuelle
- `test_credit_divise_complet.py` : Tests généraux du système
- Validation des formulaires
- Vérification des modèles
- Test des erreurs

### Scénarios de test
1. **Création normale** : Données valides
2. **Garantie unique** : Chèque unique avec tous les champs
3. **🆕 Chèques échelonnés** : Saisie manuelle complète
4. **Validation d'erreurs** : Données manquantes ou invalides
5. **Intégration** : Vérification des modèles créés

## Déploiement et maintenance

### Fichiers modifiés
- `gestion_credits/forms.py` : Nouveaux formulaires avec champs dynamiques
- `gestion_credits/views.py` : Nouvelle vue avec gestion des champs manuels
- `gestion_credits/urls.py` : Nouvelle URL
- `gestion_credits/templates/gestion_credits/credit_divise_complet_form.html` : Template avec interface dynamique

### Migrations
- Aucune migration nécessaire (modèles existants)
- Compatible avec la base de données actuelle

### Configuration
- Aucune configuration supplémentaire requise
- Intégration automatique avec le système existant

## Utilisation recommandée

### Pour les agents
1. **Formation** : Comprendre la différence entre les types de garantie
2. **🆕 Saisie manuelle** : Remplir tous les champs des chèques échelonnés
3. **Validation** : Vérifier les informations avant création
4. **Suivi** : Utiliser les alertes générées automatiquement

### Pour les administrateurs
1. **Monitoring** : Surveiller la création des crédits
2. **Maintenance** : Vérifier les logs et erreurs
3. **Évolution** : Adapter selon les besoins métier

## Avantages du nouveau système

### Pour l'utilisateur
- **Simplicité** : Une seule page au lieu de deux
- **Clarté** : Toutes les informations visibles
- **Validation** : Feedback immédiat sur les erreurs
- **🆕 Flexibilité** : Saisie manuelle des dates et numéros de référence

### Pour le système
- **Performance** : Moins de requêtes à la base
- **Cohérence** : Données validées en une fois
- **Maintenance** : Code plus simple et maintenable
- **🆕 Personnalisation** : Rappels basés sur les dates saisies manuellement

## Évolutions futures

### Fonctionnalités possibles
- **Calcul automatique** des montants par partie
- **Templates** de crédits prédéfinis
- **Import/Export** des données de crédits
- **Workflow** d'approbation des crédits
- **🆕 Gestion des échéances** avec dates personnalisées

### Améliorations techniques
- **API REST** pour l'intégration
- **Notifications** en temps réel
- **Audit trail** des modifications
- **Backup** automatique des données
- **🆕 Interface drag & drop** pour la configuration des chèques

## Support et documentation

### Ressources disponibles
- **Code source** : Commentaires détaillés
- **Tests** : Validation du bon fonctionnement
- **Templates** : Interface utilisateur documentée
- **README** : Guide d'utilisation complet
- **🆕 Scripts de test** : Validation des nouvelles fonctionnalités

### Contact et assistance
- **Développeur** : Support technique
- **Formation** : Guide utilisateur
- **Maintenance** : Mises à jour et corrections
