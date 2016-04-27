# -*- coding: utf-8 -*-
import os.path
import tempfile

import django.core.files
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import force_text

from filer.models import Folder, File
from filer.tests import create_image

from gestione_file.models import Documento, Immagine


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
