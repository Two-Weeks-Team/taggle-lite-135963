from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routes import router

app = FastAPI()

app.include_router(router, prefix="/api")

@app.get("/health", response_model=dict)
async def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    html = """
    <html>
      <head>
        <title>Taggle Lite API</title>
        <style>
          body { background-color: #111; color: #eee; font-family: Arial, Helvetica, sans-serif; padding: 2rem; }
          h1 { color: #4fd1c5; }
          a { color: #63b3ed; text-decoration: none; }
          a:hover { text-decoration: underline; }
          .endpoint { margin-bottom: 1rem; }
          .stack { margin-top: 2rem; font-size: 0.9rem; color: #aaa; }
        </style>
      </head>
      <body>
        <h1>Taggle Lite API</h1>
        <p>Simple, local‑only bookmark manager backend with AI‑enhanced tagging and clustering.</p>
        <div class="endpoints">
          <div class="endpoint"><strong>GET</strong> /health – health check</div>
          <div class="endpoint"><strong>POST</strong> /api/bookmarks – add a bookmark (Pro sync)</div>
          <div class="endpoint"><strong>GET</strong> /api/bookmarks – list / search bookmarks</div>
          <div class="endpoint"><strong>DELETE</strong> /api/bookmarks/{"{id}"} – delete a bookmark</div>
          <div class="endpoint"><strong>POST</strong> /api/generate-tags – AI tag suggestions</div>
          <div class="endpoint"><strong>POST</strong> /api/cluster – AI semantic clustering</div>
        </div>
        <div class="stack">
          <p>Tech Stack: FastAPI 0.115.0, Pydantic 2.9.0, SQLAlchemy 2.0.35, PostgreSQL, DO Serverless Inference (openai‑gpt‑oss‑120b)</p>
          <p><a href="/docs">OpenAPI Docs</a> | <a href="/redoc">ReDoc</a></p>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
