# Mon MCP Custom 🚀

Un serveur [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) personnalisé et extensible.

## 📦 Installation

```bash
# Cloner le repo
git clone https://github.com/TON_USERNAME/mon-mcp-custom.git
cd mon-mcp-custom

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer en mode développement
pip install -e ".[dev]"
```

## 🛠️ Outils disponibles

| Outil | Description |
|-------|-------------|
| `saluer` | Salue l'utilisateur par son nom |
| `calculer` | Effectue des opérations mathématiques (add, sub, mul, div) |

## ➕ Ajouter un nouvel outil

Ouvre `src/mon_mcp/server.py` et ajoute un nouvel outil :

```python
@server.tool()
async def mon_nouvel_outil(param1: str, param2: int) -> str:
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

## 🔧 Configuration avec Claude Desktop

Ajoute ceci dans ton fichier de configuration Claude Desktop (`claude_desktop_config.json`) :

### macOS/Linux
```json
{
  "mcpServers": {
    "mon-mcp-custom": {
      "command": "/chemin/vers/mon-mcp-custom/.venv/bin/python",
      "args": ["-m", "mon_mcp.server"]
    }
  }
}
```

### Windows
```json
{
  "mcpServers": {
    "mon-mcp-custom": {
      "command": "C:\\chemin\\vers\\mon-mcp-custom\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mon_mcp.server"]
    }
  }
}
```

## 🧪 Tests

```bash
pytest
```

## 📁 Structure du projet

```
mon-mcp-custom/
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

## 📝 License

MIT
