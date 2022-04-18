from django.test import TestCase
# import unittest
from .stackGenerator import Stack


class TestStack(TestCase):
    def setUp(self) -> None:
        self.stack = Stack()
        self.stack.push(1)
        self.stack.push(2)
        self.stack.push(3)
        self.stack.push(4)
        self.stack.push(5)

    def test_size(self):
        size = self.stack.size()
        self.assertIs(type(size), int)
        self.assertEqual(size, 5)

    def test_push(self):
        try:
            self.stack.push(6)
        except Exception as e:
            raise e
        self.assertEqual(self.stack.peek(), 6)

    def test_pop(self):
        popped_item = self.stack.pop()
        self.assertEqual(popped_item, 5)
        self.assertEqual(self.stack.size(), 4)
        self.assertIs(type(popped_item), int)





if __name__ == '__main__':
    unittest.main(exit=False)

