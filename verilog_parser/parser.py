import os
from pyverilog.vparser.parser import parse


class VerilogParser:
    def __init__(self, include_paths=None, defines=None):
        self.include_paths = include_paths or []
        self.defines = defines or []

    def parse_files(self, filelist):
        if not filelist:
            raise ValueError("No files provided for parsing.")
        
        for f in filelist:
            if not os.path.exists(f):
                raise FileNotFoundError(f"File not found: {f}")
        
        ast, directives = parse(
            filelist,
            preprocess_include=self.include_paths,
            preprocess_define=self.defines
        )
        return ast, directives


def show_version():
    print("Verilog code parser")
    print("Version: ", pyverilog.__version__)
    print("Usage: python example_parser.py file ...")