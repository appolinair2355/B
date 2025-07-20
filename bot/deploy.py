
import logging
import os
import zipfile
import shutil
from telethon import events
from datetime import datetime

logger = logging.getLogger(__name__)

async def handle_deploy(event, client):
    """
    Handle deployment command - creates ZIP file with all bot files
    Premium feature for licensed users
    """
    try:
        user_id = event.sender_id
        

        
        await event.respond("📦 **Création du package de déploiement...**\n\n⏳ Préparation des fichiers en cours...")
        
        # Create deployment ZIP
        zip_path = await create_deployment_zip()
        
        if zip_path and os.path.exists(zip_path):
            # Send the ZIP file
            await client.send_file(
                user_id,
                zip_path,
                caption="""
✅ **Package de déploiement TeleFeed**

📁 **Contenu du package :**
• Tous les fichiers du bot
• Configuration de déploiement
• Variables d'environnement (.env.example)
• Documentation complète

🚀 **Prêt pour le déploiement sur Render.com**

📋 **Instructions :**
1. Décompressez le fichier ZIP
2. Configurez vos variables d'environnement
3. Déployez sur Render.com
4. Votre bot sera opérationnel !
                """,
                attributes=[],
                force_document=True
            )
            
            # Clean up
            os.remove(zip_path)
            logger.info(f"Deployment package sent to user {user_id}")
            
        else:
            await event.respond("❌ **Erreur lors de la création du package**\n\nVeuillez réessayer plus tard.")
            
    except Exception as e:
        logger.error(f"Error in deploy handling: {e}")
        await event.respond("❌ Erreur lors du traitement du déploiement. Veuillez réessayer.")

async def create_deployment_zip():
    """Create a ZIP file with all necessary deployment files INCLUDING FOLDERS"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"TeleFeed_deployment_{timestamp}.zip"
        zip_path = os.path.join(os.getcwd(), zip_filename)
        
        # Individual files to include
        files_to_include = [
            'main.py',
            'requirements.txt',
            'Procfile',
            'runtime.txt',
            '.env.example',
            'user_data.json',
            'http_server.py',
            'keep_alive.py',
            'web_interface.py',
            'replit_always_on.py',
            'pyproject.toml',
            'render.yaml',
            '.replit',
            'DEPLOYMENT_GUIDE.md',
            'KEEP_ALIVE_GUIDE.md',
            'REPLIT_ALWAYS_ON_GUIDE.md'
        ]
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add individual files
            for item in files_to_include:
                if os.path.exists(item):
                    zipf.write(item, os.path.basename(item))
                    logger.info(f"Added file to ZIP: {item}")
            
            # Add entire bot directory with structure
            bot_dir = 'bot'
            if os.path.exists(bot_dir):
                for root, dirs, files in os.walk(bot_dir):
                    # Skip __pycache__ directories
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    
                    for file in files:
                        if not file.endswith('.session') and not file.endswith('.pyc'):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file_path)
                            logger.info(f"Added bot file to ZIP: {file_path}")
            
            # Add entire config directory with structure
            config_dir = 'config'
            if os.path.exists(config_dir):
                for root, dirs, files in os.walk(config_dir):
                    # Skip __pycache__ directories
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    
                    for file in files:
                        if not file.endswith('.pyc'):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file_path)
                            logger.info(f"Added config file to ZIP: {file_path}")
            
            # Add templates directory
            templates_dir = 'templates'
            if os.path.exists(templates_dir):
                for root, dirs, files in os.walk(templates_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, file_path)
                        logger.info(f"Added template file to ZIP: {file_path}")
            
            # Add logs directory (create empty if doesn't exist)
            logs_dir = 'logs'
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            if os.path.exists(logs_dir):
                for root, dirs, files in os.walk(logs_dir):
                    # Add directory even if empty
                    zipf.writestr(f"{logs_dir}/", "")
                    for file in files:
                        if not file.endswith('.log'):  # Skip log files for security
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file_path)
                            logger.info(f"Added logs file to ZIP: {file_path}")
            
            # Add deployment packages for reference
            deployment_dirs = ['deployment_files', 'final_deployment']
            for dep_dir in deployment_dirs:
                if os.path.exists(dep_dir):
                    for root, dirs, files in os.walk(dep_dir):
                        # Skip __pycache__ directories
                        dirs[:] = [d for d in dirs if d != '__pycache__']
                        
                        for file in files:
                            if not file.endswith('.session') and not file.endswith('.pyc'):
                                file_path = os.path.join(root, file)
                                # Store with original path structure
                                zipf.write(file_path, file_path)
                                logger.info(f"Added deployment file to ZIP: {file_path}")
            
            # Create deployment instructions
            instructions = f"""
