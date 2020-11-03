import string
import uuid
from typing import List, Any, Dict, Optional

from .exception import KGException
from .kubragen import KubraGen


class OutputData(str):
    """Base output data class, used to mark some output as special."""
    pass


class OD_Raw(OutputData):
    """Output raw data to file as-is."""
    pass


class OD_FileTemplate(OutputData):
    """Output string replacing files template *"${FILE_fileid}"* with file names."""
    pass


class OutputDataDumper:
    """Base class to data dumper to string."""
    kg: KubraGen

    def __init__(self, kg: KubraGen):
        self.kg = kg

    def dump(self, data) -> str:
        if isinstance(data, str):
            return data
        elif isinstance(data, bytes):
            return data.decode('utf-8')
        else:
            return repr(data)


class OutputDataDumperDefault(OutputDataDumper):
    """Default class to data dumper to string, which support file templates."""
    shfiles: Dict

    def __init__(self, kg: KubraGen, shfiles: Dict):
        super().__init__(kg)
        self.shfiles = shfiles

    def dump(self, data) -> str:
        if isinstance(data, OD_FileTemplate):
            return string.Template(data).substitute(self.shfiles)
        return super().dump(data)


class OutputFile:
    """
    Represents a file to be output.

    :param filename: base file name. Suffixes and/or prefixes can be added as needed
    :param is_sequence: whether the file is part of a sequence, if so it will be output with a numbered prefix
    """
    filename: str
    data: List[Any]
    fileid: str
    is_sequence: bool

    def __init__(self, filename: str, is_sequence: bool = True):
        self.filename = filename
        self.is_sequence = is_sequence
        self.fileid = str(uuid.uuid4()).replace('-', '')
        self.data = []

    def append(self, data: Any) -> None:
        """
        Append data to the file.

        :param data: string or relevant class
        """
        self.data.append(data)

    def output_filename(self, seq: Optional[int] = None) -> str:
        """
        Returns the filename that should be output.

        :param seq: the file sequence, if is_sequence is True
        :return: the filename
        """
        if self.is_sequence:
            if seq is None:
                raise KGException('Sequence is required for sequence files')
            return '{:03d}-{}'.format(seq+1, self.filename)
        else:
            return self.filename

    def file_newline(self) -> Optional[str]:
        """The file newline format, to be passed to the :func:`os.open` function as the "newline" parameter."""
        return None

    def file_encoding(self) -> str:
        """The file encoding, to be passed to the :func:`os.open` function as the "encoding" parameter."""
        return 'utf-8'

    def file_executable(self) -> bool:
        """Whether the file should be marked as executable."""
        return False

    def to_string(self, dumper: OutputDataDumper):
        """
        Output file to string using the dumper.

        :param dumper: dumper to use to output
        """
        ret = []
        for d in self.data:
            ret.append(dumper.dump(d))
        return '\n'.join(ret)


class OutputDriver:
    """Driver interface to output files."""


    def write_file(self, file: OutputFile, filename: str, filecontents: Any) -> None:
        """
        Outputs a file.

        :param file: file to output
        :param filename: output file name
        :param filecontents: file contents
        """
        pass


class OutputProject:
    """
    Outputs a list of files, controlling sequence of files that are sequential.

    :param kubragen: the :class:`kubragen.kubragen.Kubragen` instance
    """

    kg: KubraGen
    out_single: List[OutputFile]
    out_sequence: List[OutputFile]

    def __init__(self, kg: KubraGen):
        self.kg = kg
        self.out_single = []
        self.out_sequence = []

    def append(self, outputfile: OutputFile) -> None:
        """
        Appends a file to the project.

        :param outputfile: file to append
        """
        if outputfile.is_sequence:
            self.out_sequence.append(outputfile)
        else:
            self.out_single.append(outputfile)

    def output(self, driver: OutputDriver) -> None:
        """
        Output all files to the driver.

        :param driver: driver to output to
        """
        shfiles = {}
        for fidx, f in enumerate(self.out_sequence):
            shfiles['FILE_{}'.format(f.fileid)] = f.output_filename(fidx)
        for fidx, f in enumerate(self.out_single):
            shfiles['FILE_{}'.format(f.fileid)] = f.output_filename()

        odd = OutputDataDumperDefault(self.kg, shfiles)

        for fidx, f in enumerate(self.out_sequence):
            driver.write_file(f, f.output_filename(fidx), f.to_string(odd))

        for fidx, f in enumerate(self.out_single):
            driver.write_file(f, f.output_filename(), f.to_string(odd))
