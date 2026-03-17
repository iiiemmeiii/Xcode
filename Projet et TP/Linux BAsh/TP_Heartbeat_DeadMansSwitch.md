# TP — Heartbeat & Dead Man's Switch
### De Zéro à Expert · Théorie · Implémentation · Production · Cybersécurité

---

> **Public visé** : Débutants → Architectes système / DevSecOps  
> **Durée estimée** : 8 à 12 heures  
> **Environnement** : Linux (Bash, Python 3, systemd) — une ou plusieurs VMs recommandées  
> **Convention** : `$` = user standard · `#` = root · `→` = sortie attendue · `⚠️` = danger · `💡` = astuce

---

## TABLE DES MATIÈRES

```
NIVEAU 1 — FONDATIONS THÉORIQUES
  Module 1 : Comprendre le Heartbeat
  Module 2 : Comprendre le Dead Man's Switch
  Module 3 : Différences, cas d'usage, risques

NIVEAU 2 — PREMIERS SCRIPTS BASH
  Module 4 : Heartbeat basique en Bash
  Module 5 : Dead Man's Switch basique en Bash
  Module 6 : Exercices de consolidation

NIVEAU 3 — IMPLÉMENTATION PYTHON
  Module 7 : Heartbeat robuste en Python
  Module 8 : Dead Man's Switch robuste en Python
  Module 9 : Communication réseau (client/serveur)

NIVEAU 4 — INTÉGRATION SYSTÈME
  Module 10 : Systemd — services et timers
  Module 11 : Surveillance multi-nœuds
  Module 12 : Alertes et actions automatisées

NIVEAU 5 — EXPERT & PRODUCTION
  Module 13 : Heartbeat distribué avec Redis/API
  Module 14 : Dead Man's Switch cryptographique
  Module 15 : Cas réels — Cybersécurité & Haute Disponibilité
  Module 16 : Challenge final
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 1 — FONDATIONS THÉORIQUES
# ═══════════════════════════════════════════════════

---

## MODULE 1 — Comprendre le Heartbeat

### 1.1 Définition et analogie biologique

Le terme **heartbeat** (battement de cœur) vient directement de la biologie. Un médecin pose un stéthoscope : tant qu'il entend le cœur battre, le patient est vivant. Si le silence s'installe, c'est une urgence.

En informatique, c'est exactement le même principe :

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODÈLE HEARTBEAT                              │
│                                                                  │
│   ÉMETTEUR                          RÉCEPTEUR (Moniteur)        │
│   ─────────                         ─────────────────────       │
│                                                                  │
│   t=0s  ──→ [PING / "alive"] ──→   ✓ reçu, timer reset         │
│   t=5s  ──→ [PING / "alive"] ──→   ✓ reçu, timer reset         │
│   t=10s ──→ [PING / "alive"] ──→   ✓ reçu, timer reset         │
│   t=15s  ✗  (panne / crash)        ⚠ timer expire              │
│   t=20s                             🔴 ALERTE DÉCLENCHÉE        │
│                                     → restart / notification    │
└─────────────────────────────────────────────────────────────────┘

Formule fondamentale :
  Timeout = Intervalle × (1 + tolérance)
  Ex: signal toutes les 5s, timeout = 5 × 1.5 = 7.5s
```

### 1.2 Anatomie d'un heartbeat

Un heartbeat se compose de **4 éléments** :

```
1. L'ÉMETTEUR (Sender)
   → Le processus/service qui envoie le signal
   → Doit être léger, non bloquant
   → Doit survivre aux erreurs internes

2. LE SIGNAL (Payload)
   → Peut être vide (juste un ping TCP)
   → Peut contenir des métriques (CPU, état, version)
   → Format : HTTP GET, UDP packet, fichier touch, socket...

3. LE CANAL (Channel)
   → TCP/IP, UDP, fichier partagé, base de données, Redis...
   → Doit être indépendant du système surveillé (sinon faux positif)

4. LE RÉCEPTEUR/MONITEUR (Watcher)
   → Attend le signal dans un délai maximum (timeout)
   → Déclenche une action si le délai expire
   → Doit lui-même être hautement disponible
```

### 1.3 Les types de heartbeat

```
TYPE              MÉCANISME              USAGE TYPIQUE
──────────────    ─────────────────      ─────────────────────────
Fichier touch     touch /tmp/alive       Scripts locaux, cron
HTTP GET          curl /health           Microservices, APIs
TCP keepalive     socket persistant      Bases de données, clusters
UDP ping          datagramme léger       Haute fréquence, IoT
Base de données   UPDATE timestamp       Applications distribuées
Message broker    topic Kafka/RabbitMQ   Architectures événementielles
DNS TTL           enregistrement DNS     CDN, load balancers
```

---

## MODULE 2 — Comprendre le Dead Man's Switch

### 2.1 Origine et principe

Le **Dead Man's Switch** (DMS) vient du ferroviaire au XIXe siècle. Le conducteur de locomotive devait maintenir une poignée enfoncée. S'il lâchait (mort, évanouissement), les freins s'activaient automatiquement.

```
┌─────────────────────────────────────────────────────────────────┐
│                  MODÈLE DEAD MAN'S SWITCH                        │
│                                                                  │
│   OPÉRATEUR                         TIMER (Gardien)             │
│   ─────────                         ──────────────              │
│                                                                  │
│   t=0h  ──→ [RESET "je suis là"] → Timer = 24h                  │
│   t=12h ──→ [RESET "je suis là"] → Timer = 24h                  │
│   t=24h ──→ [RESET "je suis là"] → Timer = 24h                  │
│   t=36h  ✗  (disparu / incapacité)                              │
│   t=48h                             ⏰ Timer expire              │
│                                     🔴 ACTION IRRÉVERSIBLE      │
│                                     → publication / alerte      │
│                                     → destruction clé           │
│                                     → notification d'urgence    │
└─────────────────────────────────────────────────────────────────┘

DIFFÉRENCE CLÉ avec heartbeat :
  Heartbeat : "agis si je ne réponds PLUS"
  DMS        : "agis si je ne confirme PAS activement que tout va bien"
```

### 2.2 Cas d'usage réels

```
INFORMATIQUE / CYBERSÉCURITÉ :
  ✦ Julian Assange (WikiLeaks) : fichiers chiffrés auto-publiés
    si son serveur DMS n'est pas reset depuis son incarcération
  ✦ Journalistes sous régimes autoritaires : "insurance file"
  ✦ Kill switch de malware (auto-destruction si C2 silencieux)
  ✦ Rotation automatique de secrets si l'admin disparaît
  ✦ Backdoor d'urgence si le système de prod ne répond plus

HAUTE DISPONIBILITÉ :
  ✦ Fencing / STONITH en cluster : si le nœud ne confirme pas,
    il est "stonithé" (éteint de force) pour éviter le split-brain
  ✦ Kubernetes Pod eviction : pod supprimé si pas de heartbeat kubelet
  ✦ Lease de leader Raft/etcd : leader remplacé s'il ne renouvelle pas

PHYSIQUE / INDUSTRIEL :
  ✦ Conducteurs de trains, tracteurs, nacelles élévatrices
  ✦ Centrales nucléaires (procédures d'arrêt automatique)
  ✦ Drones militaires (RTH si signal perdu)
```

### 2.3 Anatomie d'un DMS

```
1. LE TIMER (Countdown)
   → Compte à rebours configuré (ex: 24h, 7 jours...)
   → Se reset sur confirmation reçue
   → Irréversible une fois expiré (selon implémentation)

2. LA CONFIRMATION (Check-in)
   → Action explicite de l'opérateur
   → Peut nécessiter une authentification forte
   → Peut être multi-facteur (clé + code + localisation)

3. L'ACTION (Trigger)
   → Doit être fiable même si le système principal est down
   → Doit être exécutée depuis un système EXTERNE indépendant
   → Exemples : email, publication, destruction, alerte, failover

4. LE CANAL DE SECOURS
   → Distinct du canal principal
   → Idéalement sur infrastructure différente (autre cloud, autre pays)
```

---

## MODULE 3 — Différences, Cas d'Usage, Risques

### 3.1 Tableau comparatif

```
┌─────────────────────┬──────────────────────┬────────────────────────┐
│  Critère            │  Heartbeat           │  Dead Man's Switch     │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ Direction           │ Émetteur → Moniteur  │ Opérateur → Timer      │
│ Signal              │ "Je vis"             │ "Je confirme OK"       │
│ Action si silence   │ Alerte / restart     │ Déclenchement          │
│ Réversibilité       │ Toujours réversible  │ Souvent irréversible   │
│ Fréquence           │ Secondes / minutes   │ Heures / jours         │
│ Automatisme         │ Total (machine)      │ Partiel (humain requis)│
│ Objectif principal  │ Détection de panne   │ Garantie d'action      │
│ Risque principal    │ Faux positif         │ Déclenchement accidentel│
└─────────────────────┴──────────────────────┴────────────────────────┘
```

### 3.2 Les pièges classiques

```
HEARTBEAT — PIÈGES :
  ⚠️  Faux négatif : le service répond au ping mais est planté en interne
      → Solution : healthcheck fonctionnel (tester la vraie fonctionnalité)
  
  ⚠️  Canal partagé : si le réseau tombe, le heartbeat échoue
      mais le service est vivant → faux positif
      → Solution : canaux redondants, timeouts longs
  
  ⚠️  Cascade d'alertes : 100 nœuds tombent → 100 alertes simultanées
      → Solution : déduplication, agrégation

DEAD MAN'S SWITCH — PIÈGES :
  ⚠️  Déclenchement accidentel : oubli du check-in → catastrophe
      → Solution : alertes préventives avant expiration, délai de grâce
  
  ⚠️  Compromission du timer : si l'attaquant contrôle le DMS,
      il peut l'empêcher de se déclencher
      → Solution : DMS sur infrastructure totalement séparée
  
  ⚠️  Action trop destructrice : une fois lancée, impossible d'annuler
      → Solution : période de grâce + confirmation de l'action
```

### 🔬 Exercice 1.1 — Réflexion

```
Avant de coder, répondez à ces questions :

1. Un service web répond "200 OK" à /health mais sa base de données
   est coupée. Son heartbeat est-il fiable ? Que proposez-vous ?

2. Un journaliste configure un DMS avec délai de 48h.
   Il part en vacances sans accès internet pendant 3 jours.
   Que se passe-t-il ? Comment aurait-il dû configurer son DMS ?

3. Dans un cluster de 3 nœuds, le nœud A ne reçoit plus
   le heartbeat du nœud B. Le nœud C reçoit toujours B.
   Faut-il déclencher une action sur B ? Quel mécanisme utilisez-vous ?

4. Quelle est la différence entre un watchdog matériel et
   un watchdog logiciel ? Lequel est plus fiable ? Pourquoi ?
```

**Réponses :**

