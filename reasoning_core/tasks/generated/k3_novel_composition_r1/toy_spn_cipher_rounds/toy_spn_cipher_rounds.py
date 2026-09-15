import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task


def _bin(s):
    return bin(s)[2:].zfill(8)


def _sbox_apply(nibble, sbox):
    return sbox[nibble]


# 4-bit s-boxes. Index by nibble value 0..15.
SBOX_A = [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8,
          0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7]

SBOX_B = [0x1, 0xB, 0x9, 0xC, 0x3, 0x7, 0xD, 0x2,
          0xF, 0x6, 0xA, 0x0, 0x4, 0x5, 0xE, 0x8]


def _round_fn(state, round_key, sbox, perm):
    low = state & 0x0F
    high = (state >> 4) & 0x0F
    nl = _sbox_apply(low, sbox)
    nh = _sbox_apply(high, sbox)
    nib_arr = [nl, nh]
    out_bits = [0] * 8
    for dst, src in enumerate(perm):
        out_bits[dst] = (nib_arr[src // 4] >> (src % 4)) & 1
    permuted = 0
    for b in out_bits:
        permuted = (permuted << 1) | b
    return permuted ^ round_key


@dataclass
class ToySPNConfig(Config):
    rounds: int = 2
    sbox: list = field(default_factory=lambda: list(SBOX_A))

    def apply_difficulty(self, level):
        self.rounds = 2 + level


class ToySPNCipherRounds(Task):
    summary = ("Run a toy substitution-permutation cipher on small blocks: xor the "
               "round key, map nibbles through the given s-box, and permute bit "
               "positions over the stated rounds; answers are the ciphertext.")
    design_choice = ("Ask for the ciphertext after a fixed number of rounds, with the "
                     "plaintext, key schedule, and round count given; difficulty "
                     "arises from correctly applying the s-box and permutation order.")
    config_cls = ToySPNConfig

    def _perm_for(self, key):
        rnd = random.Random(key)
        perm = list(range(8))
        rnd.shuffle(perm)
        return perm

    def _key_schedule(self, rounds, seedv):
        rnd = random.Random(seedv)
        return [rnd.randrange(256) for _ in range(rounds)]

    def generate_entry(self):
        rounds = self.config.rounds
        plaintext = random.randrange(256)
        sbox = list(SBOX_A if random.random() < 0.5 else SBOX_B)
        seedv = random.randrange(2**32)
        rkeys = self._key_schedule(rounds, seedv)
        rnd = random.Random(seedv + 1)
        perm = list(range(8))
        rnd.shuffle(perm)
        sbox_list = sbox

        state = plaintext
        for i in range(rounds):
            state = _round_fn(state, rkeys[i], sbox_list, perm)

        metadata = {
            "plaintext": plaintext,
            "round_keys": rkeys,
            "permutation": perm,
            "sbox": sbox_list,
            "rounds": rounds,
            "ciphertext": state,
        }
        return Entry(metadata=metadata, answer=str(state))

    def render_prompt(self, metadata):
        sbox = metadata["sbox"]
        perm = metadata["permutation"]
        skeyrows = ", ".join(str(k) for k in metadata["round_keys"])
        ptext = metadata["plaintext"]
        rounds = metadata["rounds"]
        return (
            f"We encrypt an 8-bit block with a toy subset-permutation network for "
            f"{rounds} rounds. Each round: XOR the block with the round key, then "
            f"split into high and low 4-bit nibbles, pass each through the s-box, "
            f"reassemble, then permute the 8 bit positions by the permutation.\n"
            f"Plaintext: {ptext}\n"
            f"Round keys (in order): [{skeyrows}]\n"
            f"S-box (index 0..15): {sbox}\n"
            f"Permutation (destination position i receives source bit perm[i]); "
            f"list perm where outbit[i] = inbit[perm[i]]: {perm}\n"
            f"What is the ciphertext after all {rounds} rounds? Answer one integer."
        )


TASK_META = {'parent_source_id': None,
 'idea': 'toy_spn_cipher_rounds (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_novel_composition_r1/toy_spn_cipher_rounds',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
