import sqlite3
import random
from datetime import datetime, timedelta

# Connexion à la base de données
conn = sqlite3.connect("data/evenements_test.db")
cursor = conn.cursor()

# Suppression et recréation de la table
cursor.execute("DROP TABLE IF EXISTS evenements")
cursor.execute("""
CREATE TABLE evenements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    categorie TEXT NOT NULL,
    description TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    horaire TEXT NOT NULL,
    heure_fermeture TEXT,
    date TEXT NOT NULL,
    prix TEXT,
    qualite REAL,
    nb_avis INTEGER,
    url_site TEXT,
    url_avis_google TEXT,
    contexte TEXT,
    tags TEXT,
    pmr BOOLEAN,
    image_url TEXT
)
""")

# Images Unsplash par catégorie
images_par_categorie = {
    "Restaurant": [
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800",
        "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800",
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",
    ],
    "Musée": [
        "https://images.unsplash.com/photo-1564399579883-451a5d44ec08?w=800",
        "https://images.unsplash.com/photo-1580922656920-6f0b44c1e39e?w=800",
        "https://images.unsplash.com/photo-1567696911980-2eed69a46042?w=800",
        "https://images.unsplash.com/photo-1577720643272-265f7f3e3197?w=800",
    ],
    "Bar": [
        "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=800",
        "https://images.unsplash.com/photo-1572116469696-31de0f17cc34?w=800",
        "https://images.unsplash.com/photo-1566417713940-fe7c737a9ef2?w=800",
        "https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=800",
    ],
    "Cinéma": [
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800",
        "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=800",
        "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=800",
        "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=800",
    ],
    "Café": [
        "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800",
        "https://images.unsplash.com/photo-1453614512568-c4024d13c247?w=800",
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800",
        "https://images.unsplash.com/photo-1442512595331-e89e73853f31?w=800",
    ],
    "Concert": [
        "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800",
        "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800",
        "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800",
        "https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=800",
    ],
    "Spectacle": [
        "https://images.unsplash.com/photo-1503095396549-807759245b35?w=800",
        "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800",
        "https://images.unsplash.com/photo-1478147427282-58a87a120781?w=800",
        "https://images.unsplash.com/photo-1507924538820-ede94a04019d?w=800",
    ],
    "Visite": [
        "https://images.unsplash.com/photo-1513581166391-887a96ddeafd?w=800",
        "https://images.unsplash.com/photo-1460881680858-30d872d5b530?w=800",
        "https://images.unsplash.com/photo-1549068106-b024baf5062d?w=800",
        "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800",
    ],
    "Parc": [
        "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=800",
        "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800",
        "https://images.unsplash.com/photo-1572120360610-d971b9d7767c?w=800",
        "https://images.unsplash.com/photo-1598632640487-6ea4a4e8b963?w=800",
    ],
    "Marché": [
        "https://images.unsplash.com/photo-1488459716781-31db52582fe9?w=800",
        "https://images.unsplash.com/photo-1555566976-02e1c1f4d7e2?w=800",
        "https://images.unsplash.com/photo-1563207153-f403bf289096?w=800",
        "https://images.unsplash.com/photo-1542838132-92c53300491e?w=800",
    ],
    "Atelier": [
        "https://images.unsplash.com/photo-1452860606245-08befc0ff44b?w=800",
        "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800",
        "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800",
        "https://images.unsplash.com/photo-1556912172-45b7abe8b7e1?w=800",
    ],
    "Rencontre littéraire": [
        "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800",
        "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800",
        "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=800",
        "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=800",
    ],
}

