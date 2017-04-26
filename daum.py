import time
import sys

from bs4 import BeautifulSoup
from workflow import Workflow, ICON_WEB, web


logger = None


def opens_word_page(href):
    """Filtering function that checks for a href that points to a word.

    The string "wordid" is "word ID". A hyperlink with this ID can be
    use to open a word page which contains definitions of the word.

    :params href: a candidate of being a link that opens word page.
    :type div: bs4.element.Tag
    :rtype: boolean
    """
    return href and 'wordid' in href


def is_useable_word(css_class):
    """Filtering function that avoids "link_txt" which is not useable in our dictionary form.

    :param css_class: a candidate of being a link that is useable.
    :type css_class: unicode
    :rtype: boolean
    """
    return css_class in ['txt_cleansch', 'txt_searchword']


def parse_definitions(divs):
    """Parsing function that scrapes definitions.

    This function returns a nested list of strings.
    A matching word may have more than one definitions, so the definitions are
    concatenated into a single unicode string before appending it to the list.

    This function returns a nested list because there are more than
    one matching word in a language.

    :param divs: each "div" should contain a specific set of unordered lists.
    :type divs: bs4.element.ResultSet
    :returns: a nested list of concatenated definitions for each matching word.
    :rtype: list
    """
    definitions = []
    for div in divs:
        uls = div.find_all('ul', attrs={'class': 'list_search'})
        definitions.append([u' '.join(ul.stripped_strings) for ul in uls])
    return definitions


def parse_matching_words(divs):
    """Parsing function that grabs all matching words.

    :param divs: each "div" should contain a specific set of hyperlinks.
    :type divs: bs4.element.ResultSet
    :returns: a nest list of matching words for each language.
    :rtype: list
    """
    hyperlinks = [div.find_all(href=opens_word_page, class_=is_useable_word) for div in divs]
    return [[hl.text for hl in hyperlink] for hyperlink in hyperlinks]


def parse_hrefs(divs):
    """Parsing function that grabs all hyperlinks that points to word pages.

    :param divs: each "div" should contain a specific set of hyperlinks.
    :type divs: bs4.element.ResultSet
    :returns: a nest list of matching hyperlinks for each language.
    :rtype: list
    """
    url = u'http://dic.daum.net'
    hyperlinks = [div.find_all(href=opens_word_page, class_=is_useable_word) for div in divs]
    return [[u'{}{}'.format(url, hl.get('href')) for hl in hyperlink] for hyperlink in hyperlinks]


def parse_available_languages(divs):
    """Parsing function that grabs all available languages by name.

    :param divs: each "div" should contain a "<h4>" tag that wraps language text.
    :type divs: bs4.element.ResultSet
    :returns: a list of language name(e.g. ["Korean", "English", "Japanese"].
    :rtype: list
    """
    return [div.find('h4').text for div in divs]


def flatten(l):
    """Recursively flatten the given list.

    :param l: a nested list
    :type l: list
    :returns: a flatten list.
    :rtype: list
    """
    if (type(l) == list and len(l) > 1):
        return l[0] + flatten(l[1:])
    return l[0]


def parse_into_items(html_doc):
    """Parse HTML document into a list of Alfred-viewable items.

    :param html_doc: an HTML document to parse.
    :type html_doc: unicode
    :returns: list of Alfred-viewable items.
    :rtype: list
    """
    soup = BeautifulSoup(html_doc, 'html.parser')
    divs = soup.find_all(attrs={'class': 'card_word'})
    # Parse needed attributes for Alfred items!
    languages = parse_available_languages(divs)
    nested_words = parse_matching_words(divs)
    nested_hrefs= parse_hrefs(divs)
    nested_defs = parse_definitions(divs)
    # Make langs nested with corresponding counts.
    counts = [len(words) for words in nested_words]
    nested_langs = [[lang] * count for lang, count in zip(languages, counts)]
    # Flatten the lists.
    langs = flatten(nested_langs)
    words = flatten(nested_words)
    hrefs = flatten(nested_hrefs)
    defs = flatten(nested_defs)

    # Create items to return.
    items = []
    for lang, href, definition, word in zip(langs, hrefs, defs, words):
        items.append({
            'title': word,
            'subtitle': u'{} | {}'.format(lang, u' '.join(defs)),
            'arg': href
        })
    return items


def main(wf):
    # Get query from Alfred input.
    query = None
    if len(wf.args):
        query = wf.args[0]

    # Grab webpage to parse.
    url = 'http://dic.daum.net/search.do'
    params = dict(q=query)
    resp = web.get(url, params)
    resp.raise_for_status()

    # Process result here.
    items = parse_into_items(resp.text)

    # Generate feedback for Alfred to read off from.
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
