## Text to PLY Converter
A Python tool for converting laser scan data stored as ASCII text (.pts, .xyz) to either binary or ASCII [PLY](http://paulbourke.net/dataformats/ply/) files.

#### Dependencies
Python 3

Pip

Cython
#### Usage

To run via python, first compile the Cython module:

`python setup.py build_ext --inplace`

Then run:

`python3 text2ply.py [options]`

Or use a pre-compiled binary

`./text2ply [options]`

-- options

```
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        input .pts or .xyz file
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        output ply filename / path
  -rh, --readheader     use this option to read the header of the .pts file for
                        the vertex count
  -e ENCODING, --encoding ENCODING
                        output PLY as binary or ascii (default = ascii)
  -p, --profile         enable the profiler (for testing purposes)
```

#### Pre-Compiled Binary Downloads
[Linux 64-bit](https://github.com/rochester-rcl/rcl-text2ply/releases/download/v0.1-alpha/text2ply)
