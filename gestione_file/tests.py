# -*- coding: utf-8 -*-
import os.path
import tempfile

import django.core.files
from django.core.urlresolvers import reverse
from django.test import TestCase

from anagrafica.models import Sede
from base.utils_tests import crea_persona_sede_appartenenza, crea_sede
from curriculum.models import Titolo, TitoloPersonale
from filer.models import Folder
from filer.tests import create_image

from gestione_file.models import Documento, DocumentoSegmento, Immagine


class FilerClipboardAdminUrlsTests(TestCase):
    def setUp(self):

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            User.objects.get(email='admin@admin.it')
        except User.DoesNotExist:
            self.superuser = User.objects.create_superuser(
                'admin@admin.it', 'secret'
            )
        self.client.login(username='admin@admin.it', password='secret')
        self.img = create_image()
        file_obj, self.filename = tempfile.mkstemp('.jpg')
        self.image_name = os.path.basename(self.filename)
        self.img.save(self.filename, 'JPEG')
        file_obj, self.doc_filename = tempfile.mkstemp('.doc')
        self.doc_name = os.path.basename(self.doc_filename)
        with open(self.doc_filename, 'w') as file_obj:
            file_obj.write('text')
        super(FilerClipboardAdminUrlsTests, self).setUp()

    def tearDown(self):
        self.client.logout()
        os.remove(self.filename)
        os.remove(self.doc_filename)
        super(FilerClipboardAdminUrlsTests, self).tearDown()

    def test_filer_upload_documento(self, extra_headers={}):
        """ Test upload documento generico """
        self.assertEqual(Documento.objects.count(), 0)
        folder = Folder.objects.create(name='foo')
        file_obj = django.core.files.File(open(self.doc_filename, 'rb'))
        url = reverse('admin:filer-ajax_upload', kwargs={'folder_id': folder.pk})
        post_data = {
            'Filename': self.doc_name,
            'Filedata': file_obj,
            'jsessionid': self.client.session.session_key
        }
        self.client.post(url, post_data, **extra_headers)
        self.assertEqual(Documento.objects.count(), 1)
        uploaded_file = Documento.objects.all()[0]
        self.assertEqual(uploaded_file.original_filename, self.doc_name)

    def test_filer_upload_documento_url(self, extra_headers={}):
        """ Test creazione documento contenente solo un link """
        self.assertEqual(Documento.objects.count(), 0)
        folder = Folder.objects.create(name='foo')
        url = reverse('admin:gestione_file_documento_add') + '?parent_id={}'.format(folder.pk)
        post_data = {
            'url_documento': 'http://www.example.com',
        }
        self.client.post(url, post_data, **extra_headers)
        self.assertEqual(Documento.objects.count(), 1)
        uploaded_file = Documento.objects.all()[0]
        self.assertEqual(uploaded_file.folder, folder)
        self.assertEqual(uploaded_file.original_filename, 'www.example.com')

    def test_filer_upload_immagine(self, extra_headers={}):
        """ Test caricamento immagine """
        self.assertEqual(Immagine.objects.count(), 0)
        folder = Folder.objects.create(name='foo')
        file_obj = django.core.files.File(open(self.filename, 'rb'))
        url = reverse('admin:filer-ajax_upload', kwargs={'folder_id': folder.pk})
        post_data = {
            'Filename': self.image_name,
            'Filedata': file_obj,
            'jsessionid': self.client.session.session_key
        }
        self.client.post(url, post_data, **extra_headers)
        self.assertEqual(Immagine.objects.count(), 1)
        uploaded_file = Immagine.objects.all()[0]
        self.assertEqual(uploaded_file.original_filename, self.image_name)


