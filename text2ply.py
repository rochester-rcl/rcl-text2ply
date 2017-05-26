#!/usr/bin/python
import argparse
import time
import sys
import cProfile
from itertools import islice
from multiprocessing import Queue, Process
from struct import pack


class PLYConvert(object):
    def __init__(self, input_file, output_encoding, output_file, max_vertices):
        self.in_file = open(input_file, 'r')
        self.encoding = output_encoding
        self.extension = input_file.split('.')[1]
        self.header = []
        self.vertices = []
        self.read_queue = Queue()
        self.read_process = Process(target=self.read_ply, args=())
        self.write_process = Process(target=self.write_ply, args=())
        self.vertex_count = 0
        self.max_vertices = max_vertices
        if self.encoding == 'ascii':
            self.ply_file = open(output_file, 'w')
        else:
            self.ply_file = open(output_file, 'wb')

    # INSTANCE METHODS
    ####################################################################################################################
    def get_ply_format(self):
        if self.encoding == 'ascii':
            encoding_format = 'format ascii 1.0\n'
            return encoding_format

        if self.encoding == 'binary':
            byte_order = sys.byteorder  # 'little' or 'big'
            encoding_format = 'format binary_{}_endian 1.0\n'.format(byte_order)
            return encoding_format

    def generate_header(self):
        encoding_format = self.get_ply_format()
        if self.extension == 'pts':
            if read_header is True:
                self.vertex_count = self.in_file.readline().strip()
            else:
                line_count = sum(1 for _ in self.in_file)
                self.vertex_count = line_count - 1
            element_vertex = 'element vertex {}\n'.format(self.vertex_count)
            header = ['ply\n', encoding_format, element_vertex, 'property double x\n', 'property double y\n',
                      'property double z\n', 'property uchar red\n', 'property uchar green\n',
                      'property uchar blue\n', 'end_header\n']
            self.header = header

        elif self.extension == 'xyz':
            self.vertex_count = sum(1 for _ in self.in_file)
            element_vertex = 'element vertex {}\n'.format(self.vertex_count)
            header = ['ply\n', encoding_format, element_vertex, 'property double x\n', 'property double y\n',
                      'property double z\n', 'property uchar red\n', 'property uchar green\n',
                      'property uchar blue\n', 'end_header\n']
        self.header = header

    def read_ply(self):
        self.in_file.seek(0)
        if self.extension == 'pts':
            next(self.in_file)
            while True:
                lines = list(islice(self.in_file, self.max_vertices))
                if not lines:
                    break
                if self.encoding == 'ascii':
                    self.read_queue.put(map(PLYConvert.format_pts_vertex_ascii, lines))
                else:
                    self.read_queue.put(map(PLYConvert.format_pts_vertex_binary, lines))

        elif self.extension == 'xyz':
            while True:
                lines = list(islice(self.in_file, self.max_vertices))
                if not lines:
                    break
                if self.encoding == 'ascii':
                    self.read_queue.put(map(PLYConvert.format_xyz_vertex_ascii, lines))
                else:
                    self.read_queue.put(map(PLYConvert.format_xyz_vertex_binary, lines))

        self.read_queue.put(None)
        self.in_file.close()
        self.in_file = None

    def write_ply(self):
        for line in self.header:
            if self.encoding == 'binary':
                self.ply_file.write(line.encode('ascii'))
            else:
                self.ply_file.write(line)
        while True:
            vertex_list = self.read_queue.get()
            if vertex_list is None:
                break
            self.ply_file.writelines(vertex_list)
        self.ply_file.close()
        self.ply_file = None

    def convert(self):
        self.read_process.start()
        self.write_process.start()
        self.read_process.join()
        self.write_process.join()

    def profile(self):
        cProfile.runctx('self.convert()', globals(), locals())

    # STATIC METHODS
    ####################################################################################################################
    @staticmethod
    def pack_vertex(vertex):
        floats = [float(point) for point in vertex[0:3]]
        ints = [int(rgb) for rgb in vertex[3:6]]
        points = pack('d' * len(floats), *floats)
        rgb = pack('B' * len(ints), *ints)
        return points + rgb

    @staticmethod
    def format_pts_vertex_ascii(line):
        vertex = line.split()
        del vertex[3]
        return ' '.join(vertex) + '\n'

    @staticmethod
    def format_pts_vertex_binary(line):
        vertex = line.split()
        del (vertex[3])
        return PLYConvert.pack_vertex(vertex)

    @staticmethod
    def format_xyz_vertex_ascii(line):
        vertex = PLYConvert.validate_xyz_data(line)
        return ' '.join(vertex) + '\n'

    @staticmethod
    def format_xyz_vertex_binary(line):
        vertex = PLYConvert.validate_xyz_data(line)
        return PLYConvert.pack_vertex(vertex)

    @staticmethod
    def validate_xyz_data(line):
        vertex = line.split()
        if len(vertex) == 8:
            del vertex[0:2]
        return vertex


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

    ply_converter = PLYConvert(file_input, encoding, ply_output, max_vertices)
    print("Generating PLY Header")
    ply_converter.generate_header()
    print("Converting to {} PLY format. This could take a while".format(encoding))
    startTime = time.time()
    if profile:
        ply_converter.profile()
    else:
        ply_converter.convert()
    print("Conversion completed in {} seconds".format((time.time() - startTime)))
