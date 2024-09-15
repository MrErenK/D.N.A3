#!/usr/bin/env python
import bz2
import lzma
import struct
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

import zstandard

from pys import update_metadata_pb2 as um

flatten = lambda l: [item for sublist in l for item in sublist]


def u32(x):
    return struct.unpack(">I", x)[0]


def u64(x):
    return struct.unpack(">Q", x)[0]


class Dumper:
    def __init__(
            self, payloadfile, out, diff=None, old=None, images="", workers=cpu_count(), buffsize=8192
    ):
        self.payloadpath = payloadfile
        payloadfile = self.open_payloadfile()
        self.payloadfile = payloadfile
        self.tls = threading.local()
        self.out = out
        self.diff = diff
        self.old = old
        self.images = images
        self.workers = workers
        self.buffsize = buffsize
        self.validate_magic()

    def open_payloadfile(self):
        return open(self.payloadpath, 'rb')

    def info(self):
        if not hasattr(self, 'dam') or not hasattr(self.dam, 'partitions'):
            raise AttributeError("'Dumper' object has no attribute 'dam' or 'dam.partitions'")
        return {
            "partitions": [part.partition_name for part in self.dam.partitions],
        }

    def run(self, slow=False, extract_partitions=None, outDir=None) -> bool:
        try:
            if self.images == "" and extract_partitions is None:
                partitions = self.dam.partitions
            else:
                partitions = []
                if self.images != "":
                    for image in self.images:
                        found = False
                        for dam_part in self.dam.partitions:
                            if dam_part.partition_name == image:
                                partitions.append(dam_part)
                                found = True
                                break
                        if not found:
                            print(f"Partition {image} not found in image")
                if extract_partitions is not None:
                    for part_name in extract_partitions:
                        found = False
                        for dam_part in self.dam.partitions:
                            if dam_part.partition_name == part_name:
                                partitions.append(dam_part)
                                found = True
                                break
                        if not found:
                            print(f"Partition {part_name} not found in image")

            if len(partitions) == 0:
                print("Not operating on any partitions")
                return False

            if outDir is None:
                outDir = self.out

            partitions_with_ops = []
            for partition in partitions:
                operations = []
                for operation in partition.operations:
                    self.payloadfile.seek(self.data_offset + operation.data_offset)
                    operations.append(
                        {
                            "data_offset": self.payloadfile.tell(),
                            "operation": operation,
                            "data_length": operation.data_length,
                        }
                    )
                partitions_with_ops.append(
                    {
                        "partition": partition,
                        "operations": operations,
                    }
                )
            partition_word = "partition" if len(partitions_with_ops) == 1 else "partitions"
            print(f"Extracting {len(partitions_with_ops)} {partition_word} to {outDir}...")

            if slow:
                for part in partitions_with_ops:
                    print(f"Extracting partition {part['partition'].partition_name}...")
                self.extract_slow(partitions_with_ops, outDir)
            else:
                for part in partitions_with_ops:
                    print(f"Extracting partition {part['partition'].partition_name}...")
                self.multiprocess_partitions(partitions_with_ops, outDir)
            print("Done!")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def extract_slow(self, partitions, outDir):
        for part in partitions:
            self.dump_part(part, outDir)

    def multiprocess_partitions(self, partitions, outDir):
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self.dump_part, part, outDir): part for part in partitions}
            for future in as_completed(futures):
                partition_name = futures[future]['partition'].partition_name
                try:
                    future.result()
                    print(f"{partition_name} Done!")
                except Exception as exc:
                    print(f"{partition_name} - processing generated an exception: {exc}")

    def validate_magic(self):
        magic = self.payloadfile.read(4)
        assert magic == b"CrAU"
        file_format_version = u64(self.payloadfile.read(8))
        assert file_format_version == 2
        manifest_size = u64(self.payloadfile.read(8))
        metadata_signature_size = 0
        if file_format_version > 1:
            metadata_signature_size = u32(self.payloadfile.read(4))
        manifest = self.payloadfile.read(manifest_size)
        self.metadata_signature = self.payloadfile.read(metadata_signature_size)
        self.data_offset = self.payloadfile.tell()
        self.dam = um.DeltaArchiveManifest()
        self.dam.ParseFromString(manifest)
        self.block_size = self.dam.block_size

    def data_for_op(self, operation, out_file, old_file):
        payloadfile = self.tls.payloadfile
        payloadfile.seek(operation["data_offset"])
        buffsize = self.buffsize
        processed_len = 0
        data_length = operation["data_length"]
        op = operation["operation"]

        # assert hashlib.sha256(data).digest() == op.data_sha256_hash, 'operation data hash mismatch'

        if op.type == op.REPLACE_XZ:
            dec = lzma.LZMADecompressor()
            out_file.seek(op.dst_extents[0].start_block * self.block_size)
            while processed_len < data_length:
                data = payloadfile.read(buffsize)
                processed_len += len(data)
                while True:
                    data = dec.decompress(data, max_length=buffsize)
                    out_file.write(data)
                    if dec.needs_input or dec.eof:
                        break
                    data = b''
        elif op.type == op.REPLACE_BZ:
            dec = bz2.BZ2Decompressor()
            out_file.seek(op.dst_extents[0].start_block * self.block_size)
            while processed_len < data_length:
                data = payloadfile.read(buffsize)
                processed_len += len(data)
                while True:
                    data = dec.decompress(data, max_length=buffsize)
                    out_file.write(data)
                    if dec.needs_input or dec.eof:
                        break
                    data = b''
        elif op.type == op.REPLACE:
            out_file.seek(op.dst_extents[0].start_block * self.block_size)
            dec = zstandard.ZstdDecompressor().decompressobj()
            if payloadfile.read(4) == b'\x28\xb5\x2f\xfd':
                payloadfile.seek(payloadfile.tell() - 4)
                while processed_len < data_length:
                    data = payloadfile.read(buffsize)
                    processed_len += len(data)
                    data = dec.decompress(data)
                    out_file.write(data)
                out_file.write(dec.flush())
            else:
                payloadfile.seek(payloadfile.tell() - 4)
                while processed_len < data_length:
                    data = payloadfile.read(buffsize)
                    processed_len += len(data)
                    out_file.write(data)

        elif op.type == op.SOURCE_COPY:
            if not self.diff:
                print("SOURCE_COPY supported only for differential OTA")
                sys.exit(-2)
            out_file.seek(op.dst_extents[0].start_block * self.block_size)
            for ext in op.src_extents:
                old_file.seek(ext.start_block * self.block_size)
                data_length = ext.num_blocks * self.block_size
                while processed_len < data_length:
                    data = old_file.read(buffsize)
                    processed_len += len(data)
                    out_file.write(data)
                processed_len = 0
        elif op.type == op.ZERO:
            for ext in op.dst_extents:
                out_file.seek(ext.start_block * self.block_size)
                data_length = ext.num_blocks * self.block_size
                while processed_len < data_length:
                    data = bytes(min(data_length - processed_len, buffsize))
                    out_file.write(data)
                    processed_len += len(data)
                processed_len = 0
        else:
            print(f"Unsupported type = {op.type:d}")
            sys.exit(-1)
        del data

    def dump_part(self, part, outDir):
        name = part["partition"].partition_name
        out_file_path = f"{outDir}/{name}.img"
        out_file = open(out_file_path, "wb")

        if self.diff:
            old_file_path = f"{self.old}/{name}.img"
            old_file = open(old_file_path, "rb")
        else:
            old_file = None

        with self.open_payloadfile() as payloadfile:
            self.tls.payloadfile = payloadfile
            self.do_ops_for_part(part, out_file, old_file)
        out_file.close()

    def do_ops_for_part(self, part, out_file, old_file):
        for op in part["operations"]:
            self.data_for_op(op, out_file, old_file)