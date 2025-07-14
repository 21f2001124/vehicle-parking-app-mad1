from flask import Flask, render_template, redirect, request,  url_for
from flask import session, flash
from datetime import datetime
from sqlalchemy import func, extract

from flask import current_app  as app # breaks the circular import loop

from application.models import * 

@app.route("/")
def index():
    return render_template("Welcome.html")


@app.route("/login", methods=["GET", "POST"])  # defauls id get method
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pwd")
        thisuser = User.query.filter_by(email=email).first()
        if thisuser:
            if thisuser.pwd == password:
                # Save the user ID in session
                session["user_id"] = thisuser.user_id
                session["user_name"] = thisuser.name
                session["user_type"] = thisuser.type

                # Optional debug log
                print("DEBUG: Logged in user_id:", session["user_id"])

                flash("Login successful!", "success")
                if thisuser.type == "user":
                    return redirect(url_for("Udashboard"))
                else:
                    return redirect(url_for("Adashboard"))
            else:
                flash("Incorrect password.", "danger")
        else:
            flash("Email not found.", "danger")

    return render_template("login.html")


@app.route("/signup",methods=["GET","POST"])  #default get method
def signup():
    # print("Form hit this route")
    if request.method== "POST" :
        email= (request.form.get("email"))
        pwd= (request.form.get("pwd"))
        name= (request.form.get("name"))
        address=(request.form.get("Address"))
        pincode= (request.form.get("pincode"))
        print("hello")
        try:
            user = User(name=name, email=email, pwd=pwd, adress= address, pincode= pincode)
            db.session.add(user)         # You forgot to pass 'user' to add()
            db.session.commit()          # Commit the session to save changes
            return redirect(url_for("login"))  # Redirect after successful signup
        except Exception as e:
            db.session.rollback()        # Roll back the session if there's an error
            print(f"Error while adding user: {e}")
            return "An error occurred during signup. Please try again."

        # return "You are sign in"
    return render_template("signup.html")

#code for display data 
@app.route("/Aeditparkinglot/<int:lot_id>", methods=["GET", "POST"])
def Aeditparkinglot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == "POST":
        lot.prime_location = request.form.get("prime_location")
        lot.address = request.form.get("address")
        lot.pincode = request.form.get("pincode")
        lot.price = request.form.get("price")
        lot.max_spots = request.form.get("max_spots")

        try:
            db.session.commit()
            return redirect(url_for("Adashboard"))
        except Exception as e:
            db.session.rollback()
            return f"Error updating parking lot: {e}"

    return render_template("Aeditparkinglot.html", lot=lot)



@app.route("/Adashboard", methods=["GET"])
def Adashboard():
    lots = ParkingLot.query.all()
    return render_template("Adashboard.html", lots=lots)


@app.route("/AdashUser", methods=["GET", "POST"])
def AdashUser():
    users = User.query.filter_by(type='user').all()
    return render_template("AdashUser.html", users=users)


@app.route("/AdashSearch", methods=["GET"])
def AdashSearch():
    dropdown = request.args.get("dropdown", "")
    query = request.args.get("query", "")
    lots = []

    if dropdown and query:
        if dropdown == "location":
            q = ParkingLot.query.filter(ParkingLot.prime_location.ilike(f"%{query}%"))
        elif dropdown == "pincode":
            q = ParkingLot.query.filter(ParkingLot.pincode.ilike(f"%{query}%"))
        elif dropdown == "user_id":
            # Example: get lots reserved by this user
            q = (
                db.session.query(ParkingLot)
                .join(ParkingSpot)
                .join(ReserveParkingSpot)
                .filter(ReserveParkingSpot.user_id == query)
                .distinct()
            )
        else:
            q = []

        for lot in q:
            total_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id).count()
            occupied = ParkingSpot.query.filter_by(lot_id=lot.lot_id, status="occupied").count()
            spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id).all()
            lots.append({
                "lot_id": lot.lot_id,
                "occupied": occupied,
                "total": total_spots,
                "spots": [{"status": s.status} for s in spots]
            })

        search_info = f"{dropdown} = {query}"
    else:
        search_info = None

    return render_template("AdashSearch.html",
                           lots=lots,
                           search_info=search_info,
                           dropdown=dropdown,
                           query=query)


