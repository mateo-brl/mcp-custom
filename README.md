# Mon MCP Custom

Un serveur [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) qui permet a Claude de **voir vos ecrans**, **interagir avec votre ordinateur**, **gerer vos fichiers**, **surveiller votre systeme** et plus encore.

> **Note** : Ce MCP est actuellement pour **Windows uniquement**.

## Fonctionnalites (27 outils)

| Categorie | Outil | Description |
|-----------|-------|-------------|
| **Diagnostic** | `ping` | Verifie que le MCP fonctionne et liste les dependances |
| **Capture** | `capture_ecrans` | Capture tous les ecrans de l'ordinateur |
| **Capture** | `capture_ecran_principal` | Capture uniquement l'ecran principal |
| **Capture** | `capture_region` | Capture une zone specifique de l'ecran |
| **Fenetres** | `liste_fenetres` | Liste toutes les fenetres ouvertes |
| **Fenetres** | `focus_fenetre` | Active une fenetre par son titre |
| **Souris** | `clic_souris` | Clic a une position (x, y) |
| **Souris** | `double_clic` | Double-clic a une position |
| **Souris** | `position_souris` | Retourne la position actuelle |
| **Souris** | `deplacer_souris` | Deplace la souris (mouvement fluide) |
| **Souris** | `scroll` | Scroll up/down |
| **Clavier** | `ecrire_texte` | Ecrit du texte (Unicode complet: accents, symboles) |
| **Clavier** | `touche_clavier` | Appuie sur une touche (enter, ctrl+c, etc.) |
| **Fichiers** | `lire_fichier` | Lit le contenu d'un fichier texte |
| **Fichiers** | `ecrire_fichier` | Cree ou ecrit un fichier |
| **Fichiers** | `copier_fichier` | Copie un fichier ou dossier |
| **Fichiers** | `deplacer_fichier` | Deplace ou renomme un fichier |
| **Fichiers** | `supprimer_fichier` | Supprime un fichier ou dossier (protection systeme) |
| **Fichiers** | `lister_repertoire` | Liste le contenu d'un repertoire avec details |
| **Fichiers** | `info_fichier` | Metadonnees d'un fichier (taille, dates, etc.) |
| **Fichiers** | `creer_repertoire` | Cree un repertoire (avec parents) |
| **Systeme** | `liste_processus` | Liste les processus (CPU, memoire) |
| **Systeme** | `info_systeme` | Infos systeme (CPU, RAM, disque, OS) |
| **Systeme** | `tuer_processus` | Termine un processus (protection processus critiques) |
| **Notification** | `notification` | Envoie une notification Windows (toast) |
| **Presse-papier** | `lire_presse_papier` | Lit le texte du presse-papier |
| **Presse-papier** | `ecrire_presse_papier` | Ecrit du texte dans le presse-papier |

## Cas d'usage

- **Assistant visuel** : "Regarde mon ecran et dis-moi ce que tu vois"
- **Gestion de fichiers** : "Cree un dossier projet et copie ces fichiers"
- **Monitoring** : "Quel processus utilise le plus de memoire ?"
- **Automatisation** : "Aide-moi a remplir ce formulaire"
- **Debogage** : "Capture cette zone de l'ecran pour voir l'erreur"
- **Notifications** : "Previens-moi quand c'est termine"

## Installation (Windows)

### 1. Cloner le repo

```cmd
git clone https://github.com/mateo-brl/mcp-custom.git
cd mcp-custom
```

### 2. Installer les dependances

```cmd
pip install -e .
```

Cela installe automatiquement :
- `mcp` - SDK MCP
- `mss` - Capture d'ecran rapide
- `Pillow` - Traitement d'images
- `pygetwindow` - Gestion des fenetres Windows
- `psutil` - Monitoring systeme et processus
- `winotify` - Notifications toast Windows

### 3. Configurer Claude Desktop

Ouvrez `%APPDATA%\Claude\claude_desktop_config.json` et ajoutez :

```json
{
  "mcpServers": {
    "mon-mcp-custom": {
      "command": "C:\\Users\\VOTRE_USER\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
      "args": ["-m", "mon_mcp.server"]
    }
  }
}
```

> Remplacez `VOTRE_USER` et `Python313` selon votre configuration.

### 4. Redemarrer Claude Desktop

## Tester

### Test rapide
```cmd
python -c "from mon_mcp.server import ping; print(ping())"
```

### Tests unitaires
```cmd
pytest tests/
```

### Dans Claude Desktop
- "Ping mon MCP"
- "Capture mon ecran"
- "Liste mes fichiers dans C:\Users\moi\Documents"
- "Quel processus utilise le plus de RAM ?"
- "Envoie-moi une notification"

## Structure du projet

```
mcp-custom/
├── src/
│   └── mon_mcp/
│       ├── __init__.py
│       ├── server.py          # Orchestrateur MCP
│       ├── win_api.py         # Windows API (ctypes)
│       └── tools/
│           ├── __init__.py
│           ├── capture.py     # Capture d'ecran
│           ├── clavier.py     # Controle clavier
│           ├── souris.py      # Controle souris
│           ├── fenetres.py    # Gestion fenetres
│           ├── fichiers.py    # Gestion fichiers
│           ├── systeme.py     # Monitoring systeme
│           ├── notification.py # Notifications
│           └── clipboard.py   # Presse-papier
├── tests/
│   ├── test_server.py
│   ├── test_fichiers.py
│   └── test_systeme.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Ajouter un nouvel outil

Creez un fichier dans `src/mon_mcp/tools/` :

```python
def mon_outil(param: str) -> str:
    """Description de l'outil."""
    return f"Resultat: {param}"

def register_tools(mcp):
    mcp.add_tool(mon_outil)
```

Puis importez-le dans `server.py` :

```python
from mon_mcp.tools import mon_module
mon_module.register_tools(mcp)
```

## Securite

Ce MCP donne a Claude la capacite de :
- Voir vos ecrans
- Controler votre souris et clavier
- Lire, ecrire et supprimer des fichiers (chemins systeme proteges)
- Lister et terminer des processus (processus critiques proteges)
- Lire et ecrire dans le presse-papier

**Utilisez-le uniquement si vous faites confiance aux actions demandees.**

## Logs de debug

```
%APPDATA%\Claude\logs\
```

## License

MIT
