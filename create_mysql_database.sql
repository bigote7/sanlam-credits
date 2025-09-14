-- Script SQL pour créer la base de données Sanlam Crédits dans MySQL
-- À exécuter dans MySQL Workbench 8.0 CE

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS sanlam_credits_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Utiliser la base de données
USE sanlam_credits_db;

-- Créer un utilisateur dédié (optionnel mais recommandé)
CREATE USER IF NOT EXISTS 'sanlam_user'@'localhost' IDENTIFIED BY 'sanlam_password_2024';
GRANT ALL PRIVILEGES ON sanlam_credits_db.* TO 'sanlam_user'@'localhost';
FLUSH PRIVILEGES;

-- Vérifier que la base a été créée
SHOW DATABASES;

-- Afficher les tables (vide au début)
SHOW TABLES;
