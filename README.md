# FSSE_JAN24_GroupF_GFP_Backend
Backend repository for the final project of PRevoU Fullstack Software Engineering Bootcamp Section Amsterdam - Group F
POSTMAN: https://documenter.getpostman.com/view/34500130/2sA3s3GrCY

### LocalBites Frontend: https://github.com/anojumisa/FSSE_JAN24_GroupF_GFP.git

## Table of Contents
- [About the Project](#about-the-project)
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)

## About the Project
LocalBites is a digital marketplace that connect food lovers with passionate artisans who craft delicacies with love and local ingredients. LocalBites is not just about indulging souvenirs but also committed to preserving the planet for future generations. That's why we've built a sustainable ecosystem around our business. Our delivery fleet consists of eco-friendly bicycles, reducing carbon emissions and supporting local communities. Our packaging is meticulously chosen to be recyclable, minimizing waste.

By choosing LocalBites, you're not just satisfying your cravings; you're also contributing to a greener planet. Every purchase brings you closer to the heart of a community and supports sustainable practices.

## Overview
This is the backend for an e-commerce application built using [Flask](https://flask.palletsprojects.com/). It provides RESTful API endpoints for user authentication, product management, and order processing.

## Features
- User Authentication (JWT-based)
- Product Management
- Order Processing

## Tech Stack
- **Backend**: Flask, JWT
- **Database**: MySQL

## Installation

### Prerequisites
- Python (v3.8 or higher)
- MySQL

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/anojumisa/FSSE_JAN24_GroupF_GFP_Backend.git
   cd your-backend-repo
2. Create Create a virtual environment and activate it:
    ```bash
    pip install pipenv
    pipenv shell
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
4. Set up environment variables (see [.env.example](/.env.example))    

5. Run the backend server:
    ```bash
    flask --app index run --debug
### Additional Notes

- **Cross-Origin Resource Sharing (CORS)**: Ensure that your backend API allows requests from your frontend domain by configuring CORS appropriately in your Flask application.
  
- **API URL Configuration**: Since the frontend and backend are in separate repositories, you'll need to ensure that the `NEXT_PUBLIC_API_URL` in the frontend's environment variables points to the correct backend API URL.

# API ENDPOINTS

| API Method | Endpoint                            | Description                               |
|------------|-------------------------------------|-------------------------------------------|
| `POST`     | `/register`                         | Register a new user                       |
| `POST`     | `/login`                            | Login user and return JWT token           |
| `GET`      | `/user/dashboard`                   | User dashboard                            |
| `PUT`      | `/profile`                          | Edit data user                            |
| `POST`     | `/logout`                           | Logout user (requires JWT)                |
| `POST`     | `/store_register`                   | Register a new seller and store           |
| `POST`     | `/store_login`                      | Login seller and return JWT token         |
| `GET`      | `/store/info`                       | Store dashboard                           |
| `GET`      | `/store/orders`                     | Retrieve store's ordered items by user    |
| `PUT`      | `/stores/me`                        | Edit data seller                          |
| `POST`     | `/store_logout`                     | Logout seller (requires JWT)              |
| `POST`     | `/products`                         | Add a new product                         |
| `GET`      | `/products`                         | Retrieve a list of products               |
| `GET`      | `/product/<id>`                     | Retrieve a single product by ID           |
| `GET`      | `/store/products_overview`          | Retrieve a list of products by store      |
| `PUT`      | `/update_product/<int:product_id>`  | Edit a single product                     |
| `DELETE`   | `/remove_product/<int:product_id>`  | Remove a single product by ID             |
| `GET`      | `/cart`                             | Retrieve a list of products to the cart   |
| `POST`     | `/cart/add`                         | Add product to the cart                   |
| `PUT`      | `/cart/update`                      | Edit product's quantity                   |
| `GET`      | `/cart`                             | Retrieve a list of items to the cart      |
| `DELETE`   | `/cart/remove`                      | Remove an item from the cart              |
| `POST`     | `/cart/checkout`                    | Checkout and process payment              |
| `DELETE`   | `/cart/clear`                       | Clearing cart                             |
| `GET`      | `/cart/total`                       | Count cart's total price                  |
| `GET`      | `/orders`                           | Retrieve user's orders                    |
| `POST`     | `/order`                            | Create a new order                        |
| `POST`     | `/order/add`                        | Add new orders                            |
| `GET`      | `/cart/total`                       | Count cart's total price                  |
| `POST`     | `/categories`                       | Add category                              |
| `GET`      | `/categories/<int:category_id>`     | Retrieve category                         |
| `PUT`      | `/category/<int:category_id>`       | Edit category                             |
| `DELETE`   | `/categories/<int:category_id>`     | Remove category                           |
| `POST`     | `/product/<int:product_id>/categories`| Add product to categorycategory         |
| `DELETE`   | `/product/<int:product_id>/categories`| Remove product from category            |
| `GET`      | `/featured-products`                | Retrieve featured products                |
| `POST`     | `/upload`                           | Upload image                              |
| `POST`     | `/store_image_url`                  | Add store image                           |
| `POST`     | `/user_image`                       | Add user image                            |
| `GET`      | `/search`                           | Retrieve searched products                |
| `GET`      | `/search/location`                  | Retrieve products filtered by location    |


