from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.controllers.api.api_router import auth_router, api_router


app = FastAPI(
    title="Simulação TCC 1",
    version="1.0.0",
    description="https://simulacaotcc.github.io/DOCS/",
    openapi_url="/openapi.json",
    docs_url="/",
)

app.include_router(auth_router)
app.include_router(api_router)

# Sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guards against HTTP Host Header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)