from django import test
from .models import Titolo, TitleGoal


# class TitoloModelTest(test.TestCase):
#     def test_model_has_area_choices(self):



class AreasModuleTest(test.TestCase):
    def test_areas_have_cv_areas_constants(self):
        from . import areas
        self.assertTrue(hasattr(areas, 'TITOLO_STUDIO_CHOICES'))
        self.assertTrue(hasattr(areas, 'PATENTE_CIVILE_CHOICES'))
        self.assertTrue(hasattr(areas, 'OBBIETTIVI_STRATEGICI'),
                    msg="Some forms/queries of (curriculum, formazione apps) "
                    "can not work without TitleGoal.OBBIETTIVI_STRATEGICI")