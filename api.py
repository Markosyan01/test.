#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, shutil, time

def cpu_usage():
    def read():
        with open('/proc/stat') as f:
            p=f.readline().split()
        vals=list(map(int,p[1:]))
        idle=vals[3]+(vals[4] if len(vals)>4 else 0)
        return sum(vals), idle
    a=read(); time.sleep(.15); b=read()
    total=b[0]-a[0]; idle=b[1]-a[1]
    return round((1-idle/total)*100,1) if total else 0

def mem():
    data={}
    with open('/proc/meminfo') as f:
        for line in f:
            k,v=line.split(':')[0],line.split()[1]
            data[k]=int(v)
    total=data['MemTotal']; avail=data['MemAvailable']
    used=total-avail
    return round(used/total*100,1), f"{used//1024} / {total//1024} MB"

def disk():
    d=shutil.disk_usage('/')
    return f"{d.used//(1024**3)} / {d.total//(1024**3)} GB"

def uptime():
    seconds=int(float(open('/proc/uptime').read().split()[0]))
    days,seconds=divmod(seconds,86400); hours,seconds=divmod(seconds,3600); minutes=seconds//60
    return f"{days}d {hours}h {minutes}m"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/api/stats':
            self.send_response(404); self.end_headers(); return
        ram, memory=mem()
        body=json.dumps({'cpu':cpu_usage(),'ram':ram,'memory':memory,'disk':disk(),'uptime':uptime()}).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Cache-Control','no-store')
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Content-Length',str(len(body))); self.end_headers()
        self.wfile.write(body)
    def log_message(self,*args): pass

HTTPServer(('127.0.0.1',9000),Handler).serve_forever()
