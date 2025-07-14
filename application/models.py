from application.database import db
from .database import db  # .takes file from the same folder as we are in



class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    pwd = db.Column(db.String(100), nullable=False)
    adress = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    # "admin" or "user"
    type = db.Column(db.String(20), nullable=False, default="user")

    # Relationship to reservations
    reservations = db.relationship('ReserveParkingSpot', backref='user', lazy=True)


class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    lot_id = db.Column(db.Integer, primary_key=True)
    prime_location = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # price per hour
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)

    # One-to-many relationship to ParkingSpot
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    spot_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), nullable=False)  # 'A' or 'O'
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.lot_id'), nullable=False)

    # Relationship to reservations
    reservations = db.relationship('ReserveParkingSpot', backref='spot', lazy=True)


class ReserveParkingSpot(db.Model):
    __tablename__ = 'reserve_parking_spot'
    res_spot_id = db.Column(db.Integer, primary_key=True)

    # Associations
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.spot_id'), nullable=False)

    # Vehicle details
    vehicle_no = db.Column(db.String(20), nullable=False)

    # Timing
    parking_time = db.Column(db.DateTime, nullable=False)
    leaving_time = db.Column(db.DateTime, nullable=True)

    # Pricing
    parking_cost_unit_time = db.Column(db.Integer, nullable=False)

    



    
    