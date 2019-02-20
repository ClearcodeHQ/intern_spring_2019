import sys

import requests
from requests import HTTPError, Timeout, TooManyRedirects
from lxml import html


def site_map(url):
    """
    Return a site map of the given site.

    :param str url: root URL of the site
    :rtype: dict
    :returns: dict mapping URL to a dict with title and links keys, title is the <title> element text, links is a set
        of URLs of linked sites from the same domain
    """
    if url.startswith('http://'):
        url = url[len('http://'):]

    sitemap = {}  # values are empty dicts if a page is being crawled
    to_crawl = [url]

    while to_crawl:
        my_url = to_crawl.pop()
        sitemap[my_url] = {}
        try:
            resp = requests.get(my_url if my_url.startswith('http') else 'http://' + my_url)
        except (ConnectionError, HTTPError, Timeout, TooManyRedirects) as e:
            print(f"There was an error: {e}")
            continue
        if resp.status_code >= 400:
            continue  # nonexistent page or error
        tree = html.fromstring(resp.content)
        try:
            title = tree.find('.//title').text
        except AttributeError:
            title = ''
        links = set()
        for link in tree.findall('.//a'):
            href = link.get('href', '')
            if href.startswith('http://'):
                href = href[len('http://'):]
            if href.startswith('/'):
                href = url + href
            if href.startswith(url):
                links.add(href)
                if href in sitemap:
                    # either cycle or already processed
                    continue
                to_crawl.append(href)
            else:
                print('ignore external', repr(href))
        sitemap[my_url] = {'title': title, 'links': links}
    return sitemap


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        print(site_map(arg))
