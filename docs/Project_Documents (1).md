# Project Technical Documentation (Full)

This document contains both descriptive documentation and a Q&A knowledge base to support AI-powered search, RAG systems, and human reference.

**Important: Scope of this Documentation**
This documentation is specifically designed for internal IT support and system administration. It covers:
- Network infrastructure and VPN connectivity
- System architecture and routing configurations
- Server access and security policies
- Software policies and coding conventions
- Bug logging and daily reporting procedures
- Domain and service information

**Out of Scope:**
This documentation does NOT cover general programming tutorials, external frameworks, or topics unrelated to the internal IT infrastructure (e.g., general web development, Python tutorials, external APIs, etc.). The IT Help Desk agent should politely decline questions outside the scope of internal IT support.

---

## ===========================
## 1. NETWORK INFORMATION
## ===========================

### Description
| Environment | IP Range | Notes |
|-------------|----------|-------|
| Production  | 10.21.32.0/24 | Internal access only |
| Staging     | 10.21.33.0/24 | QA devices only |
| Development | 10.21.34.0/24 | Open to Dev VPN users |

**Public Services**
- API Gateway: 34.118.92.14  
- Web Portal: 34.118.92.20  
- Monitoring System: 34.118.92.31

---

### Q&A Section

**Q1. What are the IP ranges for the project?**  
A1:
- Production: 10.21.32.0/24  
- Staging: 10.21.33.0/24  
- Development: 10.21.34.0/24  

**Q2. What are the public IPs of the services?**  
A2:
- API Gateway: 34.118.92.14  
- Web Portal: 34.118.92.20  
- Monitoring System: 34.118.92.31  

**Q3. Who can access Production?**  
A3: Only authorized internal staff using VPN credentials.

---

## ===========================
## 2. DOMAIN INFORMATION
## ===========================

### Description
| Service | Domain |
|---------|--------|
| Main Application | https://portal.company-project.com |
| API Endpoint | https://api.company-project.com |
| Admin Site | https://admin.company-project.com |

---

### Q&A Section

**Q1. What is the main application domain?**  
A1: https://portal.company-project.com

**Q2. What is the API domain?**  
A2: https://api.company-project.com

**Q3. Are all domains HTTPS?**  
A3: Yes, HTTPS is mandatory.

---

## ===========================
## 3. SOFTWARE POLICY
## ===========================

### Description

**Whitelisted software**
- Chrome (latest version)  
- VS Code  
- Node.js LTS  
- Git / GitHub Desktop  
- Docker & Kubernetes CLI  
- Slack / Teams  
- Postman  

**Blacklisted software**
- Torrent / P2P tools  
- Cracked or unlicensed applications  
- Unauthorized remote desktop tools  

---

### Q&A Section

**Q1. Which software are approved for development?**  
A1: Chrome, VS Code, Node LTS, Git, GitHub Desktop, Docker, Postman, Slack/Teams.

**Q2. Which software is banned?**  
A2: Torrent apps, cracked apps, non-approved remote desktop tools.

**Q3. Why are remote desktop tools restricted?**  
A3: For security, auditing, and data protection.

---

## ===========================
## 4. CODING CONVENTIONS
## ===========================

### Description
- CamelCase for variables/functions  
- PascalCase for classes  
- ESLint + Prettier required  
- Code reviews required  
- Do not commit `.env` files  
- Branch naming:
  - `feature/<task-id>-<short-desc>`
  - `bugfix/<task-id>-<short-desc>`

---

### Q&A Section

**Q1. What naming conventions are required?**  
A1: CamelCase for variables/functions, PascalCase for classes.

**Q2. Are code reviews mandatory?**  
A2: Yes, all merges require review.

**Q3. Can `.env` files be committed?**  
A3: No, they are forbidden.

---

## ===========================
## 5. DAILY REPORT RULES
## ===========================

### Description
- Send before 8:00 PM GMT+7  
- Must include:
  - DONE  
  - DOING  
  - BLOCK  
  - PLAN  

---

### Q&A Section

**Q1. What time must reports be submitted?**  
A1: Before 8:00 PM GMT+7.

**Q2. What format should be used?**  
A2: DONE, DOING, BLOCK, PLAN.

---

## ===========================
## 6. BUG LOGGING & FIXING
## ===========================

### Description

**Logging**
- Logged in Jira  
- Steps to reproduce required  
- Expected vs actual result  
- Screenshot/video mandatory  