# Base de lieux avec coordonnées GPS réelles à Toulouse
lieux_base = {
    # Restaurants (tag: faim, afterwork)
    "Restaurant": [
        (
            "Michel Sarran",
            43.6031,
            1.4501,
            "https://www.michel-sarran.com",
            ["faim", "afterwork"],
            ["couple", "groupe", "famille"],
        ),
        (
            "Le Bibent",
            43.6044,
            1.4445,
            "https://www.brasseriedesbeauxarts.com",
            ["faim", "afterwork"],
            ["couple", "seul", "groupe"],
        ),
        (
            "Chez Tonton",
            43.6025,
            1.4389,
            "https://www.cheztonton-toulouse.fr",
            ["faim", "afterwork"],
            ["famille", "groupe"],
        ),
        (
            "La Braisière",
            43.6018,
            1.4432,
            "https://www.braisiere-toulouse.fr",
            ["faim", "afterwork"],
            ["couple", "groupe"],
        ),
        (
            "Le Genty Magre",
            43.5995,
            1.4407,
            "https://www.gentymagre.com",
            ["faim", "afterwork"],
            ["couple", "seul"],
        ),
        (
            "Monsieur Georges",
            43.6052,
            1.4429,
            "https://www.monsieurgeorges.com",
            ["faim", "afterwork"],
            ["groupe", "couple"],
        ),
        (
            "Le Py-R",
            43.6008,
            1.4468,
            "https://www.le-py-r.fr",
            ["faim"],
            ["couple", "famille"],
        ),
        (
            "Solides",
            43.5981,
            1.4356,
            "https://www.solidestoulouse.fr",
            ["faim", "afterwork"],
            ["couple", "seul"],
        ),
        (
            "La Table des Merville",
            43.6102,
            1.4378,
            "https://www.tabledesmerville.fr",
            ["faim"],
            ["famille", "couple"],
        ),
        (
            "Le Colombier",
            43.5988,
            1.4412,
            "https://www.lecolombier-toulouse.fr",
            ["faim", "afterwork"],
            ["couple", "groupe"],
        ),
        (
            "Ô Saveurs",
            43.6067,
            1.4503,
            "https://www.osaveurs.fr",
            ["faim"],
            ["couple", "seul"],
        ),
        (
            "L'Entrecôte",
            43.6041,
            1.4455,
            "https://www.entrecote.fr",
            ["faim", "afterwork"],
            ["famille", "groupe", "couple"],
        ),
    ],
    # Musées (tag: pluie, touriste, pmr)
    "Musée": [
        (
            "Musée des Augustins",
            43.6004,
            1.4444,
            "https://www.augustins.org",
            ["pluie", "touriste", "pmr"],
            ["seul", "couple", "famille"],
        ),
        (
            "Les Abattoirs",
            43.6068,
            1.4287,
            "https://www.lesabattoirs.org",
            ["pluie", "touriste", "pmr"],
            ["seul", "couple"],
        ),
        (
            "Cité de l'Espace",
            43.5864,
            1.4921,
            "https://www.cite-espace.com",
            ["pluie", "touriste", "pmr"],
            ["famille", "groupe", "couple"],
        ),
        (
            "Muséum de Toulouse",
            43.6077,
            1.4494,
            "https://www.museum.toulouse.fr",
            ["pluie", "touriste", "pmr"],
            ["famille", "seul"],
        ),
        (
            "Fondation Bemberg",
            43.5998,
            1.4429,
            "https://www.fondation-bemberg.fr",
            ["pluie", "touriste", "pmr"],
            ["seul", "couple"],
        ),
    ],
    # Bars (tag: afterwork)
    "Bar": [
        (
            "Le Saint des Seins",
            43.6019,
            1.4522,
            "https://www.saintdesseins.com",
            ["afterwork"],
            ["groupe", "seul"],
        ),
        (
            "Faubourg",
            43.6033,
            1.4488,
            "https://www.faubourg-toulouse.fr",
            ["afterwork"],
            ["groupe", "couple"],
        ),
        (
            "Le Baryton",
            43.5987,
            1.4421,
            "https://www.lebaryton.fr",
            ["afterwork"],
            ["groupe", "seul", "couple"],
        ),
        (
            "La Soif",
            43.6011,
            1.4513,
            "https://www.lasoif-toulouse.fr",
            ["afterwork"],
            ["groupe", "seul"],
        ),
        (
            "Le Purple",
            43.6029,
            1.4467,
            "https://www.lepurple.fr",
            ["afterwork"],
            ["groupe", "couple"],
        ),
    ],
    # Cinémas (tag: pluie, pmr)
    "Cinéma": [
        (
            "Cinéma ABC",
            43.6052,
            1.4458,
            "https://www.cinema-abc-toulouse.fr",
            ["pluie", "pmr"],
            ["couple", "seul", "famille"],
        ),
        (
            "Gaumont Wilson",
            43.6061,
            1.4464,
            "https://www.cinemasgaumont.com",
            ["pluie", "pmr"],
            ["couple", "famille", "groupe"],
        ),
        (
            "UGC Toulouse",
            43.6105,
            1.4535,
            "https://www.ugc.fr",
            ["pluie", "pmr"],
            ["couple", "seul"],
        ),
        (
            "Utopia",
            43.5983,
            1.4392,
            "https://www.cinemas-utopia.org/toulouse",
            ["pluie", "pmr"],
            ["seul", "couple"],
        ),
    ],
    # Cafés (tag: afterwork, pluie)
    "Café": [
        (
            "Café Bibent",
            43.6044,
            1.4445,
            "https://www.cafebibenttoulouse.com",
            ["afterwork", "pluie"],
            ["seul", "couple"],
        ),
        (
            "Le Florida",
            43.6038,
            1.4431,
            "https://www.leflorida-toulouse.fr",
            ["afterwork", "pluie"],
            ["seul", "groupe"],
        ),
        (
            "Café Margot",
            43.6015,
            1.4498,
            "https://www.cafemargot.fr",
            ["afterwork", "pluie"],
            ["seul", "couple"],
        ),
        (
            "Le Père Louis",
            43.5992,
            1.4413,
            "https://www.leperelouis.fr",
            ["afterwork", "pluie"],
            ["seul", "groupe"],
        ),
    ],
    # Concerts et spectacles (tag: afterwork, touriste)
    "Concert": [
        (
            "Le Bikini",
            43.5896,
            1.4012,
            "https://www.lebikini.com",
            ["afterwork", "touriste"],
            ["couple", "groupe"],
        ),
        (
            "Le Metronum",
            43.6117,
            1.4263,
            "https://www.metronum.toulouse.fr",
            ["afterwork"],
            ["couple", "groupe", "seul"],
        ),
        (
            "La Dynamo",
            43.5958,
            1.4372,
            "https://www.ladynamo.fr",
            ["afterwork"],
            ["groupe", "couple"],
        ),
    ],
    "Spectacle": [
        (
            "Théâtre du Capitole",
            43.6045,
            1.4442,
            "https://www.theatreducapitole.fr",
            ["afterwork", "touriste", "pluie"],
            ["couple", "seul"],
        ),
        (
            "Théâtre Sorano",
            43.5842,
            1.4498,
            "https://www.theatre-sorano.fr",
            ["afterwork", "pluie"],
            ["couple", "seul", "groupe"],
        ),
        (
            "TNT",
            43.6089,
            1.4329,
            "https://www.tnt-cite.com",
            ["afterwork", "touriste", "pluie"],
            ["couple", "groupe"],
        ),
    ],
    # Visites touristiques (tag: touriste, pmr)
    "Visite": [
        (
            "Basilique Saint-Sernin",
            43.6084,
            1.4419,
            "https://www.basilique-saint-sernin.fr",
            ["touriste", "pmr", "pluie"],
            ["seul", "couple", "famille", "groupe"],
        ),
        (
            "Capitole de Toulouse",
            43.6044,
            1.4442,
            "https://www.toulouse.fr",
            ["touriste", "pmr"],
            ["seul", "couple", "famille", "groupe"],
        ),
        (
            "Couvent des Jacobins",
            43.6026,
            1.4409,
            "https://www.jacobins.toulouse.fr",
            ["touriste", "pmr", "pluie"],
            ["seul", "couple", "groupe"],
        ),
        (
            "Canal du Midi",
            43.6105,
            1.4622,
            "https://www.toulouse-tourisme.com",
            ["touriste", "pmr"],
            ["seul", "couple", "famille"],
        ),
        (
            "Pont Neuf",
            43.6002,
            1.4397,
            "https://www.toulouse-tourisme.com",
            ["touriste", "pmr"],
            ["seul", "couple", "groupe"],
        ),
        (
            "Hôtel d'Assézat",
            43.5998,
            1.4429,
            "https://www.fondation-bemberg.fr",
            ["touriste", "pluie"],
            ["seul", "couple"],
        ),
        (
            "Quais de la Garonne",
            43.5989,
            1.4385,
            "https://www.toulouse.fr",
            ["touriste", "pmr"],
            ["seul", "couple", "famille"],
        ),
        (
            "Halle de la Machine",
            43.5982,
            1.4229,
            "https://www.halledelamachine.fr",
            ["touriste", "pluie"],
            ["famille", "groupe", "couple"],
        ),
    ],
    # Parcs (pas de tag pluie)
    "Parc": [
        (
            "Jardin Japonais",
            43.5902,
            1.4516,
            "https://www.toulouse.fr",
            ["pmr"],
            ["seul", "couple", "famille"],
        ),
        (
            "Jardin des Plantes",
            43.5946,
            1.4489,
            "https://www.toulouse.fr",
            ["pmr", "touriste"],
            ["seul", "couple", "famille"],
        ),
        (
            "Prairie des Filtres",
            43.6014,
            1.4322,
            "https://www.toulouse.fr",
            ["pmr"],
            ["seul", "couple", "famille", "groupe"],
        ),
    ],
    # Marchés (tag: touriste, pmr)
    "Marché": [
        (
            "Marché Victor Hugo",
            43.6014,
            1.4464,
            "https://www.toulouse.fr",
            ["touriste", "pmr", "faim"],
            ["seul", "couple", "famille"],
        ),
        (
            "Marché des Carmes",
            43.5972,
            1.4449,
            "https://www.toulouse.fr",
            ["touriste", "pmr", "faim"],
            ["seul", "couple"],
        ),
    ],
    # Ateliers créatifs (tag: pluie)
    "Atelier": [
        (
            "Atelier Poterie Terre & Feu",
            43.6055,
            1.4391,
            "https://www.terre-et-feu.fr",
            ["pluie"],
            ["seul", "couple", "groupe"],
        ),
        (
            "Cours de Cuisine Chef à Domicile",
            43.6003,
            1.4512,
            "https://www.chefadomicile-toulouse.fr",
            ["pluie", "faim"],
            ["seul", "couple", "groupe"],
        ),
        (
            "Atelier Peinture ArtSpace",
            43.5976,
            1.4434,
            "https://www.artspace-toulouse.fr",
            ["pluie"],
            ["seul", "couple"],
        ),
        (
            "Atelier DIY La Fabrique",
            43.6089,
            1.4378,
            "https://www.lafabrique-toulouse.fr",
            ["pluie"],
            ["seul", "groupe"],
        ),
    ],
    # Rencontres littéraires (tag: pluie)
    "Rencontre littéraire": [
        (
            "Librairie Ombres Blanches",
            43.6027,
            1.4423,
            "https://www.ombres-blanches.fr",
            ["pluie", "touriste"],
            ["seul", "couple"],
        ),
        (
            "Café-Lecture La Disparate",
            43.6041,
            1.4512,
            "https://www.ladisparate.fr",
            ["pluie", "afterwork"],
            ["seul"],
        ),
        (
            "Bibliothèque José Cabanis",
            43.6102,
            1.4387,
            "https://www.bibliotheque.toulouse.fr",
            ["pluie", "pmr"],
            ["seul"],
        ),
    ],
}

