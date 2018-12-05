from django import test
from .models import Titolo


class TitoloModelTest(test.TestCase):
    def test_model_has_area_choices(self):
        self.assertTrue(hasattr(Titolo, 'AREA_CHOICES'),
            msg="Some forms/queries of the app can not work without AREA_CHOICES")


class AreasModuleTest(test.TestCase):
    def test_areas_have_cv_areas_constants(self):
        from . import areas
        self.assertTrue(hasattr(areas, 'TITOLO_STUDIO_CHOICES'))
        self.assertTrue(hasattr(areas, 'PATENTE_CIVILE_CHOICES'))