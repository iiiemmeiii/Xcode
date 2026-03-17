# TP Linux — Système de Fichiers, Droits & Attributs Spéciaux
### De Zéro à Expert · Arborescence · Permissions · Audit

---

> **Public visé** : Débutants → Administrateurs confirmés  
> **Durée estimée** : 6 à 10 heures (selon niveau)  
> **Environnement** : Linux (Ubuntu/Debian recommandé) — machine virtuelle conseillée  
> **Convention** : `$` = utilisateur standard · `#` = root · `→` = sortie attendue

---

## TABLE DES MATIÈRES

```
NIVEAU 1 — FONDATIONS
  Module 1 : L'arborescence Linux (FHS)
  Module 2 : Navigation et exploration

NIVEAU 2 — GESTION DES FICHIERS
  Module 3 : Création, déplacement, suppression
  Module 4 : Types de fichiers et inodes

NIVEAU 3 — DROITS ET PERMISSIONS
  Module 5 : Le modèle UGO (User/Group/Others)
  Module 6 : chmod, chown, chgrp

NIVEAU 4 — ATTRIBUTS SPÉCIAUX
  Module 7 : SUID, SGID, Sticky Bit
  Module 8 : Attributs étendus (chattr / lsattr)
  Module 9 : ACL (Access Control Lists)

NIVEAU 5 — AUDIT ET SÉCURITÉ
  Module 10 : Audit du système de fichiers
  Module 11 : Recherche de failles et hardening
  Module 12 : Cas pratiques et scénarios réels
```

---

# ═══════════════════════════════════════
# NIVEAU 1 — FONDATIONS
# ═══════════════════════════════════════

---

## MODULE 1 — L'Arborescence Linux (FHS)

### 1.1 Concept fondamental

Sous Linux, **tout est fichier**. Il n'existe qu'une seule arborescence, ancrée à la racine `/`. Contrairement à Windows (C:\, D:\...), les périphériques, partitions et systèmes de fichiers distants sont **montés** dans cette arborescence unique.

```
/                          ← Racine absolue du système
├── bin/                   ← Binaires essentiels (ls, cp, mv...)
├── boot/                  ← Noyau, initrd, bootloader
├── dev/                   ← Fichiers de périphériques
├── etc/                   ← Configuration système
├── home/                  ← Répertoires personnels des utilisateurs
│   ├── alice/
│   └── bob/
├── lib/                   ← Bibliothèques partagées
├── media/                 ← Points de montage automatiques (USB...)
├── mnt/                   ← Points de montage manuels
├── opt/                   ← Logiciels tiers installés manuellement
├── proc/                  ← Système de fichiers virtuel (processus, noyau)
├── root/                  ← Répertoire home de root
├── run/                   ← Données de runtime (PID, sockets...)
├── srv/                   ← Données des services (web, ftp...)
├── sys/                   ← Interface avec le noyau (sysfs)
├── tmp/                   ← Fichiers temporaires (vidé au reboot)
├── usr/                   ← Applications et données utilisateur
│   ├── bin/               ← Commandes utilisateur
│   ├── lib/               ← Bibliothèques
│   ├── local/             ← Compilations locales
│   └── share/             ← Données partagées (doc, man...)
└── var/                   ← Données variables (logs, mails, spool...)
    ├── log/
    ├── www/
    └── spool/
```

### 1.2 Rôle détaillé de chaque répertoire

| Répertoire | Contenu | Modifiable par |
|------------|---------|----------------|
| `/bin` | Commandes essentielles au démarrage | root |
| `/sbin` | Commandes système (fsck, ifconfig...) | root |
| `/etc` | Fichiers de configuration | root |
| `/home` | Données personnelles des utilisateurs | chaque user |
| `/tmp` | Fichiers temporaires (world-writable) | tous |
| `/var/log` | Journaux système | root/daemons |
| `/proc` | Pseudo-filesystem en RAM (infos noyau) | lecture seule |
| `/sys` | Interface noyau (pilotes, hardware) | root |
| `/dev` | Fichiers spéciaux de périphériques | root |

### 🔬 Exercice 1.1 — Exploration initiale

```bash
# Afficher l'arborescence de premier niveau
$ ls -la /

# Taille de chaque répertoire de premier niveau
$ du -sh /* 2>/dev/null | sort -h

# Quel filesystem est monté où ?
$ df -hT

# Afficher tous les points de montage
$ cat /proc/mounts
$ findmnt --tree
```

**Questions :**
1. Pourquoi `/proc` et `/sys` affichent-ils une taille de 0 ?
2. Quelle est la différence entre `/bin` et `/usr/bin` ?
3. Où sont stockés les logs du système ?

---

## MODULE 2 — Navigation et Exploration

### 2.1 Chemins absolus vs relatifs

```bash
# Chemin ABSOLU — part toujours de /
$ cd /home/alice/documents

# Chemin RELATIF — part du répertoire courant
$ cd documents          # si on est déjà dans /home/alice

# Raccourcis essentiels
$ cd ~                  # aller dans son home
$ cd -                  # retourner au répertoire précédent
$ cd ..                 # remonter d'un niveau
$ cd ../..              # remonter de deux niveaux
```

### 2.2 Commandes de navigation

```bash
# Où suis-je ?
$ pwd
→ /home/alice

# Lister avec détails
$ ls -la
→ total 48
→ drwxr-xr-x  5 alice alice 4096 jan 10 09:00 .
→ drwxr-xr-x  4 root  root  4096 jan  5 08:00 ..
→ -rw-r--r--  1 alice alice  220 jan  5 08:00 .bash_logout
→ -rw-r--r--  1 alice alice 3526 jan  5 08:00 .bashrc

# Comprendre la sortie de ls -la :
# [type+permissions] [liens] [user] [group] [taille] [date] [nom]
#  drwxr-xr-x          5     alice  alice   4096    jan 10   Documents

# Options utiles de ls
$ ls -lh          # tailles lisibles (K, M, G)
$ ls -lt          # tri par date de modification
$ ls -lS          # tri par taille
$ ls -R           # récursif
$ ls -d */        # seulement les répertoires
$ ls -lai         # avec numéros d'inodes
```

### 2.3 Explorer le contenu de /proc et /sys

```bash
# Informations CPU depuis /proc
$ cat /proc/cpuinfo

# Mémoire
$ cat /proc/meminfo

# Version du noyau
$ cat /proc/version
$ uname -a

# Processus en cours
$ ls /proc/ | grep -E '^[0-9]+$' | head -10

# Informations sur le PID 1 (init/systemd)
$ cat /proc/1/cmdline | tr '\0' ' '
$ ls -la /proc/1/

# Interfaces réseau depuis /sys
$ ls /sys/class/net/
$ cat /sys/class/net/eth0/address   # adresse MAC
```

### 🔬 Exercice 1.2 — Exploration avancée

```bash
# 1. Créer l'arborescence de votre session de TP
$ mkdir -p ~/tp_linux/{niveau1,niveau2,niveau3,niveau4,niveau5}
$ tree ~/tp_linux

# 2. Trouver les 10 plus gros fichiers du système
$ find / -type f -exec du -h {} + 2>/dev/null | sort -rh | head -10

# 3. Compter les fichiers dans /etc
$ find /etc -type f | wc -l

# 4. Lister tous les fichiers de configuration modifiés aujourd'hui
$ find /etc -newer /etc/passwd -type f 2>/dev/null
```

---

# ═══════════════════════════════════════
# NIVEAU 2 — GESTION DES FICHIERS
# ═══════════════════════════════════════

---

## MODULE 3 — Création, Déplacement, Suppression

### 3.1 Création de fichiers et répertoires

```bash
# Créer un fichier vide
$ touch fichier.txt

# Créer avec contenu
$ echo "Bonjour Linux" > fichier.txt
$ cat fichier.txt
→ Bonjour Linux

# Append (ajouter sans écraser)
$ echo "Deuxième ligne" >> fichier.txt

# Créer un répertoire
$ mkdir mon_dossier

# Créer une arborescence complète d'un coup
$ mkdir -p projets/web/css projets/web/js projets/python
$ tree projets/
→ projets/
→ ├── python/
→ └── web/
→     ├── css/
→     └── js/
```

### 3.2 Copie, déplacement, renommage

