# TP Cryptographie
## De la Philosophie Fondamentale à la Maîtrise Pratique
### Niveau Zéro → Expert · 2025-2026

---

> **Références officielles utilisées**
> - NIST SP 800-175B Rev.1 (2020) — Guideline for Using Cryptographic Standards
> - NIST FIPS 197 (2001, reaffirmed 2023) — AES
> - NIST FIPS 186-5 (2023) — Digital Signature Standard
> - NIST SP 800-186 (2023) — Elliptic Curves
> - NIST SP 800-208 (2020) — XMSS / LMS (post-quantique)
> - NIST IR 8413-upd1 (2023) — CRYSTALS-Kyber, CRYSTALS-Dilithium, SPHINCS+
> - RFC 9180 (2022) — Hybrid Public Key Encryption (HPKE)
> - RFC 8446 (2018) — TLS 1.3
> - RFC 9106 (2021) — Argon2
> - ANSSI — Référentiel Général de Sécurité v2.0 (2023)
>
> **Environnement** : Linux, Python 3.11+, OpenSSL 3.x
> **Durée estimée** : 10 à 16 heures
> **Convention** : `$` = terminal · `→` = sortie · `💭` = question de réflexion · `🔬` = exercice

---

## TABLE DES MATIÈRES

```
PARTIE I — PHILOSOPHIE ET FONDEMENTS
  Chapitre 1 : Qu'est-ce que la cryptographie ?
  Chapitre 2 : La théorie de Shannon — sécurité parfaite
  Chapitre 3 : Les primitives cryptographiques

PARTIE II — CRYPTOGRAPHIE SYMÉTRIQUE
  Chapitre 4 : Chiffrement par blocs — AES
  Chapitre 5 : Modes opératoires
  Chapitre 6 : Fonctions de hachage

PARTIE III — CRYPTOGRAPHIE ASYMÉTRIQUE
  Chapitre 7 : Le problème à sens unique — RSA
  Chapitre 8 : Courbes elliptiques — ECDSA / ECDH
  Chapitre 9 : Protocoles d'échange de clés

PARTIE IV — AUTHENTIFICATION ET INTÉGRITÉ
  Chapitre 10 : MAC et HMAC
  Chapitre 11 : Signatures numériques
  Chapitre 12 : PKI et certificats X.509

PARTIE V — CRYPTOGRAPHIE MODERNE (2024-2026)
  Chapitre 13 : Post-quantique — CRYSTALS et SPHINCS+
  Chapitre 14 : Chiffrement authentifié — AEAD
  Chapitre 15 : Protocoles modernes — TLS 1.3, HPKE

PARTIE VI — APPLICATIONS ET ATELIERS
  Chapitre 16 : Implémentation pratique en Python
  Chapitre 17 : Attaques classiques et contre-mesures
  Chapitre 18 : Challenge final
```

---

# ════════════════════════════════════════════════════════
# PARTIE I — PHILOSOPHIE ET FONDEMENTS
# ════════════════════════════════════════════════════════

---

## Chapitre 1 : Qu'est-ce que la Cryptographie ?

### 1.1 Définition profonde

La cryptographie n'est pas une technique — c'est une **philosophie de la confiance dans un monde hostile**. Elle répond à une question fondamentale :

> *Comment deux entités peuvent-elles communiquer de manière sécurisée sur un canal que l'adversaire contrôle entièrement ?*

```
Le modèle de Dolev-Yao (1983) — hypothèse fondamentale :

  Alice ──→ [MESSAGE] ──→ Bob
               ↕
            Ève (adversaire)
            - lit tous les messages
            - peut les modifier
            - peut en injecter de nouveaux
            - contrôle le réseau entier

La cryptographie résout ce problème en rendant
l'information inutilisable SANS la clé.
```

### 1.2 Les cinq propriétés de sécurité

```
┌─────────────────────┬──────────────────────────────────────────────┐
│  Propriété          │  Définition                                  │
├─────────────────────┼──────────────────────────────────────────────┤
│  Confidentialité    │  Seuls les destinataires légitimes lisent    │
│  (Secrecy)          │  le message                                  │
├─────────────────────┼──────────────────────────────────────────────┤
│  Intégrité          │  Le message n'a pas été altéré               │
│  (Integrity)        │  en transit                                  │
├─────────────────────┼──────────────────────────────────────────────┤
│  Authenticité       │  L'expéditeur est bien celui qu'il prétend   │
│  (Authenticity)     │  être                                        │
├─────────────────────┼──────────────────────────────────────────────┤
│  Non-répudiation    │  L'expéditeur ne peut pas nier avoir envoyé  │
│  (Non-repudiation)  │  le message                                  │
├─────────────────────┼──────────────────────────────────────────────┤
│  Disponibilité      │  Le service reste accessible (DoS)           │
│  (Availability)     │  — moins directement cryptographique         │
└─────────────────────┴──────────────────────────────────────────────┘
```

### 1.3 Principe de Kerckhoffs (1883)

> *"La sécurité d'un système cryptographique ne doit reposer que sur le secret de la clé, et non sur le secret de l'algorithme."*

Ce principe, formulé par Auguste Kerckhoffs dans "La cryptographie militaire", est **toujours la règle d'or en 2026**. Il signifie :

- L'algorithme peut être public (et doit l'être pour être audité)
- Seule la clé doit rester secrète
- Un algorithme "secret" = fausse sécurité par obscurité

💭 **Réflexion** : Pourquoi un algorithme secret est-il moins sûr qu'un algorithme public ? Pensez au nombre d'experts qui peuvent auditer un algorithme ouvert vs. fermé.

### 1.4 La sécurité computationnelle vs. parfaite

```
SÉCURITÉ PARFAITE (Shannon, 1949) :
  → L'adversaire, même avec une puissance infinie, ne peut
    pas obtenir d'information sur le message.
  → Seul le One-Time Pad (OTP) y parvient.
  → Problème pratique : la clé doit être aussi longue que le message.

SÉCURITÉ COMPUTATIONNELLE (Goldwasser, Micali, 1982) :
  → L'adversaire ne peut pas casser le système en temps polynomial
    avec une probabilité non négligeable.
  → C'est le fondement de toute la cryptographie moderne.
  → Repose sur des problèmes mathématiques supposés difficiles.

Formellement :
  Un schéma est (t, ε)-sûr si tout adversaire de complexité t
  réussit avec probabilité au plus ε.
  En pratique : t > 2^128 opérations, ε < 2^-64
```

---

## Chapitre 2 : La Théorie de Shannon

### 2.1 Claude Shannon — père de la cryptographie moderne

En 1949, Claude Shannon publie *"Communication Theory of Secrecy Systems"*, qui établit les fondements mathématiques de la cryptographie. Ses deux concepts clés :

### 2.2 Confusion et diffusion

```
CONFUSION :
  Rendre la relation entre la clé et le texte chiffré
  aussi complexe que possible.
  → Chaque bit du chiffré dépend de plusieurs bits de la clé.
  → Implémenté par : substitutions (S-boxes)

DIFFUSION :
  Propager l'influence de chaque bit du texte clair
  sur de nombreux bits du texte chiffré.
  → Modifier 1 bit en entrée → ~50% des bits changent en sortie.
  → Implémenté par : permutations, rotations, XOR

Exemple visuel (AES) :
  Avalanche effect :
  Entrée 1 : "Hello World!!!!!!"  → Chiffré : A1B2C3D4...
  Entrée 2 : "Hello World!!!!!?" → Chiffré : F7E2A1C9...
                                              ↑↑↑↑↑↑↑↑
                              Totalement différent pour 1 bit changé
```

### 2.3 Entropie et information

```
L'entropie de Shannon mesure l'incertitude d'une variable aléatoire.

H(X) = -∑ P(xi) × log₂(P(xi))

Pour une clé de 128 bits uniformément distribuée :
  H(K) = 128 bits  →  2^128 clés possibles ≈ 3.4 × 10^38

L'entropie d'un mot de passe :
  "password"  : ~6 bits (trop prévisible)
  "P@ssw0rd!" : ~28 bits (règles de substitution connues)
  "xK9#mP2$vQ": ~66 bits (aléatoire, bon)
  Phrase de 6 mots BIP39 : ~77 bits (meilleur rapport mémorabilité/entropie)
```

### 2.4 Le One-Time Pad — seul chiffrement parfait

```python
# otp_demo.py — Démonstration du One-Time Pad

def otp_encrypt(message: bytes, key: bytes) -> bytes:
    """
    Chiffrement OTP : XOR bit à bit message ⊕ clé.
    RÈGLES ABSOLUES :
      1. La clé doit être AUSSI LONGUE que le message
      2. La clé doit être VRAIMENT ALÉATOIRE (pas pseudo-aléatoire)
      3. La clé ne doit être utilisée QU'UNE SEULE FOIS
    Violer une de ces règles détruit la sécurité parfaite.
    """
    if len(key) < len(message):
        raise ValueError("La clé doit être au moins aussi longue que le message")
    return bytes(m ^ k for m, k in zip(message, key))

otp_decrypt = otp_encrypt  # XOR est sa propre inverse

# Démonstration
import os

message = b"SECRET MESSAGE"
key = os.urandom(len(message))  # clé vraiment aléatoire

ciphertext = otp_encrypt(message, key)
recovered = otp_decrypt(ciphertext, key)

print(f"Message   : {message}")
print(f"Clé       : {key.hex()}")
print(f"Chiffré   : {ciphertext.hex()}")
print(f"Déchiffré : {recovered}")

# Preuve de sécurité parfaite : deux textes clairs possibles
# pour le même chiffré avec des clés différentes
message2 = b"AUTRE MESSAGE!"
# Il existe une clé key2 telle que otp_encrypt(message2, key2) = ciphertext
key2 = bytes(c ^ m for c, m in zip(ciphertext, message2))
print(f"\nMême chiffré, message différent :")
print(f"Avec clé2 : {otp_decrypt(ciphertext, key2)}")
# → L'adversaire ne peut distinguer les deux cas !
```

💭 **Réflexion** : Si l'OTP est parfaitement sûr, pourquoi ne l'utilise-t-on pas pour tout ? Quel est le problème pratique fondamental ?

### 🔬 Exercice 2.1 — Analyser l'entropie

