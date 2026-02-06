"""Tests pour les outils de gestion de fichiers."""

import json
from pathlib import Path

from mon_mcp.tools.fichiers import (
    lire_fichier,
    ecrire_fichier,
    copier_fichier,
    deplacer_fichier,
    supprimer_fichier,
    lister_repertoire,
    info_fichier,
    creer_repertoire,
)


def test_ecrire_et_lire_fichier(tmp_path):
    """Test ecriture puis lecture d'un fichier."""
    f = str(tmp_path / "test.txt")
    result = ecrire_fichier(f, "Bonjour le monde")
    assert "Fichier ecrit" in result

    result = lire_fichier(f)
    data = json.loads(result)
    assert data["contenu"] == "Bonjour le monde"
    assert data["lignes"] == 1


def test_lire_fichier_inexistant():
    """Test lecture d'un fichier qui n'existe pas."""
    result = lire_fichier("C:\\inexistant_12345.txt")
    assert "n'existe pas" in result


def test_copier_fichier(tmp_path):
    """Test copie de fichier."""
    src = tmp_path / "source.txt"
    src.write_text("contenu original")
    dst = str(tmp_path / "copie.txt")

    result = copier_fichier(str(src), dst)
    assert "copie" in result.lower()
    assert Path(dst).read_text() == "contenu original"


def test_deplacer_fichier(tmp_path):
    """Test deplacement de fichier."""
    src = tmp_path / "avant.txt"
    src.write_text("contenu")
    dst = str(tmp_path / "apres.txt")

    result = deplacer_fichier(str(src), dst)
    assert "Deplace" in result
    assert not src.exists()
    assert Path(dst).read_text() == "contenu"


def test_supprimer_fichier(tmp_path):
    """Test suppression de fichier."""
    f = tmp_path / "a_supprimer.txt"
    f.write_text("bye")

    result = supprimer_fichier(str(f))
    assert "supprime" in result.lower()
    assert not f.exists()


def test_supprimer_refuse_chemin_systeme():
    """Test que les chemins systeme sont refuses."""
    result = supprimer_fichier("C:\\Windows")
    assert "protege" in result.lower() or "refuse" in result.lower()


def test_supprimer_refuse_racine():
    """Test que les racines de lecteur sont refusees."""
    result = supprimer_fichier("C:\\")
    assert "protege" in result.lower() or "refuse" in result.lower()


def test_lister_repertoire(tmp_path):
    """Test listage de repertoire."""
    (tmp_path / "fichier1.txt").write_text("a")
    (tmp_path / "fichier2.txt").write_text("b")
    (tmp_path / "dossier").mkdir()

    result = lister_repertoire(str(tmp_path))
    data = json.loads(result)
    assert data["nombre_elements"] == 3


def test_info_fichier(tmp_path):
    """Test info fichier."""
    f = tmp_path / "info_test.txt"
    f.write_text("test contenu")

    result = info_fichier(str(f))
    data = json.loads(result)
    assert data["type"] == "fichier"
    assert data["extension"] == ".txt"
    assert data["taille_octets"] > 0


def test_creer_repertoire(tmp_path):
    """Test creation de repertoire."""
    d = str(tmp_path / "nouveau" / "sous_dossier")
    result = creer_repertoire(d)
    assert "cree" in result.lower()
    assert Path(d).is_dir()


def test_creer_repertoire_existant(tmp_path):
    """Test creation d'un repertoire qui existe deja."""
    result = creer_repertoire(str(tmp_path))
    assert "existe deja" in result