```bash
# Copier un fichier
$ cp source.txt destination.txt

# Copier avec préservation des métadonnées (droits, dates...)
$ cp -p source.txt destination.txt

# Copier un répertoire récursivement
$ cp -r dossier_source/ dossier_dest/

# Déplacer / Renommer
$ mv ancien_nom.txt nouveau_nom.txt
$ mv fichier.txt /home/alice/documents/

# Copie sécurisée (affiche progression)
$ rsync -avh source/ destination/
```

### 3.3 Suppression

```bash
# Supprimer un fichier
$ rm fichier.txt

# Supprimer sans confirmation (DANGER)
$ rm -f fichier.txt

# Supprimer un répertoire vide
$ rmdir dossier_vide/

# Supprimer récursivement (TRÈS DANGEREUX)
$ rm -rf dossier_complet/

# ⚠️ JAMAIS : rm -rf / ou rm -rf /*
# Astuce sécurité : toujours utiliser --preserve-root
$ rm -rf --preserve-root /
```

### 3.4 Liens — Hard Links et Symlinks

```bash
# ┌─────────────────────────────────────────────────────┐
# │              Comprendre les inodes                   │
# │                                                      │
# │  Fichier = Inode (métadonnées) + Data blocks         │
# │                                                      │
# │  Hard link : 2 noms → même inode (même fichier)     │
# │  Symlink   : fichier spécial → pointe vers un chemin │
# └─────────────────────────────────────────────────────┘

# Créer un hard link
$ echo "contenu original" > original.txt
$ ln original.txt hardlink.txt
$ ls -lai original.txt hardlink.txt
→ 123456 -rw-r--r-- 2 alice alice 17 jan 10 original.txt
→ 123456 -rw-r--r-- 2 alice alice 17 jan 10 hardlink.txt
#  ↑ même inode          ↑ compteur de liens = 2

# Modifier via le hard link modifie l'original
$ echo "ajout" >> hardlink.txt
$ cat original.txt
→ contenu original
→ ajout

# Supprimer l'original : le hard link reste valide !
$ rm original.txt
$ cat hardlink.txt   # fonctionne toujours

# Créer un lien symbolique (symlink)
$ ln -s /etc/passwd lien_passwd
$ ls -la lien_passwd
→ lrwxrwxrwx 1 alice alice 11 jan 10 lien_passwd -> /etc/passwd
#  ↑ l = symlink

# Différences clés :
# Hard link : même partition, pas sur répertoires, survit à suppression source
# Symlink   : cross-partition, sur répertoires, cassé si source supprimée

# Trouver les liens brisés
$ find /home -type l ! -exec test -e {} \; -print
```

### 🔬 Exercice 2.1 — Gestion de fichiers

```bash
# Créer la structure suivante dans ~/tp_linux/niveau2/
# projet/
# ├── src/
# │   ├── main.c
# │   └── utils.c
# ├── docs/
# │   └── README.md
# └── config/
#     └── settings.conf

$ mkdir -p ~/tp_linux/niveau2/projet/{src,docs,config}
$ touch ~/tp_linux/niveau2/projet/src/{main.c,utils.c}
$ echo "# Mon Projet" > ~/tp_linux/niveau2/projet/docs/README.md
$ echo "debug=true" > ~/tp_linux/niveau2/projet/config/settings.conf

# Vérifier avec tree
$ tree ~/tp_linux/niveau2/

# Créer un symlink vers le fichier de config
$ ln -s ~/tp_linux/niveau2/projet/config/settings.conf ~/config_actif

# Vérifier
$ ls -la ~/config_actif
$ readlink -f ~/config_actif
```

---

## MODULE 4 — Types de Fichiers et Inodes

### 4.1 Les 7 types de fichiers Linux

```bash
# Premier caractère de ls -l :
# - : fichier ordinaire
# d : répertoire (directory)
# l : lien symbolique (symlink)
# c : fichier spécial caractère (terminal, clavier...)
# b : fichier spécial bloc (disque dur, partition)
# p : tube nommé (named pipe / FIFO)
# s : socket Unix

# Identifier le type avec file
$ file /bin/bash
→ /bin/bash: ELF 64-bit LSB pie executable...

$ file /etc/passwd
→ /etc/passwd: ASCII text

$ file /dev/sda
→ /dev/sda: block special (8/0)

$ file /dev/tty
→ /dev/tty: character special (5/0)

# Lister les fichiers spéciaux dans /dev
$ ls -la /dev/ | grep "^c"    # caractères
$ ls -la /dev/ | grep "^b"    # blocs

# Créer un pipe nommé
$ mkfifo ~/tp_linux/niveau2/mon_pipe
$ ls -la ~/tp_linux/niveau2/mon_pipe
→ prw-r--r-- 1 alice alice 0 jan 10 mon_pipe
#  ↑ p = pipe
```

### 4.2 Les inodes en détail

```bash
# Qu'est-ce qu'un inode ?
# Chaque fichier possède un inode qui contient :
# - Numéro d'inode (identifiant unique par filesystem)
# - Type de fichier
# - Permissions
# - Propriétaire (UID) et groupe (GID)
# - Taille
# - Timestamps : atime (accès), mtime (modification), ctime (changement inode)
# - Nombre de liens (hard links)
# - Pointeurs vers les blocs de données

# Afficher l'inode d'un fichier
$ ls -i /etc/passwd
→ 123456 /etc/passwd

# Informations complètes de l'inode
$ stat /etc/passwd
→ File: /etc/passwd
→ Size: 2847      Blocks: 8      IO Block: 4096   regular file
→ Device: 802h/2050d  Inode: 123456  Links: 1
→ Access: (0644/-rw-r--r--)  Uid: (0/root)  Gid: (0/root)
→ Access: 2024-01-10 09:00:00
→ Modify: 2024-01-05 08:00:00
→ Change: 2024-01-05 08:00:00

# Nombre d'inodes disponibles
$ df -i
→ Filesystem     Inodes  IUsed  IFree  IUse% Mounted on
→ /dev/sda1     3276800  45678 3231122    2% /

# ⚠️ Un disque peut être plein en inodes sans être plein en espace !
```

### 4.3 Timestamps et leur manipulation

```bash
# Les 3 timestamps principaux :
# atime : dernière lecture (lecture du contenu)
# mtime : dernière écriture (contenu modifié)
# ctime : dernier changement de métadonnées (chmod, chown, rename...)

# Afficher
$ stat fichier.txt | grep -E "(Access|Modify|Change)"

# Modifier mtime et atime avec touch
$ touch -t 202301011200 fichier.txt    # fixe à 2023-01-01 12:00
$ touch -m fichier.txt                 # met à jour seulement mtime

# ⚠️ ctime ne peut PAS être modifié par l'utilisateur
# (c'est une mesure de sécurité)

# Trouver des fichiers modifiés récemment
$ find /etc -mtime -1    # modifiés il y a moins de 24h
$ find /var -mtime +30   # non modifiés depuis plus de 30 jours
$ find / -newer /etc/passwd -type f 2>/dev/null
```

---

# ═══════════════════════════════════════
# NIVEAU 3 — DROITS ET PERMISSIONS
# ═══════════════════════════════════════

---

## MODULE 5 — Le Modèle UGO

### 5.1 Structure des permissions

```
Sortie de ls -l :
-rwxr-xr--  2  alice  devs  4096  jan 10  script.sh
│└──┴──┴──┘     │      │
│  │  │  │      │      └─ Groupe propriétaire
│  │  │  │      └─ Utilisateur propriétaire
│  │  │  └─ Permissions pour Others (autres)
│  │  └─ Permissions pour Group (groupe)
│  └─ Permissions pour User (propriétaire)
└─ Type de fichier (- = fichier, d = répertoire, l = symlink)

Signification des permissions :
┌──────────┬────────────────────────┬─────────────────────────┐
│ Symbole  │    Sur un fichier      │    Sur un répertoire    │
├──────────┼────────────────────────┼─────────────────────────┤
│   r (4)  │  Lire le contenu       │  Lister (ls)            │
│   w (2)  │  Modifier le contenu   │  Créer/supprimer dedans │
│   x (1)  │  Exécuter              │  Traverser (cd)         │
│   - (0)  │  Permission refusée    │  Permission refusée     │
└──────────┴────────────────────────┴─────────────────────────┘
```

### 5.2 Représentation octale