# SUMMARY PAGE
@app.route("/adashboard/summary")
def AdashSummary():
    # Get all lots
    lots = db.session.query(ParkingLot).all()

    labels = []
    revenues = []
    occupied_counts = []
    available_counts = []

    for lot in lots:
        labels.append(lot.prime_location or f"Lot {lot.lot_id}")

        # Calculate revenue: price per spot * count of reservations in that lot
        revenue_query = (
            db.session.query(func.count(ReserveParkingSpot.res_spot_id))
            .join(ParkingSpot, ReserveParkingSpot.spot_id == ParkingSpot.spot_id)
            .filter(ParkingSpot.lot_id == lot.lot_id)
        ).scalar()

        # revenue = count of reservations * lot.price_per_hour (or 0 if null)
        revenue = (revenue_query or 0) * (lot.price or 0)
        revenues.append(revenue)

        # Count occupied spots now
        occupied = (
            db.session.query(func.count(ParkingSpot.spot_id))
            .filter(ParkingSpot.lot_id == lot.lot_id, ParkingSpot.status == "occupied")
        ).scalar()

        occupied_counts.append(occupied or 0)

        # Available = max spots - occupied
        available = (lot.max_spots or 0) - (occupied or 0)
        available_counts.append(available if available >=0 else 0)

    # If no lots at all, still return empty arrays to avoid error
    return render_template(
        "AdashSummary.html",
        labels=labels,
        revenues=revenues,
        occupied=occupied_counts,
        available=available_counts
    )

@app.route("/logout", methods=["GET"])
def logout():
    # Clear all session data
    session.clear()
    # Optionally, show a flash message
    flash("You have been logged out.", "info")
    # Redirect to login page
    return redirect(url_for("login"))

@app.route("/edit_profile", methods=["GET", "POST"])
def Aeditprofile():
    # Make sure the user is logged in
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    # Load the user from the DB
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        # Update fields from form
        user.name = request.form["name"]
        user.email = request.form["email"]
        user.adress = request.form["address"]
        user.pincode = request.form["pincode"]

        # Save
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("edit_profile"))

    return render_template("Aeditprofiledetails.html", user=user)

@app.route("/Udashboard")
def Udashboard():
    user_id = session.get("user_id")

    # 🔵 Get search term from URL (GET parameter)
    search_term = request.args.get("search", "").strip()

    # Base query for lots
    lot_query = ParkingLot.query

    if search_term:
        if search_term.isdigit():
            # If search term is all digits, treat as pincode
            lot_query = lot_query.filter(ParkingLot.pincode == int(search_term))
        else:
            # Otherwise, search by prime_location (case-insensitive)
            lot_query = lot_query.filter(ParkingLot.prime_location.ilike(f"%{search_term}%"))

    # Execute the filtered (or unfiltered) query
    filtered_lots = lot_query.all()

    # For each lot, calculate available spots
    lots = []
    for lot in filtered_lots:
        total_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id).count()
        occupied_spots = ParkingSpot.query.filter(
            ParkingSpot.lot_id == lot.lot_id,
            ParkingSpot.status == "occupied"
        ).count()
        available_spots = total_spots - occupied_spots

        lots.append({
            "lot_id": lot.lot_id,
            "prime_location": lot.prime_location,
            "address": lot.address,
            "pincode": lot.pincode,
            "price": lot.price,
            "available_spots": available_spots
        })

    # 🔵 Get reservations for this user
    reservations_query = (
        db.session.query(
            ReserveParkingSpot,
            ParkingLot
        )
        .join(ParkingSpot, ReserveParkingSpot.spot_id == ParkingSpot.spot_id)
        .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.lot_id)
        .filter(ReserveParkingSpot.user_id == user_id)
        .order_by(ReserveParkingSpot.parking_time.desc())
    )

    reservations = []
    for r, lot in reservations_query:
        reservations.append({
            "res_spot_id": r.res_spot_id,
            "location": lot.prime_location,
            "vehicle_no": r.vehicle_no,
            "parking_time": r.parking_time.strftime("%Y-%m-%d %H:%M"),
            "is_active": r.leaving_time is None
        })

    return render_template(
        "Udashboard.html",
        lots=lots,
        reservations=reservations
    )


@app.route('/userdashboard/about')
def UdashAbout():
    return render_template("UdashAbout.html")
 
@app.route('/userdashboard/summary')
def UdashSummary():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in.", "danger")
        return redirect(url_for('login'))

    # Get all reservations for this user
    reservations = (
        db.session.query(
            ReserveParkingSpot,
            ParkingLot
        )
        .join(ParkingSpot, ReserveParkingSpot.spot_id == ParkingSpot.spot_id)
        .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.lot_id)
        .filter(ReserveParkingSpot.user_id == user_id)
        .all()
    )

    # Count reservations per parking lot
    usage_counts = {}
    for r, lot in reservations:
        label = lot.prime_location
        usage_counts[label] = usage_counts.get(label, 0) + 1

    # Prepare data for the chart
    labels = list(usage_counts.keys())
    data_counts = list(usage_counts.values())

    return render_template(
        "UdashSummary.html",
        labels=labels,
        data=data_counts
    )

@app.route('/userdashboard/contact')
def UdashContact():
    return render_template("UdashContact.html")

@app.route('/userdashboard/editprofile', methods=['GET', 'POST'])
def Ueditprofile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.adress = request.form['adress']
        user.pincode = request.form['pincode']
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('Udashboard'))
    return render_template("Ueditprofile.html", user=user)