```python
# Calculer l'entropie de différentes sources d'aléa
import math
from collections import Counter

def entropy_bits(data: bytes) -> float:
    """Calcule l'entropie de Shannon en bits par byte."""
    if not data:
        return 0
    counts = Counter(data)
    total = len(data)
    return -sum(
        (c/total) * math.log2(c/total)
        for c in counts.values()
    )

# Tester différentes sources
tests = {
    "Texte anglais":  b"the quick brown fox jumps over the lazy dog",
    "Données répétées": b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "Aléa vrai":      os.urandom(100),
    "Mot de passe":   b"Password123!Password123!Password123!",
}

print(f"{'Source':<20} {'Entropie':>10} {'Qualité':>15}")
print("-" * 50)
for name, data in tests.items():
    e = entropy_bits(data)
    quality = "🔴 Faible" if e < 4 else "🟡 Moyen" if e < 6 else "🟢 Bon"
    print(f"{name:<20} {e:>8.2f}/8   {quality:>15}")

# Questions :
# 1. Pourquoi l'aléa vrai a-t-il une entropie proche de 8 bits/byte ?
# 2. Qu'est-ce qu'une entropie de 8 bits/byte signifie exactement ?
# 3. Pourquoi le texte anglais a-t-il une entropie faible ?
```

---

## Chapitre 3 : Les Primitives Cryptographiques

### 3.1 La hiérarchie des primitives

```
┌─────────────────────────────────────────────────────────────────┐
│              PYRAMIDE DES PRIMITIVES                             │
│                                                                  │
│                    ┌───────────────┐                            │
│  PROTOCOLES        │  TLS, SSH,    │  ← Assemblage de          │
│                    │  PGP, Signal  │    primitives              │
│                    └───────┬───────┘                            │
│                    ┌───────▼───────┐                            │
│  SCHÉMAS           │  AES-GCM,    │  ← Combinaisons            │
│                    │  RSA-OAEP,   │    standardisées           │
│                    │  ECDSA       │                             │
│                    └───────┬───────┘                            │
│                    ┌───────▼───────┐                            │
│  PRIMITIVES        │  AES, SHA,   │  ← Briques de base         │
│                    │  RSA, ECC    │                             │
│                    └───────┬───────┘                            │
│                    ┌───────▼───────┐                            │
│  MATHÉMATIQUES     │  XOR, Modexp │  ← Opérations              │
│                    │  Mult. ECC   │    fondamentales           │
│                    └───────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Taxonomie des algorithmes

```
CRYPTOGRAPHIE SYMÉTRIQUE
  Même clé pour chiffrer et déchiffrer.
  ├── Chiffrement par blocs
  │   ├── AES-128/192/256 (FIPS 197, recommandé)
  │   ├── ChaCha20 (RFC 8439, recommandé pour logiciel)
  │   └── 3DES (obsolète, ne plus utiliser)
  ├── Modes opératoires
  │   ├── GCM (Galois/Counter Mode) — recommandé
  │   ├── CBC (Cipher Block Chaining) — avec précautions
  │   ├── CTR (Counter Mode)
  │   └── ECB (Electronic Codebook) — JAMAIS en production
  └── Fonctions de hachage
      ├── SHA-3 (FIPS 202, 2015) — famille Keccak
      ├── SHA-256/512 (FIPS 180-4) — encore sûres
      ├── BLAKE3 (2020) — le plus rapide, non-FIPS
      └── MD5/SHA-1 — cryptographiquement cassées

CRYPTOGRAPHIE ASYMÉTRIQUE
  Clé publique (chiffrement) ≠ Clé privée (déchiffrement).
  ├── Basée sur la factorisation
  │   └── RSA (FIPS 186-5) — minimum 3072 bits en 2026
  ├── Basée sur les courbes elliptiques
  │   ├── ECDSA (signatures)
  │   ├── ECDH (échange de clés)
  │   └── Ed25519 (RFC 8032) — recommandé 2026
  └── Post-quantique (NIST 2024)
      ├── ML-KEM (CRYSTALS-Kyber) — FIPS 203
      ├── ML-DSA (CRYSTALS-Dilithium) — FIPS 204
      └── SLH-DSA (SPHINCS+) — FIPS 205
```

---

# ════════════════════════════════════════════════════════
# PARTIE II — CRYPTOGRAPHIE SYMÉTRIQUE
# ════════════════════════════════════════════════════════

---

## Chapitre 4 : AES — Advanced Encryption Standard

### 4.1 Histoire et philosophie

En 1997, le NIST lance un concours mondial pour remplacer DES. Parmi 15 candidats, **Rijndael** (Joan Daemen et Vincent Rijmen, Belgique) est sélectionné en 2001 et devient AES (FIPS 197). Ce processus ouvert et compétitif est le modèle de la standardisation cryptographique moderne.

AES opère sur des **blocs de 128 bits** avec des clés de **128, 192 ou 256 bits**.

### 4.2 Structure interne de l'AES

```
AES-128 : 10 rounds
AES-192 : 12 rounds
AES-256 : 14 rounds

Chaque round (sauf le dernier) :
  1. SubBytes   → Substitution non-linéaire via S-box (confusion)
  2. ShiftRows  → Décalage cyclique des lignes (diffusion)
  3. MixColumns → Multiplication matricielle (diffusion)
  4. AddRoundKey → XOR avec la sous-clé du round (confusion)

État interne = matrice 4×4 bytes (16 bytes = 128 bits)

┌──┬──┬──┬──┐   SubBytes   ┌──┬──┬──┬──┐
│a0│a4│a8│ac│  ──────────→ │s0│s4│s8│sc│
│a1│a5│a9│ad│              │s1│s5│s9│sd│
│a2│a6│aa│ae│              │s2│s6│sa│se│
│a3│a7│ab│af│              │s3│s7│sb│sf│
└──┴──┴──┴──┘              └──┴──┴──┴──┘
                ShiftRows
┌──┬──┬──┬──┐              ┌──┬──┬──┬──┐
│s0│s4│s8│sc│  ──────────→ │s0│s4│s8│sc│  ← ligne 0 : pas de décalage
│s1│s5│s9│sd│              │s5│s9│sd│s1│  ← ligne 1 : décalage 1
│s2│s6│sa│se│              │sa│se│s2│s6│  ← ligne 2 : décalage 2
│s3│s7│sb│sf│              │sf│s3│s7│sb│  ← ligne 3 : décalage 3
└──┴──┴──┴──┘              └──┴──┴──┴──┘
```

### 4.3 Implémentation pratique avec Python

```python
#!/usr/bin/env python3
"""
aes_workshop.py — Atelier AES complet
Utilise: cryptography>=41.0.0 (pip install cryptography)
Référence: NIST FIPS 197 + SP 800-38D (GCM)
"""

import os
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.backends import default_backend


# ═══════════════════════════════════════════
# SECTION 1 : AES-GCM — LE MODE RECOMMANDÉ
# ═══════════════════════════════════════════

def aes_gcm_encrypt(plaintext: bytes, key: bytes,
                    associated_data: bytes = b"") -> dict:
    """
    Chiffrement AES-GCM (Galois/Counter Mode).

    GCM fournit simultanément :
    - Confidentialité (chiffrement CTR)
    - Intégrité + Authenticité (tag GHASH de 128 bits)
    → C'est un schéma AEAD (Authenticated Encryption with Associated Data)

    associated_data : données authentifiées mais NON chiffrées
                     (ex: headers, métadonnées)

    SÉCURITÉ CRITIQUE :
    - Nonce (IV) de 96 bits DOIT être unique par (clé, message)
    - Réutiliser un nonce avec la même clé = catastrophe complète
      (l'adversaire peut récupérer la clé et falsifier les messages)
    """
    if len(key) not in (16, 24, 32):
        raise ValueError("Clé AES : 16, 24 ou 32 bytes (128, 192 ou 256 bits)")

    # Générer un nonce aléatoire de 96 bits (12 bytes)
    # JAMAIS réutiliser ce nonce avec la même clé
    nonce = os.urandom(12)

    aesgcm = AESGCM(key)
    # encrypt() retourne ciphertext + tag (16 bytes à la fin)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, associated_data)

    return {
        "nonce": nonce,
        "ciphertext": ciphertext_with_tag[:-16],
        "tag": ciphertext_with_tag[-16:],
        "associated_data": associated_data,
        # Ce qu'on stocke/transmet : nonce + ciphertext_with_tag
        "to_transmit": nonce + ciphertext_with_tag,
    }


def aes_gcm_decrypt(nonce: bytes, ciphertext_with_tag: bytes,
                    key: bytes, associated_data: bytes = b"") -> bytes:
    """
    Déchiffrement AES-GCM avec vérification d'authenticité.
    Lève InvalidTag si les données ont été altérées.
    """
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext_with_tag, associated_data)


# ═══════════════════════════════════════════
# SECTION 2 : DÉMONSTRATION AES-GCM
# ═══════════════════════════════════════════

def demo_aes_gcm():
    print("=" * 60)
    print("  DÉMO AES-256-GCM")
    print("=" * 60)

    # Génération de clé sécurisée
    key = os.urandom(32)  # AES-256
    plaintext = b"Message confidentiel — 2026"
    aad = b"version=1,user=alice,timestamp=1704873600"

    print(f"\n[CHIFFREMENT]")
    print(f"  Message    : {plaintext.decode()}")
    print(f"  Clé (hex)  : {key.hex()}")
    print(f"  AAD        : {aad.decode()}")

    result = aes_gcm_encrypt(plaintext, key, aad)

    print(f"\n  Nonce      : {result['nonce'].hex()}")
    print(f"  Chiffré    : {result['ciphertext'].hex()}")
    print(f"  Tag Auth   : {result['tag'].hex()}")

    print(f"\n[DÉCHIFFREMENT]")
    blob = result["to_transmit"]
    nonce = blob[:12]
    ct_tag = blob[12:]
    recovered = aes_gcm_decrypt(nonce, ct_tag, key, aad)
    print(f"  Récupéré   : {recovered.decode()}")

    print(f"\n[VÉRIFICATION D'INTÉGRITÉ]")
    # Modifier un byte du chiffré
    tampered = bytearray(ct_tag)
    tampered[0] ^= 0x01  # flip 1 bit
    from cryptography.exceptions import InvalidTag
    try:
        aes_gcm_decrypt(nonce, bytes(tampered), key, aad)
        print("  ❌ BUG : altération non détectée !")
    except InvalidTag:
        print("  ✅ Altération détectée → InvalidTag levée")

    # Modifier l'AAD
    try:
        aes_gcm_decrypt(nonce, ct_tag, key, b"version=2,user=bob")
        print("  ❌ BUG : falsification AAD non détectée !")
    except InvalidTag:
        print("  ✅ Falsification AAD détectée → InvalidTag levée")


