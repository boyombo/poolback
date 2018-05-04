from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from collections import defaultdict


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
    ticket_num = db.Column(db.String(20))

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

    now = datetime.now().strftime('%Y%m%d%H%M%S')
    # total_count = len(Customer.query.all())
    total_count = db.session.query(db.func.max(Customer.id)).scalar() + 1
    postfix = '{}'.format(total_count).zfill(6)

    customer = Customer()
    customer.name = content['name']
    customer.phone = content['phone']
    customer.amount = content['amount']
    customer.draw_list = content['draws']
    # generate ticket number in format yyyymmddhhMM + 4digits for num people
    # registered in that minute
    customer.ticket_num = "{}{}".format(now, postfix)

    db.session.add(customer)
    db.session.commit()
    return jsonify({'success': True, 'ticket': customer.ticket_num})


keys_3 = {
    3: [6, 400],
    2: [3, 1200],
    1: [1, 10000]
}

keys_4 = {
    1: [1, 15000],
    3: [12, 500],
    4: [24, 300]
}


@app.route('/ways')
def ways():
    kind = request.args.get('kind', '')
    if kind not in ['exactorder', 'anyorder']:
        return jsonify(
            {
                'success': False,
                'message': 'Kind is either "exactorder" or "anyorder"'
            })
    params = request.args.get('games')
    parts = params.split(',')

    if not all(i.isdigit() for i in parts):
        return jsonify({'success': False, 'message': 'Only digits allowed'})
    unique_parts = len(set(parts))

    if len(parts) == 3:
        if kind == 'exactorder':
            return jsonify({'success': True, 'message': 1, 'amount': 10000})

        try:
            val = keys_3[unique_parts]
        except KeyError:
            return jsonify({'success': False, 'message': 'Wrong params'})
        else:
            return jsonify(
                {'success': True, 'message': val[0], 'amount': val[1]})

    elif len(parts) == 4:
        if kind == 'exactorder':
            return jsonify({'success': True, 'message': 1, 'amount': 15000})

        try:
            val = keys_4[unique_parts]
        except KeyError:
            if unique_parts == 2:
                _test_key = [i for i in parts if i == parts[0]]
                if len(_test_key) in [1, 3]:
                    val = [4, 2500]
                else:
                    val = [6, 1000]
        return jsonify({'success': True, 'message': val[0], 'amount': val[1]})

    else:
        return jsonify({'success': False, 'msg': '3 or 4 numbers allowed'})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