```
1. NON — heartbeat superficiel (HTTP 200 sans vérification interne)
   → Healthcheck profond : tester une vraie requête DB, vérifier les
     dépendances critiques, retourner 503 si une ressource est indisponible

2. Le DMS se déclenche → l'action irréversible s'exécute
   → Il aurait dû : configurer 72h+, avoir un accès backup (SMS, email)
     depuis n'importe où, ou déléguer le reset à quelqu'un de confiance

3. NON (pas directement) → le nœud A a peut-être un problème réseau
   → Quorum : décision uniquement si majorité (2/3) voit B en échec
   → Mécanisme : vote distribué, split-brain protection

4. Matériel (ex: /dev/watchdog Linux) : indépendant du noyau, se déclenche
   même si le noyau freeze. Plus fiable pour pannes kernel.
   Logiciel : peut être bloqué si le processus surveille lui-même
   → Production critique : toujours préférer matériel + logiciel en couches
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 2 — PREMIERS SCRIPTS BASH
# ═══════════════════════════════════════════════════

---

## MODULE 4 — Heartbeat Basique en Bash

### 4.1 Version 1 — Le plus simple possible

```bash
#!/bin/bash
# heartbeat_v1.sh — Émetteur heartbeat minimal
# Concept : toucher un fichier toutes les N secondes

HEARTBEAT_FILE="/tmp/heartbeat.touch"
INTERVAL=5  # secondes

echo "[HB] Démarrage heartbeat — PID $$"
echo "[HB] Fichier : $HEARTBEAT_FILE"
echo "[HB] Intervalle : ${INTERVAL}s"

while true; do
    touch "$HEARTBEAT_FILE"
    echo "[HB] $(date '+%H:%M:%S') — signal envoyé"
    sleep "$INTERVAL"
done
```

```bash
#!/bin/bash
# watcher_v1.sh — Moniteur heartbeat minimal
# Concept : vérifier si le fichier a été modifié récemment

HEARTBEAT_FILE="/tmp/heartbeat.touch"
TIMEOUT=15       # secondes avant alerte
CHECK_INTERVAL=3 # fréquence de vérification

echo "[WA] Démarrage watcher"
echo "[WA] Surveillance : $HEARTBEAT_FILE"
echo "[WA] Timeout : ${TIMEOUT}s"

while true; do
    if [ ! -f "$HEARTBEAT_FILE" ]; then
        echo "[WA] ⚠️  Fichier heartbeat absent !"
        sleep "$CHECK_INTERVAL"
        continue
    fi

    # Calculer l'âge du fichier en secondes
    NOW=$(date +%s)
    FILE_MTIME=$(stat -c %Y "$HEARTBEAT_FILE")
    AGE=$((NOW - FILE_MTIME))

    if [ "$AGE" -gt "$TIMEOUT" ]; then
        echo "[WA] 🔴 ALERTE — Heartbeat silencieux depuis ${AGE}s !"
        echo "[WA] Action : envoyer une notification..."
        # Action ici (email, restart, etc.)
    else
        echo "[WA] ✅ $(date '+%H:%M:%S') — heartbeat OK (âge: ${AGE}s)"
    fi

    sleep "$CHECK_INTERVAL"
done
```

**Test :**

```bash
# Terminal 1 : démarrer l'émetteur
$ bash heartbeat_v1.sh

# Terminal 2 : démarrer le watcher
$ bash watcher_v1.sh

# Terminal 3 : tuer l'émetteur pour voir l'alerte
$ pkill -f heartbeat_v1.sh
# → Observer l'alerte dans le terminal 2 après ~15s
```

---

### 4.2 Version 2 — Avec journalisation et pidfile

```bash
#!/bin/bash
# heartbeat_v2.sh — Émetteur avec pidfile et logs

# ── Configuration
HB_FILE="/tmp/heartbeat_v2.touch"
PID_FILE="/tmp/heartbeat_v2.pid"
LOG_FILE="/tmp/heartbeat_v2.log"
INTERVAL=5
SERVICE_NAME="mon-service"

# ── Fonctions utilitaires
log() {
    local level="$1"
    local msg="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $msg" | tee -a "$LOG_FILE"
}

cleanup() {
    log "INFO" "Arrêt du heartbeat (signal reçu)"
    rm -f "$HB_FILE" "$PID_FILE"
    exit 0
}

# ── Vérifier si déjà en cours
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        log "WARN" "Heartbeat déjà en cours (PID $OLD_PID)"
        exit 1
    fi
    log "INFO" "Ancien pidfile orphelin supprimé"
    rm -f "$PID_FILE"
fi

# ── Enregistrer notre PID
echo $$ > "$PID_FILE"
log "INFO" "Heartbeat démarré — PID $$ — Service: $SERVICE_NAME"

# ── Capturer les signaux pour cleanup propre
trap cleanup SIGTERM SIGINT SIGHUP

# ── Boucle principale
COUNTER=0
while true; do
    COUNTER=$((COUNTER + 1))

    # Mettre à jour le fichier heartbeat avec métadonnées
    {
        echo "service=$SERVICE_NAME"
        echo "pid=$$"
        echo "timestamp=$(date +%s)"
        echo "datetime=$(date '+%Y-%m-%d %H:%M:%S')"
        echo "counter=$COUNTER"
        echo "hostname=$(hostname)"
    } > "$HB_FILE"

    log "INFO" "Signal #$COUNTER envoyé"
    sleep "$INTERVAL"
done
```

```bash
#!/bin/bash
# watcher_v2.sh — Moniteur avec niveaux d'alerte et actions

# ── Configuration
HB_FILE="/tmp/heartbeat_v2.touch"
LOG_FILE="/tmp/watcher_v2.log"
TIMEOUT_WARN=10    # secondes → WARNING
TIMEOUT_CRIT=20    # secondes → CRITICAL
TIMEOUT_DEAD=30    # secondes → action d'urgence
CHECK_INTERVAL=3
SERVICE_NAME="mon-service"
ALERT_SENT=false   # éviter le spam d'alertes

log() {
    local level="$1"
    local msg="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $msg" | tee -a "$LOG_FILE"
}

action_warning() {
    log "WARN" "⚠️  Service $SERVICE_NAME : heartbeat dégradé (${AGE}s)"
    # Exemple : logger dans syslog
    logger -t "heartbeat-watcher" -p user.warning \
        "Service $SERVICE_NAME : heartbeat dégradé"
}

action_critical() {
    log "CRIT" "🟠 Service $SERVICE_NAME : heartbeat critique (${AGE}s)"
    logger -t "heartbeat-watcher" -p user.crit \
        "Service $SERVICE_NAME : heartbeat critique"
}

action_emergency() {
    log "EMRG" "🔴 Service $SERVICE_NAME : MORT (${AGE}s sans signal)"
    logger -t "heartbeat-watcher" -p user.emerg \
        "Service $SERVICE_NAME : heartbeat absent — action requise"

    # Tenter un redémarrage automatique
    log "INFO" "Tentative de redémarrage automatique..."
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        systemctl restart "$SERVICE_NAME"
        log "INFO" "Redémarrage systemd lancé"
    else
        log "WARN" "Service systemd non trouvé — action manuelle requise"
    fi
}

log "INFO" "Watcher démarré — surveillance de $SERVICE_NAME"
log "INFO" "Seuils : WARN=${TIMEOUT_WARN}s CRIT=${TIMEOUT_CRIT}s DEAD=${TIMEOUT_DEAD}s"

LAST_STATUS="OK"

while true; do
    if [ ! -f "$HB_FILE" ]; then
        AGE=999
    else
        NOW=$(date +%s)
        FILE_TS=$(grep "^timestamp=" "$HB_FILE" 2>/dev/null | cut -d= -f2)
        if [ -z "$FILE_TS" ]; then
            FILE_TS=$(stat -c %Y "$HB_FILE")
        fi
        AGE=$((NOW - FILE_TS))
    fi

    # Décider de l'état
    if [ "$AGE" -le "$TIMEOUT_WARN" ]; then
        if [ "$LAST_STATUS" != "OK" ]; then
            log "INFO" "✅ Service $SERVICE_NAME : heartbeat rétabli"
            ALERT_SENT=false
        fi
        log "INFO" "✅ OK — âge heartbeat: ${AGE}s"
        LAST_STATUS="OK"

    elif [ "$AGE" -le "$TIMEOUT_CRIT" ]; then
        if [ "$LAST_STATUS" != "WARN" ]; then
            action_warning
            LAST_STATUS="WARN"
        fi

    elif [ "$AGE" -le "$TIMEOUT_DEAD" ]; then
        if [ "$LAST_STATUS" != "CRIT" ]; then
            action_critical
            LAST_STATUS="CRIT"
        fi

    else
        if [ "$ALERT_SENT" = false ]; then
            action_emergency
            ALERT_SENT=true
            LAST_STATUS="DEAD"
        fi
    fi

    sleep "$CHECK_INTERVAL"
done
```

---

## MODULE 5 — Dead Man's Switch Basique en Bash

### 5.1 Version 1 — DMS avec fichier timestamp

```bash
#!/bin/bash
# dms_checkin.sh — Script de check-in (à exécuter manuellement)
# L'opérateur doit lancer ce script régulièrement

DMS_FILE="/tmp/dms_checkin.timestamp"
LOG_FILE="/tmp/dms_checkin.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Enregistrer le check-in
{
    echo "checkin_timestamp=$(date +%s)"
    echo "checkin_datetime=$(date '+%Y-%m-%d %H:%M:%S')"
    echo "operator_user=$(whoami)"
    echo "operator_host=$(hostname)"
} > "$DMS_FILE"

log "✅ CHECK-IN ENREGISTRÉ par $(whoami)@$(hostname)"
log "Prochain check-in requis avant : $(date -d '+24 hours' '+%Y-%m-%d %H:%M:%S')"
```

```bash
#!/bin/bash
# dms_watcher.sh — Gardien du Dead Man's Switch

DMS_FILE="/tmp/dms_checkin.timestamp"
LOG_FILE="/tmp/dms_watcher.log"
DEADLINE_SECONDS=$((24 * 3600))   # 24 heures
WARN_SECONDS=$((20 * 3600))       # alerte à 20h
CHECK_INTERVAL=300                 # vérifier toutes les 5 min

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

action_warning() {
    local remaining_h=$(( (DEADLINE_SECONDS - AGE) / 3600 ))
    log "⚠️  AVERTISSEMENT : check-in expiré dans ${remaining_h}h !"
    # Envoyer une alerte à l'opérateur
    echo "URGENT : Votre DMS expire dans ${remaining_h}h — Faites un check-in !" \
        | mail -s "[DMS] Alerte check-in" operateur@exemple.com 2>/dev/null \
        || log "WARN : envoi email échoué (mail non configuré)"
}

action_trigger() {
    log "🔴🔴🔴 DEAD MAN'S SWITCH DÉCLENCHÉ 🔴🔴🔴"
    log "Dernier check-in : il y a ${AGE}s ($(( AGE / 3600 ))h)"
    log "Exécution des actions d'urgence..."

    # === ACTIONS ICI (adapter selon le cas d'usage) ===

    # Exemple 1 : Notifier des contacts d'urgence
    log "ACTION 1 : Notification contacts d'urgence"
    echo "Le DMS a été déclenché. Dernier check-in il y a $(( AGE / 3600 ))h." \
        | mail -s "[DMS DÉCLENCHÉ] Action requise" urgence@exemple.com 2>/dev/null

    # Exemple 2 : Publier un fichier chiffré (simulation)
    log "ACTION 2 : Publication du fichier d'urgence"
    if [ -f "/secure/encrypted_payload.gpg" ]; then
        cp /secure/encrypted_payload.gpg /var/www/html/emergency_release.gpg
        log "Payload publié sur le serveur web"
    fi

    # Exemple 3 : Révoquer des accès
    log "ACTION 3 : Révocation des accès temporaires"
    # userdel tempuser 2>/dev/null

    # Exemple 4 : Logger pour audit
    logger -t "dms-trigger" -p user.emerg "DMS déclenché après ${AGE}s sans check-in"

    log "Actions terminées. DMS en état DÉCLENCHÉ."

    # Optionnel : ne plus boucler après déclenchement
    exit 0
}

