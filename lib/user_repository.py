from lib.user import User
from lib.booking import Booking
from lib.space import Space

class UserRepository:
    def __init__(self, db_connection) -> None:
        self._connection = db_connection

    def all(self):
        rows = self._connection.execute('SELECT * from users')
        users = []
        for row in rows:
            item = User(row["id"], row["name"], row["email"],
                        row["password"], row["phone_number"])
            users.append(item)
        return users

    def create(self, user):
        rows = self._connection.execute('INSERT INTO users (name, email, password, phone_number) VALUES (%s, %s, %s, %s) RETURNING id', [
                                        user.name, user.email, user.password, user.phone_number])
        row = rows[0]
        user.id = row['id']
        return user

    def find(self, user_id):
        rows = self._connection.execute(
            'SELECT * from users WHERE id = %s', [user_id])
        row = rows[0]
        return User(row["id"], row["name"], row["email"],
                    row["password"], row["phone_number"])
    
    def find_by_email(self, user_email):
        rows = self._connection.execute(
            'SELECT * from users WHERE email = %s', [user_email])
        row = rows[0]
        return User(row["id"], row["name"], row["email"],
                    row["password"], row["phone_number"])
    
    def find_user_with_bookings(self, user_id):
        # Needs updating to return bookings and spaces along with the user
        user = self.find(user_id)
        rows = self._connection.execute(
            'SELECT bookings.id as booking_id, start_date, end_date, total_price, confirmed, space_id, spaces.name, spaces.address, spaces.price, spaces.description, spaces.image_url From bookings JOIN spaces on bookings.space_id = spaces.id WHERE bookings.user_id = %s', [user_id])
        
        bookings = []
        for row in rows:
            booking = Booking(row['booking_id'], row['start_date'], row['end_date'], row['total_price'], user.id, row['space_id'], row['confirmed'])
            booking.space_name = row['name']
            booking.space_address = row['address']
            bookings.append(booking)
        user.bookings = bookings
        return user
    
    def find_with_spaces_and_bookings(self, user_id):
        rows = self._connection.execute(
            'SELECT users.id, users.email, users.password, spaces.id AS space_id, spaces.name AS space_name, spaces.description, spaces.price, spaces.user_id, spaces.image_url FROM users JOIN spaces ON users.id = spaces.user_id WHERE users.id = %s', [user_id])
        spaces = []
        for row in rows:
            print(row)
            space = Space(row['space_id'], row['space_name'], row['price'], row['description'], row['user_id'], row['image_url'])
            spaces.append(space)
        print(spaces)
        rows = self._connection.execute(
            'SELECT users.id, users.email, users.password, ' \
            'bookings.id AS booking_id, bookings.start_date, bookings.confirmed, bookings.booked_by, bookings.space_id ' \
            'FROM users JOIN bookings ON users.id = bookings.booked_by WHERE users.id = %s', [user_id])
        bookings = []
        for row in rows:
            bookings.append(Booking(row['booking_id'], row['start_date'], row['confirmed'], row['booked_by'], row['space_id']))
        user = User(row['id'], row['email'], row['password'], spaces, bookings)
        return user