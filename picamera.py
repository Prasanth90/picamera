from flask import Flask, request
from flask import render_template
import requests
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
	stage_id = request.values['stageid']
	print("Order ID", image_id)
	print("Stage ID", stage_id)
	newest = max(glob.iglob('/var/www/html/media/*.jpg'), key=os.path.getctime)
	file_name = os.path.split(newest);
	url_to_file = os.path.join("http://" + get_ip_address() + "/html/media/", file_name[1])
	print("Captured Image:", url_to_file)
	#save_to_database(image_id, url_to_file)
	post_file(newest, file_name, image_id, stage_id)
	return ''
    
def post_file(file, file_name , order_id, stage_id):
    parameters = {'order' : order_id, 'stage' : stage_id}
    image_file = {'captureFile' : ('my_file.jpg', open(file, 'rb'))}
    r = requests.post('http://d.tanios.ca/anfibio/exp/captures/save', files= image_file, data = parameters)
    print(r.text)


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
