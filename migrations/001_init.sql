-- =============================================
-- BASE DE DONNÉES : gestion_elevage
-- Description : Base pour l'application de gestion d'élevage (poulets & porcs)
-- Auteur : Astride De Priso
-- Date : 2025-11-04
-- =============================================

CREATE DATABASE IF NOT EXISTS gestion_elevage CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE gestion_elevage;

-- ===============================
-- TABLE : utilisateurs
-- ===============================
CREATE TABLE IF NOT EXISTS utilisateurs (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nom VARCHAR(100) NOT NULL,
	email VARCHAR(100) UNIQUE NOT NULL,
	mot_de_passe VARCHAR(255) NOT NULL,
	role ENUM('Admin', 'Fermier', 'Veterinaire', 'Commercial') DEFAULT 'Fermier',
	date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- TABLE : lots
-- ===============================
CREATE TABLE IF NOT EXISTS lots (
	id INT AUTO_INCREMENT PRIMARY KEY,
	type_animal ENUM('Poulet', 'Porc') NOT NULL,
	date_arrivee DATE NOT NULL,
	nombre_initial INT NOT NULL,
	poids_moyen FLOAT,
	source VARCHAR(100),
	statut ENUM('Actif', 'Vendu', 'Mort', 'Abattu') DEFAULT 'Actif',
	remarque TEXT
);

-- ===============================
-- TABLE : soins
-- ===============================
CREATE TABLE IF NOT EXISTS soins (
	id INT AUTO_INCREMENT PRIMARY KEY,
	lot_id INT NOT NULL,
	date_soin DATE NOT NULL,
	type_soin VARCHAR(100) NOT NULL,
	description TEXT,
	cout FLOAT DEFAULT 0,
	effectue_par VARCHAR(100),
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE CASCADE
);

-- ===============================
-- TABLE : depenses
-- ===============================
CREATE TABLE IF NOT EXISTS depenses (
	id INT AUTO_INCREMENT PRIMARY KEY,
	type_depense ENUM('Alimentation', 'Soin', 'Entretien', 'Autre') NOT NULL,
	description TEXT,
	montant FLOAT NOT NULL,
	date_depense DATE NOT NULL,
	lot_id INT NULL,
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE SET NULL
);

-- ===============================
-- TABLE : recettes
-- ===============================
CREATE TABLE IF NOT EXISTS recettes (
	id INT AUTO_INCREMENT PRIMARY KEY,
	type_recette ENUM('Vente', 'Produit dérivé', 'Autre') NOT NULL,
	montant FLOAT NOT NULL,
	date_recette DATE NOT NULL,
	lot_id INT NULL,
	client VARCHAR(100),
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE SET NULL
);

-- ===============================
-- TABLE : stocks
-- ===============================
CREATE TABLE IF NOT EXISTS stocks (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nom_produit VARCHAR(100) NOT NULL,
	type_produit ENUM('Aliment', 'Médicament', 'Matériel') NOT NULL,
	quantite INT DEFAULT 0,
	unite VARCHAR(50),
	date_ajout DATE DEFAULT (CURRENT_DATE)
);

-- ===============================
-- TABLE : journal_activites
-- ===============================
CREATE TABLE IF NOT EXISTS journal_activites (
	id INT AUTO_INCREMENT PRIMARY KEY,
	utilisateur_id INT NOT NULL,
	action VARCHAR(255),
	date_action DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);


