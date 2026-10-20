"""Validate local references and essential accessibility attributes without dependencies."""
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.anchors = []
        self.files = []
        self.images = 0
        self.headings = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f"Duplicate ID: {a['id']}"
            self.ids.add(a['id'])
        if tag == 'h1':
            self.headings += 1
        if tag == 'img':
            self.images += 1
            assert a.get('alt'), 'Image missing meaningful alt text'
            assert a.get('width') and a.get('height'), 'Image missing dimensions'
        for key in ('src', 'href'):
            value = a.get(key, '')
            if value.startswith('#'):
                self.anchors.append(value[1:])
            elif value and not value.startswith(('https:', 'http:', 'mailto:', 'tel:')):
                self.files.append(value)

page = Page()
source = (ROOT / 'index.html').read_text(encoding='utf-8')
page.feed(source)
assert page.headings == 1, 'Expected exactly one main heading'
assert all(a in page.ids for a in page.anchors), 'Broken internal anchor'
assert all((ROOT / f).is_file() for f in page.files), 'Missing local asset'
assert 'packmyload' not in source.lower(), 'Previous branding remains'
assert '<form' not in source, 'Review form submission behavior'
for section in ('home', 'about', 'services', 'why-us', 'faq', 'contact'):
    assert section in page.ids, f'Missing section {section}'
print(f'PASS: {len(page.anchors)} internal links, {len(set(page.files))} local assets, {page.images} images, all required sections.')
