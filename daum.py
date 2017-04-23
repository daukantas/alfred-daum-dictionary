import sys

from bs4 import BeautifulSoup
from workflow import Workflow, ICON_WEB, web


logger = None


def is_word(href):
    return href and 'wordid' in href


def find_definitions(div):
    uls = div.find_all('ul', attrs={'class': 'list_search'})
    return [u' '.join(ul.stripped_strings) for ul in uls]


def parse_result(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    url = 'http://dic.daum.net'
    divs = soup.find_all(attrs={'class': 'card_word'})
    languages = [div.find('h4').text for div in divs]
    links = [div.find_all(href=is_word) for div in divs]
    words = [[l.text for l in link] for link in links]
    hrefs = [['{}{}'.format(url, l.get('href')) for l in link] for link in links]
    definitions = [find_definitions(div) for div in divs]
    # They are all lenght 3, but each index contains a list.
    items = []
    for lang, href, definition, word in zip(languages, hrefs, definitions, words):
        for h, d, w in zip(href, definition, word):
            items.append(dict(title=w, subtitle=u'{} | {}'.format(lang, d), arg=h))
    return items


def main(wf):
    # Get query from Alfred.
    query = None
    if len(wf.args):
        query = wf.args[0]

    # Grab webpage to parse.
    # url = 'http://dic.daum.net/search.do?q={}'.format(query)
    url = 'http://dic.daum.net/search.do'
    params = dict(q=query)
    resp = web.get(url, params)
    resp.raise_for_status()

    # Process result here.
    items = parse_result(resp.text)

    # Generate feedback.
    for item in items:
        wf.add_item(
                title=item['title'],
                subtitle=item['subtitle'],
                arg=item['arg'],
                valid=True,
                icon=ICON_WEB)

    wf.send_feedback()



if __name__ == '__main__':
    wf = Workflow()
    logger = wf.logger
    sys.exit(wf.run(main))