# ═══════════════════════════════════════════
# SECTION 3 : CHACHA20-POLY1305
# ═══════════════════════════════════════════

def demo_chacha20():
    """
    ChaCha20-Poly1305 (RFC 8439) — Alternative à AES-GCM
    Avantages vs AES-GCM :
    - Plus rapide en LOGICIEL sur CPU sans AES-NI
    - Pas d'attaque par timing (implémentation constante)
    - Utilisé par TLS 1.3, WireGuard, Signal Protocol
    """
    print("\n" + "=" * 60)
    print("  DÉMO ChaCha20-Poly1305")
    print("=" * 60)

    key = os.urandom(32)  # 256 bits obligatoire
    nonce = os.urandom(12)  # 96 bits
    plaintext = b"Message chiffré avec ChaCha20"

    chacha = ChaCha20Poly1305(key)
    ciphertext = chacha.encrypt(nonce, plaintext, None)
    decrypted = chacha.decrypt(nonce, ciphertext, None)

    print(f"  Original   : {plaintext.decode()}")
    print(f"  Chiffré    : {ciphertext.hex()}")
    print(f"  Déchiffré  : {decrypted.decode()}")
    print(f"  Overhead   : {len(ciphertext) - len(plaintext)} bytes (tag Poly1305)")


if __name__ == "__main__":
    demo_aes_gcm()
    demo_chacha20()
```

### 4.4 Le piège du mode ECB

```python
# demo_ecb_vulnerability.py
# Démonstration PÉDAGOGIQUE de la vulnérabilité ECB
# NE JAMAIS utiliser ECB en production

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from PIL import Image  # pip install Pillow
import os

def encrypt_ecb(data: bytes, key: bytes) -> bytes:
    """ECB : chaque bloc est chiffré INDÉPENDAMMENT."""
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    enc = cipher.encryptor()
    # Padding manuel (pour la démo)
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len] * pad_len)
    return enc.update(data) + enc.finalize()

# PROBLÈME ECB :
# Les blocs identiques produisent des chiffrés identiques.
# Sur une image avec des zones uniformes (logo, fond blanc),
# la structure visuelle reste perceptible dans le chiffré.
#
# Essayez :
# 1. Prendre une image BMP simple (logo Linux Tux par exemple)
# 2. Chiffrer les pixels en ECB
# 3. Observer que la forme du logo est toujours visible !
#
# Cela démontre que ECB ne cache pas les patterns structurels.

# Démonstration textuelle
key = os.urandom(16)
messages = [
    b"BLOC_IDENTIQUE!!",
    b"BLOC_IDENTIQUE!!",
    b"BLOC_DIFFERENT!X",
    b"BLOC_IDENTIQUE!!",
]

print("Message         → ECB (modes.ECB)")
for msg in messages:
    ct = encrypt_ecb(msg, key)
    print(f"  {msg} → {ct[:16].hex()}")

# Sortie attendue :
# BLOC_IDENTIQUE!! → a1b2c3d4e5f6...  ← même hash
# BLOC_IDENTIQUE!! → a1b2c3d4e5f6...  ← IDENTIQUE ! révèle la répétition
# BLOC_DIFFERENT!X → f9e8d7c6b5a4...  ← différent
# BLOC_IDENTIQUE!! → a1b2c3d4e5f6...  ← IDENTIQUE encore !
```

💭 **Réflexion** : Imaginez chiffrer une base de données de votes avec ECB. Même sans connaître la clé, que pourrait déduire un adversaire sur les résultats ?

---

## Chapitre 5 : Modes Opératoires

### 5.1 Vue d'ensemble

```
┌──────────┬─────────────────────────────────────────────────────┐
│  Mode    │  Caractéristiques                                   │
├──────────┼─────────────────────────────────────────────────────┤
│  ECB     │ Pas d'IV. Blocs indépendants. ❌ NE PAS UTILISER   │
│  CBC     │ IV requis. Propagation d'erreurs. Padding requis.   │
│          │ Vulnérable à BEAST, POODLE si mal implémenté.       │
│  CFB/OFB │ Transforme bloc en chiffrement flux. IV requis.     │
│  CTR     │ Parallélisable. Transforme en flux. Nonce requis.   │
│  GCM     │ CTR + authentification GHASH. ✅ RECOMMANDÉ        │
│  CCM     │ CTR + CBC-MAC. Limité à 2^23 bytes par nonce.       │
│  XTS     │ Pour disques (NIST SP 800-38E).                     │
└──────────┴─────────────────────────────────────────────────────┘
```

### 5.2 CBC — Comprendre en profondeur

```
CBC (Cipher Block Chaining) :

Chiffrement :
  IV ──┐
       XOR ← P₁ → E(K) → C₁
  C₁ ──┐
       XOR ← P₂ → E(K) → C₂
  C₂ ──┐
       XOR ← P₃ → E(K) → C₃

Déchiffrement :
  IV ──┐
  C₁ → D(K) → XOR → P₁
  C₁ ──┐
  C₂ → D(K) → XOR → P₂

IMPLICATIONS :
1. Si un bit de C₁ est altéré :
   - P₁ est ENTIÈREMENT corrompu (16 bytes)
   - Un bit précis de P₂ est corrompu (le même bit)
   → Propagation partielle d'erreur (utile pour détection)

2. Le chiffrement est SÉQUENTIEL (ne peut pas être parallélisé)
3. Le déchiffrement PEUT être parallélisé

PADDING ORACLE ATTACK (Vaudenay, 2002) :
   Si le serveur retourne des erreurs différentes pour "padding invalide"
   vs "MAC invalide", l'adversaire peut déchiffrer n'importe quel message
   en ~O(16 × 256) = 4096 requêtes par bloc.
   → Solution : MAC-then-Encrypt → Encrypt-then-MAC (TLS 1.3 supprime CBC)
```

### 🔬 Exercice 5.1 — Implémenter et tester CBC

```python
#!/usr/bin/env python3
# exercice_cbc.py

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os

def aes_cbc_encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    """
    Chiffrement AES-CBC avec PKCS#7 padding.
    Retourne (iv, ciphertext).
    """
    iv = os.urandom(16)

    # Padding PKCS#7 : remplit le dernier bloc jusqu'à 16 bytes
    # Si la longueur est un multiple de 16, ajoute un bloc complet de 16 bytes
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    enc = cipher.encryptor()
    ciphertext = enc.update(padded) + enc.finalize()

    return iv, ciphertext

def aes_cbc_decrypt(iv: bytes, ciphertext: bytes, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    dec = cipher.decryptor()
    padded = dec.update(ciphertext) + dec.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()

# Tests
key = os.urandom(16)  # AES-128

# Test 1 : message normal
msg = b"Bonjour, cryptographie!"
iv, ct = aes_cbc_encrypt(msg, key)
recovered = aes_cbc_decrypt(iv, ct, key)
assert recovered == msg, "Déchiffrement CBC incorrect"
print(f"✅ Test 1 OK : '{recovered.decode()}'")

# Test 2 : propagation d'erreur
ct_tampered = bytearray(ct)
ct_tampered[0] ^= 0xFF  # corrompre le premier bloc
recovered_tampered = aes_cbc_decrypt(iv, bytes(ct_tampered), key)
print(f"\nTest propagation d'erreur :")
print(f"  Original  : {msg!r}")
print(f"  Corrompu  : {recovered_tampered!r}")
print(f"  → Bloc 1 entièrement corrompu : {recovered_tampered[:16]!r}")
print(f"  → Bloc 2 partiellement corrompu")

# QUESTION :
# Pourquoi corrompre CT[0] corrompt tout le bloc 1 mais seulement
# 1 bit précis du bloc 2 ? Expliquer en utilisant le schéma CBC.
```

---

## Chapitre 6 : Fonctions de Hachage

### 6.1 Propriétés fondamentales

```
Une fonction de hachage cryptographique H : {0,1}* → {0,1}^n
doit satisfaire :

1. RÉSISTANCE AUX PRÉIMAGES (one-way) :
   Étant donné h, impossible de trouver m tel que H(m) = h
   Coût : O(2^n)

2. RÉSISTANCE AUX SECONDES PRÉIMAGES :
   Étant donné m, impossible de trouver m' ≠ m tel que H(m') = H(m)
   Coût : O(2^n)

3. RÉSISTANCE AUX COLLISIONS :
   Impossible de trouver (m, m') tels que H(m) = H(m')
   Coût : O(2^(n/2)) par l'attaque des anniversaires !

PARADOXE DES ANNIVERSAIRES :
  Dans un groupe de 23 personnes, probabilité > 50% que 2 aient
  le même anniversaire (365 jours possibles).
  → Pour SHA-256 (256 bits) : sécurité collision = 128 bits
    (il faut 2^128 essais, pas 2^256)

LONGUEURS RECOMMANDÉES (NIST 2026) :
  SHA-256  : 128 bits de sécurité → ✅ Acceptable
  SHA-384  : 192 bits de sécurité → ✅ Recommandé
  SHA-512  : 256 bits de sécurité → ✅ Recommandé
  SHA3-256 : 128 bits de sécurité → ✅ Recommandé
  SHA-1    : CASSÉ (collision 2017) → ❌ Interdit
  MD5      : CASSÉ (1996) → ❌ Interdit pour sécurité
```

### 6.2 SHA-3 — Construction Keccak

```
SHA-3 utilise une construction "éponge" (sponge function),
radicalement différente de SHA-2 (Merkle-Damgård).

CONSTRUCTION ÉPONGE :
  ┌──────────────────────────────────┐
  │  État interne : 1600 bits        │
  │  (b = r + c : rate + capacity)   │
  └──────────────────────────────────┘

Phase d'absorption :
  Message ──┐
            XOR ──→ État ──→ Permutation Keccak-f[1600]
  (par blocs de r bits)

Phase d'extraction :
  ← Output (r bits) ← État ← Permutation

