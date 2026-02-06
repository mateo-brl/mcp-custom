"""Tests pour les outils Excel/CSV."""

import json

import pytest

openpyxl = pytest.importorskip("openpyxl")

from mon_mcp.tools.excel import (
    lire_excel,
    ecrire_excel,
    lire_csv,
    ecrire_csv,
    info_excel,
)


def test_round_trip_excel(tmp_path):
    """Test ecriture puis lecture Excel."""
    f = str(tmp_path / "test.xlsx")
    donnees = json.dumps([
        {"nom": "Alice", "age": 30},
        {"nom": "Bob", "age": 25},
    ])

    result = ecrire_excel(f, donnees)
    assert "ecrit" in result.lower()

    result = lire_excel(f)
    data = json.loads(result)
    assert data["lignes"] == 2
    assert data["colonnes"] == ["nom", "age"]
    assert data["donnees"][0]["nom"] == "Alice"


def test_round_trip_csv(tmp_path):
    """Test ecriture puis lecture CSV."""
    f = str(tmp_path / "test.csv")
    donnees = json.dumps([
        {"ville": "Paris", "pays": "France"},
        {"ville": "Berlin", "pays": "Allemagne"},
    ])

    result = ecrire_csv(f, donnees)
    assert "ecrit" in result.lower()

    result = lire_csv(f)
    data = json.loads(result)
    assert data["lignes"] == 2
    assert "Paris" in data["donnees"][0]["ville"]


def test_info_excel(tmp_path):
    """Test info Excel."""
    f = str(tmp_path / "info_test.xlsx")
    donnees = json.dumps([
        ["Nom", "Age"],
        ["Alice", 30],
    ])
    ecrire_excel(f, donnees)

    result = info_excel(f)
    data = json.loads(result)
    assert data["nombre_feuilles"] == 1
    assert data["feuilles"][0]["nom"] == "Sheet1"


def test_lire_excel_inexistant():
    """Test lecture fichier inexistant."""
    result = lire_excel("C:\\fichier_inexistant.xlsx")
    assert "n'existe pas" in result


def test_ecrire_excel_liste_de_listes(tmp_path):
    """Test ecriture avec liste de listes."""
    f = str(tmp_path / "listes.xlsx")
    donnees = json.dumps([
        ["Produit", "Prix"],
        ["Pomme", 1.5],
        ["Banane", 0.8],
    ])

    result = ecrire_excel(f, donnees)
    assert "ecrit" in result.lower()

    result = lire_excel(f)
    data = json.loads(result)
    assert data["lignes"] == 2