class TestSegmenti(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Documenti di test
        cls.file_1 = Documento.objects.create(url_documento='http://www.example.com')
        cls.file_2 = Documento.objects.create(url_documento='http://www.examplee.com')
        cls.titolo_patenteCRI = Titolo.objects.create(tipo='PC', nome='Titolo test')
        cls.titolo_altro = Titolo.objects.create(tipo='PC', nome='Altro titolo')

    def _crea_segmento(self, documento, segmento, sede=None, titolo=None):
        return DocumentoSegmento.objects.create(
            segmento=segmento,
            documento=documento,
            sede=sede,
            titolo=titolo
        )

    def test_filtro_semplice(self):
        segmento_1 = self._crea_segmento(self.file_1, 'A')
        segmento_2 = self._crea_segmento(self.file_2, 'D')
        volontario, _, _ = crea_persona_sede_appartenenza()
        qs = DocumentoSegmento.objects.all()

        documenti = qs.filtra_per_segmenti(volontario)
        self.assertEqual(documenti.count(), 1)
        self.assertEqual(set(documenti), set(DocumentoSegmento.objects.filter(pk=segmento_1.pk)))
        oggetti = documenti.oggetti_collegati()
        self.assertEqual(oggetti.count(), 1)
        self.assertEqual(set(oggetti), set(Documento.objects.filter(pk=self.file_1.pk)))

        segmento_3 = self._crea_segmento(self.file_2, 'B')

        documenti = qs.filtra_per_segmenti(volontario)
        self.assertEqual(documenti.count(), 2)
        self.assertEqual(set(documenti), set(DocumentoSegmento.objects.filter(pk__in=(segmento_1.pk, segmento_3.pk))))
        oggetti = documenti.oggetti_collegati()
        self.assertEqual(oggetti.count(), 2)
        self.assertEqual(set(oggetti), set(Documento.objects.filter(pk__in=(self.file_1.pk, self.file_2.pk))))

    def test_filtro_con_sede(self):
        volontario_con_sede, _, _ = crea_persona_sede_appartenenza()

        sede = volontario_con_sede.sedi_attuali().first()

        altra_sede = crea_sede()

        segmento_0 = self._crea_segmento(self.file_1, 'D')
        segmento_1 = self._crea_segmento(self.file_1, 'B', sede=altra_sede)
        segmento_2 = self._crea_segmento(self.file_2, 'B', sede=sede)

        qs = DocumentoSegmento.objects.all()

        documenti = qs.filtra_per_segmenti(volontario_con_sede)
        self.assertEqual(documenti.count(), 1)
        self.assertEqual(set(documenti), set(DocumentoSegmento.objects.filter(pk=segmento_2.pk)))
        oggetti = documenti.oggetti_collegati()
        self.assertEqual(oggetti.count(), 1)
        self.assertEqual(set(oggetti), set(Documento.objects.filter(pk=self.file_2.pk)))

        segmento_3 = self._crea_segmento(self.file_1, 'B')
        documenti = qs.filtra_per_segmenti(volontario_con_sede)
        self.assertEqual(documenti.count(), 2)
        self.assertEqual(set(documenti), set(DocumentoSegmento.objects.filter(pk__in=(segmento_2.pk, segmento_3.pk))))
        oggetti = documenti.oggetti_collegati()
        self.assertEqual(oggetti.count(), 2)
        self.assertEqual(set(oggetti), set(Documento.objects.filter(pk__in=(self.file_1.pk, self.file_2.pk))))

    def test_filtro_con_titolo(self):
        volontario_con_titolo, _, _ = crea_persona_sede_appartenenza()
        titolo_personale = TitoloPersonale.objects.create(
            titolo=self.titolo_patenteCRI, persona=volontario_con_titolo
        )

        segmento_0 = self._crea_segmento(self.file_1, 'D')
        segmento_1 = self._crea_segmento(self.file_1, 'AA', titolo=self.titolo_altro)
        segmento_2 = self._crea_segmento(self.file_2, 'AA', titolo=self.titolo_patenteCRI)
        qs = DocumentoSegmento.objects.all()

        documenti = qs.filtra_per_segmenti(volontario_con_titolo)
        self.assertEqual(documenti.count(), 1)
        self.assertEqual(set(documenti), set(DocumentoSegmento.objects.filter(pk=segmento_2.pk)))
        oggetti = documenti.oggetti_collegati()
        self.assertEqual(oggetti.count(), 1)
        self.assertEqual(set(oggetti), set(Documento.objects.filter(pk=self.file_2.pk)))
