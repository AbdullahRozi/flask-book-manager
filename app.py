from flask import Flask, jsonify ,request 
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import Mapped , mapped_column 
from sqlalchemy import String


app = Flask(__name__)
CORS(app) # This tells Flask to allow external websites (like your HTML portfolio) to access it




app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = 'books'
    id:Mapped[int] = mapped_column(primary_key=True , autoincrement=True) 
    name:Mapped[str] = mapped_column( String(100) ,nullable=False )

    def to_dict(self):
        return {"id": self.id, "name": self.name}


with app.app_context():
    db.create_all()
books = [   ]



def check_element(id):

    for task in books:
        if task["id"] == id:
            return True
    return False        

def delete_item(id):
    for task in books:
        if task["id"] == id:
            books.remove(task)
            break


# Your Flask Backend (app.py)
@app.route('/api/items', methods=['GET' , 'POST'])
def get_all_books():
    if request.method == 'POST':
        data_received = request.get_json()
        book_title = data_received.get('name')
        new_book = Book(name=book_title)
        db.session.add(new_book)
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": f"Book '{book_title}' saved successfully!"
        }), 201
    # Fetching data from SQLite
    
    all_books = Book.query.all()
    books_list = [b.to_dict() for b in all_books]
    
    return jsonify(books_list)  # Sends a JSON string down the bridge



@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    target_book = Book.query.get(task_id)

    if target_book is None:
        return jsonify({"error": "Task not found"}), 404

    else:
        db.session.delete(target_book)
        db.session.commit()   
        return jsonify({"message": f"Task {task_id} deleted successfully!"}), 200


@app.route('/api/update/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    # 1. Look up the item in the database by its ID
    target_book = Book.query.get(task_id)

    # If it doesn't exist, exit early
    if target_book is None:
        return jsonify({"error": "Task not found"}), 404

    # 2. Get the new payload sent by JavaScript (e.g., { "name": "New Title" })
    data_received = request.get_json()
    new_name = data_received.get('name')

    # Guard clause: Make sure the frontend actually sent a valid string
    if not new_name:
        return jsonify({"error": "Missing name field"}), 400

    # 3. UPDATE the property on your model instead of deleting it!
    target_book.name = new_name 

    # 4. Save the modifications to your database
    db.session.commit()   
    
    return jsonify({
        "status": "success",
        "message": f"Task {task_id} successfully updated to '{new_name}'!"
    }), 200

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(debug=True, port=5000)