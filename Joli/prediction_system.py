import logging
import re
import random
from datetime import datetime
from typing import List, Optional, Tuple
from bot.connection import active_connections

logger = logging.getLogger(__name__)

class PredictionSystem:
    """Système de prédiction automatique pour les cartes"""

    def __init__(self):
        self.predictions_active = False
        self.card_suits = {
            '♠': 'spade',    # pique
            '♠️': 'spade',   # pique emoji
            '♣': 'club',     # trèfle
            '♣️': 'club',    # trèfle emoji
            '♥': 'heart',    # coeur
            '♥️': 'heart',   # coeur emoji
            '♦': 'diamond',  # carreau
            '♦️': 'diamond', # carreau emoji
            'S': 'spade',    # spade letter
            'C': 'club',     # club letter
            'H': 'heart',    # heart letter
            'D': 'diamond'   # diamond letter
        }
        self.card_colors = {
            'spade': 'noir',
            'club': 'noir',
            'heart': 'rouge', 
            'diamond': 'rouge'
        }
        self.last_predictions = {}  # Pour éviter les doublons

    def is_active(self):
        """Vérifier si les prédictions sont actives"""
        return self.predictions_active
    
    def is_enabled(self):
        """Alias pour is_active pour compatibilité web interface"""
        return self.predictions_active

    def start_predictions(self):
        """Démarrer les prédictions automatiques"""
        self.predictions_active = True
        logger.info("🔮 Système de prédictions automatiques activé")
        return "✅ Prédictions automatiques activées"

    def stop_predictions(self):
        """Arrêter les prédictions automatiques"""
        self.predictions_active = False
        logger.info("🛑 Système de prédictions automatiques désactivé")
        return "❌ Prédictions automatiques désactivées"
    
    def enable_predictions(self):
        """Alias pour start_predictions pour compatibilité web interface"""
        return self.start_predictions()
        return self.start_predictions()

    def get_status(self):
        """Obtenir le statut du système"""
        return {
            'active': self.predictions_active,
            'total_predictions': len(self.last_predictions)
        }

    def _extract_cards_from_parentheses(self, text: str) -> List[Tuple[str, str]]:
        """Extrait les cartes des parenthèses avec leur couleur"""
        cards = []

        # Rechercher les parenthèses avec des cartes
        parentheses_pattern = r'\(([^)]+)\)'
        matches = re.findall(parentheses_pattern, text)

        for match in matches:
            # Rechercher les cartes dans chaque parenthèse
            # Format amélioré: 5♦️5♣️3♠️ ou 5♦5♣3♠ ou 5H5C3S ou même 5♦️ 5♣️ 3♠️
            # Supporter les espaces et différents formats

            # Pattern plus flexible pour capturer les cartes
            card_pattern = r'(\d+|[JQKA])([♠♣♥♦️SCHD])[️]?'
            card_matches = re.findall(card_pattern, match, re.IGNORECASE)

            # Si pas de correspondance avec le premier pattern, essayer un pattern plus simple
            if not card_matches:
                # Pattern alternatif pour format comme "5D 5C 3S"
                simple_pattern = r'(\d+|[JQKA])([SCHD])'
                card_matches = re.findall(simple_pattern, match, re.IGNORECASE)

            for value, suit in card_matches:
                color = self._get_card_color(suit)
                cards.append((f"{value}{suit}", color))
                logger.info(f"🎯 Carte détectée: {value}{suit} (couleur: {color})")

        return cards

    def _get_card_color(self, suit: str) -> str:
        """Détermine la couleur d'une carte selon sa couleur"""
        suit = suit.upper().replace('️', '')  # Supprimer les emojis variantes

        # Noir: Pique (♠, S) et Trèfle (♣, C)
        if suit in ['♠', '♣', 'S', 'C']:
            return 'noir'
        # Rouge: Cœur (♥, H) et Carreau (♦, D)  
        elif suit in ['♥', '♦', 'H', 'D']:
            return 'rouge'

        logger.warning(f"⚠️ Couleur de carte inconnue: {suit}")
        return 'inconnu'

    def _has_three_different_colors(self, cards: List[Tuple[str, str]]) -> bool:
        """Vérifie si nous avons au moins 3 cartes de couleurs différentes"""
        if len(cards) < 3:
            return False

        colors = [card[1] for card in cards[:3]]  # Prendre seulement les 3 premières cartes
        unique_colors = set(colors)

        logger.info(f"🎨 Couleurs des 3 premières cartes: {colors}")
        logger.info(f"🎨 Couleurs uniques: {unique_colors}")

        # Nous avons besoin d'au moins 2 couleurs différentes (noir et rouge)
        if len(unique_colors) >= 2:
            # Vérifier que nous avons des cartes noires et rouges
            has_black = 'noir' in unique_colors
            has_red = 'rouge' in unique_colors

            logger.info(f"✅ Cartes noires: {has_black}, Cartes rouges: {has_red}")

            if has_black and has_red:
                logger.info("🎯 CONDITION REMPLIE: 3 cartes avec couleurs différentes détectées!")
                return True

        logger.info("❌ Condition non remplie: pas assez de couleurs différentes")
        return False

    def _generate_prediction(self):
        """Générer un nombre de prédiction aléatoire"""
        return random.randint(1, 9)

    def _get_current_time(self):
        """Obtenir l'heure actuelle"""
        return datetime.now().strftime("%H:%M:%S")

    async def analyze_message(self, message_text: str, source_name: str = "Canal Inconnu") -> Optional[str]:
        """Analyse un message pour détecter les prédictions"""
        if not self.active:
            return None

        try:
            logger.info(f"🔍 Analyse du message depuis {source_name}: {message_text[:100]}...")

            # Extraire les cartes des parenthèses
            cards = self._extract_cards_from_parentheses(message_text)

            logger.info(f"🎯 Cartes extraites: {cards}")

            if len(cards) < 3:
                logger.info(f"❌ Pas assez de cartes détectées ({len(cards)}/3)")
                return None

            # Vérifier si nous avons 3 cartes de couleurs différentes
            if self._has_three_different_colors(cards):
                # Générer la prédiction
                predicted_number = self._generate_prediction()
                self.total_predictions += 1

                prediction_message = f"""
🔮 **PRÉDICTION AUTOMATIQUE DÉTECTÉE**

📍 **Source:** {source_name}
🃏 **Cartes détectées:** {', '.join([card[0] for card in cards[:3]])}
🎨 **Couleurs:** {', '.join([card[1] for card in cards[:3]])}
🎯 **Prédiction:** Le joueur recevra **3K**
🔢 **Numéro prédit:** {predicted_number}

⏰ **Heure:** {self._get_current_time()}
📊 **Total prédictions:** {self.total_predictions}
"""

                logger.info(f"🔮 Prédiction générée depuis {source_name}: {predicted_number}")
                return prediction_message
            else:
                logger.info(f"❌ Pas assez de couleurs différentes parmi: {[card[1] for card in cards]}")

        except Exception as e:
            logger.error(f"Erreur analyse message: {e}")

        return None

# Instance globale du système de prédiction
prediction_system = PredictionSystem()