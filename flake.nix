{
  description = "Development environment for wallabag-client";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        version = "1.8.11";

        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
        
        # Define runtime dependencies
        pythonRuntimeDeps = ps: with ps; [
          beautifulsoup4
          pycryptodome
          requests
          click
          yaspin
          click-repl
          pyxdg
          colorama
          delorean
          humanize
          lxml
          tzlocal
          tabulate
          packaging
          markdownify
        ];
        
        # Define development dependencies
        pythonDevDeps = ps: with ps; [
          pip
          setuptools
          setuptools-scm
          wheel
          pytest
          black
          flake8
          mypy
        ];
        
        # Full development environment
        pythonEnv = python.withPackages (ps: 
          pythonRuntimeDeps ps ++ pythonDevDeps ps
        );
        
        # Define the package
        wallabagClient = python.pkgs.buildPythonPackage {
          pname = "wallabag-client";
          version = version;
          format = "setuptools";
          
          src = ./.;

          nativeBuildInputs = with python.pkgs; [
            pip
            wheel
            setuptools
            setuptools-scm
          ];
          
          propagatedBuildInputs = pythonRuntimeDeps python.pkgs;
          
          checkInputs = with python.pkgs; [
            pytest
          ];
          
          postPatch = ''
            export SETUPTOOLS_SCM_PRETEND_VERSION=${version}
            sed -i '/setup_requires=\[/,/]/d' setup.py
          '';

          meta = with pkgs.lib; {
            description = "A command-line client for the self-hosted read-it-later app Wallabag";
            homepage = "https://github.com/artur-shaik/wallabag-client";
            license = licenses.mit;
            maintainers = [];
          };
        };
      in
      {
        packages = {
          default = wallabagClient;
          wallabag-client = wallabagClient;
        };
        
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.pre-commit
          ];

          shellHook = ''
            echo "wallabag-client development environment activated!"
            echo "Python version: $(python --version)"
            
            # Make the package installable in development mode
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            
            # Allow setup.py to work properly
            export PIP_DISABLE_PIP_VERSION_CHECK=1
            
            # For setuptools_scm to work correctly
            export SETUPTOOLS_SCM_PRETEND_VERSION=${version}
          '';
        };
      }
    );
}

