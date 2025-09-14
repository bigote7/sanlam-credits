# 🗑️ **SUPPRESSION COMPLÈTE DE LA BASE DE DONNÉES**

## ⚠️ **ATTENTION : ACTION IRRÉVERSIBLE !**

Ce document explique comment supprimer **TOUS** les clients et crédits de votre base de données.

## 📊 **État actuel de votre base :**

- **Clients :** 6
- **Crédits :** 4  
- **Échéances :** 7
- **Chèques :** 4
- **Alertes :** 7
- **Actions historiques :** 23

## 🚨 **Ce qui sera supprimé :**

1. **TOUS les clients** (6 clients)
2. **TOUS les crédits** (4 crédits)
3. **TOUTES les échéances** (7 échéances)
4. **TOUS les chèques** (4 chèques)
5. **TOUTES les alertes** (7 alertes)
6. **TOUT l'historique des actions** (23 actions)

## 🔧 **Comment procéder :**

### **Étape 1 : Vérifier l'état actuel**
```bash
python verifier_etat.py
```

### **Étape 2 : Supprimer tout (IRRÉVERSIBLE)**
```bash
python supprimer_tout.py
```

## ⚡ **Processus de suppression :**

Le script supprime dans cet ordre pour éviter les erreurs de clés étrangères :

1. **Échéances** (dépendent des crédits)
2. **Chèques** (dépendent des échéances)
3. **Alertes** (dépendent des échéances)
4. **Reports d'échéances**
5. **Historique des actions**
6. **Crédits** (dépendent des clients)
7. **Clients** (en dernier)

## ✅ **Après suppression :**

- Base de données **complètement vide**
- Tous les compteurs à **0**
- Prêt pour un **redémarrage propre**

## 🆘 **En cas de problème :**

Si une erreur survient pendant la suppression :
1. Vérifiez les logs d'erreur
2. Relancez le script
3. En dernier recours, supprimez manuellement via l'admin Django

## 💡 **Recommandations :**

- **Faites une sauvegarde** avant de commencer
- **Vérifiez** que vous êtes sur le bon environnement
- **Confirmez** deux fois avant la suppression
- **Testez** sur un environnement de développement d'abord

## 🎯 **Utilisation typique :**

```bash
# 1. Vérifier l'état
python verifier_etat.py

# 2. Si vous êtes sûr, supprimer tout
python supprimer_tout.py

# 3. Vérifier que tout est supprimé
python verifier_etat.py
```

---

**⚠️  RAPPEL : Cette action est IRRÉVERSIBLE ! Assurez-vous de vouloir vraiment tout supprimer !**
