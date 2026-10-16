"""Comprobaciones de fechas y niveles contra casos oficiales revisados."""

import unittest
from unittest.mock import patch

from src.processing.reuniones_tpm import ROOT, construir, fecha_es, leer_fuentes


class ReunionesTPMTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reuniones = construir().set_index("fecha_decision")

    def test_mantenciones_enero_a_mayo_2010_no_desaparecen(self):
        dates = ["2010-01-14", "2010-02-11", "2010-03-18", "2010-04-15", "2010-05-13"]
        sample = self.reuniones.loc[dates]
        self.assertEqual(sample["decision"].tolist(), ["mantiene"]*5)
        self.assertTrue(sample["tpm_posterior_pct"].eq(0.5).all())

    def test_junio_2010_no_confunde_anuncio_con_cambio_diario(self):
        row = self.reuniones.loc["2010-06-15"]
        self.assertEqual(str(row["fecha_corte"].date()), "2010-06-14")
        self.assertEqual(str(row["fecha_observacion_posterior"].date()), "2010-06-16")
        self.assertEqual((row["decision"], row["variacion_pb"]), ("sube", 50.0))

    def test_rango_dos_meses_y_feriado(self):
        self.assertEqual(str(fecha_es("31 de enero y 1 de febrero 2018",2018).date()), "2018-02-01")
        row = self.reuniones.loc["2014-04-17"]
        self.assertEqual(str(row["fecha_observacion_posterior"].date()), "2014-04-21")
        self.assertEqual(row["decision"], "mantiene")

    def test_correccion_documental_y_reunion_extraordinaria(self):
        row = self.reuniones.loc["2023-12-19"]
        self.assertEqual(row["tpm_posterior_pct"],8.25)
        self.assertEqual(row["variacion_pb"],-75.0)
        self.assertNotIn("2023-12-20", self.reuniones.index.strftime("%Y-%m-%d"))
        row = self.reuniones.loc["2020-03-16"]
        self.assertEqual(row["tipo_reunion"], "extraordinaria")
        self.assertEqual(str(row["fecha_corte"].date()), "2020-03-13")
        self.assertEqual(row["decision"], "baja")

    def test_cobertura_sin_reemplazar_reuniones_por_dias(self):
        counts = self.reuniones.groupby(self.reuniones.index.year).size().to_dict()
        self.assertEqual(counts,{y:12 if y<2018 else 9 if y==2020 else 8 for y in range(2010,2026)})
        self.assertEqual(len(self.reuniones),161)

    def test_rechaza_historial_que_omite_una_subida(self):
        fuentes = leer_fuentes(ROOT)
        incompleto = fuentes.loc[fuentes["fecha_decision"].ne("2010-06-15")]
        with patch("src.processing.reuniones_tpm.leer_fuentes", return_value=incompleto):
            with self.assertRaisesRegex(ValueError,"Cambio diario sin correspondencia única"):
                construir()


if __name__ == "__main__":
    unittest.main()
