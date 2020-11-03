import os
import stat
from typing import Optional

import yaml

from .object import Object
from .output import OutputFile, OutputDataDumper, OD_Raw, OutputDriver
from .yaml import YamlGenerator


class OutputFile_ShellScript(OutputFile):
    """
    An :class:`kubragen.output.OutputFile` that is a shell script.
    It is saved with newlines as LF in all platforms, and is marked as executable.
    """
    def __init__(self, filename: str, is_sequence: bool = False):
        super().__init__(filename, is_sequence)

    def file_newline(self) -> Optional[str]:
        return '\n'

    def file_executable(self) -> bool:
        return True

    def to_string(self, dumper: OutputDataDumper) -> str:
        ret = [
            '#!/bin/bash',
            '',
            super().to_string(dumper),
            ''
        ]
        return '\n'.join(ret)


class OutputFile_Yaml(OutputFile):
    """
    An :class:`kubragen.output.OutputFile` that is generic YAML file.
    No special Kubernetes-specific options will be applied.
    """
    def to_string(self, dumper: OutputDataDumper) -> str:
        yaml_dump_params = {'default_flow_style': False, 'sort_keys': False}
        ret = []
        is_first: bool = True
        for d in self.data:
            if not is_first:
                ret.append('---')
            if isinstance(d, list) and len(d) == 0:
                continue
            is_first = False
            if isinstance(d, dict) or isinstance(d, list) or isinstance(d, Object):
                if isinstance(d, list):
                    ret.append(yaml.dump_all(d, **yaml_dump_params))
                else:
                    ret.append(yaml.dump(d, **yaml_dump_params))
            else:
                ret.append(dumper.dump(d))
        return '\n'.join(ret)


class OutputFile_Kubernetes(OutputFile):
    """
    An :class:`kubragen.output.OutputFile` that is Kubernetes YAML file.
    Special Kubernetes-specific options will be applied.
    """
    def to_string(self, dumper: OutputDataDumper) -> str:
        yd = YamlGenerator(dumper.kg)
        ret = []
        is_first: bool = True
        for d in self.data:
            if isinstance(d, OD_Raw):
                ret.append(dumper.dump(d))
                continue
            if not is_first:
                ret.append('---')
            if isinstance(d, list) and len(d) == 0:
                continue
            is_first = False
            if isinstance(d, dict) or isinstance(d, list) or isinstance(d, Object):
                ret.append(yd.generate(d))
            else:
                ret.append(dumper.dump(d))
        return '\n'.join(ret)


class OutputDriver_Print(OutputDriver):
    """
    An :class:`kubragen.output.OutputDriver` that prints the files to stdout.
    """
    def write_file(self, file: OutputFile, filename, filecontents) -> None:
        print('****** BEGIN FILE: {} ********'.format(filename))
        print(filecontents)
        print('****** END FILE: {} ********'.format(filename))


class OutputDriver_Directory(OutputDriver):
    """
    An :class:`kubragen.output.OutputDriver` that writes files to a directory.

    :param path: the output directory
    """
    path: str

    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            os.makedirs(path)

    def write_file(self, file: OutputFile, filename, filecontents) -> None:
        outfilename = os.path.join(self.path, filename)
        with open(outfilename, 'w', newline=file.file_newline(), encoding=file.file_encoding()) as fl:
            fl.write(filecontents)
        if file.file_executable():
            st = os.stat(outfilename)
            os.chmod(outfilename, st.st_mode | stat.S_IEXEC)
