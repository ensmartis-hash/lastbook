"""GGUF files already in the local Hugging Face hub cache.

Lastbook can point the local AI at one of these instead of downloading the published Gemma file.
Only files under the hub cache are accepted, and projector sidecars (mmproj) are left out.
"""
import os
from pathlib import Path

MIN_BYTES = 50_000_000


def hub_roots():
    roots = []
    for key in ('HF_HUB_CACHE', 'HUGGINGFACE_HUB_CACHE'):
        if os.environ.get(key):
            roots.append(Path(os.environ[key]))
    if os.environ.get('HF_HOME'):
        roots.append(Path(os.environ['HF_HOME']) / 'hub')
    roots.append(Path.home() / '.cache' / 'huggingface' / 'hub')
    seen, out = set(), []
    for root in roots:
        try:
            root = root.expanduser().resolve()
        except OSError:
            continue
        key = str(root)
        if key not in seen:
            seen.add(key)
            out.append(root)
    return out


def family_of(name):
    n = name.lower()
    if 'gemma' in n:
        return 'gemma'
    return 'chatml'


def _repo(path):
    for part in path.parts:
        if part.startswith('models--'):
            return part[len('models--'):].replace('--', '/')
    return ''


def _skip(name):
    n = name.lower()
    return n.startswith('mmproj') or 'mmproj' in n


def list_gguf(limit=40):
    """One entry per file name and size. Snapshot copies win over loose duplicates."""
    found = {}
    for root in hub_roots():
        if not root.is_dir():
            continue
        for path in root.rglob('*.gguf'):
            if _skip(path.name):
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size < MIN_BYTES:
                continue
            key = (path.name, size)
            current = found.get(key)
            if current and 'snapshots' in str(current['path']) and 'snapshots' not in str(path):
                continue
            repo = _repo(path)
            title = path.name
            if repo:
                title = repo.split('/')[-1] + ' · ' + path.name
            found[key] = {
                'id': path.name,
                'title': title,
                'file': path.name,
                'path': str(path),
                'size': size,
                'repo': repo,
                'family': family_of(path.name + ' ' + repo),
            }
    rows = sorted(found.values(), key=lambda row: row['title'].lower())
    return rows[:limit]


def describe(path):
    """The cache entry for this path, or None when it is not a cached GGUF we listed.

    Hub snapshots are symlinks into ``blobs/``. The blob's own name is a hash, so the
    ``.gguf`` name and the repo id are read from the path the person picked.
    """
    raw = Path(path).expanduser()
    try:
        target = raw.resolve()
    except OSError:
        return None
    if not raw.is_file() or raw.suffix.lower() != '.gguf' or _skip(raw.name):
        return None
    roots = hub_roots()
    if not any(root == target or root in target.parents or root == raw or root in raw.parents for root in roots):
        return None
    try:
        size = target.stat().st_size
    except OSError:
        return None
    if size < MIN_BYTES:
        return None
    repo = _repo(raw)
    return {
        'id': raw.name,
        'title': raw.name,
        'file': raw.name,
        'path': str(raw),
        'size': size,
        'repo': repo,
        'family': family_of(raw.name + ' ' + repo),
    }