```
rwx = 4+2+1 = 7
rw- = 4+2+0 = 6
r-x = 4+0+1 = 5
r-- = 4+0+0 = 4
-wx = 0+2+1 = 3
-w- = 0+2+0 = 2
--x = 0+0+1 = 1
--- = 0+0+0 = 0

Exemples courants :
755 = rwxr-xr-x  → répertoire ou exécutable standard
644 = rw-r--r--  → fichier de configuration/données
600 = rw-------  → fichier privé (clé SSH)
777 = rwxrwxrwx  → ⚠️ DANGEREUX, éviter en production
750 = rwxr-x---  → exécutable accessible au groupe seulement
```

### 5.3 Règles d'application des permissions

```
⚠️ IMPORTANT : Les permissions sont évaluées dans l'ordre : User → Group → Others
   Dès qu'une règle correspond, elle est appliquée — les suivantes sont ignorées.

Exemple :
  Fichier : ---rwxrwx  alice  devs
  
  Si alice tente d'accéder → règle User (---) → REFUSÉ
  Même si alice est dans 'devs', la règle User prend le dessus !

Test pratique :
$ echo "test" > testfile
$ chmod 046 testfile       # ---r--rw-
$ cat testfile             # REFUSÉ (user = 0)
→ Permission denied
$ newgrp devs              # changer de groupe principal
$ cat testfile             # REFUSÉ aussi (group = 4 = r seulement pour lecture)
```

### 5.4 Le umask

```bash
# umask = masque de création de fichiers
# Permissions finales = permissions par défaut - umask

# Afficher le umask actuel
$ umask
→ 0022

# Décodage :
# Fichiers : défaut 666, avec umask 022 → 666 - 022 = 644 (rw-r--r--)
# Répertoires : défaut 777, avec umask 022 → 777 - 022 = 755 (rwxr-xr-x)

# Vérifier
$ touch test_umask && ls -la test_umask
→ -rw-r--r-- 1 alice alice 0 jan 10 test_umask

$ mkdir test_dir && ls -ld test_dir
→ drwxr-xr-x 2 alice alice 4096 jan 10 test_dir

# Changer le umask (temporaire, pour la session)
$ umask 027    # fichiers → 640, répertoires → 750

# umask permanent : l'ajouter dans ~/.bashrc ou ~/.profile
$ echo "umask 027" >> ~/.bashrc

# umask courants :
# 022 → standard (fichiers: 644, dossiers: 755)
# 027 → sécurisé (fichiers: 640, dossiers: 750) — others ne peuvent rien faire
# 077 → très restrictif (fichiers: 600, dossiers: 700) — privé total
```

### 🔬 Exercice 3.1 — Comprendre les permissions

```bash
# Créer une structure de test
$ cd ~/tp_linux/niveau3
$ mkdir -p test_perms/{public,prive,groupe}
$ echo "fichier public" > test_perms/public/readme.txt
$ echo "fichier privé" > test_perms/prive/secret.txt
$ echo "fichier groupe" > test_perms/groupe/shared.txt

# Appliquer des permissions variées
$ chmod 644 test_perms/public/readme.txt
$ chmod 600 test_perms/prive/secret.txt
$ chmod 660 test_perms/groupe/shared.txt

# Vérifier
$ ls -la test_perms/public/
$ ls -la test_perms/prive/
$ ls -la test_perms/groupe/

# Calculer manuellement :
# Quelle est la permission numérique de rw-r-x--x ?
# Réponse : 4+2+0 = 6, 4+0+1 = 5, 0+0+1 = 1 → 651
```

---

## MODULE 6 — chmod, chown, chgrp

### 6.1 chmod — changer les permissions

```bash
# ══════ MODE SYMBOLIQUE ══════

# Syntaxe : chmod [ugoa][+-=][rwx] fichier
# u = user, g = group, o = others, a = all

# Ajouter le droit d'exécution pour le propriétaire
$ chmod u+x script.sh

# Retirer le droit d'écriture pour le groupe et others
$ chmod go-w fichier.txt

# Donner lecture+exécution à tous
$ chmod a+rx programme

# Définir des droits exacts (= remplace tout)
$ chmod u=rwx,g=rx,o= fichier    # 750

# ══════ MODE OCTAL ══════

$ chmod 755 script.sh      # rwxr-xr-x
$ chmod 644 config.txt     # rw-r--r--
$ chmod 600 id_rsa         # rw------- (clé SSH)
$ chmod 777 /tmp/shared    # rwxrwxrwx (⚠️ dangereux)

# ══════ RÉCURSIF ══════

# Appliquer récursivement
$ chmod -R 755 /var/www/html/

# ⚠️ Problème du -R : met 755 sur fichiers ET répertoires
# Solution : traiter séparément
$ find /var/www/html -type d -exec chmod 755 {} \;
$ find /var/www/html -type f -exec chmod 644 {} \;

# Voir les changements avec --changes
$ chmod --changes 644 *.txt
```

### 6.2 chown — changer le propriétaire

```bash
# Changer le propriétaire (root requis)
# sudo chown nouveau_user fichier

$ sudo chown root fichier.txt
$ sudo chown alice:devs fichier.txt    # user ET groupe
$ sudo chown :devs fichier.txt         # seulement le groupe
$ sudo chown alice: fichier.txt        # user + groupe primaire de alice

# Récursif
$ sudo chown -R alice:alice /home/alice/

# Chown avec préservation des symlinks
$ sudo chown -h alice symlink.txt      # modifie le lien, pas la cible

# Trouver tous les fichiers appartenant à un user
$ find /home -user alice -type f

# Trouver les fichiers sans propriétaire valide (orphelins)
$ find / -nouser -o -nogroup 2>/dev/null
```

### 6.3 chgrp — changer le groupe

```bash
# Changer le groupe
$ chgrp devs fichier.txt
$ chgrp -R webteam /var/www/

# Lister les groupes auxquels appartient un utilisateur
$ groups alice
→ alice : alice adm cdrom sudo dip plugdev lpadmin

$ id alice
→ uid=1001(alice) gid=1001(alice) groups=1001(alice),27(sudo),1002(devs)
```

### 6.4 Gestion des utilisateurs et groupes

```bash
# Créer des utilisateurs pour les exercices
$ sudo useradd -m -s /bin/bash bob
$ sudo useradd -m -s /bin/bash charlie
$ sudo passwd bob              # définir mot de passe

# Créer des groupes
$ sudo groupadd devs
$ sudo groupadd webteam

# Ajouter un utilisateur à un groupe
$ sudo usermod -aG devs alice
$ sudo usermod -aG devs bob

# Vérifier
$ getent group devs
→ devs:x:1002:alice,bob

# Changer de groupe principal temporairement
$ newgrp devs

# Voir les fichiers de configuration
$ cat /etc/passwd    # utilisateurs
$ cat /etc/group     # groupes
$ sudo cat /etc/shadow  # mots de passe hashés (root only)
```

### 🔬 Exercice 3.2 — Permissions collaboratives

```bash
# Scénario : créer un espace partagé entre alice et bob (groupe devs)

# 1. Créer un répertoire de projet partagé
$ sudo mkdir /srv/projet_devs
$ sudo chown alice:devs /srv/projet_devs
$ sudo chmod 2775 /srv/projet_devs
# (le 2 = SGID — expliqué dans le module suivant)

# 2. alice crée des fichiers
$ sudo -u alice bash -c 'echo "code source" > /srv/projet_devs/main.c'

# 3. bob peut-il lire ? écrire ?
$ sudo -u bob cat /srv/projet_devs/main.c
$ sudo -u bob echo "modification" >> /srv/projet_devs/main.c

# 4. Charlie (pas dans devs) peut-il accéder ?
$ sudo -u charlie ls /srv/projet_devs/

# Expliquer les résultats.
```

---

# ═══════════════════════════════════════
# NIVEAU 4 — ATTRIBUTS SPÉCIAUX
# ═══════════════════════════════════════

---

## MODULE 7 — SUID, SGID, Sticky Bit

### 7.1 SUID — Set User ID

```
┌──────────────────────────────────────────────────────────────┐
│  SUID : quand un exécutable est lancé, il tourne avec les    │
│  droits du PROPRIÉTAIRE du fichier, et non de l'utilisateur  │
│  qui l'exécute.                                              │
│                                                              │
│  Notation : s à la place du x du propriétaire               │
│  -rwsr-xr-x  (SUID + x)                                     │
│  -rwSr-xr-x  (SUID sans x — rare, suspect)                  │
│                                                              │
│  Valeur octale : 4000 (ex: 4755)                             │
└──────────────────────────────────────────────────────────────┘
```