# ── Vérifier que le fichier existe au démarrage
if [ ! -f "$DMS_FILE" ]; then
    log "Aucun check-in initial — créer un check-in d'abord avec dms_checkin.sh"
    log "En attente du premier check-in..."
    while [ ! -f "$DMS_FILE" ]; do
        sleep 10
    done
    log "Premier check-in détecté. DMS activé."
fi

log "DMS Watcher démarré"
log "Délai maximum sans check-in : $((DEADLINE_SECONDS / 3600))h"

TRIGGERED=false

while true; do
    if [ ! -f "$DMS_FILE" ]; then
        AGE=$DEADLINE_SECONDS
    else
        NOW=$(date +%s)
        LAST_TS=$(grep "^checkin_timestamp=" "$DMS_FILE" | cut -d= -f2)
        AGE=$((NOW - LAST_TS))
    fi

    REMAINING=$((DEADLINE_SECONDS - AGE))

    if [ "$AGE" -ge "$DEADLINE_SECONDS" ] && [ "$TRIGGERED" = false ]; then
        action_trigger
        TRIGGERED=true

    elif [ "$AGE" -ge "$WARN_SECONDS" ] && [ "$AGE" -lt "$DEADLINE_SECONDS" ]; then
        action_warning
        log "Temps restant avant déclenchement : $((REMAINING / 3600))h $((( REMAINING % 3600) / 60))m"

    else
        log "✅ OK — Dernier check-in il y a $((AGE / 60))min — Reste $((REMAINING / 3600))h"
    fi

    sleep "$CHECK_INTERVAL"
done
```

**Test rapide :**

```bash
# 1. Faire un check-in initial
$ bash dms_checkin.sh
→ [2024-01-10 09:00:00] ✅ CHECK-IN ENREGISTRÉ par alice@server01

# 2. Démarrer le watcher (en arrière-plan)
$ bash dms_watcher.sh &

# 3. Simuler un délai sans check-in (modifier le timestamp manuellement)
$ sed -i "s/checkin_timestamp=.*/checkin_timestamp=$(( $(date +%s) - 86500 ))/" /tmp/dms_checkin.timestamp

# 4. Observer le déclenchement dans les logs
$ tail -f /tmp/dms_watcher.log
```

---

### 5.2 Version 2 — DMS avec confirmation cryptographique

```bash
#!/bin/bash
# dms_secure_checkin.sh — Check-in sécurisé avec HMAC

SECRET_KEY="changez_ce_secret_en_production_$(hostname)"
DMS_FILE="/tmp/dms_secure.dat"
LOG_FILE="/tmp/dms_secure.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

# Demander confirmation interactive
read -r -s -p "Code de confirmation DMS (masqué) : " USER_CODE
echo ""

# Vérifier le code (simulé — en prod : base de données ou HSM)
EXPECTED_CODE="dms_$(date '+%Y%m%d')_secure"
if [ "$USER_CODE" != "$EXPECTED_CODE" ]; then
    log "❌ Code incorrect — check-in refusé"
    exit 1
fi

# Générer un token HMAC signé
TIMESTAMP=$(date +%s)
TOKEN=$(echo -n "${TIMESTAMP}:$(whoami):$(hostname)" \
    | openssl dgst -sha256 -hmac "$SECRET_KEY" \
    | awk '{print $2}')

{
    echo "timestamp=$TIMESTAMP"
    echo "user=$(whoami)"
    echo "host=$(hostname)"
    echo "token=$TOKEN"
} > "$DMS_FILE"

log "✅ Check-in sécurisé enregistré (token: ${TOKEN:0:16}...)"
```

---

### 🔬 Exercice 2.1 — Améliorer les scripts

```bash
# Exercice A : Ajouter une fonctionnalité au heartbeat_v2.sh
# Objectif : inclure les métriques système dans le signal heartbeat

# Le heartbeat doit inclure :
# - Utilisation CPU (%) → commande : top -bn1 | grep "Cpu(s)" | ...
# - Mémoire libre (MB) → commande : free -m | awk ...
# - Charge système     → commande : uptime | awk ...
# - Espace disque /    → commande : df -h / | awk ...

# Modifiez la section d'écriture du fichier heartbeat
# dans heartbeat_v2.sh pour inclure ces métriques.


# Exercice B : Ajouter des niveaux de seuil au watcher
# Le watcher doit :
# - Déclencher WARN si CPU > 80%
# - Déclencher CRIT si mémoire libre < 100MB
# - Logger ces anomalies indépendamment du timeout heartbeat


# Exercice C : Implémenter un mécanisme de "grace period" dans le DMS
# Après déclenchement du DMS, attendre 1h supplémentaire
# et envoyer une dernière alerte avant l'action finale.
# Si un check-in arrive pendant cette période, annuler.
```

**Solution Exercice A :**

```bash
# Section à remplacer dans heartbeat_v2.sh :

get_cpu_usage() {
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
}

get_mem_free_mb() {
    free -m | awk '/^Mem:/{print $7}'
}

get_load_avg() {
    uptime | awk -F'load average:' '{print $2}' | xargs
}

get_disk_usage() {
    df -h / | awk 'NR==2{print $5}'
}

# Dans la boucle while :
{
    echo "service=$SERVICE_NAME"
    echo "pid=$$"
    echo "timestamp=$(date +%s)"
    echo "datetime=$(date '+%Y-%m-%d %H:%M:%S')"
    echo "counter=$COUNTER"
    echo "hostname=$(hostname)"
    echo "cpu_usage=$(get_cpu_usage)"
    echo "mem_free_mb=$(get_mem_free_mb)"
    echo "load_avg=$(get_load_avg)"
    echo "disk_usage_root=$(get_disk_usage)"
} > "$HB_FILE"
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 3 — IMPLÉMENTATION PYTHON
# ═══════════════════════════════════════════════════

---

## MODULE 7 — Heartbeat Robuste en Python

### 7.1 Classes de base

```python
#!/usr/bin/env python3
# heartbeat_core.py — Implémentation OOP du heartbeat

import time
import os
import json
import signal
import logging
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Dict, Any

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class HeartbeatSender:
    """
    Émetteur de heartbeat.
    Envoie un signal périodique pour signaler qu'il est vivant.
    Thread-safe, gère les signaux système.
    """

    def __init__(
        self,
        service_name: str,
        heartbeat_file: str,
        interval: float = 5.0,
        metadata_fn: Optional[Callable[[], Dict[str, Any]]] = None
    ):
        self.service_name = service_name
        self.heartbeat_file = Path(heartbeat_file)
        self.interval = interval
        self.metadata_fn = metadata_fn
        self.running = False
        self.counter = 0
        self.logger = logging.getLogger(f"HB.Sender.{service_name}")
        self._stop_event = threading.Event()

    def _collect_metadata(self) -> Dict[str, Any]:
        """Collecte les métadonnées du système."""
        metadata = {
            "service": self.service_name,
            "pid": os.getpid(),
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "counter": self.counter,
            "hostname": os.uname().nodename,
        }

        # Métriques système
        try:
            with open("/proc/loadavg") as f:
                load = f.read().split()
                metadata["load_1m"] = float(load[0])
                metadata["load_5m"] = float(load[1])

            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        metadata["mem_available_kb"] = int(line.split()[1])
                        break
        except Exception:
            pass

        # Métadonnées personnalisées (callback)
        if self.metadata_fn:
            try:
                custom = self.metadata_fn()
                metadata.update(custom)
            except Exception as e:
                self.logger.warning(f"Erreur métadonnées custom: {e}")

        return metadata

    def _send_signal(self):
        """Envoie le signal heartbeat."""
        self.counter += 1
        metadata = self._collect_metadata()

        # Écriture atomique (évite la lecture d'un fichier partiel)
        tmp_file = self.heartbeat_file.with_suffix('.tmp')
        with open(tmp_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        tmp_file.rename(self.heartbeat_file)

        self.logger.debug(f"Signal #{self.counter} envoyé")

    def start(self):
        """Démarre l'émetteur en arrière-plan (thread)."""
        self.running = True
        self._stop_event.clear()

        def run():
            self.logger.info(
                f"Émetteur démarré — fichier: {self.heartbeat_file} "
                f"— intervalle: {self.interval}s"
            )
            while not self._stop_event.is_set():
                try:
                    self._send_signal()
                except Exception as e:
                    self.logger.error(f"Erreur envoi signal: {e}")
                self._stop_event.wait(self.interval)

            self.logger.info("Émetteur arrêté proprement")
            # Nettoyer le fichier heartbeat
            self.heartbeat_file.unlink(missing_ok=True)

        self._thread = threading.Thread(target=run, daemon=True, name="hb-sender")
        self._thread.start()

    def stop(self):
        """Arrête l'émetteur proprement."""
        self._stop_event.set()
        if hasattr(self, '_thread'):
            self._thread.join(timeout=10)
        self.running = False


class HeartbeatWatcher:
    """
    Moniteur de heartbeat.
    Surveille un fichier heartbeat et déclenche des callbacks
    selon l'état détecté.
    """

    # États possibles
    STATE_OK = "OK"
    STATE_WARNING = "WARNING"
    STATE_CRITICAL = "CRITICAL"
    STATE_DEAD = "DEAD"
    STATE_UNKNOWN = "UNKNOWN"

    def __init__(
        self,
        service_name: str,
        heartbeat_file: str,
        timeout_warn: float = 10.0,
        timeout_crit: float = 20.0,
        timeout_dead: float = 30.0,
        check_interval: float = 3.0,
    ):
        self.service_name = service_name
        self.heartbeat_file = Path(heartbeat_file)
        self.timeout_warn = timeout_warn
        self.timeout_crit = timeout_crit
        self.timeout_dead = timeout_dead
        self.check_interval = check_interval
        self.logger = logging.getLogger(f"HB.Watcher.{service_name}")

        # Callbacks (à surcharger ou assigner)
        self.on_warning: Optional[Callable] = None
        self.on_critical: Optional[Callable] = None
        self.on_dead: Optional[Callable] = None
        self.on_recovery: Optional[Callable] = None

        self._current_state = self.STATE_UNKNOWN
        self._stop_event = threading.Event()
        self._alert_sent = {
            self.STATE_WARNING: False,
            self.STATE_CRITICAL: False,
            self.STATE_DEAD: False,
        }

    def _get_heartbeat_age(self) -> Optional[float]:
        """Retourne l'âge du dernier heartbeat en secondes, ou None."""
        if not self.heartbeat_file.exists():
            return None
        try:
            with open(self.heartbeat_file) as f:
                data = json.load(f)
            return time.time() - data.get("timestamp", 0)
        except Exception:
            return time.time() - self.heartbeat_file.stat().st_mtime

    def _determine_state(self, age: Optional[float]) -> str:
        if age is None or age > self.timeout_dead:
            return self.STATE_DEAD
        elif age > self.timeout_crit:
            return self.STATE_CRITICAL
        elif age > self.timeout_warn:
            return self.STATE_WARNING
        else:
            return self.STATE_OK

    def _handle_state_change(self, new_state: str, age: Optional[float]):
        old_state = self._current_state
        age_str = f"{age:.1f}s" if age is not None else "∞"

        if new_state == self.STATE_OK:
            if old_state != self.STATE_OK and old_state != self.STATE_UNKNOWN:
                self.logger.info(f"✅ RÉTABLI — {self.service_name} est de nouveau vivant")
                # Réinitialiser les alertes
                for k in self._alert_sent:
                    self._alert_sent[k] = False
                if self.on_recovery:
                    self.on_recovery(old_state)
            else:
                self.logger.debug(f"✅ OK — âge: {age_str}")

        elif new_state == self.STATE_WARNING:
            if not self._alert_sent[self.STATE_WARNING]:
                self.logger.warning(f"⚠️  WARNING — {self.service_name} — âge: {age_str}")
                self._alert_sent[self.STATE_WARNING] = True
                if self.on_warning:
                    self.on_warning(age)

        elif new_state == self.STATE_CRITICAL:
            if not self._alert_sent[self.STATE_CRITICAL]:
                self.logger.critical(f"🟠 CRITICAL — {self.service_name} — âge: {age_str}")
                self._alert_sent[self.STATE_CRITICAL] = True
                if self.on_critical:
                    self.on_critical(age)

        elif new_state == self.STATE_DEAD:
            if not self._alert_sent[self.STATE_DEAD]:
                self.logger.critical(f"🔴 DEAD — {self.service_name} — âge: {age_str}")
                self._alert_sent[self.STATE_DEAD] = True
                if self.on_dead:
                    self.on_dead(age)

        self._current_state = new_state

    def start(self):
        """Démarre la surveillance en arrière-plan."""
        self._stop_event.clear()

        def run():
            self.logger.info(
                f"Watcher démarré — surveillance: {self.heartbeat_file} "
                f"— seuils: WARN={self.timeout_warn}s "
                f"CRIT={self.timeout_crit}s DEAD={self.timeout_dead}s"
            )
            while not self._stop_event.is_set():
                try:
                    age = self._get_heartbeat_age()
                    state = self._determine_state(age)
                    self._handle_state_change(state, age)
                except Exception as e:
                    self.logger.error(f"Erreur vérification: {e}")
                self._stop_event.wait(self.check_interval)

        self._thread = threading.Thread(target=run, daemon=True, name="hb-watcher")
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if hasattr(self, '_thread'):
            self._thread.join(timeout=10)

    @property
    def state(self) -> str:
        return self._current_state
```

