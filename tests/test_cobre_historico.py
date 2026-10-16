import hashlib
import tempfile
import unittest
from pathlib import Path

from src.processing.cobre_historico import ROOT, build, read_cochilco


class CopperTests(unittest.TestCase):
    def test_locale_units_and_calendar_are_preserved(self):
        # 1.234,56 centavos no son 1,23456 dólares; no inventar fin de semana.
        html = "<table><tr><td>08/01/2010</td><td>1.234,56</td></tr><tr><td>11/01/2010</td><td>338,56</td></tr></table>"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "datos.xls"
            path.write_text(html, encoding="latin1")
            frame = read_cochilco(path)
        self.assertEqual(frame.cu_usd_lb.tolist(), [12.3456, 3.3856])
        self.assertEqual(frame.fecha.dt.strftime("%Y-%m-%d").tolist(), ["2010-01-08", "2010-01-11"])

    def test_duplicate_dates_are_rejected(self):
        html = "<tr><td>04/01/2010</td><td>338,56</td></tr>" * 2
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "datos.xls"
            path.write_text(html, encoding="latin1")
            with self.assertRaises(ValueError):
                read_cochilco(path)

    def test_recovered_interval_and_source_disagreement(self):
        all_data, missing, comparison, summary = build()
        self.assertEqual(len(missing), 696)
        self.assertLess(missing.fecha.max(), comparison.fecha.min())
        self.assertAlmostEqual(all_data.iloc[0].cu_usd_lb, 3.3856)
        self.assertFalse(summary["empalme_automatico"])
        self.assertGreater(summary["diferencia_absoluta_maxima_usd_lb"], 0.2)

    def test_original_bcentral_file_unchanged(self):
        digest = hashlib.sha256((ROOT / "data/raw/cu_usd_lb.xlsx").read_bytes()).hexdigest()
        self.assertEqual(digest, "cc45e40753f506a127c3a4ed4fc992cf74e5654cea06bf3d861a82daa1c297d0")


if __name__ == "__main__":
    unittest.main()
