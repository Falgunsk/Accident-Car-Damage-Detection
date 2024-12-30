import os
import pandas as pd

import forms
import logic
import Model
from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user, logout_user)
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash

import config
from flask import (Flask, flash, redirect, render_template, request, url_for)
from datetime import datetime
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['MYSQL_USER'] = config.credentials['user']
app.config['MYSQL_PASSWORD'] = config.credentials['password']
app.config['MYSQL_HOST'] = config.credentials['host']
app.config['MYSQL_PORT'] = int(config.credentials['port'])
app.config['MYSQL_DB'] = config.credentials['database']

mysql = MySQL(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, email, name, is_admin=False):
        self.id = user_id
        self.email = email
        self.name = name
        self.is_admin = is_admin
        
    def __repr__(self):
        return f'<User: {self.email}>'
    
    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_data WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    
    if user:
        return User(user[0], user[2], user[1], user[-2])
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = forms.ContactForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            subject = form.subject.data
            message = form.message.data
            
            logic.send_email(name, email, subject, message)
            
            flash('Message sent successfully. We will get back to you soon.')
            return redirect(url_for('index'))
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            password = form.password.data
            phone = form.phone.data
            address = form.address.data
            city = form.city.data
            state = form.state.data
            zip_code = form.zip_code.data
            country = form.country.data
            car_brand = form.car_brand.data
            car_model = form.car_model.data
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM user_data WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            
            if user is not None:
                print(user)
                flash('Email already exists. Please use a different email.')
                return redirect(url_for('register'))
            
            hashed_password = generate_password_hash(password)
            
            logic.register_user(name, email, hashed_password, phone, address, city, state, zip_code, country, car_brand, car_model)
            
            flash('Registration successful. Please login to continue.')
            return redirect(url_for('login'))
        
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login requests."""
    form = forms.LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            remember_me = form.remember.data
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM user_data WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            
            if user and check_password_hash(user[3], password):
                user_obj = User(user[0], user[2], user[1], user[-2])
                
                if login_user(user_obj, remember=remember_me):
                    if user[-2]:
                        return redirect(url_for('admin_dashboard'))
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password. Please try again.')
                return redirect(url_for('login'))
            
    return render_template('login.html', form=form)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admins only.')
        return redirect(url_for('index'))
    
    return render_template('admin_dashboard.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # flash(f'Welcome, {current_user.name}!')
    return render_template('dashboard.html')

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    form = forms.EstimateForm()
    brandlist, modellist = logic.get_car_data()
    
    # Always set car_brand choices regardless of method (GET or POST)
    form.car_brand.choices = [(brand, brand) for brand in brandlist]

    if request.method == 'POST':
        # Handling brand selection and model population
        if 'submit_car_brand' in request.form:
            selected_brand = form.car_brand.data
            if selected_brand in modellist:
                models_brand = set(modellist[selected_brand])
                form.car_model.choices = [(model, model) for model in models_brand]

        selected_brand = form.car_brand.data
        if selected_brand in modellist:
            models_brand = set(modellist[selected_brand])
            form.car_model.choices = [(model, model) for model in models_brand]
        
        print(f"Available car model choices: {form.car_model.choices}")
        print(f"Selected car model: {form.car_model.data}")
        print(f"Selected car brand: {form.car_brand.data}")
        
        if 'submit' in request.form and form.validate_on_submit():
            car_brand = form.car_brand.data
            car_model = form.car_model.data
            upload_image = form.upload_image.data

            # Ensure the upload directory exists
            upload_dir = os.path.join(app.root_path, 'static', 'uploads')
            output_dir = os.path.join(app.root_path, 'static', 'outputs')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)  # Create the directory if it doesn't exist

            current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # Get the current time
            
            # Save the uploaded image
            if upload_image:
                image_path = f'{upload_dir}{current_user.id}_{car_brand}_{car_model}_{current_time}.jpg'
                upload_image.save(image_path)
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM car_data WHERE brand = %s AND model = %s", (car_brand, car_model))
            car_data = cur.fetchall()
            cur.close()
            
            if not car_data:
                flash('Car brand or model not found. Please try again.')
                return redirect(url_for('predict'))
            
            path = image_path if upload_image else None
            
            model = Model.YOLOModel(image_path=path)
            
            model.predict()
            
            detected_objects = model.get_detected_objects()
            estimated_prices, total_price = model.predict_price(car_brand, car_model)
            
            original_img , out_img = model.plot_image(save_path=f'{output_dir}{current_user.id}_{car_brand}_{car_model}_{current_time}_output.jpg')
            
            
            return render_template('result.html', detected_objects=detected_objects, estimated_prices=estimated_prices, total_price=total_price, original_img=original_img, out_img=out_img)
        
        else:
            print(f"Validation errors: {form.errors}")  
        
    return render_template('predict.html', form=form)


@app.route('/result', methods=['GET']) 
@login_required
def result():
    return render_template('result.html')


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_data WHERE user_id = %s", (current_user.id,))
    user = cur.fetchone()
    cur.close()
    
    if not user:
        flash('User not found. Please login again.')
        return redirect(url_for('login'))
    
    user = pd.DataFrame([user], columns="user_id name email password phone_number address city state zipcode country registration_date car_brand car_model is_admin profile_pic".split())
    user = user.drop(columns=['password', 'is_admin'])
    
    default_pic_path = os.path.join(app.root_path, 'static', 'profile_pics', 'default.jpg')
            
    profile_pic = user.loc[0, 'profile_pic'] if user.loc[0, 'profile_pic'] else default_pic_path
    
    with open(profile_pic, 'rb') as f:
        profile_pic = base64.b64encode(f.read()).decode('utf-8')
    
    name = user.loc[0, 'name'].capitalize()
    email = user.loc[0, 'email']
    phone = user.loc[0, 'phone_number']
    address = user.loc[0, 'address']
    city = user.loc[0, 'city'].capitalize()
    state = user.loc[0, 'state'].capitalize()
    zip_code = user.loc[0, 'zipcode']
    country = user.loc[0, 'country'].upper()
    car_brand = user.loc[0, 'car_brand'].capitalize()
    car_model = user.loc[0, 'car_model'].capitalize()
    registered_on = user.loc[0, 'registration_date'].strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('profile.html', name=name, email=email, phone=phone, address=address, city=city, state=state, zip_code=zip_code, country=country, car_brand=car_brand, car_model=car_model, registered_on=registered_on, profile_pic=profile_pic)

@app.route('/settings/update-account', methods=['GET', 'POST'])
@login_required
def update_account():
    form = forms.UpdateAccountForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            phone = form.phone.data
            address = form.address.data
            city = form.city.data
            state = form.state.data
            zip_code = form.zip_code.data
            country = form.country.data
            car_brand = form.car_brand.data
            car_model = form.car_model.data
            picture = form.picture.data
            
            if picture:
                directory = os.path.join(app.root_path, 'static', 'profile_pics')
                if not os.path.exists(directory):
                    os.makedirs(directory)
                picture.save(f'{directory}{current_user.id}.jpg')
                picture_path = f'{directory}{current_user.id}.jpg'
                
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE user_id = %s", (current_user.id,))
            user = cur.fetchone()
            cur.close()
            
            if not user:
                flash('User not found. Please login again.')
                return redirect(url_for('login'))
            
            if email != user['email']:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                user2 = cur.fetchone()
                cur.close()
                
                if user2:
                    flash('Email already exists. Please use a different email.')
                    return redirect(url_for('settings'))
            
            logic.update_user(user_id=current_user.id, name=name, email=email, phone=phone, address=address, city=city, state=state, zipcode=zip_code, country=country, car_brand=car_brand, car_model=car_model, picture=picture_path)
            flash('Account updated successfully.')
        
        return redirect(url_for('dashboard'))

    return render_template('update_account.html', form = form)

@app.route('/settings/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = forms.ChangePasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            old_password = form.old_password.data
            new_password = form.new_password.data
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE user_id = %s", (current_user.id,))
            user = cur.fetchone()
            cur.close()
            
            if not user:
                flash('User not found. Please login again.')
                return redirect(url_for('login'))
            
            if not check_password_hash(user['password'], old_password):
                flash('Incorrect password. Please try again.')
                return redirect(url_for('change_password'))
            
            hashed_password = generate_password_hash(new_password)
            
            logic.update_user(user_id=current_user.id, password=hashed_password)
            flash('Password changed successfully.')
        
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html', form = form)

@app.route('/settings/reset-password', methods=['GET', 'POST'])
def reset_password():
    form = forms.ResetPasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
        
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE user_id = %s AND email = %s", (current_user.id, email))
            user = cur.fetchone()
            cur.close()
            
            if not user:
                flash('User not found. Please login again.')
                return redirect(url_for('login'))
            
            if form.validate_on_submit():
                new_password = form.new_password.data
                
            hashed_password = generate_password_hash(new_password)
            
            logic.update_user(user_id=current_user.id, password=hashed_password)
            flash('Password reset successfully.')
        
        return redirect(url_for('dashboard'))
    
    return render_template('reset_password.html', form = form)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')

@app.route('/settings/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = forms.DeleteUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE user_id = %s AND email = %s", (current_user.id, email))
            user = cur.fetchone()
            cur.close()
            
            if not user:
                flash('User not found. Please login again.')
                return redirect(url_for('login'))
            
            if not check_password_hash(user['password'], password):
                flash('Incorrect password. Please try again.')
                
            logic.delete_user(user_id=current_user.id)
            flash('Account deleted successfully.')
        
        return redirect(url_for('index'))
    
    return render_template('delete_account.html', form = form)
                      

@app.route('/admin/add-update-car', methods=['GET', 'POST'])
@login_required
def admin_add_update_car():
    if not current_user.is_admin:
        flash('Access denied. Admins only.')
        return redirect(url_for('index'))
    
    form = forms.CarDataForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            car_brand = form.car_brand.data
            car_model = form.car_model.data
            car_part = form.car_part.data
            car_part_price = form.car_part_price.data
            
            car_brand = car_brand.upper()
            car_model = car_model.capitalize()

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO car_data (brand, model, part, price) VALUES (%s, %s, %s, %s) ON DUPLICATE VALUES UPDATE price = %s",
                        (car_brand, car_model, car_part, car_part_price, car_part_price))
            mysql.connection.commit()
            cur.close()
            
            flash('Car data added/updated successfully.')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_add_update_car.html', form = form)

@app.route('/admin/view-users', methods=['GET'])
@login_required
def admin_view_users():
    if not current_user.is_admin:
        flash('Access denied. Admins only.')
        return redirect(url_for('index'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_data")
    users = cur.fetchall()
    cur.close()
    
    users = pd.DataFrame(users, columns= "user_id name email password phone_number address city state zipcode country registration_date car_brand car_model is_admin profile_pic".split())

    return render_template('admin_view_users.html', users=users)

@app.route('/admin/view-car-data', methods=['GET'])
@login_required
def admin_view_car_data():
    if not current_user.is_admin:
        flash('Access denied. Admins only.')
        return redirect(url_for('index'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM car_data")
    car_data = cur.fetchall()
    cur.close()
    
    car_data = pd.DataFrame(car_data, columns="id brand model part price".split())
    
    return render_template('admin_view_car_data.html', car_data=car_data)

@app.route('/admin/view-messages', methods=['GET'])
@login_required
def admin_view_messages():
    if not current_user.is_admin:
        flash('Access denied. Admins only.')
        return redirect(url_for('index'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM message")
    messages = cur.fetchall()
    cur.close()
    
    messages = pd.DataFrame(messages, columns="id name email subject message date".split())
    
    return render_template('admin_view_messages.html', messages=messages)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
