
-- 三校合同アプリ DB作成

-- データベース追加
CREATE DATABASE book_app
CHARACTER SET utf8mb4;

USE book_app;

-- 会員情報テーブル
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 本情報テーブル
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    book_type VARCHAR(50) NOT NULL,
    cover_image VARCHAR(255),
    summary TEXT,
    recommendation TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