### 7.2 Utilisation de la classe

```python
#!/usr/bin/env python3
# demo_heartbeat.py — Démonstration du heartbeat Python

import time
import logging
from heartbeat_core import HeartbeatSender, HeartbeatWatcher

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')


def custom_metadata():
    """Métadonnées métier personnalisées."""
    return {
        "db_connections": 42,
        "requests_per_sec": 150,
        "queue_depth": 7,
        "version": "1.2.3"
    }

def on_warning_callback(age):
    print(f"📧 EMAIL : Le service est lent (âge: {age:.1f}s)")

def on_dead_callback(age):
    print(f"📱 SMS URGENCE : Le service est mort (âge: {age}s) !")
    print(f"🔄 Tentative de redémarrage automatique...")


# Créer et démarrer l'émetteur
sender = HeartbeatSender(
    service_name="api-backend",
    heartbeat_file="/tmp/api_backend.hb",
    interval=3.0,
    metadata_fn=custom_metadata
)

# Créer et configurer le watcher
watcher = HeartbeatWatcher(
    service_name="api-backend",
    heartbeat_file="/tmp/api_backend.hb",
    timeout_warn=8.0,
    timeout_crit=15.0,
    timeout_dead=25.0,
    check_interval=2.0
)
watcher.on_warning = on_warning_callback
watcher.on_dead = on_dead_callback

print("=== DÉMO HEARTBEAT PYTHON ===")
print("Phase 1 : fonctionnement normal (10s)")
sender.start()
watcher.start()
time.sleep(10)

print("\nPhase 2 : simulation de panne (arrêt de l'émetteur)")
sender.stop()
time.sleep(30)

print("\nPhase 3 : rétablissement")
sender.start()
time.sleep(10)

sender.stop()
watcher.stop()
print("\nDémo terminée.")
```

---

## MODULE 8 — Dead Man's Switch Robuste en Python

```python
#!/usr/bin/env python3
# dms_core.py — Dead Man's Switch complet en Python

import time
import json
import os
import hashlib
import hmac
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Optional, List

logger = logging.getLogger("DMS")


class DeadManSwitch:
    """
    Dead Man's Switch robuste.
    Se déclenche si aucun check-in n'est reçu dans le délai imparti.

    Usage typique :
      - Alerte d'urgence si l'administrateur est incapable d'agir
      - Révocation automatique d'accès temporaires
      - Publication de fichiers en cas d'incident grave
    """

    STATE_ARMED      = "ARMED"       # Actif, en attente de check-ins
    STATE_WARNING    = "WARNING"     # Délai presque écoulé
    STATE_TRIGGERED  = "TRIGGERED"   # Délai expiré, action en cours
    STATE_DISARMED   = "DISARMED"    # Désarmé manuellement

    def __init__(
        self,
        name: str,
        state_file: str,
        deadline_hours: float = 24.0,
        warning_hours: float = 4.0,
        grace_hours: float = 1.0,
        secret_key: Optional[str] = None,
    ):
        self.name = name
        self.state_file = Path(state_file)
        self.deadline_seconds = deadline_hours * 3600
        self.warning_seconds = (deadline_hours - warning_hours) * 3600
        self.grace_seconds = grace_hours * 3600
        self.secret_key = (secret_key or "default_insecure_key").encode()

        self.logger = logging.getLogger(f"DMS.{name}")

        # Actions enregistrées
        self._warning_actions: List[Callable] = []
        self._trigger_actions: List[Callable] = []
        self._grace_actions: List[Callable] = []

        self._stop_event = threading.Event()
        self._state = self.STATE_DISARMED

    def _load_state(self) -> Optional[dict]:
        """Charge l'état depuis le fichier."""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Erreur lecture état: {e}")
            return None

    def _save_state(self, state: dict):
        """Sauvegarde l'état de manière atomique."""
        tmp = self.state_file.with_suffix('.tmp')
        with open(tmp, 'w') as f:
            json.dump(state, f, indent=2)
        tmp.rename(self.state_file)

    def _sign_checkin(self, timestamp: int, user: str) -> str:
        """Génère un HMAC-SHA256 pour le check-in."""
        message = f"{timestamp}:{user}:{self.name}".encode()
        return hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()

    def _verify_checkin(self, timestamp: int, user: str, token: str) -> bool:
        """Vérifie la signature d'un check-in."""
        expected = self._sign_checkin(timestamp, user)
        return hmac.compare_digest(expected, token)

    def arm(self, user: str = "system"):
        """Arme le DMS. Lance le compte à rebours."""
        timestamp = int(time.time())
        token = self._sign_checkin(timestamp, user)

        state = {
            "dms_name": self.name,
            "state": self.STATE_ARMED,
            "armed_at": timestamp,
            "armed_by": user,
            "last_checkin": timestamp,
            "last_checkin_user": user,
            "last_checkin_token": token,
            "checkin_count": 0,
            "deadline_seconds": self.deadline_seconds,
        }
        self._save_state(state)
        self._state = self.STATE_ARMED

        deadline_dt = datetime.fromtimestamp(timestamp + self.deadline_seconds)
        self.logger.info(
            f"✅ DMS '{self.name}' armé par {user} — "
            f"deadline: {deadline_dt.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def checkin(self, user: str = "operator", verify_token: Optional[str] = None) -> bool:
        """
        Effectue un check-in pour réinitialiser le timer.
        Retourne True si succès, False si échec.
        """
        state = self._load_state()
        if state is None:
            self.logger.error("DMS non armé — impossible de faire un check-in")
            return False

        if state.get("state") == self.STATE_TRIGGERED:
            self.logger.error("DMS déjà déclenché — check-in refusé")
            return False

        if state.get("state") == self.STATE_DISARMED:
            self.logger.warning("DMS désarmé — check-in ignoré")
            return False

        timestamp = int(time.time())

        # Vérifier le token si fourni
        if verify_token:
            if not self._verify_checkin(timestamp, user, verify_token):
                self.logger.warning(f"⚠️  Token invalide pour check-in de {user}")
                return False

        token = self._sign_checkin(timestamp, user)
        state["last_checkin"] = timestamp
        state["last_checkin_user"] = user
        state["last_checkin_token"] = token
        state["checkin_count"] = state.get("checkin_count", 0) + 1
        state["state"] = self.STATE_ARMED
        self._save_state(state)

        deadline_dt = datetime.fromtimestamp(timestamp + self.deadline_seconds)
        self.logger.info(
            f"✅ Check-in #{state['checkin_count']} enregistré par {user} — "
            f"nouveau deadline: {deadline_dt.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return True

    def disarm(self, user: str = "operator"):
        """Désarme le DMS (arrête le compte à rebours)."""
        state = self._load_state()
        if state:
            state["state"] = self.STATE_DISARMED
            state["disarmed_at"] = int(time.time())
            state["disarmed_by"] = user
            self._save_state(state)
        self._state = self.STATE_DISARMED
        self._stop_event.set()
        self.logger.info(f"🔓 DMS '{self.name}' désarmé par {user}")

    def add_warning_action(self, fn: Callable):
        """Ajoute une action exécutée lors de l'alerte pré-déclenchement."""
        self._warning_actions.append(fn)

    def add_trigger_action(self, fn: Callable):
        """Ajoute une action exécutée au déclenchement."""
        self._trigger_actions.append(fn)

    def add_grace_action(self, fn: Callable):
        """Ajoute une action exécutée pendant la période de grâce."""
        self._grace_actions.append(fn)

    def _execute_actions(self, actions: List[Callable], label: str):
        """Exécute une liste d'actions avec gestion des erreurs."""
        for i, action in enumerate(actions):
            try:
                self.logger.info(f"Exécution action {label} #{i+1}: {action.__name__}")
                action()
            except Exception as e:
                self.logger.error(f"Erreur action {label} #{i+1}: {e}")

    def _trigger(self, state: dict):
        """Déclenche le DMS."""
        self.logger.critical(f"🔴🔴🔴 DMS '{self.name}' DÉCLENCHÉ 🔴🔴🔴")

        age = int(time.time()) - state.get("last_checkin", 0)
        self.logger.critical(f"Dernier check-in il y a {age}s ({age//3600}h{(age%3600)//60}m)")

        # Période de grâce
        if self._grace_actions:
            self.logger.warning(f"⏳ Période de grâce ({self.grace_seconds/3600:.1f}h)...")
            self._execute_actions(self._grace_actions, "GRACE")

            # Attendre la fin de la période de grâce
            grace_start = time.time()
            while time.time() - grace_start < self.grace_seconds:
                # Vérifier si un check-in arrive pendant la grâce
                current_state = self._load_state()
                if current_state and current_state.get("last_checkin", 0) > state.get("last_checkin", 0):
                    self.logger.info("✅ Check-in reçu pendant la grâce — DMS annulé !")
                    return
                time.sleep(10)

        # Mettre à jour l'état
        state["state"] = self.STATE_TRIGGERED
        state["triggered_at"] = int(time.time())
        self._save_state(state)
        self._state = self.STATE_TRIGGERED

        # Exécuter les actions finales
        self._execute_actions(self._trigger_actions, "TRIGGER")
        self.logger.critical("Actions de déclenchement terminées.")

    def start_monitoring(self, check_interval: float = 60.0):
        """Démarre la surveillance en arrière-plan."""
        self._stop_event.clear()

        def monitor():
            self.logger.info(f"Surveillance DMS '{self.name}' démarrée")
            warning_sent = False

            while not self._stop_event.is_set():
                state = self._load_state()

                if state is None or state.get("state") in (
                    self.STATE_DISARMED, self.STATE_TRIGGERED
                ):
                    self._stop_event.wait(check_interval)
                    continue

                now = int(time.time())
                last_checkin = state.get("last_checkin", now)
                age = now - last_checkin
                remaining = self.deadline_seconds - age

                # Alerte préventive
                if age >= self.warning_seconds and not warning_sent:
                    remaining_h = remaining / 3600
                    self.logger.warning(
                        f"⚠️  Alerte préventive DMS '{self.name}' — "
                        f"déclenchement dans {remaining_h:.1f}h !"
                    )
                    warning_sent = True
                    self._execute_actions(self._warning_actions, "WARNING")

                # Déclenchement
                elif age >= self.deadline_seconds:
                    self._trigger(state)
                    break

                else:
                    remaining_h = remaining / 3600
                    self.logger.debug(
                        f"DMS OK — dernier check-in il y a {age//60}min "
                        f"— reste {remaining_h:.1f}h"
                    )

                    # Réinitialiser si check-in reçu
                    if age < self.warning_seconds:
                        warning_sent = False

                self._stop_event.wait(check_interval)

            self.logger.info(f"Surveillance DMS '{self.name}' arrêtée")

        thread = threading.Thread(target=monitor, daemon=True, name=f"dms-{self.name}")
        thread.start()
        return thread
```

