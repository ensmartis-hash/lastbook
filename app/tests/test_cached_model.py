"""A GGUF already in the Hugging Face cache can be selected instead of downloading Gemma."""
import os
import tempfile
import unittest
from pathlib import Path

from engine import hf_cache


class Cache(unittest.TestCase):
    def test_lists_a_gguf_and_skips_mmproj(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / 'models--acme--Qwen-Test' / 'snapshots' / 'abc'
            repo.mkdir(parents=True)
            good = repo / 'Qwen-Test-Q4_K_M.gguf'
            good.write_bytes(b'x' * (hf_cache.MIN_BYTES + 10))
            (repo / 'mmproj-Qwen.gguf').write_bytes(b'y' * (hf_cache.MIN_BYTES + 10))
            old = os.environ.get('HF_HUB_CACHE')
            os.environ['HF_HUB_CACHE'] = str(root)
            try:
                rows = [row for row in hf_cache.list_gguf(limit=200) if row['file'] == 'Qwen-Test-Q4_K_M.gguf']
                described = hf_cache.describe(good)
            finally:
                if old is None:
                    os.environ.pop('HF_HUB_CACHE', None)
                else:
                    os.environ['HF_HUB_CACHE'] = old
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['family'], 'chatml')
        self.assertEqual(rows[0]['repo'], 'acme/Qwen-Test')
        self.assertEqual(described['file'], 'Qwen-Test-Q4_K_M.gguf')
        self.assertIsNone(hf_cache.describe(good))


if __name__ == '__main__':
    unittest.main()
