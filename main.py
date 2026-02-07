from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, os, math
import numpy as np
import httpx
import smtplib
from email.message import EmailMessage


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CRIME_FILE = "crime_reports.json"
COMMENT_FILE = "comments.json"

for f in [CRIME_FILE, COMMENT_FILE]:
    if not os.path.exists(f):
        open(f, "w").write("{}")

def load(path):
    return json.load(open(path))

def save(path, data):
    json.dump(data, open(path,"w"), indent=2)

# ---------- MODELS ----------

class RouteReq(BaseModel):
    source:str
    destination:str
    time:str

class CrimeReport(BaseModel):
    lat:float
    lon:float
    type:str

class Comment(BaseModel):
    place_id:str
    text:str

class Vote(BaseModel):
    place_id:str
    idx:int
    delta:int

# ---------- BASIC UTILS ----------

def hav(a,b,c,d):
    R=6371
    dlat=math.radians(c-a)
    dlon=math.radians(d-b)
    x=math.sin(dlat/2)**2+math.cos(math.radians(a))*math.cos(math.radians(c))*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(x))

# ---------- ROUTING ----------

async def geocode(q):
    try:
        async with httpx.AsyncClient(timeout=20.0) as c:
            r = await c.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": q + ", Telangana, India",
                    "format": "json",
                    "limit": 1
                },
                headers={"User-Agent": "SafeRouteAI"}
            )

            j = r.json()
            if not j:
                raise HTTPException(status_code=404, detail="Location not found")

            return float(j[0]["lat"]), float(j[0]["lon"])

    except Exception:
        raise HTTPException(status_code=503, detail="Geocoding service unavailable. Try again.")


async def routes(a,b,c,d):
    async with httpx.AsyncClient(timeout=30.0) as h:
        r=await h.get(f"https://router.project-osrm.org/route/v1/driving/{b},{a};{d},{c}",
        params={"alternatives":"true","geometries":"geojson"})
        return r.json()["routes"]

# ---------- HEATMAP DATA ----------

@app.get("/heatmap")
def heatmap():
    crimes=load(CRIME_FILE)
    pts=[]
    for v in crimes.values():
        for c in v:
            pts.append([c["lat"],c["lon"],1])
    return pts
@app.get("/crimes")
def get_crimes():
    crimes = load(CRIME_FILE)
    pts = []
    for v in crimes.values():
        for c in v:
            pts.append(c)
    return pts

# ---------- REPORT CRIME ----------

@app.post("/report")
def report(r:CrimeReport):
    data=load(CRIME_FILE)
    k=f"{round(r.lat,4)},{round(r.lon,4)}"
    data.setdefault(k,[]).append({"lat":r.lat,"lon":r.lon,"type":r.type})
    save(CRIME_FILE,data)
    return {"ok":True}

# ---------- COMMENTS ----------

@app.post("/comment")
def comment(c:Comment):
    d=load(COMMENT_FILE)
    d.setdefault(c.place_id,[]).append({"text":c.text,"votes":0})
    save(COMMENT_FILE,d)
    return d[c.place_id]
@app.post("/sos")
async def sos(data: dict):

    lat = data["lat"]
    lon = data["lon"]

    send_email_alert(lat, lon)

    return {"status": "sent"}

@app.post("/vote")
def vote(v:Vote):
    d=load(COMMENT_FILE)
    d[v.place_id][v.idx]["votes"]+=v.delta
    save(COMMENT_FILE,d)
    return d[v.place_id]

@app.get("/comments/{pid}")
def get_comments(pid:str):
    return load(COMMENT_FILE).get(pid,[])

# ---------- MAIN ROUTE ----------

@app.post("/route")
async def route(r:RouteReq):
    a,b=await geocode(r.source)
    c,d=await geocode(r.destination)
    rs=await routes(a,b,c,d)

    out=[]
    for x in rs:
        risk=[]
        for p in x["geometry"]["coordinates"][::20]:
            crimes=load(CRIME_FILE)
            score=0
            for k,v in crimes.items():
                for z in v:
                    score+=1/(1+hav(p[1],p[0],z["lat"],z["lon"]))
            risk.append(score)
        danger=np.mean(risk) if risk else 0
        out.append({"polyline":x["geometry"]["coordinates"],"risk":danger})

    out.sort(key=lambda x:x["risk"])
    return {"routes":out}

@app.get("/",response_class=HTMLResponse)
def root():
    return open("index.html","r",encoding="utf8").read()
def send_email_alert(lat, lon):

    EMAIL = "nagacharanmedoji@gmail.com"
    PASSWORD = "nfqt bbgi qsda ovcm"
    TO = "ajaykumarraovemula2004@gmail.com"

    msg = EmailMessage()
    msg["Subject"] = "🚨 SafeRoute SOS Alert"
    msg["From"] = EMAIL
    msg["To"] = TO

    maps = f"https://maps.google.com/?q={lat},{lon}"

    msg.set_content(f"""
🚨 EMERGENCY ALERT 🚨

User sent SOS!

Latitude: {lat}
Longitude: {lon}

Live Map:
{maps}
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

