from flask import Flask, render_template, request, redirect, url_for
from flaskext.mysql import MySQL

app = Flask(__name__)
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'technopark'
app.config['MYSQL_DATABASE_PASSWORD'] = 'db'
app.config['MYSQL_DATABASE_DB'] = 'park'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('inc/index.html')


@app.route('/request_1', methods=['GET'])
def request_1():
    cursor = mysql.connect().cursor()

    _SQL = """SELECT driver_id, driver_surname, SUM(hour(Time_arrived - Time_departure))
FROM Schedule
JOIN Driver ON Driver.id=Schedule.driver_id
JOIN Terminal ON Terminal.id = Schedule.terminal_id
WHERE MONTH(Time_arrived)=9
AND YEAR(Time_arrived)=2019
GROUP BY driver_id;"""

    cursor.execute(_SQL)

    result = cursor.fetchall()
    res = []
    schema = ['driver_id', 'driver_surname', 'hours']

    for stud in result:
        res.append(dict(zip(schema, stud)))

    return render_template('inc/request_1.html', drivers=res)


@app.route('/request_2', methods=['GET'])
def request_2():
    cursor = mysql.connect().cursor()

    _SQL = """select driver_name from Schedule
join Driver on Schedule.driver_id = Driver.id
join Terminal on Schedule.terminal_id = Terminal.id
join Way on Schedule.way_id = Way.id
where way_name = "two_towers"
and year(Time_arrived) = "2019"
and month(Time_arrived) = "05";"""
    cursor.execute(_SQL)

    result = cursor.fetchall()
    res = []
    schema = ['driver_name']

    for stud in result:
        res.append(dict(zip(schema, stud)))

    return render_template('inc/request_2.html', drivers=res)


@app.route('/request_3', methods=['GET'])
def request_3():
    cursor = mysql.connect().cursor()

    _SQL = """SELECT driver_surname FROM Driver
LEFT JOIN Schedule on Schedule.driver_id=Driver.id
WHERE terminal_id is NULL;"""

    cursor.execute(_SQL)

    result = cursor.fetchall()
    res = []
    schema = ['driver_surname']

    for stud in result:
        res.append(dict(zip(schema, stud)))

    return render_template('inc/request_3.html', drivers_surnames=res)


@app.route('/request_4', methods=['GET'])
def request_4():
    cursor = mysql.connect().cursor()

    _SQL = """select driver_surname from Driver
left join Schedule s on Driver.id = s.driver_id
join Terminal t on s.terminal_id = t.id
where month(Time_arrived) != "05" and year(Time_arrived) != "2019"
group by driver_surname;"""
    cursor.execute(_SQL)

    result = cursor.fetchall()
    res = []
    schema = ['driver_surname']

    for stud in result:
        res.append(dict(zip(schema, stud)))

    return render_template('inc/request_4.html', drivers=res)


@app.route('/request_5', methods=['GET'])
def request_5():
    cursor = mysql.connect().cursor()

    _SQL = """SELECT * FROM Driver
WHERE start_working = (SELECT min(start_working) FROM Driver)
and end_working is not null
or (start_working - end_working) = (SELECT max(start_working - end_working) FROM Driver);
"""
    cursor.execute(_SQL)

    result = cursor.fetchall()
    res = []
    schema = ['id', 'driver_name', 'driver_surname', 'birth']

    for stud in result:
        res.append(dict(zip(schema, stud)))

    return render_template('inc/request_5.html', drivers=res)


@app.route('/request_6', methods=['GET'])
def request_6():
    cursor = mysql.connect().cursor()

    _SQL = """select statistic_driver.driver_id, num from statistic_driver
join Schedule on statistic_driver.driver_id=Schedule.driver_id
join Terminal on Schedule.terminal_id = Terminal.id
join Way on Schedule.way_id=Way.id
where MONTH(Time_arrived) = 09
and YEAR(Time_arrived) = 2019
and way_name = "death";
"""

    cursor.execute(_SQL)

    result = cursor.fetchall()
    res = []
    schema = ['driver_id', 'num']

    for stud in result:
        res.append(dict(zip(schema, stud)))

    return render_template('inc/request_6.html', drivers=res)


def check(year, month):
    cursor = mysql.connect().cursor()
    _SQL = """select count(*) from report where report_year = %s and report_month = %s"""
    data = (year, month)
    cursor.execute(_SQL, data)
    result = cursor.fetchall()
    check_result = result[0][0]
    return check_result


@app.route('/procedure', methods=['GET', 'POST'])
def procedure():
    year_form = request.form['grind_year']
    month_form = request.form['grind_month']
    print('year: ', year_form)
    print('month: ', month_form)

    cursor = mysql.connect().cursor()
    exists = check(year_form, month_form)

    if exists == 0:
        args = (year_form, month_form)
        result = cursor.callproc('sold_tickets_in_year', args)
        mysql.connect().commit()
        return redirect(url_for('print_report'))
    else:
        return 'This report already exists. Try another year or month'


@app.route('/print_report', methods=['GET'])
def print_report():
    cursor = mysql.connect().cursor()

    _SQL = """SELECT report_way, report_year, report_month, tickets_num FROM report order by tickets_num"""
    cursor.execute(_SQL)
    result = cursor.fetchall()

    res = []
    schema = ['report_way', 'report_year', 'report_month', 'tickets_num']

    for stud in result:
        res.append(dict(zip(schema, stud)))

    return render_template('inc/report.html', rows=res)


if __name__ == '__main__':
    app.run()
