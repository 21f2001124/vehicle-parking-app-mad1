from application.database import db
from .database import db  # .takes file from the same folder as we are in


#this is the table for user
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    pwd = db.Column(db.String(100), nullable=False)
    adress = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    #default is the user...so in the website no option for admin
    type = db.Column(db.String(20), nullable=False, default="user")

    #relationship to reservations of parking spot
    reservations = db.relationship('ReserveParkingSpot', backref='user', lazy=True)

# table for parkinglot
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

# table for parking spot
class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    spot_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), nullable=False)  # 'A' or 'O'
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.lot_id'), nullable=False)

    # Relationship to reservations
    reservations = db.relationship('ReserveParkingSpot', backref='spot', lazy=True)

#table for reserve parking spot 
class ReserveParkingSpot(db.Model):
    __tablename__ = 'reserve_parking_spot'
    res_spot_id = db.Column(db.Integer, primary_key=True)

    # these are the associations 
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.spot_id'), nullable=False)
    vehicle_no = db.Column(db.String(20), nullable=False) #this is vehicle detail
    #these denote the timing column of the table
    parking_time = db.Column(db.DateTime, nullable=False)
    leaving_time = db.Column(db.DateTime, nullable=True)
    #this is the prices
    parking_cost_unit_time = db.Column(db.Integer, nullable=False)

    



    
    