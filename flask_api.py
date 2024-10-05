from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS
from credentials import DB_PARAMS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8000"}})

def get_db_connection():
    conn = psycopg2.connect(
        host = DB_PARAMS["host"],
        port = DB_PARAMS["port"],
        database = DB_PARAMS["database"],
        user = DB_PARAMS["user"],
        password = DB_PARAMS["password"]
    )
    return conn

@app.route('/api/rate_curve', methods=['GET'])
def get_rate_curve():
    country = request.args.get('country')
    date = request.args.get('date')
    va_int = request.args.get('va_int')
    shock_int = request.args.get('shock_int')

    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT period, rate
        FROM eiopa
        WHERE country = %s
        AND date_trunc('month', date) = date_trunc('month', %s::date)
        AND va_int = %s
        AND shock_int = %s
        ORDER BY period
    """, (country, date, va_int, shock_int))
    
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([{'period': row[0], 'rate': row[1]} for row in results])

if __name__ == '__main__':
    app.run(debug=True)
