import unittest

import pandas as pd

from src.processing.data_unificada import vincular, validar_publicaciones


class IntegracionTest(unittest.TestCase):
    def setUp(self):
        self.meetings = pd.DataFrame({
            "id_reunion": ["RPM_20241010", "RPM_20241011"],
            "fecha_decision": pd.to_datetime(["2024-10-10", "2024-10-11"]),
            "fecha_corte": pd.to_datetime(["2024-10-09", "2024-10-10"]),
            "tipo_reunion": ["ordinaria"] * 2, "decision": ["mantiene"] * 2})
        self.datasets = {"x": pd.DataFrame({"id_observacion": ["x1", "x2"],
            "fecha": pd.to_datetime(["2024-08-01", "2024-09-01"]), "x": [999, 999]})}
        self.publications = pd.DataFrame([
            ["x1", "x", "2024-09-05", 1, "boletin", "original"],
            ["x2", "x", "2024-10-09", 2, "boletin", "original"],
            ["x2", "x", "2024-10-11", 3, "boletin", "revision"],
            ["x1", "x", "2024-10-10", 4, "boletin", "revision antigua"],
        ], columns=["id_observacion", "variable", "fecha_disponible", "valor_publicado",
                    "fuente_publicacion", "evidencia_version"])
        self.cobertura = pd.DataFrame({'variable': ['x'], 'inicio': ['2024-09-05'], 'fin': ['2024-10-10']})

    def test_no_futuro_ni_revision_ni_periodo_antiguo(self):
        # Adaptar metadatos del panel sintético a las 8 columnas de producción.
        from unittest.mock import patch
        with patch("src.processing.data_unificada.SERIES", [("x",)]):
            links, unified = vincular(self.meetings, self.datasets, self.publications, self.cobertura)
        self.assertEqual(links.valor.tolist(), [2, 2])
        self.assertEqual(links.id_observacion.tolist(), ["x2", "x2"])
        self.assertTrue(unified.lista_para_modelo.all())
        self.assertNotIn("variacion_pb", unified)

    def test_no_arrastra_ejemplo_fuera_de_calendario_documentado(self):
        from unittest.mock import patch
        coverage = self.cobertura.copy()
        coverage['fin'] = '2024-10-09'
        with patch('src.processing.data_unificada.SERIES', [('x',)]):
            links, unified = vincular(self.meetings, self.datasets, self.publications, coverage)
        self.assertEqual(links.iloc[0].valor, 2)
        self.assertTrue(pd.isna(links.iloc[1].valor))
        self.assertEqual(unified.lista_para_modelo.tolist(), [True, False])

    def test_sin_calendario_no_declara_lista_para_modelo(self):
        from unittest.mock import patch
        with patch('src.processing.data_unificada.SERIES', [('x',)]):
            _, unified = vincular(self.meetings, self.datasets, self.publications)
        self.assertFalse(unified.lista_para_modelo.any())

    def test_publicacion_posterior_no_se_une_por_mes(self):
        from unittest.mock import patch
        future = self.publications.iloc[[2]]
        with patch("src.processing.data_unificada.SERIES", [("x",)]):
            links, unified = vincular(self.meetings, self.datasets, future)
        self.assertTrue(links.valor.isna().all())
        self.assertTrue(links.candidato_valor.eq(999).all())
        self.assertFalse(unified.lista_para_modelo.any())

    def test_evidencia_incompleta_y_version_ambigua_fallan(self):
        incomplete = self.publications.copy()
        incomplete.loc[0, "evidencia_version"] = ""
        with self.assertRaisesRegex(ValueError, "incompleta"):
            validar_publicaciones(incomplete, self.datasets)
        with self.assertRaisesRegex(ValueError, "ambiguas"):
            validar_publicaciones(pd.concat([self.publications, self.publications.iloc[[0]]]), self.datasets)


if __name__ == "__main__":
    unittest.main()
