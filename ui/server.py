from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import threading
import time
import uuid
import io
import csv
import httpx
from typing import Dict, Any

from discovery.job_producer import JobProducer
from core.config import GO_SCRAPER_API_URL, GO_SCRAPER_API_KEY

app = FastAPI()
app.mount("/static", StaticFiles(directory="ui/static"), name="static")

producer = JobProducer(api_url=GO_SCRAPER_API_URL, api_key=GO_SCRAPER_API_KEY)

# In-memory session store: not persistent; suitable for local/dev
_sessions: Dict[str, Dict[str, Any]] = {}
_poll_interval = 5.0  # seconds


@app.get("/", response_class=HTMLResponse)
async def index():
    html = open("ui/static/index.html", "r", encoding="utf-8").read()
    return HTMLResponse(content=html)


@app.post("/start")
async def start_job(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    industry = body.get("industry")
    city = body.get("city")
    max_jobs = body.get("max_jobs")

    if not industry or not city:
        return JSONResponse({"error": "industry and city required"}, status_code=400)

    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"jobs": [], "results": []}

    # produce jobs synchronously but in a thread so we return quickly
    def produce_and_poll():
        submitted = producer.produce_jobs_for_industry(industry, city, max_jobs)

        job_list = []
        for item in submitted:
            # expected response: {'job_id': '...', 'status': 'pending'}
            if isinstance(item.get("response"), dict):
                job_id = item["response"].get("job_id")
            else:
                job_id = None

            job_list.append({
                "query": item.get("query"),
                "job_id": job_id,
                "status": "submitted" if job_id else "error",
                "error": item.get("error"),
            })

        _sessions[session_id]["jobs"] = job_list

        # poll job statuses until all finished
        client = httpx.Client(timeout=30.0)
        incomplete = True
        while incomplete:
            incomplete = False
            for j in _sessions[session_id]["jobs"]:
                if not j.get("job_id"):
                    continue
                if j.get("status") in ("completed", "failed"):
                    continue

                try:
                    resp = client.get(f"{GO_SCRAPER_API_URL.rstrip('/')}/jobs/{j['job_id']}", headers={"Authorization": f"Bearer {GO_SCRAPER_API_KEY}"} if GO_SCRAPER_API_KEY else {})
                    if resp.status_code == 200:
                        data = resp.json()
                        j["status"] = data.get("status")

                        if data.get("status") == "completed":
                            # Results may be embedded in `results` field
                            results = data.get("results")
                            if results:
                                # append results to session results list
                                _sessions[session_id]["results"].extend(results if isinstance(results, list) else [results])
                    else:
                        # leave status as-is; mark incomplete so we retry
                        incomplete = True
                except Exception:
                    incomplete = True

            if incomplete:
                time.sleep(_poll_interval)

    thread = threading.Thread(target=produce_and_poll, daemon=True)
    thread.start()

    return {"session_id": session_id}


@app.get("/status/{session_id}")
async def status(session_id: str):
    s = _sessions.get(session_id)
    if s is None:
        return JSONResponse({"error": "unknown session"}, status_code=404)

    total = len(s["jobs"])
    completed = len([j for j in s["jobs"] if j.get("status") == "completed"])
    return {"total": total, "completed": completed, "jobs": s["jobs"]}


@app.get("/download/{session_id}")
async def download_csv(session_id: str):
    s = _sessions.get(session_id)
    if s is None:
        return JSONResponse({"error": "unknown session"}, status_code=404)

    output = io.StringIO()
    writer = csv.writer(output)

    # determine CSV headers by inspecting first result
    results = s.get("results", [])
    if not results:
        return JSONResponse({"error": "no results yet"}, status_code=400)

    # normalize results to dicts
    first = results[0]
    if isinstance(first, dict):
        headers = list(first.keys())
        writer.writerow(headers)
        for r in results:
            writer.writerow([r.get(h, "") for h in headers])
    else:
        # fallback: single column
        writer.writerow(["result"])
        for r in results:
            writer.writerow([str(r)])

    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=leads_{session_id}.csv"})
