from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SECRET_KEY'] = 'TEST'

db = SQLAlchemy(app)

admin = Admin(app)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    phone = db.Column(db.String(20))
    amount = db.Column(db.String(10))
    draw_list = db.Column(db.String(100))
    draws = db.relationship('Draw', backref="customer", lazy=True)

    def __repr__(self):
        return self.name


class Draw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey('customer.id'), nullable=False)
    placement = db.Column(db.Integer)
    home = db.Column(db.String(50))
    away = db.Column(db.String(50))


admin.add_view(ModelView(Customer, db.session))
admin.add_view(ModelView(Draw, db.session))


@app.route('/')
def index():
    return "Hello World"


@app.route('/draw', methods=['POST'])
def draw():
    content = request.json
    print(content)

    customer = Customer()
    customer.name = content['name']
    customer.phone = content['phone']
    customer.amount = content['amount']
    customer.draw_list = content['draws']
    db.session.add(customer)
    db.session.commit()

    return jsonify({'success': True})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
