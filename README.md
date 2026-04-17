# URL Checker

Đây là một dịch vụ FastAPI dùng để kiểm tra trạng thái truy cập của URL, lưu lại lịch sử kiểm tra cơ bản và thực hành quy trình deploy từ local Docker lên Railway hoặc Render.

Project này được dùng cho bài lab Day 12, vì vậy một số phần vẫn được giữ ở mức đơn giản để phục vụ học tập. Bạn nên xem đây là project luyện tập triển khai, không phải một dịch vụ production hoàn chỉnh.

## Tính năng chính

- `GET /health` để kiểm tra service còn sống
- `GET /ready` để kiểm tra service sẵn sàng nhận request
- `POST /check` để kiểm tra một URL
- `GET /results` để xem các kết quả đã lưu
- `GET /sessions/{session_id}` để xem lịch sử theo session
- Bảo vệ endpoint bằng API key
- Hỗ trợ chạy bằng Docker và Docker Compose
- Có sẵn cấu hình deploy cho Railway và Render

## Cấu trúc project

- `app/` chứa mã nguồn FastAPI
- `url_checker_backend/` chứa dữ liệu mẫu dùng khi phát triển local
- `Dockerfile` dùng để build image production
- `Dockerfile.dev` dùng cho môi trường phát triển
- `docker-compose.yml` dùng để chạy nhiều service local
- `nginx.conf` cấu hình reverse proxy
- `railway.toml` cấu hình deploy Railway
- `render.yaml` cấu hình deploy Render

## Yêu cầu

- Python 3.11
- Docker và Docker Compose

## Biến môi trường

Các biến môi trường chính của app:

- `API_KEY` API key dùng để gọi các endpoint được bảo vệ
- `DEBUG` nên để `false` khi chạy production
- `ENV` tên môi trường, ví dụ `development` hoặc `production`
- `PORT` cổng runtime do nền tảng cloud cấp
- `REQUEST_TIMEOUT_SECONDS` thời gian chờ khi gọi HTTP ra ngoài
- `DATA_DIR` thư mục ghi dữ liệu runtime, mặc định là `/tmp/url_checker`
- `REDIS_URL` để dành cho các cải tiến trạng thái chia sẻ sau này

Không commit file `.env` thật. Chỉ commit `.env.example`.

## Chạy local không dùng Docker

Tạo virtual environment và cài thư viện:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Chạy ứng dụng:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Kiểm tra nhanh:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
curl -i -X POST http://localhost:8000/check \
	-H 'X-API-Key: change-me-in-production' \
	-H 'X-User-Id: demo-user' \
	-H 'Content-Type: application/json' \
	-d '{"url":"https://example.com"}'
```

## Chạy bằng Docker Compose

Chạy riêng app và Redis:

```bash
docker compose up -d --build app redis
```

Chạy toàn bộ stack, bao gồm nginx:

```bash
docker compose up -d --build
```

Các cổng local hiện tại:

- `8000` cho FastAPI app
- `8090` cho nginx reverse proxy

Kiểm tra trạng thái container:

```bash
docker compose ps
```

Test trực tiếp vào app:

```bash
curl -i http://localhost:8000/health
curl -i -X POST http://localhost:8000/check \
	-H 'X-API-Key: change-me-in-production' \
	-H 'X-User-Id: demo-user' \
	-H 'Content-Type: application/json' \
	-d '{"url":"https://example.com"}'
curl -i 'http://localhost:8000/results?limit=5'
```

Test qua nginx:

```bash
curl -i http://localhost:8090/health
curl -i -X POST http://localhost:8090/check \
	-H 'X-API-Key: change-me-in-production' \
	-H 'X-User-Id: demo-user' \
	-H 'Content-Type: application/json' \
	-d '{"url":"https://example.com"}'
curl -i 'http://localhost:8090/results?limit=5'
```

Dừng stack:

```bash
docker compose down
```

## Deploy lên Railway

Quy trình đề xuất:

1. Đảm bảo local test đã pass bằng Docker hoặc FastAPI local.
2. Commit và push code mới nhất lên GitHub.
3. Trong Railway, tạo project mới từ GitHub repository.
4. Nếu `url_checker` nằm trong một repo lớn hơn, đặt `Root Directory` là `url_checker`.
5. Railway sẽ dùng `Dockerfile` và `railway.toml` để build và chạy service.
6. Thêm biến môi trường trên Railway:

```env
API_KEY=your-real-secret-key
DEBUG=false
ENV=production
```

7. Chờ quá trình build, khởi động và health check hoàn tất.
8. Test domain được Railway cấp:

```bash
curl -i https://your-service-domain/health
curl -i -X POST https://your-service-domain/check \
	-H 'X-API-Key: your-real-secret-key' \
	-H 'X-User-Id: demo-user' \
	-H 'Content-Type: application/json' \
	-d '{"url":"https://example.com"}'
```

## Deploy lên Render

Project này cũng có sẵn `render.yaml`.

Quy trình cơ bản:

1. Push project lên GitHub.
2. Tạo Web Service mới trên Render từ repository.
3. Nếu cần, cấu hình Render trỏ đúng tới thư mục `url_checker`.
4. Xác nhận Render dùng Docker deployment.
5. Thêm biến môi trường như:

```env
API_KEY=your-real-secret-key
DEBUG=false
ENV=production
```

6. Deploy và test `/health`, `/check`.

## Giới hạn hiện tại

- Dữ liệu session vẫn đang dùng bộ nhớ trong process ở `app/main.py`, nên chưa thật sự stateless khi scale nhiều instance.
- Cách lưu file local trong `app/storage.py` phù hợp để demo/lab, chưa phải persistence bền vững cho production.
- Rate limit và cost guard vẫn đang hoạt động theo từng process riêng.
- `.env.example` có thể vẫn chứa các giá trị mặc định yếu để phục vụ bài lab. Hãy rà soát lại trước khi deploy thật.

## Gợi ý kiểm tra theo bài lab

Bạn có thể dùng các bước sau làm bằng chứng nộp bài Day 12:

1. App local trả `200` ở `/health`.
2. `POST /check` chạy được với API key hợp lệ.
3. API key sai bị từ chối.
4. Docker image build thành công.
5. Docker Compose stack khởi động thành công.
6. Railway deploy thành công và `/health` trả `200`.

## Lưu ý

- Không commit `.venv/`, `__pycache__/`, `.env`, hoặc secret thật.
- Nên commit `.env.example`, các Docker file và các file cấu hình deploy.
