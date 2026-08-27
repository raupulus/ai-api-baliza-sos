"""Pruebas unitarias de integridad para las fuentes de conocimiento ampliadas de Cádiz."""

from __future__ import annotations

import unittest

from common.models import Categoria
from updater.sources.fiestas_cadiz import FiestasCadizSource
from updater.sources.flora_fauna_cadiz import FloraFaunaCadizSource
from updater.sources.historia_cadiz import HistoriaCadizSource
from updater.sources.municipios_cadiz import MunicipiosCadizSource
from updater.sources.primeros_auxilios_avanzado import PrimerosAuxiliosAvanzadoSource


class TestSourcesCadiz(unittest.TestCase):

    def test_primeros_auxilios_avanzado_source(self):
        source = PrimerosAuxiliosAvanzadoSource()
        fragmentos = source.fetch()
        self.assertGreaterEqual(len(fragmentos), 10)

        for f in fragmentos:
            self.assertTrue(f.texto and len(f.texto) > 30)
            self.assertIn(f.categoria, (Categoria.PRIMEROS_AUXILIOS, Categoria.SUPERVIVENCIA))
            self.assertEqual(f.nivel_confianza, "alta")
            # Contenido médico sensible: debe tener validador humano explícito
            self.assertIsNotNone(f.validado_por)
            self.assertTrue(f.hash_contenido)

    def test_flora_fauna_cadiz_source(self):
        source = FloraFaunaCadizSource()
        fragmentos = source.fetch()
        self.assertGreaterEqual(len(fragmentos), 10)

        for f in fragmentos:
            self.assertTrue(f.texto and len(f.texto) > 30)
            self.assertIn(f.categoria, (Categoria.FLORA, Categoria.FAUNA))
            self.assertEqual(f.provincia, "Cádiz")
            self.assertTrue(f.hash_contenido)

    def test_municipios_cadiz_source_y_coordenadas(self):
        source = MunicipiosCadizSource()
        fragmentos = source.fetch()
        # 45 municipios + cumbres orográficas
        self.assertGreaterEqual(len(fragmentos), 45)

        for f in fragmentos:
            self.assertTrue(f.texto and len(f.texto) > 20)
            self.assertEqual(f.categoria, Categoria.GEOGRAFIA)
            # Comprobar metadatos de coordenadas geográficas
            self.assertIn("lat", f.metadatos)
            self.assertIn("lon", f.metadatos)
            lat = float(f.metadatos["lat"])
            lon = float(f.metadatos["lon"])
            # BBOX aproximado de la provincia de Cádiz: lat [35.9, 37.1], lon [-6.6, -5.1]
            self.assertTrue(35.8 <= lat <= 37.2, f"Latitud fuera de rango: {lat}")
            self.assertTrue(-6.7 <= lon <= -5.0, f"Longitud fuera de rango: {lon}")

    def test_fiestas_cadiz_source(self):
        source = FiestasCadizSource()
        fragmentos = source.fetch()
        self.assertGreaterEqual(len(fragmentos), 8)

        for f in fragmentos:
            self.assertTrue(f.texto and len(f.texto) > 30)
            self.assertEqual(f.categoria, Categoria.CULTURA_HISTORIA)
            self.assertTrue(f.hash_contenido)

    def test_historia_cadiz_source(self):
        source = HistoriaCadizSource()
        fragmentos = source.fetch()
        self.assertGreaterEqual(len(fragmentos), 5)

        for f in fragmentos:
            self.assertTrue(f.texto and len(f.texto) > 30)
            self.assertEqual(f.categoria, Categoria.CULTURA_HISTORIA)
            self.assertTrue(f.hash_contenido)


if __name__ == "__main__":
    unittest.main()