```bash
# Exemple réel : /usr/bin/passwd
$ ls -la /usr/bin/passwd
→ -rwsr-xr-x 1 root root 68208 jan  1 /usr/bin/passwd
#     ↑ s = SUID

# passwd doit modifier /etc/shadow (owned by root)
# Grâce au SUID, il s'exécute avec les droits de root
# tout en étant lancé par un utilisateur normal

# Autres exemples courants
$ ls -la /usr/bin/sudo
$ ls -la /bin/su
$ ls -la /usr/bin/newgrp
$ ls -la /usr/bin/ping

# Activer le SUID
$ sudo chmod u+s monprogramme
$ sudo chmod 4755 monprogramme

# ⚠️ DANGER SUID : ne jamais l'appliquer sur des scripts shell
# Un script SUID interprété peut être contourné
# Linux ignore SUID sur les scripts pour cette raison

# Trouver tous les binaires SUID sur le système
$ find / -perm -4000 -type f 2>/dev/null
$ find / -perm /4000 -type f 2>/dev/null

# Lister avec propriétaire
$ find / -perm -4000 -type f -ls 2>/dev/null
```

### 7.2 SGID — Set Group ID

```
┌──────────────────────────────────────────────────────────────┐
│  SGID sur EXÉCUTABLE :                                       │
│    L'exécutable tourne avec les droits du GROUPE du fichier  │
│                                                              │
│  SGID sur RÉPERTOIRE :                                       │
│    Les nouveaux fichiers créés dedans héritent               │
│    automatiquement du groupe du répertoire                   │
│                                                              │
│  Notation : s à la place du x du groupe                     │
│  -rwxr-sr-x  (fichier)                                       │
│  drwxrwsr-x  (répertoire)                                    │
│                                                              │
│  Valeur octale : 2000 (ex: 2755)                             │
└──────────────────────────────────────────────────────────────┘
```

```bash
# Exemple : espace de travail collaboratif
$ sudo mkdir /srv/equipe
$ sudo chown root:devs /srv/equipe
$ sudo chmod 2775 /srv/equipe
$ ls -ld /srv/equipe
→ drwxrwsr-x 2 root devs 4096 jan 10 /srv/equipe
#         ↑ s = SGID

# Test : alice (dans devs) crée un fichier
$ sudo -u alice touch /srv/equipe/projet.txt
$ ls -la /srv/equipe/projet.txt
→ -rw-rw-r-- 1 alice devs 0 jan 10 projet.txt
#                    ↑ groupe hérité de /srv/equipe

# Sans SGID, le groupe serait celui d'alice (alice)
# Avec SGID, le groupe est devs → bob peut y accéder !

# Trouver les répertoires SGID
$ find / -perm -2000 -type d 2>/dev/null

# SGID sur exécutable (exemple : write/wall)
$ ls -la /usr/bin/write
→ -rwxr-sr-x 1 root tty ... /usr/bin/write
#        ↑ s = SGID (groupe tty)
```

### 7.3 Sticky Bit

```
┌──────────────────────────────────────────────────────────────┐
│  Sticky Bit sur RÉPERTOIRE :                                 │
│    Même si le répertoire est world-writable,                 │
│    seul le PROPRIÉTAIRE d'un fichier peut le supprimer       │
│    (ou le propriétaire du répertoire, ou root)               │
│                                                              │
│  Notation : t à la place du x des others                    │
│  drwxrwxrwt  (/tmp)                                          │
│                                                              │
│  Valeur octale : 1000 (ex: 1777)                             │
└──────────────────────────────────────────────────────────────┘
```

```bash
# /tmp est le cas classique
$ ls -ld /tmp
→ drwxrwxrwt 20 root root 4096 jan 10 /tmp
#           ↑ t = sticky bit

# Test du sticky bit
$ mkdir /tmp/test_sticky
$ chmod 1777 /tmp/test_sticky
$ ls -ld /tmp/test_sticky
→ drwxrwxrwt 2 alice alice 4096 jan 10 /tmp/test_sticky

# alice crée un fichier
$ touch /tmp/test_sticky/alice_file.txt

# bob tente de supprimer le fichier d'alice
$ sudo -u bob rm /tmp/test_sticky/alice_file.txt
→ rm: cannot remove '/tmp/test_sticky/alice_file.txt': Operation not permitted

# Sans sticky bit (chmod 777) bob pourrait le supprimer !

# Appliquer le sticky bit
$ sudo chmod +t /srv/partage
$ sudo chmod 1777 /srv/partage

# Trouver les répertoires avec sticky bit
$ find / -perm -1000 -type d 2>/dev/null
```

### 7.4 Récapitulatif des bits spéciaux

```
┌────────────┬────────┬──────────────┬────────────────────────────────┐
│   Bit      │ Valeur │  Notation ls │  Effet                         │
├────────────┼────────┼──────────────┼────────────────────────────────┤
│ SUID       │  4000  │  rws (user)  │ Fichier : run as owner         │
│ SGID       │  2000  │  rws (group) │ Fichier : run as group         │
│            │        │              │ Dossier : hérite du groupe     │
│ Sticky Bit │  1000  │  rwt (other) │ Dossier : only owner can rm    │
└────────────┴────────┴──────────────┴────────────────────────────────┘

Exemple combiné : SGID + Sticky sur répertoire
$ chmod 3775 /srv/equipe    # 2000 + 1000 + 775 = 3775
$ ls -ld /srv/equipe
→ drwxrwsr-t 2 root devs 4096 jan 10 /srv/equipe
#         ↑↑ s=SGID, t=Sticky
```

### 🔬 Exercice 4.1 — Exploiter les bits spéciaux

```bash
# Scénario : simuler le fonctionnement de /usr/bin/passwd

# 1. Créer un petit programme C pour tester le SUID
$ cat > /tmp/whoami_test.c << 'EOF'
#include <stdio.h>
#include <unistd.h>

int main() {
    printf("UID réel    : %d\n", getuid());
    printf("UID effectif : %d\n", geteuid());
    printf("GID réel    : %d\n", getgid());
    printf("GID effectif : %d\n", getegid());
    return 0;
}
EOF

$ gcc /tmp/whoami_test.c -o /tmp/whoami_test

# 2. Tester sans SUID
$ /tmp/whoami_test
→ UID réel     : 1001
→ UID effectif : 1001

# 3. Appliquer SUID et changer propriétaire
$ sudo chown root /tmp/whoami_test
$ sudo chmod u+s /tmp/whoami_test

# 4. Tester avec SUID
$ /tmp/whoami_test
→ UID réel     : 1001   ← alice
→ UID effectif : 0      ← root ! (grâce au SUID)
```

---

## MODULE 8 — Attributs Étendus (chattr / lsattr)

### 8.1 Introduction aux attributs étendus

```
Les attributs étendus sont des métadonnées supplémentaires
stockées dans l'inode, au-delà des permissions classiques.
Ils sont gérés par :
  chattr : modifier les attributs
  lsattr : lister les attributs

⚠️ Nécessitent souvent les droits root pour être modifiés.
⚠️ Fonctionnent uniquement sur ext2/ext3/ext4 (et btrfs pour certains).
```

### 8.2 Attributs principaux

