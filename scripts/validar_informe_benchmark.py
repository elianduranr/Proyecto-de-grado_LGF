"""Validaciones de métricas y navegación del informe generado (Edge sin interfaz)."""
from pathlib import Path
import tempfile
import unittest

import pandas as pd
from playwright.sync_api import sync_playwright
from generar_informe_benchmark import ROOT, preparar_base, resumir, leer_control_guardado


class Metricas(unittest.TestCase):
    def test_ausencias_ceros_y_desconocidos(self):
        fuente = pd.DataFrame([
            [200, 100, 'coincide'], [50, 100, 'coincide'],
            [20, None, 'solo_estimado'], [None, 30, 'solo_produccion'],
            [0, None, 'solo_estimado'], [None, 999, 'coincide'],
        ], columns=['tallos_estimados', 'tallos_reales', 'estado'])
        fuente = fuente.assign(anio=2026, semana=1, k_finca='F', k_producto='P', k_color='C',
                               k_variedad=[str(i) for i in range(6)])
        base = preparar_base(fuente)
        r = resumir(base).iloc[0]
        self.assertEqual(r.tallos_estimados, 270)
        self.assertEqual(r.tallos_reales, 230)
        self.assertEqual(r.diferencia_tallos, -40)
        self.assertEqual(r.error_absoluto_total, 200)
        self.assertEqual(r.MAE_tallos, 40)
        self.assertAlmostEqual(r.WAPE_pct, 200/230*100)
        self.assertEqual(r.por_revisar, 1)
        self.assertEqual(r.sin_contraparte_con_volumen, 2)
        self.assertEqual(r.sin_contraparte_cero, 1)
        self.assertTrue(pd.isna(base.loc[2, 'tallos_reales_original']))
        self.assertTrue(pd.isna(fuente.loc[2, 'tallos_reales']))

    def test_denominador_cero_y_sin_comparaciones(self):
        fuente = pd.DataFrame([dict(anio=2026, semana=1, k_finca='F', k_producto='P',
                                    k_color='C', k_variedad='V', tallos_estimados=10,
                                    tallos_reales=None, estado='solo_estimado')])
        r = resumir(preparar_base(fuente)).iloc[0]
        self.assertTrue(pd.isna(r.WAPE_pct))
        self.assertEqual(r.error_absoluto_total, 10)
        fuente['estado'] = 'coincide'
        r = resumir(preparar_base(fuente)).iloc[0]
        self.assertTrue(pd.isna(r.tallos_estimados))
        self.assertTrue(pd.isna(r.error_absoluto_total))