# Descriptions par catégorie
descriptions_templates = {
    "Restaurant": [
        "Cuisine {} dans une ambiance {}",
        "Spécialités {} avec produits {}",
        "Gastronomie {} réputée",
        "Restaurant {} avec terrasse {}",
    ],
    "Musée": [
        "Collection {} d'exception",
        "Exposition {} fascinante",
        "Découverte {} interactive",
        "Parcours {} enrichissant",
    ],
    "Bar": [
        "Ambiance {} et cocktails {}",
        "Bar {} avec sélection {}",
        "{} dans un cadre {}",
        "Soirée {} garantie",
    ],
    "Cinéma": [
        "Séances {} en salle {}",
        "Programmation {} variée",
        "Cinéma {} confortable",
        "Films {} en exclusivité",
    ],
    "Café": [
        "Café {} avec {}",
        "Ambiance {} idéale pour {}",
        "Terrasse {} et {}",
        "{} authentique",
    ],
    "Concert": [
        "Concert {} avec artistes {}",
        "Soirée {} mémorable",
        "Ambiance {} électrique",
        "Musique {} live",
    ],
    "Spectacle": [
        "Spectacle {} captivant",
        "{} par une troupe {}",
        "Représentation {} émouvante",
        "Performance {} exceptionnelle",
    ],
    "Visite": [
        "Visite {} guidée",
        "Découverte {} du patrimoine",
        "Monument {} emblématique",
        "Architecture {} remarquable",
    ],
    "Parc": [
        "Espace {} apaisant",
        "Jardin {} magnifique",
        "Promenade {} agréable",
        "Nature {} en ville",
    ],
    "Marché": [
        "Marché {} authentique",
        "Produits {} du terroir",
        "Ambiance {} conviviale",
        "Marché {} traditionnel",
    ],
    "Atelier": [
        "Atelier {} créatif",
        "Cours {} pour tous niveaux",
        "Initiation {} ludique",
        "Stage {} pratique",
    ],
    "Rencontre littéraire": [
        "Rencontre {} avec l'auteur",
        "Débat {} passionnant",
        "Présentation {} d'ouvrage",
        "Lecture {} publique",
    ],
}