Avantages vs SHA-2 :
  - Résistant aux attaques par extension de longueur
    (SHA-256 vulnérable à length extension)
  - Construction plus simple à analyser
  - Modes XOF (extendable output) : SHAKE128, SHAKE256
```

### 6.3 Hachage de mots de passe — cas particulier crucial

```python
#!/usr/bin/env python3
"""
password_hashing.py
RÈGLE D'OR : Ne JAMAIS utiliser SHA-256 directement pour hacher des MDP !
Utiliser : Argon2id (RFC 9106), scrypt, bcrypt
"""

import hashlib
import os
import time

# ─── MAUVAISE PRATIQUE : SHA-256 seul ───────────────────────────────
def hash_password_bad(password: str) -> str:
    """❌ NE PAS FAIRE : trop rapide, pas de sel"""
    return hashlib.sha256(password.encode()).hexdigest()

# Problème : un GPU moderne calcule ~10^10 SHA-256/seconde
# → "password123" cassé en microsecondes avec rainbow tables

# ─── BONNE PRATIQUE : Argon2id ──────────────────────────────────────
# pip install argon2-cffi
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

def demo_argon2():
    """
    Argon2id (RFC 9106, 2021) — Champion du Password Hashing Competition
    
    Paramètres recommandés OWASP 2024 :
      m = 19456 KB (19 MB)  → mémoire requise
      t = 2               → nombre d'itérations
      p = 1               → parallélisme
    Ces paramètres rendent chaque hash ~0.5s sur hardware moderne.
    Sur GPU : pas d'accélération possible (memory-hard).
    """
    ph = PasswordHasher(
        time_cost=2,       # itérations
        memory_cost=65536, # 64 MB (agressif pour la démo, 19 MB en prod)
        parallelism=1,
        hash_len=32,
        salt_len=16,
    )

    password = "MonMotDePasse2026!"

    print("[Argon2id] Génération du hash...")
    start = time.time()
    hashed = ph.hash(password)
    elapsed = time.time() - start

    print(f"  Hash      : {hashed}")
    print(f"  Temps     : {elapsed:.3f}s")
    print(f"  Format    : $argon2id$v=19$m=65536,t=2,p=1$<sel>$<hash>")

    # Vérification
    assert ph.verify(hashed, password)
    print(f"  Vérif OK  : ✅")

    # Mauvais mot de passe
    try:
        ph.verify(hashed, "mauvais_mdp")
    except VerifyMismatchError:
        print(f"  Mauvais MDP détecté : ✅")

    # Comparaison des vitesses
    print(f"\n[Comparaison vitesses]")
    pwd = "test123"

    t0 = time.time()
    for _ in range(1000):
        hashlib.sha256(pwd.encode()).hexdigest()
    sha_time = (time.time() - t0) / 1000

    t0 = time.time()
    ph_fast = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    ph_fast.hash(pwd)
    argon_time = time.time() - t0

    print(f"  SHA-256   : {sha_time*1e6:.2f} µs  →  {1/sha_time:.0e} hashes/s")
    print(f"  Argon2id  : {argon_time*1000:.1f} ms  →  {1/argon_time:.1f} hashes/s")
    print(f"  Argon2 est {argon_time/sha_time:.0e}× plus lent → 10^x fois plus dur à casser")

demo_argon2()
```

### 🔬 Exercice 6.1 — L'attaque des anniversaires

```python
#!/usr/bin/env python3
# birthday_attack.py

import hashlib
import random
import string
import time

def truncated_hash(message: str, bits: int = 16) -> int:
    """Hash SHA-256 tronqué à 'bits' bits (pour simuler une collision plus facile)."""
    h = hashlib.sha256(message.encode()).digest()
    full = int.from_bytes(h, 'big')
    return full >> (256 - bits)

def find_collision_brute(bits: int = 16):
    """
    Trouve une collision dans un hash à 'bits' bits.
    Paradoxe des anniversaires : ~2^(bits/2) essais suffisent.
    """
    seen = {}
    attempts = 0
    expected = 2 ** (bits / 2)

    print(f"Recherche de collision sur hash à {bits} bits")
    print(f"Espace : {2**bits} valeurs possibles")
    print(f"Tentatives théoriques : ~{expected:.0f}")

    start = time.time()

    while True:
        msg = ''.join(random.choices(string.ascii_lowercase, k=10))
        h = truncated_hash(msg, bits)
        attempts += 1

        if h in seen and seen[h] != msg:
            elapsed = time.time() - start
            print(f"\n✅ Collision trouvée après {attempts} tentatives ({elapsed:.3f}s) !")
            print(f"  Message 1 : '{seen[h]}' → hash = {h:#06x}")
            print(f"  Message 2 : '{msg}' → hash = {h:#06x}")
            print(f"  Ratio réel/théorique : {attempts/expected:.2f}")
            return

        seen[h] = msg

# Tester avec différentes tailles
for bits in [16, 24, 32]:
    find_collision_brute(bits)
    print()

# QUESTION :
# Si SHA-256 a 256 bits, combien d'opérations faut-il pour trouver
# une collision ? Comparez avec l'âge de l'univers en secondes (~4×10^17).
# Pourquoi dit-on que SHA-256 offre 128 bits de sécurité contre les collisions ?
```

---

# ════════════════════════════════════════════════════════
# PARTIE III — CRYPTOGRAPHIE ASYMÉTRIQUE
# ════════════════════════════════════════════════════════

---

## Chapitre 7 : RSA — Le Problème de la Factorisation

### 7.1 Philosophie mathématique

RSA (Rivest, Shamir, Adleman, 1977) repose sur un **problème mathématique supposé difficile** : la **factorisation d'un grand nombre en ses facteurs premiers**.

```
PROBLÈME FACILE :
  Multiplier deux grands nombres premiers :
  p = 61 × q = 53  →  n = 3233
  Opération en O(log²n) — microsecondes même pour n de 2048 bits.

PROBLÈME DIFFICILE :
  Retrouver p et q depuis n = 3233
  Pour n de 2048 bits : meilleur algorithme (NFS) = O(e^(64/9 × (ln n)^(1/3) × (ln ln n)^(2/3)))
  En pratique : milliards d'années avec les ordinateurs classiques.

IMPORTANT (2026) :
  - RSA-1024 : CASSÉ (insuffisant depuis ~2010)
  - RSA-2048 : Sécurité jusqu'en ~2030 selon NIST
  - RSA-3072 : Recommandé pour sécurité post-2030
  - RSA-4096 : Forte sécurité (mais lent)
  → NIST SP 800-131A Rev.2 : RSA-2048 = 112 bits sécurité
```

### 7.2 Algorithme RSA — pas à pas

```
GÉNÉRATION DES CLÉS :

1. Choisir p et q : deux grands premiers distincts
   Exemple pédagogique (JAMAIS en production !) :
   p = 61, q = 53

2. Calculer n = p × q  (le module)
   n = 61 × 53 = 3233

3. Calculer φ(n) = (p-1)(q-1)  (indicatrice d'Euler)
   φ(n) = 60 × 52 = 3120

4. Choisir e tel que : 1 < e < φ(n) et gcd(e, φ(n)) = 1
   e = 17  (65537 = 2^16+1 en pratique, premiers de Fermat)

5. Calculer d = e⁻¹ mod φ(n)  (inverse modulaire)
   d × e ≡ 1 (mod 3120)
   d = 2753  (car 17 × 2753 = 46801 = 15 × 3120 + 1)

Clé publique  : (e=17, n=3233)
Clé privée    : (d=2753, n=3233)
DÉTRUIRE      : p, q, φ(n) après génération

CHIFFREMENT :
  c = m^e mod n
  c = 65^17 mod 3233 = 2790

DÉCHIFFREMENT :
  m = c^d mod n
  m = 2790^2753 mod 3233 = 65  ✓

POURQUOI ÇA MARCHE ? (Théorème d'Euler) :
  m^(φ(n)) ≡ 1 (mod n)  pour tout m premier avec n
  m^(e×d) = m^(1 + k×φ(n)) = m × (m^φ(n))^k ≡ m (mod n)
```

### 7.3 RSA en Python — pratique correcte

```python
#!/usr/bin/env python3
"""
rsa_workshop.py — RSA complet et sécurisé
Référence : NIST FIPS 186-5, RFC 8017 (PKCS#1 v2.2)
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import os


# ═══════════════════════════════════════════
# GÉNÉRATION DE CLÉS
# ═══════════════════════════════════════════

def generate_rsa_key(bits: int = 2048) -> tuple:
    """
    Génère une paire de clés RSA.
    bits = 2048 (acceptable), 3072 (recommandé 2026), 4096 (fort)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,   # e = 65537 = 2^16 + 1 (standard)
        key_size=bits,
        backend=default_backend()
    )
    return private_key, private_key.public_key()


# ═══════════════════════════════════════════
# CHIFFREMENT RSA-OAEP
# ═══════════════════════════════════════════

def rsa_encrypt(message: bytes, public_key) -> bytes:
    """
    Chiffrement RSA avec OAEP padding (PKCS#1 v2.2, RFC 8017).

    OAEP (Optimal Asymmetric Encryption Padding) :
    - Ajoute de l'aléa avant le chiffrement (chaque appel → résultat différent)
    - Résistant aux attaques Chosen-Ciphertext (CCA2-sécurisé)
    - Utiliser MGF1-SHA256 comme recommandé

    ❌ NE PAS utiliser PKCS#1 v1.5 padding (vulnérable à Bleichenbacher 1998)

    Limite : RSA-2048 avec OAEP-SHA256 peut chiffrer max ~190 bytes.
    Pour chiffrer de gros fichiers : RSA chiffre une clé AES symétrique
    (schéma hybride).
    """
    return public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def rsa_decrypt(ciphertext: bytes, private_key) -> bytes:
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


# ═══════════════════════════════════════════
# CHIFFREMENT HYBRIDE RSA + AES
# ═══════════════════════════════════════════

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def hybrid_encrypt(message: bytes, public_key) -> dict:
    """
    Chiffrement hybride : RSA enveloppe une clé AES éphémère.
    
    Schéma :
    1. Générer une clé AES-256 aléatoire (clé de session)
    2. Chiffrer le message avec AES-256-GCM
    3. Chiffrer la clé AES avec RSA-OAEP
    4. Transmettre : RSA(clé_AES) + AES(message)
    
    C'est le fondement de PGP, S/MIME, TLS key exchange.
    """
    # Clé AES éphémère (jamais réutilisée)
    session_key = os.urandom(32)
    nonce = os.urandom(12)

    # Chiffrer le message
    aesgcm = AESGCM(session_key)
    encrypted_message = aesgcm.encrypt(nonce, message, None)

    # Chiffrer la clé de session avec RSA
    encrypted_key = rsa_encrypt(session_key, public_key)

    return {
        "encrypted_key": encrypted_key,
        "nonce": nonce,
        "ciphertext": encrypted_message,
    }


def hybrid_decrypt(bundle: dict, private_key) -> bytes:
    # Déchiffrer la clé de session
    session_key = rsa_decrypt(bundle["encrypted_key"], private_key)
    # Déchiffrer le message
    aesgcm = AESGCM(session_key)
    return aesgcm.decrypt(bundle["nonce"], bundle["ciphertext"], None)


# ═══════════════════════════════════════════
# SÉRIALISATION DES CLÉS
# ═══════════════════════════════════════════

def save_private_key(private_key, filepath: str, password: bytes = None):
    """Sauvegarder la clé privée (chiffrée avec le mot de passe si fourni)."""
    enc = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc
    )
    with open(filepath, 'wb') as f:
        f.write(pem)
    print(f"Clé privée sauvegardée : {filepath}")


