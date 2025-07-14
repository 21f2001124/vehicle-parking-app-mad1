from flask import Flask
from application.database import db

def create_app():
    app= Flask(__name__) #to create instance of flask object can take automatically...like app.py or python.pt
    app.secret_key = "1234"
    app.debug= True #show error on lines in pages 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Vehicle_Parking_Database.sqlite3'

    db.init_app(app)

    app.app_context().push() #reduce runtime error, bring everything under context of flask application
    return app 

app=create_app()
from application.controller import *

if __name__ == "__main__":
    app.run()

#this is changed