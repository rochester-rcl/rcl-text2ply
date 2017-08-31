#!/usr/bin/python
import time
import sys
import cProfile
from itertools import islice
from threading import Thread
from queue import Queue
from struct import pack


class PLYConvert(object):
    def __init__(self, input_file, output_encoding, output_file, max_vertices, **kwargs):
        self.in_file = open(input_file, 'r')
        self.encoding = output_encoding
        self.extension = input_file.split('.')[1]
        self.header = []
        self.vertices = []
        self.read_queue = Queue()
        self.read_process = Thread(target=self.read_ply, args=())
        self.write_process = Thread(target=self.write_ply, args=())
        self.vertex_count = 0
        self.max_vertices = max_vertices
        if self.encoding == 'ascii':
            self.ply_file = open(output_file, 'w')
        else:
            self.ply_file = open(output_file, 'wb')

        try:
            self.read_header = kwargs['read_header']
        except KeyError as error:
            self.read_header = False

    # INSTANCE METHODS
    ####################################################################################################################

    def get_vertex_count(self):
        cdef int vcount = 0
        cdef list lines
        while True:
            lines = list(islice(self.in_file, self.max_vertices))
            if not lines:
                break
            else:
                vcount += len(lines)

        return vcount

    def get_ply_format(self):
        cdef str encoding_format
        cdef str byte_order
        cdef str element_vertex
        cdef list header
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
            if self.read_header is True:
                self.vertex_count = self.in_file.readline().strip()
            else:
                line_count = self.get_vertex_count()
                self.vertex_count = line_count - 1
            element_vertex = 'element vertex {}\n'.format(self.vertex_count)
            header = ['ply\n', encoding_format, element_vertex, 'property double x\n', 'property double y\n',
                      'property double z\n', 'property uchar red\n', 'property uchar green\n',
                      'property uchar blue\n', 'end_header\n']

        elif self.extension == 'xyz':
            self.vertex_count = self.get_vertex_count()
            element_vertex = 'element vertex {}\n'.format(self.vertex_count)
            header = ['ply\n', encoding_format, element_vertex, 'property double x\n', 'property double y\n',
                      'property double z\n', 'property uchar red\n', 'property uchar green\n',
                      'property uchar blue\n', 'end_header\n']
        self.header = header

    def read_ply(self):
        cdef list lines
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
    def pack_vertex(list vertex):

        cdef list floats = [float(point) for point in vertex[0:3]]
        cdef list ints = [int(rgb) for rgb in vertex[3:6]]
        points = pack('d' * len(floats), *floats)
        rgb = pack('B' * len(ints), *ints)
        return points + rgb

    @staticmethod
    def format_pts_vertex_ascii(str line):
        cdef list vertex = line.split()
        del vertex[3]
        return ' '.join(vertex) + '\n'

    @staticmethod
    def format_pts_vertex_binary(str line):
        cdef list vertex = line.split()
        del (vertex[3])
        return PLYConvert.pack_vertex(vertex)

    @staticmethod
    def format_xyz_vertex_ascii(str line):
        cdef list vertex = PLYConvert.validate_xyz_data(line)
        return ' '.join(vertex) + '\n'

    @staticmethod
    def format_xyz_vertex_binary(str line):
        cdef list vertex = PLYConvert.validate_xyz_data(line)
        return PLYConvert.pack_vertex(vertex)

    @staticmethod
    def validate_xyz_data(str line):
        cdef list vertex = line.split()
        if len(vertex) == 8:
            del vertex[0:2]
        return vertex

