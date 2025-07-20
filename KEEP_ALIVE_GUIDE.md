# 🔄 Système Keep-Alive TeleFeed

## Vue d'ensemble

Le système Keep-Alive maintient votre bot TeleFeed actif 24/7 sur Replit, même lorsque vous n'êtes pas en ligne. Il utilise un serveur HTTP intégré et un système de surveillance automatique.

## 🎯 Fonctionnalités

### Messages de Réveil Automatiques
- **Si le bot dort** → Replit envoie : "🔔 Replit: Kouamé réveil toi"
- **Bot répond** → "✅ Bot: D'accord Replit"
- **Si Replit dort** → Bot envoie : "🔔 Bot: Replit réveil toi" 
- **Replit répond** → "✅ Replit: D'accord Kouamé"

### Surveillance Automatique
- **Ping toutes les 2 minutes** pour maintenir l'activité
- **Vérification toutes les 5 minutes** de l'état des services
- **Réveil automatique après 10 minutes** d'inactivité
- **Serveur HTTP sur port 5000** (ou PORT défini)

## 🚀 Démarrage Automatique

Le système se lance automatiquement avec le bot :

```python
# main.py démarre :
1. Serveur HTTP en arrière-plan
2. Bot Telegram principal
3. Système Keep-Alive automatique
```

## 🌐 Endpoints HTTP

### `/` - Page d'accueil
Affiche le statut général du serveur

### `/ping` - Ping rapide
Maintient l'activité du serveur

### `/wake-up` - Réveil forcé
Réveille le serveur (utilisé par le bot)

### `/status` - Statut détaillé
Informations complètes sur l'activité

### `/health` - Health check
Vérification de santé pour monitoring

## 📱 Commandes Bot

### `/keepalive` (Admin seulement)
Vérifie le statut du système Keep-Alive

## 🔧 Configuration Automatique

### Variables d'environnement
- `PORT` : Port du serveur HTTP (défaut: 5000)
- `REPLIT_URL` : URL automatique de votre Replit
- Toutes les variables bot habituelles

### Logs en temps réel
```
🤖 Bot ping - HH:MM:SS
🌐 Serveur ping - HH:MM:SS
🔔 Message de réveil envoyé
✅ Service réveillé avec succès
```

## 📊 Monitoring

Le système surveille :
- **Activité du bot** (commandes, messages)
- **Activité du serveur** (requêtes HTTP)
- **Durée d'inactivité** de chaque service
- **Nombre de réveils** effectués

## 🔄 Cycle de Maintenance

1. **Activité normale** → Tout fonctionne
2. **Inactivité détectée** → Déclenchement du réveil
3. **Message d'éveil** → Service réveillé
4. **Confirmation** → Retour à l'activité normale

## 💪 Avantages

- ✅ **Bot actif 24/7** même sans interaction
- ✅ **Pas de timeout Replit** grâce aux requêtes HTTP
- ✅ **Redémarrage automatique** en cas de problème
- ✅ **Messages personnalisés** de réveil
- ✅ **Monitoring complet** des services
- ✅ **Aucune configuration manuelle** requise

## 🚨 En cas de problème

Si le système ne fonctionne pas :

1. **Vérifiez les logs** dans la console Replit
2. **Testez l'endpoint** `/status` manuellement
3. **Redémarrez le bot** si nécessaire
4. **Contactez le support** si le problème persiste

Le système est conçu pour être robuste et se relancer automatiquement en cas d'erreur.