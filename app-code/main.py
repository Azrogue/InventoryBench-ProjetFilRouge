import requests
import json
import socket
import subprocess
import os
from datetime import datetime
import time
import sys

# Configuration Directus
BASE_URL = 'https://redwire.chicken-musical.ts.net'
API_URL = f'{BASE_URL}/items'
TOKEN = ''

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}


# Fonction pour tester la connexion au DNS
MAX_RETRIES = 5
RETRY_INTERVAL = 5 # En Secondes 

def test_dns_connection():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            socket.gethostbyname(BASE_URL.replace('https://', '').replace('http://', ''))
            print("Test de connexion au DNS : OK")
            return True
        except socket.error as e:
            print(f"Test de connexion au DNS : FAIL ({e}) - Tentative {attempt}/{MAX_RETRIES}")
            if attempt < MAX_RETRIES:
                print(f"Nouvelle tentative dans {RETRY_INTERVAL} secondes...")
                time.sleep(RETRY_INTERVAL)
            else:
                print(f"L'adresse {BASE_URL} n'est pas joignable après {MAX_RETRIES} tentatives. Arrêt du programme.")
                return False

# Fonction pour créer une session
def create_session(public_ip):
    session_data = {
        "launch_date": datetime.utcnow().isoformat(),
        "public_ip": public_ip,
        "description": "Hardware scan"
    }
    response = requests.post(f'{API_URL}/sessions', headers=headers, data=json.dumps(session_data))
    if response.status_code == 200:
        session_id = response.json()['data']['id']
        print(f"Session créée avec succès : {session_id}")
        return session_id
    else:
        print(f"Erreur lors de la création de la session: {response.status_code}")
        print(response.json())
        return None

# Fonction pour vérifier si le script est exécuté avec des privilèges sudo
def check_sudo():
    if os.geteuid() != 0:
        print("Ce script doit être exécuté avec des privilèges sudo.")
        sys.exit(1)
    else:
        print("Script exécuté avec des privilèges sudo.")

# Fonction pour obtenir l'IP publique
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        print(f"IP publique récupérée : {ip}")
        return ip
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de l'IP publique : {e}")
        return None

