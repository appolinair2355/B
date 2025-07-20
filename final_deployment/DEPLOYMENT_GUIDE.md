# TeleFeed Bot - Guide de Déploiement Render.com

## 🚀 Déploiement sur Render.com

### 1. Préparation des fichiers

Les fichiers nécessaires pour le déploiement sont :
- `main.py` - Point d'entrée du bot
- `requirements.txt` - Dépendances Python
- `runtime.txt` - Version Python
- `render.yaml` - Configuration Render
- `.env.example` - Exemple de variables d'environnement
- Dossier `bot/` - Code principal du bot
- Dossier `config/` - Configuration du bot

### 2. Configuration des variables d'environnement

Dans le tableau de bord Render, ajoutez ces variables :

```
API_ID=votre_api_id_telegram
API_HASH=votre_api_hash_telegram
BOT_TOKEN=votre_bot_token
DATABASE_URL=votre_url_postgresql
ADMIN_ID=votre_user_id_admin
```

### 3. Base de données PostgreSQL

Render propose une base de données PostgreSQL gratuite :
1. Créez un service PostgreSQL sur Render
2. Copiez l'URL de connexion
3. Ajoutez-la dans DATABASE_URL

### 4. Type de service

- **Type** : Background Worker (pas Web Service!)
- **Runtime** : Python
- **Build Command** : `pip install -r requirements.txt`
- **Start Command** : `python main.py`

⚠️ **IMPORTANT** : Votre bot Telegram doit être déployé comme un **Background Worker**, pas comme un Web Service. C'est pourquoi vous aviez une page blanche !

### 5. Obtention des clés Telegram

1. Allez sur https://my.telegram.org/
2. Créez une nouvelle application
3. Notez API_ID et API_HASH
4. Créez un bot via @BotFather
5. Notez le BOT_TOKEN

### 6. Configuration finale

Une fois déployé, le bot sera accessible 24/7 sur Render.com

## ❗ Notes importantes

- Gardez vos clés API secrètes
- La base de données est nécessaire pour la persistance
- Les sessions Telegram sont automatiquement gérées
- Le bot redémarre automatiquement en cas d'erreur

## 🔄 Système Keep-Alive Intégré

Votre bot inclut un système de maintien d'activité automatique :
- **Messages de réveil personnalisés** entre le bot et Replit
- **Serveur HTTP intégré** pour éviter les timeouts
- **Surveillance automatique 24/7** des services
- **Redémarrage automatique** en cas d'inactivité

Commande admin : `/keepalive` pour vérifier le statut

## 🔧 Dépannage

Si le déploiement échoue :
1. Vérifiez les variables d'environnement
2. Assurez-vous que la base de données est accessible
3. Vérifiez les logs dans le tableau de bord Render
4. Testez l'endpoint `/status` pour le serveur HTTP
5. Contactez le support si nécessaire