def save_public_key(public_key, filepath: str):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filepath, 'wb') as f:
        f.write(pem)
    print(f"Clé publique sauvegardée : {filepath}")


# ═══════════════════════════════════════════
# DÉMONSTRATION
# ═══════════════════════════════════════════

def demo_rsa():
    print("=" * 60)
    print("  DÉMO RSA-2048 COMPLET")
    print("=" * 60)

    # Générer les clés
    print("\n[Génération RSA-2048...]")
    priv, pub = generate_rsa_key(2048)
    print(f"  Clé générée ✅")

    # Chiffrement hybride (gros fichier)
    message = b"Document confidentiel " * 100  # 2200 bytes
    print(f"\n[Chiffrement hybride ({len(message)} bytes)]")
    bundle = hybrid_encrypt(message, pub)
    print(f"  Clé chiffrée : {len(bundle['encrypted_key'])} bytes (RSA-OAEP)")
    print(f"  Message chiffré : {len(bundle['ciphertext'])} bytes (AES-GCM)")

    recovered = hybrid_decrypt(bundle, priv)
    assert recovered == message
    print(f"  Déchiffrement ✅")


demo_rsa()
```

---

## Chapitre 8 : Courbes Elliptiques

### 8.1 Philosophie mathématique

Les courbes elliptiques offrent la **même sécurité que RSA avec des clés beaucoup plus courtes**. En 2026, elles sont la recommandation principale du NIST.

```
COURBE ELLIPTIQUE sur corps fini 𝔽p :
  y² = x³ + ax + b (mod p)
  Condition : 4a³ + 27b² ≠ 0 (non singulière)

EXEMPLE : P-256 (secp256r1, NIST SP 800-186)
  a = -3
  b = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
  p = 2^256 - 2^224 + 2^192 + 2^96 - 1 (premier de 256 bits)
  n = nombre de points (ordre du groupe) ≈ 2^256

OPÉRATION FONDAMENTALE : Addition de points
  P + Q = R  (loi de groupe géométrique)
  La multiplication scalaire kP = P + P + ... + P (k fois)
  est rapide : O(log k) avec l'algorithme double-and-add.

PROBLÈME DIFFICILE : ECDLP (Elliptic Curve Discrete Logarithm Problem)
  Connaissant G (point générateur) et Q = kG,
  retrouver k est considéré impossible pour n ≈ 2^256.
  Meilleur algorithme : Pohlig-Hellman + Pollard rho = O(√n)
  Pour P-256 : O(2^128) opérations ← sécurit de 128 bits.

COMPARAISON TAILLES DE CLÉS (sécurité équivalente 128 bits) :
  RSA   : 3072 bits → signature 384 bytes
  ECC   : 256 bits  → signature 64 bytes
  → ECC est 12× plus compact, 10-40× plus rapide
```

### 8.2 ECDH — Échange de clés Diffie-Hellman sur courbes elliptiques

```python
#!/usr/bin/env python3
"""
ecdh_workshop.py — ECDH et ECDSA
Référence : NIST SP 800-186, RFC 8031
"""

from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDH, SECP256R1, SECP384R1, generate_private_key
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import os


def ecdh_key_exchange():
    """
    ECDH (Elliptic Curve Diffie-Hellman) :
    Deux parties établissent un secret partagé SANS jamais le transmettre.
    
    Magie : Alice connaît a, Bob connaît b.
    Ils s'échangent leurs clés publiques A=aG et B=bG.
    Alice calcule : a×B = a×(bG) = abG
    Bob calcule   : b×A = b×(aG) = abG
    → Même secret partagé !
    Un espion ne voit que A et B, pas a ni b.
    Retrouver a depuis A = ECDLP (supposé impossible).
    """
    curve = SECP256R1()  # P-256 — recommandé NIST

    # Alice génère sa paire de clés éphémère
    alice_private = generate_private_key(curve, default_backend())
    alice_public = alice_private.public_key()

    # Bob génère sa paire de clés éphémère
    bob_private = generate_private_key(curve, default_backend())
    bob_public = bob_private.public_key()

    # Échange des clés publiques (envoyées en clair)
    # Alice calcule le secret partagé
    alice_shared = alice_private.exchange(ECDH(), bob_public)
    # Bob calcule le secret partagé
    bob_shared = bob_private.exchange(ECDH(), alice_public)

    # Les deux secrets sont identiques
    assert alice_shared == bob_shared
    print(f"Secret partagé brut : {alice_shared.hex()}")

    # CRUCIAL : le secret brut ne s'utilise JAMAIS directement comme clé !
    # → Appliquer HKDF pour dériver une clé propre
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ECDH session key v1",
        backend=default_backend()
    ).derive(alice_shared)

    print(f"Clé dérivée (HKDF) : {derived_key.hex()}")
    print(f"→ Cette clé peut servir pour AES-256-GCM")
    return derived_key


# ═══════════════════════════════════════════
# ECDSA — Signatures numériques sur ECC
# ═══════════════════════════════════════════

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

def ecdsa_demo():
    """
    ECDSA (Elliptic Curve Digital Signature Algorithm)
    Référence : NIST FIPS 186-5
    
    ATTENTION : ECDSA nécessite un nonce k UNIQUE et ALÉATOIRE par signature.
    Réutiliser k révèle la clé privée (attaque Sony PS3, 2010).
    → Préférer Ed25519 (RFC 8032) qui évite ce problème.
    """
    # Générer une clé ECDSA P-256
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()

    message = b"Document a signer — version 1.0"

    # Signature
    signature = private_key.sign(
        message,
        ec.ECDSA(hashes.SHA256())
    )
    print(f"Signature ECDSA : {len(signature)} bytes")
    print(f"Signature (hex) : {signature.hex()[:64]}...")

    # Vérification
    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        print("✅ Signature valide")
    except InvalidSignature:
        print("❌ Signature invalide")

    # Message altéré
    try:
        public_key.verify(signature, message + b"X", ec.ECDSA(hashes.SHA256()))
        print("❌ BUG")
    except InvalidSignature:
        print("✅ Altération détectée")


# ═══════════════════════════════════════════
# Ed25519 — La recommandation 2026
# ═══════════════════════════════════════════

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)

def ed25519_demo():
    """
    Ed25519 (RFC 8032, 2017) — Edwards-curve Digital Signature Algorithm
    Courbe : Curve25519 (Bernstein)
    
    Avantages vs ECDSA :
    - Nonce déterministe (dérivé du message + clé) → pas de vulnérabilité k
    - Implémentation constante en temps (pas de timing attacks)
    - Clés et signatures très compactes : 32 + 64 bytes
    - Très rapide : ~100k signatures/seconde sur CPU moderne
    - Utilisé par : OpenSSH, Signal, Tor, WireGuard, age
    """
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    message = b"Document signe avec Ed25519"
    signature = private_key.sign(message)

    print(f"\nEd25519 :")
    print(f"  Clé privée : 32 bytes")
    print(f"  Clé publique : {len(public_key.public_bytes_raw())} bytes")
    print(f"  Signature : {len(signature)} bytes")

    public_key.verify(signature, message)
    print(f"  Signature valide ✅")

    # Comparaison tailles
    print(f"\n  Comparaison (même niveau de sécurité ~128 bits) :")
    print(f"  RSA-3072  : clé {3072//8} bytes, sign {3072//8} bytes")
    print(f"  ECDSA-256 : clé 32 bytes, sign ~72 bytes")
    print(f"  Ed25519   : clé 32 bytes, sign 64 bytes ← gagnant")


ecdh_key_exchange()
ecdsa_demo()
ed25519_demo()
```

---

## Chapitre 9 : Protocoles d'Échange de Clés

### 9.1 Le problème de la distribution de clés

```
PROBLÈME FONDAMENTAL :
  Alice veut communiquer secrètement avec Bob.
  Ils n'ont jamais communiqué auparavant.
  Comment se mettre d'accord sur une clé secrète commune
  sans la transmettre en clair ?

SOLUTIONS :
  1. Diffie-Hellman (1976) — révolution cryptographique
     → Le premier protocole à résoudre ce problème
     → Basé sur le problème du logarithme discret

  2. RSA key transport
     → Bob chiffre une clé avec la clé publique d'Alice

  3. ECDH ephemeral (ECDHE)
     → DH sur courbes elliptiques, clés éphémères
     → Fournit la Perfect Forward Secrecy (PFS)
```

### 9.2 Perfect Forward Secrecy — concept crucial

```
SANS PFS (RSA statique) :
  Alice et Bob utilisent toujours la même paire RSA.
  Un adversaire enregistre tous les échanges chiffrés.
  Plus tard, il vole la clé privée RSA.
  → Il peut déchiffrer TOUS les échanges passés enregistrés.

AVEC PFS (ECDHE) :
  Alice et Bob génèrent de NOUVELLES paires de clés éphémères
  pour chaque session. Ces clés sont détruites après la session.
  Un adversaire enregistre tous les échanges chiffrés.
  Plus tard, il vole la clé privée RSA.
  → Il ne peut déchiffrer AUCUNE session passée
    (les clés de session éphémères sont détruites).

