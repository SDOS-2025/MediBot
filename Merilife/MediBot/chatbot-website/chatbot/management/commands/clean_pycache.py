import os
import shutil
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Recursively delete all __pycache__ directories and .pyc files"

    def add_arguments(self, parser):
        parser.add_argument(
            'path', nargs='?', default='.',
            help="Root path to start cleaning from (default: project root)"
        )

    def handle(self, *args, **options):
        root = options['path']
        removed_dirs = 0
        removed_files = 0

        for dirpath, dirnames, filenames in os.walk(root):
            # remove __pycache__ dirs
            if "__pycache__" in dirnames:
                cache_dir = os.path.join(dirpath, "__pycache__")
                shutil.rmtree(cache_dir)
                self.stdout.write(f"Removed directory: {cache_dir}")
                removed_dirs += 1
                dirnames.remove("__pycache__")

            # remove .pyc files
            for fname in filenames:
                if fname.endswith(".pyc"):
                    file_path = os.path.join(dirpath, fname)
                    os.remove(file_path)
                    self.stdout.write(f"Removed file:      {file_path}")
                    removed_files += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Removed {removed_dirs} __pycache__ dirs and {removed_files} .pyc files."
        ))