### 8.2 Utilisation complète du DMS

```python
#!/usr/bin/env python3
# demo_dms.py — Démonstration du Dead Man's Switch

import time
import logging
from dms_core import DeadManSwitch

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# ── Définir les actions
def action_warning():
    print("📧 EMAIL : Votre DMS expire bientôt — faites un check-in !")

def action_grace():
    print("📱 SMS : DERNIÈRE CHANCE — DMS déclenchement imminent !")
    print("📱 SMS : Vous avez 1h pour faire un check-in d'urgence")

def action_trigger_1():
    print("🔴 ACTION 1 : Envoi des emails d'urgence aux contacts")

def action_trigger_2():
    print("🔴 ACTION 2 : Publication du fichier insurance.gpg")

def action_trigger_3():
    print("🔴 ACTION 3 : Révocation de tous les tokens d'accès")


# ── Créer le DMS (délai court pour la démo)
dms = DeadManSwitch(
    name="admin-urgence",
    state_file="/tmp/dms_admin.json",
    deadline_hours=0.01,    # 36 secondes pour la démo (normalement: 24h)
    warning_hours=0.003,    # alerte à 10s avant
    grace_hours=0.002,      # grâce de 7s
    secret_key="ma_cle_secrete_demo"
)

# Enregistrer les actions
dms.add_warning_action(action_warning)
dms.add_grace_action(action_grace)
dms.add_trigger_action(action_trigger_1)
dms.add_trigger_action(action_trigger_2)
dms.add_trigger_action(action_trigger_3)

print("=== DÉMO DEAD MAN'S SWITCH ===\n")

# Scénario 1 : check-ins réguliers (fonctionnement normal)
print("--- Scénario 1 : fonctionnement normal ---")
dms.arm(user="alice")
dms.start_monitoring(check_interval=2.0)

for i in range(3):
    time.sleep(8)
    dms.checkin(user="alice")

print("\n--- Scénario 2 : simulation d'absence ---")
print("(Plus de check-in → déclenchement automatique)\n")
time.sleep(60)  # Attendre le déclenchement

print("\nDémo terminée.")
```

---

## MODULE 9 — Communication Réseau (Client/Serveur)

```python
#!/usr/bin/env python3
# heartbeat_server.py — Serveur HTTP de réception de heartbeats

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict
import logging

logger = logging.getLogger("HB.Server")


class HeartbeatRegistry:
    """Registre central de tous les services surveillés."""

    def __init__(self):
        self._services: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._callbacks = []

    def register_heartbeat(self, service_name: str, data: dict):
        """Enregistre un heartbeat reçu."""
        with self._lock:
            now = time.time()
            if service_name not in self._services:
                logger.info(f"Nouveau service enregistré: {service_name}")

            self._services[service_name] = {
                **data,
                "last_seen": now,
                "last_seen_dt": time.strftime("%Y-%m-%d %H:%M:%S"),
                "consecutive_ok": self._services.get(
                    service_name, {}
                ).get("consecutive_ok", 0) + 1
            }

    def get_all_services(self) -> Dict[str, dict]:
        with self._lock:
            return dict(self._services)

    def get_service_age(self, service_name: str) -> float:
        with self._lock:
            svc = self._services.get(service_name)
            if not svc:
                return float('inf')
            return time.time() - svc["last_seen"]

    def get_health_report(self, timeout: float = 30.0) -> dict:
        report = {"timestamp": time.time(), "services": {}}
        for name, data in self.get_all_services().items():
            age = time.time() - data["last_seen"]
            report["services"][name] = {
                "status": "OK" if age <= timeout else "DEAD",
                "age_seconds": round(age, 2),
                "last_seen": data["last_seen_dt"],
                "data": data
            }
        return report


registry = HeartbeatRegistry()


class HeartbeatHandler(BaseHTTPRequestHandler):
    """Gestionnaire HTTP pour les heartbeats entrants."""

    def log_message(self, format, *args):
        # Supprimer les logs HTTP par défaut (trop verbeux)
        pass

    def do_POST(self):
        """Recevoir un heartbeat."""
        if self.path != "/heartbeat":
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            service = data.get("service", "unknown")

            registry.register_heartbeat(service, data)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "ok", "received": True}
            self.wfile.write(json.dumps(response).encode())

            logger.debug(f"Heartbeat reçu de: {service}")

        except Exception as e:
            logger.error(f"Erreur traitement heartbeat: {e}")
            self.send_response(400)
            self.end_headers()

    def do_GET(self):
        """Rapport de santé des services."""
        if self.path == "/health":
            report = registry.get_health_report()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(report, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()


def start_server(host: str = "0.0.0.0", port: int = 8765):
    server = HTTPServer((host, port), HeartbeatHandler)
    logger.info(f"Serveur heartbeat démarré sur {host}:{port}")
    logger.info(f"  POST /heartbeat  → envoyer un heartbeat")
    logger.info(f"  GET  /health     → rapport de santé")
    server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    start_server()
```

```python
#!/usr/bin/env python3
# heartbeat_http_sender.py — Émetteur heartbeat via HTTP

import time
import json
import os
import threading
import urllib.request
import urllib.error
import logging

logger = logging.getLogger("HB.HTTPSender")


class HTTPHeartbeatSender:
    """Émetteur de heartbeat vers un serveur HTTP."""

    def __init__(
        self,
        service_name: str,
        server_url: str,
        interval: float = 5.0,
        timeout: float = 3.0
    ):
        self.service_name = service_name
        self.endpoint = f"{server_url.rstrip('/')}/heartbeat"
        self.interval = interval
        self.timeout = timeout
        self._stop_event = threading.Event()
        self._consecutive_failures = 0

    def _send(self):
        payload = json.dumps({
            "service": self.service_name,
            "timestamp": time.time(),
            "pid": os.getpid(),
            "hostname": os.uname().nodename,
        }).encode()

        req = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout):
                self._consecutive_failures = 0
                logger.debug("Heartbeat HTTP envoyé avec succès")
        except Exception as e:
            self._consecutive_failures += 1
            logger.warning(
                f"Échec envoi heartbeat (#{self._consecutive_failures}): {e}"
            )

    def start(self):
        self._stop_event.clear()

        def run():
            while not self._stop_event.is_set():
                self._send()
                self._stop_event.wait(self.interval)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def stop(self):
        self._stop_event.set()


# Test rapide
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s [%(levelname)s]: %(message)s')

    sender = HTTPHeartbeatSender(
        service_name="mon-api",
        server_url="http://localhost:8765",
        interval=3.0
    )
    sender.start()

    print("Envoi de heartbeats pendant 30s...")
    print("Vérifier : curl http://localhost:8765/health")
    time.sleep(30)
    sender.stop()
    print("Terminé.")
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 4 — INTÉGRATION SYSTÈME
# ═══════════════════════════════════════════════════

---

## MODULE 10 — Systemd — Services et Timers

### 10.1 Service systemd pour le heartbeat

```ini
# /etc/systemd/system/heartbeat-sender.service

[Unit]
Description=Heartbeat Sender Service
Documentation=https://wiki.interne/heartbeat
After=network.target
Wants=network.target

# Redémarrer si le service supervisé crash
# (le heartbeat doit survivre au service qu'il surveille)
StartLimitIntervalSec=60
StartLimitBurst=5

[Service]
Type=simple
User=monitoring
Group=monitoring
WorkingDirectory=/opt/heartbeat

# Le script émetteur
ExecStart=/usr/bin/python3 /opt/heartbeat/heartbeat_sender.py

# Redémarrage automatique
Restart=always
RestartSec=5s

# Isolation de sécurité
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/heartbeat

# Limites ressources
MemoryMax=50M
CPUQuota=5%

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=heartbeat-sender

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/heartbeat-watcher.service

[Unit]
Description=Heartbeat Watcher - Service Monitor
After=network.target
Requires=heartbeat-sender.service

[Service]
Type=simple
User=monitoring
ExecStart=/usr/bin/python3 /opt/heartbeat/heartbeat_watcher.py
Restart=always
RestartSec=3s
NoNewPrivileges=true
PrivateTmp=true

# Action en cas de crash du watcher lui-même
OnFailure=heartbeat-watcher-recovery.service

[Install]
WantedBy=multi-user.target
```

### 10.2 Timer systemd pour le DMS check-in

```ini
# /etc/systemd/system/dms-checkin.timer
# Timer qui RAPPELLE à l'opérateur de faire son check-in

[Unit]
Description=Dead Man's Switch - Rappel Check-in
Documentation=https://wiki.interne/dms

[Timer]
# Envoyer un rappel toutes les 8h
OnCalendar=*-*-* 08,16,00:00:00
# Aussi au démarrage du système
OnBootSec=5min
# Précision (évite que tous les timers s'exécutent en même temps)
AccuracySec=1min
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/dms-checkin.service
# Service exécuté par le timer

[Unit]
Description=Dead Man's Switch - Vérification Check-in
After=network.target

[Service]
Type=oneshot
User=root
ExecStart=/opt/dms/dms_check_reminder.sh
StandardOutput=journal
SyslogIdentifier=dms-checkin
```

```bash
#!/bin/bash
# /opt/dms/dms_check_reminder.sh

DMS_FILE="/var/lib/dms/checkin.json"
DEADLINE_HOURS=24
WARN_REMAINING_HOURS=6

