from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from datetime import datetime
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CreateAssetForm, CreateAssetUpdateForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Asset, Asset_Update



@app.route('/')
@app.route('/index')
@login_required
def index():
    assets = Asset.query.all()
    asset_updates = Asset_Update.query.all().order_by(Asset_Update.timestamp)
    return render_template('index.html', title='Home', assets=assets, asset_updates=asset_updates)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/asset/<asset_name>')
@login_required
def asset(asset_name):
    asset = Asset.query.filter_by(asset_name=asset_name).first_or_404()
    asset_updates = [
        {'author': "Phil", 'body': 'Test asset update #1'},
        {'author': "Phil", 'body': 'Test asset update #2'}
    ]
    return render_template('asset.html', asset=asset, asset_updates=asset_updates)

@app.route('/create_asset', methods=['GET', 'POST'])
def create_asset():
    # if current_user!=1:
    #     return redirect(url_for('index'))
    form = CreateAssetForm()
    if form.validate_on_submit():
        asset = Asset(asset_name=form.asset_name.data, asset_thesis=form.asset_thesis.data, asset_type=form.asset_thesis.data, asset_class=form.asset_class.data)
        db.session.add(asset)
        db.session.commit()
        flash('Congratulations, you have just created a new asset!')
        return redirect(url_for('create_asset'))
    return render_template('create_asset.html', title='Create Asset', form=form)



@app.route('/create_asset_update', methods=['GET', 'POST'])
def create_asset_update():
    # if current_user!=1:
    #     return redirect(url_for('index'))
    available_assets = db.session.query(Asset).all()
    assets_list = [(i.id, i.asset_name) for i in available_assets]
    form = CreateAssetUpdateForm()
    form.asset.choices = assets_list
    if form.validate_on_submit():
        asset_update = Asset_Update(asset=form.asset.data, asset_update_title=form.asset_update_title.data, asset_update_content=form.asset_update_content.data)
        db.session.add(asset_update)
        db.session.commit()
        flash('Congratulations, you have just created a new asset update!')
        return redirect(url_for('create_asset_update'))
    return render_template('create_asset_update.html', title='Create Asset Update', form=form)