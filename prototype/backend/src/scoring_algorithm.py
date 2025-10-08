from datetime import datetime, timedelta
from typing import Dict, Optional
import math

class ScoringAlgorithm:
    
    @staticmethod
    def calculer_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance en mètres entre deux points GPS (formule haversine)"""
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Rayon de la Terre en mètres
        return c * r
    
    @staticmethod
    def obtenir_moment_journee(heure: int) -> str:
        """Détermine le moment de la journée"""
        if 6 <= heure < 12:
            return "matin"
        elif 12 <= heure < 18:
            return "apres-midi"
        elif 18 <= heure < 23:
            return "soiree"
        else:
            return "nuit"
    
    @staticmethod
    def calculer_score_temporel(evenement, maintenant: datetime) -> float:
        """Score basé sur la disponibilité et l'urgence temporelle"""
        score = 0.0
        
        # Convertir date_debut en datetime si nécessaire
        date_debut = evenement.date_debut
        if not isinstance(date_debut, datetime):
            date_debut = datetime.combine(date_debut, datetime.min.time())
        
        date_fin = evenement.date_fin or date_debut
        if not isinstance(date_fin, datetime):
            date_fin = datetime.combine(date_fin, datetime.max.time())
        
        # 1. Disponibilité immédiate (40 points)
        if date_debut.date() <= maintenant.date() <= date_fin.date():
            if evenement.heure_debut and evenement.heure_fin:
                try:
                    h_debut = int(evenement.heure_debut.split(':')[0])
                    h_fin = int(evenement.heure_fin.split(':')[0])
                    heure_actuelle = maintenant.hour
            
                    # Si c'est aujourd'hui et que l'heure de début est passée, score = 0
                    if date_debut.date() == maintenant.date() and h_debut < heure_actuelle:
                        return 0  # Événement déjà commencé ou terminé
            
                    if h_debut <= heure_actuelle <= h_fin:
                        score += 40
                    else:   
                        # Calcul du temps d'attente
                        if heure_actuelle < h_debut:
                            heures_attente = h_debut - heure_actuelle
                            if heures_attente < 2:
                                score += 30
                            elif heures_attente < 4:
                                score += 15
                except:
                    score += 40
            else:
                score += 40  # Événement toute la journée
        
        # 2. Urgence temporelle (30 points)
        jours_restants = (date_fin.date() - maintenant.date()).days
        if jours_restants == 0:
            score += 30  # Dernier jour !
        elif jours_restants <= 3:
            score += 20
        elif jours_restants <= 7:
            score += 10
        elif jours_restants <= 30:
            score += 5
        
        # 3. Concordance moment optimal (30 points)
        moment_actuel = ScoringAlgorithm.obtenir_moment_journee(maintenant.hour)
        if evenement.meilleur_moment == moment_actuel:
            score += 30
        elif evenement.meilleur_moment:
            score += 15  # Pas optimal mais acceptable
        else:
            score += 20  # Pas de préférence = neutre
        
        return score
    
    @staticmethod
    def calculer_score_distance(
        evenement, 
        lat_user: float, 
        lon_user: float, 
        temps_disponible: Optional[int] = None
    ) -> float:
        """Score basé sur la proximité et l'accessibilité"""
        score = 0.0
        
        distance_m = ScoringAlgorithm.calculer_distance(
            lat_user, lon_user, 
            evenement.latitude, evenement.longitude
        )
        
        # 1. Distance physique (60 points)
        if distance_m < 500:
            score += 60
        elif distance_m < 1000:
            score += 50
        elif distance_m < 2000:
            score += 35
        elif distance_m < 5000:
            score += 20
        elif distance_m < 10000:
            score += 10
        else:
            score += 5
        
        # 2. Compatibilité temps disponible (40 points)
        if temps_disponible:
            # Estimation temps trajet (moyenne 15 min/km à pied)
            temps_trajet = (distance_m / 1000) * 15
            temps_total = temps_trajet * 2 + evenement.duree_moyenne_visite  # Aller-retour
            
            ratio = temps_total / temps_disponible
            if ratio <= 0.8:
                score += 40  # Confortable
            elif ratio <= 1.0:
                score += 25  # Juste
            elif ratio <= 1.2:
                score += 10  # Serré
            # Sinon 0
        else:
            score += 40  # Pas de contrainte = score max
        
        return score
    
    @staticmethod
    def calculer_score_meteo(evenement, meteo: Dict) -> float:
        """Score basé sur l'adéquation avec la météo"""
        score = 0.0
        
        il_pleut = meteo.get("pluie", False)
        temperature = meteo.get("temperature", 20)
        
        # 1. Adéquation pluie (60 points)
        if il_pleut:
            if evenement.interieur or evenement.praticable_pluie:
                score += 60
            else:
                score += 0  # Événement extérieur sous la pluie = mauvais
        else:
            if not evenement.interieur:
                score += 60  # Extérieur par beau temps = parfait
            else:
                score += 40  # Intérieur acceptable même beau temps
        
        # 2. Température (25 points)
        if evenement.sensibilite_temperature == "forte":
            if 15 <= temperature <= 25:
                score += 25
            elif 10 <= temperature <= 30:
                score += 15
            else:
                score += 5
        elif evenement.sensibilite_temperature == "moyenne":
            if 10 <= temperature <= 30:
                score += 25
            else:
                score += 15
        else:  # faible
            score += 25
        
        # 3. Conditions générales (15 points)
        vent = meteo.get("vent", 0)
        if vent < 5 and not il_pleut:
            score += 15
        elif vent < 10:
            score += 10
        else:
            score += 5
        
        return score
    
    @staticmethod
    def calculer_score_contexte_social(
        evenement, 
        composition: str = "solo",
        ages: list = None
    ) -> float:
        """Score basé sur l'adéquation avec le contexte social"""
        score = 0.0
        
        # 1. Adéquation composition (70 points)
        composition_match = {
            "solo": evenement.adapte_solo,
            "couple": evenement.adapte_couple,
            "famille": evenement.adapte_famille,
            "groupe": evenement.adapte_groupe
        }
        
        if composition_match.get(composition, False):
            score += 70
        else:
            score += 30  # Acceptable mais pas optimal
        
        # 2. Adéquation âge (30 points)
        if ages:
            ages_ok = all(
                evenement.age_min <= age <= evenement.age_max 
                for age in ages
            )
            if ages_ok:
                score += 30
            else:
                score += 0  # Pas adapté à l'âge
        else:
            score += 30  # Pas de contrainte
        
        return score
    
    @staticmethod
    def calculer_score_qualite(evenement, utilisateur_a_vu: bool = False) -> float:
        """Score basé sur la qualité et la découverte"""
        score = 0.0
        
        # 1. Note globale pondérée (50 points)
        note_ponderee = (
            (evenement.note_moyenne or 3.0) * 0.4 +
            (evenement.note_curation or 3.0) * 0.4 +
            (evenement.source_fiabilite or 3) * 0.2
        ) / 5.0 * 50
        score += note_ponderee
        
        # 2. Facteur découverte (30 points)
        if not utilisateur_a_vu:
            score += 30
        else:
            score += 10  # Déjà vu mais acceptable
        
        # 3. Popularité modérée (20 points)
        # Favorise les événements ni trop populaires ni trop obscurs
        popularite = evenement.popularite or 0
        if 10 <= popularite <= 100:
            score += 20
        elif 5 <= popularite <= 200:
            score += 15
        else:
            score += 10
        
        return score
    
    @staticmethod
    def calculer_score_total(
        evenement,
        lat_user: float,
        lon_user: float,
        meteo: Dict,
        maintenant: Optional[datetime] = None,
        composition: str = "solo",
        ages: list = None,
        temps_disponible: Optional[int] = None,
        utilisateur_a_vu: bool = False
    ) -> Dict:
        """Calcule le score total avec détail des composantes"""
        
        if maintenant is None:
            maintenant = datetime.now()
        
        # Calcul de chaque score
        score_temporel = ScoringAlgorithm.calculer_score_temporel(evenement, maintenant)
        score_distance = ScoringAlgorithm.calculer_score_distance(
            evenement, lat_user, lon_user, temps_disponible
        )
        score_meteo = ScoringAlgorithm.calculer_score_meteo(evenement, meteo)
        score_social = ScoringAlgorithm.calculer_score_contexte_social(
            evenement, composition, ages
        )
        score_qualite = ScoringAlgorithm.calculer_score_qualite(evenement, utilisateur_a_vu)
        
        # Pondération finale
        score_total = (
            score_temporel * 0.30 +
            score_distance * 0.25 +
            score_meteo * 0.20 +
            score_social * 0.15 +
            score_qualite * 0.10
        )
        
        return {
            "score_total": round(score_total, 2),
            "score_temporel": round(score_temporel, 2),
            "score_distance": round(score_distance, 2),
            "score_meteo": round(score_meteo, 2),
            "score_social": round(score_social, 2),
            "score_qualite": round(score_qualite, 2),
            "distance_m": ScoringAlgorithm.calculer_distance(
                lat_user, lon_user, 
                evenement.latitude, evenement.longitude
            )
        }   