# Fonction pour exécuter lshw et obtenir les informations matérielles
def get_hardware_info():
    hardware_info = []

    print("Récupération des informations du matériel...")

    try:
        result = subprocess.run(['lshw', '-json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        lshw_data = json.loads(result.stdout)

        # Récupération des informations CPU
        for child in lshw_data.get('children', []):
            if child['class'] == 'bus':
                for item in child.get('children', []):
                    if item['class'] == 'processor':
                        cpu_info = {
                            "serial_number": item.get('serial', f"CPU-{item['id']}"),
                            "name": item.get('product', ''),
                            "type": "CPU",
                            "manufacturer": item.get('vendor', 'Unknown'),
                            "other_details": {
                                "version": item.get('version', ''),
                                "frequency": item.get('capacity', '')
                            }
                        }
                        print(f"Informations CPU récupérées: {json.dumps(cpu_info, indent=4)}")
                        hardware_info.append(cpu_info)

                    # Récupération des informations RAM
                    if item['class'] == 'memory':
                        for memory in item.get('children', []):
                            if memory['class'] == 'memory':
                                ram_info = {
                                    "serial_number": memory.get('serial', f"RAM-{memory['id']}"),
                                    "name": memory.get('product', 'RAM'),
                                    "type": "RAM",
                                    "manufacturer": memory.get('vendor', 'Unknown'),
                                    "other_details": {
                                        "size": memory.get('size', '')
                                    }
                                }
                                print(f"Informations RAM récupérées: {json.dumps(ram_info, indent=4)}")
                                hardware_info.append(ram_info)

                    # Récupération des informations disques
                    if item['class'] == 'storage':
                        for disk in item.get('children', []):
                            if disk['class'] == 'disk':
                                disk_info = {
                                    "serial_number": disk.get('serial', f"DISK-{disk['logicalname']}"),
                                    "name": disk.get('product', ''),
                                    "type": "Disk",
                                    "manufacturer": disk.get('vendor', 'Unknown'),
                                    "other_details": {
                                        "size": disk.get('size', '')
                                    }
                                }
                                print(f"Informations disque récupérées: {json.dumps(disk_info, indent=4)}")
                                hardware_info.append(disk_info)

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de lshw: {e}")
        print(e.stderr)

    return hardware_info

# Fonction pour récupérer les composants existants depuis Directus
def get_existing_components():
    print("Récupération des composants existants depuis Directus...")
    response = requests.get(f'{API_URL}/components', headers=headers)
    if response.status_code == 200:
        existing_components = response.json()['data']
        print(f"Composants existants récupérés : {len(existing_components)} trouvés")
        return existing_components
    else:
        print(f"Erreur lors de la récupération des composants existants : {response.status_code}")
        return []

# Fonction pour comparer et mettre à jour les composants
def update_components(new_components, existing_components, session_id):
    new_count = 0
    update_count = 0

    print("Comparaison et mise à jour des composants...")

    for new_component in new_components:
        matched = False
        new_component['session_id'] = session_id  # Associer le composant à la session actuelle
        for existing_component in existing_components:
            if new_component["serial_number"] == existing_component["serial_number"]:
                matched = True
                # Mise à jour du composant
                print(f"Mise à jour du composant existant: {json.dumps(new_component, indent=4)}")
                response = requests.patch(f'{API_URL}/components/{existing_component["id"]}', headers=headers, data=json.dumps(new_component))
                if response.status_code == 200:
                    print(f"Composant mis à jour : {new_component['serial_number']}")
                    update_count += 1
                else:
                    print(f"Erreur lors de la mise à jour du composant {new_component['serial_number']} : {response.status_code}")
                    print(response.json())
                break
        if not matched:
            # Création d'un nouveau composant
            print(f"Création d'un nouveau composant: {json.dumps(new_component, indent=4)}")
            response = requests.post(f'{API_URL}/components', headers=headers, data=json.dumps(new_component))
            if response.status_code == 200:
                print(f"Composant créé : {new_component['serial_number']}")
                new_count += 1
            else:
                print(f"Erreur lors de la création du composant {new_component['serial_number']} : {response.status_code}")
                print(response.json())

    print(f"{new_count} nouveaux composants créés, {update_count} composants mis à jour")

# Exécution principale
if __name__ == "__main__":
    # ASCII art title
    title = """
    \033[92m

██╗███╗   ██╗██╗   ██╗███████╗███╗   ██╗████████╗ ██████╗ ██████╗ ██╗   ██╗    ██████╗ ███████╗███╗   ██╗ ██████╗██╗  ██╗
██║████╗  ██║██║   ██║██╔════╝████╗  ██║╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝    ██╔══██╗██╔════╝████╗  ██║██╔════╝██║  ██║
██║██╔██╗ ██║██║   ██║█████╗  ██╔██╗ ██║   ██║   ██║   ██║██████╔╝ ╚████╔╝     ██████╔╝█████╗  ██╔██╗ ██║██║     ███████║
██║██║╚██╗██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║   ██║   ██║██╔══██╗  ╚██╔╝      ██╔══██╗██╔══╝  ██║╚██╗██║██║     ██╔══██║
██║██║ ╚████║ ╚████╔╝ ███████╗██║ ╚████║   ██║   ╚██████╔╝██║  ██║   ██║       ██████╔╝███████╗██║ ╚████║╚██████╗██║  ██║
╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝

                   By Judi and Billel
    \033[0m
    """
    # Print the title
    print(title)

    check_sudo()
    if test_dns_connection():
        print("Connexion réussie.")
        public_ip = get_public_ip()
        if public_ip:
            session_id = create_session(public_ip)
            if session_id:
                new_components = get_hardware_info()
                existing_components = get_existing_components()
                update_components(new_components, existing_components, session_id)
    else:
        print("Impossible de se connecter au DNS. Vérifiez votre connexion réseau et réessayez.")
        exit(1)