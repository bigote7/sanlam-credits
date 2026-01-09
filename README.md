# 🏦 Sanlam Crédits - Application de Gestion des Crédits Clients

## 📋 Description

**Sanlam Crédits** est une application web Django complète développée pour la société d'assurance Sanlam afin de gérer les crédits clients et envoyer des rappels automatiques aux agents pour ne pas oublier les paiements.

## ✨ Fonctionnalités Principales

### 1. 🧑‍💼 Gestion des Clients
- **CRUD complet** : Création, lecture, mise à jour et suppression des clients
- **Informations uniques** : CIN (unique), téléphone (unique)
- **Données complètes** : Nom, prénom, email, adresse, dates de création/modification

### 2. 💳 Gestion des Crédits

#### Type 1 : Crédit Divisé en Plusieurs Parties (1 à 5)
- **Saisie flexible** : Montant total, nombre de parties, montant et date de chaque partie
- **Règles métier** :
  - La première partie est **toujours en espèces**
  - Les autres parties sont sous forme de **chèques de garantie**
  - Gestion intelligente des échéances avec rappels automatiques

#### Type 2 : Crédit Unique avec Date ou Durée
- **Flexibilité temporelle** : Saisie en jours, semaines, mois ou date exacte
- **Calcul automatique** : L'application calcule automatiquement la date d'échéance
- **Rappels intelligents** : Alertes automatiques à la date prévue

### 3. 🔔 Système d'Alertes et Rappels
- **Tableau de bord intelligent** : Échéances aujourd'hui, cette semaine et en retard
- **Gestion des alertes** : Possibilité de marquer comme traitées ou reportées
- **Reports flexibles** : Chaque échéance peut avoir un report unique sans affecter les autres
- **Notifications automatiques** : Rappels quotidiens pour les agents

### 4. 🏦 Gestion des Chèques de Garantie
- **Décision d'encaissement** : L'agent choisit d'encaisser ou non le chèque
- **Rappels intelligents** :
  - Si encaissé → Rappel pour dépôt du chèque
  - Si non encaissé → Rappel "appeler le client pour paiement en espèces"

## 🏗️ Architecture Technique

### Modèles de Données
- **Client** : Informations personnelles et de contact
- **Credit** : Gestion des crédits avec types et montants
- **Echeance** : Échéances de paiement avec statuts
- **Cheque** : Chèques de garantie et leur gestion
- **Alerte** : Système de rappels et notifications
- **ReportEcheance** : Historique des reports d'échéances

### Technologies Utilisées
- **Backend** : Django 5.2.5
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Frontend** : Bootstrap 5.3.0 + Bootstrap Icons
- **Authentification** : Système d'utilisateurs Django intégré
- **Interface d'administration** : Admin Django personnalisé

### Structure du Projet
```
sanlam_credits/
├── gestion_credits/          # Application principale
│   ├── models.py            # Modèles de données
│   ├── views.py             # Logique métier
│   ├── forms.py             # Formulaires
│   ├── admin.py             # Interface d'administration
│   ├── urls.py              # Configuration des URLs
│   └── templates/           # Templates HTML
├── sanlam_credits/          # Configuration du projet
│   ├── settings.py          # Paramètres Django
│   └── urls.py              # URLs principales
├── manage.py                # Script de gestion Django
├── create_sample_data.py    # Script de données d'exemple
└── README.md                # Ce fichier
```

## 🚀 Installation et Configuration

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)
- Git (pour cloner le projet)

### 1. Cloner le Projet
```bash
git clone <url-du-repo>
cd sanlam_credits
```

### 2. Créer l'Environnement Virtuel
```bash
python -m venv venv
```

### 3. Activer l'Environnement Virtuel
**Windows :**
```bash
venv\Scripts\activate
```

**Linux/Mac :**
```bash
source venv/bin/activate
```

### 4. Installer les Dépendances
```bash
pip install django
```

### 5. Configurer la Base de Données
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un Super Utilisateur
```bash
python manage.py createsuperuser
```

### 7. Créer les Données d'Exemple
```bash
python create_sample_data.py
```

### 8. Démarrer le Serveur
```bash
python manage.py runserver
```

L'application sera accessible à l'adresse : **http://127.0.0.1:8000/**

## 👥 Utilisateurs de Test

### Agent Sanlam
- **Nom d'utilisateur** : `agent_sanlam`
- **Mot de passe** : `sanlam123`
- **Rôle** : Agent de crédit avec accès complet

### Super Utilisateur
- **Nom d'utilisateur** : `LABIB` (ou celui que vous avez créé)
- **Mot de passe** : Celui que vous avez défini
- **Rôle** : Administrateur avec accès à l'interface d'administration

