require('dotenv').config();
const mysql = require('mysql2/promise');

async function initDatabase() {
  let connection;
  
  try {
    // Connect without database to create it
    connection = await mysql.createConnection({
      host: process.env.DB_HOST,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      port: process.env.DB_PORT
    });

    console.log('Connected to MySQL server');

    // Create database
    await connection.query(`CREATE DATABASE IF NOT EXISTS ${process.env.DB_NAME}`);
    console.log(`Database ${process.env.DB_NAME} created or already exists`);

    // Use the database
    await connection.query(`USE ${process.env.DB_NAME}`);

    // Create users table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20),
        role ENUM('customer', 'admin') DEFAULT 'customer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      )
    `);
    console.log('Users table created');

    // Create categories table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS categories (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log('Categories table created');

    // Create products table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS products (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        stock INT DEFAULT 0,
        category_id INT,
        image_url VARCHAR(500),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
      )
    `);
    console.log('Products table created');

    // Create cart_items table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS cart_items (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        UNIQUE KEY unique_cart_item (user_id, product_id)
      )
    `);
    console.log('Cart items table created');

    // Create orders table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS orders (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
        shipping_address_id INT,
        payment_method VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `);
    console.log('Orders table created');

    // Create order_items table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS order_items (
        id INT PRIMARY KEY AUTO_INCREMENT,
        order_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id)
      )
    `);
    console.log('Order items table created');

    // Create reviews table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS reviews (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        UNIQUE KEY unique_review (user_id, product_id)
      )
    `);
    console.log('Reviews table created');

    // Create wishlist table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS wishlist (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        UNIQUE KEY unique_wishlist_item (user_id, product_id)
      )
    `);
    console.log('Wishlist table created');

    // Create addresses table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS addresses (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        label VARCHAR(50),
        street VARCHAR(255) NOT NULL,
        city VARCHAR(100) NOT NULL,
        state VARCHAR(100) NOT NULL,
        zip_code VARCHAR(20) NOT NULL,
        country VARCHAR(100) NOT NULL,
        is_default BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `);
    console.log('Addresses table created');

    // Create payment_methods table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS payment_methods (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        card_type VARCHAR(50) NOT NULL,
        last_four VARCHAR(4) NOT NULL,
        expiry_month INT NOT NULL,
        expiry_year INT NOT NULL,
        is_default BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `);
    console.log('Payment methods table created');

    // Insert sample categories
    await connection.query(`
      INSERT IGNORE INTO categories (id, name, description) VALUES
      (1, 'Electronics', 'Electronic devices and accessories'),
      (2, 'Clothing', 'Apparel and fashion'),
      (3, 'Books', 'Books and reading materials'),
      (4, 'Home & Garden', 'Home improvement and garden supplies'),
      (5, 'Sports', 'Sports equipment and accessories')
    `);
    console.log('Sample categories inserted');

    // Insert sample products
    await connection.query(`
      INSERT IGNORE INTO products (id, name, description, price, stock, category_id, image_url) VALUES
      (1, 'Smartphone X', 'Latest smartphone with advanced features', 699.99, 50, 1, 'https://example.com/phone.jpg'),
      (2, 'Laptop Pro', 'High-performance laptop for professionals', 1299.99, 30, 1, 'https://example.com/laptop.jpg'),
      (3, 'Wireless Headphones', 'Noise-cancelling wireless headphones', 199.99, 100, 1, 'https://example.com/headphones.jpg'),
      (4, 'T-Shirt Classic', 'Comfortable cotton t-shirt', 29.99, 200, 2, 'https://example.com/tshirt.jpg'),
      (5, 'Jeans Denim', 'Stylish denim jeans', 59.99, 150, 2, 'https://example.com/jeans.jpg'),
      (6, 'Programming Guide', 'Complete guide to modern programming', 49.99, 80, 3, 'https://example.com/book.jpg'),
      (7, 'Garden Tool Set', 'Complete set of garden tools', 89.99, 40, 4, 'https://example.com/tools.jpg'),
      (8, 'Yoga Mat', 'Non-slip yoga mat for exercise', 39.99, 120, 5, 'https://example.com/yogamat.jpg'),
      (9, 'Running Shoes', 'Lightweight running shoes', 79.99, 90, 5, 'https://example.com/shoes.jpg'),
      (10, 'Smart Watch', 'Fitness tracking smart watch', 249.99, 60, 1, 'https://example.com/watch.jpg')
    `);
    console.log('Sample products inserted');

    console.log('\nDatabase initialization completed successfully!');
    
  } catch (error) {
    console.error('Database initialization error:', error);
    process.exit(1);
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}

initDatabase();
