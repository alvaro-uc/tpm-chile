import unittest

import pandas as pd

from src.processing.estudio_final import alinear


class AlineacionTemporalTest(unittest.TestCase):
    def test_dolar_admite_corte_y_cobre_exige_fecha_anterior(self):
        serie = pd.Series([1.0, 2.0, 3.0], index=pd.to_datetime([
            "2024-10-15", "2024-10-16", "2024-10-17",
        ]))
        corte = pd.Series(pd.to_datetime(["2024-10-16"]))
        self.assertEqual(alinear(serie, corte, dias_max=7).valor.iat[0], 2.0)
        self.assertEqual(alinear(serie, corte, dias_max=7, estricto=True).valor.iat[0], 1.0)

    def test_corte_anterior_a_la_primera_observacion_y_dato_antiguo_quedan_vacios(self):
        serie = pd.Series([1.0], index=pd.to_datetime(["2024-10-01"]))
        corte = pd.Series(pd.to_datetime(["2024-09-30", "2024-10-15"]))
        resultado = alinear(serie, corte, dias_max=7)
        self.assertTrue(pd.isna(resultado.fecha.iat[0]))
        self.assertTrue(resultado.valor.isna().all())

    def test_rezago_mensual_usa_calendario_y_excluye_referencia_intermedia(self):
        serie = pd.Series([1.0, 2.0, 3.0], index=pd.to_datetime([
            "2024-11-01", "2024-12-01", "2025-01-01",
        ]))
        corte = pd.Series(pd.to_datetime(["2025-01-15"]))
        resultado = alinear(serie, corte, dias_max=100, periodo_meses=2)
        self.assertEqual(resultado.fecha.iat[0], pd.Timestamp("2024-11-01"))
        self.assertEqual(resultado.valor.iat[0], 1.0)
