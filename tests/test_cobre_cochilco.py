import unittest

import pandas as pd

from src.processing.cobre_cochilco import build, combine


class CopperFullPeriodTests(unittest.TestCase):
    def test_conflicting_overlap_is_rejected(self):
        a = pd.DataFrame({"fecha": pd.to_datetime(["2013-01-02"]), "cu_usd_lb": [3.0]})
        b = a.assign(cu_usd_lb=3.01)
        with self.assertRaisesRegex(ValueError, "contradictorios"):
            combine([a, b])

    def test_identical_overlap_retains_original_provenance(self):
        a = pd.DataFrame({"fecha": pd.to_datetime(["2013-01-02"]), "cu_usd_lb": [3.0], "archivo_origen": ["primero"]})
        b = a.assign(archivo_origen="segundo")
        result, duplicates = combine([a, b])
        self.assertEqual(duplicates, 1)
        self.assertEqual(result.archivo_origen.tolist(), ["primero"])

    def test_full_period_uses_only_cochilco_and_no_fabricated_dates(self):
        frame, absent, summary = build()
        self.assertEqual(frame.fecha.dt.year.nunique(), 16)
        self.assertEqual(summary["meses_cubiertos"], 192)
        self.assertFalse(frame.fecha.duplicated().any())
        self.assertFalse(frame.cu_usd_lb.isna().any())
        self.assertEqual(frame.fuente.unique().tolist(), ["Cochilco"])
        self.assertFalse(summary["mezcla_con_bcentral"])
        self.assertEqual(len(set(frame.fecha) & set(absent.fecha)), 0)
        self.assertEqual(frame.fecha.max().year, 2025)
        self.assertTrue(frame.archivo_origen.str.startswith("cochilco_").all())


if __name__ == "__main__":
    unittest.main()
