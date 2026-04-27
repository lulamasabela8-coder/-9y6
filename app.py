from flask import Flask, render_template, request, redirect, session
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt  

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  

# Database connection
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root@Admin1",
    database="apple"  
)
cursor = conn.cursor(dictionary=True)


cursor.execute("CREATE DATABASE IF NOT EXISTS apple")
cursor.execute("USE apple")

# Create 'users' table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(255)
    )
""")
conn.commit()  


data = pd.read_csv("apple_data.csv")

# Clean and process data
data.drop_duplicates(inplace=True)  
data.dropna(inplace=True)
data['Year'] = data['Year'].astype(int)
data['Energy_kWh'] = data['Energy_kWh'].astype(float)
data['CO2_kg'] = data['CO2_kg'].astype(float)

# Data Analysis
n_data = data.groupby('Product').agg({
    'Energy_kWh': 'sum',
    'CO2_kg': 'sum'
}).head()

print(n_data)


@app.route('/charts')
def charts():
    # Graphs
    url = "apple_data.csv"
    data = pd.read_csv(url)

    plt.plot(data['Year'], data['Energy_kWh'], label="Energy Usage (kWh)")
    plt.xlabel("Year")
    plt.ylabel("Energy (kWh)")
    plt.title("Electricity Usage Trend Over 5 Years")
    plt.legend()
    plt.savefig("static/plots/energy_trend.png")
    plt.show()

    # CO2 vs kWh
    plt.scatter(data['Energy_kWh'], data['CO2_kg'], label="CO2 Emissions")
    plt.xlabel("Energy (kWh)")
    plt.ylabel("CO2 Emissions")
    plt.title("Graph of kWh vs CO2")
    plt.savefig("static/plots/co2_vs_kwh.png")
    plt.show()

    return render_template('charts.html')  


@app.route('/')
def home():
    return render_template('login.html') 


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            """INSERT INTO users (name, email, password) VALUES (%s, %s, %s)""",
            (name, email, password)
        )
        conn.commit()

        return redirect('/login')

    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            session['user'] = user['name'] 
            return redirect('/dashboard')

    return render_template('login.html')


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    return render_template(
        'dashboard.html',
        energy="static/plots/energy_trend.png",
        co2="static/plots/co2_vs_kwh.png"
    )


# LOGOUT
@app.route('/logout')
def logout():
    session('user', None) 
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)