**Severity Levels**
- S1: System down  
- S2: Major function broken  
- S3: Minor/UI  
- S4: Suggestion  

**Fixing**
- Assigned owner required  
- Fix via Pull Request  
- QA must verify  
- If repeated 3 times → Critical Regression  

---

### Q&A Section

**Q1. Where are bugs logged?**  
A1: In Jira, under correct sprint/component.

**Q2. What info is mandatory?**  
A2: Steps to reproduce, expected result, actual result, environment, screenshot/video.

**Q3. Who closes a bug?**  
A3: Only QA after verification.

---

## ===========================
## 7. SERVER ACCESS
## ===========================

### Description
| Environment | Access | Address | Notes |
|-------------|--------|---------|-------|
| Production  | VPN → SSH | 192.168.80.21 | No direct DB queries |
| Staging     | VPN → SSH | 192.168.80.41 | Read-only DB access allowed |
| Monitoring  | HTTPS   | https://monitor.company-client.com | Admin account in Vault |

All credentials stored in Vault. Violations lead to account suspension.

---

### Q&A Section

**Q1. How to access the Production server?**  
A1: VPN → SSH to 192.168.80.21. Direct DB queries are blocked.

**Q2. Where are credentials stored?**  
A2: In the Vault system (not in plain text).

**Q3. What happens if access rules are broken?**  
A3: Account suspension and security audit.

---

## ===========================
## 8. VPN TROUBLESHOOTING GUIDE
## ===========================

### Description

**VPN Setup and Troubleshooting Guide**

When users encounter VPN connection issues, follow these steps:

**Step 1: Check Internet Connection**
- Verify the device has a stable Internet connection
- Try accessing public websites (google.com, baidu.com)
- Check network speed: minimum 5 Mbps download, 2 Mbps upload

**Step 2: Check VPN Software**
- Confirm VPN software is installed with the correct version
- Required versions: Cisco AnyConnect 4.10+ or FortiClient 7.0+
- Check VPN service status on the system

**Step 3: Restart VPN Software**
- Completely close the VPN application (not just minimize)
- Wait 10 seconds
- Reopen the VPN application
- Log in again with credentials from Vault

**Step 4: Check VPN Configuration**
- Server address: vpn.company-project.com
- Port: 443 (HTTPS)
- Protocol: SSL/TLS
- Group: Internal-Users (or Development-Team for developers)

**Step 5: Clear Cache and Old Configuration**
- Windows: Delete folder `%ProgramData%\Cisco\Cisco AnyConnect Secure Mobility Client`
- Mac: Delete folder `~/Library/Application Support/Cisco/Cisco AnyConnect`
- Linux: Delete file `~/.anyconnect`

**Step 6: Restart Network Services**
- Windows: Run `ipconfig /flushdns` and `netsh winsock reset` (requires admin)
- Mac: Run `sudo killall -HUP mDNSResponder`
- Linux: Run `sudo systemctl restart NetworkManager`

**Step 7: Check Firewall and Antivirus**
- Temporarily disable Windows Firewall/Defender
- Temporarily disable Antivirus software
- Try connecting to VPN again
- If successful, add exception for VPN client

**Step 8: Check SSL Certificate**
- Ensure system date/time is accurate (more than 5 minutes off will cause SSL errors)
- Verify VPN server certificate is still valid
- Update root certificates if necessary

**Step 9: Contact IT Support**
- If the above steps do not resolve the issue, create a ticket in Jira
- Provide the following information:
  - Error code (if available)
  - Error screenshot
  - Log file from VPN client
  - Time when the issue occurred

**Support Information:**
- IT Helpdesk: support@company-project.com
- Hotline: +84-xxx-xxx-xxxx (business hours)
- Ticket System: https://jira.company-project.com

---

### Q&A Section

**Q1. How to fix VPN connection errors?**  
A1: Follow these steps: 1. Check Internet connection, 2. Restart VPN software, 3. Check VPN configuration (server: vpn.company-project.com, port: 443), 4. Clear VPN cache, 5. Restart network services, 6. Check Firewall/Antivirus, 7. Check SSL certificate, 8. Contact IT Support if still not working.

**Q2. What are the VPN connection details?**  
A2: Server address: vpn.company-project.com, Port: 443 (HTTPS), Protocol: SSL/TLS, Group: Internal-Users or Development-Team.

**Q3. What should I do if I still cannot connect after trying these steps?**  
A3: Create a ticket in Jira with error code, screenshot, log file, and time when the issue occurred. Contact IT Helpdesk: support@company-project.com.

