# AvatarClub 운영 배포 가이드 (AWS Lightsail + Cloudflare)

이 문서는 AvatarClub 을 Lightsail 인스턴스 1대에 Docker 로 올리고, Cloudflare 를 앞에 두는
배포 절차다. 처음부터 끝까지 순서대로 따라가면 된다.

## 구성

```
   사용자
     │  HTTPS
     ▼
 Cloudflare (프록시 ON, Full strict)
     │  HTTPS (Origin CA 인증서)
     ▼
 Lightsail :443
     │
 frontend 컨테이너 (nginx)
     ├─ /            → Vue SPA 정적 파일
     └─ /api/*       → backend 컨테이너 :8000 (FastAPI)
                          ├─ Neon PostgreSQL  (외부)
                          ├─ AWS S3           (외부)
                          ├─ fal.ai           (외부)
                          └─ 토스페이먼츠     (외부)
```

프론트와 API 가 **같은 오리진**이다. `avatarclub.example.com/api/*` 가 백엔드로 프록시되므로
CORS 설정도, api 서브도메인도 필요 없다. 백엔드 8000 포트는 호스트에 노출하지 않는다.

> 이 문서의 `avatarclub.example.com` 은 전부 실제 도메인으로 바꿔 읽을 것.

---

## 0. 미리 준비할 것

| 항목 | 비고 |
|---|---|
| Cloudflare 에 등록된 도메인 | 네임서버가 Cloudflare 를 가리키고 있어야 함 (Active 상태) |
| Neon PostgreSQL 연결 문자열 | `sslmode=require` 포함 |
| S3 버킷 + IAM 액세스 키 | 버킷은 퍼블릭일 필요 없음 (presigned URL 사용) |
| fal.ai API 키 | 없으면 이미지 생성이 전부 실패 |
| 토스페이먼츠 키 | 사업자등록 전이면 테스트 키(`test_ck_*`, `test_sk_*`)로 오픈 가능 |
| 구글 OAuth 클라이언트 ID | 선택. 없으면 구글 로그인 버튼이 숨겨짐 |
| Gmail 앱 비밀번호 | 선택. 없으면 문의 알림 메일만 안 나감 (문의 저장은 정상) |

---

## 1. Lightsail 인스턴스 생성

1. Lightsail 콘솔 → **Create instance**
2. **리전**: `ap-northeast-2` (서울). 주 사용자가 한국이면 지연시간 차이가 크다.
3. **플랫폼**: Linux/Unix → **OS Only** → **Ubuntu 24.04 LTS**
4. **플랜**: **2GB RAM / 2 vCPU ($12/월)** 이상 권장.
   - 1GB($7) 도 서비스 구동 자체는 되지만, 인스턴스에서 프론트를 빌드할 때
     `npm ci` + Vite 빌드가 메모리를 크게 먹어 OOM 으로 죽는 경우가 많다.
   - 1GB 로 가려면 아래 6번의 스왑을 반드시 잡을 것.
5. 생성 후 **Networking → Static IP** 에서 고정 IP 를 할당해 인스턴스에 붙인다.
   - 이걸 안 하면 인스턴스를 재시작할 때 공인 IP 가 바뀌어 DNS 가 깨진다.

## 2. 방화벽

### 2-1. Lightsail 콘솔 방화벽

인스턴스 → **Networking** → IPv4 Firewall:

| 애플리케이션 | 프로토콜 | 포트 | 제한 |
|---|---|---|---|
| SSH | TCP | 22 | 가능하면 본인 IP 로 제한 |
| HTTP | TCP | 80 | 전체 허용 (아래에서 다시 좁힌다) |
| HTTPS | TCP | 443 | 전체 허용 (아래에서 다시 좁힌다) |

**8000 은 열지 않는다.** 백엔드는 컨테이너 네트워크 안에서만 접근된다.

### 2-2. Cloudflare 우회 차단 (중요)

Cloudflare 를 우회해 origin IP 로 직접 붙는 경로가 열려 있으면,
Cloudflare 의 DDoS 방어·WAF 가 모두 무의미해지고 `CF-Connecting-IP` 를 위조한
레이트리밋 우회도 가능해진다. 80/443 을 Cloudflare 대역에서만 받도록 막는다.

주의: **ufw 로는 막히지 않는다.** Docker 가 게시한 포트는 iptables `nat` 테이블에
직접 규칙을 넣어 ufw 의 INPUT 체인을 건너뛴다. Docker 가 존중하는 `DOCKER-USER`
체인에 규칙을 넣어야 한다.

```bash
sudo apt-get update && sudo apt-get install -y iptables-persistent

# Cloudflare 대역만 80/443 허용, 나머지는 차단
for ip in $(curl -s https://www.cloudflare.com/ips-v4); do
  sudo iptables -I DOCKER-USER -s "$ip" -p tcp -m multiport --dports 80,443 -j ACCEPT
done
# 위 ACCEPT 들보다 뒤에 놓이도록 -A 로 추가
sudo iptables -A DOCKER-USER -p tcp -m multiport --dports 80,443 -j DROP

sudo netfilter-persistent save
```

