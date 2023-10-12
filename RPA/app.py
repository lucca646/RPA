import os
from flask import Flask, render_template, send_from_directory, request, send_file
from werkzeug.utils import secure_filename
import math
import json  
import xml.etree.ElementTree as ET 
import simplekml
from shapely.geometry import Point, Polygon
import gpxpy
import random
from pyngrok import ngrok

# Obtenez la liste des tunnels actifs
app = Flask(__name__)
#app.run(host='0.0.0.0', port=709)


# Générer une valeur aléatoire pour 'a' et initialiser une variable pour vérifier si 'a' est unique
a = None
is_unique = False

# Charger le contenu du fichier JSON existant
with open('data/off.json', 'r') as json_file:
    data = json.load(json_file)

# Continuer à générer une nouvelle valeur jusqu'à ce qu'elle soit unique
while not is_unique:
    a = int(random.choice(range(100000)))
    if a not in data['values']:
        is_unique = True

# Ajouter la valeur 'a' à la liste
data['values'].append(a)

# Enregistrer le contenu mis à jour dans le fichier JSON
with open('data/off.json', 'w') as json_file:
    json.dump(data, json_file)

# Définir le répertoire de téléchargement des fichiers GPX
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/data/<path:filename>')
def serve_file(filename):
    # Utilisez send_from_directory pour servir le fichier du répertoire "data"
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)    

# Fonction pour déplacer et renommer le fichier GPX
def move_and_rename_gpx(file):
    if file:
        # Sécurisez le nom du fichier pour éviter tout problème de sécurité
        filename = secure_filename(file.filename)
        gpx_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'zone.gpx')
        file.save(gpx_filepath)
        return True
    return False

@app.route('/', methods=['GET', 'POST'])
def upload_gpx():
    if request.method == 'POST':
        # Vérifiez si un fichier GPX a été envoyé et déplacez-le
        if move_and_rename_gpx(request.files['file']):
            kml()
            print (a)
            return render_template('map.html', a=a)
        else:
            return "Le fichier n'est pas valide ou vide."

    return render_template('index.html')