**Q4. Which VPN client versions are supported?**  
A4: Cisco AnyConnect 4.10+ or FortiClient 7.0+.

**Q5. Why does VPN require accurate system date and time?**  
A5: VPN uses SSL/TLS certificates. If system date/time is off by more than 5 minutes, it will cause certificate authentication errors.

---

## ===========================
## 9. SYSTEM ARCHITECTURE & ROUTING
## ===========================

### Description

**System Architecture and Routing Structure**

The system uses a microservices architecture with API Gateway as the single entry point. Services are deployed on a Kubernetes cluster.

**Architecture Overview:**
- **API Gateway**: Entry point for all requests from clients
- **Service Registry**: Manages service discovery (Consul)
- **Load Balancer**: Distributes traffic across service instances
- **Database Cluster**: PostgreSQL with replication and failover

**Service X - Routing Structure:**

Service X is a microservice that handles core business logic. Routing is configured through Kubernetes Ingress and internal service mesh.

**Ingress Configuration (YAML):**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: service-x-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rewrite-target: /$1
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - api.company-project.com
      secretName: service-x-tls
  rules:
    - host: api.company-project.com
      http:
        paths:
          - path: /api/v1/service-x(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: service-x
                port:
                  number: 8080
          - path: /api/v1/service-x/health
            pathType: Exact
            backend:
              service:
                name: service-x-health
                port:
                  number: 9090
```

**Service Configuration (YAML):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: service-x
  namespace: production
  labels:
    app: service-x
    version: v1
spec:
  type: ClusterIP
  selector:
    app: service-x
    tier: backend
  ports:
    - name: http
      port: 8080
      targetPort: 8080
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: 9090
      protocol: TCP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

**Deployment Configuration (YAML):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-x
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: service-x
      tier: backend
  template:
    metadata:
      labels:
        app: service-x
        tier: backend
    spec:
      containers:
        - name: service-x
          image: registry.company-project.com/service-x:v1.2.3
          ports:
            - containerPort: 8080
              name: http
            - containerPort: 9090
              name: metrics
          env:
            - name: DB_HOST
              valueFrom:
                secretKeyRef:
                  name: service-x-secrets
                  key: db-host
            - name: DB_PORT
              value: "5432"
            - name: LOG_LEVEL
              value: "info"
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 9090
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 9090
            initialDelaySeconds: 5
            periodSeconds: 5
```

**Internal Routing Rules:**

Service X uses internal routing based on path and method:
- `GET /api/v1/service-x/users` → User Management Service
- `POST /api/v1/service-x/orders` → Order Processing Service
- `GET /api/v1/service-x/reports` → Reporting Service
- `PUT /api/v1/service-x/config` → Configuration Service

**Load Balancing Strategy:**
- Round-robin for regular requests
- Session affinity (sticky session) for stateful requests
- Health check every 5 seconds to remove unhealthy instances

**Network Policy (YAML):**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: service-x-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: service-x
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: production
        - podSelector:
            matchLabels:
              app: api-gateway
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
```

---

### Q&A Section

**Q1. What is the routing structure of Service X?**  
A1: Service X uses Kubernetes Ingress with path `/api/v1/service-x(/|$)(.*)` routing to the service on port 8080. Health check endpoint is at `/api/v1/service-x/health` on port 9090. Internal routing is based on path: `/users`, `/orders`, `/reports`, `/config`.

**Q2. How does Service X use YAML configuration?**  
A2: Service X is configured through 4 types of YAML: Ingress (routing from Internet), Service (internal service discovery), Deployment (container orchestration), and NetworkPolicy (security rules). All are deployed in the `production` namespace.

**Q3. How does Service X handle load balancing?**  
A3: Service X uses round-robin for regular requests and session affinity (sticky session) for stateful requests. Health check every 5 seconds to remove unhealthy instances. Deployment has 3 replicas with rolling update strategy.

**Q4. Which ports are used for Service X?**  
A4: Port 8080 for HTTP traffic, port 9090 for metrics and health check.

**Q5. What connections does Service X network policy allow?**  
A5: Ingress only allows from the `production` namespace and from `api-gateway` pod. Egress only allows connections to PostgreSQL (port 5432) and Redis (port 6379).

**Q6. How many replicas does Service X have?**  
A6: Service X has 3 replicas with rolling update strategy (maxSurge: 1, maxUnavailable: 0).

---

_Last Update: 2025-01-01_  
_Author: Project Technical Manager_
