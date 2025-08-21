-- DROP DATABASE food_inventory
CREATE DATABASE food_inventory;

USE food_inventory;

/*+
CREATE TABLE users(
	id int not null auto_increment unique,
    username varchar(100) not null,
    password varchar(100) not null
);
ALTER TABLE users ADD CONSTRAINT PK_users PRIMARY KEY(id);
*/

CREATE TABLE foods(
	id int not null auto_increment unique,
    name varchar(100) not null,
    category_id int not null,
    admission_date date not null
);

ALTER TABLE foods ADD CONSTRAINT PK_food PRIMARY KEY(id);

CREATE TABLE categories(
	id int not null auto_increment unique,
    name varchar(100) not null
);

ALTER TABLE foods ADD CONSTRAINT FK_food_categories FOREIGN KEY(category_id) 
REFERENCES categories (id);
ALTER TABLE categories ADD CONSTRAINT PK_categories PRIMARY KEY(id);

CREATE TABLE notifications(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    food_id INT NOT NULL,
    user_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE notifications ADD CONSTRAINT FK_notifications_foods FOREIGN KEY(food_id)
REFERENCES foods (id);

SELECT * FROM categories;
SELECT * FROM foods;

