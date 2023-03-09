import psycopg2

conn = psycopg2.connect(
    database="oslo_city_bike", user='postgres', password='rotin11', host='127.0.0.1', port= '5432'
)

cursor = conn.cursor()
#Creating Database Oslo_city_bike
#sql = '''CREATE database OSLO_City_Bike''';
#cursor.execute(sql)
#conn.commit()
#Creating Table Station_Status
cursor.execute("DROP TABLE IF EXISTS Station_Status")
sql ='''CREATE TABLE Station_Status(
    Station_id CHAR(20) NOT NULL,
    is_installed INT,
    is_renting INT,
    is_returning INT,
    last_reported INT,
    num_bikes_available INT,
    num_docks_available INT,
    date date
)'''
cursor.execute(sql)
conn.commit()

conn.close()