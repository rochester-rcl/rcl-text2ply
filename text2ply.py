#!/usr/bin/python
import time
import argparse
from plyconvert import PLYConvert

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a script to convert a PTS or XYZ file to a PLY")
    parser.add_argument('-i', '--input_file', help="input .pts or .xyz file", required="true",
                        type=str)
    parser.add_argument('-o', '--output_file', help="output ply filename / path", required="true", type=str)
    parser.add_argument('-rh', '--readheader',
                        help="use this option to read the header of the pts file for the vertex count",
                        action='store_true')
    parser.add_argument('-e', '--encoding', help="output PLY as binary or ascii (default = ascii)", default="ascii",
                        type=str)
    parser.add_argument('-mv', '--max_vertices',
                        help="max number of vertices (lines) to read into memory before sending "
                             "\n to the worker queue (default = 5000)",
                        default=5000, type=int)
    parser.add_argument('-p', '--profile', help="enable the profiler (for testing purposes)", action="store_true")

    args = vars(parser.parse_args())

    file_input = args['input_file']
    ply_output = args['output_file']
    encoding = args['encoding']
    max_vertices = args['max_vertices']
    read_header = args['readheader']
    profile = args['profile']

    ply_converter = PLYConvert(file_input, encoding, ply_output, max_vertices, read_header=read_header)
    print("Generating PLY Header")
    ply_converter.generate_header()
    print("Converting to {} PLY format. This could take a while".format(encoding))
    startTime = time.time()
    if profile:
        ply_converter.profile()
    else:
        ply_converter.convert()
    print("Conversion completed in {} seconds".format((time.time() - startTime)))
