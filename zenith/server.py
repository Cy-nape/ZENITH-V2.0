import time
import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from zenith.scanner.secrets import scan_with_ai

app = FastAPI()

class ScanRequest(BaseModel):
    content: str
    filename: str

@app.post("/scan")
async def scan(req: ScanRequest):
    try:
        start_time = time.perf_counter()
        
        # Calculate the project directory relative to the incoming file being edited
        project_path = os.path.dirname(os.path.abspath(req.filename))
        findings = scan_with_ai(req.content, project_path=project_path)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            "findings": findings,
            "scan_time_ms": round(elapsed_ms, 2),
            "engine": "LRU Cached AI / Native Pipeline",
        }
    except Exception as e:
        print(f"Error evaluating scan request: {e}")
        traceback.print_exc()
        # Return graceful empty list so VS code doesn't explode
        return JSONResponse(status_code=200, content={"findings": [], "scan_time_ms": 0, "engine": "Error Fallback"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)
