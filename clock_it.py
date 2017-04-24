#!/usr/bin/env python
"""Run Alfred script and time it.
"""
import time

from workflow import web

from daum import parse_into_items


def main():
    # The query "a" has 20 links.
    query = 'a'
    # Grab webpage to parse.
    # url = 'http://dic.daum.net/search.do?q={}'.format(query)
    url = 'http://dic.daum.net/search.do'
    params = dict(q=query)
    resp = web.get(url, params)
    resp.raise_for_status()

    # Clock it.
    start = time.clock()
    items = parse_into_items(resp.text)
    end = time.clock()
    print('Took: {} seconds'.format(end - start))


if __name__ == '__main__':
    main()
