## REST API Service for Posting, Transforming, and Commenting on Images

<p align="center">
    <img src="https://img.shields.io/badge/Language-Python-9cf">
    <img src="https://img.shields.io/badge/Version-3.6.6-36c8e6">
    <img src="https://img.shields.io/badge/FastAPI-0.95.1-3ec689">
    <img src="https://img.shields.io/badge/SQLAlchemy-2.0-f9a033">
    <img src="https://img.shields.io/badge/Pytest-7.3.0-7a6fb8">
    <img src="https://img.shields.io/badge/Unittest-00a0e6">
    <img src="https://img.shields.io/badge/License-MIT-yellow">

</p>

## About

This is a REST API service that allows users to post images, transform them and comment on them. It is built using Python, FastAPI, SQLAlchemy, Cloudinary, and qrcode.

### Technologies
Python - Programming language
FastAPI - Web framework for building APIs
SQLAlchemy - Object-relational mapping library
Cloudinary - Cloud-based image and video management service
qrcode - QR code generator library

## Features
### The API supports the following features:

+ User registration and authentication
+ Uploading and storing images
+ Adding image tags and filtering images by tags
+ Transforming images (e.g., resizing, cropping, rotating, adding text or watermark)
+ Rating images and commenting on them

# Introduction

### Installation
## To install the dependencies, you can run the following command:

bash Copy code
```
pip install -r requirements.txt
```


After that, you can run the app using the following command:

bash Copy code
```
uvicorn app.main:app --reload
```



## How to use it?
### Authorization

+ Before use User should be signed up with a unique username, first name, last name, email, and password.
+ After signing up User should confirm their email.

### Features

+ Users can post images and add image tags.
+ Posted images can be rated and commented on by other users.

### Endpoints
The API supports the following endpoints described in project documentation [GoIT Team 3 WEB project](docs/_build/static/index.html)


### Our Team 3:

</p>
<div align="left">
  <a href="https://github.com/SSP0d">Serhii Pidkopai</a><br>
  <a href="https://github.com/valeri7122">Valeri Tretiakov</a><br>
  <a href="https://github.com/TT1410">Taras Plaksii</a><br>
  <a href="https://github.com/OlgaNazarenko">Olga Nazarenko</a><br>
  <a href="https://github.com/YaroslavZq">Yaroslav Zhuk</a><br>
  <a href="https://github.com/AndrewCheUA">Andrii Cheban</a><br>
</div>