C'est pourquoi TLS 1.3 impose ECDHE pour tous les échanges.
```

---

# ════════════════════════════════════════════════════════
# PARTIE IV — AUTHENTIFICATION ET INTÉGRITÉ
# ════════════════════════════════════════════════════════

---

## Chapitre 10 : MAC et HMAC

### 10.1 Différence Hash vs MAC

```
HASH seul : H(message) → pas d'authentification
  N'importe qui peut calculer H(message_modifié).
  → Intégrité SANS authenticité.

MAC (Message Authentication Code) : MAC(clé, message)
  Seul quelqu'un connaissant la clé peut calculer un MAC valide.
  → Intégrité ET authenticité simultanément.
  → Symétrique : les deux parties partagent la même clé.

HMAC (Hash-based MAC, RFC 2104) :
  HMAC(K, m) = H((K ⊕ opad) || H((K ⊕ ipad) || m))
  où opad = 0x5C5C...5C et ipad = 0x3636...36
  
  Construction sécurisée qui évite les attaques par extension
  de longueur contre HMAC-SHA-256.
```

### 10.2 Implémentation HMAC

```python
#!/usr/bin/env python3
# hmac_workshop.py

import hmac
import hashlib
import os
import time

def compute_hmac(message: bytes, key: bytes) -> bytes:
    """Calcule HMAC-SHA256."""
    return hmac.new(key, message, hashlib.sha256).digest()

def verify_hmac(message: bytes, key: bytes, received_mac: bytes) -> bool:
    """
    Vérification en temps constant (constant-time).
    CRUCIAL : Ne jamais comparer les MACs avec == ou byte à byte !
    
    Si on compare byte à byte et qu'on s'arrête dès le premier mismatch,
    un adversaire peut mesurer le temps de comparaison pour deviner le MAC
    byte par byte (timing attack).
    
    hmac.compare_digest() utilise une comparaison en temps constant.
    """
    expected = compute_hmac(message, key)
    return hmac.compare_digest(expected, received_mac)

# Démonstration timing attack (PÉDAGOGIQUE)
key = os.urandom(32)
message = b"message important"
valid_mac = compute_hmac(message, key)
wrong_mac = bytes(b ^ 0xFF for b in valid_mac)  # MAC faux

# Temps avec comparaison naïve (vulnérable)
def vulnerable_compare(a: bytes, b: bytes) -> bool:
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x != y:
            return False  # ← s'arrête tôt si différent → timing leak
    return True

# Mesurer la différence de temps (exagérée ici pour illustration)
N = 100000
t0 = time.perf_counter()
for _ in range(N):
    vulnerable_compare(valid_mac, wrong_mac)
t_wrong = time.perf_counter() - t0

t0 = time.perf_counter()
for _ in range(N):
    vulnerable_compare(valid_mac, valid_mac)
t_valid = time.perf_counter() - t0

print(f"Comparaison naïve :")
print(f"  MAC faux   : {t_wrong*1000:.2f} ms → s'arrête au 1er byte différent")
print(f"  MAC valide : {t_valid*1000:.2f} ms → parcourt tous les bytes")
print(f"  Différence : {abs(t_valid-t_wrong)*1000:.2f} ms ← timing leak !")

print(f"\nComparaison hmac.compare_digest() :")
t0 = time.perf_counter()
for _ in range(N):
    hmac.compare_digest(valid_mac, wrong_mac)
t_safe_wrong = time.perf_counter() - t0

t0 = time.perf_counter()
for _ in range(N):
    hmac.compare_digest(valid_mac, valid_mac)
t_safe_valid = time.perf_counter() - t0

print(f"  MAC faux   : {t_safe_wrong*1000:.2f} ms")
print(f"  MAC valide : {t_safe_valid*1000:.2f} ms")
print(f"  Différence : {abs(t_safe_valid-t_safe_wrong)*1000:.2f} ms ← ~0 ✅")
```

---

## Chapitre 11 : Signatures Numériques

### 11.1 Ce que garantit une signature numérique

```
SIGNATURE NUMÉRIQUE = Hachage chiffré avec la clé privée

Propriétés :
  ✓ Authenticité : seul le détenteur de la clé privée peut signer
  ✓ Intégrité    : toute modification invalide la signature
  ✓ Non-répudiation : le signataire ne peut pas nier avoir signé

