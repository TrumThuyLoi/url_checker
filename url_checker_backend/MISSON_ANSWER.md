## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **API key và database password hardcode trong code** — `OPENAI_API_KEY = "sk-hardcoded-fake-key-never-do-this"` và `DATABASE_URL = "...password123..."`. Nếu push lên GitHub public, secret bị lộ ngay lập tức.
2. **Log ra secret** — `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")` in key ra stdout, ai đọc log là thấy.
3. **Dùng `print()` thay vì proper logging** — không có log level, không có timestamp chuẩn, không thể filter hay parse tự động trên production.
4. **Không có health check endpoint** — không có `/health`, platform (Railway, Render, K8s) không biết app còn sống hay đã crash để tự động restart.
5. **Port cố định và host `localhost`** — `host="localhost", port=8000` hardcode khiến app không nhận traffic bên ngoài khi chạy trong container hoặc cloud (cần `0.0.0.0` và `PORT` từ env var).
6. **`reload=True` bật cứng** — debug reload chạy trong production tốn tài nguyên và có thể gây restart bất ngờ.

### Exercise 1.3: Comparison table
| Feature | Develop (❌) | Production (✅) | Why Important? |
|---------|-------------|----------------|----------------|
| Config | Hardcode trực tiếp trong code (`OPENAI_API_KEY = "sk-..."`) | Đọc từ environment variables qua `config.py` (pydantic Settings) | Đổi môi trường không cần sửa code; không lộ secret khi push git |
| Health check | Không có | `GET /health` (liveness) + readiness flag `is_ready` | Platform biết khi nào restart container và khi nào route traffic |
| Logging | `print()` — không có level, không có cấu trúc | Structured JSON logging — có `time`, `level`, `msg` | Dễ search, filter, alert trên log aggregator (Datadog, Loki) |
| Shutdown | Tắt đột ngột | `lifespan()` — đợi request hiện tại hoàn thành, đóng connection | Tránh làm đứt request đang xử lý, tránh data corruption |
| Host/Port | `host="localhost", port=8000` cứng | `host="0.0.0.0"`, port đọc từ `settings.port` (env var `PORT`) | Container và cloud platform inject `PORT` động; `localhost` không nhận traffic từ ngoài |
| Secret | `"sk-hardcoded..."` trong source code | Không có secret nào trong code | Tránh lộ key trong git history kể cả khi xóa sau |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image:** `python:3.11` — Full Python distribution (~1GB) chứa Python runtime, pip, và standard library đủ để chạy app.
2. **Working directory:** `/app` — Tất cả file commands trong container sẽ chạy từ thư mục này.

### Exercise 2.3: Image size comparison
- Develop: 1.66 GB
- Production: 236 MB
- Difference: 85.8% smaller

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

### Exercise 3.1: Deployment Info
- **Public URL**: https://lab11ex3-production.up.railway.app/
- **Platform**: Render (Singapore)
- **Status**: Deployment successful with healthy Liveness/Readiness probes.

### Exercise 3.2: Comparison of render.yaml vs railway.toml
- **railway.toml**: Chú trọng tính tối giản, dễ cấu hình nhanh qua CLI. Phù hợp cho các service đơn lẻ hoặc deploy nhanh.
- **render.yaml**: Là "Infrastructure as Code" thực thụ, cho phép quản lý toàn bộ hệ sinh thái (Web, Redis, Postgres) trong một file duy nhất. Dễ dàng tái sử dụng và quản lý version.

## Part 4: API Security

### Exercise 4.2-4.3: Test results
```bash
# Login lấy JWT token (student)
curl -X POST http://localhost:8001/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"demo123"}'
# => 200 OK

# Gọi /ask không có token
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain JWT"}'
# => 401 Unauthorized

# Gọi /ask có token hợp lệ
curl -X POST http://localhost:8001/ask \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain JWT"}'
# => 200 OK
```

Rate limiting (student): request 1-10 trả 200, request 11-12 trả 429.

```json
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
```

Rate limiting (admin/teacher): gửi 20 requests liên tục đều 200 (không chạm limit user).

### Exercise 4.4: Cost guard implementation
Mình implement `CostGuard` theo 3 bước:

1. Check budget trước khi gọi LLM (`check_budget`):
- Per-user budget: `$1/day` -> vượt thì trả `HTTP 402`.
- Global budget: `$10/day` -> vượt thì trả `HTTP 503`.

2. Record usage sau mỗi request (`record_usage`):
- Cộng `input_tokens`, `output_tokens`, `request_count`.
- Tính cost theo đơn giá token và cộng vào tổng chi phí.

3. Cảnh báo và reset theo ngày:
- Cảnh báo khi user dùng >= 80% budget.
- Dữ liệu usage reset khi sang ngày mới.