def generer_url_avis_google(nom_lieu):
    nom_encode = nom_lieu.replace(" ", "+").replace("'", "%27")
    return f"https://www.google.com/maps/search/?api=1&query={nom_encode}+Toulouse"


def generer_description(categorie):
    template = random.choice(
        descriptions_templates.get(categorie, ["Événement intéressant"])
    )
    adjectifs = [
        "chaleureux",
        "convivial",
        "moderne",
        "cosy",
        "élégant",
        "authentique",
        "dynamique",
    ]
    return template.format(*random.sample(adjectifs, template.count("{}")))


def generer_horaire(categorie):
    """Génère un horaire adapté à la catégorie"""
    if categorie == "Restaurant":
        return random.choice(
            ["12:00", "12:30", "13:00", "19:00", "19:30", "20:00", "20:30"]
        )
    elif categorie in ["Bar", "Concert"]:
        return random.choice(["18:00", "19:00", "20:00", "21:00", "22:00"])
    elif categorie == "Marché":
        return random.choice(["08:00", "09:00", "10:00"])
    elif categorie == "Café":
        return random.choice(["08:00", "10:00", "14:00", "16:00", "18:00"])
    elif categorie in ["Musée", "Visite"]:
        return random.choice(["10:00", "11:00", "14:00", "15:00", "16:00"])
    elif categorie == "Atelier":
        return random.choice(["10:00", "14:00", "18:00", "19:00"])
    elif categorie == "Rencontre littéraire":
        return random.choice(["18:00", "18:30", "19:00", "19:30"])
    elif categorie == "Spectacle":
        return random.choice(["20:00", "20:30", "21:00"])
    elif categorie == "Cinéma":
        return random.choice(["14:00", "16:30", "19:00", "21:30"])
    else:
        return random.choice(["10:00", "14:00", "18:00"])


