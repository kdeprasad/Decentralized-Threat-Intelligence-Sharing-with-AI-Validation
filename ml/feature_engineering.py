"""
Feature engineering for threat indicator classification.

Extracts numeric features from raw threat submission fields so they can
be consumed by a scikit-learn model.

Features (12 total):
    1.  has_ip            – whether an IP address is present
    2.  has_domain        – whether a domain is present
    3.  has_hash          – whether a malware hash is present
    4.  has_description   – whether a description is present
    5.  filled_count      – number of non-empty fields (0-4)
    6.  description_len   – character length of description
    7.  desc_word_count   – word count in description
    8.  hash_len          – length of malware hash (0, 32, or 64)
    9.  domain_len        – length of domain string
    10. domain_dot_count  – number of dots in domain (subdomain depth)
    11. threat_type_enc   – ordinal-encoded threat type
    12. is_suspicious_tld – 1 if domain ends with a high-risk TLD
"""

import re

import numpy as np
import pandas as pd

THREAT_TYPE_MAP = {
    "phishing": 0,
    "malware": 1,
    "ransomware": 2,
    "command_and_control": 3,
    "data_exfiltration": 4,
    "denial_of_service": 5,
    "brute_force": 6,
    "other": 7,
}

SUSPICIOUS_TLDS = {".xyz", ".tk", ".top", ".buzz", ".ru", ".cn", ".cc", ".pw", ".gq", ".ml"}

FEATURE_NAMES = [
    "has_ip",
    "has_domain",
    "has_hash",
    "has_description",
    "filled_count",
    "description_len",
    "desc_word_count",
    "hash_len",
    "domain_len",
    "domain_dot_count",
    "threat_type_enc",
    "is_suspicious_tld",
]


def extract_features_single(
    ip_address: str | None,
    domain: str | None,
    malware_hash: str | None,
    threat_type: str | None,
    description: str | None,
) -> np.ndarray:
    """
    Extract a 1-D feature vector from a single submission.

    Returns:
        np.ndarray of shape (12,)
    """
    ip = ip_address or ""
    dom = domain or ""
    h = malware_hash or ""
    desc = description or ""
    tt = (threat_type or "other").lower()

    has_ip = int(bool(ip.strip()))
    has_domain = int(bool(dom.strip()))
    has_hash = int(bool(h.strip()))
    has_desc = int(bool(desc.strip()))
    filled_count = has_ip + has_domain + has_hash + has_desc
    description_len = len(desc)
    desc_word_count = len(desc.split()) if desc.strip() else 0
    hash_len = len(h.strip())
    domain_len = len(dom.strip())
    domain_dot_count = dom.count(".")
    threat_type_enc = THREAT_TYPE_MAP.get(tt, 7)
    is_suspicious_tld = int(any(dom.lower().endswith(tld) for tld in SUSPICIOUS_TLDS))

    return np.array([
        has_ip,
        has_domain,
        has_hash,
        has_desc,
        filled_count,
        description_len,
        desc_word_count,
        hash_len,
        domain_len,
        domain_dot_count,
        threat_type_enc,
        is_suspicious_tld,
    ], dtype=np.float64)


def extract_features_df(df: pd.DataFrame) -> np.ndarray:
    """
    Extract features from every row of a DataFrame.

    Expects columns: ip_address, domain, malware_hash, threat_type, description

    Returns:
        np.ndarray of shape (n_rows, 12)
    """
    features = []
    for _, row in df.iterrows():
        features.append(
            extract_features_single(
                ip_address=str(row.get("ip_address", "")),
                domain=str(row.get("domain", "")),
                malware_hash=str(row.get("malware_hash", "")),
                threat_type=str(row.get("threat_type", "other")),
                description=str(row.get("description", "")),
            )
        )
    return np.vstack(features)
