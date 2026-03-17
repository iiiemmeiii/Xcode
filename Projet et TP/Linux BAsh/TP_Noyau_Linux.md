# TP — Noyau Linux & Structures de Bas Niveau
## Comprendre, Analyser et Manipuler le Cœur du Système
### Niveau Zéro → Expert Noyau · 2025-2026

---

> **Références officielles utilisées**
> - Linux Kernel Documentation — https://www.kernel.org/doc/html/latest/
> - Linux Kernel Source (6.x) — https://elixir.bootlin.com/linux/latest/source
> - Robert Love — *Linux Kernel Development* (3rd ed., Addison-Wesley)
> - Daniel P. Bovet & Marco Cesati — *Understanding the Linux Kernel* (O'Reilly)
> - LWN.net — Linux Weekly News (référence communauté noyau)
> - LKML — Linux Kernel Mailing List Archives
> - Linux man-pages 6.x — https://man7.org/linux/man-pages/
> - Ulrich Drepper — *What Every Programmer Should Know About Memory* (Red Hat)
> - ARM Architecture Reference Manual (ARMv8-A)
> - Intel 64 and IA-32 Architectures Software Developer's Manual Vol. 3
>
> **Environnement** : Linux 6.x (Ubuntu 24.04 LTS recommandé), VM ou bare metal
> **Prérequis** : Bases C, usage terminal Linux
> **Durée estimée** : 15 à 25 heures
> **Convention** : `$` = user · `#` = root · `→` = sortie · `💭` = réflexion · `🔬` = exercice

---

## TABLE DES MATIÈRES

```
PARTIE I — PHILOSOPHIE ET ARCHITECTURE GÉNÉRALE
  Chapitre 1  : Qu'est-ce qu'un noyau ?
  Chapitre 2  : Architecture x86-64 et modes CPU
  Chapitre 3  : Organisation du code source Linux

PARTIE II — MÉMOIRE ET ADRESSAGE
  Chapitre 4  : Mémoire virtuelle — la grande illusion
  Chapitre 5  : Tables de pages et MMU
  Chapitre 6  : Allocateurs mémoire du noyau

PARTIE III — PROCESSUS ET ORDONNANCEMENT
  Chapitre 7  : Structure task_struct — l'ADN d'un processus
  Chapitre 8  : Ordonnanceur CFS
  Chapitre 9  : Signaux et IPC

PARTIE IV — SYSTÈME DE FICHIERS ET VFS
  Chapitre 10 : Virtual File System — l'abstraction ultime
  Chapitre 11 : Inodes, dentries, superblocs
  Chapitre 12 : Appels système — la frontière

PARTIE V — DRIVERS ET MODULES
  Chapitre 13 : Écrire un module noyau
  Chapitre 14 : Character devices et /dev
  Chapitre 15 : Interruptions et gestion matérielle

PARTIE VI — OUTILS D'INSPECTION ET MANIPULATION
  Chapitre 16 : /proc et /sys — lire le noyau vivant
  Chapitre 17 : eBPF — observer sans modifier
  Chapitre 18 : Débogage noyau — kgdb, ftrace, perf

PARTIE VII — SÉCURITÉ ET DÉFENSE EN PROFONDEUR
  Chapitre 19 : Mécanismes de sécurité du noyau
  Chapitre 20 : Namespaces et cgroups

PARTIE VIII — CHALLENGES ET PROJETS
  Chapitre 21 : Projet — Module noyau complet
  Chapitre 22 : Challenge final
```

---

# ════════════════════════════════════════════════════════
# PARTIE I — PHILOSOPHIE ET ARCHITECTURE GÉNÉRALE
# ════════════════════════════════════════════════════════

---

## Chapitre 1 : Qu'est-ce qu'un Noyau ?

### 1.1 Le noyau — définition philosophique profonde

Un noyau (kernel) est la **couche logicielle qui fait le lien entre le matériel brut et les programmes des utilisateurs**. C'est le seul programme qui s'exécute avec tous les privilèges sur la machine. Il possède un accès direct à :

- La mémoire physique totale
- Tous les périphériques (disques, réseau, GPU...)
- Les registres du processeur
- Les instructions privilégiées (arrêt, gestion des interruptions...)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PILE LOGICIELLE LINUX                         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │    Applications utilisateur (bash, firefox, python...)   │   │
│  │                   (User Space)                           │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                              │  syscalls (interface contrôlée)  │
│  ╔══════════════════════════▼══════════════════════════════╗   │
│  ║                   NOYAU LINUX 6.x                        ║   │
│  ║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   ║   │
│  ║  │ Scheduler│ │  Memory  │ │   VFS    │ │  Network │   ║   │
│  ║  │   CFS    │ │ Manager  │ │  Layer   │ │  Stack   │   ║   │
│  ║  └──────────┘ └──────────┘ └──────────┘ └──────────┘   ║   │
│  ║  ┌──────────────────────────────────────────────────┐   ║   │
│  ║  │         Drivers (char, block, net, USB...)       │   ║   │
│  ║  └──────────────────────────────────────────────────┘   ║   │
│  ║  ┌──────────────────────────────────────────────────┐   ║   │
│  ║  │      Architecture (x86, ARM, RISC-V...)          │   ║   │
│  ║  └──────────────────────────────────────────────────┘   ║   │
│  ╚══════════════════════════╤══════════════════════════════╝   │
│                              │  accès matériel direct           │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Matériel : CPU, RAM, NIC, SATA, USB, GPU...            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Types de noyaux

```
MONOLITHIQUE (Linux, BSD) :
  → Tout le noyau s'exécute dans un seul espace d'adressage
  → Appels de fonctions internes directs (très rapide)
  → Un bug dans un driver peut planter tout le système
  → Modules chargés dynamiquement pour la flexibilité
  Linux = monolithique + modules

MICRO-NOYAU (Minix, QNX, L4) :
  → Seul l'essentiel dans le noyau (IPC, scheduler, MMU)
  → Drivers et services en espace utilisateur
  → Plus stable (bug driver ≠ crash noyau)
  → Plus lent (changements de contexte supplémentaires)

HYBRIDE (Windows NT, macOS XNU) :
  → Mélange des deux approches

UNIKERNEL (MirageOS, OSv) :
  → Application + noyau minimal compilés ensemble
  → Très léger, très rapide, très sécurisé
  → Pas de multi-processus
  → Populaire en cloud/containers 2026

EXOKERNEL (recherche MIT) :
  → Le noyau gère seulement la protection
  → Les applications gèrent leurs propres abstractions
```

### 1.3 Taille et complexité du noyau Linux

```bash
# Statistiques du noyau Linux 6.12 (2024)
$ git clone --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
$ find linux/ -name "*.c" -o -name "*.h" | xargs wc -l | tail -1
→ ~35,000,000 lignes de code

$ ls linux/
→ arch/          # Architectures (x86, arm, arm64, riscv...)
→ block/         # Sous-système I/O de blocs
→ crypto/        # Primitives cryptographiques
→ drivers/       # Drivers (50%+ du code total !)
→ fs/            # Systèmes de fichiers (ext4, btrfs, nfs...)
→ include/       # Headers partagés
→ init/          # Code d'initialisation (start_kernel)
→ ipc/           # Inter-Process Communication
→ kernel/        # Cœur : scheduler, signaux, timers...
→ lib/           # Bibliothèques internes
→ mm/            # Memory Management
→ net/           # Pile réseau
→ security/      # LSM (SELinux, AppArmor...)
→ sound/         # Sous-système audio

# Contributions : 15,000+ développeurs, 1000+ entreprises
# Red Hat, Intel, Samsung, Google, Meta, Microsoft...
```

---

## Chapitre 2 : Architecture x86-64 et Modes CPU

### 2.1 Les anneaux de protection (rings)

L'architecture x86 définit 4 niveaux de privilèges (rings 0-3). Linux n'en utilise que 2 :

```
x86 PROTECTION RINGS :

     ┌─────────────────────────┐
     │   Ring 0 — Kernel Mode  │  ← NOYAU LINUX
     │   Accès total           │    instructions privilégiées
     │   toutes instructions   │    accès registres CR0-CR4
     │   tous les registres    │    activation/désactivation IRQ
     └──────────┬──────────────┘
                │ syscall / sysret
     ┌──────────▼──────────────┐
     │   Ring 3 — User Mode    │  ← PROCESSUS UTILISATEUR
     │   Accès restreint       │    bash, firefox, python...
     │   pas d'I/O direct      │    GPF si instruction privilégiée
     │   pas de mémoire noyau  │
     └─────────────────────────┘

     Rings 1 et 2 : non utilisés par Linux
     (historiquement pour les OS/2, aujourd'hui inutilisés)

TRANSITION USER → KERNEL :
  Ancienne méthode : int 0x80 (interruption logicielle, lente)
  Méthode moderne  : syscall / sysret (instruction dédiée, rapide)
  
  Sur syscall :
  1. CPU passe Ring 3 → Ring 0
  2. Change de pile (RSP → kernel stack du processus)
  3. Sauvegarde les registres
  4. Appelle le gestionnaire du syscall
  5. sysret : revient en Ring 3
```

### 2.2 Registres CPU x86-64 — la vue noyau

```
REGISTRES GÉNÉRAUX (64 bits) :
  RAX  : valeur de retour des syscalls / résultat
  RBX  : registre préservé (callee-saved)
  RCX  : 4ème argument syscall / compteur
  RDX  : 3ème argument syscall
  RSI  : 2ème argument syscall
  RDI  : 1er argument syscall
  R8   : 5ème argument syscall
  R9   : 6ème argument syscall
  R10  : 4ème argument syscall (quand RAX,RDI,RSI,RDX,R10,R8,R9)
  R11  : temporaire (non préservé par syscall)
  R12-R15 : préservés (callee-saved)

REGISTRES SPÉCIAUX :
  RIP  : Instruction Pointer (adresse prochaine instruction)
  RSP  : Stack Pointer (sommet de pile)
  RBP  : Base Pointer (base du frame courant)
  RFLAGS : flags (ZF, CF, SF, OF, IF...)

REGISTRES DE SEGMENTS (héritage 16-bit, rôle limité en 64-bit) :
  CS   : Code Segment (bits 0-1 = CPL = Ring actuel !)
  SS   : Stack Segment
  DS,ES,FS,GS : Data Segments
  FS   : utilisé par Linux pour le thread-local storage (TLS)
  GS   : utilisé par Linux pour per-CPU data

REGISTRES DE CONTRÔLE (Ring 0 uniquement) :
  CR0  : bits de contrôle (PE=protected mode, PG=paging, WP=write protect)
  CR2  : adresse de la dernière page fault
  CR3  : adresse physique du répertoire de pages (PML4)
  CR4  : fonctionnalités étendues (PAE, PSE, OSFXSR...)
  CR8  : TPR (Task Priority Register) — gestion interruptions

MSR (Model-Specific Registers) :
  EFER (0xC0000080)    : Extended Feature Enable (LME=long mode)
  LSTAR (0xC0000082)   : adresse du gestionnaire syscall
  STAR (0xC0000081)    : segments pour syscall/sysret
  GS_BASE (0xC0000101) : base du segment GS
```

### 2.3 Inspecter les registres depuis l'espace utilisateur

```bash
# Voir les informations CPU
$ cat /proc/cpuinfo | head -30

# Capabilities du CPU (flags)
$ grep flags /proc/cpuinfo | head -1 | tr ' ' '\n' | sort

# Registres de contrôle (nécessite root)
$ cat /sys/devices/system/cpu/cpu0/topology/core_id

# Avec GDB : voir tous les registres d'un processus
$ gdb /bin/ls
(gdb) start
(gdb) info registers all
(gdb) x/20i $rip    # désassembler depuis RIP
(gdb) x/20gx $rsp   # voir la pile

# MSR avec msr-tools
$ sudo apt install msr-tools
$ sudo modprobe msr
$ sudo rdmsr 0xC0000082  # lire LSTAR (adresse syscall handler)
→ ffffffff81e00010       # adresse kernel de entry_SYSCALL_64

# Voir les ring transitions en temps réel avec perf
$ sudo perf stat -e cpu/mode-switches/ ls
```

---

## Chapitre 3 : Organisation du Code Source

### 3.1 Naviguer dans les sources

```bash
# Installer les outils de navigation
$ sudo apt install linux-source cscope ctags

# Décompresser les sources
$ ls /usr/src/
$ sudo tar -xf /usr/src/linux-source-*.tar.bz2 -C /tmp/

# OU cloner directement
$ git clone --depth 1 https://kernel.googlesource.com/pub/scm/linux/kernel/git/stable/linux.git

# Outils de navigation
$ make cscope      # base de données de navigation (dans les sources)
$ make tags        # tags ctags

# Avec cscope
$ cscope -d        # lancer l'interface
# Ctrl+\ s → chercher un symbole
# Ctrl+\ g → aller à la définition
# Ctrl+\ c → trouver les appelants

# Avec grep (le plus simple)
$ grep -r "struct task_struct" kernel/ --include="*.h" | head -5

# Avec Elixir (online) : https://elixir.bootlin.com/linux/latest/source
# Permet de naviguer et de suivre les références en ligne

# Trouver où est définie une structure
$ grep -r "^struct task_struct" include/ --include="*.h"
→ include/linux/sched.h:struct task_struct {
```

### 3.2 Compilation d'un noyau custom

```bash
# Prérequis
$ sudo apt install build-essential libncurses-dev bison flex \
  libssl-dev libelf-dev bc dwarves zstd

# Dans le répertoire source
$ cp /boot/config-$(uname -r) .config    # config actuelle comme base
$ make menuconfig                          # interface de configuration

# Paramètres importants à explorer dans menuconfig :
# General setup → Kernel compression mode
# Processor type and features → Processor family
# Memory Management support
# Kernel debugging → tout activer pour le développement

# Compilation (utiliser tous les cœurs)
$ make -j$(nproc) 2>&1 | tee build.log

# Installation
$ sudo make modules_install
$ sudo make install
$ sudo update-grub

# Vérifier le noyau actif
$ uname -r
→ 6.12.0-custom
```

---

# ════════════════════════════════════════════════════════
# PARTIE II — MÉMOIRE ET ADRESSAGE
# ════════════════════════════════════════════════════════

---

## Chapitre 4 : Mémoire Virtuelle — La Grande Illusion

### 4.1 Philosophie de la mémoire virtuelle

La mémoire virtuelle est l'une des idées les plus profondes de l'informatique moderne. Elle crée une **illusion** : chaque processus croit posséder l'intégralité de l'espace d'adressage de la machine, de façon privée et continue. En réalité :

```
RÉALITÉ vs ILLUSION :

  PROCESSUS A (voit)              RÉALITÉ PHYSIQUE
  ┌──────────────────┐            ┌────────────────────┐
  │ 0x0000...0000    │            │ Page physique 0x100│ ← processus A
  │ [texte prog A]   │  ──────→   │ Page physique 0x201│ ← processus B
  │ [données A]      │            │ Page physique 0x100│ ← processus A
  │ [pile A]         │            │     ...            │
  │ 0xFFFF...FFFF    │            │ Page physique 0x050│ ← partagée
  └──────────────────┘            └────────────────────┘

  Adresse virtuelle 0x400000 chez A ≠ 0x400000 chez B
  → Chaque processus a son propre mapping virtuel→physique

  Ce mapping est stocké dans les TABLES DE PAGES
  et géré par la MMU (Memory Management Unit) du CPU
```

### 4.2 Layout de la mémoire virtuelle x86-64

```
ESPACE D'ADRESSAGE VIRTUEL x86-64 (48 bits utilisés = 256 TB) :

Adresse 0xFFFFFFFFFFFFFFFF
│                             KERNEL SPACE (non accessible user)
│  0xFFFF888000000000         direct_map : mappage direct RAM physique
│  0xFFFFFFFF80000000         kernel text/data (vmlinux)
│  0xFFFFFFFF82000000         modules
│  0xFFFFFF0000000000         vmalloc area
│  0xFFFF000000000000         Début espace noyau
│                             ← TROU (adresses canoniques invalides)
│  0x00007FFFFFFFFFFF         Fin espace utilisateur
│                             USER SPACE (accessible user)
│  0x00007FFF00000000         Pile (grandit vers le bas)
│  0x...........              mmap area (bibliothèques, fichiers mappés)
│  0x0000555555555000         Heap (grandit vers le haut)
│  0x0000000000401000         Données/BSS
│  0x0000000000400000         Code (text segment)
│  0x0000000000000000         NULL (jamais mappé — protection SIGSEGV)

TROU CANONIQUE :
  Les adresses entre 0x0000800000000000 et 0xFFFF000000000000
  ne sont pas utilisées (bits 48-63 doivent reproduire le bit 47).
  Toute tentative d'accès = #GP (General Protection Fault).

ASLR (Address Space Layout Randomization) :
  Le noyau randomise les adresses de base au lancement :
  → mmap area base : +/- quelques TB aléatoires
  → Pile : +/- quelques MB
  → Code (PIE executables) : complètement randomisé
  Objectif : rendre les exploits de type ROP/ret2libc plus difficiles.
```

### 4.3 Inspecter la mémoire d'un processus

```bash
# Cartographie de la mémoire d'un processus
$ cat /proc/$$/maps
→ 55a3f1200000-55a3f1201000 r--p 00000000 08:01 12345  /usr/bin/bash
→ 55a3f1201000-55a3f12d0000 r-xp 00001000 08:01 12345  /usr/bin/bash
→ 7f8a2c000000-7f8a2c200000 rw-p 00000000 00:00 0      [heap]
→ 7ffe1a2b0000-7ffe1a2d0000 rw-p 00000000 00:00 0      [stack]
→ 7ffe1a3f5000-7ffe1a3f9000 r--p 00000000 00:00 0      [vvar]
→ 7ffe1a3f9000-7ffe1a3fb000 r-xp 00000000 00:00 0      [vdso]
→ ffffffffff600000-ffffffffff601000 --xp 00000000 00:00 0  [vsyscall]

# Format : adresse_début-adresse_fin permis offset dev inode fichier
# Permis : r=read w=write x=exec p=private s=shared

# Carte mémoire plus détaillée
$ cat /proc/$$/smaps | head -30
→ 55a3f1200000-55a3f1201000 r--p 00000000 08:01 12345 /usr/bin/bash
→ Size:                  4 kB
→ KernelPageSize:        4 kB
→ Rss:                   4 kB     ← pages réellement en RAM
→ Pss:                   4 kB     ← pages proportionnelles
→ Shared_Clean:          4 kB
→ Private_Dirty:         0 kB
→ Referenced:            4 kB
→ Anonymous:             0 kB

# Utilisation mémoire globale
$ cat /proc/meminfo
→ MemTotal:       16384000 kB
→ MemFree:         4096000 kB
→ MemAvailable:    8000000 kB
→ Buffers:          512000 kB
→ Cached:          4096000 kB
→ SwapCached:           0 kB
→ AnonPages:       2048000 kB
→ Mapped:          1024000 kB
→ KernelStack:       32768 kB
→ PageTables:        32000 kB
→ Slab:             512000 kB  ← allocateur slab du noyau

# Statistiques détaillées de la mémoire noyau
$ sudo cat /proc/slabinfo | head -20
$ sudo slabtop -o              # vue temps réel des slabs
```

---

## Chapitre 5 : Tables de Pages et MMU

### 5.1 La traduction d'adresse x86-64 à 4 niveaux

```
TRADUCTION ADRESSE VIRTUELLE → PHYSIQUE (4-level paging x86-64) :

Adresse virtuelle : 48 bits utilisés
  ┌──────┬──────────┬──────────┬──────────┬──────────┬────────────┐
  │ sign │  PGD idx │  PUD idx │  PMD idx │  PTE idx │   offset   │
  │ 16b  │    9b    │    9b    │    9b    │    9b    │    12b     │
  └──────┴──────────┴──────────┴──────────┴──────────┴────────────┘
          [47:39]     [38:30]    [29:21]    [20:12]     [11:0]

Processus de traduction :
  1. CR3 → adresse physique de PGD (Page Global Directory)
  2. PGD[bits 47:39] → adresse PUD (Page Upper Directory)
  3. PUD[bits 38:30] → adresse PMD (Page Middle Directory)
  4. PMD[bits 29:21] → adresse PTE (Page Table Entry)
  5. PTE[bits 20:12] → adresse physique de la page
  6. adresse_physique + offset → octet final

  Total : 4 accès mémoire pour chaque accès mémoire !
  → TLB (Translation Lookaside Buffer) cache les translations récentes
  → Cache de ~1000-2000 entrées dans le CPU
  → TLB miss = très coûteux (4 accès mémoire supplémentaires)

ENTRÉE DE TABLE DE PAGES (PTE) — 64 bits :
  Bit 0  : P    (Present) — page présente en RAM
  Bit 1  : RW   (Read/Write) — écriture autorisée
  Bit 2  : US   (User/Supervisor) — accessible en Ring 3
  Bit 3  : PWT  (Page Write Through)
  Bit 4  : PCD  (Page Cache Disable)
  Bit 5  : A    (Accessed) — mis à 1 par MMU si accès
  Bit 6  : D    (Dirty) — mis à 1 par MMU si écrit
  Bit 7  : PAT/PS (Page Size pour hugepages)
  Bits 12-51 : adresse physique de la page (4KB alignée)
  Bit 63 : NX  (No-Execute) — bit XD/NX SMEP

5-LEVEL PAGING (Linux 6.x, x86-64 avec LA57) :
  Ajoute un niveau P4D entre PGD et PUD
  → espace d'adressage : 57 bits = 128 PB (pétaoctets)
  → Activé via CONFIG_X86_5LEVEL
```

### 5.2 Inspecter les tables de pages

```bash
# Voir les tables de pages d'un processus (nécessite root)
$ sudo cat /proc/$$/pagemap | xxd | head -20
# Chaque entrée = 8 bytes correspondant à une page virtuelle
# Bit 63 = page présente, bits 0-54 = page frame number (PFN)

# Script Python pour décoder pagemap
cat << 'EOF' > /tmp/read_pagemap.py
#!/usr/bin/env python3
"""Lire les tables de pages d'un processus via /proc/PID/pagemap"""

import struct
import sys
import os

def read_page_mapping(pid: int, vaddr: int) -> dict:
    """Retourne les informations de mapping pour une adresse virtuelle."""
    page_size = 4096
    page_num = vaddr // page_size

    with open(f"/proc/{pid}/pagemap", "rb") as f:
        f.seek(page_num * 8)
        data = f.read(8)

    if len(data) < 8:
        return {"present": False}

    entry = struct.unpack("<Q", data)[0]
    present = bool(entry >> 63)
    swapped = bool((entry >> 62) & 1)
    pfn = entry & ((1 << 55) - 1)

    return {
        "virtual_addr": hex(vaddr),
        "present": present,
        "swapped": swapped,
        "pfn": pfn,
        "physical_addr": hex(pfn * page_size + (vaddr % page_size)) if present else None,
    }

if __name__ == "__main__":
    pid = int(sys.argv[1]) if len(sys.argv) > 1 else os.getpid()
    # Lire les maps pour trouver des adresses valides
    with open(f"/proc/{pid}/maps") as f:
        for line in f:
            parts = line.split()
            start = int(parts[0].split('-')[0], 16)
            info = read_page_mapping(pid, start)
            if info["present"]:
                print(f"VA: {info['virtual_addr']} → PA: {info['physical_addr']}")
                if info['pfn']:
                    break
EOF
$ sudo python3 /tmp/read_pagemap.py $$

# Statistiques TLB
$ sudo perf stat -e dTLB-load-misses,dTLB-store-misses,iTLB-load-misses ls
→ Performance counter stats for 'ls':
→         234 dTLB-load-misses
→          12 dTLB-store-misses
→          78 iTLB-load-misses

# Huge pages
$ cat /proc/meminfo | grep -i huge
→ HugePages_Total:       0
→ Hugepagesize:       2048 kB  (2MB huge pages)

$ grep -r "transparent_hugepage" /sys/kernel/mm/transparent_hugepage/
$ cat /sys/kernel/mm/transparent_hugepage/enabled
→ always [madvise] never
```

---

## Chapitre 6 : Allocateurs Mémoire du Noyau

### 6.1 Les allocateurs en couches

```
HIÉRARCHIE DES ALLOCATEURS NOYAU :

  kmalloc(size, GFP_KERNEL)      ← allocation générique (objets <quelques pages)
       │
       ▼
  SLAB / SLUB / SLOB allocator   ← gestion des caches d'objets
       │
       ▼
  Buddy allocator (page allocator) ← gestion par puissances de 2 (pages physiques)
       │
       ▼
  MÉMOIRE PHYSIQUE (pages 4KB)

vmalloc(size)                    ← allocation contiguë virtuellement (pas physiquement)
  → Pour de grandes zones dont la contiguïté physique n'est pas requise
  → Plus lent (tables de pages spéciales)
  → Utilisé par les modules noyau (code)

get_free_pages(GFP_KERNEL, order) ← allocation de 2^order pages physiques contiguës
  → order=0 : 4 KB
  → order=1 : 8 KB
  → order=10 : 4 MB
```

### 6.2 Le Buddy Allocator

```
PRINCIPE DU BUDDY SYSTEM :
  La mémoire est gérée par blocs de taille 2^n pages.
  Chaque bloc a un "buddy" (copain) de la même taille.

  Allocation de 16 KB (4 pages) :
  → Cherche un bloc libre de 4 pages
  → Si non disponible, split un bloc de 8 pages
  → Retourne 4 pages, place les 4 autres dans la liste libre

  Libération :
  → Si le buddy est aussi libre → fusionner en 8 pages
  → Si le buddy du bloc de 8 est libre → fusionner en 16 pages
  → etc. (coalescing)

  Avantage : pas de fragmentation externe
  Inconvénient : fragmentation interne (allouer 5 pages → donne 8)

INSPECTION :
$ cat /proc/buddyinfo
→ Node 0, zone    DMA     1  0  0  0  0  0  1  0  0  1  3
→ Node 0, zone  DMA32   250 127  87  42  17   9   3   1   1   0  0
→ Node 0, zone   Normal 1024 512 256  128  64  32  16   8   4   2  1
                           ↑   ↑   ↑   ↑   ↑
                           │   │   │   │   └── order 4 : blocs 16 pages disponibles
                           │   │   │   └───── order 3 : blocs 8 pages
                           │   │   └───────── order 2 : blocs 4 pages
                           │   └───────────── order 1 : blocs 2 pages
                           └───────────────── order 0 : pages simples disponibles
```

### 6.3 Le SLUB Allocator — l'allocateur moderne

```
PROBLÈME DU BUDDY POUR LES PETITS OBJETS :
  Allouer une structure task_struct (~9 KB) avec le buddy
  → gaspillage : le buddy allouerait 16 KB (2^14 bytes)
  → recréer la structure à chaque fork() = coûteux en initialisation

SOLUTION SLAB/SLUB :
  Maintenir des CACHES d'objets pré-initialisés.
  
  struct kmem_cache {
    // chaque cache correspond à un type d'objet
    const char *name;         // "task_struct", "inode_cache"...
    size_t object_size;       // taille de chaque objet
    size_t size;              // taille avec alignement
    unsigned int align;       // contrainte d'alignement
    // ... pools de pages, statistiques...
  };

  Opération :
  1. Allouer de grandes pages via le buddy
  2. Découper en objects de taille fixe
  3. Maintenir des listes free/partial/full
  4. kmalloc() = piocher dans le cache approprié (O(1))
  5. kfree() = remettre l'objet dans le cache (pas de retour au buddy)
```

```bash
# Voir tous les caches SLUB actifs
$ sudo cat /proc/slabinfo
→ # name            <active_objs> <num_objs> <objsize> <objperslab> <pagesperslab>
→ task_struct            512       512      9152         4          9
→ mm_struct              128       128      1408         5          2
→ files_cache            256       256       832         5          1
→ inode_cache          2048      2048       704         5          1
→ dentry               8192      8192       192        16          1

# Infos détaillées sur un cache
$ sudo cat /sys/kernel/slab/task_struct/object_size
→ 9152
$ sudo cat /sys/kernel/slab/task_struct/reclaim_account
$ sudo cat /sys/kernel/slab/task_struct/align

# Statistiques temps réel
$ sudo slabtop
# Ou avec vmstat
$ vmstat -m | head -20

# Avec eBPF : tracer les allocations kmalloc
$ sudo bpftrace -e 'kprobe:__kmalloc { @sizes[arg0] = count(); }'
```

---

# ════════════════════════════════════════════════════════
# PARTIE III — PROCESSUS ET ORDONNANCEMENT
# ════════════════════════════════════════════════════════

---

## Chapitre 7 : task_struct — L'ADN d'un Processus

### 7.1 La structure fondamentale

`task_struct` est **la** structure centrale du noyau Linux. Chaque processus ou thread possède une instance de cette structure. Elle contient tout ce que le noyau sait sur une tâche.

```c
// include/linux/sched.h — version simplifiée pédagogique
// La vraie structure fait ~700 lignes

struct task_struct {
    // ── ÉTAT DE LA TÂCHE ──────────────────────────────────────
    volatile long         state;          // TASK_RUNNING, TASK_INTERRUPTIBLE...
    void                 *stack;          // pile noyau de la tâche (~16 KB)
    refcount_t            usage;          // compteur de références
    unsigned int          flags;          // PF_KTHREAD, PF_EXITING...
    int                   exit_code;      // code de retour
    int                   exit_signal;    // signal à envoyer au parent

    // ── IDENTIFIANTS ──────────────────────────────────────────
    pid_t                 pid;            // Process ID
    pid_t                 tgid;           // Thread Group ID (= PID du leader)
    char                  comm[TASK_COMM_LEN]; // nom (16 octets max)

    // ── HIÉRARCHIE ────────────────────────────────────────────
    struct task_struct   *real_parent;    // parent biologique
    struct task_struct   *parent;         // parent SIGCHLD
    struct list_head      children;       // liste des enfants
    struct list_head      sibling;        // chaîne des frères/sœurs
    struct task_struct   *group_leader;   // leader du thread group

    // ── ORDONNANCEMENT ────────────────────────────────────────
    int                   prio;           // priorité dynamique
    int                   static_prio;    // priorité statique (nice)
    int                   normal_prio;    // priorité normale
    unsigned int          rt_priority;    // priorité temps réel (0-99)
    const struct sched_class *sched_class; // CFS, RT, IDLE...
    struct sched_entity   se;             // entité CFS (vruntime...)
    unsigned int          policy;         // SCHED_NORMAL, SCHED_FIFO...

    // ── MÉMOIRE ──────────────────────────────────────────────
    struct mm_struct      *mm;            // espace mémoire (NULL si kthread)
    struct mm_struct      *active_mm;     // mm actif (peut ≠ mm pour kthreads)

    // ── FICHIERS ──────────────────────────────────────────────
    struct fs_struct      *fs;            // répertoire courant, umask
    struct files_struct   *files;         // table des descripteurs de fichiers
    struct nsproxy        *nsproxy;       // namespaces (mount, net, pid...)

    // ── SIGNAUX ──────────────────────────────────────────────
    struct signal_struct  *signal;        // gestionnaire de signaux du groupe
    struct sighand_struct *sighand;       // gestionnaires des signaux
    sigset_t              blocked;        // masque des signaux bloqués
    struct sigpending     pending;        // signaux en attente

    // ── CREDENTIALS (SÉCURITÉ) ───────────────────────────────
    const struct cred     *real_cred;     // uid/gid réels
    const struct cred     *cred;          // uid/gid effectifs

    // ── TIMING ───────────────────────────────────────────────
    u64                   utime;          // temps CPU en user space
    u64                   stime;          // temps CPU en kernel space
    u64                   start_time;     // timestamp de création
    struct timespec64     start_boottime;

    // ── LISTE DES TÂCHES ─────────────────────────────────────
    struct list_head      tasks;          // chaîne de tous les processus
    // init_task (PID 0) est la tête de cette liste circulaire

    // ── CGROUPS ──────────────────────────────────────────────
    struct css_set __rcu  *cgroups;       // appartenance aux cgroups
    struct list_head       cg_list;
};
```

### 7.2 États d'un processus

```
MACHINE D'ÉTATS DES TÂCHES :

              fork()
              ────→  TASK_RUNNING (runnable)
                           │
              ────────────→│←────────────
              │            │             │
         schedule()    schedule()    wakeup()
              │            │             │
              ▼            ▼             │
        En exécution   TASK_INTERRUPTIBLE  ← attente signal possible
        (sur CPU)      TASK_UNINTERRUPTIBLE ← attente NON interruptible (I/O)
                       TASK_KILLABLE      ← interruptible par signal fatal seulement
                            │
                       exit()│
                            ▼
                       TASK_ZOMBIE      ← terminated, parent n'a pas encore lu
                            │
                       wait()│ (parent)
                            ▼
                       Disparition totale

TASK_UNINTERRUPTIBLE :
  État D dans ps/top (diskwait, uninterruptible sleep)
  Un processus en état D NE PEUT PAS être tué (même kill -9)
  Typiquement : attente I/O disque, NFS...
  Un processus bloqué en D pendant longtemps = anomalie système
```

### 7.3 Inspecter task_struct depuis l'espace utilisateur

```bash
# La fenêtre sur task_struct : /proc/PID/status
$ cat /proc/$$/status
→ Name:    bash
→ Umask:   0022
→ State:   S (sleeping)
→ Tgid:    12345        # Thread Group ID
→ Ngid:    0
→ Pid:     12345
→ PPid:    12344        # Parent PID
→ TracerPid: 0          # PID du débogueur (0 = pas tracé)
→ Uid:    1000 1000 1000 1000   # real euid suid fsuid
→ Gid:    1000 1000 1000 1000
→ FDSize:   256         # taille table FD
→ Groups:  27 100 1000  # groupes supplémentaires
→ VmPeak:  123456 kB    # pic mémoire virtuelle
→ VmSize:   98765 kB    # mémoire virtuelle actuelle
→ VmRSS:    12345 kB    # mémoire physique réelle
→ VmStk:    8192 kB     # taille de la pile
→ Threads:  1           # nombre de threads
→ SigBlk:  0000000000000000  # signaux bloqués (bitmask)
→ SigIgn:  0000000000000001  # signaux ignorés
→ SigCgt:  00000001f8014a03  # signaux catchés
→ CapInh:  0000000000000000  # capabilities héritées
→ CapPrm:  0000000000000000  # capabilities permises
→ CapEff:  0000000000000000  # capabilities effectives

# Voir la liste des processus dans le noyau
$ cat /proc/$$/wchan       # fonction noyau où le processus attend
→ do_wait

# Timeline des processus (du plus ancien au plus récent)
$ ps -eo pid,ppid,lstart,comm --sort=lstart | head -20

# Arbre des processus
$ pstree -p | head -20

# Accéder à la pile noyau d'un processus (si CONFIG_STACKTRACE)
$ sudo cat /proc/$$/wchan
$ sudo cat /sys/kernel/debug/tracing/trace
```

---

## Chapitre 8 : Ordonnanceur CFS

### 8.1 Completely Fair Scheduler — philosophie

```
OBJECTIF DU CFS (Con Kolivas / Ingo Molnár, 2007) :
  Traiter tous les processus équitablement.
  Un processus ne doit pas attendre le CPU plus longtemps
  qu'un autre de même priorité.

CONCEPT CLEF : vruntime (virtual runtime)
  Chaque tâche accumule un vruntime = temps CPU utilisé * pondération
  L'ordonnanceur sélectionne TOUJOURS la tâche avec le plus petit vruntime.

  Pondération (nice) :
  nice -20 (priorité max) : pondération = 1/3 des autres
  nice   0 (par défaut)   : pondération = 1 (neutre)
  nice +19 (priorité min) : pondération = 3x les autres
  → nice -20 accumule le vruntime 3x moins vite → obtient 3x plus de CPU

RED-BLACK TREE :
  Les tâches actives sont stockées dans un arbre rouge-noir
  trié par vruntime.
  → La tâche à gauche (vruntime min) est toujours la suivante.
  → O(log n) pour l'insertion/suppression
  → O(1) pour trouver la prochaine tâche (leftmost node cached)

  struct sched_entity {
    struct load_weight load;
    struct rb_node run_node;    // nœud dans le rbtree
    u64 exec_start;             // timestamp début d'exécution
    u64 sum_exec_runtime;       // temps total d'exécution
    u64 vruntime;               // ← LA valeur clé
    u64 prev_sum_exec_runtime;
  };
```

### 8.2 Classes d'ordonnancement

```
SCHED_DEADLINE > SCHED_FIFO/SCHED_RR > SCHED_NORMAL/SCHED_BATCH/SCHED_IDLE

SCHED_NORMAL (CFS) :
  → Processus classiques
  → Paramètre : nice (-20 à +19)
  → Préemptible

SCHED_BATCH (CFS) :
  → Tâches batch (calcul intensif)
  → Tolère une plus grande latence

SCHED_IDLE (CFS) :
  → Priorité ultra-basse
  → Exécuté seulement si rien d'autre

SCHED_FIFO (RT) :
  → Temps réel, premier entré premier servi
  → Priorité RT : 1-99 (99 = max)
  → Préemption seulement par tâche RT plus prioritaire
  → ⚠️ Un SCHED_FIFO avec boucle infinie = CPU monopolisé

SCHED_RR (RT) :
  → Temps réel avec quantum de temps
  → Rotation entre tâches RT de même priorité

SCHED_DEADLINE (EDF) :
  → Earliest Deadline First
  → Paramètres : runtime, deadline, period
  → Garantit le deadline si (Σ runtime_i/period_i ≤ 1)
```

```bash
# Voir l'ordonnanceur d'un processus
$ chrt -p $$
→ pid 12345's current scheduling policy: SCHED_OTHER
→ pid 12345's current scheduling priority: 0

# Modifier la politique d'ordonnancement
$ sudo chrt -f -p 50 $$      # SCHED_FIFO priorité 50
$ sudo chrt -r -p 50 $$      # SCHED_RR priorité 50
$ nice -n -5 commande        # SCHED_NORMAL avec nice -5

# Voir les statistiques CFS
$ cat /proc/$$/sched
→ bash (12345, #threads: 1)
→ -------------------------------------------------------------------
→ se.exec_start                    : 1234567890.123456
→ se.vruntime                      :       123456.789012
→ se.sum_exec_runtime              :          456.789012
→ nr_switches                      :              12345
→ nr_voluntary_switches            :              12000
→ nr_involuntary_switches          :                345
→ se.load.weight                   :               1024
→ policy                           :                  0  # SCHED_NORMAL

# Perf : voir qui utilise le CPU
$ sudo perf top
$ sudo perf record -ag sleep 10
$ sudo perf report

# Latence d'ordonnancement
$ sudo apt install rt-tests
$ sudo cyclictest -t1 -p 80 -n -i 10000 -l 10000
```

---

# ════════════════════════════════════════════════════════
# PARTIE IV — SYSTÈME DE FICHIERS ET VFS
# ════════════════════════════════════════════════════════

---

## Chapitre 10 : Virtual File System — L'Abstraction Ultime

### 10.1 Philosophie du VFS

Le VFS est l'une des abstractions les plus élégantes du noyau Linux. Il permet à une seule interface unifiée (`open()`, `read()`, `write()`...) de fonctionner sur :

```
ext4, btrfs, xfs, ntfs, fat32        → systèmes de fichiers disque
tmpfs, ramfs, shmfs                   → systèmes en mémoire
procfs (/proc), sysfs (/sys), debugfs → interfaces noyau pseudo-FS
nfs, cifs, sshfs                      → fichiers réseau
pipe, socket, /dev/null, /dev/zero    → périphériques et IPC
```

```
ARCHITECTURE VFS :

Application : open("/etc/passwd", O_RDONLY)
    │
    ▼ syscall sys_open
VFS Layer :
    ├── Résoudre le chemin (/etc/passwd)
    │   └── dentry cache (dcache) ← cache de résolution de chemins
    │
    ├── Trouver l'inode
    │   └── inode cache ← cache des métadonnées de fichiers
    │
    └── Appeler les opérations du FS concret
        │
        ├── ext4_file_operations.open()  → si fichier ext4
        ├── proc_file_operations.open()  → si fichier /proc
        ├── nfs_file_operations.open()   → si NFS
        └── ... (chaque FS implémente la même interface)
```

### 10.2 Les structures fondamentales du VFS

```c
// Les 4 objets fondamentaux du VFS

// 1. SUPERBLOCK — représente un système de fichiers monté
struct super_block {
    dev_t                  s_dev;       // numéro de périphérique
    unsigned long          s_blocksize; // taille des blocs (ex: 4096)
    unsigned char          s_blocksize_bits;
    loff_t                 s_maxbytes;  // taille max d'un fichier
    struct file_system_type *s_type;    // type (ext4, nfs...)
    const struct super_operations *s_op; // alloc_inode, sync_fs...
    struct dentry          *s_root;     // dentry racine
    struct list_head       s_list;      // liste de tous les superblocks
    // ...
};

// 2. INODE — représente un fichier (métadonnées)
struct inode {
    umode_t                i_mode;      // type + permissions (rwxrwxrwx)
    unsigned short         i_opflags;
    kuid_t                 i_uid;       // propriétaire
    kgid_t                 i_gid;       // groupe
    unsigned int           i_flags;
    ino_t                  i_ino;       // numéro d'inode
    dev_t                  i_rdev;      // pour les devices
    loff_t                 i_size;      // taille en bytes
    struct timespec64      i_atime;     // dernier accès
    struct timespec64      i_mtime;     // dernière modification
    struct timespec64      i_ctime;     // dernier changement de métadonnées
    unsigned long          i_nlink;     // nombre de hard links
    blkcnt_t               i_blocks;    // blocs 512-byte alloués
    const struct inode_operations *i_op;  // create, link, mkdir...
    const struct file_operations  *i_fop; // open, read, write...
    struct address_space   *i_mapping;  // cache des pages du fichier
};

// 3. DENTRY — représente une entrée de répertoire (chemin)
struct dentry {
    unsigned int           d_flags;
    struct qstr            d_name;      // le nom du fichier
    struct inode           *d_inode;    // l'inode associé (NULL si négatif)
    struct dentry          *d_parent;   // dentry du répertoire parent
    struct list_head       d_child;     // entrées dans le parent
    struct list_head       d_subdirs;   // sous-répertoires
    const struct dentry_operations *d_op;
    struct super_block     *d_sb;       // superblock du FS
    // Dentries négatives : chemin "non-existant" en cache (rapide ENOENT)
};

// 4. FILE — représente un fichier ouvert (par processus)
struct file {
    struct path            f_path;      // dentry + mount point
    struct inode           *f_inode;    // inode du fichier
    const struct file_operations *f_op; // opérations
    loff_t                 f_pos;       // position courante (offset)
    unsigned int           f_flags;     // O_RDONLY, O_WRONLY...
    fmode_t                f_mode;      // FMODE_READ, FMODE_WRITE
    struct task_struct     *f_owner;    // pour signaux async
    u64                    f_version;
    // ...
};
```

### 10.3 Explorer le VFS en direct

```bash
# Inodes
$ stat /etc/passwd
→ File: /etc/passwd
→ Size: 2456          Blocks: 8          IO Block: 4096   regular file
→ Device: 802h/2050d  Inode: 131073      Links: 1
→ Access: (0644/-rw-r--r--)  Uid: (0/root)  Gid: (0/root)
→ Access: 2024-01-10 08:00:00.000000000 +0100
→ Modify: 2024-01-08 12:00:00.000000000 +0100
→ Change: 2024-01-08 12:00:00.000000000 +0100

# Numéro d'inode
$ ls -i /etc/passwd
→ 131073 /etc/passwd

# Hard links (même inode)
$ ln /tmp/original /tmp/hardlink
$ ls -i /tmp/original /tmp/hardlink
→ 999999 /tmp/hardlink
→ 999999 /tmp/original   ← même inode !

# Voir les superblocks montés
$ cat /proc/mounts
→ sysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
→ proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
→ devtmpfs /dev devtmpfs rw,nosuid,size=1024k,nr_inodes=4096 0 0
→ /dev/sda1 / ext4 rw,relatime,errors=remount-ro 0 0

# Statistiques dentry cache
$ sudo sysctl -a | grep dentry
$ cat /proc/sys/fs/dentry-state
→ 125432  120000  45  0  0  0
#  count  unused  age_limit  dummy dummy dummy

# Statistiques inode cache
$ cat /proc/sys/fs/inode-state
→ 45231  2341  0  0  0  0  0
#  count  unused  dummy...

# Vider les caches (attention en production !)
$ sudo echo 3 > /proc/sys/vm/drop_caches
# 1 = page cache, 2 = dentries+inodes, 3 = tout

# debugfs — inspecter un FS ext4 en détail
$ sudo debugfs /dev/sda1
debugfs> stat <131073>          # infos d'un inode
debugfs> dump <131073> /tmp/out # extraire un fichier par inode
debugfs> ls /etc/               # lister un répertoire
debugfs> show_super_stats       # statistiques du superbloc
```

---

## Chapitre 12 : Appels Système — La Frontière

### 12.1 Anatomie d'un appel système

```
DÉFINITION :
  Un syscall est le seul mécanisme pour passer du Ring 3 au Ring 0
  de façon contrôlée. C'est la frontière entre user space et kernel.

TABLES DES SYSCALLS x86-64 :
  Chaque syscall a un numéro (RAX lors de l'appel).
  La table est dans arch/x86/entry/syscalls/syscall_64.tbl

  0   read
  1   write
  2   open
  3   close
  39  getpid
  57  fork
  59  execve
  60  exit
  ...
  449 futex_waitv (Linux 5.16)

FLUX D'UN SYSCALL read(fd, buf, count) :

User space :
  1. Placer les arguments : RDI=fd, RSI=buf_ptr, RDX=count
  2. Placer le numéro : RAX=0 (read)
  3. Exécuter l'instruction SYSCALL

CPU (automatique) :
  4. Sauvegarder RIP, RFLAGS, RSP
  5. Charger RIP depuis MSR LSTAR (entry_SYSCALL_64)
  6. Passer Ring 3 → Ring 0
  7. Charger la pile noyau (depuis tss.rsp0)

Kernel (entry_SYSCALL_64 dans arch/x86/entry/entry_64.S) :
  8. Sauvegarder tous les registres user (struct pt_regs sur la pile)
  9. Appeler do_syscall_64(nr, regs)
 10. Récupérer la fonction depuis sys_call_table[nr]
 11. Appeler ksys_read(fd, buf, count)
 12. Placer la valeur de retour dans RAX
 13. Restaurer les registres user

CPU (SYSRET) :
 14. Restaurer RIP, RFLAGS, RSP
 15. Passer Ring 0 → Ring 3

User space :
 16. Reprendre après SYSCALL avec retour dans RAX
```

### 12.2 Tracer les syscalls

```bash
# strace — trace tous les syscalls d'un processus
$ strace ls
→ execve("/usr/bin/ls", ["ls"], 0x... /* env */) = 0
→ brk(NULL) = 0x55a3f1400000
→ mmap(NULL, 8192, PROT_READ|PROT_WRITE, ...) = 0x7f...
→ openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
→ ...
→ getdents64(3, 0x55a3f1402560, 32768) = 112
→ write(1, "bin etc home tmp\n", 17) = 17
→ close(1) = 0
→ close(2) = 0
→ exit_group(0) = ?

# Compter les syscalls
$ strace -c ls 2>&1
→ % time     seconds  usecs/call     calls    errors syscall
→ ─────── ──────────  ──────────  ──────── ─────── ──────────
→   36.11   0.000325           8        40          read
→   28.57   0.000257          12        21           3 openat
→   15.18   0.000137           5        25          mmap
→    8.93   0.000080           5        16          close

# Filtrer par type de syscall
$ strace -e trace=network curl google.com 2>&1 | head -20
$ strace -e trace=file ls 2>&1 | head -20

# ltrace — trace les appels de bibliothèques
$ ltrace ls 2>&1 | head -20

# Avec perf : syscalls les plus fréquents système-wide
$ sudo perf stat -e 'syscalls:sys_enter_*' -a sleep 5 2>&1 | sort -rn | head

# Avec eBPF : tracer read() en temps réel
$ sudo bpftrace -e '
tracepoint:syscalls:sys_enter_read {
    printf("PID %d lisant fd=%d count=%d\n", pid, args->fd, args->count);
}'
```

### 🔬 Exercice 12.1 — Implémenter un appel système

```c
/* Ajout d'un syscall personnalisé dans le noyau Linux
 * Fichier : kernel/my_syscall.c
 * Ce syscall retourne le nombre de processus actifs
 */

#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/sched.h>

SYSCALL_DEFINE0(count_processes)
{
    struct task_struct *task;
    int count = 0;

    /* Parcourir tous les processus */
    for_each_process(task) {
        count++;
    }

    pr_info("count_processes: found %d processes\n", count);
    return count;
}
```

```c
/* Test depuis user space */
#include <stdio.h>
#include <sys/syscall.h>
#include <unistd.h>

/* Numéro à ajouter dans syscall_64.tbl */
#define __NR_count_processes 462

int main(void)
{
    long count = syscall(__NR_count_processes);
    printf("Nombre de processus : %ld\n", count);
    return 0;
}
```

```bash
# Ajouter dans arch/x86/entry/syscalls/syscall_64.tbl :
# 462  common  count_processes  sys_count_processes

# Ajouter dans include/linux/syscalls.h :
# asmlinkage long sys_count_processes(void);

# Ajouter kernel/my_syscall.c aux objets Makefile
# Recompiler le noyau et tester
```

---

# ════════════════════════════════════════════════════════
# PARTIE V — DRIVERS ET MODULES
# ════════════════════════════════════════════════════════

---

## Chapitre 13 : Écrire un Module Noyau

### 13.1 Anatomie d'un module

```c
/* hello_module.c — Module noyau minimal
 * Compilation : make -C /lib/modules/$(uname -r)/build M=$(pwd) modules
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Étudiant Linux");
MODULE_DESCRIPTION("Module pédagogique : Hello World");
MODULE_VERSION("1.0");

static int __init hello_init(void)
{
    printk(KERN_INFO "Hello, Noyau ! Module chargé\n");
    /* KERN_EMERG, KERN_ALERT, KERN_CRIT, KERN_ERR,
       KERN_WARNING, KERN_NOTICE, KERN_INFO, KERN_DEBUG */
    pr_info("Module hello version 1.0 chargé avec PID %d\n",
            current->pid);
    return 0;  /* 0 = succès, <0 = erreur */
}

static void __exit hello_exit(void)
{
    printk(KERN_INFO "Goodbye, Noyau ! Module déchargé\n");
}

module_init(hello_init);
module_exit(hello_exit);
```

```makefile
# Makefile pour module noyau
obj-m += hello_module.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

```bash
# Compilation et chargement
$ make
$ sudo insmod hello_module.ko
$ dmesg | tail -5
→ [12345.678901] Hello, Noyau ! Module chargé
→ [12345.678902] Module hello version 1.0 chargé avec PID 1234

# Informations sur le module
$ lsmod | grep hello
→ hello_module          16384  0

$ modinfo hello_module.ko
→ filename:       /home/user/hello_module.ko
→ version:        1.0
→ description:    Module pédagogique : Hello World
→ author:         Étudiant Linux
→ license:        GPL

# Déchargement
$ sudo rmmod hello_module
$ dmesg | tail -2
→ [12347.000000] Goodbye, Noyau ! Module déchargé
```

### 13.2 Module avec paramètres

```c
/* param_module.c — Module avec paramètres et /proc */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/uaccess.h>
#include <linux/slab.h>

#define PROC_NAME "my_module"
#define MAX_MSG_LEN 256

/* Paramètre du module (passé avec insmod param_module.ko message="bonjour") */
static char *message = "Valeur par défaut";
static int counter = 0;

module_param(message, charp, S_IRUGO);
MODULE_PARM_DESC(message, "Message à afficher dans /proc");

/* Fichier /proc/my_module */
static int proc_show(struct seq_file *m, void *v)
{
    seq_printf(m, "Message   : %s\n", message);
    seq_printf(m, "Compteur  : %d\n", counter++);
    seq_printf(m, "Noyau ver : %s\n", UTS_RELEASE);
    return 0;
}

static int proc_open(struct inode *inode, struct file *file)
{
    return single_open(file, proc_show, NULL);
}

/* Écriture dans /proc/my_module */
static ssize_t proc_write(struct file *file, const char __user *buf,
                           size_t count, loff_t *ppos)
{
    char *kbuf;

    if (count > MAX_MSG_LEN)
        return -EINVAL;

    kbuf = kmalloc(count + 1, GFP_KERNEL);
    if (!kbuf)
        return -ENOMEM;

    if (copy_from_user(kbuf, buf, count)) {
        kfree(kbuf);
        return -EFAULT;
    }
    kbuf[count] = '\0';

    pr_info("Message reçu : %s\n", kbuf);
    kfree(kbuf);
    return count;
}

/* Interface /proc */
static const struct proc_ops proc_fops = {
    .proc_open    = proc_open,
    .proc_read    = seq_read,
    .proc_write   = proc_write,
    .proc_lseek   = seq_lseek,
    .proc_release = single_release,
};

static struct proc_dir_entry *proc_entry;

static int __init param_init(void)
{
    proc_entry = proc_create(PROC_NAME, 0666, NULL, &proc_fops);
    if (!proc_entry) {
        pr_err("Échec création /proc/%s\n", PROC_NAME);
        return -ENOMEM;
    }
    pr_info("Module paramétré chargé. /proc/%s créé\n", PROC_NAME);
    return 0;
}

static void __exit param_exit(void)
{
    proc_remove(proc_entry);
    pr_info("Module déchargé, /proc/%s supprimé\n", PROC_NAME);
}

MODULE_LICENSE("GPL");
module_init(param_init);
module_exit(param_exit);
```

```bash
# Test
$ sudo insmod param_module.ko message="Bonjour noyau"
$ cat /proc/my_module
→ Message   : Bonjour noyau
→ Compteur  : 0
→ Noyau ver : 6.8.0-47-generic

$ cat /proc/my_module
→ Message   : Bonjour noyau
→ Compteur  : 1  ← incrémenté à chaque lecture

$ echo "Test écriture" | sudo tee /proc/my_module
$ dmesg | tail -1
→ Message reçu : Test écriture
```

---

## Chapitre 14 : Character Devices

```c
/* chardev.c — Périphérique caractère complet
 * Crée /dev/chardev qui mémorise ce qu'on lui écrit
 * et le retourne à la lecture.
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/slab.h>

#define DEVICE_NAME "chardev"
#define CLASS_NAME  "chardev_class"
#define BUF_SIZE    4096

static dev_t dev_number;          /* major:minor alloués dynamiquement */
static struct cdev my_cdev;
static struct class *dev_class;
static char kernel_buffer[BUF_SIZE];
static int buf_len = 0;
static DEFINE_MUTEX(chardev_mutex);  /* protection accès concurrent */

/* open() */
static int dev_open(struct inode *inode, struct file *filp)
{
    pr_info("chardev: opened by PID %d\n", current->pid);
    return 0;
}

/* release() — appelé à la fermeture */
static int dev_release(struct inode *inode, struct file *filp)
{
    pr_info("chardev: closed by PID %d\n", current->pid);
    return 0;
}

/* read() — copie kernel_buffer → user space */
static ssize_t dev_read(struct file *filp, char __user *user_buf,
                         size_t count, loff_t *f_pos)
{
    ssize_t ret;

    mutex_lock(&chardev_mutex);

    if (*f_pos >= buf_len) {
        ret = 0;  /* EOF */
        goto out;
    }

    count = min(count, (size_t)(buf_len - *f_pos));

    /* copy_to_user : copie sécurisée vers user space
     * Vérifie les permissions et gère les page faults */
    if (copy_to_user(user_buf, kernel_buffer + *f_pos, count)) {
        ret = -EFAULT;
        goto out;
    }

    *f_pos += count;
    ret = count;

out:
    mutex_unlock(&chardev_mutex);
    return ret;
}

/* write() — copie user space → kernel_buffer */
static ssize_t dev_write(struct file *filp, const char __user *user_buf,
                          size_t count, loff_t *f_pos)
{
    ssize_t ret;

    if (count > BUF_SIZE)
        return -EINVAL;

    mutex_lock(&chardev_mutex);

    if (copy_from_user(kernel_buffer, user_buf, count)) {
        ret = -EFAULT;
        goto out;
    }

    buf_len = count;
    *f_pos = 0;
    ret = count;
    pr_info("chardev: received %zu bytes\n", count);

out:
    mutex_unlock(&chardev_mutex);
    return ret;
}

/* ioctl() — commandes de contrôle */
#define CHARDEV_MAGIC    'k'
#define CHARDEV_RESET    _IO(CHARDEV_MAGIC, 0)
#define CHARDEV_GETSIZE  _IOR(CHARDEV_MAGIC, 1, int)

static long dev_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
    switch (cmd) {
    case CHARDEV_RESET:
        mutex_lock(&chardev_mutex);
        memset(kernel_buffer, 0, BUF_SIZE);
        buf_len = 0;
        mutex_unlock(&chardev_mutex);
        pr_info("chardev: buffer reset\n");
        break;

    case CHARDEV_GETSIZE:
        if (copy_to_user((int __user *)arg, &buf_len, sizeof(int)))
            return -EFAULT;
        break;

    default:
        return -ENOTTY;  /* Not a typewriter — commande inconnue */
    }
    return 0;
}