PROCESSUS :
  1. Alice calcule : h = SHA256(message)
  2. Alice calcule : s = Sign(clé_privée_Alice, h)
  3. Alice publie  : (message, s)
  
  Bob vérifie :
  1. Bob calcule   : h' = SHA256(message)
  2. Bob vérifie   : Verify(clé_publique_Alice, h', s) == True
  
  Si message modifié : h' ≠ h → vérification échoue.
  Si signature falsifiée : sans clé privée d'Alice, impossible.
```

### 11.2 Signatures avec Python — cas pratiques

```python
#!/usr/bin/env python3
# signing_workshop.py

import json
import time
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


class DocumentSigner:
    """
    Système de signature de documents.
    Utilise Ed25519 (RFC 8032).
    """

    def __init__(self):
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def sign_document(self, document: dict) -> dict:
        """
        Signe un document JSON.
        Retourne le document avec sa signature.
        """
        # Canonicaliser le JSON (ordre des clés déterministe)
        canonical = json.dumps(document, sort_keys=True, ensure_ascii=True)
        signature = self.private_key.sign(canonical.encode())

        return {
            "document": document,
            "signature": base64.b64encode(signature).decode(),
            "signed_at": time.time(),
            "algorithm": "Ed25519",
        }

    def verify_document(self, signed_doc: dict) -> bool:
        """Vérifie la signature d'un document signé."""
        canonical = json.dumps(
            signed_doc["document"], sort_keys=True, ensure_ascii=True
        )
        sig = base64.b64decode(signed_doc["signature"])
        try:
            self.public_key.verify(sig, canonical.encode())
            return True
        except InvalidSignature:
            return False

    def get_public_key_pem(self) -> str:
        return self.public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()


# Test
signer = DocumentSigner()

contract = {
    "parties": ["Alice Corp", "Bob Ltd"],
    "objet": "Fourniture de services cloud",
    "montant": 50000,
    "devise": "EUR",
    "date": "2026-01-10"
}

print("Signature du contrat...")
signed = signer.sign_document(contract)
print(f"  Signature : {signed['signature'][:40]}...")
print(f"  Validité  : {'✅' if signer.verify_document(signed) else '❌'}")

# Tentative de modification
tampered = dict(signed)
tampered["document"]["montant"] = 500000  # modifier le montant !
print(f"\nContrat falsifié (montant modifié) :")
print(f"  Validité  : {'✅' if signer.verify_document(tampered) else '❌ Falsification détectée'}")
```

---

# ════════════════════════════════════════════════════════
# PARTIE V — CRYPTOGRAPHIE MODERNE (2024-2026)
# ════════════════════════════════════════════════════════

---

## Chapitre 13 : Post-Quantique

### 13.1 La menace quantique

```
ALGORITHME DE SHOR (1994) :
  Un ordinateur quantique suffisamment grand peut factoriser
  n = p×q en O(log³n) opérations quantiques.
  → RSA, DH, ECDH, ECDSA : TOUS compromis par un tel ordinateur.

ALGORITHME DE GROVER (1996) :
  Accélère la recherche exhaustive par √ (racine carrée).
  → AES-128 : sécurité réduite à 64 bits (insuffisant)
  → AES-256 : sécurité réduite à 128 bits (acceptable)
  → SHA-256 : résistance collisions réduite à 85 bits (limite)
  → SHA-384+ : rester en sécurité post-quantique

ÉTAT EN 2026 :
  - Pas encore d'ordinateur quantique capable de casser RSA-2048
  - Mais : "Store now, decrypt later" → des adversaires enregistrent
    les communications chiffrées AUJOURD'HUI pour les déchiffrer
    quand les ordinateurs quantiques seront disponibles.
  - Migration urgente pour les données à longue durée de vie.

NIST POST-QUANTUM STANDARDS (août 2024) :
  FIPS 203 : ML-KEM (Module-Lattice KEM = CRYSTALS-Kyber)
             → Chiffrement et échange de clés
  FIPS 204 : ML-DSA (Module-Lattice DSA = CRYSTALS-Dilithium)
             → Signatures numériques
  FIPS 205 : SLH-DSA (Stateless Hash-based DSA = SPHINCS+)
             → Signatures alternatives (basées sur hash)
```

### 13.2 Kyber/ML-KEM — chiffrement post-quantique

```python
#!/usr/bin/env python3
"""
post_quantum_demo.py
Démontre les algorithmes post-quantiques.
pip install kyber-py  (implémentation pédagogique, pas pour production)
Note : utiliser liboqs en production (https://openquantumsafe.org)
"""

# Démonstration conceptuelle des propriétés ML-KEM
print("=" * 60)
print("  CRYPTOGRAPHIE POST-QUANTIQUE — ML-KEM (FIPS 203)")
print("=" * 60)

print("""
KYBER / ML-KEM repose sur le problème MLWE :
  Module Learning With Errors

Problème LWE :
  Données : (A, b = A×s + e)  où s = secret, e = erreur petite
  Problème : retrouver s

C'est un problème de réseau euclidien (lattice problem).
Résistant aux ordinateurs quantiques ET classiques.

Tailles de clés ML-KEM (FIPS 203) :
  ML-KEM-512  : clé pub 800 bytes  → sécurité ≈ AES-128 (Cat. 1)
  ML-KEM-768  : clé pub 1184 bytes → sécurité ≈ AES-192 (Cat. 3) ← recommandé
  ML-KEM-1024 : clé pub 1568 bytes → sécurité ≈ AES-256 (Cat. 5)

Comparaison avec RSA-3072 :
  RSA-3072    : clé pub 384 bytes, sécurité classique 128 bits
  ML-KEM-768  : clé pub 1184 bytes, sécurité post-quantique 128 bits
""")

# Schéma KEM (Key Encapsulation Mechanism)
print("""
FONCTIONNEMENT KEM :
  1. Bob génère (clé_pub, clé_priv)
  2. Alice appelle Encapsulate(clé_pub_Bob) → (ciphertext, shared_secret)
  3. Alice envoie ciphertext à Bob
  4. Bob appelle Decapsulate(clé_priv_Bob, ciphertext) → shared_secret
  5. Alice et Bob ont le même shared_secret → utilisé pour AES

SCHÉMA HYBRIDE recommandé par BSI/ANSSI 2026 :
  Combiner ECC (ECDH) + ML-KEM → double sécurité
  Si l'un est cassé, l'autre protège encore.
  shared_key = HKDF(ECDH_secret || ML-KEM_secret)
""")
```

### 13.3 Migration post-quantique — roadmap pratique

```
NIST SP 800-131B (prévu 2025-2026) — planning de migration :

IMMÉDIAT (2024-2026) :
  ✓ Passer à TLS 1.3 partout
  ✓ Remplacer RSA-1024/2048 par RSA-3072 ou ECDSA P-384
  ✓ AES-256 pour toutes les nouvelles données
  ✓ SHA-384/512 pour les signatures

COURT TERME (2026-2028) :
  ✓ Déployer ML-KEM en mode hybride (ECC + ML-KEM)
  ✓ Déployer ML-DSA pour les signatures critiques
  ✓ Auditer les systèmes pour identifier RSA/ECC

MOYEN TERME (2028-2030) :
  ✓ Compléter la migration vers algorithmes post-quantiques
  ✓ Déprécier RSA et ECC seuls pour nouvelles applications

LONG TERME (2030+) :
  ✓ Retirer RSA/ECC des systèmes actifs
  ✓ Vérifier les archives chiffrées pré-2026
```

---

## Chapitre 14 : TLS 1.3 — Le Protocole de Référence

### 14.1 Architecture TLS 1.3 (RFC 8446)

```
TLS 1.3 vs TLS 1.2 :
  TLS 1.2 : 2 round-trips pour établir la connexion
  TLS 1.3 : 1 round-trip (ou 0-RTT pour les reprises)

Algorithmes supportés par TLS 1.3 :
  Échange de clés : ECDHE (P-256, P-384, X25519, X448)
  Chiffrement    : AES-128-GCM, AES-256-GCM, ChaCha20-Poly1305
  Hachage MAC    : SHA-256, SHA-384
  Signatures     : ECDSA, Ed25519, RSA-PSS

Algorithmes RETIRÉS en TLS 1.3 :
  ❌ RSA key exchange (pas de PFS)
  ❌ DH statique (pas de PFS)
  ❌ RC4, DES, 3DES
  ❌ MD5, SHA-1 pour signatures
  ❌ CBC mode (vulnérable à BEAST, POODLE)
  ❌ Compression (vulnérable à CRIME)
```

### 14.2 Analyser TLS avec OpenSSL

```bash
# Vérifier la configuration TLS d'un serveur
$ openssl s_client -connect google.com:443 -tls1_3 2>/dev/null | head -20
→ SSL-Session:
→     Protocol  : TLSv1.3
→     Cipher    : TLS_AES_256_GCM_SHA384
→     Session-ID: ...

# Lister les suites de chiffrement TLS 1.3
$ openssl ciphers -v TLSv1.3
→ TLS_AES_256_GCM_SHA384  TLSv1.3 Kx=any  Au=any  Enc=AESGCM(256) Mac=AEAD
→ TLS_CHACHA20_POLY1305_SHA256  ...
→ TLS_AES_128_GCM_SHA256  ...

# Vérifier un certificat
$ openssl x509 -in /etc/ssl/certs/ca-certificates.crt -noout -text | head -40

# Test de sécurité complet avec testssl.sh
$ bash testssl.sh google.com

# Générer un certificat auto-signé avec Ed25519
$ openssl genpkey -algorithm ed25519 -out private.pem
$ openssl req -new -x509 -key private.pem -out cert.pem -days 365 \
  -subj "/C=FR/O=MonOrg/CN=exemple.local"
$ openssl x509 -in cert.pem -noout -text | grep -E "(Algorithm|Public|Subject)"
→   Signature Algorithm: ED25519
→   Public Key Algorithm: ED25519
→   Subject: C=FR, O=MonOrg, CN=exemple.local
```

---

# ════════════════════════════════════════════════════════
# PARTIE VI — APPLICATIONS ET ATELIERS
# ════════════════════════════════════════════════════════

---

## Chapitre 17 : Attaques Classiques et Contre-Mesures

### 17.1 Catalogue des attaques

```
ATTAQUES SUR LE CANAL AUXILIAIRE (Side-Channel) :
  Timing Attack    → mesurer le temps d'exécution révèle des bits de clé
  Power Analysis   → mesurer la consommation électrique (crypto IoT)
  Cache Attack     → Flush+Reload, Spectre sur AES non protégé
  Countermeasure   → Implémentations à temps constant, masquage

ATTAQUES SUR LES PRIMITIVES :
  Padding Oracle   → CBC avec erreurs de padding différenciées (Vaudenay)
  Lucky 13         → Timing attack sur CBC avec MAC
  BEAST/POODLE     → Attaques sur SSLv3/TLS 1.0 avec CBC
  Countermeasure   → TLS 1.3 supprime tous ces modes

ATTAQUES SUR L'ALÉA :
  Nonce Reuse      → Réutiliser un nonce AES-GCM → fuite de clé
  Weak PRNG        → Android Bitcoin wallet 2013 (java.util.Random)
  Predictable IV   → BEAST attack (IV CBC prévisible)
  Countermeasure   → os.urandom(), /dev/urandom, CSPRNG

ATTAQUES DE PROTOCOLES :
  MITM             → Sans vérification de certificat
  Replay Attack    → Sans nonce ou timestamp
  Downgrade        → Forcer une version de protocole plus faible
  Countermeasure   → PKI, timestamps, TLS_FALLBACK_SCSV
```

### 17.2 Démonstration d'une nonce reuse attack

```python
#!/usr/bin/env python3
"""
nonce_reuse_attack.py
DÉMONSTRATION PÉDAGOGIQUE de l'attaque nonce reuse sur AES-GCM.
Montre pourquoi réutiliser un nonce est catastrophique.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def catastrophic_nonce_reuse():
    """
    Si deux messages sont chiffrés avec le même (clé, nonce) en CTR/GCM :
    C1 = P1 ⊕ keystream
    C2 = P2 ⊕ keystream  (même keystream !)
    
    Alors : C1 ⊕ C2 = P1 ⊕ P2
    Si on connaît P1, on peut récupérer P2 :
    P2 = C1 ⊕ C2 ⊕ P1
    
    En pratique (Two-Time Pad Attack) :
    L'adversaire obtient C1 ⊕ C2, et avec de la statistique
    sur le texte anglais, peut retrouver les deux messages.
    """
    key = os.urandom(32)
    FIXED_NONCE = b'\x00' * 12  # ← CATASTROPHE : nonce fixe !

    message1 = b"Mon mot de passe est SuperSecret!"
    message2 = b"Virement compte 12345 = 50000EUR"

    aesgcm = AESGCM(key)

    # Chiffrement avec le MÊME nonce (erreur de programmation)
    ct1 = aesgcm.encrypt(FIXED_NONCE, message1, None)
    ct2 = aesgcm.encrypt(FIXED_NONCE, message2, None)

    print(f"Message 1 : {message1}")
    print(f"Message 2 : {message2}")
    print(f"CT1 (sans tag) : {ct1[:-16].hex()}")
    print(f"CT2 (sans tag) : {ct2[:-16].hex()}")

    # Attaque : XOR des deux chiffrés (sans les tags de 16 bytes)
    xor_ct = bytes(a ^ b for a, b in zip(ct1[:-16], ct2[:-16]))
    print(f"\nCT1 ⊕ CT2 = P1 ⊕ P2 = {xor_ct.hex()}")

    # Si l'adversaire connaît/devine P1 (message1)
    recovered_p2 = bytes(x ^ y for x, y in zip(xor_ct, message1))
    print(f"\nAttaque Two-Time Pad :")
    print(f"  P2 récupéré : {recovered_p2}")
    # → Le message confidentiel est entièrement révélé !

    print(f"\n✅ Contre-mesure : nonce aléatoire par message")
    print(f"  nonce1 = {os.urandom(12).hex()}")
    print(f"  nonce2 = {os.urandom(12).hex()} ← toujours différent")

catastrophic_nonce_reuse()
```

---

## Chapitre 18 : Challenge Final

### 🔴 Challenge 1 — Implémenter un système de messagerie chiffrée E2E

```
CONTEXTE :
  Concevoir et implémenter un système de messagerie
  chiffrée de bout en bout inspiré du Signal Protocol.

EXIGENCES TECHNIQUES :
  1. Échange de clés initial (X3DH — Extended Triple DH)
     - Clés d'identité Ed25519 permanentes (IK)
     - Clés signées préliminaires ECDH (SPK, rotées chaque semaine)
     - One-time prekeys ECDH (OPK, à usage unique)

  2. Double Ratchet (pour chaque session)
     - Diffie-Hellman Ratchet : nouvelle paire de clés à chaque message
     - Symmetric-Key Ratchet : dérive les clés de message via HKDF
     → Fournit : PFS + Break-in recovery (compromission passée/future)

  3. Chiffrement des messages
     - AES-256-GCM avec AEAD
     - AAD = numéro de message + identités

  4. Propriétés à démontrer :
     - Confidentialité : seul le destinataire peut lire
     - Authenticité : impossible de forger un message
     - PFS : compromettre une clé ne révèle pas les messages passés
     - Deniability : impossible de prouver qu'Alice a envoyé X à Bob

IMPLÉMENTATION MINIMALE :
```

```python
#!/usr/bin/env python3
# challenge_e2e_messaging.py
# Signal Protocol simplifié — à compléter

from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey, X25519PublicKey
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os


class SignalUser:
    """
    Utilisateur avec ses clés Signal Protocol.
    À COMPLÉTER pour l'implémentation complète.
    """

    def __init__(self, name: str):
        self.name = name

        # Clé d'identité (permanente, signée)
        self.ik_private = X25519PrivateKey.generate()
        self.ik_public = self.ik_private.public_key()

        # Clé de signature d'identité (pour SPK)
        self.ik_sign_private = Ed25519PrivateKey.generate()
        self.ik_sign_public = self.ik_sign_private.public_key()

        # Signed Prekey (rotée toutes les semaines)
        self.spk_private = X25519PrivateKey.generate()
        self.spk_public = self.spk_private.public_key()

        # Signature de la SPK par la clé d'identité
        self.spk_sig = self.ik_sign_private.sign(
            self.spk_public.public_bytes_raw()
        )

        # One-Time Prekeys (100 générées d'avance)
        self.otpks = [
            (X25519PrivateKey.generate(), ) for _ in range(10)
        ]
        self.otpks = [
            (priv, priv.public_key()) for (priv,) in self.otpks
        ]

    def get_prekey_bundle(self) -> dict:
        """Retourne le bundle de clés publiques (publié sur le serveur)."""
        opk_priv, opk_pub = self.otpks.pop(0)
        return {
            "identity_key": self.ik_public.public_bytes_raw(),
            "signed_prekey": self.spk_public.public_bytes_raw(),
            "spk_signature": self.spk_sig,
            "one_time_prekey": opk_pub.public_bytes_raw(),
            "sign_key": self.ik_sign_public,
            "_opk_private": opk_priv,  # gardé côté serveur pour Bob
        }


class X3DHHandshake:
    """
    X3DH — Extended Triple Diffie-Hellman
    Protocole d'établissement de session Signal.
    """

    @staticmethod
    def initiate(alice: SignalUser, bob_bundle: dict) -> tuple[bytes, bytes]:
        """
        Alice initie une session avec Bob.
        Retourne (shared_secret, ephemeral_key_pub).
        """
        # Vérifier la signature de la SPK de Bob
        from cryptography.exceptions import InvalidSignature
        try:
            bob_bundle["sign_key"].verify(
                bob_bundle["spk_signature"],
                bob_bundle["signed_prekey"]
            )
        except InvalidSignature:
            raise ValueError("SPK signature invalide — attaque possible !")

        # Générer une clé éphémère
        ek_private = X25519PrivateKey.generate()
        ek_public = ek_private.public_key()

        # Charger les clés publiques de Bob
        bob_ik = X25519PublicKey.from_public_bytes(bob_bundle["identity_key"])
        bob_spk = X25519PublicKey.from_public_bytes(bob_bundle["signed_prekey"])
        bob_opk = X25519PublicKey.from_public_bytes(bob_bundle["one_time_prekey"])

        # 4 échanges DH
        dh1 = alice.ik_private.exchange(bob_spk)   # IK_A × SPK_B
        dh2 = ek_private.exchange(bob_ik)           # EK_A × IK_B
        dh3 = ek_private.exchange(bob_spk)          # EK_A × SPK_B
        dh4 = ek_private.exchange(bob_opk)          # EK_A × OPK_B

        # Dériver le secret partagé
        master_secret = dh1 + dh2 + dh3 + dh4
        shared_secret = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'\x00' * 32,
            info=b"X3DH Signal v1",
        ).derive(master_secret)

        return shared_secret, ek_public.public_bytes_raw()


# TODO pour les étudiants :
# 1. Compléter X3DHHandshake.receive() du côté de Bob
# 2. Implémenter le Double Ratchet (DH Ratchet + Symmetric Ratchet)
# 3. Chiffrer/déchiffrer des messages avec le ratchet
# 4. Tester la propriété PFS : compromettre une clé ne révèle pas les anciens messages
# 5. Comparer avec l'implémentation officielle : https://signal.org/docs/specifications/x3dh/
```

### 🔴 Challenge 2 — Analyser et casser un chiffrement faible

```python
#!/usr/bin/env python3
"""
challenge_cryptanalysis.py
Cinq défis de cryptanalyse, du plus simple au plus complexe.
"""

import base64
import string

# ══════════════════════════════════════════
# DÉFI 1 — César (débutant)
# ══════════════════════════════════════════
# Déchiffrer ce message chiffré par décalage César :
CIPHER_1 = "YBYNQR RFG YN PBEQR QR YN PBCBYBTVR"
# Indice : analyse de fréquences (E est la lettre la plus fréquente en français)
# TODO : implémenter une attaque par analyse de fréquences

# ══════════════════════════════════════════
# DÉFI 2 — Vigenère (intermédiaire)
# ══════════════════════════════════════════
CIPHER_2 = "LXFOPVEFRNHR"
# Chiffré avec une clé de 3 lettres
# Méthode : test de Kasiski pour trouver la longueur de clé
# puis analyse de fréquences sur chaque sous-séquence
# TODO : implémenter l'attaque de Kasiski

# ══════════════════════════════════════════
# DÉFI 3 — XOR avec clé répétée (avancé)
# ══════════════════════════════════════════
CIPHER_3 = bytes.fromhex(
    "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"
)
# Chiffré avec XOR et une clé d'UN seul byte (0x00-0xFF)
# Méthode : tester les 256 clés possibles, garder celle qui produit du texte anglais
# Score = somme des fréquences des lettres courantes (espace, e, t, a, o, i, n)
# TODO : implémenter le brute force avec scoring de fréquences

# ══════════════════════════════════════════
# DÉFI 4 — Padding Oracle (expert)
# ══════════════════════════════════════════
# Simuler une attaque padding oracle sur AES-CBC

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

SECRET_KEY = os.urandom(16)
SECRET_MESSAGE = b"Le mot de passe est: Hunter42!"

def encrypt_with_padding(plaintext: bytes) -> tuple[bytes, bytes]:
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), default_backend())
    ct = cipher.encryptor()
    return iv, ct.update(padded) + ct.finalize()

def oracle_decrypt(iv: bytes, ciphertext: bytes) -> bool:
    """
    Oracle : retourne True si le padding est valide.
    En pratique : le serveur retourne HTTP 200 vs 403.
    C'est la SEULE information qu'on exploite.
    """
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), default_backend())
    dec = cipher.decryptor()
    plaintext = dec.update(ciphertext) + dec.finalize()
    try:
        unpadder = padding.PKCS7(128).unpadder()
        unpadder.update(plaintext) + unpadder.finalize()
        return True  # Padding valide
    except ValueError:
        return False  # Padding invalide

# TODO : implémenter l'attaque padding oracle complète
# Algorithme :
# Pour chaque bloc de ciphertext :
#   Pour chaque position i de 1 à 16 :
#     Trouver le byte b tel que oracle(iv_modifié, C_n) = True
#     → Ce byte révèle un byte du plaintext intermédiaire
#     → XOR avec le ciphertext précédent révèle le plaintext
#
# Référence : https://research.nccgroup.com/2021/02/17/padding-oracle-attacks-in-the-wild/

iv, ciphertext = encrypt_with_padding(SECRET_MESSAGE)
print(f"Votre objectif : déchiffrer ce message sans la clé")
print(f"IV    : {iv.hex()}")
print(f"CT    : {ciphertext.hex()}")
print(f"Seule information disponible : oracle_decrypt(iv, ct) → bool")
print(f"Bon courage ! (environ {16 * 256} appels oracle nécessaires par bloc)")
```

---

# ANNEXES

---

## Annexe A — Recommandations 2026

```
ALGORITHMES RECOMMANDÉS (NIST + ANSSI 2026)

CHIFFREMENT SYMÉTRIQUE :
  ✅ AES-256-GCM         → données en transit et au repos
  ✅ ChaCha20-Poly1305   → logiciel sur CPU sans AES-NI
  ✅ AES-128-GCM         → acceptable (128 bits sécurité)
  ❌ DES, 3DES, RC4      → interdits
  ❌ AES-ECB             → interdit (ne pas utiliser ECB jamais)

HACHAGE :
  ✅ SHA-256, SHA-384, SHA-512   → signatures, intégrité
  ✅ SHA3-256, SHA3-384          → alternative (résistant extensions)
  ✅ BLAKE3                      → vitesse (non-FIPS)
  ✅ Argon2id (RFC 9106)         → mots de passe UNIQUEMENT
  ❌ SHA-1, MD5, MD4             → interdits pour sécurité

ASYMÉTRIQUE CLASSIQUE :
  ✅ Ed25519 (RFC 8032)          → signatures (recommandé)
  ✅ X25519 (RFC 7748)           → échange de clés (recommandé)
  ✅ ECDSA P-384                 → si FIPS requis
  ✅ RSA-3072 / RSA-4096         → si ECC impossible
  ❌ RSA-1024/2048               → insuffisant post-2030
  ❌ DSA, DH < 2048              → interdits

POST-QUANTIQUE (migration 2026-2030) :
  ✅ ML-KEM-768 (FIPS 203)       → chiffrement/KEM
  ✅ ML-DSA-65 (FIPS 204)        → signatures
  ✅ SLH-DSA (FIPS 205)          → signatures alternatives
  ⚠️ Hybride ECC + PQC           → recommandé pendant transition
```

## Annexe B — Tailles de Clés et Durées de Sécurité

```
Sécurité  Symétrique  RSA/DH    ECC    Valide jusqu'à
───────────────────────────────────────────────────────
80 bits   2TDEA       1024      160    < 2010 (obsolète)
112 bits  AES-112     2048      224    ~2030
128 bits  AES-128     3072      256    ~2030+
192 bits  AES-192     7680      384    ~2040+
256 bits  AES-256     15360     521    long terme

Source : NIST SP 800-57 Part 1 Rev.5 (2020)
```

## Annexe C — Ressources Officielles

```
STANDARDS FONDAMENTAUX :
  https://csrc.nist.gov/publications/fips  → Tous les FIPS
  https://csrc.nist.gov/publications/sp    → Special Publications
  https://www.rfc-editor.org               → RFC (protocoles)
  https://www.ssi.gouv.fr/entreprise/reglementation/ria/  → ANSSI RGS

DOCUMENTATION PYTHON :
  https://cryptography.io/en/latest/       → pyca/cryptography
  https://pycryptodome.readthedocs.io/     → PyCryptodome

POST-QUANTIQUE :
  https://csrc.nist.gov/projects/post-quantum-cryptography
  https://openquantumsafe.org              → liboqs (implémentations)

OUTILS PRATIQUES :
  https://testssl.sh                       → audit TLS
  https://www.ssllabs.com/ssltest/        → test SSL en ligne
  https://smallstep.com                   → PKI moderne
  https://age-encryption.org              → chiffrement de fichiers moderne
```

---

*TP rédigé en référence aux standards NIST, ANSSI et RFC en vigueur en 2026.*
*Toutes les implémentations utilisent la bibliothèque `cryptography` (pyca) — ne jamais ré-implémenter les primitives cryptographiques soi-même.*
*"Never roll your own crypto." — adage fondamental de la communauté cryptographique.*
