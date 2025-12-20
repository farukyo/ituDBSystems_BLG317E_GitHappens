import pymysql
try:
    conn = pymysql.connect(host='127.0.0.1', user='root', password='sevval2005.', database='githappens')
    cursor = conn.cursor()
    cursor.execute("SELECT seriesId, seriesTitle, startYear FROM series WHERE seriesTitle LIKE '%gilmore%' LIMIT 5;")
    print('Gilmore series:', cursor.fetchall())
    
    # 2018'de başlayanlar
    cursor.execute("SELECT seriesId, seriesTitle, startYear FROM series WHERE startYear = 2018 LIMIT 5;")
    print('2018 series:', cursor.fetchall())
    
    conn.close()
except Exception as e:
    print('Error:', e)
