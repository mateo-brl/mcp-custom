# Mon MCP Custom 🚀

Un serveur [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) personnalisé et extensible.

> ⚠️ **Note** : Ce guide est actuellement pour **Windows uniquement**. Les instructions pour macOS/Linux seront ajoutées prochainement.

## 📦 Installation (Windows)

```cmd
# Cloner le repo
git clone https://github.com/mateo-brl/mcp-custom.git
cd mcp-custom

# Installer en mode développement (Python global)
pip install -e .
```

### ⚠️ Problèmes connus et solutions

#### Erreur PowerShell "script non signé numériquement"
Si vous essayez d'activer un environnement virtuel dans PowerShell :
```
.venv\Scripts\activate : Impossible de charger le fichier ... n'est pas signé numériquement
```

**Solutions :**
1. **Utiliser cmd.exe** au lieu de PowerShell :
   ```cmd
   .venv\Scripts\activate.bat
   ```
2. **Ou utiliser Python global** (recommandé pour simplifier) :
   ```cmd
   pip install -e .
   ```

#### Erreur "No module named 'mon_mcp'"
Assurez-vous d'avoir installé le package :
```cmd
pip install -e .
```

#### Erreur "Server object has no attribute 'tool'"
Le SDK MCP utilise `FastMCP`, pas `Server`. Vérifiez que votre `server.py` utilise :
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("mon-mcp-custom")

@mcp.tool()  # et non @server.tool()
def mon_outil():
    ...
```

## 🛠️ Outils disponibles

| Outil | Description |
|-------|-------------|
| `saluer` | Salue l'utilisateur par son nom |
| `calculer` | Effectue des opérations mathématiques (add, sub, mul, div) |

## ➕ Ajouter un nouvel outil

Ouvrez `src/mon_mcp/server.py` et ajoutez un nouvel outil :

```python
@mcp.tool()
def mon_nouvel_outil(param1: str, param2: int) -> str:
    """
    Description de ce que fait l'outil.
    
    Args:
        param1: Description du premier paramètre
        param2: Description du deuxième paramètre
        
    Returns:
        Ce que retourne l'outil
    """
    # Ta logique ici
    return f"Résultat: {param1}, {param2}"
```

Puis redémarrez Claude Desktop.

## 🔧 Configuration Claude Desktop (Windows)

1. Ouvrez le fichier de configuration :
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```
   (soit `C:\Users\VOTRE_USER\AppData\Roaming\Claude\claude_desktop_config.json`)

2. Ajoutez cette configuration :

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

> 💡 Remplacez `VOTRE_USER` par votre nom d'utilisateur Windows et `Python313` par votre version de Python.

3. Redémarrez Claude Desktop

## 🧪 Tester le serveur

### Test rapide en ligne de commande
```cmd
python -c "from mon_mcp.server import mcp; print('OK, serveur prêt!')"
```

### Avec MCP Inspector
```cmd
npx @modelcontextprotocol/inspector python -m mon_mcp.server
```

### Dans Claude Desktop
Demandez simplement :
- "Salue [votre nom] avec mon MCP"
- "Calcule 42 + 17"

## 📁 Structure du projet

```
mcp-custom/
├── src/
│   └── mon_mcp/
│       ├── __init__.py
│       └── server.py      # ← Ajoute tes outils ici
├── tests/
│   └── test_server.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## 🔍 Logs de debug

Les logs Claude Desktop se trouvent dans :
```
%APPDATA%\Claude\logs\
```

Consultez-les si le serveur ne démarre pas correctement.

## 📝 License

MIT
