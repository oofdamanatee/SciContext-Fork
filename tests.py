from django.test import TestCase
from config.models import Contexts


class ContextTestCase(TestCase):
    def setUp(self):
        self.obj1 = Contexts.objects.create(id=998, name="Testy1", filename="hulk")
        self.obj2 = Contexts.objects.create(id=999, name="Testy2", version=0.1, filename="widow")

    def test_ctxs(self):
        ctx1 = Contexts.objects.get(name="Testy1")
        ctx2 = Contexts.objects.get(name="Testy2")
        self.assertEqual(ctx1.getfile(), 'This context has filename hulk')
        self.assertEqual(ctx2.getfile(), 'This context has filename widow')

    def tearDown(self):
        self.obj1.delete()
        self.obj2.delete()