def calculer_heure_fermeture(horaire, categorie):
    heure = int(horaire.split(":")[0])

    durees = {
        "Restaurant": 2,
        "Café": 2,
        "Bar": 4,
        "Concert": 4,
        "Spectacle": 2,
        "Musée": 1,
        "Cinéma": 2,
        "Parc": None,
        "Marché": None,
        "Visite": 1,
        "Atelier": 2,
        "Rencontre littéraire": 2,
    }

    if categorie == "Parc":
        return "20:00"
    elif categorie == "Marché":
        return "13:30"
    else:
        duree = durees.get(categorie, 2)
        return f"{(heure + duree) % 24:02d}:{random.choice(['00', '30'])}"


# Génération des 300 événements sur 7 jours
date_debut = datetime(2025, 10, 4)
evenements_generes = []

# Environ 43 événements par jour
evenements_par_jour = 43

for jour in range(7):
    date_actuelle = date_debut + timedelta(days=jour)
    date_str = date_actuelle.strftime("%Y-%m-%d")

    for _ in range(evenements_par_jour):
        # Choisir une catégorie aléatoire
        categorie = random.choice(list(lieux_base.keys()))
        lieux_categorie = lieux_base[categorie]

        # Choisir un lieu
        nom_lieu, lat, lon, url_site, tags_list, contextes_list = random.choice(
            lieux_categorie
        )

        # Petite variation GPS
        lat += random.uniform(-0.0005, 0.0005)
        lon += random.uniform(-0.0005, 0.0005)

        horaire = generer_horaire(categorie)
        heure_fermeture = calculer_heure_fermeture(horaire, categorie)

        description = generer_description(categorie)

        # Prix selon catégorie
        prix_options = {
            "Restaurant": ["15€", "25€", "35€", "50€"],
            "Musée": ["Gratuit", "8€", "12€", "15€"],
            "Bar": ["Gratuit", "5€", "10€"],
            "Cinéma": ["9€", "11€"],
            "Café": ["5€", "8€", "12€"],
            "Concert": ["15€", "20€", "25€"],
            "Spectacle": ["15€", "22€", "28€"],
            "Visite": ["Gratuit", "5€", "8€"],
            "Parc": ["Gratuit"],
            "Marché": ["Gratuit"],
            "Atelier": ["20€", "35€", "45€"],
            "Rencontre littéraire": ["Gratuit", "5€"],
        }
        prix = random.choice(prix_options.get(categorie, ["Gratuit"]))

        qualite = round(random.uniform(3.8, 4.9), 1)
        nb_avis = random.randint(50, 1500)

        # Sélectionner des contextes et tags
        contexte = ",".join(
            random.sample(
                contextes_list, min(random.randint(1, 3), len(contextes_list))
            )
        )

        # IMPORTANT: Ne pas mélanger les tags - garder tous les tags de la catégorie
        tags = ",".join(tags_list)  # Tous les tags sans échantillonnage aléatoire

        pmr = 1 if "pmr" in tags else random.choice([0, 0, 1])  # 33% de PMR

        url_avis_google = generer_url_avis_google(nom_lieu)

        # Choisir une image aléatoire pour la catégorie
        image_url = random.choice(
            images_par_categorie.get(categorie, images_par_categorie["Restaurant"])
        )

        evenement = (
            nom_lieu,
            categorie,
            description,
            round(lat, 6),
            round(lon, 6),
            horaire,
            heure_fermeture,
            date_str,
            prix,
            qualite,
            nb_avis,
            url_site,
            url_avis_google,
            contexte,
            tags,
            pmr,
            image_url,
        )

        evenements_generes.append(evenement)

