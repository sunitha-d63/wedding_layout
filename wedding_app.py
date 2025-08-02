from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify,abort
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from config import Config
from database import db
from forms import LoginForm, RegistrationForm
from models import User, Wishlist, Cart
from data.hindu_wedding_cards import cards
from data.wedding_cards_section import affordable_cards
from data.all_cards import all_cards
from flask_migrate import Migrate
from datetime import datetime
import random

TAX_RATE = 0.10

PAYMENT_METHODS = [
    {"name": "Paytm", "image": "images/paytm.png"},
    {"name": "Gpay", "image": "images/gpay.png"},
    {"name": "PhonePe", "image": "images/phonepay.png"},
    {"name": "Cred", "image": "images/cred.png"},
]

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def root():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        login_form = LoginForm()
        reg_form = RegistrationForm()
        if current_user.is_authenticated:
            return redirect(url_for('home'))

        next_page = request.args.get('next') or request.form.get('next') or url_for('home')

        if login_form.validate_on_submit():
            user = User.query.filter_by(email=login_form.email.data).first()
            if user and user.check_password(login_form.password.data):
                session.clear()
                login_user(user)
                return redirect(next_page)
            flash('Invalid email or password', 'danger')

        return render_template('auth.html', login_form=login_form, reg_form=reg_form, next=next_page)

    @app.route('/register', methods=['POST'])
    def register():
        login_form = LoginForm()
        reg_form = RegistrationForm()
        if reg_form.validate_on_submit():
            if User.query.filter_by(email=reg_form.email.data).first():
                flash('Email already registered', 'warning')
            else:
                user = User(name=reg_form.name.data, email=reg_form.email.data)
                user.set_password(reg_form.password.data)
                db.session.add(user)
                db.session.commit()
                flash('Account created! Please log in.', 'success')
                return redirect(url_for('login'))

        return render_template('auth.html', login_form=login_form, reg_form=reg_form, next='')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        return redirect(url_for('login'))

    @app.route('/home')
    @login_required
    def home():
        return render_template('home.html', name=current_user.name, cards=affordable_cards)

    @app.route('/about')
    @login_required
    def about():
        return render_template('about.html')

    @app.route('/contact')
    @login_required
    def contact():
        return render_template('contact.html')

    @app.route('/faq')
    @login_required
    def faq():
        return render_template('faq.html')

    @app.route('/how-to-order')
    @login_required
    def how_to_order():
        return render_template('how_to_order.html')

    @app.route('/wedding_cards')
    @login_required
    def wedding_cards():
        return render_template('wedding_cards.html')

    @app.route('/hindu_wedding_cards')
    @login_required
    def hindu_wedding_cards():
        return render_template('hindu_wedding_cards.html', cards=cards)

    @app.route('/invitation_card_section')
    @login_required
    def invitation_card_section():
        return render_template('invitation_card_section.html')

    @app.route('/wedding-cards-affordable')
    @login_required
    def wedding_cards_affordable():
        return render_template('wedding_cards_section.html', cards=affordable_cards, active='wedding_cards')

    @app.route('/wishlist')
    @login_required
    def wishlist():
        items = Wishlist.query.filter_by(user_id=current_user.id).all()
        return render_template('wishlist.html', items=items)
    
    @app.route('/add_to_wishlist/<int:card_id>', methods=['POST'])
    @login_required
    def add_to_wishlist(card_id):
        from data.all_cards import all_cards 
    
        existing = Wishlist.query.filter_by(user_id=current_user.id, card_id=card_id).first()
        if existing:
            return jsonify({'message': 'Already in wishlist.'})

        card = next((c for c in all_cards if c['id'] == card_id), None)
        if not card:
            return jsonify({'message': 'Card not found'}), 404

        wishlist_item = Wishlist(
            user_id=current_user.id,
            card_id=card_id,
            title=card['title'],
            price=card['price'],
            image=card['src'] 
    )
        db.session.add(wishlist_item)
        db.session.commit()

        return jsonify({'message': 'Added to wishlist!'})

    @app.route('/wishlist/remove/<int:wishlist_id>', methods=['POST'])
    @login_required
    def remove_from_wishlist(wishlist_id):
        item = Wishlist.query.get_or_404(wishlist_id)
        if item.user_id != current_user.id:
            abort(403)
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for('wishlist'))
    
    @app.route('/cart')
    @login_required
    def cart():
        cart_dict = session.get('cart', {})
        total_ex = sum(v['price'] * v['qty'] for v in cart_dict.values())
        total_tax = total_ex * TAX_RATE
        grand_total = total_ex + total_tax
        return render_template('cart.html', cart=cart_dict, total_ex=total_ex, total_tax=total_tax, grand_total=grand_total)

    @app.route('/product/<int:card_id>')
    @login_required
    def product_detail(card_id):
        card = next((c for c in cards if c['id'] == card_id), None)
        if not card:
            return "Card not found", 404

        wedding_info = {
            'ring_img': 'ring.jpg',
            'groom': 'Ramesh',
            'bride': 'Sita',
            'date': 'December 12, 2025',
            'time': '6:00 PM',
            'location': 'Lakshmi Marriage Hall, Chennai'
        }

        related_cards_pool = [c for c in cards if c['id'] != card_id]
        related_cards = random.sample(related_cards_pool, min(4, len(related_cards_pool)))

        return render_template('product_detail.html', card=card, wedding_info=wedding_info, related_cards=related_cards)

    @app.route('/add_to_cart', methods=['POST'])
    @login_required
    def add_to_cart():
        card_id = str(request.form.get('card_id'))
        card = next((c for c in all_cards if str(c['id']) == card_id), None)
        if card:
            cart = session.get('cart', {})
            item = cart.get(card_id, {
                'sku': card['sku'],
                'title': card['title'],
                'price': card['price'],
                'src': url_for('static', filename='images/' + card['src']),
                'qty': 0
            })
            item['qty'] += 1
            cart[card_id] = item
            session['cart'] = cart
            session.modified = True
        return redirect(request.referrer or url_for('home'))

    @app.route('/update_cart', methods=['POST'])
    @login_required
    def update_cart():
        card_id = request.form.get('card_id')
        action = request.form.get('action')
        cart = session.get('cart', {})

        if card_id in cart:
            if action == 'inc':
                cart[card_id]['qty'] += 1
            elif action == 'dec':
                cart[card_id]['qty'] = max(1, cart[card_id]['qty'] - 1)
            elif action == 'remove':
                cart.pop(card_id)

        session['cart'] = cart
        session.modified = True
        return redirect(url_for('cart'))

    @app.route('/checkout', methods=['GET', 'POST'])
    @login_required
    def checkout():
        cart = session.get('cart', {})
        subtotal = sum(v['price'] * v['qty'] for v in cart.values())
        tax = subtotal * TAX_RATE
        total = subtotal + tax

        now = datetime.now()
        today_str = now.strftime("%B %d, %Y")
        now_str = now.strftime("%I:%M %p")

        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            payment_method = request.form.get('payment_method')

            if not payment_method:
                flash("Please select a payment method.", "danger")
                return render_template('checkout.html',
                    methods=PAYMENT_METHODS,
                    checkout_items=list(cart.values()),
                    subtotal=subtotal,
                    total=total,
                    date=today_str,
                    time=now_str
                )

            session['order'] = {
                'order_id': datetime.utcnow().strftime('%Y%m%d%H%M%S'),
                'user': {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'address': address
                },
                'payment_method': payment_method,
                'total': total
            }

            session['cart'] = {}

            return redirect(url_for('order_confirmation'))

        return render_template('checkout.html',
            methods=PAYMENT_METHODS,
            checkout_items=list(cart.values()),
            subtotal=subtotal,
            total=total,
            date=today_str,
            time=now_str
        )

    @app.route('/order-confirmation')
    @login_required
    def order_confirmation():
        order = session.get('order')
        if not order:
            return redirect(url_for('checkout'))

        return render_template(
            'orderconfirmation.html',
            order_id=order['order_id'],
            user=order['user'],
            payment_method=order['payment_method']
        )

    @app.context_processor
    def utility_context():
        return dict(TAX_RATE=TAX_RATE)

    @app.context_processor
    def inject_cart_count():
        cart = session.get('cart', {})
        count = sum(item['qty'] for item in cart.values())
        return dict(cart_count=count)

    initial_filters = [
    "Wedding Cards",
    "Scroll Cards",
    "Theme Cards",
    "Birthday Cards",
    "Engagement Cards"
]

    ideas = [f"images/search{i}.png" for i in range(1, 6)]
    popular = [f"images/search{i}.png" for i in range(6, 12)]
    @app.route('/search', methods=['GET', 'POST'])
    def search():
        query = ''
        filters = initial_filters.copy()
        results = []

        if request.method == 'POST':
            query = request.form.get('search_query', '').strip()
            removed = request.form.get('remove_filter')
            if removed in filters:
                filters.remove(removed)
        else:
            query = request.args.get('q', '').strip()

        if query:
            results = [card for card in cards if query.lower() in card['title'].lower()]
        return render_template(
            'search.html',
            query=query,
            results=results,
            filters=filters,
            ideas=ideas,
            popular=popular
    )

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    create_app().run(debug=True)