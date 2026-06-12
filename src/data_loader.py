import json
import gzip

def iter_candidates(filepath):
    """
    Yields candidates one by one from a JSONL file to prevent memory overload.
    Supports .jsonl, .jsonl.gz, and standard .json files.
    """
    is_gzipped = filepath.endswith('.gz')
    open_func = gzip.open if is_gzipped else open
    mode = 'rt' if is_gzipped else 'r'
    
    with open_func(filepath, mode, encoding='utf-8') as f:
        if filepath.endswith('.json'):
            # The sample file is a single pretty-printed JSON array
            data = json.load(f)
            for item in data:
                yield item
        else:
            # The full dataset is JSON Lines
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)
