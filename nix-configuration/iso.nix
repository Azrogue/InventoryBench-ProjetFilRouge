{ config, pkgs, lib, ... }:
{
  imports = [ <nixpkgs/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix> ];

  # compress 6x faster than default
  # but iso is 15% bigger
  # default is xz which is very slow
  isoImage.squashfsCompression = "zstd -Xcompression-level 6";

  # my azerty keyboard
  i18n.defaultLocale = "fr_FR.UTF-8";
  services.xserver.layout = "fr";
  console = {
    keyMap = "fr";
  };

  # xanmod kernel for better performance
  # see https://xanmod.org/
  boot.kernelPackages = pkgs.linuxPackages_xanmod;

  # Use the latest Linux kernel
  # boot.kernelPackages = pkgs.linuxPackages_latest;

  # Needed for https://github.com/NixOS/nixpkgs/issues/58959
  boot.supportedFilesystems = lib.mkForce [ "btrfs" "reiserfs" "vfat" "f2fs" "xfs" "ntfs" "cifs" ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.useDHCP = true;
  # Set your time zone.
  time.timeZone = "Europe/Paris";

  environment.systemPackages = with pkgs; [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.psutil
      python-pkgs.requests
      python-pkgs.py-cpuinfo
    ]))
  ];

    systemd.services.myPythonScript = {
    description = "Run my Python script";
    after = [ "network.target" "getty@tty1.service" ];
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      ExecStart = "/run/current-system/sw/bin/python3 /iso/InventoryBench/main.py";
      Restart = "always";
      StandardInput = "tty";
      StandardOutput = "tty";
      TTYPath = "/dev/tty1";
    };
  };

  isoImage = {
    contents = [
      { source = ./main.py; target = "/InventoryBench/main.py"; mode = "0755";  }
    ];
  };
}
