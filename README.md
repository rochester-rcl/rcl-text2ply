## Text to PLY Converter
A Python tool for converting laser scan data stored as ASCII text (.pts, .xyz) to either binary or ASCII [PLY](http://paulbourke.net/dataformats/ply/) files.

#### Dependencies
Python 3
#### Usage

To run via python

`python3 text2ply.py [options]`

Or a pre-compiled binary

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

#### Downloads
