{
  description = "Shelly H&T input plugin for Telegraf";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem
    (
      system: let
        pkgs = import nixpkgs {inherit system;};
        pkg_deps = pypkgs: [pypkgs.paho-mqtt];
      in {
        formatter = pkgs.writeShellApplication {
          name = "Format everything";
          text = ''
            echo "Formatting Nix files..."
            ${pkgs.alejandra}/bin/alejandra "$1"
            echo "Formatting Python files..."
            ${pkgs.black}/bin/black "$1/src"
          '';
        };
        packages.default = self.packages.${system}.shellyht2telegraf;
        packages.shellyht2telegraf = pkgs.python3Packages.buildPythonApplication {
          pname = "shellyht2telegraf";
          version = "0.1.0";
          src = ./src;
          propagatedBuildInputs = pkg_deps pkgs.python3Packages;
          format = "other";
          dontBuild = true;
          dontConfigure = true;
          installPhase = ''
            install -Dm 0755 $src/shellyht2telegraf.py $out/bin/shellyht2telegraf
          '';
        };

        devShells.default = pkgs.mkShell {
          packages = [
            (pkgs.python3.withPackages (
              python-pkgs: pkg_deps python-pkgs
            ))
          ];
        };
      }
    )
    // {
      overlays.default = final: prev: {shellyht2telegraf = self.packages."${prev.system}".shellyht2telegraf;};
    };
}