static const struct file_operations fops = {
    .owner          = THIS_MODULE,
    .open           = dev_open,
    .release        = dev_release,
    .read           = dev_read,
    .write          = dev_write,
    .unlocked_ioctl = dev_ioctl,
};

static int __init chardev_init(void)
{
    int ret;

    /* Allouer un major:minor dynamiquement */
    ret = alloc_chrdev_region(&dev_number, 0, 1, DEVICE_NAME);
    if (ret < 0) {
        pr_err("chardev: alloc_chrdev_region failed\n");
        return ret;
    }
    pr_info("chardev: major=%d, minor=%d\n",
            MAJOR(dev_number), MINOR(dev_number));

    /* Initialiser et enregistrer le cdev */
    cdev_init(&my_cdev, &fops);
    my_cdev.owner = THIS_MODULE;
    ret = cdev_add(&my_cdev, dev_number, 1);
    if (ret < 0) goto err_cdev;

    /* Créer la classe et le nœud /dev/chardev automatiquement */
    dev_class = class_create(CLASS_NAME);
    if (IS_ERR(dev_class)) {
        ret = PTR_ERR(dev_class);
        goto err_class;
    }

    if (IS_ERR(device_create(dev_class, NULL, dev_number,
                              NULL, DEVICE_NAME))) {
        ret = -ENOMEM;
        goto err_device;
    }

    pr_info("chardev: /dev/%s créé\n", DEVICE_NAME);
    return 0;

err_device:
    class_destroy(dev_class);
err_class:
    cdev_del(&my_cdev);
err_cdev:
    unregister_chrdev_region(dev_number, 1);
    return ret;
}