if [ ! -f "$DMS_FILE" ]; then
    echo "DMS non initialisé"
    exit 0
fi

LAST_CHECKIN=$(python3 -c "import json; d=json.load(open('$DMS_FILE')); print(d['last_checkin'])")
NOW=$(date +%s)
AGE=$((NOW - LAST_CHECKIN))
REMAINING=$(( (DEADLINE_HOURS * 3600) - AGE ))
REMAINING_H=$((REMAINING / 3600))

echo "DMS Status : Dernier check-in il y a $((AGE/3600))h — Reste ${REMAINING_H}h"

if [ "$REMAINING_H" -le "$WARN_REMAINING_HOURS" ]; then
    # Envoyer alerte via journald (sera capturée par le monitoring)
    systemd-cat -t dms-alert -p warning \
        echo "⚠️  DMS expire dans ${REMAINING_H}h — CHECK-IN REQUIS"

    # Optionnel : notification wall à tous les utilisateurs connectés
    wall "⚠️  URGENT : Dead Man's Switch expire dans ${REMAINING_H}h. Faire un check-in !"
fi
```

```bash
# Activer et démarrer les services
$ sudo systemctl daemon-reload
$ sudo systemctl enable heartbeat-sender heartbeat-watcher
$ sudo systemctl start heartbeat-sender heartbeat-watcher

# Vérifier
$ sudo systemctl status heartbeat-sender
$ sudo journalctl -u heartbeat-sender -f

# Activer le timer DMS
$ sudo systemctl enable dms-checkin.timer
$ sudo systemctl start dms-checkin.timer
$ sudo systemctl list-timers dms-checkin.timer
```

---

## MODULE 11 — Surveillance Multi-Nœuds

```python
#!/usr/bin/env python3
# multinode_monitor.py — Surveillance d'un cluster de serveurs

import time
import json
import threading
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger("MultiNodeMonitor")


class NodeState(Enum):
    HEALTHY   = "healthy"
    DEGRADED  = "degraded"
    FAILED    = "failed"
    UNKNOWN   = "unknown"


@dataclass
class Node:
    name: str
    host: str
    port: int = 8765
    timeout_warn: float = 10.0
    timeout_dead: float = 30.0
    state: NodeState = NodeState.UNKNOWN
    last_heartbeat: float = 0.0
    last_data: dict = field(default_factory=dict)
    failure_count: int = 0


class ClusterMonitor:
    """
    Surveille un cluster de nœuds via heartbeat HTTP.
    Implémente un quorum pour éviter les faux positifs.
    """

    def __init__(self, quorum_ratio: float = 0.5):
        self.nodes: Dict[str, Node] = {}
        self.quorum_ratio = quorum_ratio  # 50% du cluster doit voir un nœud en panne
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    def add_node(self, name: str, host: str, port: int = 8765):
        with self._lock:
            self.nodes[name] = Node(name=name, host=host, port=port)
        logger.info(f"Nœud ajouté: {name} ({host}:{port})")

    def _poll_node(self, node: Node) -> Optional[dict]:
        """Interroge un nœud pour son heartbeat."""
        url = f"http://{node.host}:{node.port}/health"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read())
        except Exception:
            return None

    def _check_node(self, node: Node):
        """Vérifie l'état d'un nœud."""
        data = self._poll_node(node)
        now = time.time()

        with self._lock:
            if data is None:
                node.failure_count += 1
                age = now - node.last_heartbeat if node.last_heartbeat else float('inf')
            else:
                node.last_heartbeat = now
                node.last_data = data
                node.failure_count = 0
                age = 0.0

            # Déterminer l'état
            old_state = node.state
            if age <= node.timeout_warn:
                node.state = NodeState.HEALTHY
            elif age <= node.timeout_dead:
                node.state = NodeState.DEGRADED
            else:
                node.state = NodeState.FAILED

            if old_state != node.state:
                logger.info(
                    f"Changement d'état: {node.name} "
                    f"{old_state.value} → {node.state.value}"
                )

    def get_cluster_health(self) -> dict:
        """Rapport de santé du cluster avec calcul de quorum."""
        with self._lock:
            total = len(self.nodes)
            healthy = sum(1 for n in self.nodes.values()
                         if n.state == NodeState.HEALTHY)
            failed = sum(1 for n in self.nodes.values()
                        if n.state == NodeState.FAILED)

            health_ratio = healthy / total if total > 0 else 0
            cluster_state = "HEALTHY" if health_ratio > self.quorum_ratio else "DEGRADED"
            if healthy == 0:
                cluster_state = "CRITICAL"

            return {
                "cluster_state": cluster_state,
                "total_nodes": total,
                "healthy_nodes": healthy,
                "failed_nodes": failed,
                "health_ratio": round(health_ratio, 2),
                "quorum_threshold": self.quorum_ratio,
                "nodes": {
                    name: {
                        "state": node.state.value,
                        "last_heartbeat": node.last_heartbeat,
                        "failure_count": node.failure_count
                    }
                    for name, node in self.nodes.items()
                }
            }

    def start(self, poll_interval: float = 5.0):
        """Démarre la surveillance de tous les nœuds."""
        self._stop_event.clear()

        def monitor_all():
            while not self._stop_event.is_set():
                threads = []
                for node in list(self.nodes.values()):
                    t = threading.Thread(
                        target=self._check_node,
                        args=(node,),
                        daemon=True
                    )
                    t.start()
                    threads.append(t)

                for t in threads:
                    t.join(timeout=10)

                # Afficher le résumé
                health = self.get_cluster_health()
                logger.info(
                    f"Cluster: {health['cluster_state']} — "
                    f"{health['healthy_nodes']}/{health['total_nodes']} nœuds sains"
                )

                self._stop_event.wait(poll_interval)

        thread = threading.Thread(target=monitor_all, daemon=True)
        thread.start()
        return thread


# Exemple d'utilisation
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s [%(levelname)s]: %(message)s')

    monitor = ClusterMonitor(quorum_ratio=0.6)
    monitor.add_node("web-01", "192.168.1.10", 8765)
    monitor.add_node("web-02", "192.168.1.11", 8765)
    monitor.add_node("web-03", "192.168.1.12", 8765)
    monitor.add_node("db-01",  "192.168.1.20", 8765)

    thread = monitor.start(poll_interval=5.0)

    try:
        while True:
            time.sleep(10)
            health = monitor.get_cluster_health()
            print(json.dumps(health, indent=2))
    except KeyboardInterrupt:
        pass
```

---

# ═══════════════════════════════════════════════════
# NIVEAU 5 — EXPERT & PRODUCTION
# ═══════════════════════════════════════════════════

---

## MODULE 13 — Heartbeat Distribué avec Redis

```python
#!/usr/bin/env python3
# heartbeat_redis.py — Heartbeat haute disponibilité avec Redis
#
# Prérequis : pip install redis
# Redis offre : atomicité, TTL natif, pub/sub, persistance

import time
import json
import os
import threading
import logging
from typing import Callable, Optional, Dict, Any

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  redis non installé. Installer avec : pip install redis")

logger = logging.getLogger("HB.Redis")


class RedisHeartbeatSender:
    """
    Émetteur heartbeat utilisant Redis comme backend.
    Avantage : TTL natif → si l'émetteur crash, la clé expire automatiquement
    """

    HEARTBEAT_KEY_PREFIX = "heartbeat:"
    DEFAULT_TTL = 15  # secondes (2x l'intervalle d'envoi recommandé)

    def __init__(
        self,
        service_name: str,
        redis_url: str = "redis://localhost:6379",
        interval: float = 5.0,
        ttl: int = 15,
        metadata_fn: Optional[Callable[[], Dict[str, Any]]] = None
    ):
        if not REDIS_AVAILABLE:
            raise ImportError("Module redis requis : pip install redis")

        self.service_name = service_name
        self.key = f"{self.HEARTBEAT_KEY_PREFIX}{service_name}"
        self.interval = interval
        self.ttl = ttl
        self.metadata_fn = metadata_fn
        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._stop_event = threading.Event()
        self._counter = 0
        self.logger = logging.getLogger(f"HB.Redis.Sender.{service_name}")

    def _send(self):
        self._counter += 1
        data = {
            "service": self.service_name,
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pid": os.getpid(),
            "hostname": os.uname().nodename,
            "counter": self._counter,
        }

        if self.metadata_fn:
            try:
                data.update(self.metadata_fn())
            except Exception as e:
                self.logger.warning(f"Erreur métadonnées: {e}")

        # SET avec TTL atomique — si le processus crash, la clé expire seule
        self._redis.setex(self.key, self.ttl, json.dumps(data))

        # Publier un événement pour les watchers en temps réel
        self._redis.publish(f"heartbeat_events", json.dumps({
            "event": "heartbeat",
            "service": self.service_name,
            "timestamp": data["timestamp"]
        }))

        self.logger.debug(f"Signal #{self._counter} publié sur Redis (TTL: {self.ttl}s)")

    def start(self):
        self._stop_event.clear()

        def run():
            self.logger.info(
                f"Émetteur Redis démarré — clé: {self.key} "
                f"— TTL: {self.ttl}s — intervalle: {self.interval}s"
            )
            while not self._stop_event.is_set():
                try:
                    self._send()
                except redis.RedisError as e:
                    self.logger.error(f"Erreur Redis: {e}")
                except Exception as e:
                    self.logger.error(f"Erreur inattendue: {e}")
                self._stop_event.wait(self.interval)

        thread = threading.Thread(target=run, daemon=True, name=f"hb-redis-{self.service_name}")
        thread.start()

    def stop(self):
        self._stop_event.set()
        try:
            self._redis.delete(self.key)  # Supprimer proprement
        except Exception:
            pass


