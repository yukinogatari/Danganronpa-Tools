A set of scripts for working with the data in Danganronpa V3 for the PS Vita and PC.

## Dependencies

* Python 2.7 (x86)
    * <http://www.python.org/download/>
* Pillow (for srd texture extraction)
    * <https://python-pillow.org/>

## Scripts

#### drv3_ex_all.py

An all-in-one extractor for a bunch of the data in Danganronpa V3.

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

--------------------------------------------------------------------------------

#### acb_ex.py

This script will extract the game's audio from its ".acb" and ".awb" files.
The code for getting audio filenames out of acb files is a little messy,
so I excluded this step from `drv3_ex_all.py`, meaning you'll have to modify
the paths it works from yourself if you want to use the script.

Theoretically, this should also work with the other DR games (and, likely,
other games that use these Criware formats), but the code as it stands is
hardcoded to use NDRV3-specific paths, so I'm putting it in here.

--------------------------------------------------------------------------------

#### *_ex.py

The extraction scripts can also be run individually to operate on different
file formats, but I couldn't be bothered to write proper command-line interfaces
for them, so you're on your own if you want to use them.

## Acknowledgments

* swizzle.py based on code from [Scarlet](https://github.com/xdanieldzd/Scarlet)
by [xdanieldzd](https://github.com/xdanieldzd)
* query_utf.py based on code from [cpk.bms](http://aluigi.altervista.org/bms/cpk.bms)