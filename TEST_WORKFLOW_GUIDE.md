# Guide de Test du Workflow GitPusher

## 🚀 Comment tester le workflow complet

### Étape 1 : Connexion avec GitHub OAuth

1. Allez sur votre application GitPusher
2. Cliquez sur **"Login / Sign up"**
3. Cliquez sur **"Continue with GitHub"**
4. Connectez-vous à GitHub et autorisez l'application
5. Vous serez automatiquement redirigé vers le dashboard

### Étape 2 : Créer un nouveau projet

1. Dans le dashboard, cliquez sur **"New workflow"** (bouton cyan avec gradient)
2. Un nouveau projet sera créé avec un nom auto-généré (ex: `auto-repo-xxxxx`)
3. Le projet apparaîtra dans la liste de gauche avec le statut "pending"

### Étape 3 : Uploader des fichiers

1. Sélectionnez le projet dans la liste (il sera surligné en cyan)
2. Dans la section "Upload files" à droite :
   - Cliquez sur le bouton "Choose files" ou
   - Glissez-déposez des fichiers directement
3. Fichiers de test disponibles :
   - `/tmp/test_project.py` - Un simple calculateur Python
   - Ou utilisez vos propres fichiers !

### Étape 4 : Lancer l'automatisation

1. Après avoir uploadé les fichiers, cliquez sur **"Launch automation"**
2. Le système va :
   - ✨ Analyser vos fichiers avec l'IA
   - 📝 Générer un README.md automatique
   - 💬 Créer des messages de commit intelligents
   - 🎯 Créer un nouveau repository GitHub
   - 🚀 Pousser tous vos fichiers sur GitHub

### Étape 5 : Voir le résultat

1. Une fois terminé (status devient "done"), vous verrez :
   - Un lien vers votre nouveau repository GitHub
   - Le statut changera de "pending" à "done" (vert)
2. Cliquez sur "Open repo" pour voir votre repository sur GitHub

## 🎯 Ce que l'IA va générer

- **README.md** : Description automatique du projet basée sur vos fichiers
- **Commits** : Messages de commit intelligents en français ou anglais
- **Structure** : Organisation propre de vos fichiers

## ⚙️ Configuration actuelle

✅ **Emergent LLM Key** : Configurée (pour l'IA)
✅ **GitHub OAuth** : Configuré (Client ID: Ov23liJwKIdDCi58Wyu1)
✅ **Backend** : Fonctionnel
✅ **Frontend** : Modernisé avec dashboard sophistiqué

## 🐛 En cas de problème

- Vérifiez que vous êtes bien connecté avec GitHub
- Assurez-vous d'avoir uploadé au moins un fichier
- Vérifiez les logs dans "Historique des jobs"
- Le token GitHub doit avoir les permissions `repo`

## 📊 Statistiques du dashboard

Le dashboard affiche maintenant :
- **Total Projects** : Nombre total de projets
- **Completed** : Projets terminés avec succès
- **Pending** : Projets en attente
- **Total Jobs** : Nombre total d'exécutions

Profitez de votre workflow Git automatisé ! 🎉