# 🚀 PACKAGE DE DÉPLOIEMENT TELEFEED COMPLET

## 📁 CONTENU DU PACKAGE :

### Fichiers principaux :
- main.py (Point d'entrée)
- requirements.txt (Dépendances)
- .env.example (Variables d'environnement)
- Procfile (Configuration Heroku/Render)
- runtime.txt (Version Python)

### Dossiers inclus :
- bot/ (Tous les modules du bot)
- config/ (Configuration)
- templates/ (Interface web)
- logs/ (Dossier de logs)
- deployment_files/ (Configurations de déploiement)
- final_deployment/ (Version finale)

### Fichiers de support :
- http_server.py (Serveur web)
- keep_alive.py (Maintien d'activité)
- web_interface.py (Interface web)
- replit_always_on.py (Always On Replit)

## 🔧 DÉPLOIEMENT :

1. **Replit Always On :**
   - Importez tous les fichiers
   - Configurez les variables d'environnement
   - Activez Always On

2. **Render/Heroku :**
   - Utilisez les fichiers de deployment_files/
   - Configurez les variables d'environnement
   - Déployez avec Procfile

3. **Configuration :**
   - Copiez .env.example vers .env
   - Remplissez vos clés API
   - Lancez avec python main.py

## ⚠️ IMPORTANT :
- N'oubliez pas de configurer vos variables d'environnement
- Les fichiers .session sont exclus pour la sécurité
- Consultez DEPLOYMENT_GUIDE.md pour plus de détails

Créé le : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            
            zipf.writestr("DEPLOYMENT_INSTRUCTIONS.md", instructions)
            if os.path.exists(config_dir):
                for file in os.listdir(config_dir):
                    file_path = os.path.join(config_dir, file)
                    if os.path.isfile(file_path) and '__pycache__' not in file:
                        zipf.write(file_path, file)
                        logger.info(f"Added file to ZIP: {file}")
            
            # Create deployment instructions
            instructions = """
# TeleFeed Bot - Instructions de Déploiement

## Configuration requise

1. **Variables d'environnement (.env) :**
   - API_ID=votre_api_id
   - API_HASH=votre_api_hash
   - BOT_TOKEN=votre_bot_token
   - DATABASE_URL=votre_database_url
   - ADMIN_ID=votre_admin_id

2. **Base de données :**
   - PostgreSQL requis
   - Configurez DATABASE_URL avec vos credentials

## Déploiement sur Render.com

1. Créez un nouveau service Web
2. Connectez votre repository
3. Configurez les variables d'environnement
4. Le bot se lancera automatiquement avec `python main.py`

## Fonctionnalités incluses

- ✅ Gestion des sessions persistantes
- ✅ Redirections automatiques
- ✅ Système de licences
- ✅ Paiements intégrés
- ✅ Administration complète

## Support

Pour toute assistance, contactez le support TeleFeed.
            """
            
            zipf.writestr("DEPLOYMENT_INSTRUCTIONS.md", instructions)
            
            # Create .env.example if it doesn't exist
            env_example = """
# TeleFeed Bot Configuration
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://user:password@host:port/database
ADMIN_ID=your_admin_id_here
            """
            
            if not os.path.exists('.env.example'):
                zipf.writestr(".env.example", env_example)
        
        logger.info(f"Deployment ZIP created: {zip_path}")
        return zip_path
        
    except Exception as e:
        logger.error(f"Error creating deployment ZIP: {e}")
        return None

async def is_premium_user(user_id):
    """Check if user has premium access"""
    from bot.database import is_user_licensed
    return await is_user_licensed(user_id)
