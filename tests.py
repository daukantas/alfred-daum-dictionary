# -*- coding: utf-8 -*-
import unittest

from daum import parse_into_items
from daum import flatten

class ResultTest(unittest.TestCase):

    def empty_doc(self):
        items = parse_into_items(u'')
        self.assertEqual(items, [])

    def test_simple_doc(self):
        html_doc = u'''
            <h1>Hello!</h1>
            <div class="card_word #word #eng">
                <h4 class="tit_word">영어사전</h4>
                <a href="wordid_blah" class="txt_searchword">
                    Test1
                </a>
                <ul class="list_search">
                    <li>meaning1</li>
                    <li>meaning2</li>
                </ul>
                <a href="wordid_blah" class="txt_searchword">
                    Test2
                </a>
                <ul class="list_search">
                    <li>meaning3</li>
                    <li>meaning4</li>
                </ul>
                <a href="wordid_blah" class="txt_searchword">
                    Test3
                </a>
                <ul class="list_search">
                    <li>meaning5</li>
                    <li>meaning6</li>
                </ul>
            </div>
            <h1>Good bye</h1>
        '''
        items = parse_into_items(html_doc)
        self.assertEqual(len(items), 3)


class HelpersTest(unittest.TestCase):

    def test_empty(self):
        test_list = []
        l = flatten(test_list)
        self.assertEqual(l, test_list)

    def test_non_nested(self):
        test_list = [1,2,3]
        l = flatten(test_list)
        self.assertEqual(l, test_list)

    def test_nested(self):
        # test_list = [[range(5)], range(5, 10)]
        test_list = [[1,2],3]
        l = flatten(test_list)
        self.assertEqual(l, [1,2,3])


if __name__ == '__main__':
    unittest.main()
