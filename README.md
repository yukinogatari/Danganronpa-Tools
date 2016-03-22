Some miscellaneous scripts I wrote for working with data in the Danganronpa PS Vita games.

The code's not meant to be super robust or anything, and there's very little
in the way of actual error handling, so don't expect much.
It *should* do its job, though.

## Dependencies

* Python 2.7 (x86)
    * <http://www.python.org/download/>
* PyQt4 (for `shtx_conv`)
    * <http://www.riverbankcomputing.co.uk/software/pyqt/download>

## Scripts

### shtx_conv.py

Converts SHTX and SHTXFS-formatted image files to PNG.

#### Usage

```
shtx_conv.py [-h] [-o <output dir>]
             <input file|dir> [<input file|dir> ...]
```

You can drag/drop files or directories onto the `shtx_conv.py` file to process them.
If no output directory is provided (such as in a drag/drop), all files are
converted in place.

Directories are traversed recursively to look for files to convert.

### dr_dec.py

Decompresses the compressed data used in the Danganronpa PS Vita games.
(Header: `FC AA 55 A7`)

#### Usage

```
dr_dec.py [-h] [-o <output dir>]                 
          <input file|dir> [<input file|dir> ...]
```

You can drag/drop files or directories onto the `dr_dec.py` file to process them.
If no output directory is provided (such as in a drag/drop), a "dec" directory
is created beside the input, and decompressed data is placed there.

Directories are traversed recursively to look for files to decompress.

## Thanks

* [FireyFly](https://github.com/FireyFly) for helping figure out the compression.
* [Ehm2k](https://twitter.com/Ehm2k) for putting the scripts to good use.