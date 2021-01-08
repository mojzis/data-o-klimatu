import pathlib
import re
import html

import click
import mistune
import frontmatter
from jinja2 import Environment, FileSystemLoader
from slugify import slugify


@click.group()
def main():
    """click"""


def load_mds(path):
    glob = pathlib.Path(path).glob("*.md")
    results = []
    md = mistune.Markdown()
    for item in sorted(glob, reverse=True):
        matter = frontmatter.load(item)
        data = dict(matter)
        data['body'] = md(matter.content)
        data['filename'] = pathlib.Path(item).stem
        results.append(data)

    return results


def load_notebooks(path):
    glob = pathlib.Path(path).glob("*.html")
    results = []
    for item in sorted(glob, reverse=True):
        data = {}
        with open(item, encoding='utf-8') as f:
            body = f.read()
            data['body'] = body
            # this is a bit too fragile ...
            title_match = re.search('<h1 id=\".+\">(?P<title>.+)<a class=\"anchor', body)
            data['title'] = title_match.groupdict().get('title')
            # slugify was confused from html entities
            data['slug'] = slugify(html.unescape(data['title']))
        data['filename'] = pathlib.Path(item).stem
        results.append(data)

    return results


@click.command()
def pub():
    # ntbs = load_mds('notebooks')
    ntbs = load_notebooks('work')
    env = Environment(
        loader=FileSystemLoader('templates'),
    )
    for notebook in ntbs:
        with open(f'public/{notebook["slug"]}.html', 'w', encoding='utf-8') as cp:
            cp.write(env.get_template('ntb.html.j2').render(piece=notebook))
    with open(f'public/index.html', 'w', encoding='utf-8') as index:
        index.write(env.get_template('index.html.j2').render(notebooks=ntbs))


main.add_command(pub)

if __name__ == "__main__":
    main()
