# Mon MCP Custom

Un serveur [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) qui permet a Claude de **voir vos ecrans**, **interagir avec votre ordinateur**, **gerer vos fichiers**, **surveiller votre systeme** et plus encore.

> **Compatible Windows et Linux** — detection automatique de la plateforme.

## Fonctionnalites (37 outils)

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
| **Notification** | `notification` | Envoie une notification desktop (toast) |
| **Presse-papier** | `lire_presse_papier` | Lit le texte du presse-papier |
| **Presse-papier** | `ecrire_presse_papier` | Ecrit du texte dans le presse-papier |
| **Lanceur** | `lancer_app` | Lance une application par nom ou chemin |
| **Lanceur** | `ouvrir_url` | Ouvre une URL dans le navigateur par defaut |
| **Recherche** | `rechercher_fichiers` | Recherche de fichiers par nom, contenu ou extension |
| **OCR** | `ocr_image` | Extrait le texte d'une image (necessite Tesseract) |
| **OCR** | `ocr_ecran` | Capture une region de l'ecran et extrait le texte |
| **Excel/CSV** | `lire_excel` | Lit un fichier .xlsx en JSON |
| **Excel/CSV** | `ecrire_excel` | Cree un fichier .xlsx depuis des donnees JSON |
| **Excel/CSV** | `lire_csv` | Lit un fichier CSV en JSON |
| **Excel/CSV** | `ecrire_csv` | Ecrit un fichier CSV depuis des donnees JSON |
| **Excel/CSV** | `info_excel` | Infos sur un fichier Excel (feuilles, lignes, colonnes) |

## Cas d'usage

- **Assistant visuel** : "Regarde mon ecran et dis-moi ce que tu vois"
- **Gestion de fichiers** : "Cree un dossier projet et copie ces fichiers"
- **Monitoring** : "Quel processus utilise le plus de memoire ?"
- **Automatisation** : "Aide-moi a remplir ce formulaire"
- **Debogage** : "Capture cette zone de l'ecran pour voir l'erreur"
- **Notifications** : "Previens-moi quand c'est termine"
- **Recherche** : "Trouve tous les fichiers .csv contenant 'budget' dans mes Documents"
- **OCR** : "Lis le texte de cette capture d'ecran"
- **Excel** : "Cree un fichier Excel avec ces donnees clients"
- **Lanceur** : "Ouvre VS Code et le site de Jira"

## Installation

### 1. Cloner le repo

```bash
git clone https://github.com/mateo-brl/mcp-custom.git
cd mcp-custom
```

### 2. Installer les dependances

```bash
pip install -e .
```

Les dependances sont installees automatiquement selon votre plateforme :

| Dependance | Windows | Linux | Usage |
|------------|---------|-------|-------|
| `mcp` | oui | oui | SDK MCP |
| `mss` | oui | oui | Capture d'ecran |
| `Pillow` | oui | oui | Traitement d'images |
| `psutil` | oui | oui | Monitoring systeme |
| `pygetwindow` | oui | — | Gestion fenetres Windows |
| `winotify` | oui | — | Notifications Windows |
| `pynput` | — | oui | Controle souris/clavier Linux |
| `pyperclip` | — | oui | Presse-papier Linux |
| `notify-py` | — | oui | Notifications Linux |

### Extras optionnels

```bash
# OCR (necessite aussi Tesseract installe sur le systeme)
pip install -e ".[ocr]"

# Excel (.xlsx)
pip install -e ".[excel]"

# Tout installer
pip install -e ".[all]"
```

### 3. Configurer Claude Desktop

#### Windows

Ouvrez `%APPDATA%\Claude\claude_desktop_config.json` :

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

#### Linux

Ouvrez `~/.config/Claude/claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "mon-mcp-custom": {
      "command": "python3",
      "args": ["-m", "mon_mcp.server"]
    }
  }
}
```

> Remplacez les chemins selon votre configuration.

### 4. Redemarrer Claude Desktop

## Tester

### Test rapide
```bash
python -c "from mon_mcp.server import ping; print(ping())"
```

### Tests unitaires
```bash
pytest tests/
```

### Dans Claude Desktop
- "Ping mon MCP"
- "Capture mon ecran"
- "Liste mes fichiers dans ~/Documents"
- "Quel processus utilise le plus de RAM ?"
- "Envoie-moi une notification"
- "Trouve les fichiers Excel dans mon bureau"
- "Cree un CSV avec ces donnees"

## Structure du projet

```
mcp-custom/
├── src/
│   └── mon_mcp/
│       ├── __init__.py
│       ├── server.py              # Orchestrateur MCP (37 outils)
│       ├── platform_api.py        # Routeur plateforme (auto-detect OS)
│       ├── _platform_windows.py   # Backend Windows (ctypes, pygetwindow)
│       ├── _platform_linux.py     # Backend Linux (pynput, pyperclip)
│       ├── _platform_stub.py      # Stub plateformes non supportees
│       ├── win_api.py             # Shim retrocompatibilite (deprecie)
│       └── tools/
│           ├── __init__.py
│           ├── capture.py         # Capture d'ecran (mss)
│           ├── clavier.py         # Controle clavier
│           ├── souris.py          # Controle souris
│           ├── fenetres.py        # Gestion fenetres
│           ├── fichiers.py        # Gestion fichiers
│           ├── systeme.py         # Monitoring systeme
│           ├── notification.py    # Notifications desktop
│           ├── clipboard.py       # Presse-papier
│           ├── lanceur.py         # Lanceur d'apps / URLs
│           ├── recherche.py       # Recherche de fichiers
│           ├── ocr.py             # OCR (pytesseract)
│           └── excel.py           # Excel/CSV
├── tests/
│   ├── test_server.py
│   ├── test_fichiers.py
│   ├── test_systeme.py
│   ├── test_lanceur.py
│   ├── test_recherche.py
│   └── test_excel.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Architecture plateforme

```
platform_api.py  ──┬── _platform_windows.py  (ctypes user32/kernel32, pygetwindow, winotify)
                   ├── _platform_linux.py     (pynput, pyperclip, notifypy, wmctrl)
                   └── _platform_stub.py      (erreurs descriptives)
```

Le routeur `platform_api.py` detecte automatiquement l'OS au demarrage et charge le bon backend. Tous les modules d'outils importent depuis `platform_api` — aucun code specifique a un OS dans les outils.

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
- Lancer des applications et ouvrir des URLs

Les chemins systeme et processus critiques sont proteges automatiquement selon la plateforme (Windows et Linux).

**Utilisez-le uniquement si vous faites confiance aux actions demandees.**

## Logs de debug

- **Windows** : `%APPDATA%\Claude\logs\`
- **Linux** : `~/.config/Claude/logs/`

## License

MIT
