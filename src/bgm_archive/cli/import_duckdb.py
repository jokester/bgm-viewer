from typing import Iterable
import click
import tqdm
import concurrent.futures as cf
from pathlib import Path
from collections import Counter

from bgm_archive.loader.wiki_archive_loader import WikiArchiveLoader
from bgm_archive.graph import BgmGraph
