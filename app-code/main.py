import os
import platform
import psutil
import subprocess
import re
import requests
import json
import cpuinfo  # Assurez-vous que le module est installé via 'pip install py-cpuinfo'

DIRECTUS_API_URL = "https://redwire.chicken-musical.ts.net"
DIRECTUS_API_TOKEN = "Lvfr-bSLCpREJV1aWIG67oh-fJx9qWdu"

headers = {
    "Authorization": f"Bearer {DIRECTUS_API_TOKEN}",
    "Content-Type": "application/json"
}
# Fonction pour récupérer les informations CPU
def get_cpu_info():
    cpu_info = cpuinfo.get_cpu_info()
    return {
        'marque': cpu_info['brand_raw'],
        'frequence': cpu_info['hz_actual_friendly'],
        'architecture': cpu_info['arch']
    }

# Fonction pour récupérer les informations mémoire sur Windows
def get_memory_info_windows():
    virtual_mem = psutil.virtual_memory()
    ram_capacity_gb = virtual_mem.total / (1024 ** 3)
    return {
        'total': virtual_mem.total,
        'disponible': virtual_mem.available,
        'utilisee': virtual_mem.used,
        'ram_capacity_gb': ram_capacity_gb,
        'ram_manufacturer': get_ram_manufacturer()
    }

# Fonction pour obtenir le fabricant de la RAM sur Windows
def get_ram_manufacturer():
    command = "wmic memorychip get manufacturer"
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        lines = result.stdout.strip().split('\n')
        manufacturers = {line.strip() for line in lines[1:] if line.strip()}  # Utiliser un ensemble pour éviter les duplications
        if manufacturers:
            return ', '.join(manufacturers)  # Joindre les fabricants avec une virgule
        else:
            return "N/A"
    except subprocess.CalledProcessError:
        print("Erreur lors de l'exécution de la commande 'wmic memorychip'. Assurez-vous qu'elle est installée et que vous avez les permissions nécessaires.")
        return "N/A"

# Fonction pour récupérer les informations GPU 
def get_gpu_info():
    gpus = []
    system = platform.system()

    if system == "Windows":
        command = "wmic path win32_VideoController get name"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        gpus = result.stdout.strip().split('\n')[1:]
    elif system == "Linux":
        command = "lshw -C display"
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "product:" in line:
                    gpu = line.split("product:")[1].strip()
                    gpus.append(gpu)
        except subprocess.CalledProcessError:
            print("Erreur lors de l'exécution de la commande 'lshw'. Assurez-vous qu'elle est installée et que vous avez les permissions nécessaires.")
    elif system == "Darwin":
        command = "system_profiler SPDisplaysDataType | grep 'Chipset Model'"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        gpus = re.findall(r'Chipset Model: (.+)', result.stdout)

    return [gpu.strip() for gpu in gpus if gpu.strip()]

# Fonction pour ajouter un composant à Directus
def add_composant(numero_serie, nom, type_name):
    try:
        response = requests.get(f"{DIRECTUS_API_URL}/items/type_composant?filter[nom_type_composant][_eq]={type_name}", headers=headers)
        response_data = response.json()
        if 'data' in response_data and response_data['data']:
            type_id = response_data['data'][0]['id']
        else:
            print(f"Erreur: Type de composant '{type_name}' introuvable.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête get_type_id: {e}")
        return False

    data = {
        "numero_serie": numero_serie,
        "nom": nom,
        "type_composant": type_id
    }

    try:
        response = requests.post(f"{DIRECTUS_API_URL}/items/Composants", headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"Erreur lors de l'ajout du composant {nom}: {response.status_code} {response.text}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête add_composant: {e}")
        return False
    

def main():
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

    # Récupération des informations CPU
    cpu_info = get_cpu_info()
    cpu_model_name = cpu_info.get('marque', 'N/A')
    # Ajout du composant CPU à Directus
    success = add_composant("N/A", f"{cpu_model_name}", "CPU")
    if success:
        print(f"Composant CPU ajouté: {cpu_model_name}")
    else:
        print("Échec de l'ajout du composant CPU")

    # Récupération des informations mémoire spécifique à Windows
    memory_info = get_memory_info_windows()
    ram_capacity_gb = memory_info.get('ram_capacity_gb', 0)
    ram_manufacturer = memory_info.get('ram_manufacturer', 'N/A')

    # Ajout du composant RAM à Directus avec le fabricant et la capacité
    success = add_composant("N/A", f"{ram_manufacturer} {ram_capacity_gb:.2f}GB", "RAM")
    if success:
        print(f"Composant RAM ajouté: {ram_manufacturer} {ram_capacity_gb:.2f}GB")
    else:
        print("Échec de l'ajout du composant RAM")

    # Récupération des informations GPU
    gpu_info = get_gpu_info()
    for gpu in gpu_info:
        # Ajout du composant GPU à Directus
        success = add_composant("N/A", f"{gpu}", "GPU")
        if success:
            print(f"Composant GPU ajouté: {gpu}")
        else:
            print(f"Échec de l'ajout du composant GPU: {gpu}")


    # Prompt the user to press a key to continue to bash
    input("\nPress any key to continue to a bash terminal...")

    # Open a bash shell
    os.system("bash")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()