static void __exit chardev_exit(void)
{
    device_destroy(dev_class, dev_number);
    class_destroy(dev_class);
    cdev_del(&my_cdev);
    unregister_chrdev_region(dev_number, 1);
    pr_info("chardev: module removed\n");
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Étudiant Noyau");
module_init(chardev_init);
module_exit(chardev_exit);
```

```bash
# Test du character device
$ sudo insmod chardev.ko
$ ls -la /dev/chardev
→ crw-rw-rw- 1 root root 240, 0 jan 10 12:00 /dev/chardev

# Écriture
$ echo "Bonjour noyau !" | sudo tee /dev/chardev

# Lecture
$ sudo cat /dev/chardev
→ Bonjour noyau !

# Test avec un programme C
cat << 'EOF' > test_chardev.c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>

#define CHARDEV_MAGIC    'k'
#define CHARDEV_RESET    _IO(CHARDEV_MAGIC, 0)
#define CHARDEV_GETSIZE  _IOR(CHARDEV_MAGIC, 1, int)

int main(void) {
    int fd = open("/dev/chardev", O_RDWR);
    char msg[] = "Test ioctl et chardev";
    char buf[256] = {0};
    int size;

    write(fd, msg, strlen(msg));
    ioctl(fd, CHARDEV_GETSIZE, &size);
    printf("Taille écrite : %d\n", size);

    lseek(fd, 0, SEEK_SET);
    read(fd, buf, sizeof(buf));
    printf("Lu : %s\n", buf);

    ioctl(fd, CHARDEV_RESET, 0);
    close(fd);
    return 0;
}
EOF
$ gcc test_chardev.c -o test_chardev
$ sudo ./test_chardev
```

---

# ════════════════════════════════════════════════════════
# PARTIE VI — OUTILS D'INSPECTION
# ════════════════════════════════════════════════════════

---

## Chapitre 16 : /proc et /sys — Lire le Noyau Vivant

### 16.1 /proc — La fenêtre sur le noyau

```
/proc N'EST PAS un système de fichiers sur disque.
C'est une interface en mémoire générée à la volée par le noyau.

Chaque "fichier" dans /proc est un point de vue sur
une structure de données du noyau.

STRUCTURE DE /proc :
  /proc/[PID]/         → informations par processus
    cmdline            → arguments de lancement
    comm               → nom du processus (16 chars)
    exe                → lien symbolique vers l'exécutable
    fd/                → descripteurs de fichiers ouverts
    maps               → carte mémoire virtuelle
    mem                → mémoire du processus (lecture directe !)
    net/               → statistiques réseau du process
    ns/                → namespaces
    stat               → statistiques (utilisé par top/ps)
    status             → état lisible humainement
    syscall            → syscall en cours
    wchan              → fonction noyau d'attente

  /proc/sys/           → paramètres noyau (sysctl)
    kernel/            → paramètres généraux
    net/               → paramètres réseau
    vm/                → gestion mémoire
    fs/                → systèmes de fichiers

  Fichiers globaux :
    /proc/cpuinfo      → infos processeurs
    /proc/meminfo      → utilisation mémoire
    /proc/interrupts   → compteurs d'interruptions par CPU
    /proc/iomem        → carte mémoire physique
    /proc/ioports      → ports I/O (héritage x86)
    /proc/kallsyms     → symboles noyau avec adresses
    /proc/kcore        → image mémoire noyau (ELF)
    /proc/loadavg      → charge système (1, 5, 15 min)
    /proc/modules      → modules chargés
    /proc/net/         → statistiques réseau globales
    /proc/slabinfo     → allocateur slab
    /proc/vmstat       → statistiques mémoire virtuelle
    /proc/zoneinfo     → zones mémoire NUMA
```

### 16.2 sysctl — Modifier le noyau en direct

```bash
# Lire un paramètre
$ sysctl kernel.hostname
→ kernel.hostname = monserveur

$ sysctl net.ipv4.ip_forward
→ net.ipv4.ip_forward = 0

# Modifier un paramètre (temporaire, jusqu'au reboot)
$ sudo sysctl -w net.ipv4.ip_forward=1
$ sudo sysctl -w kernel.dmesg_restrict=0  # autoriser dmesg sans root

# Modification permanente
$ sudo nano /etc/sysctl.conf
# ou créer un fichier dans /etc/sysctl.d/
$ echo "net.ipv4.ip_forward = 1" | sudo tee /etc/sysctl.d/99-forward.conf
$ sudo sysctl --system  # recharger

# Paramètres importants à connaître
$ sysctl -a 2>/dev/null | grep -E \
  "kernel\.(pid_max|threads-max|printk|panic|randomize_va_space|\
  perf_event_paranoid|kptr_restrict|dmesg_restrict|yama)"

# Paramètres de sécurité critiques
$ sysctl kernel.kptr_restrict        # cacher les adresses noyau
→ kernel.kptr_restrict = 1  (2 = toujours caché, 0 = visible root)

$ sysctl kernel.dmesg_restrict       # restreindre dmesg
$ sysctl kernel.perf_event_paranoid  # restreindre perf
$ sysctl kernel.randomize_va_space   # ASLR (0=off, 1=partial, 2=full)

$ sysctl vm.overcommit_memory        # stratégie overcommit
# 0 = heuristique, 1 = toujours OK, 2 = jamais au-delà de la RAM+swap
```

### 16.3 /sys — Interface sysfs

```bash
# sysfs expose les objets du kernel (devices, bus, classes)
$ ls /sys/
→ block/  bus/  class/  dev/  devices/  firmware/  fs/
→ hypervisor/  kernel/  module/  power/

# Informations CPU
$ cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
→ 3600000  (3.6 GHz)

$ cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
→ powersave

# Changer le governor
$ echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Informations sur les modules
$ ls /sys/module/
$ cat /sys/module/ext4/version

# Information sur les PCI devices
$ ls /sys/bus/pci/devices/
$ cat /sys/bus/pci/devices/0000:00:1f.2/class
→ 0x010601  # Storage controller

# Contrôle d'énergie
$ cat /sys/class/power_supply/BAT0/capacity
→ 87  (87% de batterie)

$ cat /sys/class/net/eth0/speed
→ 1000  (1 Gbps)

# Kernel features
$ ls /sys/kernel/
→ boot_params  debug  fscaps  iommu_groups  irq  mm  notes  profiling  security  slab
```

---

## Chapitre 17 : eBPF — Observer sans Modifier

### 17.1 Philosophie eBPF

eBPF (extended Berkeley Packet Filter) est une **révolution** dans l'observabilité du noyau. Il permet d'exécuter des programmes sandboxés directement dans le noyau, sans modifier son code source et sans risquer de le planter.

```
AVANT eBPF :
  Pour tracer le noyau → modifier le code source + recompiler
  ou utiliser des modules noyau (risqué, peut crasher)
  ou DTrace (uniquement Solaris/BSD)

AVEC eBPF (Linux 3.15+, mature depuis 4.x) :
  → Charger un programme eBPF depuis user space
  → Le vérificateur noyau vérifie la sécurité (pas de boucles infinies,
    pas d'accès mémoire invalides, pas d'appels de fonctions arbitraires)
  → Le JIT compile en instructions natives
  → Le programme s'attache à des points de trace (kprobe, tracepoint, uprobe...)
  → Collecte des données via eBPF maps (shared memory)
  → ZERO downtime, ZERO risque de crash noyau

USAGES 2026 :
  Observabilité  : traces de syscalls, réseau, mémoire (BCC, bpftrace)
  Réseau         : XDP (eXpress Data Path), tc, socket filtering
  Sécurité       : Falco, Cilium, Tetragon
  Performance    : profilage CPU, cache misses, latences I/O
```

### 17.2 bpftrace — le langage haut niveau eBPF

```bash
# Installation
$ sudo apt install bpftrace bpfcc-tools linux-headers-$(uname -r)

# ════ EXEMPLES FONDAMENTAUX ════

# 1. Hello World eBPF
$ sudo bpftrace -e 'BEGIN { printf("Hello eBPF!\n"); exit(); }'

# 2. Compter les syscalls par processus
$ sudo bpftrace -e '
tracepoint:raw_syscalls:sys_enter {
    @syscalls[comm] = count();
}
END {
    print(@syscalls);
}'

# 3. Tracer toutes les ouvertures de fichiers
$ sudo bpftrace -e '
tracepoint:syscalls:sys_enter_openat {
    printf("PID %-6d %-16s %s\n", pid, comm, str(args->filename));
}'

# 4. Distribution des latences de read()
$ sudo bpftrace -e '
tracepoint:syscalls:sys_enter_read  { @start[tid] = nsecs; }
tracepoint:syscalls:sys_exit_read
/pid == $1 && @start[tid]/
{
    @latency = hist(nsecs - @start[tid]);
    delete(@start[tid]);
}' $(pgrep nginx)

# 5. Top 10 fonctions noyau les plus appelées
$ sudo bpftrace -e '
kprobe:* { @[func] = count(); }
END { print(@, 10); }' &
sleep 5
kill %1

# 6. Tracer les allocations mémoire (fuite mémoire)
$ sudo bpftrace -e '
kprobe:__kmalloc {
    @allocs[comm, arg0] = count();
}
kprobe:kfree { @frees[comm] = count(); }
END {
    printf("Allocations par process+taille :\n");
    print(@allocs);
}'

# 7. Monitorer les connexions réseau
$ sudo bpftrace -e '
kprobe:tcp_connect {
    printf("PID %d connecting\n", pid);
}'

# 8. Tracer les page faults
$ sudo bpftrace -e '
software:page-faults:1 {
    @[comm, ustack] = count();
}
END { print(@, 5); }'
```

### 17.3 BCC — BPF Compiler Collection

```python
#!/usr/bin/env python3
"""
bcc_example.py — Observer les I/O disque avec BCC
pip install bcc  (ou depuis les paquets système)
"""

from bcc import BPF
import time
import ctypes

# Programme eBPF en C (compilé par LLVM à la volée)
bpf_program = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

// Structure pour stocker les infos I/O
struct io_data {
    u32  pid;
    u32  rwflag;    // 0=read, 1=write
    u64  bytes;
    char comm[TASK_COMM_LEN];
    char disk[DISK_NAME_LEN];
};

// eBPF map : perf event buffer pour transmettre les données vers user space
BPF_PERF_OUTPUT(io_events);

// Attaché à block_rq_issue : quand une requête I/O est émise
TRACEPOINT_PROBE(block, block_rq_issue)
{
    struct io_data data = {};

    data.pid    = bpf_get_current_pid_tgid() >> 32;
    data.bytes  = args->nr_sector * 512;
    data.rwflag = (args->rwbs[0] == 'W') ? 1 : 0;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    bpf_probe_read_kernel_str(&data.disk, sizeof(data.disk), args->name);

    io_events.perf_submit(args, &data, sizeof(data));
    return 0;
}
"""

b = BPF(text=bpf_program)

print("Surveillance des I/O disque... (Ctrl+C pour arrêter)")
print(f"{'PID':>7} {'COMM':<16} {'DISK':<8} {'TYPE':>6} {'BYTES':>10}")

def print_event(cpu, data, size):
    event = b["io_events"].event(data)
    op = "WRITE" if event.rwflag else "READ"
    print(f"{event.pid:>7} {event.comm.decode():16} "
          f"{event.disk.decode():8} {op:>6} {event.bytes:>10}")

b["io_events"].open_perf_buffer(print_event)

try:
    while True:
        b.perf_buffer_poll()
except KeyboardInterrupt:
    pass
```

---

## Chapitre 18 : Débogage Noyau

### 18.1 ftrace — Le traceur intégré

```bash
# ftrace est disponible via debugfs
$ sudo mount -t debugfs none /sys/kernel/debug  # si non monté
$ ls /sys/kernel/debug/tracing/

# Lister les traceurs disponibles
$ cat /sys/kernel/debug/tracing/available_tracers
→ hwlat blk mmiotrace function_graph wakeup_dl wakeup_rt wakeup function nop

# Activer le function tracer
$ sudo bash -c '
echo function > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on
cat /sys/kernel/debug/tracing/trace | head -30
echo 0 > /sys/kernel/debug/tracing/tracing_on'

# Tracer seulement certaines fonctions
$ sudo bash -c '
echo "ext4_*" > /sys/kernel/debug/tracing/set_ftrace_filter
echo function > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on'

# Tracer un processus spécifique
$ sudo bash -c "
echo $$ > /sys/kernel/debug/tracing/set_ftrace_pid
echo function_graph > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on"
# Effectuer une action dans le shell
# ls /tmp
$ sudo bash -c "
echo 0 > /sys/kernel/debug/tracing/tracing_on
cat /sys/kernel/debug/tracing/trace | head -50"

# trace-cmd — wrapper plus facile
$ sudo apt install trace-cmd
$ sudo trace-cmd record -e syscalls -p function_graph ls
$ trace-cmd report | head -50
```

### 18.2 perf — Profilage avancé

```bash
# Installation
$ sudo apt install linux-perf

# Profiler une commande
$ sudo perf stat ls
→ Performance counter stats for 'ls':
→       1.234567      task-clock (msec)
→               1      context-switches
→               0      cpu-migrations
→             120      page-faults
→       4,567,890      cycles
→       3,456,789      instructions              # IPC = 0.76
→         234,567      branches
→           1,234      branch-misses             # 0.5%

# Record + report
$ sudo perf record -g ls
$ sudo perf report --stdio | head -30

# Flamegraph (visualisation des hotspots)
$ sudo perf record -F 99 -ag sleep 30  # 30s de profiling
$ sudo perf script > out.perf
$ git clone https://github.com/brendangregg/FlameGraph
$ FlameGraph/stackcollapse-perf.pl out.perf | FlameGraph/flamegraph.pl > flamegraph.svg

# Événements matériels
$ sudo perf stat -e cache-misses,cache-references,instructions ./mon_programme
$ sudo perf stat -e L1-dcache-loads,L1-dcache-load-misses ./mon_programme

# Tracer les fonctions noyau les plus coûteuses
$ sudo perf top -a --stdio
$ sudo perf top -a -e cycles:k  # seulement kernel

# Analyser les verrouillages
$ sudo perf lock record ls
$ sudo perf lock report

# Analyser les appels scheduler
$ sudo perf sched record sleep 1
$ sudo perf sched latency | head -20
```

---

# ════════════════════════════════════════════════════════
# PARTIE VII — SÉCURITÉ
# ════════════════════════════════════════════════════════

---

## Chapitre 19 : Mécanismes de Sécurité du Noyau

### 19.1 Défenses intégrées (Linux 6.x)

```
KASLR (Kernel Address Space Layout Randomization) :
  → Randomise l'adresse de chargement du noyau au boot
  → Rend les exploits basés sur des adresses fixes impossibles
  → Désactiver : kaslr sur la ligne de commande noyau (débogage)
  $ cat /proc/kallsyms | grep " T " | head  # adresses randomisées

SMEP (Supervisor Mode Execution Prevention) :
  → Interdit au noyau d'exécuter du code en espace utilisateur
  → CR4 bit 20 = 1 si activé
  → Bloque les exploits "ret2user" (rediriger le noyau vers code user)

SMAP (Supervisor Mode Access Prevention) :
  → Interdit au noyau de LIRE/ÉCRIRE la mémoire utilisateur
    sans utiliser copy_to_user/copy_from_user
  → CR4 bit 21 = 1 si activé
  → Force l'utilisation des helpers sécurisés

KPTI (Kernel Page Table Isolation, Meltdown mitigation) :
  → Sépare totalement les tables de pages user et kernel
  → Au syscall : switch de CR3 (coûteux en performance ~5-30%)
  → Empêche l'exploit Meltdown (lire la mémoire noyau depuis user)

Stack Canaries (__stack_chk_guard) :
  → Valeur secrète placée avant l'adresse de retour sur la pile
  → Vérifiée avant le return → détecte les buffer overflows
  $ objdump -d /usr/bin/ls | grep __stack_chk

CFI (Control Flow Integrity) :
  → Vérifie que les sauts/appels indirects vont vers des cibles valides
  → Bloque les exploits ROP (Return-Oriented Programming)
  → Disponible avec Clang CFI dans les kernels Android et récents

FORTIFY_SOURCE :
  → Vérifie les tailles des buffers dans memcpy, strcpy, etc.
  → Détecte les overflows à la compilation ET à l'exécution
  $ gcc -D_FORTIFY_SOURCE=2 -O2 prog.c

LSM (Linux Security Modules) :
  → Hooks dans le noyau pour politiques de contrôle d'accès
  → SELinux, AppArmor, Smack, TOMOYO, Landlock
  $ cat /sys/kernel/security/lsm
  → lockdown,capability,landlock,yama,apparmor
```

### 19.2 Linux Capabilities

```
PROBLÈME DU MODÈLE UNIX CLASSIQUE :
  root = tout puissant, non-root = très limité.
  Un démon réseau a besoin de bind() sur le port 80 (<1024)
  → devait être root → privilèges excessifs.

CAPABILITIES (POSIX 1003.1e) :
  Divisent les privilèges root en ~40 capacités indépendantes.
  Chaque processus a 3 sets :
    Permitted   : capacités autorisées
    Effective   : capacités actives
    Inheritable : capacités transmises aux enfants

PRINCIPALES CAPABILITIES :
  CAP_NET_BIND_SERVICE  → bind sur ports < 1024
  CAP_NET_ADMIN         → config réseau (iptables, routes...)
  CAP_SYS_ADMIN         → beaucoup de choses (trop large !)
  CAP_SYS_PTRACE        → ptrace d'autres processus
  CAP_SYS_MODULE        → charger/décharger des modules
  CAP_DAC_OVERRIDE      → ignorer les permissions fichiers
  CAP_SETUID/SETGID     → changer UID/GID
  CAP_KILL              → envoyer des signaux à n'importe qui
  CAP_AUDIT_WRITE       → écrire dans le log d'audit
  CAP_SYS_RAWIO         → I/O physique directes (iopl/ioperm)
```

```bash
# Voir les capabilities d'un processus
$ cat /proc/$$/status | grep Cap
→ CapInh:  0000000000000000
→ CapPrm:  0000000000000000
→ CapEff:  0000000000000000   ← 0 = pas de capabilities spéciales

# Décoder un bitmask de capabilities
$ python3 -c "
caps = {
    0:'chown', 1:'dac_override', 2:'dac_read_search',
    6:'setuid', 7:'setgid', 10:'net_bind_service',
    12:'net_admin', 14:'ipc_lock', 16:'sys_module',
    21:'sys_admin', 22:'sys_boot', 23:'sys_nice',
    27:'sys_ptrace', 29:'audit_write', 36:'syslog',
    37:'wake_alarm', 38:'block_suspend', 39:'audit_read',
}
val = 0xffffffffffffffff  # root : toutes les capabilities
active = [name for bit, name in caps.items() if (val >> bit) & 1]
print('Capabilities actives:', active)
"

# Assigner une capability à un binaire
$ sudo setcap cap_net_bind_service=eip /usr/bin/mon_serveur
$ getcap /usr/bin/mon_serveur
→ /usr/bin/mon_serveur cap_net_bind_service=eip

# Exemple : ping sans être root
$ ls -la /usr/bin/ping
→ -rwxr-xr-x 1 root root ... /usr/bin/ping
$ getcap /usr/bin/ping
→ /usr/bin/ping cap_net_raw=ep  ← capability raw socket

# Supprimer les capabilities d'un binaire
$ sudo setcap -r /usr/bin/mon_serveur
```

---

## Chapitre 20 : Namespaces et cgroups

### 20.1 Namespaces — l'isolation du noyau

```
LES 8 NAMESPACES LINUX :

  PID  (CLONE_NEWPID)   : PIDs isolés. init du container = PID 1.
  NET  (CLONE_NEWNET)   : interfaces réseau, routes, iptables isolés.
  MNT  (CLONE_NEWNS)    : points de montage isolés (base de chroot++).
  UTS  (CLONE_NEWUTS)   : hostname et domainname isolés.
  IPC  (CLONE_NEWIPC)   : sémaphores, queues de messages, shm isolés.
  USER (CLONE_NEWUSER)  : UID/GID mapping (root dans container ≠ root hôte).
  CGROUP (CLONE_NEWCGROUP): vue isolée sur les cgroups.
  TIME (CLONE_NEWTIME)  : horloge système isolée (Linux 5.6+).

VISUALISER LES NAMESPACES :
  $ ls -la /proc/$$/ns/
  → lrwxrwxrwx 1 ... cgroup -> cgroup:[4026531835]
  → lrwxrwxrwx 1 ... ipc -> ipc:[4026531839]
  → lrwxrwxrwx 1 ... mnt -> mnt:[4026531840]
  → lrwxrwxrwx 1 ... net -> net:[4026531992]
  → lrwxrwxrwx 1 ... pid -> pid:[4026531836]
  → lrwxrwxrwx 1 ... time -> time:[4026531834]
  → lrwxrwxrwx 1 ... user -> user:[4026531837]
  → lrwxrwxrwx 1 ... uts -> uts:[4026531838]

  Deux processus dans le même namespace partagent le même numéro inode.
```

```bash
# Créer un namespace PID isolé
$ sudo unshare --pid --fork --mount-proc bash
# Dans ce shell, les PIDs recommencent à 1 !
$ ps aux
→ PID  COMMAND
→   1  bash          ← ce bash est PID 1 dans ce namespace
→   2  ps aux

# Namespace réseau isolé
$ sudo ip netns add test_ns
$ sudo ip netns exec test_ns bash
$ ip a    # seulement lo, pas d'eth0 !
$ exit
$ sudo ip netns delete test_ns

# Conteneur manuel avec unshare (Docker fait la même chose)
$ sudo unshare \
    --pid --fork \
    --mount-proc \
    --net \
    --uts \
    --ipc \
    --user \
    --map-root-user \
    bash

# Voir les namespaces de Docker
$ docker run -d nginx
$ CONTAINER_PID=$(docker inspect --format '{{.State.Pid}}' $(docker ps -q))
$ ls -la /proc/$CONTAINER_PID/ns/
# Les namespaces diffèrent de ceux du host !
$ sudo lsns | head -20
```

### 20.2 cgroups v2 — contrôle des ressources

```bash
# cgroups v2 est monté sur /sys/fs/cgroup
$ ls /sys/fs/cgroup/
→ cgroup.controllers  cgroup.max.depth  cgroup.procs
→ cgroup.stat         cgroup.subtree_control  cpu.stat
→ io.stat             memory.stat       ...

# Créer un cgroup
$ sudo mkdir /sys/fs/cgroup/mon_groupe

# Activer les contrôleurs (mémoire, CPU, I/O)
$ echo "+cpu +memory +io" | \
  sudo tee /sys/fs/cgroup/mon_groupe/cgroup.subtree_control

# Limiter la mémoire à 100 MB
$ echo $((100 * 1024 * 1024)) | \
  sudo tee /sys/fs/cgroup/mon_groupe/memory.max

# Limiter l'utilisation CPU à 50% (500ms sur 1000ms)
$ echo "500000 1000000" | \
  sudo tee /sys/fs/cgroup/mon_groupe/cpu.max

# Assigner un processus au cgroup
$ echo $$ | sudo tee /sys/fs/cgroup/mon_groupe/cgroup.procs

# Vérifier
$ cat /sys/fs/cgroup/mon_groupe/memory.current
$ cat /sys/fs/cgroup/mon_groupe/cpu.stat

# Avec systemd (la vraie façon)
$ systemd-run --unit=mon_service \
    --property=MemoryMax=100M \
    --property=CPUQuota=50% \
    /bin/stress --vm 1 --vm-bytes 200M

# Voir les cgroups des processus
$ systemctl status mon_service
$ cat /proc/$$/cgroup
→ 0::/user.slice/user-1000.slice/session-1.scope
```

---

# ════════════════════════════════════════════════════════
# PARTIE VIII — CHALLENGES ET PROJETS
# ════════════════════════════════════════════════════════

---

## Chapitre 21 : Projet Complet — Module de Monitoring Système

```c
/* sysmon.c — Module noyau de monitoring temps réel
 * Expose des statistiques système via /proc/sysmon
 * et permet de configurer des alertes via /proc/sysmon_config
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/sched.h>
#include <linux/mm.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/jiffies.h>
#include <linux/timer.h>
#include <linux/spinlock.h>

#define SYSMON_INTERVAL_MS 1000  /* période de collecte */
#define HISTORY_SIZE       60    /* 60 secondes d'historique */

struct cpu_sample {
    u64 user;
    u64 nice;
    u64 system;
    u64 idle;
    u64 total;
    unsigned long timestamp;
};

struct sysmon_data {
    struct cpu_sample cpu_history[HISTORY_SIZE];
    int cpu_head;
    unsigned long mem_total;
    unsigned long mem_free;
    int process_count;
    spinlock_t lock;
};

static struct sysmon_data *smon;
static struct timer_list collection_timer;

/* Collecte les données système */
static void collect_stats(struct timer_list *t)
{
    struct task_struct *task;
    int count = 0;
    struct cpu_sample *s;
    u64 user = 0, nice = 0, system = 0, idle = 0;
    int cpu;

    spin_lock(&smon->lock);

    /* Compter les processus */
    rcu_read_lock();
    for_each_process(task) count++;
    rcu_read_unlock();
    smon->process_count = count;

    /* Mémoire */
    smon->mem_total = totalram_pages() * PAGE_SIZE / 1024;
    smon->mem_free  = global_zone_page_state(NR_FREE_PAGES) * PAGE_SIZE / 1024;

    /* CPU (simplifié) */
    s = &smon->cpu_history[smon->cpu_head % HISTORY_SIZE];
    s->timestamp = jiffies;
    /* En production : lire kcpustat_cpu(cpu) pour chaque CPU */

    smon->cpu_head++;
    spin_unlock(&smon->lock);

    /* Reprogrammer le timer */
    mod_timer(&collection_timer, jiffies + msecs_to_jiffies(SYSMON_INTERVAL_MS));
}

/* Affichage /proc/sysmon */
static int sysmon_show(struct seq_file *m, void *v)
{
    spin_lock(&smon->lock);

    seq_printf(m, "=== SYSMON — Noyau %s ===\n\n", UTS_RELEASE);
    seq_printf(m, "Mémoire totale  : %lu KB\n", smon->mem_total);
    seq_printf(m, "Mémoire libre   : %lu KB  (%.1f%%)\n",
               smon->mem_free,
               smon->mem_total ? (100.0 * smon->mem_free / smon->mem_total) : 0);
    seq_printf(m, "Processus       : %d\n", smon->process_count);
    seq_printf(m, "Uptime          : %lu secondes\n",
               (unsigned long)(jiffies / HZ));

    spin_unlock(&smon->lock);

    /* Liste les 10 processus les plus récents */
    seq_printf(m, "\n=== PROCESSUS ACTIFS ===\n");
    seq_printf(m, "%-8s %-16s %-8s %-8s\n",
               "PID", "COMM", "STATE", "PRIO");

    struct task_struct *task;
    int shown = 0;
    rcu_read_lock();
    for_each_process(task) {
        if (shown++ >= 10) break;
        seq_printf(m, "%-8d %-16s %-8c %-8d\n",
                   task->pid,
                   task->comm,
                   task_state_to_char(task),
                   task->normal_prio);
    }
    rcu_read_unlock();

    return 0;
}

static int sysmon_open(struct inode *inode, struct file *file)
{
    return single_open(file, sysmon_show, NULL);
}

static const struct proc_ops sysmon_ops = {
    .proc_open    = sysmon_open,
    .proc_read    = seq_read,
    .proc_lseek   = seq_lseek,
    .proc_release = single_release,
};

static int __init sysmon_init(void)
{
    smon = kzalloc(sizeof(*smon), GFP_KERNEL);
    if (!smon) return -ENOMEM;

    spin_lock_init(&smon->lock);

    if (!proc_create("sysmon", 0444, NULL, &sysmon_ops)) {
        kfree(smon);
        return -ENOMEM;
    }

    timer_setup(&collection_timer, collect_stats, 0);
    mod_timer(&collection_timer, jiffies + msecs_to_jiffies(SYSMON_INTERVAL_MS));

    pr_info("sysmon: module chargé, /proc/sysmon disponible\n");
    return 0;
}

static void __exit sysmon_exit(void)
{
    del_timer_sync(&collection_timer);
    proc_remove(proc_lookup_de("sysmon", NULL));
    kfree(smon);
    pr_info("sysmon: module déchargé\n");
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Étudiant Noyau");
MODULE_DESCRIPTION("Module de monitoring système - TP");
module_init(sysmon_init);
module_exit(sysmon_exit);
```

---

## Chapitre 22 : Challenge Final

### 🔴 Challenge 1 — Analyser un kernel panic

```
DUMP DE KERNEL PANIC À ANALYSER :

[  245.123456] BUG: unable to handle kernel NULL pointer dereference at 0000000000000008
[  245.123457] PGD 0 P4D 0
[  245.123458] Oops: 0002 [#1] SMP PTI
[  245.123459] CPU: 2 PID: 1234 Comm: mymodule Not tainted 6.8.0-47-generic #47-Ubuntu
[  245.123460] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3
[  245.123461] RIP: 0010:my_driver_write+0x2a/0x80 [mymodule]
[  245.123462] Code: 48 89 fb 48 8b 47 08 48 85 c0 74 05 48 8b 40 08 48 89 c6 ...
[  245.123463] RSP: 0018:ffffb3c240a1be20 EFLAGS: 00010246
[  245.123464] RAX: 0000000000000000 RBX: ffff9a8741234000 RCX: 0000000000000015
[  245.123465] RDX: 0000000000000015 RSI: 00007ffd12345678 RDI: ffff9a8741234000
[  245.123466] RBP: ffffb3c240a1be48 R08: 0000000000000000 R09: 0000000000000000
[  245.123467] R10: 0000000000000000 R11: 0000000000000246 R12: 0000000000000015
[  245.123468] R13: 00007ffd12345678 R14: ffff9a8741234000 R15: 0000000000000000
[  245.123469] FS:  00007f8b12345700(0000) GS:ffff9a875fc80000(0000) knlGS:0000000000000000
[  245.123470] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
[  245.123471] CR2: 0000000000000008 CR3: 000000012345e001 CR4: 00000000003706e0
[  245.123472] Call Trace:
[  245.123473]  <TASK>
[  245.123474]  vfs_write+0xb2/0x2d0
[  245.123475]  ksys_write+0x6b/0xf0
[  245.123476]  __x64_sys_write+0x19/0x30
[  245.123477]  do_syscall_64+0x5b/0x90
[  245.123478]  entry_SYSCALL_64_after_hwframe+0x6e/0xd8

QUESTIONS :
1. Quelle est la cause exacte du panic ?
2. Dans quelle fonction et à quel offset s'est produit le crash ?
3. Quelle était la valeur du registre CR2 et que signifie-t-elle ?
4. Quelle est la chaîne d'appel (call trace) qui a mené au crash ?
5. Le bit 1 dans l'Oops code (0002) indique quoi ?
6. Comment aurait-on pu éviter ce bug ?
7. Écrire le code C défectueux qui aurait pu produire ce crash.
```

**Réponses :**

```
1. NULL pointer dereference : le driver tente d'écrire à l'adresse 0x0000000000000008
   Ce n'est pas exactement NULL (0x0) mais une déréférencement d'un pointeur NULL + offset 8
   → Typiquement : struct *ptr = NULL; ptr->champ = valeur; où champ est à l'offset 8

2. Fonction : my_driver_write, offset 0x2a dans la fonction (0x2a = 42 bytes)
   Dans le module mymodule.ko

3. CR2 = 0x0000000000000008 : c'est l'adresse qui a causé la page fault
   Le processeur stocke dans CR2 l'adresse fautive lors d'un #PF (page fault)
   0x8 = 8 bytes après NULL → accès à un pointeur null + membre de struct à offset 8

4. Call trace :
   entry_SYSCALL_64 → do_syscall_64 → sys_write → ksys_write
   → vfs_write → my_driver_write (CRASH ici)
   → Un write() userspace a appelé notre driver qui a crashé

5. Oops code 0002 :
   Bit 0 = 0 : page non présente (not-present page)
   Bit 1 = 1 : opération d'ÉCRITURE (1=write, 0=read)
   Bit 2 = 0 : depuis kernel mode (0=kernel, 1=user)
   → Tentative d'ÉCRITURE dans une page non présente, depuis le kernel

6. Prévention :
   - Toujours vérifier les pointeurs avant déréférencement
   - Utiliser WARN_ON_NULL(), BUG_ON(ptr == NULL)
   - Valider les pointeurs reçus de l'espace utilisateur

7. Code défectueux probable :
   struct my_device {
       int unused;       // offset 0
       struct buffer *buf;  // offset 8 ← ICI
   };
   
   static ssize_t my_driver_write(...) {
       struct my_device *dev = filp->private_data;
       // dev->buf est NULL (non initialisé !)
       dev->buf->data = kmalloc(count, GFP_KERNEL);  // CRASH : déréférence NULL+8
       ...
   }
   
   Fix : vérifier dev->buf != NULL avant utilisation
```

### 🔴 Challenge 2 — Écrire un eBPF de sécurité

```bash
# Mission : Détecter et alerter en temps réel les comportements suspects :
# 1. Exécution de /etc/shadow ou /etc/passwd par un processus non root
# 2. Tentative de setuid(0) par un processus non-root
# 3. Création d'un fichier dans /tmp avec droits d'exécution
# 4. Connexion réseau sortante vers le port 4444 (shell inversé courant)

# Squelette eBPF à compléter :

sudo bpftrace -e '
/* TODO 1 : Détecter lecture de fichiers sensibles */
tracepoint:syscalls:sys_enter_openat
/str(args->filename) == "/etc/shadow" && uid != 0/
{
    printf("⚠️  ALERTE: %s (PID %d, UID %d) tente lire /etc/shadow!\n",
           comm, pid, uid);
}

/* TODO 2 : Détecter setuid(0) */
/* Compléter : tracepoint:syscalls:sys_enter_setuid */

/* TODO 3 : Détecter création fichier exécutable dans /tmp */
/* Compléter : tracepoint:syscalls:sys_enter_openat avec flags O_CREAT */
/* et vérifier le mode contient S_IXUSR */

/* TODO 4 : Détecter connexion port 4444 */
/* Compléter : kprobe:tcp_connect ou tracepoint:syscalls:sys_enter_connect */
'
```

---

# ANNEXES

---

## Annexe A — Commandes de Référence Noyau

```bash
# ═══ INFORMATIONS SYSTÈME ═══
uname -r                    # version noyau
uname -a                    # tout
cat /proc/version           # version détaillée
dmesg -T                    # messages noyau avec timestamps
dmesg -l err,crit,emerg     # seulement les erreurs
journalctl -k               # messages noyau via journald

# ═══ MODULES ═══
lsmod                       # modules chargés
modinfo nom_module          # infos d'un module
insmod module.ko            # charger
rmmod nom_module            # décharger
modprobe nom_module         # charger avec dépendances
modprobe -r nom_module      # décharger avec dépendances

# ═══ MÉMOIRE ═══
free -h                     # résumé mémoire
cat /proc/meminfo           # détails
vmstat 1 10                 # statistiques VM (1s, 10 fois)
slabtop -o                  # caches SLUB
sudo cat /proc/buddyinfo    # buddy allocator
numactl --hardware          # topology NUMA

# ═══ PROCESSUS ═══
ps aux                      # tous les processus
top / htop                  # interactif
cat /proc/PID/maps          # mémoire virtuelle
cat /proc/PID/status        # état
cat /proc/PID/syscall       # syscall en cours
ls -la /proc/PID/fd/        # fichiers ouverts

# ═══ PERFORMANCE ═══
perf stat commande          # compteurs hardware
perf top                    # hotspots CPU
sar -u 1 10                 # CPU (sysstat)
iostat -x 1                 # I/O disque
ss -s                       # statistiques socket

# ═══ SÉCURITÉ ═══
cat /proc/PID/status | grep Cap  # capabilities
getcap fichier              # capabilities d'un binaire
getfattr -n security.selinux fichier  # labels SELinux
aa-status                   # état AppArmor
ls /sys/kernel/security/    # LSM actifs
```

## Annexe B — Ressources Essentielles

```
DOCUMENTATION OFFICIELLE :
  https://www.kernel.org/doc/html/latest/         → Doc officielle
  https://elixir.bootlin.com/linux/latest/source  → Sources navigables
  https://lwn.net                                 → Articles noyau
  https://lkml.org                                → Mailing list

LIVRES DE RÉFÉRENCE :
  Robert Love — Linux Kernel Development (3rd ed., 2010)
  Bovet & Cesati — Understanding the Linux Kernel (3rd ed., O'Reilly)
  Greg Kroah-Hartman — Linux Device Drivers (3rd ed., libre en ligne)
  Jonathan Corbet — Linux Device Drivers 4th ed. (en cours)

eBPF / TRACING :
  https://ebpf.io                                 → Introduction eBPF
  https://github.com/iovisor/bcc                  → BCC tools
  https://github.com/iovisor/bpftrace             → bpftrace
  Brendan Gregg — BPF Performance Tools (Addison-Wesley 2019)

SÉCURITÉ NOYAU :
  https://kernsec.org                             → Kernel Self Protection Project
  https://grsecurity.net/features.php             → Hardening avancé
  https://syzkaller.appspot.com                   → Fuzzer noyau (syzbot)

EXERCICES PRATIQUES :
  https://kernelnewbies.org                       → Pour débuter
  https://eudyptula-challenge.org                 → Challenges modules
  https://github.com/torvalds/linux/tree/master/samples/  → Exemples officiels
```

## Annexe C — Glossaire des Structures Clés

```
task_struct    → Représente un processus/thread
mm_struct      → Espace d'adressage d'un processus  
vm_area_struct → Zone de mémoire virtuelle (une ligne de /proc/PID/maps)
page           → Décrit une page physique de 4KB (struct page)
super_block    → Instance d'un FS monté
inode          → Métadonnées d'un fichier
dentry         → Entrée de répertoire (cache de résolution de chemin)
file           → Fichier ouvert (par processus)
socket         → Socket réseau (implémente file_operations)
sk_buff        → Paquet réseau (socket buffer)
net_device     → Interface réseau
request_queue  → File de requêtes I/O blocs
bio            → Block I/O request (unit)
kmem_cache     → Cache SLUB d'objets de type fixe
rb_node        → Nœud d'arbre rouge-noir
list_head      → Élément de liste doublement chaînée circulaire
work_struct    → Travail différé (workqueue)
completion     → Synchronisation asynchrone
mutex, spinlock, rwlock → Primitives de synchronisation
rcu_head       → Read-Copy-Update (synchronisation lock-free)
```

---

*TP rédigé en référence aux sources officielles du noyau Linux 6.x et à la documentation LKML.*
*Toutes les manipulations bas niveau (modules, /proc, sysctl) doivent être pratiquées dans une machine virtuelle.*
*Ne jamais modifier les paramètres sysctl critiques sur un système de production sans test préalable.*
*Le noyau Linux est un bien commun — contribuer sur kernel.org est accessible à tous.*