def kml():
    import random

    gpx_file = open('data/zone.gpx', 'r')
    gpx = gpxpy.parse(gpx_file)

    # Extraire les points du premier segment du premier tracé (vous pouvez ajuster cela en fonction de votre fichier GPX)
    segment = gpx.tracks[0].segments[0]
    polygon_points = [(point.latitude, point.longitude) for point in segment.points]

    # Afficher les points extraits
    print("Points extraits du fichier GPX:")
    for point in polygon_points:
        f"Latitude: {point[0]}, Longitude: {point[1]}"

    # Fermer le fichier GPX
    gpx_file.close()

    polygon = Polygon(polygon_points)
    # Trouver les sommets les plus éloignés du polygone
    # Trouver les limites du polygone
    min_lat = min(point[0] for point in polygon_points)
    max_lat = max(point[0] for point in polygon_points)
    min_lon = min(point[1] for point in polygon_points)
    max_lon = max(point[1] for point in polygon_points)

    # Ajouter une petite marge (par exemple, 0.001 degré) pour s'assurer que le polygone est englobé
    margin = 0.001
    coord1 = (min_lat - margin, min_lon - margin)  # Coin supérieur gauche
    coord2 = (max_lat + margin, max_lon + margin)  # Coin inférieur droit

    print("Coin supérieur gauche:", coord1)
    print("Coin inférieur droit:", coord2)
    # Affichage des nouvelles coordonnées
    print("Coin supérieur gauche (coord1):", coord1)
    print("Coin inférieur droit (coord2):", coord2)


    lat1, lon1 = min(coord1[0], coord2[0]), min(coord1[1], coord2[1])
    lat2, lon2 = max(coord1[0], coord2[0]), max(coord1[1], coord2[1])

    # Coins du rectangle
    coin_sup_gauche = (lat2, lon1)  # Coin supérieur gauche
    coin_sup_droit = (lat2, lon2)   # Coin supérieur droit
    coin_inf_gauche = (lat1, lon1)  # Coin inférieur gauche
    coin_inf_droit = (lat1, lon2)   # Coin inférieur droit

    # Espacement en mètres entre les points du cadrillage (1 mètre dans cet exemple)
    spacing_meters = 8 #int(input("nombre de mètres entre les arbres: "))


    earth_radius = 6371000  # En mètres
    def euclidean_distance(lat1, lon1, lat2, lon2):
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        return math.sqrt(delta_lat**2 + delta_lon**2) * 111319.9  # Conversion en mètres


    distance_cote1 = int(euclidean_distance(coord1[0], coord1[1], coord2[0], coord1[1]))
    distance_cote2 = int(euclidean_distance(coord1[0], coord1[1], coord1[0], coord2[1]))

    print("Distance côté 1: ", distance_cote1, "m")
    print("Distance côté 2:", distance_cote2, "m")


    # Calcul du nombre de points dans chaque dimension (latitude et longitude)
    num_points_lat = int(distance_cote1 / spacing_meters) + 1
    num_points_lon = int(distance_cote2 / spacing_meters) + 1

    # Création de la liste de coordonnées GPS
    grid_points = []

        
    for i in range(num_points_lat):
        for j in range(num_points_lon):
            lat = coord1[0] + (i / (num_points_lat - 1)) * (coord2[0] - coord1[0])
            lon = coord1[1] + (j / (num_points_lon - 1)) * (coord2[1] - coord1[1])
            lat = round(lat, 6)
            lon = round(lon, 6)
            grid_points.append((lat, lon))

    # Affichage des coordonnées GPS de tous les points
    for i, point in enumerate(grid_points, 1):
        f"Point {i}: Latitude {point[0]}, Longitude {point[1]}"
        
    # Création d'une liste de listes
    listes = []

    for i in range(num_points_lat):
        sublist = grid_points[i * num_points_lon : (i + 1) * num_points_lon]
        if i % 2 == 1:
            sublist = sublist[::-1]
        listes.append(sublist)

    # Affichage de chaque sous-liste
    for i, sublist in enumerate(listes, 1):
        f"Liste {i}: {sublist}"
    merged_list = [item for sublist in listes for item in sublist]


    grid_points = merged_list

    with open('data/points_gps.json', 'w') as json_file:
        json.dump(grid_points, json_file)
        
    coordonnees_existantes = grid_points
    amplitude_max = 0.00003
    coordonnees_aleatoires = []
    for lat, lon in coordonnees_existantes:
        # Générez un petit déplacement aléatoire en latitude et longitude
        delta_lat = random.uniform(-amplitude_max, amplitude_max)
        delta_lon = random.uniform(-amplitude_max, amplitude_max)
        
        # Ajoutez le déplacement aléatoire aux coordonnées existantes
        nouvelle_lat = lat + delta_lat
        nouvelle_lon = lon + delta_lon
        
        # Ajoutez les nouvelles coordonnées à la liste
        coordonnees_aleatoires.append((nouvelle_lat, nouvelle_lon))

    # Affichez les nouvelles coordonnées avec de l'aléatoire
    for lat, lon in coordonnees_aleatoires:
        f"Latitude : {lat}, Longitude : {lon}"





    # Liste des coordonnées GPS à filtrer
    coordinates_to_filter = coordonnees_aleatoires

    # Liste pour stocker les coordonnées à l'intérieur du polygone
    filtered_coordinates = []

    # Filtrer les coordonnées à l'intérieur du polygone
    for coord in coordinates_to_filter:
        point = Point(coord[0], coord[1])
        if polygon.contains(point):
            filtered_coordinates.append(coord)






    points_gps = filtered_coordinates


    kml = ET.Element("kml")
    document = ET.SubElement(kml, "Document")


    import random

    # Pourcentages souhaités
    percentages = {
        "Chenes": 25,
        "Hetres": 20,
        "Erables": 15,
        "Sapins": 20,
        "Epinettes": 10
    }

    # Liste des étiquettes d'arbres en fonction des pourcentages
    tree_labels = []
    for tree, percentage in percentages.items():
        num_points = int(percentage / 100 * len(points_gps))
        tree_labels.extend([tree] * num_points)

    # Mélanger la liste d'étiquettes pour une répartition aléatoire
    random.shuffle(tree_labels)

    # Maintenant, vous pouvez attribuer les étiquettes aux points GPS
    for i, (point, label) in enumerate(zip(points_gps, tree_labels), 1):
        placemark = ET.SubElement(document, "Placemark")
        name = ET.SubElement(placemark, "name")
        # Spécifiez l'encodage des caractères en utilisant "utf-8"
        name.text = f"Point {i} ({label})".encode("utf-8").decode("utf-8")
        coordinates = ET.SubElement(placemark, "Point")
        coord = ET.SubElement(coordinates, "coordinates")
        coord.text = f"{point[1]},{point[0]},0"  # Format : longitude,latitude,altitude



    # Enregistrement du fichier KML
    tree = ET.ElementTree(kml)
    tree.write("data/points_gps.kml")

    fichier_kml = "data/points_gps.kml"
    itineraire_nom = "Itinéraire"

    # Créez un objet KML
    kml = simplekml.Kml()

    # Créez un itinéraire dans le KML en utilisant les points GPS de votre choix
    itineraire = kml.newlinestring(name="trajet", description="itinéraire")

    # Ajoutez les coordonnées de l'itinéraire (exemple : [(longitude1, latitude1), (longitude2, latitude2), ...])
    itineraire.coords = [(lon, lat) for lat, lon in points_gps]  # Inversez l'ordre (longitude, latitude)

    # Ajoutez également des points à votre KML (exemple : [(longitude1, latitude1), (longitude2, latitude2), ...])
    # for lat, lon in grid_points:
    #     kml.newpoint(name="Point", coords=[(lon, lat)])  # Crée un point pour chaque paire de coordonnées

    # Enregistrez le KML
    kml.save(f"data/itineraires/{a}.kml")

    print('Fichier KML avec l\'itinéraire créé avec succès.')

    # Enregistrement des points au format JSON
    with open('data/points_gps.json', 'w') as json_file:
        json.dump(points_gps, json_file)
    return send_file(f"data/itineraires/{a}.kml", as_attachment=True)

@app.route('/download_kml', methods=['GET'])
def download_kml():
    return send_file(f"data/itineraires/{a}.kml", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
