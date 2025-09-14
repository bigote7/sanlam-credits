-- Script SQL pour créer la base de données Sanlam Crédits
-- À exécuter dans phpMyAdmin de WAMP

CREATE DATABASE IF NOT EXISTS sanlam_credits_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Vérifier que la base a été créée
SHOW DATABASES;

-- Utiliser la base de données
USE sanlam_credits_db;

-- Afficher les tables (vide au début)
SHOW TABLES;