class RedisHeartbeatWatcher:
    """
    Moniteur heartbeat utilisant Redis.
    Utilise les TTL Redis + pub/sub pour une détection immédiate.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        check_interval: float = 5.0
    ):
        if not REDIS_AVAILABLE:
            raise ImportError("Module redis requis")

        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._pubsub = self._redis.pubsub()
        self.check_interval = check_interval
        self._monitored: Dict[str, dict] = {}
        self._callbacks: Dict[str, Callable] = {}
        self._stop_event = threading.Event()
        self.logger = logging.getLogger("HB.Redis.Watcher")

    def watch(self, service_name: str, on_dead: Callable, ttl_threshold: int = 15):
        """Enregistre un service à surveiller."""
        self._monitored[service_name] = {
            "key": f"heartbeat:{service_name}",
            "ttl_threshold": ttl_threshold,
            "last_state": "UNKNOWN",
            "on_dead": on_dead
        }
        self.logger.info(f"Surveillance ajoutée: {service_name}")

    def get_all_heartbeats(self) -> Dict[str, Optional[dict]]:
        """Récupère tous les heartbeats actuels depuis Redis."""
        result = {}
        for svc_name, config in self._monitored.items():
            raw = self._redis.get(config["key"])
            if raw:
                try:
                    result[svc_name] = json.loads(raw)
                except Exception:
                    result[svc_name] = None
            else:
                result[svc_name] = None
        return result

    def start(self):
        """Démarre la surveillance en polling + pub/sub."""
        self._stop_event.clear()

        def poll():
            """Vérification périodique pour les services silencieux."""
            while not self._stop_event.is_set():
                for svc_name, config in self._monitored.items():
                    exists = self._redis.exists(config["key"])
                    last_state = config["last_state"]

                    if not exists and last_state != "DEAD":
                        self.logger.critical(
                            f"🔴 {svc_name} : clé Redis absente/expirée — SERVICE MORT"
                        )
                        config["last_state"] = "DEAD"
                        try:
                            config["on_dead"](svc_name)
                        except Exception as e:
                            self.logger.error(f"Erreur callback on_dead: {e}")

                    elif exists and last_state == "DEAD":
                        self.logger.info(f"✅ {svc_name} : heartbeat rétabli")
                        config["last_state"] = "OK"

                self._stop_event.wait(self.check_interval)

        thread = threading.Thread(target=poll, daemon=True, name="hb-redis-watcher")
        thread.start()
        self.logger.info("Watcher Redis démarré")
```

---

## MODULE 14 — Dead Man's Switch Cryptographique

```python
#!/usr/bin/env python3
# dms_crypto.py — DMS avec chiffrement et publication automatique
#
# Cas d'usage : journaliste/lanceur d'alerte
# Si le check-in n'arrive pas → déchiffrement et publication automatique
#
# Prérequis : pip install cryptography

import time
import json
import os
import base64
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  cryptography non installé : pip install cryptography")

logger = logging.getLogger("DMS.Crypto")


class CryptoDMS:
    """
    Dead Man's Switch avec chiffrement symétrique.

    Fonctionnement :
    1. L'opérateur chiffre un payload avec un mot de passe
    2. Le payload chiffré est stocké localement
    3. Si pas de check-in dans le délai → déchiffrement + action
    4. La clé n'est JAMAIS stockée — elle est dérivée du mot de passe
       qui doit être saisi à chaque check-in

    Sécurité : même si l'attaquant vole le fichier chiffré,
               sans le mot de passe = inutilisable.
    """

    def __init__(
        self,
        name: str,
        storage_dir: str,
        deadline_hours: float = 24.0,
        grace_hours: float = 2.0,
    ):
        if not CRYPTO_AVAILABLE:
            raise ImportError("Module cryptography requis")

        self.name = name
        self.storage = Path(storage_dir)
        self.storage.mkdir(parents=True, exist_ok=True)
        self.deadline_seconds = deadline_hours * 3600
        self.grace_seconds = grace_hours * 3600

        self.payload_file = self.storage / f"{name}_payload.enc"
        self.state_file = self.storage / f"{name}_state.json"
        self.salt_file = self.storage / f"{name}_salt.bin"

        self._stop_event = threading.Event()

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Dérive une clé Fernet depuis un mot de passe (PBKDF2)."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # OWASP 2023 recommandation
        )
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key)

    def seal_payload(self, payload: str, password: str):
        """
        Scelle le payload chiffré.
        Le payload ne pourra être déchiffré qu'avec le mot de passe.
        """
        # Générer un sel aléatoire
        salt = os.urandom(32)
        self.salt_file.write_bytes(salt)

        # Dériver la clé
        key = self._derive_key(password, salt)
        fernet = Fernet(key)

        # Chiffrer le payload
        encrypted = fernet.encrypt(payload.encode())
        self.payload_file.write_bytes(encrypted)

        # Hasher le mot de passe pour vérification future (sans stocker le MP)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt, 480000
        ).hex()

        logger.info(f"✅ Payload scellé ({len(encrypted)} bytes chiffrés)")
        return pwd_hash

    def checkin(self, password: str, pwd_hash: str) -> bool:
        """
        Effectue un check-in en vérifiant le mot de passe.
        Réinitialise le timer si correct.
        """
        if not self.salt_file.exists():
            logger.error("DMS non initialisé — utiliser seal_payload() d'abord")
            return False

        salt = self.salt_file.read_bytes()

        # Vérifier le mot de passe (sans stocker le MP lui-même)
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt, 480000
        ).hex()

        if computed_hash != pwd_hash:
            logger.warning("❌ Mot de passe incorrect — check-in refusé")
            return False

        # Enregistrer le check-in
        state = {
            "last_checkin": time.time(),
            "last_checkin_dt": datetime.now().isoformat(),
            "deadline_seconds": self.deadline_seconds,
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

        deadline = datetime.fromtimestamp(time.time() + self.deadline_seconds)
        logger.info(
            f"✅ Check-in enregistré — "
            f"deadline: {deadline.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return True

    def _trigger_action(self, password: str):
        """Déchiffre et publie le payload au déclenchement."""
        logger.critical("🔴 DMS DÉCLENCHÉ — déchiffrement du payload...")

        if not self.payload_file.exists() or not self.salt_file.exists():
            logger.error("Fichiers chiffrés introuvables !")
            return

        salt = self.salt_file.read_bytes()
        key = self._derive_key(password, salt)
        fernet = Fernet(key)

        try:
            encrypted = self.payload_file.read_bytes()
            decrypted = fernet.decrypt(encrypted).decode()

            logger.critical(f"Payload déchiffré ({len(decrypted)} caractères)")
            logger.critical("Publication en cours...")

            # Exemple : écrire dans un fichier public
            output = self.storage / f"{self.name}_RELEASED_{int(time.time())}.txt"
            output.write_text(decrypted)
            logger.critical(f"✅ Payload publié : {output}")

            # Ici : intégrer upload vers serveur distant, email, etc.

        except Exception as e:
            logger.error(f"Erreur déchiffrement: {e}")

    def start_monitoring(self, password: str, check_interval: float = 30.0):
        """
        Démarre la surveillance.
        ATTENTION : le mot de passe est en mémoire vive seulement.
        """
        self._stop_event.clear()

        def monitor():
            while not self._stop_event.is_set():
                try:
                    state_data = json.loads(self.state_file.read_text())
                    age = time.time() - state_data["last_checkin"]
                    remaining = self.deadline_seconds - age

                    if age >= self.deadline_seconds:
                        logger.critical(
                            f"Délai expiré depuis {age - self.deadline_seconds:.0f}s"
                        )

                        # Période de grâce
                        grace_end = time.time() + self.grace_seconds
                        logger.warning(
                            f"⏳ Période de grâce : {self.grace_seconds/3600:.1f}h"
                        )

                        while time.time() < grace_end:
                            # Vérifier nouveau check-in
                            new_state = json.loads(self.state_file.read_text())
                            if new_state["last_checkin"] > state_data["last_checkin"]:
                                logger.info("✅ Check-in pendant la grâce — DMS annulé !")
                                return
                            time.sleep(10)

                        # Déclencher
                        self._trigger_action(password)
                        break

                    else:
                        logger.debug(
                            f"DMS OK — reste {remaining/3600:.1f}h"
                        )

                except Exception as e:
                    logger.error(f"Erreur monitoring: {e}")

                self._stop_event.wait(check_interval)

        thread = threading.Thread(target=monitor, daemon=True, name=f"dms-crypto-{self.name}")
        thread.start()
        return thread


# Démonstration
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s [%(levelname)s]: %(message)s')

    dms = CryptoDMS(
        name="insurance",
        storage_dir="/tmp/dms_crypto",
        deadline_hours=0.005,  # ~18s pour la démo
        grace_hours=0.001,     # ~3s de grâce
    )

    SECRET_PASSWORD = "mon_mot_de_passe_tres_secret"
    PAYLOAD = """
    DÉCLARATION D'URGENCE — Document confidentiel
    Date : 2024-01-10
    
    Si vous lisez ceci, c'est que le Dead Man's Switch a été déclenché.
    Les informations suivantes sont à divulguer immédiatement :
    [Contenu de la déclaration d'urgence...]
    """

    print("1. Scellement du payload chiffré")
    pwd_hash = dms.seal_payload(PAYLOAD, SECRET_PASSWORD)
    print(f"   Hash du mot de passe (à stocker séparément) : {pwd_hash[:32]}...")

    print("\n2. Armement du DMS avec check-in initial")
    dms.checkin(SECRET_PASSWORD, pwd_hash)

    print("\n3. Démarrage de la surveillance (pas de check-in → déclenchement)")
    dms.start_monitoring(SECRET_PASSWORD, check_interval=3.0)

    time.sleep(30)
    print("\nDémo terminée — vérifier /tmp/dms_crypto/ pour le payload publié")
```

---

## MODULE 15 — Cas Réels — Cybersécurité & Haute Disponibilité

### 15.1 Heartbeat pour détection de split-brain (cluster)

```python
#!/usr/bin/env python3
# split_brain_guard.py
# Protège un cluster contre le split-brain via heartbeat + quorum

"""
PROBLÈME SPLIT-BRAIN :
  Cluster à 2 nœuds (A et B).
  Le réseau entre eux est coupé.
  A pense que B est mort → A prend le leadership
  B pense que A est mort → B prend le leadership
  → Les deux nœuds écrivent simultanément → CORRUPTION DE DONNÉES

SOLUTION QUORUM :
  3 nœuds minimum.
  Un nœud ne peut prendre le leadership que s'il voit la majorité.
  Avec réseau coupé entre A et B :
    A voit [A, C] = 2/3 → peut prendre le leadership
    B voit [B] = 1/3 → ne peut PAS prendre le leadership
  → Un seul leader possible
"""

import time
import json
import threading
import os
from typing import Dict, Set
import logging

logger = logging.getLogger("ClusterGuard")


class ClusterNode:
    def __init__(self, node_id: str, total_nodes: int, quorum_size: int):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.quorum_size = quorum_size  # nombre minimum pour le quorum
        self.is_leader = False
        self.seen_nodes: Set[str] = {node_id}  # nœuds visibles
        self._heartbeats: Dict[str, float] = {node_id: time.time()}
        self._lock = threading.Lock()

    def receive_heartbeat(self, from_node: str, timestamp: float):
        """Reçoit un heartbeat d'un autre nœud."""
        with self._lock:
            self._heartbeats[from_node] = timestamp
            self.seen_nodes.add(from_node)

    def check_quorum(self, timeout: float = 10.0) -> bool:
        """Vérifie si on a le quorum (majorité des nœuds)."""
        with self._lock:
            now = time.time()
            # Nœuds vivants = heartbeat récent
            alive = {
                node_id for node_id, ts in self._heartbeats.items()
                if (now - ts) <= timeout
            }
            has_quorum = len(alive) >= self.quorum_size
            logger.info(
                f"Nœud {self.node_id}: voit {len(alive)}/{self.total_nodes} nœuds "
                f"— quorum: {'✅' if has_quorum else '❌'}"
            )
            return has_quorum

    def attempt_leadership(self) -> bool:
        """Tente de prendre le leadership si quorum disponible."""
        if self.check_quorum():
            if not self.is_leader:
                self.is_leader = True
                logger.info(f"🏆 Nœud {self.node_id} devient LEADER")
            return True
        else:
            if self.is_leader:
                self.is_leader = False
                logger.warning(
                    f"⚠️  Nœud {self.node_id} PERD le leadership "
                    f"(quorum insuffisant — protection split-brain)"
                )
            return False
```

### 15.2 Kill switch pour service compromis

```bash
#!/bin/bash
# kill_switch.sh — Arrêt d'urgence automatique d'un service compromis
#
# Usage : Le service envoie un heartbeat toutes les 30s
# Si le heartbeat contient des indicateurs de compromission
# (CPU anormal, connexions suspectes, fichiers modifiés)
# → le kill switch s'active automatiquement

HEARTBEAT_FILE="/var/lib/myapp/heartbeat.json"
LOCKFILE="/var/run/kill_switch.lock"
LOG="/var/log/kill_switch.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

check_compromise_indicators() {
    local hb_file="$1"

    # Lire les métriques du heartbeat
    CPU=$(python3 -c "import json; d=json.load(open('$hb_file')); print(d.get('cpu_usage', 0))" 2>/dev/null)
    SUSPICIOUS_CONNS=$(python3 -c "import json; d=json.load(open('$hb_file')); print(d.get('suspicious_connections', 0))" 2>/dev/null)
    INTEGRITY_OK=$(python3 -c "import json; d=json.load(open('$hb_file')); print(d.get('integrity_check', 'true'))" 2>/dev/null)

    # Indicateurs de compromission
    local compromised=0

    if [ "${CPU%.*}" -gt 95 ] 2>/dev/null; then
        log "⚠️  CPU anormal: ${CPU}%"
        compromised=1
    fi

    if [ "${SUSPICIOUS_CONNS:-0}" -gt 0 ] 2>/dev/null; then
        log "⚠️  Connexions suspectes détectées: $SUSPICIOUS_CONNS"
        compromised=1
    fi

    if [ "$INTEGRITY_OK" = "false" ]; then
        log "⚠️  Vérification d'intégrité échouée"
        compromised=1
    fi

    return $compromised
}

emergency_shutdown() {
    local reason="$1"
    log "🔴 KILL SWITCH ACTIVÉ — Raison: $reason"

    # 1. Isoler le réseau du service
    log "Isolation réseau..."
    iptables -I OUTPUT -m owner --uid-owner myapp -j DROP 2>/dev/null
    iptables -I INPUT -m owner --uid-owner myapp -j DROP 2>/dev/null

    # 2. Arrêter le service
    log "Arrêt du service..."
    systemctl stop myapp.service

    # 3. Capturer l'état pour forensique
    log "Capture forensique..."
    ps auxf > /var/log/forensic_$(date +%s)_processes.txt
    ss -tnp > /var/log/forensic_$(date +%s)_network.txt
    journalctl -u myapp --since "1 hour ago" > /var/log/forensic_$(date +%s)_journal.txt

    # 4. Alerter l'équipe sécurité
    log "Envoi alerte sécurité..."
    logger -t kill-switch -p security.crit "KILL SWITCH: $reason"

    # 5. Créer le lockfile (empêche redémarrage automatique)
    echo "$reason" > "$LOCKFILE"

    log "Kill switch terminé — redémarrage manuel requis"
    exit 0
}

# Boucle principale
while true; do
    if [ ! -f "$HEARTBEAT_FILE" ]; then
        log "Heartbeat absent — service non démarré ou crashé"
        sleep 30
        continue
    fi

    AGE=$(( $(date +%s) - $(python3 -c "import json; d=json.load(open('$HEARTBEAT_FILE')); print(int(d.get('timestamp', 0)))") ))

    if [ "$AGE" -gt 90 ]; then
        emergency_shutdown "Heartbeat absent depuis ${AGE}s"
    fi

    if ! check_compromise_indicators "$HEARTBEAT_FILE"; then
        emergency_shutdown "Indicateurs de compromission détectés"
    fi

    sleep 15
done
```

---

## MODULE 16 — Challenge Final

### 🔴 Challenge Expert — Système de Surveillance Complet

**Objectif** : Concevoir et implémenter un système de surveillance combinant heartbeat distribué et dead man's switch, pour une infrastructure fictive critique.

```
CONTEXTE :
  Vous êtes ingénieur chez SecureBank. L'infrastructure critique comprend :
  - 3 serveurs API (web-01, web-02, web-03)
  - 1 serveur base de données (db-master)
  - 1 serveur de backup (backup-01)
  - 2 administrateurs (alice, bob)

EXIGENCES :

1. HEARTBEAT (35 points)
   a) Chaque serveur doit envoyer un heartbeat toutes les 10s
      incluant : CPU, mémoire, connexions actives, version de l'app
   
   b) Le moniteur central doit :
      - Alerter si un serveur ne répond plus depuis 25s
      - Déclencher un failover automatique si web-01 tombe
      - Ne pas déclencher d'alerte si 1 serveur sur 3 est en maintenance
      - Implémenter un quorum : action seulement si 2/3 monitors confirment la panne
   
   c) Anti-faux-positifs :
      - Healthcheck profond (tester une vraie requête DB depuis l'API)
      - Timeout exponentiel (5s, 10s, 20s avant alerte)

2. DEAD MAN'S SWITCH (35 points)
   a) Délai de déclenchement : 48h sans check-in
   b) Alertes préventives : à 24h, 12h, 6h, 2h, 30min avant expiration
   c) Check-in requiert : authentification TOTP + mot de passe
   d) Si déclenché :
      - Notifier alice ET bob (emails + SMS)
      - Révoquer tous les tokens JWT actifs
      - Activer le mode lecture seule sur la DB
      - Publier un rapport d'état horodaté et signé
   e) Le DMS doit être hébergé sur une infrastructure SÉPARÉE
      (pas sur les serveurs surveillés)

