"""
Module d'operations web (telechargement, extraction de texte/liens).

Utilise urllib (stdlib) par defaut, avec fallback sur requests/beautifulsoup4 si disponibles.

Outils: telecharger_url, extraire_texte_url, verifier_url, extraire_liens
"""

import json
import os
import re
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

# Limite de taille de telechargement (100 MB)
MAX_DOWNLOAD_SIZE = 100 * 1024 * 1024

# User-Agent pour eviter les blocages
USER_AGENT = "Mozilla/5.0 (compatible; MCP-Custom/0.6)"


def _validate_url(url: str) -> str | None:
    """Valide et normalise une URL. Retourne None si invalide."""
    url = url.strip()
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    if not re.match(r"https?://[^\s/$.?#].[^\s]*", url):
        return None
    return url


class _TextExtractor(HTMLParser):
    """Extracteur de texte brut depuis HTML (stdlib, sans BeautifulSoup)."""

    SKIP_TAGS = {"script", "style", "nav", "footer", "header", "noscript", "svg", "iframe"}

    def __init__(self):
        super().__init__()
        self.text_parts: list[str] = []
        self.links: list[dict] = []
        self.title = ""
        self._skip_depth = 0
        self._in_title = False
        self._current_link: dict | None = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "a" and "href" in attrs_dict:
            self._current_link = {"href": attrs_dict["href"], "texte": ""}
        if tag in ("br", "p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr"):
            self.text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._current_link:
            self.links.append(self._current_link)
            self._current_link = None

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()
        if self._skip_depth == 0:
            self.text_parts.append(data)
        if self._current_link is not None:
            self._current_link["texte"] += data.strip()


