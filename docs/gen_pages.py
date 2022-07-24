"""Generate the code reference pages."""

from pathlib import Path, PosixPath
from typing import Tuple

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()


def keep_file(
    file: PosixPath, exclude: Tuple = ('__main__.py', '__init__.py', 'logger.py')
) -> bool:
    file_string = '/'.join(file.parts)
    for suffix in exclude:
        if file_string.endswith(suffix):
            return False
    return True


def get_files():
    files = sorted(Path('src').rglob('*.py'))
    return list(filter(lambda file: keep_file(file), files))


for path in get_files():
    module_path = path.relative_to('src').with_suffix('')
    doc_path = path.relative_to('src').with_suffix('.md')
    full_doc_path = Path('docs', doc_path)

    parts = list(module_path.parts)

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, 'w') as fd:
        identifier = '.'.join(parts)
        print('::: ' + identifier, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

    with mkdocs_gen_files.open('docs/SUMMARY.md', 'w') as nav_file:
        nav_item = list(nav.build_literate_nav())
        nav_item[0] = nav_item[0].title()
        nav_file.writelines(nav_item)