Ghi chú: bản lab dùng in-memory để demo; production nên lưu Redis/DB để hoạt động khi scale nhiều instances.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
#### Exercise 5.1: Health checks (`/health` và `/ready`)

**Mục tiêu:** phân biệt liveness và readiness.

**Các bước thực hiện:**

1. Chạy bản develop:

```bash
cd 05-scaling-reliability/develop
python app.py
```

2. Test liveness:

```bash
curl http://localhost:8000/health
```

Kỳ vọng: trả `200` và có các trường như `status`, `uptime_seconds`, `timestamp`.

Kết quả chạy lại (thực tế qua Nginx `:8080`):

```json
{"status":"ok","instance_id":"instance-d0913e","uptime_seconds":205.2,"storage":"redis","redis_connected":true}
```

3. Test readiness:

```bash
curl http://localhost:8000/ready
```

Kỳ vọng:
- Khi app đã startup xong: `200` và `{"ready": true, ...}`
- Khi app đang shutdown hoặc chưa sẵn sàng: `503`

Kết quả chạy lại (thực tế qua Nginx `:8080`):

```json
{"ready":true,"instance":"instance-d0913e"}
```

**Kết luận:** `/health` dùng để biết process còn sống; `/ready` dùng để quyết định có route traffic vào instance hay không.

#### Exercise 5.2: Graceful shutdown

**Mục tiêu:** khi nhận `SIGTERM`, app không chết đột ngột mà chờ request đang xử lý hoàn thành.

**Các bước thực hiện:**

1. Chạy app và lấy PID:

```bash
python app.py &
PID=$!
echo $PID
```

2. Gửi request (terminal khác):

```bash
curl "http://localhost:8000/ask?question=Long%20task" -X POST
```

3. Gửi signal shutdown:

```bash
kill -SIGTERM $PID
```

4. Quan sát log:
- Có message `Graceful shutdown initiated...`
- Có thể có `Waiting for ... in-flight requests...`
- Kết thúc bằng `Shutdown complete`

**Kết luận:** app xử lý shutdown có kiểm soát, giảm rủi ro drop request.

#### Exercise 5.3: Stateless design (Redis session)

**Mục tiêu:** không lưu state trong RAM của 1 instance, mà lưu ngoài (Redis) để scale ngang.

**Các điểm chính trong code `production/app.py`:**
- `save_session(session_id, data)` lưu session vào Redis (kèm TTL)
- `load_session(session_id)` đọc session từ Redis
- `append_to_history(...)` cập nhật lịch sử hội thoại
- Endpoint `/chat` nhận `session_id`, nên request sau có thể vào instance khác vẫn tiếp tục đúng context

**Kết luận:** state được externalize, nhiều instance cùng truy cập được session chung.

#### Exercise 5.4: Load balancing với Nginx

**Mục tiêu:** phân phối request qua nhiều agent instances.

**Các bước thực hiện:**

1. Vào thư mục production của Part 5:

```bash
cd 05-scaling-reliability/production
```

2. Chạy stack:

```bash
docker compose up --scale agent=3
```

Lệnh mình chạy lại:

```bash
docker compose down -v
docker compose up -d --build --scale agent=3
docker compose ps
```

Trạng thái: `redis healthy`, `nginx started`, `agent-1/2/3 started`.

3. Gửi nhiều request qua Nginx (port 8080):

```bash
for i in {1..10}; do
  curl -s -X POST http://localhost:8080/chat \
    -H "Content-Type: application/json" \
    -d '{"question":"Request '$i'"}'
  echo
done
```

4. Quan sát kết quả:
- Trường `served_by` thay đổi giữa các request
- Header `X-Served-By` cho thấy upstream khác nhau

**Kết luận:** Nginx đang round-robin traffic thay vì dồn vào 1 instance.

#### Exercise 5.5: Test stateless

**Mục tiêu:** chứng minh hội thoại vẫn giữ được khi request đi qua nhiều instance.

**Các bước thực hiện:**

1. Khi stack đang chạy, execute script test:

```bash
python test_stateless.py
```

Kết quả chạy lại (rút gọn):

```text
Instances used: {'instance-d8e20e', 'instance-d0913e', 'instance-61dadc'}
Total messages: 10
Session history preserved across all instances via Redis
```

2. Script sẽ tự động:
- Tạo session
- Gửi nhiều câu hỏi liên tiếp
- In `served_by` từng request
- Đọc lại `/chat/{session_id}/history`

3. Tiêu chí pass:
- Có nhiều instance khác nhau xử lý request
- `history` vẫn đầy đủ, đúng số message

**Kết luận tổng Part 5:**
- Có health/readiness checks
- Có graceful shutdown
- Stateless qua Redis
- Có load balancing qua Nginx
- Session vẫn nhất quán khi scale nhiều instances
```

---