```bash
# Lister les attributs d'un fichier
$ lsattr /etc/passwd
→ ----i--------e-- /etc/passwd
#      ↑ i = immutable !

# ══ ATTRIBUT i — Immutable ══
# Le fichier ne peut être ni modifié, ni supprimé, ni renommé
# Même par root !

$ sudo chattr +i fichier_important.txt
$ lsattr fichier_important.txt
→ ----i--------e-- fichier_important.txt

$ sudo rm fichier_important.txt
→ rm: cannot remove 'fichier_important.txt': Operation not permitted

$ echo "test" >> fichier_important.txt
→ -bash: fichier_important.txt: Operation not permitted

$ sudo mv fichier_important.txt autre_nom.txt
→ mv: cannot move: Operation not permitted

# Retirer l'attribut immutable
$ sudo chattr -i fichier_important.txt

# ══ ATTRIBUT a — Append only ══
# On ne peut qu'ajouter à la fin du fichier (parfait pour les logs)

$ sudo chattr +a /var/log/mon_app.log
$ echo "log entry" >> /var/log/mon_app.log    # OK
$ echo "override" > /var/log/mon_app.log      # REFUSÉ
→ -bash: /var/log/mon_app.log: Operation not permitted
$ sudo truncate /var/log/mon_app.log          # REFUSÉ

# ══ ATTRIBUT e — Extent format ══
# Automatiquement sur ext4 — indique que l'inode utilise les extents

# ══ ATTRIBUT s — Secure deletion ══
# Écrase avec des zéros à la suppression (sécurité)
$ sudo chattr +s fichier_sensible.txt

# ══ ATTRIBUT u — Undeletable ══
# Contenu préservé pour permettre la récupération

# ══ ATTRIBUT c — Compressed ══
# Stockage compressé (selon le filesystem)

# ══ ATTRIBUT d — No dump ══
# Exclu des sauvegardes avec dump
$ sudo chattr +d cache.tmp
```

### 8.3 Tableau complet des attributs

```
┌────────┬──────────────────────┬─────────────────────────────────────────┐
│ Attr.  │  Nom                 │  Effet                                  │
├────────┼──────────────────────┼─────────────────────────────────────────┤
│  a     │  Append only         │  Écriture en ajout uniquement           │
│  c     │  Compressed          │  Stockage compressé                     │
│  d     │  No dump             │  Ignoré par dump(8)                     │
│  e     │  Extent format       │  Utilise les extents (ext4 auto)        │
│  i     │  Immutable           │  Aucune modification possible           │
│  j     │  Journaling data     │  Données journalisées (ext3/4)          │
│  s     │  Secure delete       │  Zéros sur suppression                  │
│  S     │  Synchronous         │  Écritures synchrones                   │
│  t     │  No tail-merging     │  Pas de fusion de blocs partiels        │
│  T     │  Top dir hierarchy   │  Traité comme répertoire racine         │
│  u     │  Undeletable         │  Données préservées après suppression   │
└────────┴──────────────────────┴─────────────────────────────────────────┘
```

### 8.4 Extended Attributes (xattr)

```bash
# Les xattrs sont différents des attributs chattr
# Ils stockent des paires clé=valeur

# Installer les outils
$ sudo apt install attr

# Ajouter un xattr
$ setfattr -n user.commentaire -v "fichier confidentiel" rapport.pdf
$ setfattr -n user.auteur -v "alice" rapport.pdf

# Lire les xattr
$ getfattr -d rapport.pdf
→ # file: rapport.pdf
→ user.auteur="alice"
→ user.commentaire="fichier confidentiel"

# Xattr de sécurité (SELinux/AppArmor)
$ getfattr -n security.selinux /etc/passwd

# Supprimer un xattr
$ setfattr -x user.commentaire rapport.pdf
```

### 🔬 Exercice 4.2 — Protéger des fichiers critiques

```bash
# Scénario : sécuriser des fichiers de configuration critiques

# 1. Créer et sécuriser un fichier de config
$ echo "API_KEY=secret123" | sudo tee /etc/myapp.conf
$ sudo chattr +i /etc/myapp.conf

# 2. Tenter de le modifier (même en root)
$ sudo echo "MODIF=test" >> /etc/myapp.conf
# Que se passe-t-il ?

# 3. Créer un fichier de log sécurisé (append-only)
$ sudo touch /var/log/audit_secure.log
$ sudo chattr +a /var/log/audit_secure.log

# 4. Tester
$ echo "$(date): connexion alice" | sudo tee -a /var/log/audit_secure.log
$ sudo truncate -s 0 /var/log/audit_secure.log
# Que se passe-t-il ?

# 5. Vérifier tous les attributs
$ lsattr /etc/myapp.conf
$ lsattr /var/log/audit_secure.log
```

---

## MODULE 9 — ACL (Access Control Lists)

### 9.1 Pourquoi les ACL ?

```
Limitation du modèle UGO :
  Un fichier n'a qu'UN propriétaire et qu'UN groupe.
  On ne peut pas donner des droits différents à plusieurs users/groupes.

Avec les ACL, on peut définir des permissions granulaires :
  - alice : rw-
  - bob   : r--
  - charlie : ---
  - groupe devs : r-x
  - groupe sysadmin : rwx
```

### 9.2 Activer et utiliser les ACL

```bash
# Vérifier que les ACL sont actives
$ mount | grep acl
# Sur ext4 moderne, c'est activé par défaut

# Installer les outils si nécessaire
$ sudo apt install acl

# ══ COMMANDES PRINCIPALES ══

# Afficher les ACL d'un fichier
$ getfacl fichier.txt
→ # file: fichier.txt
→ # owner: alice
→ # group: alice
→ user::rw-        ← permissions propriétaire (classique)
→ group::r--       ← permissions groupe (classique)
→ other::r--       ← permissions others (classique)

# Ajouter des ACL
# setfacl -m u:utilisateur:permissions fichier
# setfacl -m g:groupe:permissions fichier

$ setfacl -m u:bob:rw- fichier.txt
$ setfacl -m u:charlie:--- fichier.txt
$ setfacl -m g:devs:r-x fichier.txt

# Vérifier
$ getfacl fichier.txt
→ # file: fichier.txt
→ # owner: alice
→ # group: alice
→ user::rw-
→ user:bob:rw-        ← ACL de bob
→ user:charlie:---    ← ACL de charlie
→ group::r--
→ group:devs:r-x      ← ACL du groupe devs
→ mask::rw-           ← masque effectif (expliqué après)
→ other::r--

# Présence d'ACL indiquée par + dans ls -l
$ ls -la fichier.txt
→ -rw-rw-r--+ 1 alice alice 0 jan 10 fichier.txt
#             ↑ + = ACL présentes
```

### 9.3 Le masque ACL

```bash
# Le masque définit les permissions MAXIMALES pour :
#   - les ACL utilisateur (sauf propriétaire)
#   - les ACL de groupe
#   - le groupe propriétaire standard

# La permission EFFECTIVE = ACL AND masque
# Exemple : ACL bob=rwx, masque=r-- → effectif=r--

# Modifier le masque
$ setfacl -m mask::r-- fichier.txt
$ getfacl fichier.txt
→ user:bob:rw-         #effective:r--
→ group::r--           #effective:r--
→ mask::r--

# Recalcul automatique du masque lors d'ajout d'ACL
$ setfacl -m u:bob:rwx fichier.txt
# Le masque s'ajuste pour ne pas bloquer bob
```

### 9.4 ACL par défaut sur répertoires

```bash
# Les ACL par défaut s'appliquent aux NOUVEAUX fichiers créés dans un répertoire

$ mkdir /srv/projet_acl
$ sudo chown alice:devs /srv/projet_acl

# Définir des ACL par défaut
$ setfacl -d -m u::rwx /srv/projet_acl      # propriétaire
$ setfacl -d -m g:devs:rwx /srv/projet_acl  # groupe devs
$ setfacl -d -m g::r-x /srv/projet_acl      # groupe propriétaire
$ setfacl -d -m o::--- /srv/projet_acl      # others : rien

# Vérifier
$ getfacl /srv/projet_acl
→ # file: projet_acl
→ # owner: alice
→ # group: devs
→ user::rwx
→ group::r-x
→ other::r-x
→ default:user::rwx
→ default:group:devs:rwx
→ default:group::r-x
→ default:other::---

# Test : alice crée un fichier
$ sudo -u alice touch /srv/projet_acl/nouveau.txt
$ getfacl /srv/projet_acl/nouveau.txt
# → les ACL par défaut ont été héritées !

# Supprimer toutes les ACL
$ setfacl -b fichier.txt         # ACL spécifiques
$ setfacl -k repertoire/         # ACL par défaut seulement
$ setfacl -b -k repertoire/      # tout supprimer
```

### 9.5 Sauvegarde et restauration des ACL

```bash
# Sauvegarder toutes les ACL d'une arborescence
$ getfacl -R /srv/projet_acl > acl_backup.txt

# Restaurer
$ setfacl --restore=acl_backup.txt
```

### 🔬 Exercice 4.3 — Scénario multi-équipes