# Insertion dans la base
cursor.executemany(
    """
    INSERT INTO evenements 
    (nom, categorie, description, latitude, longitude, horaire, heure_fermeture, 
     date, prix, qualite, nb_avis, url_site, url_avis_google, contexte, tags, pmr, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""",
    evenements_generes,
)

conn.commit()

# Statistiques
cursor.execute("SELECT COUNT(*) FROM evenements")
total = cursor.fetchone()[0]

cursor.execute(
    "SELECT categorie, COUNT(*) as count FROM evenements GROUP BY categorie ORDER BY count DESC"
)
categories = cursor.fetchall()

cursor.execute(
    'SELECT tags, COUNT(*) as count FROM evenements WHERE tags LIKE "%pluie%" GROUP BY tags'
)
tags_pluie = cursor.fetchall()

cursor.execute(
    'SELECT tags, COUNT(*) as count FROM evenements WHERE tags LIKE "%afterwork%" GROUP BY tags'
)
tags_afterwork = cursor.fetchall()

print(f"✅ Base de données générée avec succès !")
print(f"📊 {total} événements créés sur 7 jours")
print(f"\n📈 Répartition par catégorie :")
for cat, count in categories:
    print(f"  • {cat}: {count} événements")

print(f"\n🌧️  Événements 'Il pleut': {sum([c[1] for c in tags_pluie])}")
print(f"🍺 Événements 'Afterwork': {sum([c[1] for c in tags_afterwork])}")

# Exemples d'événements par filtre
print(f"\n📋 Exemples par filtre :")
for filtre in ["pluie", "afterwork", "touriste", "faim", "pmr"]:
    cursor.execute(
        f"SELECT nom, categorie FROM evenements WHERE tags LIKE ? LIMIT 3",
        (f"%{filtre}%",),
    )
    events = cursor.fetchall()
    print(f"\n  {filtre.upper()}:")
    for e in events:
        print(f"    - {e[0]} ({e[1]})")

conn.close()
print("\n💾 Base sauvegardée dans 'evenements_test.db'")