## 📊 Exemple Concret Implémenté

### Cas d'Usage : Crédit Immobilier de 12 000 DH

**Client** : Ahmed Alaoui  
**Montant total** : 12 000 DH  
**Nombre de parties** : 4

#### Détail des Échéances :

1. **Partie 1** : 3 000 DH en espèces (01/01/2025)
   - Paiement immédiat en espèces
   - Alerte créée pour rappel

2. **Partie 2** : 3 000 DH (chèque garantie) → 01/04/2025
   - **Scénario** : Chèque non encaissé
   - **Action** : Rappel "appeler le client pour paiement en espèces"
   - **Alerte** : Créée automatiquement

3. **Partie 3** : 3 000 DH (chèque garantie) → 01/07/2025
   - Rappel prévu à la date d'échéance
   - Gestion standard du chèque de garantie

4. **Partie 4** : 3 000 DH (chèque garantie) → 01/10/2025
   - Rappel prévu à la date d'échéance
   - Gestion standard du chèque de garantie

## 🔧 Fonctionnalités Avancées

### Gestion des Reports
- **Report unique** : Chaque échéance peut être reportée individuellement
- **Historique** : Conservation de l'historique des reports
- **Flexibilité** : Les reports n'affectent pas les autres échéances

### Système d'Alertes Intelligent
- **Types d'alertes** : Échéance, rappel, chèque garantie, retard
- **Statuts** : En attente, traitée, reportée
- **Priorisation** : Alertes urgentes pour les échéances en retard

### Interface d'Administration
- **Vue d'ensemble** : Statuts des crédits et échéances
- **Filtres avancés** : Recherche et tri par différents critères
- **Actions en lot** : Gestion efficace des données

## 📱 Interface Utilisateur

### Design Responsive
- **Bootstrap 5** : Interface moderne et responsive
- **Navigation intuitive** : Sidebar avec accès rapide aux fonctionnalités
- **Tableaux de bord** : Visualisation claire des données importantes

### Composants Visuels
- **Cartes statistiques** : Vue d'ensemble des métriques clés
- **Tableaux interactifs** : Données organisées avec actions rapides
- **Badges colorés** : Statuts visuels pour une compréhension immédiate
- **Icônes Bootstrap** : Interface intuitive et professionnelle

## 🔒 Sécurité

### Authentification
- **Login obligatoire** : Toutes les pages protégées
- **Gestion des sessions** : Sécurisation des connexions
- **Permissions** : Contrôle d'accès basé sur les rôles

### Validation des Données
- **Formulaires sécurisés** : Protection CSRF intégrée
- **Validation côté serveur** : Vérification des données
- **Sanitisation** : Protection contre les injections

## 🚀 Déploiement en Production

### Recommandations
- **Base de données** : PostgreSQL pour la production
- **Serveur web** : Nginx + Gunicorn
- **Environnement** : Linux avec Python 3.8+
- **SSL** : Certificat HTTPS obligatoire

### Variables d'Environnement
```bash
DEBUG=False
SECRET_KEY=<clé-secrète-production>
DATABASE_URL=<url-base-de-données>
ALLOWED_HOSTS=<domaines-autorisés>
```

## 📈 Évolutions Futures

### Fonctionnalités Planifiées
- **API REST** : Interface programmatique
- **Notifications push** : Alertes en temps réel
- **Rapports avancés** : Analytics et métriques
- **Intégration SMS** : Rappels par message
- **Application mobile** : Accès mobile aux agents

### Améliorations Techniques
- **Cache Redis** : Performance des requêtes
- **Tâches asynchrones** : Traitement en arrière-plan
- **Tests automatisés** : Couverture de code
- **CI/CD** : Déploiement automatisé

## 🤝 Contribution

### Comment Contribuer
1. **Fork** le projet
2. **Créer** une branche pour votre fonctionnalité
3. **Commiter** vos changements
4. **Pousser** vers la branche
5. **Créer** une Pull Request

### Standards de Code
- **PEP 8** : Style de code Python
- **Docstrings** : Documentation des fonctions
- **Tests** : Couverture de code minimale
- **Commits** : Messages clairs et descriptifs

## 📞 Support

### Contact
- **Développeur** : LABIB LAYACHI
- **Email** : support@sanlam.ma
- **Documentation** : Ce fichier README C.P.LAYACHI LABIB

### Ressources
- **Documentation Django** : https://docs.djangoproject.com/
- **Bootstrap** : https://getbootstrap.com/
- **Python** : https://www.python.org/

## 📄 Licence

Ce projet est développé pour **Sanlam** et est destiné à un usage interne.

---

**🎯 Sanlam Crédits** - Simplifiez la gestion de vos crédits clients avec une solution moderne et intuitive !