확인: 다른 곳에서 `curl -sv --max-time 5 http://<고정IP>/` 가 타임아웃되면 성공이다.

> Cloudflare 대역은 드물게 바뀐다. 위 루프를 월 1회 정도 다시 돌리거나,
> `frontend/cloudflare-realip.conf` 갱신과 같이 처리할 것.

## 3. Docker 설치

SSH 접속 후:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
newgrp docker   # 또는 재로그인
docker compose version
```

## 4. Cloudflare 설정

### 4-1. DNS

**DNS → Records** 에서:

| Type | Name | Content | Proxy |
|---|---|---|---|
| A | `@` | Lightsail 고정 IP | **Proxied (주황 구름)** |
| A | `www` | Lightsail 고정 IP | **Proxied** |

프록시가 꺼져 있으면(회색 구름) origin IP 가 그대로 노출되고, 2-2 의 방화벽 때문에
사이트가 아예 안 열린다. 반드시 켤 것.

### 4-2. SSL/TLS 모드

**SSL/TLS → Overview → Full (strict)** 로 설정한다.

- `Flexible` 은 절대 쓰지 말 것. 엣지~origin 구간이 평문이라 JWT 가 그대로 흐르고,
  nginx 의 301 리다이렉트와 겹쳐 무한 리다이렉트가 난다.
- `Full` 은 origin 인증서를 검증하지 않아 중간자 공격을 막지 못한다.

### 4-3. Origin 인증서 발급

**SSL/TLS → Origin Server → Create Certificate**

- Private key type: RSA (2048)
- Hostnames: `avatarclub.example.com`, `*.avatarclub.example.com`
- 유효기간: 15년

화면에 뜨는 두 블록을 인스턴스에 저장한다. **Private Key 는 이 화면을 닫으면 다시 볼 수 없다.**

```bash
mkdir -p ~/avatarclub/certs
nano ~/avatarclub/certs/origin.pem   # Origin Certificate 붙여넣기
nano ~/avatarclub/certs/origin.key   # Private Key 붙여넣기
chmod 600 ~/avatarclub/certs/origin.key
```

인증서는 리포 옆의 `./certs/` 에 두면 된다 — compose 바인드 마운트의 관례적인 위치다.
이 리포는 공개돼 있으므로 `certs/`, `*.pem`, `*.key` 는 `.gitignore` 로 막아뒀다.
그래도 개인키를 git 작업 트리 밖에 두고 싶으면 `.env` 에 절대경로를 지정하면 된다:

```
CERTS_DIR=/etc/avatarclub/certs
```

## 5. 코드 배포

```bash
cd ~
git clone https://github.com/minq11/avatarbank.git avatarclub-src
cd avatarclub-src
# 위에서 만든 인증서를 프로젝트 루트로 옮긴다 (compose 가 ./certs 를 마운트한다)
mv ~/avatarclub/certs ./certs

cp .env.example .env
nano .env
```

`.env` 에서 최소한 아래는 반드시 채운다:

- `DATABASE_URL` — Neon 연결 문자열
- `JWT_SECRET_KEY` — `openssl rand -hex 32` 결과
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `S3_BUCKET` / `AWS_REGION`
- `FAL_API_KEY`
- `TOSS_CLIENT_KEY` / `TOSS_SECRET_KEY`
- `PAYMENT_SUCCESS_URL` / `PAYMENT_FAIL_URL` — **운영 도메인으로**
- `ADMIN_EMAIL_WHITELIST`

## 6. (1GB 인스턴스만) 스왑

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 7. 기동

```bash
cd ~/avatarclub-src
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

두 컨테이너가 `healthy` 로 올라오면 된다.

확인:

```bash
# origin 에서 직접 (Origin 인증서는 공인 체인이 아니라 -k 필요)
curl -k https://localhost/            # SPA HTML
curl -k https://localhost/api/health  # {"status":"ok"}
```

브라우저에서 `https://avatarclub.example.com` 접속.

## 8. 외부 서비스에 운영 도메인 등록

배포가 떴다고 끝이 아니다. 아래를 등록하지 않으면 해당 기능만 조용히 실패한다.

### 8-1. 구글 로그인

GCP 콘솔 → API 및 서비스 → 사용자 인증 정보 → OAuth 클라이언트 ID:

- **승인된 자바스크립트 원본**에 `https://avatarclub.example.com` 추가

누락되면 버튼은 뜨는데 클릭 시 실패한다. 개발용 `http://localhost:5173` 은 남겨둬도 된다.

### 8-2. 토스페이먼츠

`.env` 의 `PAYMENT_SUCCESS_URL` / `PAYMENT_FAIL_URL` 이 운영 도메인인지 다시 확인.
localhost 로 남아 있으면 결제는 승인되는데 사용자가 돌아올 곳이 없어진다.

### 8-3. S3 CORS

