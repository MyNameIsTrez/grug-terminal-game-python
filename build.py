# python3 build.py

from distutils.ccompiler import new_compiler

if __name__ == '__main__':
    compiler = new_compiler()

    compiler.compile(['demo.c'])

    compiler.link_executable(['demo.o'], 'demo.so')