```bash
# Scénario : /srv/documents doit être accessible ainsi :
# - alice (chef) : lecture + écriture + exécution
# - bob (dev) : lecture + écriture
# - charlie (stagiaire) : lecture seule
# - groupe rh : aucun accès
# - groupe it : lecture + exécution

$ sudo mkdir /srv/documents
$ sudo chown alice:alice /srv/documents

# Appliquer les ACL
$ sudo setfacl -m u:alice:rwx /srv/documents
$ sudo setfacl -m u:bob:rw- /srv/documents
$ sudo setfacl -m u:charlie:r-- /srv/documents
$ sudo setfacl -m g:rh:--- /srv/documents
$ sudo setfacl -m g:it:r-x /srv/documents

# Vérifier chaque cas
$ sudo -u alice ls /srv/documents     # OK
$ sudo -u bob touch /srv/documents/f  # OK
$ sudo -u charlie rm /srv/documents/f # REFUSÉ ?
$ sudo -u charlie cat /srv/documents/f # OK ?

# Ajouter des ACL par défaut pour les nouveaux fichiers
$ sudo setfacl -d -m u:bob:rw- /srv/documents
$ sudo setfacl -d -m u:charlie:r-- /srv/documents
```

---

# ═══════════════════════════════════════
# NIVEAU 5 — AUDIT ET SÉCURITÉ
# ═══════════════════════════════════════

---

## MODULE 10 — Audit du Système de Fichiers

### 10.1 find — L'outil d'audit indispensable

```bash
# ══════ RECHERCHE PAR PERMISSIONS ══════

# Trouver tous les fichiers SUID
$ find / -perm -4000 -type f 2>/dev/null
$ find / -perm /4000 -type f -ls 2>/dev/null

# Trouver tous les fichiers SGID
$ find / -perm -2000 -type f 2>/dev/null

# Trouver SUID et SGID ensemble
$ find / -perm /6000 -type f 2>/dev/null

# Fichiers world-writable (écriture par tous — DANGER)
$ find / -perm -0002 -type f 2>/dev/null
$ find / -perm -0002 ! -type l 2>/dev/null  # exclure symlinks

# Répertoires world-writable
$ find / -perm -0002 -type d 2>/dev/null

# Fichiers avec permissions dangereuses 777
$ find / -perm 777 -type f 2>/dev/null

# ══════ RECHERCHE PAR PROPRIÉTAIRE ══════

# Fichiers sans propriétaire (orphelins)
$ find / -nouser 2>/dev/null
$ find / -nogroup 2>/dev/null

# Fichiers appartenant à root
$ find /home -user root -type f 2>/dev/null

# Fichiers appartenant à un UID numérique (user supprimé)
$ find / -uid 1234 2>/dev/null

# ══════ RECHERCHE TEMPORELLE ══════

# Fichiers modifiés dans les dernières 24h
$ find /etc -mtime -1 -type f

# Fichiers modifiés dans la dernière heure
$ find /var -mmin -60 -type f

# Fichiers accédés dans les 7 derniers jours
$ find /home -atime -7 -type f

# Fichiers plus récents qu'un fichier de référence
$ find /etc -newer /etc/passwd -type f

# ══════ RECHERCHE AVANCÉE ══════

# Combiner plusieurs critères
$ find /home -user alice -name "*.sh" -perm -u+x

# Fichiers volumineux
$ find / -size +100M -type f 2>/dev/null

# Fichiers vides
$ find /var/log -size 0 -type f

# Fichiers avec un nombre spécifique de liens (hard links)
$ find / -links +3 -type f 2>/dev/null

# Fichiers cachés (commençant par .)
$ find /home -name ".*" -type f

# Exécuter une commande sur chaque résultat
$ find /tmp -type f -mtime +7 -exec rm {} \;
$ find / -perm -4000 -exec ls -la {} \; 2>/dev/null
```

### 10.2 Audit des logs système

```bash
# ══════ JOURNAUX PRINCIPAUX ══════

# Journal systemd (moderne)
$ journalctl -xe                      # journal avec erreurs
$ journalctl -u ssh                   # logs du service SSH
$ journalctl --since "1 hour ago"     # dernière heure
$ journalctl -p err                   # seulement les erreurs
$ journalctl -b                       # boot actuel
$ journalctl -b -1                    # boot précédent

# Logs classiques dans /var/log
$ tail -f /var/log/syslog             # temps réel
$ tail -f /var/log/auth.log           # authentifications
$ grep "Failed password" /var/log/auth.log
$ grep "sudo" /var/log/auth.log
$ grep "CRON" /var/log/syslog

# Connexions récentes
$ last                                # historique des connexions
$ lastb                               # tentatives échouées
$ lastlog                             # dernière connexion de chaque user
$ w                                   # utilisateurs connectés maintenant
$ who                                 # idem

# ══════ AUDIT AVEC AUDITD ══════

# Installer auditd
$ sudo apt install auditd

# Démarrer le service
$ sudo systemctl start auditd
$ sudo systemctl enable auditd

# Ajouter des règles d'audit
# Surveiller les accès à /etc/passwd
$ sudo auditctl -w /etc/passwd -p rwxa -k passwd_watch

# Surveiller les accès à /etc/shadow
$ sudo auditctl -w /etc/shadow -p rwxa -k shadow_watch

# Surveiller une commande
$ sudo auditctl -a always,exit -F exe=/usr/bin/passwd -k passwd_exec

# Lire les logs d'audit
$ sudo ausearch -k passwd_watch
$ sudo ausearch -k shadow_watch --start today
$ sudo ausearch -m USER_AUTH --start today   # authentifications

# Rapport d'audit
$ sudo aureport --summary
$ sudo aureport -au                          # rapport authentifications
$ sudo aureport --file                       # rapport accès fichiers
```

### 10.3 Vérification d'intégrité avec AIDE

```bash
# AIDE (Advanced Intrusion Detection Environment)
$ sudo apt install aide

# Initialiser la base de données de référence
$ sudo aide --init
$ sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Vérifier l'intégrité (comparer avec la référence)
$ sudo aide --check

# Sortie typique d'une intrusion :
→ AIDE found differences between database and filesystem!!
→
→ changed: /etc/passwd
→   Permissions   : -rw-r--r-- | -rwsr--r--
→   Size          : 2847 | 2850
→   MD5           : abc123... | def456...

# Mettre à jour après changements légitimes
$ sudo aide --update
```

### 10.4 Vérification d'intégrité des packages

```bash
# Debian/Ubuntu : vérifier les fichiers modifiés
$ sudo dpkg --verify

# Afficher les fichiers modifiés depuis l'installation
$ sudo debsums -c

# RPM (RHEL/CentOS) : vérifier les fichiers modifiés
$ sudo rpm -Va 2>/dev/null | grep -v "^.......T"

# Signification des lettres dans rpm -Va :
# S = taille modifiée
# M = permissions modifiées
# 5 = MD5 modifié
# U = propriétaire modifié
# G = groupe modifié
# T = timestamp modifié
```

---

## MODULE 11 — Recherche de Failles et Hardening

### 11.1 Script d'audit de sécurité

```bash
#!/bin/bash
# Script d'audit de sécurité du système de fichiers
# Sauvegarder dans : ~/tp_linux/niveau5/audit_fs.sh

echo "════════════════════════════════════════════"
echo "        AUDIT SÉCURITÉ SYSTÈME DE FICHIERS  "
echo "════════════════════════════════════════════"
echo "Date : $(date)"
echo "Hôte : $(hostname)"
echo ""

echo "▶ 1. Fichiers SUID"
echo "─────────────────────────────────────────"
find / -perm -4000 -type f -ls 2>/dev/null
echo ""

echo "▶ 2. Fichiers SGID"
echo "─────────────────────────────────────────"
find / -perm -2000 -type f -ls 2>/dev/null
echo ""

echo "▶ 3. Fichiers world-writable"
echo "─────────────────────────────────────────"
find / -perm -0002 -type f ! -path "/proc/*" -ls 2>/dev/null
echo ""

echo "▶ 4. Répertoires world-writable (hors /tmp)"
echo "─────────────────────────────────────────"
find / -perm -0002 -type d ! -path "/tmp" ! -path "/proc/*" -ls 2>/dev/null
echo ""

echo "▶ 5. Fichiers sans propriétaire"
echo "─────────────────────────────────────────"
find / -nouser -o -nogroup 2>/dev/null | grep -v "^/proc"
echo ""

echo "▶ 6. Fichiers .rhosts et .netrc"
echo "─────────────────────────────────────────"
find /home -name ".rhosts" -o -name ".netrc" 2>/dev/null
echo ""

echo "▶ 7. Fichiers authorized_keys"
echo "─────────────────────────────────────────"
find /home -name "authorized_keys" -ls 2>/dev/null
find /root -name "authorized_keys" -ls 2>/dev/null
echo ""

echo "▶ 8. Crontabs utilisateurs"
echo "─────────────────────────────────────────"
ls -la /var/spool/cron/crontabs/ 2>/dev/null
ls -la /etc/cron* 2>/dev/null
echo ""

echo "▶ 9. Fichiers avec attribut immutable"
echo "─────────────────────────────────────────"
find / -xdev -exec lsattr {} \; 2>/dev/null | grep "\-i-"
echo ""

echo "▶ 10. Umask des utilisateurs"
echo "─────────────────────────────────────────"
grep "umask" /etc/profile /etc/bashrc /etc/login.defs 2>/dev/null
echo ""

echo "════════════════════════════════════════════"
echo "              FIN DE L'AUDIT               "
echo "════════════════════════════════════════════"
```

