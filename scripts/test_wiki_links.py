"""Validate links after docs/wiki is exported to its separate GitHub Wiki repo."""
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'https://github.com/sauna-studio/sauna-docs/blob/main/'


def invalid_links(content, wiki_root, repository_root):
    invalid = []
    for target in re.findall(r'\]\(([^)]+)\)', content):
        target = target.split('#', 1)[0]
        if not target:
            continue
        if target.startswith(PREFIX):
            path = repository_root / unquote(target[len(PREFIX):])
            if not path.is_file():
                invalid.append(target)
        elif urlparse(target).scheme:
            continue
        else:
            # The published Wiki has only these pages; sibling repo directories
            # are absent even if the same relative path exists in this checkout.
            if '/' in target or target in {'.', '..'}:
                invalid.append(target)
            elif not (wiki_root / (target if target.endswith('.md') else target + '.md')).is_file():
                invalid.append(target)
    return invalid


class ExportedWikiLinksTests(unittest.TestCase):
    def test_actual_exported_pages(self):
        for page in (ROOT / 'docs/wiki').glob('*.md'):
            with self.subTest(page=page.name):
                self.assertEqual(invalid_links(page.read_text(), ROOT / 'docs/wiki', ROOT), [])

    def test_sibling_adr_path_is_invalid_even_in_source_checkout(self):
        self.assertEqual(invalid_links('[ADR](../adr/0006-local-apple-container.md)', ROOT / 'docs/wiki', ROOT), ['../adr/0006-local-apple-container.md'])

    def test_wiki_pages_and_absolute_repository_adr_survive_export(self):
        content = '[Architecture](Architecture)\n[ADR](' + PREFIX + 'docs/adr/0006-local-apple-container.md)'
        self.assertEqual(invalid_links(content, ROOT / 'docs/wiki', ROOT), [])


if __name__ == '__main__':
    unittest.main()
