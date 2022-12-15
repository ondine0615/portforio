from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from app import app
import psycopg2
from psycopg2.extras import RealDictCursor
import json

MAPBOX_ACCESS_KEY = "pk.eyJ1Ijoib25kaW5lMDYxNSIsImEiOiJjbDhwZGljdG0wbnZ3M3ZvZ3lwZWtieThyIn0.Bth2_STTLlVHzduY-47WYQ"

conn = psycopg2.connect(
    database="OSLO_CITY_Bike",
    user='postgres',
    password='password',
    host='127.0.0.1',
    port='5432'
)

cursor=conn.cursor(cursor_factory=RealDictCursor)

@app.route("/", methods=['GET','POST'])
@app.route("/home",methods=["GET","POST"])
def home():
    return render_template("home.html",MAPBOX_ACCESS_KEY=MAPBOX_ACCESS_KEY)

@app.route("/event",methods=["GET","POST"])
def event():
    cursor.execute(open("SQLEVENT.sql","r").read())
    event =json.dumps(cursor.fetchall(),indent=2)
    print(event)
    return event