# 🔀 TP Pédagogique — Les Proxies en Profondeur
### De zéro à expert · Architecture, protocoles, implémentation, détection · 2026

> **⚠️ Avertissement éthique**  
> Ce TP est strictement pédagogique. Les techniques présentées doivent être utilisées **uniquement sur vos propres infrastructures** ou avec une autorisation explicite. L'utilisation de proxies pour contourner des restrictions légales, espionner des communications ou masquer des activités illicites est punissable par la loi.

---

## 📚 Table des matières

1. [Fondamentaux — Qu'est-ce qu'un proxy ?](#1-fondamentaux)
2. [Taxonomie complète des proxies](#2-taxonomie)
3. [Niveau 1 — Proxies HTTP/HTTPS](#3-niveau-1--http--https)
4. [Niveau 2 — Proxies SOCKS](#4-niveau-2--socks)
5. [Niveau 3 — Reverse Proxy](#5-niveau-3--reverse-proxy)
6. [Niveau 4 — Implémentation from scratch](#6-niveau-4--implémentation)
7. [Niveau 5 — Chaînage et anonymisation](#7-niveau-5--chaînage)
8. [Niveau 6 — Détection et fingerprinting](#8-niveau-6--détection)
9. [Niveau Expert — Proxy transparent & interception TLS](#9-niveau-expert)
10. [Exercices pratiques](#10-exercices-pratiques)
11. [Outils de référence 2026](#11-outils-de-référence)

---

## 1. Fondamentaux

### 1.1 Le problème que résout un proxy

Sans proxy, la communication est **directe** :

```
[Client] ──────────────────────────► [Serveur]
  IP: 192.168.1.10                    IP: 93.184.216.34
  Voit directement le serveur         Voit directement le client
```

Avec un proxy, la communication est **indirecte** :

```
[Client] ──────► [Proxy] ──────► [Serveur]
  192.168.1.10    10.0.0.1        93.184.216.34
                     ↑
              Le serveur voit l'IP du proxy
              Le proxy voit les deux parties
```

### 1.2 Les 5 rôles fondamentaux d'un proxy

| Rôle | Description | Exemple concret |
|------|-------------|----------------|
| **Anonymisation** | Masquer l'IP du client | Navigation privée |
| **Filtrage** | Bloquer/autoriser du contenu | Proxy d'entreprise |
| **Cache** | Stocker les réponses | Squid, Varnish |
| **Load balancing** | Répartir la charge | Nginx, HAProxy |
| **Inspection** | Analyser le trafic | Firewall applicatif |

### 1.3 Proxy vs VPN vs NAT — Les différences

```
NAT (Network Address Translation)
  Niveau : Couche 3 (réseau)
  Protocole : Tous
  Transparence : Totalement transparent pour l'application
  Usage : Partage d'une IP publique entre plusieurs machines

PROXY
  Niveau : Couche 7 (application)
  Protocole : Spécifique (HTTP, SOCKS...)
  Transparence : L'application doit être configurée (sauf proxy transparent)
  Usage : Filtrage, anonymisation, cache

VPN
  Niveau : Couche 3 (ou 2)
  Protocole : Tous (tunnel chiffré)
  Transparence : Transparent pour toutes les applications
  Usage : Tunnel sécurisé, contournement de restrictions
```

---

## 2. Taxonomie

### 2.1 Carte mentale des types de proxies

```
PROXIES
├── Par direction
│   ├── Forward Proxy (client → proxy → internet)
│   └── Reverse Proxy (internet → proxy → serveurs internes)
│
├── Par protocole
│   ├── HTTP Proxy (port 8080, 3128...)
│   ├── HTTPS/CONNECT Proxy (tunnel SSL)
│   ├── SOCKS4 (TCP uniquement)
│   ├── SOCKS4a (+ résolution DNS déléguée)
│   └── SOCKS5 (TCP + UDP + auth + IPv6)
│
├── Par niveau d'anonymat
│   ├── Transparent (révèle l'IP réelle via X-Forwarded-For)
│   ├── Anonymous (cache l'IP mais révèle être un proxy)
│   └── Elite/High-Anonymous (invisible — ne révèle rien)
│
├── Par architecture
│   ├── Proxy simple
│   ├── Proxy chaîné (proxy chain)
│   ├── Proxy rotatif (rotation d'IPs)
│   └── Proxy résidentiel (IPs de vraies machines)
│
└── Par usage spécifique
    ├── Web proxy (HTTP/HTTPS)
    ├── DNS proxy
    ├── SMTP proxy (mail)
    ├── FTP proxy
    └── Proxy transparent (interception sans config client)
```

### 2.2 Les en-têtes HTTP révélatrices

```
# Un proxy transparent ou anonyme ajoute ces en-têtes :
X-Forwarded-For: 192.168.1.10, 10.0.0.1
Via: 1.1 proxy.example.com (squid/5.0)
X-Real-IP: 192.168.1.10
X-Proxy-ID: abc123
Forwarded: for=192.168.1.10; by=10.0.0.1; proto=http

# Un proxy elite ne les ajoute PAS → le serveur voit seulement l'IP du proxy
```

---

## 3. Niveau 1 — HTTP / HTTPS

### 3.1 Fonctionnement du proxy HTTP

Le proxy HTTP est un **intermédiaire applicatif**. Il comprend le protocole HTTP et peut lire, modifier, filtrer les requêtes.

```
Client → Proxy : requête HTTP complète avec URL absolue
GET http://example.com/page HTTP/1.1
Host: example.com
Proxy-Authorization: Basic dXNlcjpwYXNz  (si auth requise)

Proxy → Serveur : requête HTTP normale
GET /page HTTP/1.1
Host: example.com
X-Forwarded-For: 192.168.1.10  (selon config)
```

### 3.2 Utiliser un proxy HTTP avec curl

```bash
# Proxy HTTP explicite
curl -x http://proxy.example.com:8080 http://example.com

# Proxy avec authentification
curl -x http://user:pass@proxy.example.com:8080 http://example.com

# Variable d'environnement (affecte toutes les commandes)
export http_proxy="http://proxy.example.com:8080"
export https_proxy="http://proxy.example.com:8080"
export no_proxy="localhost,127.0.0.1,192.168.0.0/16"

curl http://example.com    # utilise http_proxy automatiquement

# Unset
unset http_proxy https_proxy

# Vérifier que le proxy fonctionne
curl -x http://proxy:8080 -s https://ipinfo.io/ip
# Doit retourner l'IP du proxy, pas votre IP réelle
```

### 3.3 La méthode CONNECT (proxy HTTPS)

Pour HTTPS, le proxy ne peut pas lire le trafic chiffré. Il utilise la méthode **CONNECT** pour créer un tunnel opaque.

```
Client → Proxy :
CONNECT example.com:443 HTTP/1.1
Host: example.com:443
Proxy-Authorization: Basic ...

Proxy → Client :
HTTP/1.1 200 Connection established

[Tunnel TCP brut établi — proxy ne voit que des octets chiffrés]

Client ←──── TLS Handshake ────► Serveur
       (à travers le tunnel)
```

```bash
# Visualiser la méthode CONNECT en action
curl -v -x http://proxy:8080 https://example.com 2>&1 | grep -A5 "CONNECT"

# Test manuel avec netcat (éducatif)
# Connexion au proxy
nc proxy.example.com 8080 <<'EOF'
CONNECT example.com:443 HTTP/1.1
Host: example.com:443

EOF
# Le proxy répond : HTTP/1.1 200 Connection established
```

### 3.4 Configurer Squid (proxy HTTP/HTTPS)

```bash
# Installation
sudo apt install squid -y

# Configuration minimale : /etc/squid/squid.conf
sudo tee /etc/squid/squid.conf <<'EOF'
# Port d'écoute
http_port 3128

# ACL réseau local autorisé
acl localnet src 192.168.0.0/16
acl localnet src 10.0.0.0/8
acl localnet src 172.16.0.0/12

# Ports autorisés
acl SSL_ports port 443
acl Safe_ports port 80 21 443 70 210 1025-65535

# Règles d'accès
http_access deny !Safe_ports
http_access allow localnet
http_access allow localhost
http_access deny all

# Cache
cache_mem 256 MB
cache_dir ufs /var/spool/squid 10000 16 256
maximum_object_size 100 MB

# Logs
access_log /var/log/squid/access.log squid
EOF

# Démarrage
sudo squid -z        # initialiser le cache
sudo systemctl start squid
sudo systemctl enable squid

# Test
curl -x http://localhost:3128 http://example.com -v

# Surveiller les logs en temps réel
sudo tail -f /var/log/squid/access.log
```

### 3.5 Proxy avec authentification

```bash
# Créer un fichier de mots de passe
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/squid/passwd user1
sudo htpasswd /etc/squid/passwd user2

# Ajouter à squid.conf
cat >> /etc/squid/squid.conf <<'EOF'
# Authentification Basic
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
auth_param basic realm "Proxy Squid"
auth_param basic credentialsttl 2 hours

acl authenticated proxy_auth REQUIRED
http_access allow authenticated
EOF

sudo systemctl restart squid

# Test avec auth
curl -x http://user1:monpass@localhost:3128 http://example.com
```

---

## 4. Niveau 2 — SOCKS

### 4.1 SOCKS vs HTTP : les différences fondamentales

```
HTTP Proxy                          SOCKS Proxy
──────────────────────────────      ──────────────────────────────
Comprend HTTP                       Protocole agnostique (tout TCP/UDP)
Peut lire/modifier les requêtes     Tunnel opaque de niveau transport
Port standard : 8080, 3128          Port standard : 1080
Fonctionne surtout pour HTTP/S      Fonctionne pour FTP, SSH, SMTP...
X-Forwarded-For possible            Pas d'en-têtes applicatives ajoutées
```

### 4.2 SOCKS4 vs SOCKS4a vs SOCKS5

```
SOCKS4
  ✓ TCP uniquement
  ✓ IPv4 seulement
  ✗ Pas d'authentification
  ✗ Le client résout le DNS lui-même (fuite DNS possible!)

SOCKS4a
  ✓ TCP uniquement
  ✓ Peut déléguer la résolution DNS au proxy
  ✗ Pas d'authentification

SOCKS5 (RFC 1928)
  ✓ TCP + UDP
  ✓ IPv4 + IPv6
  ✓ Authentification (user/pass, GSSAPI)
  ✓ Résolution DNS déléguée au proxy (pas de fuite DNS)
  ✓ Bind (le serveur initie la connexion vers le client)
```

### 4.3 Utiliser SOCKS5 avec curl

```bash
# SOCKS5 basique
curl --socks5 proxy.example.com:1080 http://example.com

# SOCKS5 avec résolution DNS côté proxy (évite les fuites DNS)
curl --socks5-hostname proxy.example.com:1080 http://example.com

# SOCKS5 avec authentification
curl --socks5 user:pass@proxy.example.com:1080 http://example.com

# SOCKS4
curl --socks4 proxy.example.com:1080 http://example.com

# Via variable d'environnement
export ALL_PROXY="socks5h://user:pass@proxy.example.com:1080"
# "socks5h" = socks5 + hostname resolution (le h = hostname)
curl http://example.com

# Vérification de l'IP
curl --socks5-hostname proxy:1080 -s https://ipinfo.io/ip
```

### 4.4 Le protocole SOCKS5 en détail

```
PHASE 1 — Négociation d'authentification
─────────────────────────────────────────
Client → Proxy :
  VER=0x05  NMETHODS=0x02  METHODS=[0x00, 0x02]
  (version 5, 2 méthodes supportées: no-auth et user/pass)

Proxy → Client :
  VER=0x05  METHOD=0x02
  (version 5, on choisit user/pass)

PHASE 2 — Authentification (si METHOD=0x02)
────────────────────────────────────────────
Client → Proxy :
  VER=0x01  ULEN  USERNAME  PLEN  PASSWORD

Proxy → Client :
  VER=0x01  STATUS=0x00  (0x00 = succès)

PHASE 3 — Requête de connexion
────────────────────────────────
Client → Proxy :
  VER=0x05  CMD=0x01  RSV=0x00  ATYP=0x03
  ADDR_LEN  "example.com"  PORT=0x01BB (443)
  
  CMD : 0x01=CONNECT, 0x02=BIND, 0x03=UDP ASSOCIATE
  ATYP: 0x01=IPv4, 0x03=hostname, 0x04=IPv6

Proxy → Client :
  VER=0x05  REP=0x00  RSV=0x00  ATYP  BIND_ADDR  BIND_PORT
  (REP=0x00 = succès)

PHASE 4 — Tunnel établi
────────────────────────
Données TCP transitent librement dans les deux sens
```

### 4.5 Implémenter un client SOCKS5 minimal en Python

```python
#!/usr/bin/env python3
# socks5_client.py — Client SOCKS5 from scratch (éducatif)

import socket
import struct

def socks5_connect(proxy_host: str, proxy_port: int,
                   target_host: str, target_port: int,
                   username: str = None, password: str = None) -> socket.socket:
    """
    Établit une connexion TCP via un proxy SOCKS5.
    Retourne le socket prêt à l'emploi.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((proxy_host, proxy_port))
    
    # --- Phase 1 : Négociation méthode d'auth ---
    if username and password:
        # Proposer no-auth (0x00) et user/pass (0x02)
        sock.sendall(b'\x05\x02\x00\x02')
    else:
        # Proposer uniquement no-auth
        sock.sendall(b'\x05\x01\x00')
    
    resp = sock.recv(2)
    if resp[0] != 0x05:
        raise Exception("Le serveur n'est pas un proxy SOCKS5")
    chosen_method = resp[1]
    
    # --- Phase 2 : Authentification ---
    if chosen_method == 0x02:
        if not username or not password:
            raise Exception("Le proxy requiert une authentification")
        
        user_bytes = username.encode()
        pass_bytes = password.encode()
        auth_msg = (
            b'\x01' +
            bytes([len(user_bytes)]) + user_bytes +
            bytes([len(pass_bytes)]) + pass_bytes
        )
        sock.sendall(auth_msg)
        
        auth_resp = sock.recv(2)
        if auth_resp[1] != 0x00:
            raise Exception("Authentification SOCKS5 échouée")
            
    elif chosen_method == 0xFF:
        raise Exception("Aucune méthode d'auth acceptable")
    
    # --- Phase 3 : Requête CONNECT ---
    host_bytes = target_host.encode()
    request = (
        b'\x05'                       # VER
        b'\x01'                       # CMD = CONNECT
        b'\x00'                       # RSV
        b'\x03'                       # ATYP = hostname
        + bytes([len(host_bytes)])    # longueur hostname
        + host_bytes                  # hostname
        + struct.pack('>H', target_port)  # port big-endian
    )
    sock.sendall(request)
    
    # Lire la réponse
    resp = sock.recv(4)
    if resp[1] != 0x00:
        errors = {
            0x01: "Erreur générale",
            0x02: "Connexion refusée par les règles",
            0x03: "Réseau inaccessible",
            0x04: "Hôte inaccessible",
            0x05: "Connexion refusée",
            0x07: "Commande non supportée",
            0x08: "Type d'adresse non supporté",
        }
        raise Exception(f"SOCKS5 erreur: {errors.get(resp[1], 'Inconnue')}")
    
    # Consommer le reste de la réponse (BIND_ADDR + BIND_PORT)
    atyp = resp[3]
    if atyp == 0x01:    sock.recv(4)    # IPv4
    elif atyp == 0x03:  sock.recv(sock.recv(1)[0])  # hostname
    elif atyp == 0x04:  sock.recv(16)   # IPv6
    sock.recv(2)  # BIND_PORT
    
    print(f"✓ Tunnel SOCKS5 établi vers {target_host}:{target_port}")
    return sock


# --- Exemple d'utilisation ---
if __name__ == "__main__":
    try:
        sock = socks5_connect(
            proxy_host="127.0.0.1",
            proxy_port=1080,
            target_host="example.com",
            target_port=80
        )
        
        # Envoyer une requête HTTP simple à travers le tunnel
        req = b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n"
        sock.sendall(req)
        
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        
        print(response[:500].decode(errors='replace'))
        sock.close()
        
    except Exception as e:
        print(f"Erreur : {e}")
```

```bash
# Tester le client (avec un proxy SOCKS5 local, ex: SSH tunnel)
# D'abord créer un proxy SOCKS5 local via SSH :
ssh -D 1080 user@serveur.example.com -N &

# Puis tester notre client
python3 socks5_client.py
```

---

## 5. Niveau 3 — Reverse Proxy

### 5.1 Concept : le proxy inverse

Un **reverse proxy** se place devant les serveurs, pas devant les clients. Il est transparent pour les clients — ils croient parler directement au serveur final.

```
Forward Proxy :          Reverse Proxy :
─────────────────        ──────────────────────────────────
[Client] → [Proxy]       [Internet] → [Reverse Proxy]
[Proxy]  → [Server]      [Rev.Proxy] → [Backend 1]
                         [Rev.Proxy] → [Backend 2]
                         [Rev.Proxy] → [Backend 3]
```

**Cas d'usage :**
- Load balancing entre plusieurs backends
- Terminaison TLS (le certificat SSL est sur le reverse proxy)
- Cache et compression
- Protection WAF (Web Application Firewall)
- Routing par chemin ou nom de domaine

### 5.2 Nginx comme reverse proxy

```bash
sudo apt install nginx -y

# Configuration reverse proxy basique
sudo tee /etc/nginx/sites-available/reverse_proxy <<'NGINX'
server {
    listen 80;
    server_name proxy.example.com;

    # Reverse proxy simple vers un backend
    location / {
        proxy_pass http://127.0.0.1:8000;
        
        # En-têtes importantes
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_read_timeout 60s;
        
        # Buffers
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 8 8k;
    }
    
    # Proxy différent selon le chemin
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;  # note le / final : rewrite
    }
    
    location /static/ {
        alias /var/www/static/;  # servi directement, sans proxy
    }
}
NGINX

# Load balancing avec Nginx
sudo tee /etc/nginx/sites-available/load_balancer <<'NGINX'
upstream backend_pool {
    # Méthodes : round_robin (défaut), least_conn, ip_hash, random
    least_conn;
    
    server 10.0.0.1:8000 weight=3;  # reçoit 3x plus de trafic
    server 10.0.0.2:8000 weight=1;
    server 10.0.0.3:8000 backup;    # utilisé seulement si les autres tombent
    
    keepalive 32;  # connexions persistantes vers les backends
}

server {
    listen 443 ssl;
    server_name example.com;
    
    ssl_certificate /etc/ssl/certs/example.crt;
    ssl_certificate_key /etc/ssl/private/example.key;
    
    location / {
        proxy_pass http://backend_pool;
        proxy_http_version 1.1;
        proxy_set_header Connection "";  # requis pour keepalive
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
NGINX

sudo ln -s /etc/nginx/sites-available/reverse_proxy /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 5.3 HAProxy — load balancer expert

```bash
sudo apt install haproxy -y

sudo tee /etc/haproxy/haproxy.cfg <<'HAPROXY'
global
    log /dev/log local0
    maxconn 50000
    user haproxy
    group haproxy

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5s
    timeout client  30s
    timeout server  30s

frontend http_in
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/combined.pem
    
    # Redirection HTTP → HTTPS
    redirect scheme https if !{ ssl_fc }
    
    # Routing selon l'en-tête Host
    acl host_api hdr(host) -i api.example.com
    acl host_app hdr(host) -i app.example.com
    
    use_backend api_servers if host_api
    use_backend app_servers if host_app
    default_backend app_servers

backend api_servers
    balance roundrobin
    option httpchk GET /health
    server api1 10.0.0.1:8000 check
    server api2 10.0.0.2:8000 check

backend app_servers
    balance leastconn
    cookie SERVERID insert indirect nocache
    server app1 10.0.0.3:3000 check cookie app1
    server app2 10.0.0.4:3000 check cookie app2

# Interface de monitoring
frontend stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
HAPROXY

sudo haproxy -c -f /etc/haproxy/haproxy.cfg  # vérification syntaxe
sudo systemctl restart haproxy
```

---

## 6. Niveau 4 — Implémentation

### 6.1 Proxy HTTP from scratch en Python

```python
#!/usr/bin/env python3
# http_proxy.py — Proxy HTTP/CONNECT minimal éducatif
# Usage : python3 http_proxy.py 8888

import socket
import threading
import select
import sys

LISTEN_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
BUFFER_SIZE = 65536

def handle_client(client_sock: socket.socket, addr: tuple):
    """Gère une connexion client entrante."""
    try:
        request = client_sock.recv(BUFFER_SIZE)
        if not request:
            return
        
        first_line = request.split(b'\r\n')[0].decode(errors='replace')
        method, url, version = first_line.split(' ', 2)
        
        print(f"[{addr[0]}] {method} {url}")
        
        if method == 'CONNECT':
            # ── Méthode CONNECT (HTTPS) ──
            handle_connect(client_sock, url)
        else:
            # ── Méthode GET/POST/... (HTTP) ──
            handle_http(client_sock, request, url)
            
    except Exception as e:
        print(f"[ERREUR] {e}")
    finally:
        client_sock.close()


def handle_connect(client_sock: socket.socket, hostport: str):
    """Gère le tunnel CONNECT pour HTTPS."""
    host, port = hostport.rsplit(':', 1)
    port = int(port)
    
    try:
        # Connexion au serveur cible
        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_sock.connect((host, port))
        
        # Informer le client que le tunnel est établi
        client_sock.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        
        # Relayer les données dans les deux sens
        relay_tcp(client_sock, remote_sock)
        
    except Exception as e:
        client_sock.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
        print(f"[CONNECT erreur] {host}:{port} → {e}")


def handle_http(client_sock: socket.socket, request: bytes, url: str):
    """Gère une requête HTTP standard."""
    # Extraire host et port depuis l'URL
    if url.startswith('http://'):
        url_stripped = url[7:]
    else:
        url_stripped = url
    
    if '/' in url_stripped:
        hostport, path = url_stripped.split('/', 1)
        path = '/' + path
    else:
        hostport, path = url_stripped, '/'
    
    if ':' in hostport:
        host, port = hostport.rsplit(':', 1)
        port = int(port)
    else:
        host, port = hostport, 80
    
    try:
        # Connexion au serveur
        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_sock.connect((host, port))
        
        # Réécrire la requête (URL absolue → relative)
        lines = request.split(b'\r\n')
        first_line_parts = lines[0].split(b' ')
        lines[0] = first_line_parts[0] + b' ' + path.encode() + b' ' + first_line_parts[2]
        
        # Supprimer l'en-tête Proxy-Connection
        lines = [l for l in lines if not l.lower().startswith(b'proxy-connection:')]
        
        modified_request = b'\r\n'.join(lines)
        remote_sock.sendall(modified_request)
        
        # Relayer la réponse
        while True:
            data = remote_sock.recv(BUFFER_SIZE)
            if not data:
                break
            client_sock.sendall(data)
            
        remote_sock.close()
        
    except Exception as e:
        print(f"[HTTP erreur] {host}:{port} → {e}")


def relay_tcp(sock1: socket.socket, sock2: socket.socket):
    """Relaie des données TCP bidirectionnellement."""
    sockets = [sock1, sock2]
    try:
        while True:
            readable, _, exceptional = select.select(sockets, [], sockets, 60)
            
            if exceptional:
                break
                
            for s in readable:
                other = sock2 if s is sock1 else sock1
                data = s.recv(BUFFER_SIZE)
                if not data:
                    return
                other.sendall(data)
    except:
        pass
    finally:
        sock1.close()
        sock2.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(100)
    
    print(f"🔀 Proxy HTTP démarré sur le port {LISTEN_PORT}")
    print(f"   Configurer : export http_proxy=http://localhost:{LISTEN_PORT}")
    
    while True:
        client_sock, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(client_sock, addr))
        t.daemon = True
        t.start()


if __name__ == '__main__':
    main()
```

```bash
# Lancer le proxy
python3 http_proxy.py 8888

# Dans un autre terminal, tester
curl -x http://localhost:8888 http://example.com
curl -x http://localhost:8888 https://example.com
```

### 6.2 Proxy SOCKS5 simple en Python

```python
#!/usr/bin/env python3
# socks5_server.py — Serveur SOCKS5 minimal (éducatif)

import socket
import struct
import threading
import select
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 1080
BUFFER = 65536

def handle(client: socket.socket):
    try:
        # Phase 1 : négociation
        data = client.recv(2)
        ver, nmethods = data[0], data[1]
        methods = client.recv(nmethods)
        
        if ver != 5:
            client.close(); return
        
        # On accepte sans authentification (méthode 0x00)
        client.sendall(b'\x05\x00')
        
        # Phase 3 : requête
        data = client.recv(4)
        ver, cmd, rsv, atyp = data
        
        if atyp == 0x01:    # IPv4
            addr_bytes = client.recv(4)
            target_host = socket.inet_ntoa(addr_bytes)
        elif atyp == 0x03:  # hostname
            length = client.recv(1)[0]
            target_host = client.recv(length).decode()
        elif atyp == 0x04:  # IPv6
            addr_bytes = client.recv(16)
            target_host = socket.inet_ntop(socket.AF_INET6, addr_bytes)
        else:
            client.close(); return
        
        port_bytes = client.recv(2)
        target_port = struct.unpack('>H', port_bytes)[0]
        
        print(f"  CONNECT → {target_host}:{target_port}")
        
        if cmd == 0x01:  # CONNECT
            try:
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((target_host, target_port))
                
                # Réponse de succès
                local_ip = socket.inet_aton(remote.getsockname()[0])
                local_port = struct.pack('>H', remote.getsockname()[1])
                client.sendall(b'\x05\x00\x00\x01' + local_ip + local_port)
                
                # Relais bidirectionnel
                relay(client, remote)
                
            except Exception as e:
                client.sendall(b'\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00')
        else:
            client.sendall(b'\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00')
            
    except Exception as e:
        print(f"[ERR] {e}")
    finally:
        client.close()


def relay(a: socket.socket, b: socket.socket):
    sockets = [a, b]
    try:
        while True:
            r, _, ex = select.select(sockets, [], sockets, 30)
            if ex: break
            for s in r:
                other = b if s is a else a
                data = s.recv(BUFFER)
                if not data: return
                other.sendall(data)
    except: pass


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', PORT))
server.listen(100)
print(f"🧦 Proxy SOCKS5 sur le port {PORT}")

while True:
    client, addr = server.accept()
    print(f"[+] Connexion de {addr[0]}")
    threading.Thread(target=handle, args=(client,), daemon=True).start()
```

```bash
python3 socks5_server.py 1080

# Test
curl --socks5-hostname localhost:1080 http://example.com
curl --socks5-hostname localhost:1080 -s https://ipinfo.io/ip
```

---

## 7. Niveau 5 — Chaînage

### 7.1 ProxyChains — chaîner plusieurs proxies

```bash
# Installation
sudo apt install proxychains4 -y

# Configuration : /etc/proxychains4.conf
sudo tee /etc/proxychains4.conf <<'EOF'
# Mode de chaînage
# dynamic_chain  = ignore les proxies morts, continue la chaîne
# strict_chain   = tous les proxies doivent fonctionner
# round_robin_chain = rotation à chaque connexion
# random_chain   = ordre aléatoire

dynamic_chain

proxy_dns     # résoudre DNS via le proxy (pas de fuite!)
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
# type  host          port  [user  pass]
socks5  127.0.0.1     1080
socks5  10.0.0.1      1080  user  pass
http    proxy2.lan    8080
socks4  proxy3.example.com  1080
EOF

# Utilisation : faire passer n'importe quel outil via la chaîne
proxychains4 curl https://ipinfo.io/ip
proxychains4 wget http://example.com
proxychains4 nmap -sT -Pn -p 80,443 example.com
proxychains4 ssh user@remote.server
proxychains4 python3 mon_script.py
```

### 7.2 Chaînage SSH (tunnel SOCKS5 dynamique)

```bash
# Créer un proxy SOCKS5 sur un serveur distant via SSH
# -D port_local : active le dynamic forwarding (SOCKS5)
# -N : pas de commande, juste le tunnel
# -f : fond de tâche

ssh -D 1080 -N -f user@serveur1.example.com

# Chaîner deux serveurs SSH
ssh -D 1080 -N -f -J user@jump.example.com user@serveur_final.example.com
# -J = ProxyJump : passe par un serveur intermédiaire

# Vérifier que le tunnel est actif
ss -tlnp | grep 1080

# Utiliser le tunnel
curl --socks5-hostname localhost:1080 https://ipinfo.io/ip
# → IP de serveur1.example.com

# Tunnel local (port forwarding)
ssh -L 8080:intranet.internal:80 user@bastion.example.com -N
# localhost:8080 → intranet.internal:80 via bastion
curl http://localhost:8080

# Tunnel inverse (reverse tunnel)
ssh -R 9090:localhost:22 user@serveur_public.com -N
# Depuis serveur_public.com : ssh localhost -p 9090 → revient sur notre machine
```

### 7.3 Architecture de chaînage avancée

```
Requête : client → proxy1 → proxy2 → proxy3 → destination

Anonymat :
- destination voit l'IP de proxy3
- proxy3 voit l'IP de proxy2
- proxy2 voit l'IP de proxy1
- proxy1 voit l'IP réelle du client

⚠️  Chaque proxy de la chaîne peut loguer le trafic.
    La chaîne est aussi solide que son maillon le plus faible.
    
Tor applique ce principe avec chiffrement en couches (onion routing) :
- Chaque nœud ne connaît que le suivant et le précédent
- Le trafic est chiffré en couches successives
```

```bash
# Tor comme proxy SOCKS5 local
sudo apt install tor -y
sudo systemctl start tor

# Tor écoute sur 9050 (SOCKS5) par défaut
curl --socks5-hostname localhost:9050 https://check.torproject.org/api/ip

# Combiner VPN + Tor + ProxyChains
# [Vous] → VPN → Tor → ProxyChains (SOCKS5) → Destination
# Configuration ProxyChains avec Tor + proxy supplémentaire :
cat >> /etc/proxychains4.conf <<'EOF'
socks5  127.0.0.1  9050   # Tor
socks5  proxy.example.com 1080  # proxy supplémentaire
EOF
```

---

## 8. Niveau 6 — Détection

### 8.1 En-têtes HTTP révélatrices

```bash
# Serveur de test qui affiche toutes les en-têtes reçues
python3 - <<'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler

class EchoHeaders(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        
        output = f"IP source connexion TCP : {self.client_address[0]}\n\n"
        output += "En-têtes HTTP reçues :\n"
        output += "─" * 40 + "\n"
        for key, value in self.headers.items():
            output += f"  {key}: {value}\n"
        
        # Analyser les en-têtes suspectes
        output += "\n─── Analyse ───\n"
        suspicious = {
            'X-Forwarded-For': 'proxy transparent/anonyme',
            'Via': 'proxy HTTP',
            'X-Real-IP': 'reverse proxy',
            'Forwarded': 'proxy RFC 7239',
            'X-Proxy-ID': 'proxy identifié',
            'Proxy-Connection': 'proxy explicite',
            'X-BlueCoat-Via': 'proxy BlueCoat entreprise',
            'X-Squid-Error': 'proxy Squid',
        }
        found = False
        for h, desc in suspicious.items():
            if h in self.headers:
                output += f"  ⚠️  {h} détecté → {desc}\n"
                found = True
        if not found:
            output += "  ✅ Aucune en-tête proxy détectée\n"
        
        self.wfile.write(output.encode())
    
    def log_message(self, *args): pass  # Silencieux

print("Serveur sur http://localhost:8000")
print("Testez avec : curl -x http://votre_proxy:port http://localhost:8000")
HTTPServer(('0.0.0.0', 8000), EchoHeaders).serve_forever()
EOF
```

### 8.2 Script de détection proxy complet

```python
#!/usr/bin/env python3
# detect_proxy.py — Détection multi-méthodes d'un proxy

import requests
import socket
import time

PROXY_HEADERS = [
    'X-Forwarded-For', 'X-Real-IP', 'Via', 'Forwarded',
    'X-Proxy-ID', 'X-BlueCoat-Via', 'X-Squid-Error',
    'Proxy-Connection', 'X-Forwarded-Host', 'X-Forwarded-Server',
    'Client-IP', 'True-Client-IP', 'CF-Connecting-IP',
]

KNOWN_PROXY_PORTS = [
    80, 8080, 8888, 3128, 1080, 8118, 9050, 8083, 9080,
    4444, 3333, 1234, 7070, 6588, 8000, 9090
]

def check_open_ports(ip: str, timeout: float = 1.0) -> list:
    """Vérifie les ports proxy courants sur une IP."""
    open_ports = []
    for port in KNOWN_PROXY_PORTS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    return open_ports


def analyze_headers(headers: dict) -> list:
    """Analyse les en-têtes HTTP pour détecter un proxy."""
    findings = []
    for h in PROXY_HEADERS:
        if h in headers:
            findings.append(f"En-tête '{h}': {headers[h]}")
    return findings


def check_latency_consistency(url: str, n: int = 5) -> dict:
    """Mesure la variance de latence (élevée → proxy probable)."""
    latencies = []
    for _ in range(n):
        start = time.time()
        try:
            requests.get(url, timeout=5)
            latencies.append((time.time() - start) * 1000)
        except:
            pass
        time.sleep(0.1)
    
    if not latencies:
        return {}
    
    avg = sum(latencies) / len(latencies)
    variance = sum((x - avg) ** 2 for x in latencies) / len(latencies)
    import math
    stdev = math.sqrt(variance)
    
    return {
        "avg_ms": round(avg, 1),
        "stdev_ms": round(stdev, 1),
        "high_variance": stdev > 50,  # heuristique
    }


def full_proxy_check(ip: str, port: int = 8080):
    print(f"\n{'='*55}")
    print(f"  Analyse proxy : {ip}:{port}")
    print(f"{'='*55}")
    
    # 1. Test connexion directe
    print("\n[1] Test connectivité TCP...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    reachable = sock.connect_ex((ip, port)) == 0
    sock.close()
    print(f"  Port {port} ouvert : {'✓' if reachable else '✗'}")
    
    if not reachable:
        print("  ✗ Port fermé ou filtré")
        return
    
    # 2. Test HTTP via le proxy
    print("\n[2] Test requête via proxy HTTP...")
    try:
        proxies = {"http": f"http://{ip}:{port}", "https": f"http://{ip}:{port}"}
        r = requests.get("http://ip-api.com/json", proxies=proxies, timeout=10)
        data = r.json()
        print(f"  ✓ Proxy fonctionnel")
        print(f"  IP vue par l'extérieur : {data.get('query')}")
        print(f"  Pays                  : {data.get('country')}")
        print(f"  FAI                   : {data.get('isp')}")
        proxy_works_http = True
    except Exception as e:
        print(f"  ✗ Proxy HTTP inopérant : {e}")
        proxy_works_http = False
    
    # 3. Détection niveau d'anonymat
    print("\n[3] Niveau d'anonymat...")
    try:
        r = requests.get("http://httpbin.org/headers", proxies=proxies, timeout=10)
        headers = r.json().get("headers", {})
        findings = analyze_headers(headers)
        
        if not findings:
            print("  ✓ Elite/High-Anonymous — aucune en-tête révélatrice")
        elif any('X-Forwarded-For' in f for f in findings):
            print("  ⚠️  Transparent — révèle votre vraie IP !")
        else:
            print("  ⚠️  Anonymous — révèle la présence d'un proxy")
        
        for f in findings:
            print(f"    → {f}")
    except Exception as e:
        print(f"  Erreur : {e}")
    
    # 4. Ports proxy ouverts sur la machine
    print("\n[4] Autres ports proxy ouverts...")
    open_ports = check_open_ports(ip)
    if open_ports:
        print(f"  Ports ouverts : {open_ports}")
    else:
        print("  Aucun port proxy courant détecté")
    
    print()


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        parts = sys.argv[1].split(':')
        full_proxy_check(parts[0], int(parts[1]) if len(parts) > 1 else 8080)
    else:
        print("Usage : python3 detect_proxy.py IP:PORT")
        print("Exemple : python3 detect_proxy.py 127.0.0.1:3128")
```

---

## 9. Niveau Expert — Proxy transparent & interception TLS

### 9.1 Proxy transparent (sans configuration client)

Un proxy **transparent** intercepte le trafic réseau sans que le client ne soit configuré pour l'utiliser. Cela requiert une manipulation au niveau réseau (iptables/nftables).

```bash
# Principe : rediriger le trafic HTTP/HTTPS vers notre proxy
# via des règles iptables REDIRECT

# Activer le forwarding IP
echo 1 > /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.ip_forward=1

# Rediriger HTTP (port 80) vers notre proxy (port 3129)
sudo iptables -t nat -A PREROUTING \
  -i eth0 \
  -p tcp --dport 80 \
  ! -d 127.0.0.0/8 \
  -j REDIRECT --to-port 3129

# Rediriger HTTPS (port 443) vers notre proxy TLS (port 3130)
sudo iptables -t nat -A PREROUTING \
  -i eth0 \
  -p tcp --dport 443 \
  ! -d 127.0.0.0/8 \
  -j REDIRECT --to-port 3130

# Voir les règles NAT
sudo iptables -t nat -L -n -v

# Avec nftables (2026 — remplace iptables)
sudo nft add table nat
sudo nft add chain nat prerouting '{ type nat hook prerouting priority -100; }'
sudo nft add rule nat prerouting tcp dport 80 redirect to :3129
sudo nft add rule nat prerouting tcp dport 443 redirect to :3130

# Voir les règles nftables
sudo nft list ruleset
```

### 9.2 mitmproxy — Interception TLS (Man-in-the-Middle pédagogique)

```bash
# Installation
pip install mitmproxy

# Modes de fonctionnement :
# mitmproxy  → interface TUI interactive
# mitmweb    → interface web
# mitmdump   → ligne de commande (comme tcpdump)

# 1. Mode proxy explicite (port 8080)
mitmproxy -p 8080

# 2. Mode proxy transparent
mitmproxy --mode transparent -p 8080

# 3. Mode reverse proxy
mitmproxy --mode reverse:http://backend:8000 -p 8080

# Tester l'interception
# D'abord installer le certificat mitmproxy (CA) :
# ~/.mitmproxy/mitmproxy-ca-cert.pem

curl -x http://localhost:8080 \
     --cacert ~/.mitmproxy/mitmproxy-ca-cert.pem \
     https://example.com

# Ou ignorer la vérification TLS (tests seulement!)
curl -x http://localhost:8080 -k https://example.com

# Script mitmproxy pour logger/modifier les requêtes
cat > intercept.py << 'EOF'
"""
Script mitmproxy : logge toutes les requêtes et injecte un en-tête
Usage : mitmproxy -s intercept.py
"""
from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
    """Intercepte chaque requête avant qu'elle parte."""
    print(f"→ {flow.request.method} {flow.request.pretty_url}")
    
    # Ajouter un en-tête personnalisé
    flow.request.headers["X-Intercepted-By"] = "mitmproxy-demo"
    
    # Bloquer certains domaines
    if "ads.example.com" in flow.request.host:
        flow.response = http.Response.make(403, b"Blocked by proxy")

def response(flow: http.HTTPFlow) -> None:
    """Intercepte chaque réponse avant qu'elle arrive au client."""
    print(f"← {flow.response.status_code} {flow.request.pretty_url}")
    
    # Modifier le corps de la réponse
    if flow.response.headers.get("content-type", "").startswith("text/html"):
        content = flow.response.content
        modified = content.replace(b"</body>", b"<!-- intercepté par mitmproxy --></body>")
        flow.response.content = modified
EOF

mitmproxy -s intercept.py -p 8080
```

### 9.3 Comment fonctionne l'interception TLS

```
Sans interception (TLS normal) :
─────────────────────────────────
[Client] ──── TLS (cert example.com) ────► [Serveur example.com]
         Client vérifie le cert avec les CA système

Avec mitmproxy (MitM) :
─────────────────────────────────────────────────────
[Client] ──TLS (cert *.example.com signé par mitmproxy CA)──► [mitmproxy]
                                                                     │
                                                     TLS réel vers serveur
                                                                     │
                                                          [Serveur example.com]

⚠️  Le client doit faire confiance au CA de mitmproxy
    → C'est pourquoi il faut installer le certificat mitmproxy
    → Sans ce certificat : ERREUR SSL "untrusted certificate"
    → Les navigateurs modernes + HSTS + certificate pinning résistent à ça
```

```bash
# Générer un CA personnalisé (pour labo)
openssl genrsa -out myca.key 4096
openssl req -new -x509 -days 3650 -key myca.key \
  -out myca.crt \
  -subj "/CN=Mon CA Proxy/O=Lab/C=FR"

# Installer ce CA sur les clients (Ubuntu)
sudo cp myca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Générer un certificat serveur signé par notre CA
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "/CN=example.com/O=Lab/C=FR"
openssl x509 -req -days 365 -in server.csr \
  -CA myca.crt -CAkey myca.key -CAcreateserial \
  -out server.crt

# Vérifier la chaîne de confiance
openssl verify -CAfile myca.crt server.crt
```

---

## 10. Exercices pratiques

### TP 1 — Débutant : Identifier le type de proxy

```bash
# Objectif : comprendre ce qu'un proxy révèle sur vous

# 1. Notez votre IP sans proxy
echo "IP sans proxy :"
curl -s https://ipinfo.io/ip

# 2. Testez un proxy gratuit (ATTENTION : proxies publics = risque de sécurité !)
# Pour ce TP, utilisez uniquement des proxies que vous contrôlez
# Exemples avec un proxy local Squid :
curl -x http://localhost:3128 -s https://ipinfo.io/ip

# 3. Vérifiez les en-têtes transmises
curl -x http://localhost:3128 -s http://httpbin.org/headers | python3 -m json.tool

# Questions :
# - Y a-t-il un X-Forwarded-For ?
# - L'IP vue est-elle celle du proxy ou la vôtre ?
# - Quel est le niveau d'anonymat du proxy ?
```

### TP 2 — Intermédiaire : Proxy HTTP from scratch

```bash
# Objectif : lancer et utiliser notre proxy Python maison

# 1. Lancer le proxy
python3 http_proxy.py 9999 &

# 2. Tester HTTP
curl -x http://localhost:9999 http://example.com -v 2>&1 | head -30

# 3. Tester HTTPS (tunnel CONNECT)
curl -x http://localhost:9999 https://example.com -v 2>&1 | grep "CONNECT\|200\|SSL"

# 4. Observer les logs du proxy
# (le proxy affiche chaque requête dans le terminal)

# 5. Modifier le proxy pour :
#    - Logger dans un fichier
#    - Bloquer certains domaines (ex: ads.example.com)
#    - Ajouter/supprimer des en-têtes

# Questions :
# - Combien de connexions TCP pour une page avec ressources ?
# - Que se passe-t-il avec HTTP/2 ?
# - Pourquoi le proxy ne peut-il pas lire le trafic HTTPS ?
```

### TP 3 — Avancé : Chaînage et détection

```bash
# Objectif : mettre en place une chaîne de proxies et la détecter

# Terminal 1 : Lancer proxy SOCKS5 (port 1080)
python3 socks5_server.py 1080

# Terminal 2 : Lancer proxy HTTP (port 8080)
python3 http_proxy.py 8080

# Terminal 3 : Configurer ProxyChains
cat > /tmp/proxychains_test.conf <<'EOF'
strict_chain
proxy_dns
[ProxyList]
socks5 127.0.0.1 1080
http   127.0.0.1 8080
EOF

proxychains4 -f /tmp/proxychains_test.conf curl https://ipinfo.io/ip

# Lancer le serveur d'analyse d'en-têtes
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        for k,v in self.headers.items():
            self.wfile.write(f'{k}: {v}\n'.encode())
    def log_message(self,*a): pass
HTTPServer(('0.0.0.0',7777),H).serve_forever()
" &

# Tester à travers la chaîne
proxychains4 -f /tmp/proxychains_test.conf curl http://localhost:7777

# Questions :
# - Quelles en-têtes révèlent la présence d'un proxy ?
# - Y a-t-il des fuites d'informations ?
# - Comment rendre la chaîne "elite" (aucune fuite) ?
```

### TP 4 — Expert : mitmproxy en action

```bash
# Objectif : Intercepter et modifier du trafic HTTPS

# 1. Lancer mitmproxy
mitmproxy -p 8080

# 2. Dans un autre terminal, configurer curl pour utiliser mitmproxy
# et faire confiance au CA de mitmproxy
curl -x http://localhost:8080 \
     --cacert ~/.mitmproxy/mitmproxy-ca-cert.pem \
     https://httpbin.org/get

# Observer dans mitmproxy :
# - Toutes les requêtes apparaissent
# - Appuyez sur Entrée pour voir les détails
# - Appuyez sur e pour modifier (edit) une requête/réponse

# 3. Script d'interception automatique
cat > /tmp/modifier.py << 'EOF'
from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    # Remplacer le contenu de la réponse JSON
    if "httpbin.org" in flow.request.host:
        import json
        try:
            data = json.loads(flow.response.content)
            data["intercepted"] = True
            data["modified_by"] = "mitmproxy_tp"
            flow.response.content = json.dumps(data).encode()
            print(f"[+] Réponse modifiée : {flow.request.url}")
        except:
            pass
EOF

mitmproxy -s /tmp/modifier.py -p 8080

# Dans un autre terminal :
curl -x http://localhost:8080 \
     --cacert ~/.mitmproxy/mitmproxy-ca-cert.pem \
     https://httpbin.org/get | python3 -m json.tool

# Le champ "intercepted": true doit apparaître dans la réponse
```

---

## 11. Outils de référence 2026

### CLI essentiels

| Outil | Rôle | Installation |
|-------|------|-------------|
| `curl` | Client HTTP avec support proxy | Préinstallé |
| `wget` | Téléchargement avec proxy | `apt install wget` |
| `proxychains4` | Chaînage de proxies | `apt install proxychains4` |
| `mitmproxy` | Interception TLS | `pip install mitmproxy` |
| `squid` | Proxy HTTP/HTTPS complet | `apt install squid` |
| `nginx` | Reverse proxy / LB | `apt install nginx` |
| `haproxy` | Load balancer expert | `apt install haproxy` |
| `tinyproxy` | Proxy HTTP ultra-léger | `apt install tinyproxy` |
| `3proxy` | Proxy multi-protocole | Compilation |
| `dante` | Serveur SOCKS5 | `apt install dante-server` |

### Serveurs SOCKS5 prêts à l'emploi

```bash
# Dante SOCKS5 server
sudo apt install dante-server -y

sudo tee /etc/danted.conf <<'EOF'
logoutput: /var/log/danted.log

internal: 0.0.0.0 port = 1080
external: eth0

socksmethod: username none
clientmethod: none

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: connect disconnect
}

socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    command: connect
    log: connect disconnect
    socksmethod: none
}
EOF

sudo systemctl restart danted
curl --socks5-hostname localhost:1080 https://ipinfo.io/ip
```

### Récapitulatif des commandes proxy

```bash
# ── CURL ──────────────────────────────────────────────
curl -x http://proxy:port URL             # Proxy HTTP
curl -x http://user:pass@proxy:port URL   # Proxy HTTP + auth
curl --socks5 proxy:port URL              # SOCKS5
curl --socks5-hostname proxy:port URL     # SOCKS5 + DNS délégué
curl --socks4 proxy:port URL              # SOCKS4
curl --noproxy "host1,host2" URL          # Exclure des hôtes

# ── VARIABLES D'ENVIRONNEMENT ─────────────────────────
export http_proxy=http://proxy:port
export https_proxy=http://proxy:port
export all_proxy=socks5h://proxy:port
export no_proxy=localhost,127.0.0.1

# ── PROXYCHAINS ───────────────────────────────────────
proxychains4 COMMANDE                     # Via la chaîne configurée
proxychains4 -f /chemin/proxychains.conf COMMANDE

# ── SSH TUNNELS ───────────────────────────────────────
ssh -D 1080 user@serveur -N               # SOCKS5 dynamique
ssh -L local:cible:port user@bastion -N   # Port forwarding local
ssh -R distant:local:port user@serveur -N # Port forwarding inverse

# ── TEST ET VÉRIFICATION ──────────────────────────────
curl -s https://ipinfo.io/ip              # Voir son IP publique
curl -s http://httpbin.org/headers        # Voir les en-têtes envoyées
curl -s http://ip-api.com/json            # Géo + infos complètes
```

---

*Document créé à des fins pédagogiques — 2026*  
*Toujours expérimenter dans un environnement isolé que vous contrôlez.*  
*Ne jamais utiliser ces techniques sur des réseaux ou systèmes sans autorisation explicite.*
