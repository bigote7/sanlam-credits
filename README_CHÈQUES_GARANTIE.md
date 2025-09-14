# 🏦 **Système de Gestion des Chèques de Garantie - Sanlam Crédits**

## 📋 **Vue d'ensemble**

Ce système permet de gérer les crédits divisés avec des chèques de garantie selon vos spécifications exactes :

- **Crédit de 12 000 DH** pour le client **Hiba Layachi**
- **Divisé en 3 parties** :
  - **Partie 1** : 4 000 DH en espèces (paiement initial)
  - **Partie 2** : 4 000 DH par chèque de garantie
  - **Partie 3** : 4 000 DH par chèque de garantie

## 🔧 **Modifications Apportées**

### 1. **Modèle Cheque (models.py)**

#### Nouveaux Champs Ajoutés :
- `date_reglement_prevu` : Date prévue pour le règlement du chèque
- `statut` : Statut du chèque (garantie, à encaisser, encaissé, reporté, annulé)
- `remarques` : Remarques optionnelles sur le chèque
- `date_modification` : Date de dernière modification

#### Statuts Disponibles :
- **`garantie`** : Chèque de garantie (par défaut)
- **`encaisser`** : À encaisser
- **`encaisse`** : Encaissé
- **`reporte`** : Reporté
- **`annule`** : Annulé

### 2. **Formulaire EcheanceAvecChequeForm (forms.py)**

Nouveau formulaire pour créer des échéances avec ou sans chèques de garantie :

- **Champs obligatoires** : Partie, Montant, Date d'échéance
- **Champs conditionnels** : Si pas en espèces → Numéro chèque, Banque, Date règlement prévu
- **Validation** : Vérification que les champs chèque sont remplis si nécessaire

### 3. **Vue gerer_cheque_garantie (views.py)**

Nouvelle vue pour gérer individuellement chaque chèque de garantie :

- **Marquer pour encaissement** : Change le statut et crée une alerte de dépôt
- **Contacter le client** : Crée une alerte pour demander le règlement en espèces
- **Reporter la date** : Modifie la date de règlement prévue

### 4. **Template gerer_cheque_garantie.html**

Interface moderne pour gérer les chèques avec :
- **Informations détaillées** du chèque
- **Actions disponibles** (encaisser, contacter, reporter)
- **Modal de report** de date
- **Statuts visuels** colorés

## 🚀 **Utilisation du Système**

### **Étape 1 : Créer un Crédit Divisé**

1. Aller sur **"Crédits"** → **"Créer un Crédit"**
2. Choisir **"Crédit Divisé"**
3. Remplir :
   - Client : Hiba Layachi
   - Montant total : 12 000 DH
   - Nombre de parties : 3
   - Description : Détails du crédit

### **Étape 2 : Créer les Échéances**

1. Cliquer sur **"Créer Échéances"**
2. Le système crée automatiquement :
   - **Partie 1** : 4 000 DH en espèces (30 jours)
   - **Partie 2** : 4 000 DH par chèque (60 jours)
   - **Partie 3** : 4 000 DH par chèque (90 jours)

### **Étape 3 : Gérer les Chèques de Garantie**

Pour chaque chèque de garantie, l'agent peut :

#### **Option A : Encaisser le Chèque**
- Cliquer sur **"Gérer"** → **"Marquer à Encaisser"**
- Le statut passe à "À Encaisser"
- Une alerte est créée pour le dépôt

#### **Option B : Contacter le Client**
- Cliquer sur **"Gérer"** → **"Contacter Client"**
- Une alerte est créée pour appeler le client
- Demander le règlement en espèces

#### **Option C : Reporter la Date**
- Cliquer sur **"Gérer"** → **"Reporter"**
- Choisir une nouvelle date de règlement
- Le système crée une nouvelle alerte

## 📊 **Affichage dans l'Interface**

### **Page Détails du Crédit**

1. **Informations Générales** :
   - Client, montant total, type de crédit
   - Résumé des échéances (total, payées, en attente, en retard)

2. **Table des Échéances** :
   - Partie, montant, date, type, statut
   - Actions : traiter, reporter, gérer chèque

3. **Section Chèques de Garantie** :
   - Cartes détaillées pour chaque chèque
   - Informations : montant, numéro, banque, date règlement, statut
   - Bouton "Gérer" pour chaque chèque

### **Page Gestion Chèque**

- **Informations complètes** du chèque
- **Actions disponibles** avec explications
- **Historique** des modifications
- **Modal de report** de date

## 🔔 **Système d'Alertes Automatiques**

### **Types d'Alertes Créées**

1. **Échéance de paiement** : Pour chaque partie
2. **Chèque de garantie** : Pour contacter le client
3. **Dépôt de chèque** : Si marqué pour encaissement
4. **Contact client** : Si demande de règlement en espèces

### **Gestion des Alertes**

- **Page Alertes** : Liste de toutes les alertes
- **Filtres** : Par statut et type
- **Actions** : Marquer comme traité, reporter
- **Statuts visuels** : En attente, traitée, reportée

## 🎯 **Exemple Concret : Hiba Layachi**

### **Scénario Créé**

```
Client : Hiba Layachi
Crédit : 12 000 DH divisé en 3 parties

Partie 1 (30 jours) : 4 000 DH en espèces
Partie 2 (60 jours) : 4 000 DH par chèque de garantie
Partie 3 (90 jours) : 4 000 DH par chèque de garantie
```

### **Workflow Recommandé**

1. **À la date de la Partie 2** :
   - Alerte automatique : "Contacter Hiba pour règlement chèque"
   - Agent choisit : encaisser ou contacter

2. **Si encaissement** :
   - Statut → "À Encaisser"
   - Alerte créée : "Déposer le chèque"

3. **Si contact client** :
   - Alerte créée : "Appeler Hiba pour paiement espèces"

4. **Si report** :
   - Nouvelle date définie
   - Nouvelle alerte programmée

## 🔧 **Configuration Technique**

### **Migrations Appliquées**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **Script de Test**

```bash
python create_credit_hiba.py
```

### **URLs Ajoutées**

- `/cheques/<id>/gerer/` : Gérer un chèque de garantie

## 📱 **Interface Responsive**

- **Bootstrap 5** pour un design moderne
- **Cartes colorées** pour différencier les types
- **Badges visuels** pour les statuts
- **Actions contextuelles** selon le type de chèque

## 🎨 **Codes Couleurs**

- **🔵 Bleu** : Chèques de garantie
- **🟡 Jaune** : À encaisser
- **🟢 Vert** : Encaissé
- **🟣 Violet** : Reporté
- **🔴 Rouge** : Annulé

## 🚀 **Prochaines Étapes**

1. **Tester le système** avec le script de création
2. **Créer des crédits** manuellement via l'interface
3. **Gérer les chèques** selon les besoins
4. **Surveiller les alertes** automatiques

---

## 📞 **Support**

Pour toute question ou modification, consultez la documentation Django ou contactez l'équipe de développement.

**🎉 Le système est maintenant prêt à gérer vos chèques de garantie selon vos spécifications exactes !**
