#!/usr/local/bin/python3
import urllib.request
from bs4 import BeautifulSoup
import re
import sys

ruby_doc_url = 'https://ruby-doc.org/'
core_url = ruby_doc_url + 'core/'
stdlib_url = ruby_doc_url + 'stdlib/'
stdlib_toc_url = stdlib_url + 'toc.html'

def parse_html(url):
    fp = urllib.request.urlopen(url)
    html = fp.read().decode('utf8')
    fp.close()
    return BeautifulSoup(html, 'html.parser')

def extract_keywords(url, methods, classes):
    # Get html doc
    soup = parse_html(url)

    method_links = soup.find('div', { 'id': 'method-index' }).findAll('a')
    for method_link in method_links:
        matches = re.search('^([A-Za-z_]+[!?]?).*', method_link.string)
        if matches:
            keyword = matches.group(1)
            if re.match('^[A-Z]', keyword):
                classes.append(keyword)
            else:
                methods.append(keyword)

    class_links = soup.find('div', { 'id': 'class-index' }).findAll('a')
    for class_link in class_links:
        for name in class_link.string.split('::'):
            if re.match('^[A-Z][A-Za-z]+$', name):
                classes.append(name)

def get_stdlib_urls(toc_url):
    soup = parse_html(toc_url)
    urls = []
    return list(map(lambda a: stdlib_url + a['href'], soup.findAll('a', { 'class': 'mature' })))

def output_keywords(name, keywords):
    print('ruby_' + name + '_keywords = [', end='')
    line_length = 0
    for i in range(len(keywords)):
        if line_length == 0:
            print("\n    ", end='')
            line_length = 4
        print("'" + keywords[i] + "'", end='')
        if i < len(keywords)-1:
            print(',', end='')
            line_length += len(keywords[i]) + 1
            if line_length < 80:
                print(' ', end='')
            else:
                line_length = 0
    print("\n]")

def process_urls(urls, name):
    # Extract keywords from all urls
    methods = []
    classes = []
    for url in urls:
        try:
            print('# Parsed url: ' + url, end='')
            extract_keywords(url, methods, classes)
            print(' -> OK')
        except:
            print(' -> ERROR: ', sys.exc_info()[0])

    # Remove duplicates and sort
    methods = list(set(methods))
    methods.sort()
    classes = list(set(classes))
    classes.sort()

    # Generate formatted output
    keywords = methods + classes
    output_keywords(name, keywords)

process_urls([ core_url ], 'core')
process_urls(get_stdlib_urls(stdlib_toc_url), 'stdlib')
