import unittest
from math_utils import cosine

class TestCosine(unittest.TestCase):
    def test_iguais(self): self.assertAlmostEqual(cosine([1,0],[1,0]),1)
    def test_ortogonais(self): self.assertAlmostEqual(cosine([1,0],[0,1]),0)
    def test_incompativeis(self):
        with self.assertRaises(ValueError): cosine([1],[1,2])
    def test_zero(self):
        with self.assertRaises(ValueError): cosine([0,0],[1,0])

if __name__=="__main__": unittest.main()