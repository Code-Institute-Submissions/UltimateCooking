import os
from os import path
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from flask_s3 import FlaskS3
import boto3
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from __main__ import app
from __main__ import mongo


def upload_file(file_name, bucket):
    """
    Function to upload a file to an S3 bucket
    """
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)

    return response


@app.route('/manage_tools')
def manage_tools():
    return render_template("tool/tool_manage.html",
                           tools=mongo.db.tools.find())


@app.route('/add_tool')
def add_tool():
    return render_template("tool/tool_add.html")


@app.route('/insert_tool', methods=['POST'])
def insert_tool():
    f = request.files['file']
    f.save(os.path.join(app.config['UPLOAD_FOLDER_TOOL'], f.filename))
    upload_file(app.config['UPLOAD_FOLDER_TOOL'] + "/" + f.filename,
                app.config['FLASKS3_BUCKET_NAME'])
    url = f.filename
    tool_doc = {
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'picture': url,
        'brand': request.form.get('brand'),
        'price': request.form.get('price')
        }
    mongo.db.tools.insert_one(tool_doc)
    return redirect(url_for('manage_tools'))


@app.route('/edit_tool/<tool_id>')
def edit_tool(tool_id):
    the_tool = mongo.db.tools.find_one({'_id': ObjectId(tool_id)})
    return render_template("tool/tool_edit.html",
                           tool=the_tool,
                           imagePath=app.config['UPLOAD_FOLDER_TOOL'],
                           s3link=app.config['AWS_BUCKET_LINK'])


@app.route('/update_tool/<tool_id>', methods=['POST'])
def update_tool(tool_id):
    tools = mongo.db.tools
    pictures = mongo.db.tools.find_one({'_id': ObjectId(tool_id)}, {'picture': 1, '_id': 0})
    tools.update({'_id': ObjectId(tool_id)},
                 {
                     'name': request.form.get('name'),
                     'description': request.form.get('description'),
                     'picture': pictures['picture'],
                     'brand': request.form.get('brand'),
                     'price': request.form.get('price')
                 })
    return redirect(url_for('manage_tools'))


@app.route('/delete_tool/<tool_id>')
def delete_tool(tool_id):
    mongo.db.tools.remove({'_id': ObjectId(tool_id)})
    return redirect(url_for('manage_tools'))


@app.route('/edit_tool_picture/<tool_id>')
def edit_tool_picture(tool_id):
    the_tool = mongo.db.tools.find_one({'_id': ObjectId(tool_id)})
    return render_template("tool/tool_pic_edit.html",
                           tool=the_tool,
                           imagePath=app.config['UPLOAD_FOLDER_TOOL'],
                           s3link=app.config['AWS_BUCKET_LINK'])


@app.route('/update_tool_picture/<tool_id>', methods=['POST'])
def update_tool_picture(tool_id):
    f = request.files['file']
    f.save(os.path.join(app.config['UPLOAD_FOLDER_TOOL'], f.filename))
    upload_file(app.config['UPLOAD_FOLDER_TOOL'] + "/" + f.filename,
                app.config['FLASKS3_BUCKET_NAME'])
    url = f.filename
    tools = mongo.db.tools
    tool = mongo.db.tools.find_one({'_id': ObjectId(tool_id)})
    tools.update({'_id': ObjectId(tool_id)},
                 {
                     'name': tool['name'],
                     'description': tool['description'],
                     'picture': url,
                     'brand': tool['brand'],
                     'price': tool['price']
                 })
    return redirect(url_for('manage_tools'))


@app.route('/view_tools_grid')
def view_tools_grid():
    return render_template("tool/tool_view_grid.html",
                           tools=mongo.db.tools.find(),
                           imagePath=app.config['UPLOAD_FOLDER_TOOL'],
                           s3link=app.config['AWS_BUCKET_LINK'])


@app.route('/view_tool/<tool_id>')
def view_tool(tool_id):
    the_tool = mongo.db.tools.find_one({'_id': ObjectId(tool_id)})
    return render_template("tool/tool_view.html",
                           tool=the_tool,
                           imagePath=app.config['UPLOAD_FOLDER_TOOL'],
                           s3link=app.config['AWS_BUCKET_LINK'])
