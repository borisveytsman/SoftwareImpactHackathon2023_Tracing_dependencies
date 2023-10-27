# SPDX-FileCopyrightText: 2023 Brown, E. M., Nesbitt, A., Hébert-Dufresne, L., Veytsman, B., Pimentel, J. F., Druskat, S., Mietchen, D.
#
# SPDX-License-Identifier: MIT

import sys
import os
import ast
import argparse

from io import StringIO

import pandas as pd
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell

def to_unicode(text):
    """Convert text to unicode"""
    if sys.version_info < (3, 0):
        if isinstance(text, unicode):
            return text
        return str(text).decode("utf-8")
    if isinstance(text, str):
        return text
    return bytes(text).decode("utf-8")


class PathLocalChecker(object):
    """Check if module is local by looking at the directory
    From https://github.com/gems-uff/jupyter-archaeology"""

    def __init__(self, path):
        path = to_unicode(path)
        self.base = os.path.dirname(path)

    def exists(self, path):
        """Check if path exists"""
        return os.path.exists(path)

    def iterate_files(self):
        """Iterate on repository files"""
        for _root, _sub_folder, files in os.walk(self.base):
            for name in files:
                yield name

    def is_local(self, module):
        """Check if module is local by checking if its package exists"""
        if module.startswith("."):
            return True
        path = self.base
        for part in module.split("."):
            path = os.path.join(path, part)
            if not self.exists(path) and not self.exists(path + u".py"):
                return False
        return True

    def local_possibility(self, module):
        """Rate how likely the module is local. Maximum = 4"""
        if self.is_local(module):
            return 4
        module = module.replace(".", "/")
        if not module:
            return 0

        modes = [
            [module, 3, "Full match"],
        ]
        split = module.split("/", 1)
        if len(split) > 1:
            modes.append((split[-1], 2, "all but first 2"))
        split = module.split("/")
        if len(split) > 2:
            modes.append((split[-1], 1, "module name 1"))

        # Check if a folder matchs the module
        for name in self.iterate_files():
            for modname, value, _result in modes:
                if name.endswith(modname):
                    if len(name) <= len(modname):
                        return value
                    if name[-len(modname) - 1] == '/':
                        return value
        return 0


class ModuleExtractor(ast.NodeVisitor):
    """AST visitor that extract imports from AST tree
    Subset of https://github.com/gems-uff/jupyter-archaeology 
    """
    
    def __init__(self):
        self.result = []
    
    def new_module(self, line, import_type, name):
        self.result.append({
            'line': line,
            'import_type': import_type,
            'name': name,
        })
    
    def visit_Call(self, node):
        """get_ipython().<method> calls"""
        func = node.func
        if not isinstance(func, ast.Attribute):
            return self.generic_visit(node)
        value = func.value
        if not isinstance(value, ast.Call):
            return self.generic_visit(node)
        value_func = value.func
        if not isinstance(value_func, ast.Name):
            return self.generic_visit(node)
        if value_func.id != "get_ipython":
            return self.generic_visit(node)
        args = node.args
        if not args:
            return self.generic_visit(node)
        if not isinstance(args[0], ast.Str):
            return self.generic_visit(node)
        if not args[0].s:
            return self.generic_visit(node)
        type_ = func.attr
        split = args[0].s.split()
        name, = split[0:1] or ['']
        if name == "load_ext":
            try:
                module = split[1] if len(split) > 1 else args[1].s
            except IndexError:
                return
            self.new_module(node.lineno, "load_ext", module)
    
    def visit_Import(self, node):
        """Get module from imports"""
        for import_ in node.names:
            self.new_module(node.lineno, "import", import_.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Get module from imports"""
        self.new_module(
            node.lineno, "import_from",
            ("." * (node.level or 0)) + (node.module or "")
        )
        self.generic_visit(node)


def extract_imports(tree):
    extractor = ModuleExtractor()
    extractor.visit(tree)
    return extractor.result


def extract_from_pyfile(path, project_path=None):
    project_path = project_path or os.path.dirname(path)
    local_checker = PathLocalChecker(project_path)
    with open(path, "r") as f:
        result = extract_imports(ast.parse(f.read()))
    for import_def in result:
        import_def['local'] = local_checker.local_possibility(import_def["name"])
        import_def['filename'] = path
        import_def['filetype'] = 'python'
    return result


def extract_from_notebook(path, project_path=None):
    project_path = project_path or os.path.dirname(path)
    local_checker = PathLocalChecker(project_path)

    shell = InteractiveShell.instance()
    result = []
    with open(path) as ofile:
        notebook = nbf.read(ofile, nbf.NO_CONVERT)
        metadata = notebook["metadata"]
        
        kernel = metadata.get("kernelspec", {}).get("name", "no-kernel")
        language_info = metadata.get("language_info", {})
        language = language_info.get("name", "unknown")
        language_version = language_info.get("version", "unknown")
        
        is_python = language == "python"
        is_unknown_version = language_version == "unknown"
        
        cells = notebook["cells"]
        for index, cell in enumerate(cells):
            source = raw_source = cell["source"] = cell.get("source", "") or ""
            if is_python and cell.get("cell_type") == "code":
                try:
                    source = shell.input_transformer_manager.transform_cell(raw_source)
                    cell_result = extract_imports(ast.parse(source))
                    for import_def in cell_result:
                        import_def['local'] = local_checker.local_possibility(import_def["name"])
                        import_def['cell'] = index
                        import_def['filename'] = path
                        import_def['filetype'] = 'notebook'
                    result += cell_result

                except (IndentationError, SyntaxError) as err:
                    print("Error on cell transformation: {}".format(traceback.format_exc()))
                    source = ""
                    status = "load-syntax-error"
                    cell_status.add("syntax-error")
                if "\0" in source:
                    print("Found null byte in source. Replacing it by \\n")
                    source = source.replace("\0", "\n")
    return result

def extract_from_file(fullpath, project_path=None):
    if fullpath.endswith('.ipynb'):
        return extract_from_notebook(fullpath, project_path)
    if fullpath.endswith('.py'):
        return extract_from_pyfile(fullpath, project_path)
    return []


def extract_from_directory(path):
    result = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            fullpath = os.path.join(root, filename)
            if ".ipynb_checkpoints" in filename:
                continue
            partial_result = extract_from_file(fullpath, path)
            result += partial_result
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import extractor')
    parser.add_argument("source")
    parser.add_argument("--csv", help="output result as csv",
                    action="store_true")

    args = parser.parse_args()
    if os.path.isfile(args.source):
        data = extract_from_file(args.source)
    else:
        data = extract_from_directory(args.source)

    if args.csv:
        df = pd.DataFrame.from_records(data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        print(csv_buffer.getvalue())
    else:
        print(data)