3. INTÉGRATION SYSTEMD (15 points)
   a) Les deux systèmes démarrent au boot
   b) Redémarrage automatique en cas de crash
   c) Logs dans journald avec rotation
   d) Timer pour les vérifications périodiques

4. DOCUMENTATION ET TESTS (15 points)
   a) README avec architecture en ASCII art
   b) Tests unitaires pour les fonctions critiques
   c) Script de test de régression automatique
   d) Runbook : procédures en cas d'alerte
```

**Critères d'évaluation :**

```
FONCTIONNEL (50%) :
  □ Le heartbeat détecte correctement les pannes
  □ Le DMS se déclenche exactement au bon moment
  □ Le quorum fonctionne (pas de faux positifs)
  □ Les actions d'urgence s'exécutent dans l'ordre
  □ La période de grâce annule correctement le déclenchement

ROBUSTESSE (25%) :
  □ Résistance aux erreurs réseau temporaires
  □ Gestion des fichiers corrompus
  □ Reprise après redémarrage système
  □ Pas de fuite mémoire (long run)

CODE QUALITY (25%) :
  □ Code lisible et commenté
  □ Gestion d'erreurs complète
  □ Tests automatisés
  □ Configuration externalisée (pas de hardcode)
```

**Squelette de solution :**

```python
# solution_architecture.py — Squelette à compléter

class SecureBankMonitor:
    """
    Système de surveillance complet pour SecureBank.
    Combine heartbeat distribué + DMS avec quorum.
    """

    def __init__(self, config_file: str):
        # TODO : charger la configuration depuis YAML/JSON
        self.config = self._load_config(config_file)

        # Composants heartbeat
        self.hb_senders = {}    # {server_name: HeartbeatSender}
        self.hb_watchers = {}   # {server_name: HeartbeatWatcher}
        self.cluster_monitor = None  # ClusterMonitor

        # Composant DMS
        self.dms = None  # DeadManSwitch

        # État global
        self.maintenance_mode = set()  # serveurs en maintenance

    def _load_config(self, config_file: str) -> dict:
        """TODO : implémenter le chargement de config"""
        pass

    def setup_heartbeats(self):
        """TODO : initialiser tous les heartbeat senders/watchers"""
        pass

    def setup_dms(self):
        """TODO : initialiser le DMS avec les actions d'urgence"""
        pass

    def perform_deep_health_check(self, server: str) -> bool:
        """TODO : healthcheck profond (DB query, etc.)"""
        pass

    def trigger_failover(self, failed_server: str):
        """TODO : basculement automatique"""
        pass

    def start(self):
        """TODO : démarrer tous les composants"""
        pass

    def stop(self):
        """TODO : arrêt propre"""
        pass
```

---

# ANNEXES

---

## ANNEXE A — Cheatsheet

```bash
# ══ HEARTBEAT — COMMANDES UTILES ══

# Tester un heartbeat fichier
$ stat -c %Y /tmp/heartbeat.touch    # timestamp de modification
$ date +%s                            # timestamp actuel
$ echo $(( $(date +%s) - $(stat -c %Y /tmp/heartbeat.touch) ))  # âge

# Voir les heartbeats Redis
$ redis-cli keys "heartbeat:*"
$ redis-cli get "heartbeat:mon-service"
$ redis-cli ttl "heartbeat:mon-service"   # TTL restant en secondes

# Surveiller en temps réel
$ watch -n1 'cat /tmp/heartbeat.json | python3 -m json.tool'
$ redis-cli subscribe heartbeat_events

# ══ DEAD MAN'S SWITCH ══

# Vérifier le délai restant
$ python3 -c "
import json, time
d = json.load(open('/tmp/dms_state.json'))
age = time.time() - d['last_checkin']
remaining = d['deadline_seconds'] - age
print(f'Age: {age/3600:.1f}h  Remaining: {remaining/3600:.1f}h')
"

# ══ SYSTEMD ══

$ systemctl status heartbeat-sender
$ journalctl -u heartbeat-sender -f --since "10 min ago"
$ systemctl list-timers
$ systemctl is-active heartbeat-watcher
```

## ANNEXE B — Comparaison des Solutions Production

```
Solution            │ Heartbeat  │ DMS  │ Distribué │ Complexité │ Cas d'usage
────────────────────┼────────────┼──────┼───────────┼────────────┼─────────────
Fichier touch       │     ✅     │  ✅  │     ❌    │  Faible    │ Scripts locaux
Systemd watchdog    │     ✅     │  ✅  │     ❌    │  Moyenne   │ Services Linux
Redis TTL           │     ✅     │  ✅  │     ✅    │  Moyenne   │ Microservices
etcd leases         │     ✅     │  ✅  │     ✅    │  Haute     │ Kubernetes
Consul              │     ✅     │  ❌  │     ✅    │  Haute     │ Service mesh
Prometheus + AM     │     ✅     │  ❌  │     ✅    │  Haute     │ Infra monitoring
Pacemaker/Corosync  │     ✅     │  ❌  │     ✅    │  Très haute│ Clusters HA
Dead Man's Snitch   │     ✅     │  ✅  │     SaaS  │  Faible    │ SaaS cron monitor
```

## ANNEXE C — Ressources

```
DOCUMENTATION :
  systemd.watchdog(7)              → man systemd.watchdog
  /dev/watchdog                    → Linux Hardware Watchdog
  RFC 5424                         → Syslog Protocol
  etcd lease API                   → etcd.io/docs/v3.5/learning/api

OUTILS OPEN SOURCE :
  Consul        → consul.io           (service discovery + health checks)
  Patroni       → github/zalando      (DMS pour PostgreSQL)
  keepalived    → keepalived.org      (VRRP + heartbeat)
  Pacemaker     → clusterlabs.org     (cluster resource manager)
  Dead Man's    → deadmanssnitch.com  (SaaS DMS pour cron jobs)
  Snitch

LECTURE RECOMMANDÉE :
  "Designing Distributed Systems" — Brendan Burns (O'Reilly)
  "Release It!" — Michael Nygard (Pragmatic Programmer)
  "Site Reliability Engineering" — Google (SRE Book, libre en ligne)
```

---

*TP rédigé pour une progression complète de zéro à expert*  
*Tester dans un environnement isolé — ne jamais déployer un DMS en production sans revue de sécurité*  
*Les délais dans les démos sont volontairement raccourcis — adapter en production*
