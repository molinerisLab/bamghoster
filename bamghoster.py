#!/usr/bin/env python3

import argparse
import pysam
import os
import tempfile
import shutil
import sys

def rename_reads(input_bam, output_bam, preserve_mtime=False, compresslevel=8):
    if input_bam == "-":
        infile = pysam.AlignmentFile(fileobj=sys.stdin.buffer, mode="rb")
    else:
        infile = pysam.AlignmentFile(input_bam, "rb")

    if output_bam == "-":
        outfile = pysam.AlignmentFile(fileobj=sys.stdout.buffer, mode="wb", header=infile.header, compresslevel=compresslevel)
    else:
        outfile = pysam.AlignmentFile(output_bam, "wb", header=infile.header, compresslevel=compresslevel)

    name_map = {}
    counter = 0

    for read in infile:
        old_name = read.query_name
        if old_name not in name_map:
            name_map[old_name] = str(counter)
            counter += 1
        read.query_name = name_map[old_name]
        read.query_qualities = [0] * read.query_length  # Remove quality (set to zero = ASCII 33 = '!')
        outfile.write(read)

    infile.close()
    outfile.close()

    if preserve_mtime and input_bam != "-" and output_bam != "-":
        stat_info = os.stat(input_bam)
        os.utime(output_bam, (stat_info.st_atime, stat_info.st_mtime))

def report_size_reduction(original_path, reduced_path):
    try:
        orig_size = os.path.getsize(original_path)
        new_size = os.path.getsize(reduced_path)
        reduction = 100.0 * (orig_size - new_size) / orig_size if orig_size > 0 else 0.0
        print(f"Original size: {orig_size} bytes", file=sys.stderr)
        print(f"Reduced size:  {new_size} bytes", file=sys.stderr)
        print(f"Reduction:     {reduction:.2f}%", file=sys.stderr)
    except Exception as e:
        print(f"Error reporting size reduction: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        prog="bamghoster",
        description="bamghoster: Strip BAM files of read names and base quality scores, preserving only the essentials."
    )

    parser.add_argument(
        "input", nargs="?", default="-",
        help="Input BAM file (default: stdin)"
    )
    parser.add_argument(
        "-o", "--output", default="-",
        help="Output BAM file (default: stdout)"
    )
    parser.add_argument(
        "-i", "--inplace", action="store_true",
        help="Modify input file in place"
    )
    parser.add_argument(
        "-t", "--touch", action="store_true",
        help="Set output mtime same as input (for Make/Snakemake)"
    )
    parser.add_argument(
        "-c", "--compress", type=int, default=8,
        help="Compression level for BAM output (0-9, default: 8)"
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Print original and final size with percentage reduction to stderr"
    )

    args = parser.parse_args()

    print("WARNING: bamghoster irreversibly removes base quality scores and replaces read names.", file=sys.stderr)
    print("This is generally safe for RNA-seq workflows that do not rely on quality scores or read identifiers.", file=sys.stderr)
    print("Examples: transcript quantification, gene expression analysis, basic alignment QC.", file=sys.stderr)
    print("Do NOT use for workflows that require read-level identity, deduplication, variant calling, or UMI-based processing.", file=sys.stderr)

    if args.inplace and args.input == "-":
        parser.error("In-place mode requires a regular input file.")

    if args.inplace and args.output != "-":
        parser.error("Cannot use --inplace with --output.")

    if args.inplace:
        with tempfile.NamedTemporaryFile(suffix=".bam", prefix="tmp_rename_", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            rename_reads(args.input, tmp_path, preserve_mtime=args.touch, compresslevel=args.compress)
            if args.report:
                report_size_reduction(args.input, tmp_path)
            shutil.move(tmp_path, args.input)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    else:
        rename_reads(args.input, args.output, preserve_mtime=args.touch, compresslevel=args.compress)
        if args.report and args.input != "-" and args.output != "-":
            report_size_reduction(args.input, args.output)

if __name__ == "__main__":
    main()
