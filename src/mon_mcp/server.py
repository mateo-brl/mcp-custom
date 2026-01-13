"""
Serveur MCP Custom - Point d'entrée principal.

Ce serveur peut être étendu en ajoutant de nouveaux outils avec le décorateur @mcp.tool()
"""

from mcp.server.fastmcp import FastMCP

# Création du serveur MCP
mcp = FastMCP("mon-mcp-custom")


# =============================================================================
# OUTILS - Ajoute tes outils ici avec @mcp.tool()
# =============================================================================

@mcp.tool()
def saluer(nom: str) -> str:
    """
    Un outil exemple qui salue l'utilisateur.
    
    Args:
        nom: Le nom de la personne à saluer
        
    Returns:
        Un message de salutation personnalisé
    """
    return f"Bonjour {nom} ! Bienvenue sur mon MCP custom 🎉"


@mcp.tool()
def calculer(operation: str, a: float, b: float) -> str:
    """
    Effectue une opération mathématique simple.
    
    Args:
        operation: L'opération à effectuer (add, sub, mul, div)
        a: Premier nombre
        b: Deuxième nombre
        
    Returns:
        Le résultat de l'opération
    """
    operations = {
        "add": lambda x, y: x + y,
        "sub": lambda x, y: x - y,
        "mul": lambda x, y: x * y,
        "div": lambda x, y: x / y if y != 0 else "Erreur: division par zéro",
    }
    
    if operation not in operations:
        return f"Opération inconnue: {operation}. Utilise: add, sub, mul, div"
    
    result = operations[operation](a, b)
    return f"{a} {operation} {b} = {result}"


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
