import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from jose import jwt, JWTError
from typing import Dict, Any
import time

# --- 載入環境變數 ---
# ⚠️ 在實際生產環境中，JWT_SECRET_KEY 應由 Vault 或 CI/CD 安全注入
load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-default-key")
ALGORITHM = "HS256"

# --- 模擬資料庫 (有狀態 API Key 儲存) ---
# 模擬 API Key 數據庫: {api_key: UserData}
API_KEY_DATABASE: Dict[str, Any] = {
    "SECRET_B2B_KEY_001": {
        "user_id": 9001,
        "role": "system_admin",
        "issued_at": int(time.time())
    },
    "SECRET_ANALYTICS_KEY_002": {
        "user_id": 9002,
        "role": "analytics_reader",
        "issued_at": int(time.time())
    }
}

# --- Pydantic 模型定義 ---

class TokenPayload(BaseModel):
    """JWT Token 內容物 (Payload)"""
    user_id: int = Field(..., description="用戶或服務 ID")
    role: str = Field(..., description="用戶角色")
    exp: int = Field(..., description="過期時間戳")

class UserCredentials(BaseModel):
    """模擬登入請求體"""
    username: str
    password: str

class VerifyResult(BaseModel):
    """驗證成功後返回給 Gateway 的中繼資料"""
    user_id: int
    role: str

# --- 應用程式實例化 ---
app = FastAPI(
    title="Auth Service Core",
    description="身份驗證和憑證發放的核心服務，供 API Gateway 呼叫。"
)


# --- JWT 相關函式 (在記憶體中處理密鑰) ---

def create_access_token(user_id: int, role: str, expires_delta: int = 3600) -> str:
    """生成 JWT Token"""
    expire = int(time.time()) + expires_delta
    to_encode = {"user_id": user_id, "role": role, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> TokenPayload:
    """驗證 JWT 簽名並解碼"""
    try:
        # 從記憶體讀取 JWT_SECRET_KEY 進行驗籤
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except JWTError:
        # JWTError 包含過期、簽名無效等錯誤
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token signature."
        )


# =======================================================
# 路由 I: 憑證發放 (Issuance)
# =======================================================

@app.post("/auth/login", response_model=Dict[str, str], summary="發放 JWT Token (模擬登入)")
async def login_for_access_token(credentials: UserCredentials):
    # ⚠️ 這裡應查詢資料庫驗證用戶名和密碼
    if credentials.username != "admin" or credentials.password != "secure_pass":
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 成功驗證，發放 JWT
    access_token = create_access_token(user_id=1, role="admin", expires_delta=3600)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/key/issue", response_model=Dict[str, str], summary="發放 API Key (模擬管理員操作)")
async def issue_api_key():
    # ⚠️ 在真實環境中，這裡需要執行更複雜的 Key 生成和儲存邏輯
    new_key = "GENERATED_KEY_" + os.urandom(16).hex()
    API_KEY_DATABASE[new_key] = {"user_id": 9003, "role": "service_user", "issued_at": int(time.time())}
    return {"api_key": new_key, "warning": "Key saved to simulated DB."}


# =======================================================
# 路由 II: 憑證驗證 (Validation) - 供 API Gateway 呼叫
# =======================================================

@app.get(
    "/auth/verify_jwt",
    response_model=VerifyResult,
    summary="驗證 JWT Token (Gateway 呼叫 - 無狀態)"
)
async def verify_jwt_token(
    token: str  # Gateway 會將 Token 作為 Query 或 Header 傳遞給我們
):
    """
    核心邏輯：從記憶體密鑰驗證 JWT。
    這個端點必須極快，以避免成為 Gateway 的瓶頸。
    """
    payload = decode_access_token(token)
    
    # 驗證成功 (200 OK)
    return VerifyResult(user_id=payload.user_id, role=payload.role)


@app.get(
    "/auth/verify_apikey",
    response_model=VerifyResult,
    summary="驗證 API Key (Gateway 呼叫 - 有狀態)"
)
async def verify_api_key(
    api_key: str  # Gateway 會將 API Key 作為 Query 或 Header 傳遞給我們
):
    """
    核心邏輯：查詢資料庫/快取來驗證 API Key 的有效性。
    """
    user_data = API_KEY_DATABASE.get(api_key)

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid API Key provided.")
    
    # ⚠️ 在真實環境中，這裡應檢查配額、過期時間等

    # 驗證成功 (200 OK)
    return VerifyResult(user_id=user_data["user_id"], role=user_data["role"])


# =======================================================
# 路由 III: 健康檢查 (Health Check)
# =======================================================

@app.get("/health", summary="健康檢查")
def health_check():
    # 檢查 JWT_SECRET_KEY 是否載入
    if not JWT_SECRET_KEY:
         raise HTTPException(status_code=500, detail="JWT Secret Key not initialized.")
    return {"status": "ok", "message": "Auth Service is running."}


# --- 啟動說明 ---
if __name__ == "__main__":
    # 在您的 `.env` 文件中設定 JWT_SECRET_KEY
    # JWT_SECRET_KEY="your-super-secret-key-12345"
    import uvicorn
    print(f"Auth Service loaded with Secret Key: {JWT_SECRET_KEY[:8]}...")
    uvicorn.run(app, port=8081)
