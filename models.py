from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from flask_login import LoginManager

# Create database connection object
db = SQLAlchemy()
login = LoginManager()

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    second_name = db.Column(db.String(30))
    short_name = db.Column(db.String(3))
    steam_id = db.Column(db.Integer(), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    event_registrations = db.relationship('Event_Registration', backref='user_br', lazy=True)
    event_results = db.relationship('Event_Results', backref='user_results_br', lazy=True)
 
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    udp_port = db.Column(db.Integer, nullable=False)
    tcp_port = db.Column(db.Integer, nullable=False)
    max_connections = db.Column(db.Integer, nullable=False)
    register_to_lobby = db.Column(db.Boolean, default=True)
    lan_discovery = db.Column(db.Boolean, default=False)
    server_name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    admin_password = db.Column(db.String(255), nullable=False)
    spectator_password = db.Column(db.String(255), nullable=False)
    track_medal_requirement = db.Column(db.Integer, nullable=False)
    safety_rating_requirement = db.Column(db.Integer, nullable=False)
    racecract_rating_requirement = db.Column(db.Integer, nullable=False)
    dump_leaderboards = db.Column(db.Boolean, default=False)
    is_race_locked = db.Column(db.Boolean, default=False)
    randomize_track_when_empty = db.Column(db.Boolean, default=False)
    max_car_slots = db.Column(db.Integer, nullable=False)
    central_entry_list_path = db.Column(db.String(255), nullable=False)
    short_formation_lap = db.Column(db.Boolean, default=False)
    allow_auto_dq = db.Column(db.Boolean, default=False)
    dump_entry_list = db.Column(db.Boolean, default=False)
    formation_lap_type = db.Column(db.Integer, nullable=False)
    car_group = db.Column(db.String(255), nullable=False)
    track = db.Column(db.String(255), nullable=False)
    pre_race_waiting_time_seconds = db.Column(db.Integer, nullable=False)
    session_over_time_seconds = db.Column(db.Integer, nullable=False)
    ambient_temperature = db.Column(db.Integer, nullable=False)
    cloud_level = db.Column(db.Float, nullable=False)
    rain = db.Column(db.Float, nullable=False)
    weather_randomness = db.Column(db.Integer, nullable=False)
    post_qualy_seconds = db.Column(db.Integer, nullable=False)
    post_race_seconds = db.Column(db.Integer, nullable=False)
    practice_hour_of_day = db.Column(db.Integer, nullable=False)
    practice_day_of_weekend = db.Column(db.Integer, nullable=False)
    practice_time_multiplier = db.Column(db.Integer, nullable=False)
    practice_session_duration = db.Column(db.Integer, nullable=False)
    qualy_hour_of_day = db.Column(db.Integer, nullable=False)
    qualy_day_of_weekend = db.Column(db.Integer, nullable=False)
    qualy_time_multiplier = db.Column(db.Integer, nullable=False)
    qualy_session_duration = db.Column(db.Integer, nullable=False)
    race_hour_of_day = db.Column(db.Integer, nullable=False)
    race_day_of_weekend = db.Column(db.Integer, nullable=False)
    race_time_multiplier = db.Column(db.Integer, nullable=False)
    race_session_duration = db.Column(db.Integer, nullable=False)
    qualifying_stand_type = db.Column(db.Integer, nullable=False)
    pit_window_length = db.Column(db.Integer, nullable=False)
    driver_stint_time = db.Column(db.Integer, nullable=False)
    mandatory_pitstop_count = db.Column(db.Integer, nullable=False)
    max_total_driving_time = db.Column(db.Integer, nullable=False)
    max_drivers_count = db.Column(db.Integer, nullable=False)
    tyre_set_count = db.Column(db.Integer, nullable=False)
    is_refuelling_allowed_in_race = db.Column(db.Boolean, default=False)
    is_refuelling_time_fixed = db.Column(db.Boolean, default=False)
    is_mandatory_pitstop_refuelling_required = db.Column(db.Boolean, default=False)
    is_mandatory_pitstop_tyre_changed_required = db.Column(db.Boolean, default=False)
    is_mandatory_pitstop_swap_driver_required = db.Column(db.Boolean, default=False)
    stability_control_level_max = db.Column(db.Integer, nullable=False)
    disable_autosteer = db.Column(db.Boolean, default=False)
    disable_auto_lights = db.Column(db.Boolean, default=False)
    disable_auto_wiper = db.Column(db.Boolean, default=False)
    disable_auto_engine_start = db.Column(db.Boolean, default=False)
    disable_auto_pit_limiter = db.Column(db.Boolean, default=False)
    disable_auto_gear = db.Column(db.Boolean, default=False)
    disable_auto_clutch = db.Column(db.Boolean, default=False)
    disable_ideal_line = db.Column(db.Boolean, default=False)
    server_start_time = db.Column(db.DateTime)
    pid = db.Column(db.Integer, nullable=True)
    event_registrations = db.relationship('Event_Registration', backref='event_br', lazy=True)
    event_stats = db.relationship('Event_Stats', backref='event_stats_br', lazy=True)
    event_results = db.relationship('Event_Results', backref='event_results_br', lazy=True)

class Event_Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Event_Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    session_type = db.Column(db.String(3), nullable=False)
    best_lap = db.Column(db.Integer, nullable=False)
    best_sector_one = db.Column(db.Integer, nullable=False)
    best_sector_two = db.Column(db.Integer, nullable=False)
    best_sector_three = db.Column(db.Integer, nullable=False)

class Event_Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    session_type = db.Column(db.String(3), nullable=False)
    finish_position = db.Column(db.Integer, nullable=False)
    car_model = db.Column(db.Integer, db.ForeignKey('car__models.model_id'), nullable=False)
    best_lap = db.Column(db.Integer, nullable=False)
    best_sector_one = db.Column(db.Integer, nullable=False)
    best_sector_two = db.Column(db.Integer, nullable=False)
    best_sector_three = db.Column(db.Integer, nullable=False)
    total_time = db.Column(db.Integer, nullable=False)
    lap_count = db.Column(db.Integer, nullable=False)

class Car_Models(db.Model):
    model_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255), nullable=False)
    model_year = db.Column(db.Integer, nullable=False)
    model_class = db.Column(db.String(10), nullable=False)
    car_results = db.relationship('Event_Results', backref='car_model_br', lazy=True)

