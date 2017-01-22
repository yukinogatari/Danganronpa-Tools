A set of scripts for working with the data in New Danganronpa V3 for the PS Vita.

## Dependencies

* Python 2.7 (x86)
    * <http://www.python.org/download/>
* Pillow (for srd texture extraction)
    * <https://python-pillow.org/>

## Scripts

#### drv3_ex_all.py

An all-in-one extractor for a bunch of the data in New Danganronpa V3.

#### Usage

```
usage: drv3_ex_all.py [-h] [-o <output dir>] [--no-crop]
                      <input dir> [<input dir> ...]

positional arguments:
  <input dir>           An input directory.

optional arguments:
  -h, --help            show this help message and exit
  -o <output dir>, --output <output dir>
                        The output directory.
  --no-crop             Don't crop srd textures to their display dimensions.
```

You can drag/drop directories onto the `drv3_ex_all.py` file to process them.
If no output directory is provided (such as in a drag/drop), a "dec" directory
is created beside the input, and decompressed data is placed there.

This directory is then searched for ".rsct", ".wrd", ".stx", and ".srd" files
to extract data from, which are placed in a new directory with "-ex" appended
to the name.

## Acknowledgments

* swizzle.py based on code from [Scarlet](https://github.com/xdanieldzd/Scarlet)
by [xdanieldzd](https://github.com/xdanieldzd)