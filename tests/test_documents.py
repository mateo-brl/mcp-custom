"""Tests pour le module documents."""

import json
import os
import tempfile

import pytest


def test_creer_word():
    """Test creation d'un document Word."""
    pytest.importorskip("docx")
    from mon_mcp.tools.documents import creer_word

    with tempfile.TemporaryDirectory() as tmpdir:
        chemin = os.path.join(tmpdir, "test.docx")
        contenu = "# Titre\n\nUn paragraphe de test.\n\n- Point 1\n- Point 2"
        result = json.loads(creer_word(chemin, contenu))
        assert "fichier" in result
        assert result["paragraphes"] >= 3
        assert os.path.exists(chemin)


def test_creer_word_manquant():
    """Test message d'erreur quand python-docx manquant."""
    # Ce test verifie juste que la fonction ne crash pas
    from mon_mcp.tools.documents import creer_word
    result = json.loads(creer_word("test.docx", "contenu"))
    # Soit ca marche (docx installe), soit erreur propre
    assert "fichier" in result or "erreur" in result


def test_creer_powerpoint():
    """Test creation d'une presentation PowerPoint."""
    pytest.importorskip("pptx")
    from mon_mcp.tools.documents import creer_powerpoint

    with tempfile.TemporaryDirectory() as tmpdir:
        chemin = os.path.join(tmpdir, "test.pptx")
        slides = json.dumps([
            {"titre": "Slide 1", "contenu": ["Point A", "Point B"]},
            {"titre": "Slide 2", "contenu": ["Point C"]},
        ])
        result = json.loads(creer_powerpoint(chemin, slides))
        assert result["diapositives"] == 2
        assert os.path.exists(chemin)


def test_creer_pdf():
    """Test creation d'un PDF."""
    pytest.importorskip("reportlab")
    from mon_mcp.tools.documents import creer_pdf

    with tempfile.TemporaryDirectory() as tmpdir:
        chemin = os.path.join(tmpdir, "test.pdf")
        contenu = "# Rapport\n\nContenu du rapport.\n\n- Point 1\n- Point 2"
        result = json.loads(creer_pdf(chemin, contenu))
        assert "fichier" in result
        assert os.path.exists(chemin)
