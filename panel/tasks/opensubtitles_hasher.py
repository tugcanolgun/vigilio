import struct
import os


def get_hash(file_path) -> str:
    try:
        long_long_format: str = "<q"  # little-endian long long
        byte_size: int = struct.calcsize(long_long_format)

        file_size: int = os.path.getsize(file_path)
        _hash: int = file_size

        if file_size < 65536 * 2:
            raise Exception("SizeError")

        with open(file_path, "rb") as f:
            for x in range(65536 // byte_size):
                buffer = f.read(byte_size)
                (l_value,) = struct.unpack(long_long_format, buffer)
                _hash += l_value
                _hash = _hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

            f.seek(max(0, file_size - 65536), 0)
            for x in range(65536 // byte_size):
                buffer = f.read(byte_size)
                (l_value,) = struct.unpack(long_long_format, buffer)
                _hash += l_value
                _hash = _hash & 0xFFFFFFFFFFFFFFFF

        return "%016x" % _hash

    except IOError:
        raise
    except Exception as exp:
        raise exp
