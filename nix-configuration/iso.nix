{ config, pkgs, lib, ... }:
{
  imports = [ <nixpkgs/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix> ];

  # Compress 6x faster than default but iso is 15% bigger
  isoImage.squashfsCompression = "zstd -Xcompression-level 6";

  # My azerty keyboard
  i18n.defaultLocale = "fr_FR.UTF-8";
  services.xserver.layout = "fr";
  console.keyMap = "fr";

  # Xanmod kernel for better performance
  boot.kernelPackages = pkgs.linuxPackages_xanmod;
  
  # Needed for specific file system support
  boot.supportedFilesystems = lib.mkForce [ "btrfs" "reiserfs" "vfat" "f2fs" "xfs" "ntfs" "cifs" ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.useDHCP = true;
  time.timeZone = "Europe/Paris";

  # Environment packages
  environment.systemPackages = with pkgs; [
    (pkgs.python3.withPackages (ps: with ps; [ requests ]))
    lshw
    wpa_supplicant
    wirelesstools
    iw
  ];

  isoImage.contents = [
    { source = ./main.py; target = "/InventoryBench/main.py"; mode = "0755"; }
  ];

  users.users.nixos = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    shell = pkgs.bash;
    initialPassword = "nixos";
  };

  boot.kernelParams = [ "video=HDMI-1:1280x720@60" ];

  services.kmscon = {
    enable = true;
    autologinUser = "nixos";
    extraConfig = ''
      xkb-layout=fr
      font-size=12
    '';     
    extraOptions = "--term xterm-256color --font-engine unifont";
  };

  programs.bash.shellAliases = {
    inventory-bench = "sudo python3 /iso/InventoryBench/main.py";
  };

  programs.bash.interactiveShellInit = ''
    sudo python3 /iso/InventoryBench/main.py
  '';

  networking.wireless = {
    enable = true;
    userControlled.enable = true;
    networks = {
      "👨‍🎓CFA ITIS | ETUDIANTS" = {};
      "iPhone Y" = {
        psk = "password";
      };
    };
  };
}