class Informe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = preparar_base(pd.read_excel(ROOT/'Notebooks/consolidado_benchmark.xlsx'))
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(channel='msedge', headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
        self.errors = []
        self.page.on('pageerror', lambda err: self.errors.append(str(err)))
        self.page.goto((ROOT/'Notebooks/informes/informe_gerencia_benchmark.html').as_uri())

    def tearDown(self):
        self.page.close()
        self.assertEqual(self.errors, [])

    def assert_metrics(self, expected):
        actual = self.page.evaluate('benchmark.aggregate(benchmark.rows)[0]')
        for key in ['tallos_estimados', 'tallos_reales', 'diferencia_tallos',
                    'error_absoluto_total', 'MAE_tallos', 'WAPE_pct', 'comparaciones']:
            if pd.isna(expected[key]): self.assertIsNone(actual[key], key)
            else: self.assertAlmostEqual(actual[key], expected[key], places=7, msg=key)

    def test_totales_excel_y_todas_las_pestanas(self):
        resumen = resumir(self.base).iloc[0]
        self.assert_metrics(resumen)
        excel = pd.read_excel(ROOT/'Notebooks/informes/informe_gerencia_benchmark.xlsx', sheet_name='Resumen').iloc[0]
        self.assertAlmostEqual(excel.WAPE_pct, resumen.WAPE_pct)
        for tab in ['semanas', 'fincas', 'productos', 'colores', 'variedades', 'detalle', 'metodo', 'resumen']:
            self.page.locator(f'[data-tab="{tab}"]').click()
            self.assertTrue(self.page.locator('#content').inner_text())
            if tab in ['fincas', 'productos', 'colores', 'variedades']:
                self.page.locator('#cross').select_option('cruce')
                self.page.locator('#chart-metric').select_option('WAPE_pct')
                total = self.page.evaluate('benchmark.table.reduce((s,r)=>s+r.error_absoluto_total,0)')
                self.assertEqual(total, resumen.error_absoluto_total)

    def test_filtros_combinados_no_consecutivos(self):
        self.page.locator('#filter-semana summary').click()
        self.page.locator('#filter-semana [data-index="9"]').check()
        self.page.locator('#filter-semana [data-index="19"]').check()
        self.page.locator('[data-close="semana"]').click()
        self.page.locator('#filter-k_finca summary').click()
        self.page.locator('#filter-k_finca label', has_text='GAITANA').locator('input').check()
        self.page.locator('[data-close="k_finca"]').click()
        self.page.locator('#filter-k_producto summary').click()
        self.page.locator('#filter-k_producto [data-find]').fill('MINICARNATION')
        self.assertEqual(self.page.locator('#filter-k_producto .choices-list label:visible').count(), 1)
        self.page.locator('#filter-k_producto label', has_text='MINICARNATION').locator('input').check()
        self.page.locator('[data-close="k_producto"]').click()
        self.page.locator('#filter-k_color summary').click()
        self.page.locator('#filter-k_color label[data-option="WHITE"] input').check()
        self.page.locator('[data-close="k_color"]').click()
        self.page.locator('#include-recovered').uncheck()
        df = self.base.loc[self.base.semana.isin([10,20]) & self.base.k_finca.eq('GAITANA')
                           & self.base.k_producto.eq('MINICARNATION') & self.base.k_color.eq('WHITE')
                           & self.base.estado.ne('unido_variedad')]
        self.assertGreater(len(df), 0)
        self.assert_metrics(resumir(df).iloc[0])
        self.page.locator('#reset').click()
        self.assertEqual(self.page.evaluate('benchmark.rows.length'), len(self.base))

    def test_cobertura_control_y_seleccion_vacia(self):
        self.page.locator('#complete-only').check()
        complete = {(r['anio'],r['semana']) for r in leer_control_guardado(ROOT/'Notebooks/03_benchmark_estimado_ingeniero.ipynb') if r['estado_semana']=='completa'}
        df = self.base.loc[[tuple(x) in complete for x in self.base[['anio','semana']].to_numpy()]]
        self.assert_metrics(resumir(df).iloc[0])
        self.page.locator('#reset').click()
        self.page.locator('#filter-semana summary').click()
        self.page.locator('#week-from').fill('40')
        self.page.locator('#week-to').fill('42')
        self.page.locator('#week-apply').click()
        self.assertEqual(self.page.evaluate('benchmark.rows.length'), 0)
        self.assertIn('No hay registros', self.page.locator('#notices').inner_text())
        self.assertIsNone(self.page.evaluate('benchmark.aggregate(benchmark.rows)[0].WAPE_pct'))

    def test_descarga_paginacion_y_movil(self):
        self.page.locator('[data-tab="detalle"]').click()
        self.page.locator('#next').click()
        self.assertIn('2 de', self.page.locator('#page-info').inner_text())
        self.page.locator('#table-search').fill('PERFECT')
        with self.page.expect_download() as info:
            self.page.locator('#csv').click()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'detalle.csv'
            info.value.save_as(path)
            descargado = pd.read_csv(path, sep=';', decimal=',')
            self.assertGreater(len(descargado), 0)
            self.assertTrue(descargado.k_variedad.str.contains('PERFECT').all())
        self.page.set_viewport_size({'width':390, 'height':844})
        self.page.locator('[data-tab="resumen"]').click()
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 391)


if __name__ == '__main__':
    unittest.main(verbosity=2)
