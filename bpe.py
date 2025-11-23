import pickle
import regex as re

# -------------------------
# Pre-tokenizer
# -------------------------
HINDI_PATTERN = re.compile(
    r"( ?[\p{Devanagari}\p{M}]+| ?\p{N}+| ?[^\p{Devanagari}\p{M}\p{N}\s]+|\s+)",
    re.UNICODE
)

def pretokenize_hindi(text):
    return re.findall(HINDI_PATTERN, text)


# -------------------------
# Tokenizer Class
# -------------------------
class HindiBPETokenizer:
    def __init__(self, id2sym, sym2id, merges):
        self.id2sym = id2sym
        self.sym2id = sym2id
        self.merges = merges

        # ------ UNK TOKEN ------
        self.unk_token = "<unk>"
        self.unk_id = max(id2sym.keys()) + 1
        self.id2sym[self.unk_id] = self.unk_token
        self.sym2id[self.unk_token] = self.unk_id

        # ------ MERGE STRUCTURES ------
        self.merge_ranks = {(a, b): rank for rank, (a, b, _) in enumerate(merges)}
        self.pair2newid = {(a, b): new_id for (a, b, new_id) in merges}

    # ---------------------------------------
    # APPLY MERGES TO A SEQUENCE OF IDS
    # ---------------------------------------
    def _apply_merges(self, seq):
        while True:
            if len(seq) < 2:
                return seq

            pairs = [(seq[i], seq[i+1]) for i in range(len(seq)-1)]

            ranked = [
                (self.merge_ranks[pair], idx, pair)
                for idx, pair in enumerate(pairs)
                if pair in self.merge_ranks
            ]

            if not ranked:
                return seq

            _, idx, (a, b) = min(ranked)
            new_id = self.pair2newid[(a, b)]

            new_seq = []
            i = 0
            L = len(seq)
            while i < L:
                if i == idx:
                    new_seq.append(new_id)
                    i += 2
                else:
                    new_seq.append(seq[i])
                    i += 1

            seq = new_seq

    # ---------------------------------------
    # ENCODE
    # ---------------------------------------
    def encode(self, text):
        pretoks = pretokenize_hindi(text)
        output = []

        for tok in pretoks:
            # USE THE UNK TOKEN SAFELY
            seq = [self.sym2id.get(ch, self.unk_id) for ch in tok]

            seq = self._apply_merges(seq)
            output.extend(seq)

        return output

    # ---------------------------------------
    # DECODE
    # ---------------------------------------
    def decode(self, ids):
        return "".join(self.id2sym.get(i, "<unk>") for i in ids)

    # ---------------------------------------
    # SAVE
    # ---------------------------------------
    def save(self, path="hindi_tokenizer.pkl"):
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "id2sym": self.id2sym,
                    "sym2id": self.sym2id,
                    "merges": self.merges
                },
                f
            )

    # ---------------------------------------
    # LOAD
    # ---------------------------------------
    @classmethod
    def load(cls, path="hindi_tokenizer.pkl"):
        with open(path, "rb") as f:
            data = pickle.load(f)
        return cls(
            data["id2sym"],
            data["sym2id"],
            data["merges"]
        )


# -------------------------------------------------
# GLOBAL TOKENIZER INSTANCE
# -------------------------------------------------
tok = HindiBPETokenizer.load("hindi_tokenizer.pkl")

def bpe_encode_string(text):
    ids = tok.encode(text)
    toks = [tok.id2sym[i] for i in ids]
    return ids, toks
