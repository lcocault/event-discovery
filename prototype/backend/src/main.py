from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sqlite3
from datetime import datetime
import requests
from math import radians, cos, sin, asin, sqrt

app = FastAPI()

# Configuration CORS pour le frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATABASE_NAME = "data/evenements_test.db"
OPENWEATHER_API_KEY = "7c1b853174a50201bf589eb2303fe8c"


def get_db_connection():
    """Connexion à la base de données"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def obtenir_meteo(lat: float, lon: float):
    """Récupère les données météo"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fr"
        response = requests.get(url, timeout=5)
        data = response.json()

        return {
            "temperature": round(data["main"]["temp"], 1),
            "pluie": "rain" in data.get("weather", [{}])[0].get("main", "").lower(),
            "description": data["weather"][0]["description"],
        }
    except Exception as e:
        print(f"Erreur API météo: {e}")
        return {"temperature": 20, "pluie": False, "description": "Ensoleillé"}


class ScoringAlgorithm:
    """Algorithme de scoring adapté pour la nouvelle structure de base"""

    @staticmethod
    def calculer_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance en mètres entre deux points GPS"""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Rayon de la Terre en mètres
        return c * r

    @staticmethod
    def calculer_score_temporalite(evenement, maintenant: datetime) -> float:
        """Score basé sur l'horaire et la date (30 points)"""
        score = 0.0

        try:
            # Concordance avec l'heure actuelle
            heure_event = int(evenement["horaire"].split(":")[0])
            heure_actuelle = maintenant.hour

            diff_heures = abs(heure_event - heure_actuelle)

            if diff_heures <= 1:
                score += 30  # Événement dans l'heure
            elif diff_heures <= 2:
                score += 25
            elif diff_heures <= 3:
                score += 20
            elif diff_heures <= 4:
                score += 15
            else:
                score += 10

        except:
            score += 15  # Score moyen si pas d'horaire précis

        return score

    @staticmethod
    def calculer_score_distance(
        evenement, lat_user: float, lon_user: float, temps_disponible: Optional[int]
    ) -> float:
        """Score basé sur la proximité (60 points)"""
        score = 0.0

        distance_m = ScoringAlgorithm.calculer_distance(
            lat_user, lon_user, evenement["latitude"], evenement["longitude"]
        )

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

        # Compatibilité temps disponible (estimation 1h de visite moyenne)
        if temps_disponible:
            temps_trajet = (distance_m / 1000) * 15  # 15 min par km
            temps_total = temps_trajet * 2 + 60  # 1h de visite
            ratio = temps_total / temps_disponible

            if ratio <= 0.8:
                score += 40
            elif ratio <= 1.0:
                score += 25
            elif ratio <= 1.2:
                score += 10
        else:
            score += 40

        return score

    @staticmethod
    def calculer_score_meteo(evenement, meteo: dict) -> float:
        """Score basé sur la météo (40 points)"""
        score = 0.0

        il_pleut = meteo.get("pluie", False)
        temperature = meteo.get("temperature", 20)
        categorie = evenement["categorie"]

        # Catégories intérieures
        interieures = [
            "Musée",
            "Cinéma",
            "Restaurant",
            "Bar",
            "Café",
            "Concert",
            "Spectacle",
        ]

        if categorie in interieures:
            score += 30
            if il_pleut:
                score += 10  # Bonus si pluie et intérieur
        else:
            if not il_pleut:
                score += 30
                if 15 <= temperature <= 28:
                    score += 10
            else:
                score += 5  # Activité extérieure sous la pluie = moins attractif

        return score

    @staticmethod
    def calculer_score_contexte(evenement, composition: Optional[str]) -> float:
        """Score basé sur le contexte social (40 points)"""
        score = 0.0

        if not composition:
            return 40  # Pas de préférence = neutre

        contexte_social = evenement["contexte"] or ""

        if composition in contexte_social:
            score += 40
        else:
            score += 15

        return score

    @staticmethod
    def calculer_score_qualite(evenement) -> float:
        """Score basé sur la qualité du lieu (30 points)"""
        score = 0.0

        note = evenement["qualite"] or 0
        nb_avis = evenement["nb_avis"] or 0

        # Score basé sur la note
        if note >= 4.5:
            score += 20
        elif note >= 4.0:
            score += 15
        elif note >= 3.5:
            score += 10
        else:
            score += 5

        # Bonus pour popularité
        if nb_avis > 500:
            score += 10
        elif nb_avis > 100:
            score += 7
        elif nb_avis > 20:
            score += 5
        else:
            score += 2

        return score

    @staticmethod
    def appliquer_filtre_rapide(evenement, quick_filter: str) -> float:
        """Bonus pour les filtres rapides (20 points)"""
        score = 0.0
        tags = evenement["tags"] or ""

        if quick_filter == "hazard":
            import random

            score = random.uniform(0, 20)
            return score

        # Vérifier si le tag est dans les tags de l'événement
        if quick_filter and quick_filter in tags:
            score += 20

        if quick_filter == "pmr" and evenement["pmr"]:
            score += 20

        return score


@app.get("/")
def read_root():
    """Point d'entrée de l'API"""
    return {
        "message": "API Que Faire - Backend opérationnel",
        "version": "3.2",
        "endpoints": ["/suggestions", "/meteo", "/evenements", "/stats"],
    }


