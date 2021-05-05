import os
import struct

IPC_FIFO_NAME = "ipc_fifo"


def encode_msg_size(size):
    return struct.pack("<I", size)


def decode_msg_size(size_bytes):
    return struct.unpack("<I", size_bytes)[0]


def create_msg(content):
    size = len(content)
    return encode_msg_size(size) + content


def get_message(fifo):
    msg_size_bytes = os.read(fifo, 4)
    msg_size = decode_msg_size(msg_size_bytes)
    msg_content = os.read(fifo, msg_size)
    return msg_content