@app.route("/admin/parking_lot/new", methods=["GET", "POST"])
def AnewParkingLot():
    if request.method == "POST":
        max_spots = int(request.form["max_spots"])
        lot = ParkingLot(
            prime_location=request.form["prime_location"],
            address=request.form["address"],
            pincode=request.form["pincode"],
            price=request.form["price"],
            max_spots=max_spots
        )
        db.session.add(lot)
        db.session.flush()  # gets lot.lot_id

        # Create spots
        for _ in range(max_spots):
            spot = ParkingSpot(
                status="available",
                lot_id=lot.lot_id
            )
            db.session.add(spot)

        db.session.commit()
        return redirect(url_for("Adashboard"))

    return render_template("Anewparkinglot.html")



from flask import request, redirect, flash, url_for

@app.route('/delete_parking_lot/<int:lot_id>')
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    occupied_count = ParkingSpot.query.filter_by(lot_id=lot_id, status='occupied').count()

    if occupied_count > 0:
        flash('Spots are occupied. Cannot delete!', 'danger')
        # redirect back to the referring page
        return redirect(request.referrer or url_for('Adashboard'))

    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully.', 'success')
    # redirect back to the referring page
    return redirect(request.referrer or url_for('Adashboard'))



@app.route("/admin/parking_spot/<int:spot_id>", methods=["GET", "POST"])
def AviewParkingSpot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            if spot.status == "occupied":
                return "Cannot delete occupied parking spot.", 400
            
            # Debugging output
            print("Deleting spot with ID:", spot.spot_id)
            
            db.session.delete(spot)
            db.session.commit()
            return redirect(url_for("Adashboard"))

        elif action == "close":
            return redirect(url_for("Adashboard"))

    return render_template("Aviewparkingspot.html", spot=spot)




@app.route("/admin/parking_spot/<int:spot_id>/details", methods=["GET"])
def Aoccupieddetails(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.status != "occupied":
        return "Spot is not occupied.", 400
    # Suppose you have extra fields related to occupancy in your model
    return render_template("Aoccupieddetails.html", spot=spot)

@app.route("/book_parking/<int:lot_id>", methods=["GET", "POST"])
def Ubookparkingspot(lot_id):
    # Make sure user is logged in
    if "user_id" not in session:
        flash("Please log in to book a spot.", "warning")
        return redirect(url_for("login"))

    # Fetch the parking lot
    lot = ParkingLot.query.get_or_404(lot_id)

    # Get the first available spot
    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status="available").first()

    if not available_spot:
        flash("No available spots in this lot.", "danger")
        return redirect(url_for("Udashboard"))

    if request.method == "POST":
        vehicle_no = request.form.get("vehicle_no")

        if not vehicle_no:
            flash("Vehicle number is required.", "danger")
            return redirect(url_for("Ubookparkingspot", lot_id=lot_id))

        # Update the spot status
        available_spot.status = "occupied"

        # Create reservation record
        reservation = ReserveParkingSpot(
            spot_id=available_spot.spot_id,
            user_id=session["user_id"],
            vehicle_no=vehicle_no,
            parking_time=datetime.now(),
            leaving_time=None,  # can be updated when released
            parking_cost_unit_time=lot.price
        )

        db.session.add(reservation)
        db.session.commit()

        flash("Spot reserved successfully!", "success")
        return redirect(url_for("Udashboard"))
    
    
    # Render the booking page with data
    return render_template(
        "Ubookparkingspot.html",
        lot=lot,
        spot=available_spot,
        user_id=session["user_id"]
    )

@app.route("/release_parking/<int:res_id>", methods=["GET"])
def Ureleaseparkingspot(res_id):
    reservation = ReserveParkingSpot.query.get_or_404(res_id)
    spot = ParkingSpot.query.get_or_404(reservation.spot_id)
    lot = ParkingLot.query.get_or_404(spot.lot_id)

    if reservation.leaving_time:
        flash("This spot is already released.", "info")
        return redirect(url_for("Udashboard"))

    release_time = datetime.now()
    duration = (release_time - reservation.parking_time).total_seconds() / 3600
    cost_per_hour = lot.price
    total_cost = round(duration * cost_per_hour, 2)

    return render_template(
        "Ureleaseparkingspot.html",
        reservation=reservation,
        spot=spot,
        lot=lot,
        release_time=release_time.strftime("%Y-%m-%d %H:%M"),
        total_cost=total_cost
    )


@app.route("/release_parking/<int:res_id>", methods=["POST"])
def Uconfirmrelease(res_id):
    reservation = ReserveParkingSpot.query.get_or_404(res_id)
    spot = ParkingSpot.query.get_or_404(reservation.spot_id)

    if not reservation.leaving_time:
        reservation.leaving_time = datetime.now()
        spot.status = "available"
        db.session.commit()
        flash("Parking spot released successfully!", "success")

    return redirect(url_for("Udashboard"))