def _fetch_url(url: str, timeout: int = 30) -> tuple[bytes, dict]:
    """Telecharge le contenu d'une URL. Retourne (contenu, headers)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        # Verifier la taille
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_DOWNLOAD_SIZE:
            raise ValueError(f"Fichier trop volumineux: {int(content_length)} octets (max: {MAX_DOWNLOAD_SIZE})")

        content = response.read(MAX_DOWNLOAD_SIZE + 1)
        if len(content) > MAX_DOWNLOAD_SIZE:
            raise ValueError(f"Fichier trop volumineux (max: {MAX_DOWNLOAD_SIZE} octets)")

        headers = {k: v for k, v in response.headers.items()}
        return content, headers


def telecharger_url(url: str, destination: str, timeout: int = 30) -> str:
    """
    Telecharge un fichier depuis une URL.

    Args:
        url: L'URL du fichier a telecharger
        destination: Chemin local ou sauvegarder le fichier
        timeout: Timeout en secondes (defaut: 30)

    Returns:
        JSON avec url, fichier, taille, type_contenu, duree.
    """
    url = _validate_url(url)
    if not url:
        return json.dumps({"erreur": "URL invalide. Doit commencer par http:// ou https://"}, ensure_ascii=False)

    destination = os.path.abspath(destination)
    timeout = min(max(1, timeout), 120)

    try:
        start = time.time()
        content, headers = _fetch_url(url, timeout)
        duree = round(time.time() - start, 3)

        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, "wb") as f:
            f.write(content)

        taille = len(content)
        if taille < 1024:
            taille_str = f"{taille} B"
        elif taille < 1024 * 1024:
            taille_str = f"{taille / 1024:.1f} KB"
        else:
            taille_str = f"{taille / (1024 * 1024):.1f} MB"

        return json.dumps({
            "url": url,
            "fichier": destination,
            "taille": taille_str,
            "taille_octets": taille,
            "type_contenu": headers.get("Content-Type", "inconnu"),
            "duree_secondes": duree,
        }, ensure_ascii=False)

    except urllib.error.HTTPError as e:
        return json.dumps({"erreur": f"Erreur HTTP {e.code}: {e.reason}"}, ensure_ascii=False)
    except urllib.error.URLError as e:
        return json.dumps({"erreur": f"Erreur URL: {e.reason}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"erreur": str(e)}, ensure_ascii=False)


def extraire_texte_url(url: str, timeout: int = 30) -> str:
    """
    Extrait le texte lisible d'une page web.

    Args:
        url: L'URL de la page a lire
        timeout: Timeout en secondes (defaut: 30)

    Returns:
        JSON avec url, titre, texte, longueur.
    """
    url = _validate_url(url)
    if not url:
        return json.dumps({"erreur": "URL invalide."}, ensure_ascii=False)

    timeout = min(max(1, timeout), 120)

    try:
        start = time.time()
        content, headers = _fetch_url(url, timeout)
        duree = round(time.time() - start, 3)

        content_type = headers.get("Content-Type", "")
        if "text/html" not in content_type and "text/plain" not in content_type:
            # Pas du HTML/texte, retourner info basique
            return json.dumps({
                "url": url,
                "type_contenu": content_type,
                "erreur": "Le contenu n'est pas du texte/HTML.",
                "taille_octets": len(content),
            }, ensure_ascii=False)

        # Decoder le HTML
        encoding = "utf-8"
        if "charset=" in content_type:
            encoding = content_type.split("charset=")[-1].split(";")[0].strip()

        try:
            html = content.decode(encoding, errors="replace")
        except (LookupError, UnicodeDecodeError):
            html = content.decode("utf-8", errors="replace")

        # Essayer BeautifulSoup d'abord (meilleure extraction)
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            # Supprimer les elements non-textuels
            for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                tag.decompose()
            titre = soup.title.string.strip() if soup.title and soup.title.string else ""
            texte = soup.get_text(separator="\n", strip=True)
        except ImportError:
            # Fallback sur HTMLParser stdlib
            parser = _TextExtractor()
            parser.feed(html)
            titre = parser.title
            texte = "".join(parser.text_parts)

        # Nettoyer le texte
        lines = [line.strip() for line in texte.split("\n")]
        texte = "\n".join(line for line in lines if line)

        # Limiter la taille du texte
        tronque = False
        if len(texte) > 50000:
            texte = texte[:50000]
            tronque = True

        return json.dumps({
            "url": url,
            "titre": titre,
            "texte": texte,
            "longueur": len(texte),
            "tronque": tronque,
            "duree_secondes": duree,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"erreur": str(e)}, ensure_ascii=False)


def verifier_url(url: str, timeout: int = 10) -> str:
    """
    Verifie si une URL est accessible (requete HEAD).

    Args:
        url: L'URL a verifier
        timeout: Timeout en secondes (defaut: 10)

    Returns:
        JSON avec accessible, code_statut, type_contenu, temps_reponse.
    """
    url = _validate_url(url)
    if not url:
        return json.dumps({"erreur": "URL invalide."}, ensure_ascii=False)

    timeout = min(max(1, timeout), 30)

    try:
        start = time.time()
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            duree_ms = round((time.time() - start) * 1000)
            content_length = response.headers.get("Content-Length")
            return json.dumps({
                "url": url,
                "accessible": True,
                "code_statut": response.status,
                "type_contenu": response.headers.get("Content-Type", "inconnu"),
                "taille": int(content_length) if content_length else None,
                "temps_reponse_ms": duree_ms,
            }, ensure_ascii=False)

    except urllib.error.HTTPError as e:
        duree_ms = round((time.time() - start) * 1000)
        return json.dumps({
            "url": url,
            "accessible": False,
            "code_statut": e.code,
            "raison": e.reason,
            "temps_reponse_ms": duree_ms,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "url": url,
            "accessible": False,
            "erreur": str(e),
        }, ensure_ascii=False)


def extraire_liens(url: str, filtre: str = "", timeout: int = 30) -> str:
    """
    Extrait tous les liens d'une page web.

    Args:
        url: L'URL de la page
        filtre: Filtre optionnel pour les liens (ex: ".pdf", "download")
        timeout: Timeout en secondes (defaut: 30)

    Returns:
        JSON avec la liste des liens (texte, href, type).
    """
    url = _validate_url(url)
    if not url:
        return json.dumps({"erreur": "URL invalide."}, ensure_ascii=False)

    timeout = min(max(1, timeout), 120)

    try:
        content, headers = _fetch_url(url, timeout)

        content_type = headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return json.dumps({"erreur": "Le contenu n'est pas du HTML."}, ensure_ascii=False)

        encoding = "utf-8"
        if "charset=" in content_type:
            encoding = content_type.split("charset=")[-1].split(";")[0].strip()

        try:
            html = content.decode(encoding, errors="replace")
        except (LookupError, UnicodeDecodeError):
            html = content.decode("utf-8", errors="replace")

        # Extraire les liens
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            liens_bruts = []
            for a in soup.find_all("a", href=True):
                liens_bruts.append({
                    "texte": a.get_text(strip=True) or "",
                    "href": a["href"],
                })
        except ImportError:
            parser = _TextExtractor()
            parser.feed(html)
            liens_bruts = parser.links

        # Classifier et filtrer les liens
        from urllib.parse import urljoin, urlparse
        base_domain = urlparse(url).netloc

        liens = []
        for lien in liens_bruts:
            href = lien["href"]
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            # Resoudre les URLs relatives
            href_absolu = urljoin(url, href)
            parsed = urlparse(href_absolu)

            lien_type = "interne" if parsed.netloc == base_domain else "externe"

            if filtre and filtre.lower() not in href_absolu.lower() and filtre.lower() not in lien["texte"].lower():
                continue

            liens.append({
                "texte": lien["texte"][:100],
                "href": href_absolu,
                "type": lien_type,
            })

        # Limiter le nombre de liens
        total = len(liens)
        liens = liens[:500]

        return json.dumps({
            "url": url,
            "liens": liens,
            "total": total,
            "filtre": filtre or None,
            "limite_atteinte": total > 500,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"erreur": str(e)}, ensure_ascii=False)


def register_tools(mcp):
    mcp.add_tool(telecharger_url)
    mcp.add_tool(extraire_texte_url)
    mcp.add_tool(verifier_url)
    mcp.add_tool(extraire_liens)
