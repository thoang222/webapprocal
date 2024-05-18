
from threading import Thread
import mysql.connector,os, json
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import telebot,re, random, datetime
from flask import Flask, render_template, request, session, redirect, url_for,jsonify, abort
from mysql1 import mysql_data
import requests,uuid
class MyApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.list_token = ['6925235593:AAG5rThJDhzPeYOD0JGFjlgG_V3KMnhKA9w','6940379920:AAFRkVjtT5Y4_QI1L8NnBWeZ2gmugdqINhI'] 
        self.group_id = "-4011473840"

        self.valid_username = "nhothoang"
        self.valid_password = "km@123456" 

        self.host = "localhost"
        self.user = "root"
        self.password = "123456"
        self.database_name = "user_data"
        self.table_name = "customers"
        self.app.secret_key = 'nhothoang'

        # self.host = "service1.c1oky8gamqpg.ap-southeast-1.rds.amazonaws.com"
        # self.user = "nhothoang"
        # self.password = "km22071994"
        # self.database_name = "user_data"
        # self.table_name = "customers"


        self.app.config['MYSQL_HOST'] = self.host
        self.app.config['MYSQL_USER'] = self.user
        self.app.config['MYSQL_PASSWORD'] = self.password
        self.app.config['MYSQL_DB'] = self.database_name
        self.mysql = MySQL(self.app)
        # Define routes
        self.app.add_url_rule('/check', 'index', self.index)
        self.app.add_url_rule('/login1', 'login1', self.login1, methods=['POST'])
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET','POST'])
        self.app.add_url_rule('/', 'login', self.login, methods=['GET', 'POST'])

        self.app.add_url_rule('/register', 'register', self.register, methods=['GET', 'POST'])
        # @app.route('/approval', methods=['GET', 'POST'])        
        # self.app.add_url_rule('/approval', 'approval', self.approval, methods=['GET', 'POST'])
        # self.app.add_url_rule('/expzalo', 'expzalo',  lambda:self.approval(column_name="expzalo"), methods=['GET', 'POST'])
        # self.app.add_url_rule('/expfacebook', 'expfacebook',  lambda:self.approval(column_name="expfacebook"), methods=['GET', 'POST'])
        self.app.add_url_rule('/expdate', 'expdate', lambda: self.approval(column_name="expdate"), methods=['GET', 'POST'])
        self.app.add_url_rule('/expzalo', 'expzalo', lambda: self.approval(column_name="expzalo"), methods=['GET', 'POST'])
        self.app.add_url_rule('/expfacebook', 'expfacebook', lambda: self.approval(column_name="expfacebook"), methods=['GET', 'POST'])
        self.app.add_url_rule('/exptiktok', 'exptiktok', lambda: self.approval(column_name="exptiktok"), methods=['GET', 'POST'])
        self.app.add_url_rule('/exptelegram', 'exptelegram', lambda: self.approval(column_name="exptelegram"), methods=['GET', 'POST'])
        self.app.add_url_rule('/uuid', 'uuid', lambda: self.approval(column_name="uuid"), methods=['GET', 'POST'])
        
        # @app.route('/disapproval', methods=['GET', 'POST'])
        # self.app.add_url_rule('/disapproval', 'disapproval', self.disapproval, methods=['POST'])
        # @app.route('/<path:file_path>')
        self.app.add_url_rule('/<path:file_path>', 'get_json', self.get_json, methods=['GET'])
        # @app.route('/data', methods=['POST'])
        self.app.add_url_rule('/data', 'data', self.handle_data, methods=['POST'])

        # @app.route('/delete_account', methods=['GET', 'POST'])
        self.app.add_url_rule('/delete_account', 'delete_account', self.delete_account, methods=['GET', 'POST'])
        self.app.add_url_rule("/money", 'money', self.money, methods=['GET', 'POST'])
        # @app.route('/logout')
        self.app.add_url_rule('/logout', 'logout', self.logout)
        #  @app.route('/logout2')
        self.app.add_url_rule('/logout2', 'logout2', self.logout2)

    def creadte_database(self):
        mysql_instance = mysql_data(self.host, self.user, self.password, self.database_name, self.table_name)
        Thread(target=mysql_instance.create_database).start()

    def send_mess_tele(self,token=None, id="-4011473840", content = None):
        telebot.TeleBot(token=token).send_message(chat_id=id, text=content)
    def get_mysql_cursor(self):
        return self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    def index(self):
        if 'username' in session:
            return redirect(url_for('expdate'))
        return render_template('login1.html')


    def login1(self):
        entered_username = request.form.get('username')
        entered_password = request.form.get('password')

        if entered_username == self.valid_username and entered_password == self.valid_password:
            session['username'] = entered_username
            return redirect(url_for('expdate'))
        else:
            return render_template('login1.html', error="Invalid username or password")



    def login(self):
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            # passport = request.form['passport']
            # approval = 1
            cursor = self.get_mysql_cursor()
            cursor.execute(f'SELECT * FROM {self.table_name} WHERE username = %s AND password = %s', (username, password))
            customer = cursor.fetchone()
            if customer:
                session['loggedin'] = True
                session['id'] = customer['id']
                session['username'] = customer['username']
                msg = f'Logged in successfully!{customer["expdate"]}/{customer["expzalo"]}/{customer["expfacebook"]}/{customer["exptiktok"]}/{customer["exptelegram"]}@{customer["uuid"]}'
                #return render_template('index.html', msg=msg)
            else:
                msg = 'Incorrect username, password, or passport. Please try again.'
        return render_template('login.html', msg=msg)

    def send_mess_tele(self,token=None, id="-4173135015", content = None):
        telebot.TeleBot(token=token).send_message(chat_id=id, text=content)

    def register(self):
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'uuid' in request.form:
            username = request.form['username']
            password = request.form['password']
            uuid = request.form['uuid']
            cursor =self.get_mysql_cursor()
            cursor.execute(f'SELECT * FROM {self.table_name} WHERE username = %s OR uuid = %s', (username,uuid))
            existing_user = cursor.fetchone()
            if existing_user:
                if existing_user['username'] == username:
                    msg = 'Username already exists!'
                elif existing_user['uuid'] == uuid:
                    msg = 'UUID already exists!'

            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password:
                msg = 'Please fill out the form!'

            else:
                response = requests.get("http://worldtimeapi.org/api/timezone/Asia/Ho_Chi_Minh")
                data = response.json()
                current_time_str = data['datetime']
                current_time = datetime.datetime.fromisoformat(current_time_str)
                cursor.execute(f'INSERT INTO {self.table_name} (username, password, expdate, uuid) VALUES (%s, %s, %s, %s)', (username, password, current_time, uuid))
                cursor.connection.commit()
                msg = 'You have successfully registered!'
                # token = random.choice(self.list_token)
                # self.send_mess_tele(token=token, content=f"Resgister success in service1\naccount: {username}\nPassword: {password}")
                return render_template('login.html', msg=msg)
            
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return render_template('register.html', msg=msg)


    # @app.route('/<path:file_path>')
    def get_json(self,file_path):
        if file_path.endswith('.json'):
            file_path = os.path.join(os.getcwd(), file_path)
        else:
            file_path = os.path.join(os.getcwd(), file_path + '.json')
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                return jsonify(data)
            except FileNotFoundError:
                abort(404)
            except Exception as e:
                abort(500)
        else:
            abort(404)


    # @app.route('/data', methods=['POST'])
    def handle_data(self):
        data = request.json
        if data:
            if "filename" in data:
                filename = f"{data['filename']}.json" 

                with open(f'{os.getcwd()}/{filename}', 'w') as file:
                    json.dump(data["data"], file, indent=4)
                
                return jsonify({'message': 'Data received and saved successfully!'}), 200
        else:
            return jsonify({'error': 'No data received!'}), 400 



    # @app.route('/approval', methods=['GET', 'POST'])
    def approval(self, column_name=None):
        if 'username' in session:
            msg = ''
            if request.method == 'POST' and "username" in request.form and column_name in request.form:
                username = request.form['username']
                expdate = request.form[column_name]

                current_time = datetime.datetime.now()
                future_time = current_time + datetime.timedelta(days=int(expdate))
                try:
                    cursor = self.get_mysql_cursor()
                    cursor.execute(f"SELECT * FROM {self.table_name} WHERE username = %s", (username,))
                    customer = cursor.fetchone()

                    if customer:
                        msg = 'Approval successfully!'
                        cursor.execute(f"UPDATE {self.table_name} SET {column_name} = %s WHERE username = %s", (future_time, username))
                        cursor.connection.commit()
                    else:
                        msg = 'Incorrect username. Please try again.'
                except mysql.connector.Error as err:
                    msg = f"Error: {err}"
                finally:
                    cursor.close()
            return render_template('approval.html', msg=msg, column_name=column_name)
        else:
            return redirect(url_for('index'))
    def money(self):
        if 'username' in session:
            msg = ''
            if request.method == 'POST' and "username" in request.form:
                username = request.form['username']
                money = request.form['money']
                try:
                    cursor = self.get_mysql_cursor()
                    cursor.execute(f"SELECT * FROM {self.table_name} WHERE username = %s", (username,))
                    customer = cursor.fetchone()
                    if customer:
                        msg = 'add money successfully!'
                        cursor.execute(f"UPDATE {self.table_name} SET money = %s WHERE username = %s", (money, username))
                        cursor.connection.commit()
                    else:
                        msg = 'Incorrect username. Please try again.'
                except mysql.connector.Error as err:
                    msg = f"Error: {err}"
                finally:
                    cursor.close()
            return render_template('money.html', msg=msg)    
        else:
            return redirect(url_for('index'))  

    # @app.route('/delete_account', methods=['GET', 'POST'])
    def delete_account(self):
        if 'username' in session:
            msg = ''
            if request.method == 'POST' and "username" in request.form:
                username = request.form['username']
                
                try:
                    cursor = self.get_mysql_cursor()
                    cursor.execute(f"SELECT * FROM {self.table_name} WHERE username = %s", (username,))
                    customer = cursor.fetchone()

                    if customer:        
                        # cursor = mysql.connection.cursor()
                        cursor.execute(f"DELETE FROM {self.table_name} WHERE username = %s", (username,))
                        cursor.connection.commit()
                        msg = f'Account with username {username} has been deleted.'
                    else:
                        msg = 'Incorrect username. Please try again.'
                except:
                    msg = "Error deleting account."
                finally:
                    cursor.close()
            return render_template('delete_account.html', msg=msg)
        else:
            return redirect(url_for('index'))

    # @app.route('/logout')
    def logout(self):
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('login'))

    # @app.route('/logout2')
    def logout2(self):
        session.pop('username', None)
        return redirect(url_for('index'))




