from flask import Flask, render_template, request, redirect, url_for
from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user, login_user, logout_user, roles_required
from flask_security.utils import hash_password
from models import db, User, Role, Event, Event_Registration
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, BooleanField, DecimalField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, InputRequired
from flask import abort
import datetime
import json_creator
from distutils.dir_util import copy_tree, remove_tree
from pathlib import Path
import os
import subprocess
import psutil

# Create app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECURITY_PASSWORD_SALT'] = 'super-salt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_POST_LOGIN_VIEW'] = '/account'

db.init_app(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    # user_datastore.create_role(name='admin',description='Ultimate user')
    # user_datastore.create_user(first_name='Peter', 
    #                         second_name='Cosgrave',
    #                         short_name='COS', 
    #                         steam_id=12345678901234567, 
    #                         email='peter.cosgrave.1@gmail.com', 
    #                         password=hash_password('testing1'),
    #                         active=1)
    # db.session.commit()

# Views
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/account/', methods=['POST', 'GET'])
@login_required
def account():
    user = User.query.filter_by(id = current_user.id).first()
    form = UpdateForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return render_template('account.html', form=form, value='Profile updated successfully')
    return render_template('account.html', form=form)

# @app.route('/login/', methods = ['POST', 'GET'])
# def login():
#     if current_user.is_authenticated:
#         return redirect('/account')
    
#     form = LoginForm()
#     # if form.validate_on_submit():
#     #     email = form.email.data
#     #     user = User.query.filter_by(email = email).first()
#     #     if user is not None and user.check_password(form.password.data):
#     #         login_user(user)
#     #         return redirect('/account')
#     #     else: 
#     #         return render_template('login.html', form=form, value='Incorrect email or password')
     
#     return render_template('login.html', form=form)
 
@app.route('/register/', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/account')
        
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.first_name.data
        surname = form.second_name.data
        short_name = form.short_name.data
        steam_id = form.steam_id.data
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(email=email).first():
            return render_template('register.html', form=form, value='User with this email already exists')
        if User.query.filter_by(steam_id=steam_id).first():
            return render_template('register.html', form=form, value='User with this steam id already exists')
        user_datastore.create_user(first_name=name, 
                            second_name=surname,
                            short_name=short_name, 
                            steam_id=steam_id, 
                            email=email, 
                            password=hash_password(password),
                            active=1)
        db.session.commit()
        user = User.query.filter_by(email = email).first()
        login_user(user)
        return redirect('/account')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()

@app.route('/events/')
def events():
    events = Event.query.all()
    event_registrations = Event_Registration.query.all()
    return render_template('events.html', events=events, event_registrations=event_registrations)

@app.route('/view-event/', methods=['GET'])
def view_event():
    event_id = request.args.get('id')
    event = Event.query.filter_by(id=event_id).first()
    event_registrations = Event_Registration.query.filter_by(event_id=event_id).all()
    if not event:
        abort(404)
    if current_user.is_authenticated:
        if Event_Registration.query.filter_by(event_id=event_id, user_id=current_user.id).first():
            return render_template('view-event-logged-in.html', event=event, event_registrations=event_registrations)
        else:
            return render_template('view-event-unregistered.html', event=event, event_registrations=event_registrations)
    return render_template('view-event-logged-out.html', event=event, event_registrations=event_registrations)

@app.route('/edit-event/', methods=['POST', 'GET'])
@login_required
@roles_required('Admin')
def edit_event():
    event_id = request.args.get('id')
    event = Event.query.filter_by(id=event_id).first()
    old_event_time = event.server_start_time.strftime("%d%m%Y%H%M")
    if not event:
        abort(404)
    form = UpdateEventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        updated_event = Event.query.filter_by(id=event_id).first()
        server_folder = updated_event.server_start_time.strftime("%d%m%Y%H%M")
        try:
            remove_tree('servers/'+old_event_time)
        except:
            print('No previous server config found, continuing...')
        fromDirectory = 'Assetto Corsa Competizione Dedicated Server/server'
        toDirectory = 'servers/'+server_folder
        copy_tree(fromDirectory, toDirectory)
        event_registrations = Event_Registration.query.filter_by(event_id=event.id).all()
        json_creator.create_configuration_json_file(event.udp_port, event.tcp_port, event.max_connections, event.register_to_lobby, event.lan_discovery, server_folder)
        json_creator.create_settings_json_file(event.server_name, event.password, event.admin_password, event.spectator_password, event.track_medal_requirement, 
                                                event.safety_rating_requirement, event.racecract_rating_requirement,
                                                event.dump_leaderboards, event.is_race_locked, event.randomize_track_when_empty,
                                                event.max_car_slots, event.central_entry_list_path, event.short_formation_lap,
                                                event.allow_auto_dq, event.dump_entry_list, event.formation_lap_type,
                                                event.car_group, server_folder)
        json_creator.create_event_json_file(event.track, event.pre_race_waiting_time_seconds, event.session_over_time_seconds,
                                            event.ambient_temperature, event.cloud_level, event.rain, event.weather_randomness,
                                            event.practice_hour_of_day, event.practice_day_of_weekend, event.practice_time_multiplier,
                                            event.practice_session_duration,event.qualy_hour_of_day, event.qualy_day_of_weekend,
                                            event.qualy_time_multiplier, event.qualy_session_duration, event.race_hour_of_day, 
                                            event.race_day_of_weekend, event.race_time_multiplier, event.race_session_duration,
                                            event.post_qualy_seconds, event.post_race_seconds, server_folder)
        json_creator.create_event_rules_json_file(event.qualifying_stand_type, event.pit_window_length, event.driver_stint_time,
                                                event.mandatory_pitstop_count, event.max_total_driving_time, event.max_drivers_count,
                                                event.is_refuelling_allowed_in_race, event.is_refuelling_time_fixed,
                                                event.is_mandatory_pitstop_refuelling_required, event.is_mandatory_pitstop_tyre_changed_required,
                                                event.is_mandatory_pitstop_swap_driver_required, event.tyre_set_count, server_folder)
        json_creator.create_assist_rules_json_file(event.stability_control_level_max, event.disable_autosteer,
                                                    event.disable_auto_lights, event.disable_auto_wiper, event.disable_auto_engine_start,
                                                    event.disable_auto_pit_limiter, event.disable_auto_gear, event.disable_auto_clutch,
                                                    event.disable_ideal_line, server_folder)
        json_creator.create_entry_list_json_file(event_registrations, server_folder)
        return render_template('edit-event.html', form=form, value='Event updated successfully')
    return render_template('edit-event.html', form=form)

@app.route('/add-event/', methods=['POST', 'GET'])
@login_required
@roles_required('Admin')
def add_event():
    form = UpdateEventForm()
    if form.validate_on_submit():
        udp_port = form.udp_port.data
        tcp_port = form.tcp_port.data
        max_connections = form.max_connections.data
        register_to_lobby = form.register_to_lobby.data
        lan_discovery = form.lan_discovery.data
        server_name = form.server_name.data
        password = form.password.data
        admin_password = form.admin_password.data
        spectator_password = form.spectator_password.data
        track_medal_requirement = form.track_medal_requirement.data
        safety_rating_requirement = form.safety_rating_requirement.data
        racecract_rating_requirement = form.racecract_rating_requirement.data
        dump_leaderboards = form.dump_leaderboards.data
        is_race_locked = form.is_race_locked.data
        randomize_track_when_empty = form.randomize_track_when_empty.data
        max_car_slots = form.max_car_slots.data
        central_entry_list_path = form.central_entry_list_path.data
        short_formation_lap = form.short_formation_lap.data
        allow_auto_dq = form.allow_auto_dq.data
        dump_entry_list = form.dump_entry_list.data
        formation_lap_type = form.formation_lap_type.data
        car_group = form.car_group.data
        track = form.track.data
        pre_race_waiting_time_seconds = form.pre_race_waiting_time_seconds.data
        session_over_time_seconds = form.session_over_time_seconds.data
        ambient_temperature = form.ambient_temperature.data
        cloud_level = form.cloud_level.data
        rain = form.rain.data
        weather_randomness = form.weather_randomness.data
        post_qualy_seconds = form.post_qualy_seconds.data
        post_race_seconds = form.post_race_seconds.data
        practice_hour_of_day = form.practice_hour_of_day.data
        practice_day_of_weekend = form.practice_day_of_weekend.data
        practice_time_multiplier = form.practice_time_multiplier.data
        practice_session_duration = form.practice_session_duration.data
        qualy_hour_of_day = form.qualy_hour_of_day.data
        qualy_day_of_weekend = form.qualy_day_of_weekend.data
        qualy_time_multiplier = form.qualy_time_multiplier.data
        qualy_session_duration = form.qualy_session_duration.data
        race_hour_of_day = form.race_hour_of_day.data
        race_day_of_weekend = form.race_day_of_weekend.data
        race_time_multiplier = form.race_time_multiplier.data
        race_session_duration = form.race_session_duration.data
        qualifying_stand_type = form.qualifying_stand_type.data
        pit_window_length = form.pit_window_length.data
        driver_stint_time = form.driver_stint_time.data
        mandatory_pitstop_count = form.mandatory_pitstop_count.data
        max_total_driving_time = form.max_total_driving_time.data
        max_drivers_count = form.max_drivers_count.data
        tyre_set_count = form.tyre_set_count.data
        is_refuelling_allowed_in_race = form.is_refuelling_allowed_in_race.data
        is_refuelling_time_fixed = form.is_refuelling_time_fixed.data
        is_mandatory_pitstop_refuelling_required = form.is_mandatory_pitstop_refuelling_required.data
        is_mandatory_pitstop_tyre_changed_required = form.is_mandatory_pitstop_tyre_changed_required.data
        is_mandatory_pitstop_swap_driver_required = form.is_mandatory_pitstop_swap_driver_required.data
        stability_control_level_max = form.stability_control_level_max.data
        disable_autosteer = form.disable_autosteer.data
        disable_auto_lights = form.disable_auto_lights.data
        disable_auto_wiper = form.disable_auto_wiper.data
        disable_auto_engine_start = form.disable_auto_engine_start.data
        disable_auto_pit_limiter = form.disable_auto_pit_limiter.data
        disable_auto_gear = form.disable_auto_gear.data
        disable_auto_clutch = form.disable_auto_clutch.data
        disable_ideal_line = form.disable_ideal_line.data
        server_start_time = form.server_start_time.data
        new_event = Event(udp_port=udp_port, tcp_port=tcp_port, max_connections=max_connections, 
                        register_to_lobby=register_to_lobby, lan_discovery=lan_discovery, server_name=server_name,
                        password=password, admin_password=admin_password, spectator_password=spectator_password,
                        track_medal_requirement=track_medal_requirement, safety_rating_requirement=safety_rating_requirement,
                        racecract_rating_requirement=racecract_rating_requirement, dump_leaderboards=dump_leaderboards,
                        is_race_locked=is_race_locked, randomize_track_when_empty=randomize_track_when_empty, max_car_slots=max_car_slots,
                        central_entry_list_path=central_entry_list_path, short_formation_lap=short_formation_lap, allow_auto_dq=allow_auto_dq,
                        dump_entry_list=dump_entry_list, formation_lap_type=formation_lap_type, car_group=car_group,
                        track=track, pre_race_waiting_time_seconds=pre_race_waiting_time_seconds, session_over_time_seconds=session_over_time_seconds,
                        ambient_temperature=ambient_temperature, cloud_level=cloud_level, rain=rain, weather_randomness=weather_randomness,
                        post_qualy_seconds=post_qualy_seconds, post_race_seconds=post_race_seconds, practice_hour_of_day=practice_hour_of_day,
                        practice_day_of_weekend=practice_day_of_weekend, practice_time_multiplier=practice_time_multiplier, practice_session_duration=practice_session_duration,
                        qualy_hour_of_day=qualy_hour_of_day, qualy_day_of_weekend=qualy_day_of_weekend, qualy_time_multiplier=qualy_time_multiplier,
                        qualy_session_duration=qualy_session_duration, race_hour_of_day=race_hour_of_day, race_day_of_weekend=race_day_of_weekend,
                        race_time_multiplier=race_time_multiplier, race_session_duration=race_session_duration,
                        qualifying_stand_type=qualifying_stand_type, pit_window_length=pit_window_length, driver_stint_time=driver_stint_time,
                        mandatory_pitstop_count=mandatory_pitstop_count, max_total_driving_time=max_total_driving_time, max_drivers_count=max_drivers_count,
                        tyre_set_count=tyre_set_count, is_refuelling_allowed_in_race=is_refuelling_allowed_in_race, is_refuelling_time_fixed=is_refuelling_time_fixed,
                        is_mandatory_pitstop_refuelling_required=is_mandatory_pitstop_refuelling_required, is_mandatory_pitstop_tyre_changed_required=is_mandatory_pitstop_tyre_changed_required,
                        is_mandatory_pitstop_swap_driver_required=is_mandatory_pitstop_swap_driver_required,
                        stability_control_level_max=stability_control_level_max, disable_autosteer=disable_autosteer,
                        disable_auto_lights=disable_auto_lights, disable_auto_wiper=disable_auto_wiper, disable_auto_engine_start=disable_auto_engine_start,
                        disable_auto_pit_limiter=disable_auto_pit_limiter, disable_auto_gear=disable_auto_gear, disable_auto_clutch=disable_auto_clutch,
                        disable_ideal_line=disable_ideal_line, server_start_time=server_start_time)
        db.session.add(new_event)
        db.session.commit()
        server_folder = server_start_time.strftime("%d%m%Y%H%M")
        fromDirectory = 'Assetto Corsa Competizione Dedicated Server/server'
        toDirectory = 'servers/'+server_folder
        copy_tree(fromDirectory, toDirectory)
        event = Event.query.filter_by(id=new_event.id).first()
        event_registrations = Event_Registration.query.filter_by(event_id=event.id).all()
        json_creator.create_configuration_json_file(event.udp_port, event.tcp_port, event.max_connections, event.register_to_lobby, event.lan_discovery, server_folder)
        json_creator.create_settings_json_file(event.server_name, event.password, event.admin_password, event.spectator_password, event.track_medal_requirement, 
                                                event.safety_rating_requirement, event.racecract_rating_requirement,
                                                event.dump_leaderboards, event.is_race_locked, event.randomize_track_when_empty,
                                                event.max_car_slots, event.central_entry_list_path, event.short_formation_lap,
                                                event.allow_auto_dq, event.dump_entry_list, event.formation_lap_type,
                                                event.car_group, server_folder)
        json_creator.create_event_json_file(event.track, event.pre_race_waiting_time_seconds, event.session_over_time_seconds,
                                            event.ambient_temperature, event.cloud_level, event.rain, event.weather_randomness,
                                            event.practice_hour_of_day, event.practice_day_of_weekend, event.practice_time_multiplier,
                                            event.practice_session_duration,event.qualy_hour_of_day, event.qualy_day_of_weekend,
                                            event.qualy_time_multiplier, event.qualy_session_duration, event.race_hour_of_day, 
                                            event.race_day_of_weekend, event.race_time_multiplier, event.race_session_duration,
                                            event.post_qualy_seconds, event.post_race_seconds, server_folder)
        json_creator.create_event_rules_json_file(event.qualifying_stand_type, event.pit_window_length, event.driver_stint_time,
                                                event.mandatory_pitstop_count, event.max_total_driving_time, event.max_drivers_count,
                                                event.is_refuelling_allowed_in_race, event.is_refuelling_time_fixed,
                                                event.is_mandatory_pitstop_refuelling_required, event.is_mandatory_pitstop_tyre_changed_required,
                                                event.is_mandatory_pitstop_swap_driver_required, event.tyre_set_count, server_folder)
        json_creator.create_assist_rules_json_file(event.stability_control_level_max, event.disable_autosteer,
                                                    event.disable_auto_lights, event.disable_auto_wiper, event.disable_auto_engine_start,
                                                    event.disable_auto_pit_limiter, event.disable_auto_gear, event.disable_auto_clutch,
                                                    event.disable_ideal_line, server_folder)
        json_creator.create_entry_list_json_file(event_registrations, server_folder)
        return render_template('add-event.html', form=form, value='Event added successfully')
    print(form.errors.items())
    return render_template('add-event.html', form=form)

@app.route('/register-for-event/', methods=['POST', 'GET'])
@login_required
def register_for_event():
    event_id = request.args.get('id')
    event = Event.query.filter_by(id=event_id).first()
    user = User.query.filter_by(id = current_user.id).first()
    if current_user.is_authenticated and not Event_Registration.query.filter_by(event_id=event_id, user_id=current_user.id).first():
        registration = Event_Registration(event_br=event, user_br=user)
        db.session.add(registration)
        db.session.commit()
        server_folder = event.server_start_time.strftime("%d%m%Y%H%M")
        file_path = Path(os.getcwd()+'/servers/'+server_folder+'/cfg/entryList.json')
        try:
            file_path.unlink()
        except OSError as e:
            print("Error: %s : %s" % (file_path, e.strerror))
        event_registrations = Event_Registration.query.filter_by(event_id=event.id).all()
        json_creator.create_entry_list_json_file(event_registrations, server_folder)
        return redirect(url_for('view_event', id=event_id))
    else:
        return redirect(url_for('view_event', id=event_id))

@app.route('/unregister-for-event/', methods=['POST', 'GET'])
@login_required
def unregister_for_event():
    event_id = request.args.get('id')
    if current_user.is_authenticated and Event_Registration.query.filter_by(event_id=event_id, user_id=current_user.id).first():
        Event_Registration.query.filter_by(event_id=event_id, user_id=current_user.id).delete()
        db.session.commit()
        event = Event.query.filter_by(id=event_id).first()
        server_folder = event.server_start_time.strftime("%d%m%Y%H%M")
        file_path = Path(os.getcwd()+'/servers/'+server_folder+'/cfg/entryList.json')
        try:
            file_path.unlink()
        except OSError as e:
            print("Error: %s : %s" % (file_path, e.strerror))
        event_registrations = Event_Registration.query.filter_by(event_id=event.id).all()
        json_creator.create_entry_list_json_file(event_registrations, server_folder)
        return redirect(url_for('view_event', id=event_id))
    else:
        return redirect(url_for('view_event', id=event_id))

@app.route('/start-server/', methods=['POST', 'GET'])
@login_required
@roles_required('Admin')
def start_server():
    event_type = request.args.get('event_type')
    if event_type == 'hourly':
        time_now = datetime.datetime.now()
        formatted_time_now = time_now.strftime("%d%m%Y%H00")
        current_directory = r"C:\Users\peter\Documents\acc-community-website\servers\\"+formatted_time_now
        exe_file = r"C:\Users\peter\Documents\acc-community-website\servers\\"+formatted_time_now+r"\\accServer.exe"
        game_server = subprocess.Popen(args=exe_file, cwd=current_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        event = Event.query.filter_by(server_start_time=time_now.strftime('%Y-%m-%d %H:00:00.000000')).first()
        event.pid=game_server.pid
        db.session.commit()
        return 'Server Started: ' + str(game_server.pid)
    else:
        return 'No event of this type to start'

@app.route('/stop-server/', methods=['POST', 'GET'])
@login_required
@roles_required('Admin')
def stop_server():
    event_type = request.args.get('event_type')
    if event_type == 'hourly':
        time_now = datetime.datetime.now()
        formatted_time_now = time_now.strftime("%d%m%Y%H00")
        event = Event.query.filter_by(server_start_time=time_now.strftime('%Y-%m-%d %H:00:00.000000')).first()
        p = psutil.Process(int(event.pid))
        p.terminate()
        event.pid = 0
        db.session.commit()
        return 'Server Stopped'
    else:
        return 'No event of this type to stop'

# Forms 
class RegistrationForm(FlaskForm):
    first_name = StringField(label=('Name'), validators=[DataRequired(), Length(max=30)])
    second_name = StringField(label=('Surname'), validators=[DataRequired(), Length(max=30)])
    short_name = StringField(label=('Short Name'), validators=[DataRequired(), Length(min=3, max=3, message='Short Name must be %(min)d characters')])
    steam_id = StringField(label=('Steam ID'), validators=[DataRequired(), Length(min=17, max=17, message='Steam ID must be %(min)d characters')])
    email = StringField(label=('Email'), validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(label=('Password'), validators=[DataRequired(), Length(min=8, message='Password should be at least %(min)d characters long')])
    submit = SubmitField(label=('Submit'))

class UpdateForm(FlaskForm):
    first_name = StringField(label=('Name'), validators=[DataRequired(), Length(max=30)])
    second_name = StringField(label=('Surname'), validators=[DataRequired(), Length(max=30)])
    short_name = StringField(label=('Short Name'), validators=[DataRequired(), Length(min=3, max=3, message='Short Name must be %(min)d characters')])
    steam_id = StringField(label=('Steam ID'), validators=[DataRequired(), Length(min=17, max=17, message='Steam ID must be %(min)d characters')])
    email = StringField(label=('Email'), validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField(label=('Submit'))

class UpdateEventForm(FlaskForm):
    # configuration.json settings
    udp_port = IntegerField(label=('UDP Port'), validators=[DataRequired()])
    tcp_port = IntegerField(label=('TCP Port'), validators=[DataRequired()])
    max_connections = IntegerField(label=('Max Connections'), validators=[DataRequired()])
    register_to_lobby = BooleanField(label=('Register to Lobby'))
    lan_discovery = BooleanField(label=('Lan Discovery'))
    # setings.json settings
    server_name = StringField(label=('Server Name'), validators=[DataRequired(), Length(max=255)])
    password = StringField(label=('Password'), validators=[DataRequired(), Length(max=255)])
    admin_password = StringField(label=('Admin Password'), validators=[DataRequired(), Length(max=255)])
    spectator_password = StringField(label=('Spectator Password'), validators=[DataRequired(), Length(max=255)])
    track_medal_requirement = IntegerField(label=('Track Medals Requirement'), validators=[DataRequired()])
    safety_rating_requirement = IntegerField(label=('Safety Rating Requirement'), validators=[DataRequired()])
    racecract_rating_requirement = IntegerField(label=('Racecract Rating Requirement'), validators=[DataRequired()])
    dump_leaderboards = BooleanField(label=('Dump Leaderboards'))
    is_race_locked = BooleanField(label=('Is Race Locked'))
    randomize_track_when_empty = BooleanField(label=('Randomize Track When Empty'))
    max_car_slots = IntegerField(label=('Max Car Slots'), validators=[DataRequired()])
    central_entry_list_path = StringField(label=('Path To Entry List'), validators=[Length(max=255)])
    short_formation_lap = BooleanField(label=('Short Formation Lap'))
    allow_auto_dq = BooleanField(label=('Allow Auto DQ'))
    dump_entry_list = BooleanField(label=('Dump Entry List'))
    formation_lap_type = IntegerField(label=('Formation Lap Type'), validators=[DataRequired()])
    car_group = StringField(label=('Car Group'), validators=[DataRequired(), Length(max=255)])
    # event.json
    track = StringField(label=('Track'), validators=[DataRequired(), Length(max=255)])
    pre_race_waiting_time_seconds = IntegerField(label=('Pre-Race Waiting Time Seconds'), validators=[DataRequired()])
    session_over_time_seconds = IntegerField(label=('Session Over Time Seconds'), validators=[DataRequired()])
    ambient_temperature = IntegerField(label=('Ambient Temperature'), validators=[DataRequired()])
    cloud_level = DecimalField(label=('Cloud Level'), validators=[InputRequired()])
    rain = DecimalField(label=('Rain'), validators=[InputRequired()])
    weather_randomness = IntegerField(label=('Weather Randomness'), validators=[DataRequired()])
    post_qualy_seconds = IntegerField(label=('Post Qualy Seconds'), validators=[DataRequired()])
    post_race_seconds = IntegerField(label=('Post Race Seconds'), validators=[DataRequired()])
    practice_hour_of_day = IntegerField(label=('Practice Hour of Day'), validators=[DataRequired()])
    practice_day_of_weekend = IntegerField(label=('Practice Day of Weekend'), validators=[DataRequired()])
    practice_time_multiplier = IntegerField(label=('Practice Time Multiplier'), validators=[DataRequired()])
    practice_session_duration = IntegerField(label=('Practice Session Duration'), validators=[DataRequired()])
    qualy_hour_of_day = IntegerField(label=('Qualy Hour of Day'), validators=[DataRequired()])
    qualy_day_of_weekend = IntegerField(label=('Qualy Day of Weekend'), validators=[DataRequired()])
    qualy_time_multiplier = IntegerField(label=('Qualy Time Multiplier'), validators=[DataRequired()])
    qualy_session_duration = IntegerField(label=('Qualy Session Duration'), validators=[DataRequired()])
    race_hour_of_day = IntegerField(label=('Race Hour of Day'), validators=[DataRequired()])
    race_day_of_weekend = IntegerField(label=('Race Day of Weekend'), validators=[DataRequired()])
    race_time_multiplier = IntegerField(label=('Race Time Multiplier'), validators=[DataRequired()])
    race_session_duration = IntegerField(label=('Race Session Duration'), validators=[DataRequired()])
    # eventRules.json
    qualifying_stand_type = IntegerField(label=('Qualifying Stand Type'), validators=[DataRequired()])
    pit_window_length = IntegerField(label=('Pit Window Length'), validators=[DataRequired()])
    driver_stint_time = IntegerField(label=('Driver Stint Time'), validators=[DataRequired()])
    mandatory_pitstop_count = IntegerField(label=('Mandatory Pitstop Count'), validators=[InputRequired()])
    max_total_driving_time = IntegerField(label=('Max Total Driving Time'), validators=[DataRequired()])
    max_drivers_count = IntegerField(label=('Max Drivers Count'), validators=[DataRequired()])
    tyre_set_count = IntegerField(label=('Tyre Set Count'), validators=[InputRequired()])
    is_refuelling_allowed_in_race = BooleanField(label=('Is Refuelling Allowed in Race'))
    is_refuelling_time_fixed = BooleanField(label=('Is Refuelling Time Fixed'))
    is_mandatory_pitstop_refuelling_required = BooleanField(label=('Is Mandatory Pitstop Refuelling Required'))
    is_mandatory_pitstop_tyre_changed_required = BooleanField(label=('Is Mandatory Pitstop Tyre Change Required'))
    is_mandatory_pitstop_swap_driver_required = BooleanField(label=('Is Mandatory Pitstop Swap Driver Required'))
    # assistRules.json
    stability_control_level_max = IntegerField(label=('Stability Control Level Max'), validators=[InputRequired()])
    disable_autosteer = BooleanField(label=('Disable Auto-Steer'))
    disable_auto_lights = BooleanField(label=('Diable Auto-Lights'))
    disable_auto_wiper = BooleanField(label=('Disable Auto-Wiper'))
    disable_auto_engine_start = BooleanField(label=('Disable Auto-Engine Start'))
    disable_auto_pit_limiter = BooleanField(label=('Disable Auto Pit Limiter'))
    disable_auto_gear = BooleanField(label=('Disable Auto-Gear'))
    disable_auto_clutch = BooleanField(label=('Disable Auto-Clutch'))
    disable_ideal_line = BooleanField(label=('Disable Ideal Line'))

    server_start_time = DateTimeField(label=('Server Start Time'), format='%d-%m-%Y %H:%M')
    submit = SubmitField(label=('Submit'))
if __name__ == '__main__':
    app.run()