# Dự Án SaaS Y Tế

## Ví dụ ứng dụng container hóa, deploy lên AWS Lambda Container Image

Repo này được trình bày trong khóa học AI Engineering Production của Ed Donner (tuần 1):

## Hướng dẫn ngắn gọn

### Yêu cầu chuẩn bị

Các bước đã được trình bày trong khóa học:
1. Bạn đã tạo hoặc clone repo này
2. Bạn đã tạo tài khoản AWS, tạo IAM user, cấp đầy đủ quyền cần thiết, và đã thiết lập cảnh báo ngân sách
3. Bạn đã cài đặt AWS CLI và đã chạy `aws configure`
4. Bạn đã cài Docker Desktop và đang chạy, lệnh `docker ps` hoạt động
5. Bạn đã tạo file `.env` và `.env.local` từ các file mẫu và điền key của mình

### Các bước thực hiện

#### BƯỚC 1: Tạo ECR Repository

1. Trong AWS Console, tìm **ECR**
2. Bấm **Get started** hoặc **Create repository**
3. **Quan trọng**: Đảm bảo bạn đang ở đúng region (góc trên bên phải AWS Console — phải khớp với `DEFAULT_AWS_REGION` của bạn)
4. Cấu hình:
   - Visibility settings: **Private** (hoặc tiêu đề có thể là 'Create private repository')
   - Repository name: `consultation-app` (phải khớp chính xác!)
   - Để các thiết lập khác mặc định
5. Bấm **Create repository**
6. **Kiểm tra**: Bạn sẽ thấy repo `consultation-app` mới trong danh sách

#### BƯỚC 2: Đẩy Image lên ECR

**Mac/Linux**:
```bash
# Nạp biến môi trường
export $(cat .env | grep -v '^#' | xargs)

# 1. Xác thực Docker với ECR (dùng giá trị từ .env!)
aws ecr get-login-password --region $DEFAULT_AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com

# 2. Build cho Linux/AMD64 (BẮT BUỘC với máy Mac Apple Silicon!)
docker build --platform linux/amd64 --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" -t consultation-app .

# 3. Tag image
docker tag consultation-app:latest $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/consultation-app:latest

# 4. Đẩy lên ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/consultation-app:latest
```

**Windows PowerShell**:
```powershell
# Nạp biến môi trường
Get-Content .env | ForEach-Object {
    if ($_ -match '^(.+?)=(.+)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

# 1. Xác thực Docker với ECR
aws ecr get-login-password --region $env:DEFAULT_AWS_REGION | docker login --username AWS --password-stdin "$env:AWS_ACCOUNT_ID.dkr.ecr.$env:DEFAULT_AWS_REGION.amazonaws.com"

# 2. Build cho Linux/AMD64
docker build --platform linux/amd64 --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$env:NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" -t consultation-app .

# 3. Tag image
docker tag consultation-app:latest "$env:AWS_ACCOUNT_ID.dkr.ecr.$env:DEFAULT_AWS_REGION.amazonaws.com/consultation-app:latest"

# 4. Đẩy lên ECR
docker push "$env:AWS_ACCOUNT_ID.dkr.ecr.$env:DEFAULT_AWS_REGION.amazonaws.com/consultation-app:latest"
```

**Lưu ý cho Mac Apple Silicon (M1/M2/M3/M4/M5)**: Tham số `--platform linux/amd64` là BẮT BUỘC. Nếu thiếu, Lambda sẽ báo lỗi "exec format error" vì Lambda mặc định chạy trên kiến trúc amd64.

#### BƯỚC 3: Thiết lập Lambda

1. Trong AWS Console, tìm Lambda, xác nhận region (góc trên bên phải) là region mặc định của bạn, bấm **Create Function**
2. Chọn **Container image** và **Function name**: `consultation-app`
3. **Container image URI**: bấm **Browse images**, chọn repository `consultation-app` với tag `latest`, rồi bấm **Create function**
4. Tại trang của function, bấm `Configuration`
   - Chọn General Configuration, Edit. Đổi Memory thành 1024 MB và timeout thành 5 phút, rồi Save
   - Chọn Environment Variables và thêm `CLERK_SECRET_KEY`, `CLERK_JWKS_URL` và `OPENAI_API_KEY` rồi Save
   - Chọn Function URL. Chọn **Auth type**: **NONE**. Trong Additional Settings, **Invoke mode**: **RESPONSE_STREAM**. Rồi bấm Save.

Cuối cùng bấm vào Function URL ở đầu trang — VÀ THÀNH CÔNG — bạn sẽ thấy ứng dụng SaaS y tế đã chạy trực tuyến!