### 11.2 Hardening du système de fichiers

```bash
# ══════ SÉCURISATION DES MONTAGES ══════

# Options de montage sécurisées dans /etc/fstab :
# nodev   : interdit les fichiers de périphériques
# nosuid  : désactive SUID/SGID
# noexec  : interdit l'exécution de programmes

# Exemple de /etc/fstab sécurisé :
# /dev/sda1  /          ext4  defaults,nodev             0 1
# /dev/sda2  /tmp       ext4  defaults,nodev,nosuid,noexec 0 2
# /dev/sda3  /home      ext4  defaults,nodev,nosuid        0 2
# /dev/sda4  /var       ext4  defaults,nodev,nosuid        0 2
# tmpfs      /dev/shm   tmpfs defaults,nodev,nosuid,noexec 0 0

# Remonter avec options (sans redémarrer)
$ sudo mount -o remount,noexec,nosuid /tmp

# ══════ HARDENING /TMP ══════

# Créer /tmp en RAM avec tmpfs sécurisé
$ sudo mount -t tmpfs -o size=512M,nodev,nosuid,noexec tmpfs /tmp

# ══════ SÉCURISER /PROC ══════

# Masquer les infos des processus des autres utilisateurs
$ sudo mount -o remount,hidepid=2 /proc
# hidepid=0 : par défaut (tous voient tout)
# hidepid=1 : ls /proc mais pas de contenu
# hidepid=2 : processus des autres invisibles

# Permanent dans /etc/fstab :
# proc /proc proc defaults,hidepid=2 0 0

# ══════ PERMISSIONS CRITIQUES ══════

# Fichiers sensibles
$ sudo chmod 640 /etc/shadow       # root:shadow seulement
$ sudo chmod 600 /etc/gshadow
$ sudo chmod 644 /etc/passwd
$ sudo chmod 644 /etc/group

# Répertoires home sécurisés
$ sudo chmod 750 /home/alice       # alice + groupe alice seulement

# Clés SSH
$ chmod 700 ~/.ssh
$ chmod 600 ~/.ssh/id_rsa
$ chmod 644 ~/.ssh/id_rsa.pub
$ chmod 600 ~/.ssh/authorized_keys

# ══════ STICKY BIT SUR RÉPERTOIRES PARTAGÉS ══════

$ sudo chmod +t /tmp
$ sudo chmod +t /var/tmp
```

### 11.3 Checkliste de sécurité

```
✅ CHECKLIST SÉCURITÉ SYSTÈME DE FICHIERS

SUID/SGID :
  □ Inventorier tous les binaires SUID/SGID
  □ Supprimer le SUID sur les binaires non nécessaires
  □ Vérifier régulièrement les nouveaux SUID

PERMISSIONS :
  □ umask 027 (ou 022 minimum) pour tous les users
  □ /etc/shadow chmod 000 ou 640
  □ /boot accessible en lecture seule (chmod 700)
  □ Répertoires home chmod 700 ou 750
  □ Pas de fichiers 777

MONTAGES :
  □ /tmp en noexec,nosuid,nodev
  □ /home en nosuid
  □ /var en nosuid,nodev
  □ /proc avec hidepid=2

AUDIT :
  □ auditd installé et configuré
  □ Surveillance /etc/passwd, /etc/shadow, /etc/sudoers
  □ AIDE ou tripwire pour l'intégrité
  □ Rotation des logs configurée

ACL :
  □ Droits précis plutôt que groupes larges
  □ Revue régulière des ACL
```

---

## MODULE 12 — Cas Pratiques et Scénarios Réels

### 12.1 Scénario 1 — Serveur Web Multi-Sites

```bash
# Objectif : héberger plusieurs sites avec isolation des droits

# Structure
$ sudo mkdir -p /var/www/{site1,site2,commun}
$ sudo mkdir -p /var/www/site1/{html,logs,config}
$ sudo mkdir -p /var/www/site2/{html,logs,config}

# Utilisateurs et groupes
$ sudo useradd -r -s /sbin/nologin www-data
$ sudo groupadd site1-admins
$ sudo groupadd site2-admins

$ sudo usermod -aG site1-admins alice
$ sudo usermod -aG site2-admins bob
$ sudo usermod -aG site1-admins www-data
$ sudo usermod -aG site2-admins www-data

# Permissions site1
$ sudo chown -R root:site1-admins /var/www/site1/
$ sudo chmod -R 2750 /var/www/site1/         # SGID + rwxr-x---
$ sudo chmod -R 2770 /var/www/site1/html/    # www-data peut écrire
$ sudo chattr +a /var/www/site1/logs/access.log  # append only

# Permissions site2 (isolation totale)
$ sudo chown -R root:site2-admins /var/www/site2/
$ sudo chmod -R 2750 /var/www/site2/

# alice ne peut pas accéder à site2 !
$ sudo -u alice ls /var/www/site2/
→ Permission denied

# Répertoire commun avec ACL
$ sudo chown root:root /var/www/commun
$ sudo setfacl -m g:site1-admins:r-x /var/www/commun
$ sudo setfacl -m g:site2-admins:r-x /var/www/commun
```

### 12.2 Scénario 2 — Forensique et Détection d'Intrusion

```bash
# Objectif : détecter une intrusion hypothétique

# 1. Créer une "intrusion" simulée
$ sudo cp /bin/bash /tmp/.shell_hidden
$ sudo chmod 4755 /tmp/.shell_hidden   # SUID !
$ echo "backdoor data" > /tmp/.evil_file

# 2. Lancer l'audit
$ find / -perm -4000 -type f 2>/dev/null | sort > /tmp/suid_audit.txt

# 3. Comparer avec une baseline connue (simulée)
$ cat > /tmp/suid_baseline.txt << 'EOF'
/usr/bin/passwd
/usr/bin/sudo
/usr/bin/su
/usr/bin/mount
/usr/bin/umount
EOF

$ diff /tmp/suid_baseline.txt /tmp/suid_audit.txt
→ /tmp/.shell_hidden   ← ANOMALIE DÉTECTÉE !

# 4. Investiguer le fichier suspect
$ stat /tmp/.shell_hidden
$ file /tmp/.shell_hidden
$ ls -la /tmp/.shell_hidden
$ sha256sum /tmp/.shell_hidden    # empreinte du binaire

# 5. Vérifier les dernières modifications
$ find / -newer /tmp/suid_baseline.txt -perm -4000 2>/dev/null

# 6. Inspecter les logs d'accès
$ sudo ausearch -f /tmp/.shell_hidden 2>/dev/null
$ sudo grep "shell_hidden" /var/log/auth.log
```

### 12.3 Scénario 3 — Récupération de Droits Perdus

```bash
# Scénario : un admin a fait chmod 000 /bin/chmod par accident !

# Simuler le problème (dans un environnement de test UNIQUEMENT)
$ sudo chmod 000 /bin/chmod
→ Maintenant on ne peut plus utiliser chmod !

# Solution 1 : utiliser install
$ sudo install -m 755 /bin/chmod /bin/chmod

# Solution 2 : utiliser python pour changer les permissions
$ sudo python3 -c "import os; os.chmod('/bin/chmod', 0o755)"

# Solution 3 : depuis un autre shell avec les droits
$ sudo perl -e 'chmod 0755, "/bin/chmod"'

# Solution 4 : depuis le mode recovery / rescue
# Booter en mode rescue → accès root sans restriction

# Récupération si chmod sur /etc/shadow cassé
$ sudo python3 -c "import os; os.chmod('/etc/shadow', 0o640)"
$ sudo chown root:shadow /etc/shadow
```

