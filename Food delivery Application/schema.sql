CREATE DATABASE food_app; 
USE food_app;
DESC subscriptions;
select * from UserDetails;

CREATE TABLE address (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    full_name VARCHAR(100),
    mobile VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    pincode VARCHAR(10),
    landmark VARCHAR(100)
);
CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    item_name VARCHAR(200),
    price DECIMAL(10,2),
    quantity INT,
    subtotal DECIMAL(10,2),
     image VARCHAR(255)
);
CREATE TABLE delivery_location (
id INT AUTO_INCREMENT PRIMARY KEY,
order_id INT,
latitude DOUBLE,
longitude DOUBLE
);
CREATE TABLE delivery_partners (
  partner_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  phone VARCHAR(15),
  latitude DOUBLE,
  longitude DOUBLE,
  is_available BOOLEAN
);
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    item_name VARCHAR(200),
    price DECIMAL(10,2),
    quantity INT,
    subtotal DECIMAL(10,2),
    image VARCHAR(255)
);
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total_amount DECIMAL(10,2),
    order_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    partner_id INT,
    delivery_otp varchar(10)
);
CREATE TABLE restaurants (
  restaurant_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  latitude DOUBLE,
  longitude DOUBLE,
  address TEXT
);
CREATE TABLE users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  phone VARCHAR(15),
  latitude DOUBLE,
  longitude DOUBLE,
  address TEXT
);
Create Table Userdetails(
   Id int primary key auto_increment,
	  name varchar(200),
    Email varchar(200),
    Mobile bigint,
    Password varchar(200),
    latitude double,
    longitude double
);
CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(200)
);

CREATE TABLE subscriptions (
    subscription_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    food_name VARCHAR(100),
    price DECIMAL(10,2),
    plan_type VARCHAR(20),
    delivery_address TEXT,
    start_date DATE,
    end_date DATE,
    subscription_status VARCHAR(20) DEFAULT 'Active',
    restaurant_name VARCHAR(100),
    delivery_time VARCHAR(100)
);

INSERT INTO delivery_partners (name,phone,is_available)
VALUES
('suraj Kumar','6207618768',1),
('Rahul Kumar','6206518976',1);

INSERT INTO admin (username, password)
VALUES ('admin', 'admin123');