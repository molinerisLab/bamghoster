# 🧬 bamghoster

**Strip your BAMs to the bone.**  
`bamghoster` is a fast and simple tool to anonymize and slim down BAM files by:

- Replacing read names with integers (preserves pairing)
- Removing all base quality scores (sets them to `'!'`)
- Optionally reporting space savings
- Suitable for streaming (stdin/stdout) and in-place editing

 > ⚠️ **Warning: `bamghoster` is irreversible – the original read names and quality scores are permanently removed!**
---

## 🔍 When to Use (and Not Use)

### ✅ Safe to use in most **RNA-seq** scenarios:
- Transcript quantification (e.g. Salmon, Kallisto, featuresCount)
- Gene expression estimation
- Read count summarization
- Visualization or basic alignment QC

### ❌ Not safe for:
- Variant calling (GATK, DeepVariant, etc.)
- Deduplication (Picard `MarkDuplicates`, etc. simply deduplicate the bam before ghosting it!)
- UMI or barcode-based analyses (simply deduplicate the bam before ghosting it!)
- Any pipeline that needs original read names or quality scores\

---

## 💡 Example Usage

#### Basic file-to-file:
```bash
bamghoster input.bam -o stripped.bam
```

#### In-place processing:
```bash
bamghoster input.bam --inplace
```

#### Streaming with samtools:
```bash
samtools view -b input.bam | bamghoster | samtools view -h > output.sam
```

#### Reporting space savings:
```bash
bamghoster input.bam -o output.bam --report
```

---

## 🛠️ Options

| Option             | Description                                                   |
|--------------------|---------------------------------------------------------------|
| `input`            | Input BAM file (or `-` for stdin)                             |
| `-o`, `--output`   | Output BAM file (or `-` for stdout)                           |
| `-i`, `--inplace`  | Overwrite the input file in-place                             |
| `-t`, `--touch`    | Set output file mtime same as input (for Make/Snakemake)      |
| `-c`, `--compress` | Compression level (0–9, default: `8`)                         |
| `--report`         | Print input/output size and % reduction to stderr             |

---

## 📆 Installation

You need Python 3 and `pysam` installed. You can install it like this:

```bash
pip install pysam
```

Make the script executable:

```bash
chmod +x bamghoster
```

(Optional) Move it to your `$PATH`:

```bash
mv bamghoster /usr/local/bin/
```

---

## 📄 License

AGPL3

---

## 👤 Author

Developed with care by a researcher who got tired of giant BAM files.
Questions? Ideas? PRs welcome!