### 12.4 Scénario 4 — Audit Complet d'un Serveur de Production

```bash
#!/bin/bash
# audit_production.sh — Script complet d'audit

RAPPORT="/var/log/audit_$(date +%Y%m%d_%H%M%S).txt"

{
echo "=== AUDIT PRODUCTION $(hostname) — $(date) ==="
echo ""

# Informations générales
echo "--- SYSTÈME ---"
uname -a
uptime
echo ""

# Partitions et espace disque
echo "--- DISQUE ---"
df -hT
echo ""
df -i
echo ""

# Points de montage et options
echo "--- MONTAGES ---"
findmnt --list
echo ""

# Utilisateurs connectés
echo "--- UTILISATEURS CONNECTÉS ---"
w
echo ""
last | head -20
echo ""

# Comptes utilisateurs
echo "--- COMPTES UTILISATEURS ---"
echo "Comptes avec UID 0 (root) :"
awk -F: '($3 == 0) {print}' /etc/passwd
echo ""
echo "Comptes sans mot de passe :"
sudo awk -F: '($2 == "" || $2 == "!!" ) {print $1}' /etc/shadow
echo ""

# SUID/SGID
echo "--- SUID/SGID ---"
find / -xdev \( -perm -4000 -o -perm -2000 \) -type f -ls 2>/dev/null
echo ""

# World-writable
echo "--- WORLD-WRITABLE ---"
find / -xdev -perm -0002 -type f 2>/dev/null | grep -v "^/proc"
echo ""

# Fichiers orphelins
echo "--- FICHIERS ORPHELINS ---"
find / -xdev \( -nouser -o -nogroup \) 2>/dev/null
echo ""

# Fichiers récemment modifiés dans /etc
echo "--- MODIFICATIONS RÉCENTES /etc (48h) ---"
find /etc -mtime -2 -type f -ls 2>/dev/null
echo ""

# .ssh directories
echo "--- CLÉS SSH ---"
find /home /root -name "authorized_keys" -ls 2>/dev/null
find /home /root -name "*.pem" -o -name "id_rsa" 2>/dev/null | xargs ls -la 2>/dev/null
echo ""

# ACL inhabituelles
echo "--- ACL PRÉSENTES ---"
find / -xdev -exec getfacl {} \; 2>/dev/null | grep -B2 "user:" | grep -v "^#"
echo ""

echo "=== FIN DU RAPPORT ==="
} | tee "$RAPPORT"

echo "Rapport sauvegardé : $RAPPORT"
```

---

# ANNEXES

---

## ANNEXE A — Récapitulatif des Commandes

```
┌────────────────────────────────────────────────────────────────────────┐
│                    RÉFÉRENCE RAPIDE                                     │
├──────────────┬─────────────────────────────────────────────────────────┤
│ ls -la       │ Lister avec permissions                                  │
│ stat         │ Informations complètes (inode, timestamps...)            │
│ file         │ Type d'un fichier                                        │
│ find         │ Recherche selon critères (droits, user, date...)         │
├──────────────┼─────────────────────────────────────────────────────────┤
│ chmod        │ Modifier les permissions (symbolique ou octal)           │
│ chown        │ Changer le propriétaire                                  │
│ chgrp        │ Changer le groupe                                        │
│ umask        │ Afficher/modifier le masque de création                  │
├──────────────┼─────────────────────────────────────────────────────────┤
│ chattr       │ Modifier les attributs étendus (immutable, append...)    │
│ lsattr       │ Lister les attributs étendus                             │
│ setfattr     │ Définir des xattributs (user.*)                          │
│ getfattr     │ Lire les xattributs                                      │
├──────────────┼─────────────────────────────────────────────────────────┤
│ setfacl      │ Définir des ACL                                          │
│ getfacl      │ Lire les ACL                                             │
├──────────────┼─────────────────────────────────────────────────────────┤
│ mount        │ Monter un système de fichiers                            │
│ umount       │ Démonter                                                 │
│ df -hT       │ Espace disque par partition (avec type)                  │
│ df -i        │ Utilisation des inodes                                   │
│ du -sh       │ Taille d'un répertoire                                   │
│ findmnt      │ Arborescence des montages                                │
├──────────────┼─────────────────────────────────────────────────────────┤
│ ln -s        │ Créer un lien symbolique                                 │
│ ln           │ Créer un hard link                                       │
│ readlink -f  │ Résoudre un symlink                                      │
└──────────────┴─────────────────────────────────────────────────────────┘
```

## ANNEXE B — Valeurs octales de référence

```
Fichiers courants :
  400  r--------  Lecture seule par le propriétaire (très restrictif)
  444  r--r--r--  Lecture seule pour tous
  600  rw-------  Lecture/écriture propriétaire seul (clés privées)
  640  rw-r-----  Lecture pour le groupe (config sensible)
  644  rw-r--r--  Standard pour les fichiers de données
  660  rw-rw----  Lecture/écriture propriétaire + groupe
  664  rw-rw-r--  Comme 644 mais groupe peut écrire
  666  rw-rw-rw-  ⚠️ Tout le monde peut lire/écrire
  700  rwx------  Exécutable privé
  711  rwx--x--x  Exécutable par tous, données privées
  750  rwxr-x---  Standard exécutable avec groupe
  755  rwxr-xr-x  Standard pour exécutables et répertoires
  775  rwxrwxr-x  Répertoire collaboratif groupe + lisible
  777  rwxrwxrwx  ⚠️⚠️ Dangereux — éviter absolument

Avec bits spéciaux :
  1755 rwxr-xr-t  Sticky (ex: /tmp sécurisé)
  2755 rwxr-sr-x  SGID sur exécutable
  2775 rwxrwsr-x  SGID sur répertoire collaboratif
  4755 rwsr-xr-x  SUID standard (ex: passwd)
  4711 rws--x--x  SUID minimal
```

## ANNEXE C — Diagnostic rapide

```bash
# Pourquoi est-ce que je ne peux pas accéder à ce fichier ?
$ namei -l /chemin/vers/fichier
# Affiche les permissions de chaque composant du chemin

# Qui a le droit sur ce fichier ? (ACL incluses)
$ getfacl /chemin/vers/fichier

# Sous quel utilisateur/groupe tourne ce processus ?
$ ps aux | grep processus
$ cat /proc/PID/status | grep -E "Uid|Gid"

# Quels fichiers un processus a ouvert ?
$ sudo lsof -p PID

# Quel processus utilise ce fichier ?
$ sudo lsof /chemin/vers/fichier
$ sudo fuser /chemin/vers/fichier
```

---

## ÉVALUATION FINALE

### Exercice synthèse (niveau expert)

```
Vous êtes administrateur système. Un collègue vous signale des comportements
suspects. Votre mission :

1. AUDIT INITIAL
   a) Lancer le script audit_production.sh
   b) Identifier tous les binaires SUID anormaux
   c) Trouver les fichiers world-writable hors /tmp

2. CONFIGURATION SÉCURISÉE
   a) Créer la structure suivante avec les bons droits :
      /srv/entreprise/
      ├── rh/          → RH : rwx | Autres : rien
      ├── finance/     → Finance : rwx | Direction : r-- | Autres : rien
      ├── it/          → IT : rwx | Tous-lecture : r-- | Autres : rien
      └── direction/   → Direction : rwx | Autres : rien

   b) Utiliser les ACL pour les accès croisés
   c) Appliquer le SGID sur tous les répertoires
   d) Protéger les logs de chaque département avec chattr +a

3. HARDENING
   a) Sécuriser les options de montage de /tmp et /home
   b) Vérifier et corriger les umask des utilisateurs
   c) Mettre en place auditd pour surveiller /srv/entreprise/

4. DOCUMENTATION
   Rédiger un rapport listant :
   - Les failles trouvées
   - Les corrections appliquées
   - Les commandes exactes utilisées
```

---

*TP rédigé pour une progression complète de zéro à expert*
*Testez toujours dans un environnement isolé (VM) avant la production*
