from flask import Flask, request
from flask import render_template
from flask_cors import CORS, cross_origin
import glob
import os
import socket
from pymongo import MongoClient 

app = Flask(__name__)
CORS(app)
client = MongoClient()
db = client.picam
collection = db.captured_images


@app.route('/')
def hello():
	return "Hello World"

@app.route('/images')
def show_images():
	items = collection.find({})
	return render_template('index.html', items=items)


@app.route('/screenshot', methods=['POST'])
def take_screenshot():
	image_id = request.values['orderid']
	print("Order ID", image_id)
	newest = max(glob.iglob('/var/www/html/media/*.jpg'), key=os.path.getctime)
	file_name = os.path.split(newest);
	url_to_file = os.path.join("http://" + get_ip_address() + "/html/media/", file_name[1])
	print("Captured Image:", url_to_file)
	save_to_database(image_id, url_to_file)
	return ''


def save_to_database(order_id, image_url):
	post = {"order_id": order_id, "image_url": image_url}
	collection.insert_one(post).inserted_id
	print("Saved to Database")

def get_ip_address():
        try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
                return "";


if __name__ == '__main__':
	print("Starting the Web Server")
	app.run(host='0.0.0.0')
