import unittest, tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
import banco
from math_utils import cosine

class TestCosine(unittest.TestCase):
    def test_iguais(self): self.assertAlmostEqual(cosine([1,0],[1,0]),1)
    def test_ortogonais(self): self.assertAlmostEqual(cosine([1,0],[0,1]),0)
    def test_incompativeis(self):
        with self.assertRaises(ValueError): cosine([1],[1,2])
    def test_zero(self):
        with self.assertRaises(ValueError): cosine([0,0],[1,0])

class TestBanco(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.p1=patch.object(banco,"DB_PATH",Path(self.tmp.name)/"t.db"); self.p1.start()
        banco.init_db()
    def tearDown(self): self.p1.stop(); self.tmp.cleanup()
    def test_crud(self):
        banco.save_person("Pessoa",np.array([[1,0],[.9,.1]],np.float32))
        self.assertEqual(len(banco.list_people()),1)
        self.assertEqual(len(banco.embeddings()),1)
        self.assertTrue(banco.delete_person(1))
        self.assertEqual(len(banco.list_people()),0)
    def test_duplicado(self):
        banco.save_person("Ana",[1,0])
        with self.assertRaises(ValueError): banco.save_person("ana",[0,1])
    def test_vazio(self):
        with self.assertRaises(ValueError): banco.save_person(" ",[1,0])

if __name__=="__main__": unittest.main()
