# Création d'une ISO Bootable avec NixOS pour Lancer un Script Python

Ce projet utilise NixOS pour créer une image ISO bootable permettant de lancer un script Python facilement et rapidement. L'intérêt d'utiliser NixOS pour ce type de projet réside dans sa capacité à fournir des environnements reproductibles et à gérer les dépendances de manière efficace.

## Avantages de NixOS

- **Reproductibilité** : Grâce à la gestion déclarative des configurations, chaque construction de l'ISO sera identique, garantissant que votre script Python s'exécutera toujours dans le même environnement.
- **Gestion des dépendances** : NixOS permet d'inclure facilement toutes les dépendances nécessaires pour votre script Python directement dans l'ISO, sans avoir à se soucier des conflits de versions ou des dépendances manquantes.
- **Simplicité** : La configuration en Nix est concise et permet de définir toutes les étapes nécessaires pour préparer l'environnement d'exécution de votre script.

## Fichiers du Projet

- `iso.nix` : Configuration NixOS pour générer l'ISO bootable.
- `shell.nix` : permet d'ouvrir un shell NixOS interactif qui aura python et les dépéndances de notre script Python
- `main.py` : Exemple de script Python qui sera exécuté au démarrage de l'ISO.

## Génération de l'ISO

Pour générer l'image ISO bootable depuis un hôte NixOS, utilisez la commande suivante :

```sh
NIX_PATH=nixpkgs=https://github.com/NixOS/nixpkgs/archive/74e2faf5965a12e8fa5cff799b1b19c6cd26b0e3.tar.gz nix-shell -p nixos-generators --run "nixos-generate --format iso --configuration ./iso.nix -o result"
```

## Inclusion de Fichiers dans l'ISO 
Si vous avez des fichiers à copier dans l'ISO via la section `isoImage.contents` de la configuration `iso.nix`, placez-les à côté de `iso.nix` pour qu'ils soient inclus lors de la génération de l'ISO. Par exemple, pour inclure un script Python, votre configuration pourrait ressembler à ceci :

```nix
isoImage = {
  contents = [
    { source = ./main.py; target = "/InventoryBench/main.py"; mode = "0755"; }
  ];
};
```

## Conclusion 

NixOS offre une solution puissante et flexible pour créer des environnements d'exécution personnalisés et reproductibles. En utilisant ce projet comme point de départ, vous pouvez facilement créer une image ISO bootable contenant tout ce dont vous avez besoin pour exécuter vos scripts Python.