if __name__ == "__main__":
    my_app = MyApp()
    my_app.creadte_database()
    my_app.app.run(debug=True)

            
    # @app.route('/approval', methods=['GET', 'POST'])
    # def approval():
    #     if 'username' in session:
    #         msg = ''
    #         if request.method == 'POST' and "username" in request.form and "expdate" in request.form:
    #             username = request.form['username']
    #             expdate = int(request.form['expdate'])
    #             print(username, expdate)
                
    #             current_time = datetime.datetime.now()
    #             future_time = current_time + datetime.timedelta(days=expdate)
                
    #             formatted_future_time = future_time.strftime('%Y-%m-%d %H:%M:%S')
                
    #             try:
    #                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #                 cursor.execute("SELECT * FROM {} WHERE username = %s".format(table_name), (username,))
    #                 customer = cursor.fetchone()

    #                 if customer:
    #                     print(formatted_future_time)
    #                     msg = 'Approval successfully!'
    #                     cursor.execute("UPDATE {} SET expdate = %s WHERE username = %s".format(table_name), (formatted_future_time, username))
    #                     mysql.connection.commit() 
    #                 else:
    #                     msg = 'Incorrect username. Please try again.'
    #             except mysql.connector.Error as err:
    #                 msg = f"Error: {err}"
    #             finally:
    #                 cursor.close()
    #         return render_template('approval.html', msg=msg)
    #     else:
    #         return redirect(url_for('index'))


    # @app.route('/disapproval', methods=['GET', 'POST'])
    # def disapproval(self):
    #     if 'username' in session:
    #         msg = ''
    #         if request.method == 'POST' and "passport" in request.form:
    #             passport = request.form['passport']
    #             try:
    #                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #                 cursor.execute(f"SELECT * FROM {table_name} WHERE passport = %s", (passport,))
    #                 customer = cursor.fetchone()

    #                 if customer:
    #                     msg = 'Disapproval successfully!'
    #                     cursor.execute(f"UPDATE {table_name} SET approval = 0 WHERE passport = %s", (passport,))
    #                     mysql.connection.commit() 
    #                     # return render_template('index.html', msg=msg)
    #                 else:
    #                     msg = 'Incorrect passport. Please try again.'
    #             except mysql.connector.Error as err:
    #                 msg = f"Error: {err}"
    #             finally:
    #                 cursor.close()
    #         return render_template('disapproval.html', msg=msg)
    #     else:
    #         return redirect(url_for('index'))



    # @app.route('/check_account', methods=['GET', 'POST'])
    # def check_account():
    #     if 'username' in session:
    #         msg = ''
    #         if request.method == 'POST' and "passport" in request.form:
    #             passport = request.form['passport']
    #             try:
    #                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #                 cursor.execute(f"SELECT * FROM {self.table_name} WHERE passport = %s", (passport,))
    #                 customer = cursor.fetchone()

    #                 if customer:
    #                     username = customer.get('username')
    #                     password = customer.get('password')
    #                     approval = customer.get('approval')

    #                     msg = f'Account: {username}, Password: {password}, Approval: {approval}'
    #                 else:
    #                     msg = 'Incorrect passport. Please try again.'
    #             except:
    #                 msg = "Not connected to Database"
    #             finally:
    #                 cursor.close()
    #         return render_template('check_account.html', msg=msg)
    #     else:
    #         return redirect(url_for('index'))

    # @app.route('/delete_account', methods=['GET', 'POST'])
    # def delete_account():
    #     if 'username' in session:
    #         msg = ''
    #         if request.method == 'POST' and "passport" in request.form:
    #             passport = request.form['passport']
                
    #             try:
    #                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #                 cursor.execute(f"SELECT * FROM {table_name} WHERE passport = %s", (passport,))
    #                 customer = cursor.fetchone()

    #                 if customer:        
    #                     cursor = mysql.connection.cursor()
    #                     cursor.execute(f"DELETE FROM {table_name} WHERE passport = %s", (passport,))
    #                     mysql.connection.commit()
    #                     msg = f'Account with passport {passport} has been deleted.'
    #                 else:
    #                     msg = 'Incorrect passport. Please try again.'
    #             except:
    #                 msg = "Error deleting account."
    #             finally:
    #                 cursor.close()
    #         return render_template('delete_account.html', msg=msg)
    #     else:
    #         return redirect(url_for('index'))

    # @app.route('/remove_account1', methods=['GET', 'POST'])
    # def remove_account():
    #     if 'username' in session:
    #         msg = ''
    #         if request.method == 'POST':
    #             try:
    #                 cursor = mysql.connection.cursor()
    #                 cursor.execute(f"DELETE FROM {table_name} WHERE approval = 0")
    #                 mysql.connection.commit()
    #                 msg = 'Accounts with approval = 0 have been removed.'
    #             except:
    #                 msg = "Error removing accounts."
    #             finally:
    #                 cursor.close()

    #         return render_template('remove_account.html', msg=msg)
    #     else:
    #         return redirect(url_for('index'))

    # @app.route("/country")
    # def country():
    #     return render_template("country.html")
    


    # @app.route('/logout')
    # def logout():
    #     session.pop('loggedin', None)
    #     session.pop('id', None)
    #     session.pop('username', None)
    #     return redirect(url_for('login'))

    # @app.route('/logout2')
    # def logout2():
    #     session.pop('username', None)
    #     return redirect(url_for('index'))