브라우저가 presigned URL 로 이미지를 직접 받는다. 버킷 → 권한 → CORS 에:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT"],
    "AllowedOrigins": ["https://avatarclub.example.com"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

## 9. 배포 / 업데이트

```bash
cd ~/Avatarbank
make deploy
```

`make deploy` 가 하는 일: `git pull` → 이미지 재빌드 → 기동 → 20초 대기 →
컨테이너 상태와 헬스체크 출력. 매번 확인까지 한 번에 끝난다.

`make` 가 없으면 `sudo apt-get install -y make` 한 번만 하면 된다.

자주 쓰는 나머지:

```bash
make status      # 컨테이너 상태 + 헬스체크
make prod-logs   # 로그 따라보기
make prod-down   # 정지
make help        # 전체 타깃 목록
```

더 짧게 치고 싶으면 셸 별칭을 걸어둔다:

```bash
echo "alias deploy='cd ~/Avatarbank && make deploy'" >> ~/.bashrc
source ~/.bashrc
# 이제 어느 디렉터리에서든 deploy 한 단어로 배포된다
```

수동으로 할 때는:

```bash
cd ~/Avatarbank
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

프론트의 `VITE_API_BASE_URL` 과 사업자 정보(`src/config/business.ts`)는
**빌드 시점에 번들에 구워진다.** `--build` 없이는 `git pull` 을 해도 화면이
그대로다. `make deploy` 는 항상 `--build` 를 붙인다.

롤백:

```bash
git log --oneline -10
git checkout <이전_커밋>
docker compose -f docker-compose.prod.yml up -d --build
```

## 10. 오픈 전 체크리스트

- [ ] `.env` 의 `JWT_SECRET_KEY` 가 `CHANGE_ME` 가 아니다 (아니면 백엔드가 기동을 거부한다)
- [ ] `PAYMENT_SUCCESS_URL` / `PAYMENT_FAIL_URL` 이 운영 도메인이다
- [ ] Cloudflare SSL 모드가 **Full (strict)** 이다
- [ ] DNS 레코드가 **Proxied** 다
- [ ] origin IP 직접 접속이 차단된다 (2-2)
- [ ] 구글 OAuth 승인된 원본에 운영 도메인이 있다
- [ ] S3 CORS 에 운영 도메인이 있다
- [ ] 실제로 가입 → 크레딧 지급 → 이미지 생성 → 결제(테스트 키) 를 한 번 통과시켜 봤다
- [ ] `.env` 가 커밋되지 않았다 (`git status` 로 확인)

---

## 알려진 제약 — 오픈 후 볼 것

`나중에할일.md` 와 함께 볼 것. 이번 배포 구성에서 특히 걸리는 것만 추린다.

### Cloudflare 100초 타임아웃

무료 플랜은 origin 응답을 100초까지만 기다리고 **524** 를 돌려준다.
`fal_client.py` 는 180초까지 기다리므로, 생성이 100초를 넘기면 백엔드는 성공했는데
사용자는 오류를 보게 된다(크레딧은 이미 차감된 상태). 현재 모델(`z-image/turbo`)은
보통 10초 내라 여유가 있지만, **모델을 바꾸면 이 한계를 가장 먼저 만난다.**
그때는 생성을 비동기 작업(폴링)으로 바꿔야 한다.

### DB 마이그레이션 없음

스키마는 기동 시 `Base.metadata.create_all` 로만 만들어진다. 빈 DB 에 처음 붙일 때는
문제없지만, 이후 컬럼을 바꾸면 **자동 반영되지 않는다.** 운영 데이터가 쌓이기 전에
Alembic 을 도입할 것.

### 레이트리밋이 프로세스 로컬

`rate_limit.py` 는 메모리 기반이라 uvicorn 워커를 늘리면 실제 제한이 워커 수만큼
느슨해진다. 현재 워커 1개(기본값)라 정확히 동작한다. 스케일아웃 시 Redis 로 옮길 것.

### 토스 테스트 키로 오픈

테스트 키 상태에서는 실제 결제가 일어나지 않는다. 결제 UI 를 노출한 채 두면
사용자가 크레딧을 못 받는다고 문의할 수 있다. 사업자등록·심사 완료 전까지는
결제 진입점을 막아두거나 안내 문구를 두는 편이 낫다.
또한 이용약관(`TermsPage.vue` 제4조)의 환불 규정이 아직 "결제 미연동" 기준이라,
유료화 시점에 사실과 어긋난다.

### 모더레이션 no-op

`moderation.py` 의 `check_prompt()` 는 현재 모든 프롬프트를 통과시킨다.
`FAL_ENABLE_SAFETY_CHECKER` 도 꺼져 있어 **필터가 사실상 없는 상태**로 공개된다.
팬 자유 프롬프트 경로가 열려 있으므로 오픈 전에 정책을 정할 것.

### HSTS

안정화 후 Cloudflare → SSL/TLS → Edge Certificates → HSTS 에서 켤 것.
한 번 켜면 브라우저에 캐시되어 max-age 동안 되돌릴 수 없으니, 도메인 구성이
확정된 뒤에 켠다.
