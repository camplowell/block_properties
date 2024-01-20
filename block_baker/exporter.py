import argparse
from pathlib import Path
import re
from typing import List

from evaluation.evaluator import evaluate

arg_parser = argparse.ArgumentParser(
	prog="exporter",
	description="Assemble tags into block.properties files",
	epilog='Nested tags are written as "parent/child" and enum tags are written as "tag:value"'
)


def export(path:str):
	path = Path(path)
