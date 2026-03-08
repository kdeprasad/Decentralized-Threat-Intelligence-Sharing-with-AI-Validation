"""
Synthetic dataset generator for threat intelligence classification.

Generates a CSV of labelled threat submissions for training the validation
model.  Each row represents a threat indicator with features and a binary
label:
    1 = legitimate threat (valid)
    0 = junk / false positive (invalid)

Usage:
    python -m ml.generate_dataset          # writes ml/dataset.csv
    python -m ml.generate_dataset --rows 5000
"""

import argparse
import csv
import os
import random
import string
from pathlib import Path

# ── Configuration ───────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "dataset.csv"

THREAT_TYPES = [
    "phishing",
    "malware",
    "ransomware",
    "command_and_control",
    "data_exfiltration",
    "denial_of_service",
    "brute_force",
    "other",
]

# TLDs often seen in malicious vs benign domains
MALICIOUS_TLDS = [".xyz", ".tk", ".top", ".buzz", ".ru", ".cn", ".cc"]
BENIGN_TLDS = [".com", ".org", ".net", ".edu", ".gov"]


# ── Helpers ─────────────────────────────────────────────
def _random_ip() -> str:
    return f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def _random_domain(malicious: bool) -> str:
    length = random.randint(4, 20)
    name = "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    tld = random.choice(MALICIOUS_TLDS if malicious else BENIGN_TLDS)
    return name + tld


def _random_hash() -> str:
    """Return a random hex string that looks like an MD5 or SHA-256 hash."""
    length = random.choice([32, 64])  # MD5=32, SHA-256=64
    return "".join(random.choices(string.hexdigits[:16], k=length))


def _random_description(is_valid: bool) -> str:
    valid_descriptions = [
        "Suspicious outbound traffic to known C2 server",
        "Phishing email targeting employees with fake login page",
        "Ransomware dropper detected in email attachment",
        "Brute force SSH attempts from this IP",
        "Domain hosting exploit kit distributing malware",
        "Data exfiltration via DNS tunnelling detected",
        "Malicious macro in Office document",
        "Drive-by download serving banking trojan",
        "Credential harvesting page impersonating corporate SSO",
        "Botnet command-and-control beacon every 60 seconds",
    ]
    invalid_descriptions = [
        "",
        "test",
        "asdf",
        "just checking",
        "hello world",
        "not sure",
        "ignore this",
        "123",
        "n/a",
        "unknown",
    ]
    return random.choice(valid_descriptions if is_valid else invalid_descriptions)


def generate_row(is_valid: bool) -> dict:
    """Generate a single labelled training sample."""
    threat_type = random.choice(THREAT_TYPES)

    if is_valid:
        # Valid threats: tend to have more fields filled, real-looking data
        has_ip = random.random() < 0.7
        has_domain = random.random() < 0.6
        has_hash = random.random() < 0.5
        has_desc = random.random() < 0.9
    else:
        # Junk submissions: fewer fields, often empty or garbage
        has_ip = random.random() < 0.3
        has_domain = random.random() < 0.2
        has_hash = random.random() < 0.15
        has_desc = random.random() < 0.4

    return {
        "ip_address": _random_ip() if has_ip else "",
        "domain": _random_domain(malicious=is_valid) if has_domain else "",
        "malware_hash": _random_hash() if has_hash else "",
        "threat_type": threat_type,
        "description": _random_description(is_valid) if has_desc else "",
        "label": 1 if is_valid else 0,
    }


def generate_dataset(n_rows: int = 2000) -> Path:
    """Write n_rows labelled samples to CSV and return the file path."""
    rows = []
    for _ in range(n_rows):
        is_valid = random.random() < 0.6  # 60 % valid, 40 % junk
        rows.append(generate_row(is_valid))

    random.shuffle(rows)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✔ Generated {n_rows} samples → {OUTPUT_FILE}")
    return OUTPUT_FILE


# ── CLI ─────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic threat dataset")
    parser.add_argument("--rows", type=int, default=2000, help="Number of rows")
    args = parser.parse_args()
    generate_dataset(args.rows)
