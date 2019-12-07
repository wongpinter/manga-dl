from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
import os
import tqdm


def zipdir(basedir, archive_name):
    files = total_file(basedir)

    pbar = tqdm.tqdm(total=len(files), unit=" images", desc="Creating CBZ file..", position=0, leave=False)
    with closing(ZipFile(archive_name, "w", ZIP_DEFLATED)) as z:
        for abs_file, rel_file in files:
            pbar.update()
            z.write(abs_file, rel_file)

    pbar.close()


def total_file(basedir):
    total_files = []

    for root, dirs, files in os.walk(basedir):
        # NOTE: ignore empty directories
        for fn in files:
            if fn[-4:] != '.zip':
                abs_filename = os.path.join(root, fn)
                rel_filename = abs_filename[len(basedir) + len(os.sep):]
                total_files.append([abs_filename, rel_filename])

    return total_files