@app.get("/meteo")
def get_meteo(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """Retourne les données météo actuelles"""
    return obtenir_meteo(lat, lon)


@app.get("/suggestions")
def get_suggestions(
    lat: float = Query(..., description="Latitude de l'utilisateur"),
    lon: float = Query(..., description="Longitude de l'utilisateur"),
    composition: Optional[str] = Query(
        None, description="seul, couple, groupe, famille"
    ),
    temps_disponible: Optional[int] = Query(
        None, description="Temps disponible en minutes"
    ),
    date: Optional[str] = Query(None, description="Date au format YYYY-MM-DD"),
    quick_filter: Optional[str] = Query(
        None, description="Filtre rapide: afterwork, pluie, touriste, faim, hazard, pmr"
    ),
):
    """
    Endpoint principal qui retourne les suggestions d'événements
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    maintenant = datetime.now()

    try:
        # Récupérer la météo
        meteo = obtenir_meteo(lat, lon)

        # Date de recherche (aujourd'hui par défaut)
        if date:
            date_recherche = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        else:
            date_recherche = maintenant.strftime("%Y-%m-%d")

        # Requête SQL avec filtre de date
        cursor.execute("SELECT * FROM evenements WHERE date = ?", (date_recherche,))

        tous_evenements_rows = cursor.fetchall()

        print(
            f"📅 Recherche pour {date_recherche}: {len(tous_evenements_rows)} événements trouvés"
        )

        # Calculer les scores
        resultats = []

        for evt_row in tous_evenements_rows:
            evt = dict(evt_row)

            try:
                # Filtrer les événements passés (pour aujourd'hui uniquement)
                if date_recherche == maintenant.strftime("%Y-%m-%d"):
                    if evt["horaire"]:
                        try:
                            h_debut = int(evt["horaire"].split(":")[0])
                            if (
                                h_debut < maintenant.hour - 1
                            ):  # Événements passés depuis plus d'1h
                                continue
                        except:
                            pass

                # Calculer la distance
                distance_m = ScoringAlgorithm.calculer_distance(
                    lat, lon, evt["latitude"], evt["longitude"]
                )

                # Calculer les scores
                score_temporel = ScoringAlgorithm.calculer_score_temporalite(
                    evt, maintenant
                )
                score_distance = ScoringAlgorithm.calculer_score_distance(
                    evt, lat, lon, temps_disponible
                )
                score_meteo = ScoringAlgorithm.calculer_score_meteo(evt, meteo)
                score_contexte = ScoringAlgorithm.calculer_score_contexte(
                    evt, composition
                )
                score_qualite = ScoringAlgorithm.calculer_score_qualite(evt)

                score_total = (
                    score_temporel
                    + score_distance
                    + score_meteo
                    + score_contexte
                    + score_qualite
                )

                # Appliquer le filtre rapide
                if quick_filter:
                    bonus_filtre = ScoringAlgorithm.appliquer_filtre_rapide(
                        evt, quick_filter
                    )
                    score_total += bonus_filtre

                # Formater le résultat pour le frontend
                resultats.append(
                    {
                        "id": evt["id"],
                        "nom": evt["nom"],
                        "categorie": evt["categorie"],
                        "description": evt["description"],
                        "latitude": evt["latitude"],
                        "longitude": evt["longitude"],
                        "distance": round(distance_m / 1000, 1),
                        "horaire": evt["horaire"] or "Toute la journée",
                        "heureFermeture": evt["heure_fermeture"] or "?",
                        "date": evt["date"],
                        "score": int(score_total),
                        "contexte": evt["contexte"].split(",")
                        if evt["contexte"]
                        else [],
                        "qualite": evt["qualite"] or 4.0,
                        "nbAvis": evt["nb_avis"] or 0,
                        "prix": evt["prix"] or "Gratuit",
                        "urlSite": evt["url_site"],
                        "urlAvisGoogle": evt["url_avis_google"],
                        "tags": evt["tags"].split(",") if evt["tags"] else [],
                        "pmr": bool(evt["pmr"]),
                        "imageUrl": evt["image_url"]
                        if "image_url" in evt.keys()
                        else None,
                    }
                )

            except Exception as e:
                print(f"❌ Erreur sur événement {evt.get('nom', 'inconnu')}: {e}")
                continue

        # Trier par score décroissant
        resultats.sort(key=lambda x: x["score"], reverse=True)

        print(
            f"✅ {len(resultats)} événements retournés (score max: {resultats[0]['score'] if resultats else 0})"
        )

        return resultats[:50]  # Limiter à 50 résultats

    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
        return {"error": str(e)}

    finally:
        conn.close()


@app.get("/evenements")
def get_all_evenements():
    """Retourne tous les événements (pour l'admin)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM evenements LIMIT 100")
    evenements = cursor.fetchall()

    conn.close()

    return [dict(evt) for evt in evenements]


@app.get("/stats")
def get_stats():
    """Retourne des statistiques sur la base de données"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM evenements")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT date) FROM evenements")
    nb_jours = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT categorie) FROM evenements")
    nb_categories = cursor.fetchone()[0]

    cursor.execute(
        "SELECT categorie, COUNT(*) as count FROM evenements GROUP BY categorie"
    )
    categories = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute(
        "SELECT date, COUNT(*) as count FROM evenements GROUP BY date ORDER BY date"
    )
    par_date = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    return {
        "total_evenements": total,
        "nb_jours": nb_jours,
        "nb_categories": nb_categories,
        "repartition_categories": categories,
        "evenements_par_date": par_date,
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Démarrage du serveur sur http://localhost:8000")
    print("📊 Statistiques: http://localhost:8000/stats")
    print("🌤️ Météo: http://localhost:8000/meteo?lat=43.604&lon=1.444")
    print("📖 Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
