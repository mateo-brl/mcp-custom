# Mon MCP Custom 🚀

Un serveur [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) qui permet à Claude de **voir vos écrans** et **interagir avec votre ordinateur** pour vous assister comme un véritable agent.

> ⚠️ **Note** : Ce MCP est actuellement pour **Windows uniquement**.

## ✨ Fonctionnalités

| Catégorie | Outil | Description |
|-----------|-------|-------------|
| 🔧 **Diagnostic** | `ping` | Vérifie que le MCP fonctionne et liste les dépendances |
| 📸 **Capture** | `capture_ecrans` | Capture tous les écrans de l'ordinateur |
| 📸 **Capture** | `capture_ecran_principal` | Capture uniquement l'écran principal |
| 🪟 **Fenêtres** | `liste_fenetres` | Liste toutes les fenêtres ouvertes |
| 🪟 **Fenêtres** | `focus_fenetre` | Active une fenêtre par son titre |
| 🖱️ **Souris** | `clic_souris` | Clic à une position (x, y) |
| 🖱️ **Souris** | `double_clic` | Double-clic à une position |
| 🖱️ **Souris** | `position_souris` | Retourne la position actuelle |
| 🖱️ **Souris** | `deplacer_souris` | Déplace la souris vers une position |
| 🖱️ **Souris** | `scroll` | Scroll up/down |
| ⌨️ **Clavier** | `ecrire_texte` | Écrit du texte au clavier |
| ⌨️ **Clavier** | `touche_clavier` | Appuie sur une touche (enter, ctrl+c, etc.) |

## 🎯 Cas d'usage

- **Assistant visuel** : "Regarde mon écran et dis-moi ce que tu vois"
- **Automatisation guidée** : "Aide-moi à remplir ce formulaire"
- **Débogage** : "Capture mon écran pour voir l'erreur"
- **Navigation assistée** : "Clique sur le bouton Valider"

## 📦 Installation (Windows)

### 1. Cloner le repo

```cmd
git clone https://github.com/mateo-brl/mcp-custom.git
cd mcp-custom
```

### 2. Installer les dépendances

```cmd
pip install -e .
```

Cela installe automatiquement :
- `mcp` - SDK MCP
- `mss` - Capture d'écran rapide
- `Pillow` - Traitement d'images
- `pyautogui` - Contrôle souris/clavier
- `pygetwindow` - Gestion des fenêtres Windows

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

> 💡 Remplacez `VOTRE_USER` et `Python313` selon votre configuration.

### 4. Redémarrer Claude Desktop

## 🧪 Tester

### Test rapide
```cmd
python -c "from mon_mcp.server import ping; print(ping())"
```

### Dans Claude Desktop
Demandez simplement :
- "Ping mon MCP"
- "Capture mon écran"
- "Liste mes fenêtres ouvertes"

## ⚠️ Problèmes connus et solutions

### Erreur PowerShell "script non signé numériquement"
```
.venv\Scripts\activate : Impossible de charger le fichier ... n'est pas signé numériquement
```

**Solution** : Utilisez `cmd.exe` au lieu de PowerShell, ou installez directement avec Python global :
```cmd
pip install -e .
```

### Erreur "No module named 'mon_mcp'"
Assurez-vous d'avoir installé le package :
```cmd
pip install -e .
```

### Erreur "Server object has no attribute 'tool'"
Vérifiez que `server.py` utilise `FastMCP` :
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("mon-mcp-custom")
```

### Les captures d'écran ne fonctionnent pas
Installez les dépendances manuellement :
```cmd
pip install mss Pillow pyautogui pygetwindow
```

## 📁 Structure du projet

```
mcp-custom/
├── src/
│   └── mon_mcp/
│       ├── __init__.py
│       └── server.py      # ← Les outils MCP
├── tests/
│   └── test_server.py
├── pyproject.toml         # Dépendances
├── README.md
├── LICENSE
└── .gitignore
```

## ➕ Ajouter un nouvel outil

Ouvrez `src/mon_mcp/server.py` et ajoutez :

```python
@mcp.tool()
def mon_outil(param: str) -> str:
    """Description de l'outil."""
    return f"Résultat: {param}"
```

Puis redémarrez Claude Desktop.

## 🔍 Logs de debug

Les logs Claude Desktop se trouvent dans :
```
%APPDATA%\Claude\logs\
```

## 🔒 Sécurité

Ce MCP donne à Claude la capacité de :
- Voir vos écrans
- Contrôler votre souris et clavier
- Lister et activer des fenêtres

**Utilisez-le uniquement si vous faites confiance aux actions demandées.** Claude vous demandera toujours confirmation avant d'effectuer des actions sensibles.

## 📝 License

MIT

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une PR.
