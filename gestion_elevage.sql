-- =============================================
-- SCRIPT SQL COMPLET - FARM MANAGER v2.0
-- =============================================

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS gestion_elevage CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE gestion_elevage;

-- =============================================
-- TABLE 1 : utilisateurs
-- =============================================
CREATE TABLE IF NOT EXISTS utilisateurs (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nom VARCHAR(100) NOT NULL COMMENT 'Nom complet de l''utilisateur',
	email VARCHAR(100) UNIQUE NOT NULL COMMENT 'Email (unique)',
	mot_de_passe VARCHAR(255) NOT NULL COMMENT 'Mot de passe haché (bcrypt)',
	role ENUM('Admin', 'Fermier', 'Veterinaire', 'Gestionnaire', 'Commercial') DEFAULT 'Fermier' COMMENT 'Rôle de l''utilisateur',
	date_creation DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de création du compte'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 2 : lots
-- =============================================
-- Gère les lots d'animaux (poulets, porcs)
CREATE TABLE IF NOT EXISTS lots (
	id INT AUTO_INCREMENT PRIMARY KEY,
	type_animal ENUM('Poulet', 'Porc') NOT NULL COMMENT 'Type d''animal',
	date_arrivee DATE NOT NULL COMMENT 'Date d''arrivée du lot',
	nombre_initial INT NOT NULL COMMENT 'Nombre d''animaux à l''arrivée',
	poids_moyen FLOAT COMMENT 'Poids moyen en kg',
	source VARCHAR(100) COMMENT 'Fournisseur ou source',
	statut ENUM('Actif', 'Vendu', 'Mort', 'Abattu', 'Terminé') DEFAULT 'Actif' COMMENT 'Statut actuel du lot',
	remarque TEXT COMMENT 'Remarques additionnelles',
	cout_initial FLOAT DEFAULT 0 COMMENT 'Coût d''achat initial du lot'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 3 : mortalites
-- =============================================
CREATE TABLE IF NOT EXISTS mortalites (
	id INT AUTO_INCREMENT PRIMARY KEY,
	lot_id INT NOT NULL COMMENT 'Référence au lot',
	date_event DATE NOT NULL COMMENT 'Date de la mortalité',
	quantite INT NOT NULL COMMENT 'Nombre d''animaux morts',
	motif VARCHAR(255) COMMENT 'Raison de la mortalité (optionnel)',
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE CASCADE,
	INDEX idx_mortalites_lot (lot_id),
	INDEX idx_mortalites_date (date_event)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 4 : ventes_animaux 
-- =============================================
CREATE TABLE IF NOT EXISTS ventes_animaux (
	id INT AUTO_INCREMENT PRIMARY KEY,
	lot_id INT NOT NULL COMMENT 'Référence au lot',
	date_vente DATE NOT NULL COMMENT 'Date de la vente',
	quantite INT NOT NULL COMMENT 'Nombre d''animaux vendus',
	prix_unitaire FLOAT NOT NULL COMMENT 'Prix unitaire en FCFA',
	client VARCHAR(100) COMMENT 'Nom du client (si non enregistré)',
	client_id INT NULL COMMENT 'Référence au client enregistré (FK ajoutée plus bas)',
	moyen_paiement ENUM('Espèces', 'Chèque', 'Virement', 'Autre') DEFAULT 'Espèces' COMMENT 'Moyen de paiement',
	statut_paiement ENUM('Payé', 'En attente', 'Partiel') DEFAULT 'Payé' COMMENT 'Statut du paiement',
	notes TEXT COMMENT 'Notes additionnelles sur la vente',
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE CASCADE,
	INDEX idx_ventes_lot (lot_id),
	INDEX idx_ventes_date (date_vente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE : abattages 
-- =============================================
CREATE TABLE IF NOT EXISTS abattages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lot_id INT NOT NULL COMMENT 'Référence au lot',
    date_abattage DATE NOT NULL COMMENT 'Date de l''abattage',
    quantite INT NOT NULL COMMENT 'Nombre d''animaux abattus',
    poids_unitaire FLOAT COMMENT 'Poids moyen à l''abattage (optionnel)',
    FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE CASCADE,
    INDEX idx_abattages_lot (lot_id),
    INDEX idx_abattages_date (date_abattage)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 5 : soins
-- =============================================
CREATE TABLE IF NOT EXISTS soins (
	id INT AUTO_INCREMENT PRIMARY KEY,
	lot_id INT NOT NULL COMMENT 'Référence au lot',
	date_soin DATE NOT NULL COMMENT 'Date du soin',
	type_soin VARCHAR(100) NOT NULL COMMENT 'Type de soin (vaccin, traitement, etc.)',
	description TEXT COMMENT 'Description détaillée',
	cout FLOAT DEFAULT 0 COMMENT 'Coût du soin en FCFA',
	effectue_par VARCHAR(100) COMMENT 'Personne ayant effectué le soin',
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE CASCADE,
	INDEX idx_soins_lot_date (lot_id, date_soin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 6 : depenses
-- =============================================
CREATE TABLE IF NOT EXISTS depenses (
	id INT AUTO_INCREMENT PRIMARY KEY,
	type_depense ENUM('Alimentation', 'Soin', 'Entretien', 'Autre') NOT NULL COMMENT 'Type de dépense',
	description TEXT COMMENT 'Description de la dépense',
	montant FLOAT NOT NULL COMMENT 'Montant en FCFA',
	date_depense DATE NOT NULL COMMENT 'Date de la dépense',
	lot_id INT NULL COMMENT 'Référence au lot (optionnel)',
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE SET NULL,
	INDEX idx_depenses_date (date_depense),
	INDEX idx_depenses_lot (lot_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 7 : recettes
-- =============================================
CREATE TABLE IF NOT EXISTS recettes (
	id INT AUTO_INCREMENT PRIMARY KEY,
	type_recette ENUM('Vente', 'Produit dérivé', 'Autre') NOT NULL COMMENT 'Type de recette',
	montant FLOAT NOT NULL COMMENT 'Montant en FCFA',
	date_recette DATE NOT NULL COMMENT 'Date de la recette',
	lot_id INT NULL COMMENT 'Référence au lot (optionnel)',
	client VARCHAR(100) COMMENT 'Nom du client',
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE SET NULL,
	INDEX idx_recettes_date (date_recette),
	INDEX idx_recettes_lot (lot_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 8 : stocks
-- ==============================================
CREATE TABLE IF NOT EXISTS stocks (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nom_produit VARCHAR(100) NOT NULL COMMENT 'Nom du produit',
	type_produit ENUM('Aliment', 'Médicament', 'Matériel') NOT NULL COMMENT 'Type de produit',
	quantite INT DEFAULT 0 COMMENT 'Quantité en stock',
	unite VARCHAR(50) COMMENT 'Unité de mesure (kg, L, unités, etc.)',
	seuil_alerte INT DEFAULT 10 COMMENT 'Seuil d''alerte (quantité minimale)',
	fournisseur VARCHAR(100) COMMENT 'Nom du fournisseur',
	date_ajout DATE DEFAULT (CURRENT_DATE) COMMENT 'Date d''ajout du produit',
	INDEX idx_stocks_seuil (seuil_alerte, quantite)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 9 : journal_activites
-- =============================================
CREATE TABLE IF NOT EXISTS journal_activites (
	id INT AUTO_INCREMENT PRIMARY KEY,
	utilisateur_id INT NOT NULL COMMENT 'Référence à l''utilisateur',
	action VARCHAR(255) COMMENT 'Description de l''action',
	module VARCHAR(50) COMMENT 'Module concerné (Lots, Soins, Stocks, etc.)',
	details TEXT COMMENT 'Détails de l''action',
	date_action DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date et heure de l''action',
	FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
	INDEX idx_journal_user (utilisateur_id),
	INDEX idx_journal_date (date_action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 10 : soins_preconfigures
-- =============================================
CREATE TABLE IF NOT EXISTS soins_preconfigures (
	id INT AUTO_INCREMENT PRIMARY KEY,
	type_animal ENUM('Poulet', 'Porc') NOT NULL COMMENT 'Type d''animal',
	jour_application INT NOT NULL COMMENT 'Jour dans le cycle (0 = à l''arrivée)',
	type_soin VARCHAR(100) NOT NULL COMMENT 'Type de soin',
	description TEXT COMMENT 'Description du soin',
	cout_estime FLOAT DEFAULT 0 COMMENT 'Coût estimé en FCFA',
	actif BOOLEAN DEFAULT TRUE COMMENT 'Soin actif ou désactivé',
	date_creation DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de création',
	INDEX idx_soins_preconfig_type_jour (type_animal, jour_application)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 11 : parametres
-- =============================================
CREATE TABLE IF NOT EXISTS parametres (
	id INT AUTO_INCREMENT PRIMARY KEY,
	cle VARCHAR(50) UNIQUE NOT NULL COMMENT 'Clé du paramètre',
	valeur VARCHAR(255) COMMENT 'Valeur du paramètre',
	description TEXT COMMENT 'Description du paramètre',
	date_modification DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Date de dernière modification'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 12 : clients
-- =============================================
CREATE TABLE IF NOT EXISTS clients (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nom VARCHAR(100) NOT NULL COMMENT 'Nom du client',
	telephone VARCHAR(20) COMMENT 'Numéro de téléphone',
	email VARCHAR(100) COMMENT 'Adresse email',
	adresse TEXT COMMENT 'Adresse complète',
	type_client ENUM('Particulier', 'Restaurant', 'Boucherie', 'Autre') DEFAULT 'Particulier' COMMENT 'Type de client',
	date_creation DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de création',
	actif BOOLEAN DEFAULT TRUE COMMENT 'Client actif ou désactivé',
	INDEX idx_clients_nom (nom)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- TABLE 13 : produits_derives
-- =============================================
CREATE TABLE IF NOT EXISTS produits_derives (
	id INT AUTO_INCREMENT PRIMARY KEY,
	type_produit ENUM('Œufs', 'Fumier', 'Plumes', 'Autre') NOT NULL COMMENT 'Type de produit',
	quantite DECIMAL(10,2) NOT NULL COMMENT 'Quantité vendue',
	unite VARCHAR(50) NOT NULL COMMENT 'Unité de mesure (kg, unités, etc.)',
	prix_unitaire FLOAT NOT NULL COMMENT 'Prix unitaire en FCFA',
	date_vente DATE NOT NULL COMMENT 'Date de vente',
	client_id INT NULL COMMENT 'Référence au client enregistré',
	client_nom VARCHAR(100) COMMENT 'Nom du client si non enregistré',
	montant_total FLOAT NOT NULL COMMENT 'Montant total en FCFA',
	moyen_paiement ENUM('Espèces', 'Chèque', 'Virement', 'Autre') DEFAULT 'Espèces' COMMENT 'Moyen de paiement',
	notes TEXT COMMENT 'Notes additionnelles',
	FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
	INDEX idx_produits_derives_date (date_vente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- CONTRAINTES DE CLÉS ÉTRANGÈRES SUPPLÉMENTAIRES
-- =============================================
-- Ajouter la contrainte FK pour ventes_animaux -> clients
-- (créée après la table clients pour éviter les erreurs)

-- Vérifier si la contrainte existe déjà avant de l'ajouter
SET @constraint_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = 'gestion_elevage'
    AND TABLE_NAME = 'ventes_animaux'
    AND CONSTRAINT_NAME = 'fk_vente_client'
);

SET @sql = IF(@constraint_exists = 0,
    'ALTER TABLE ventes_animaux ADD CONSTRAINT fk_vente_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL',
    'SELECT "Contrainte fk_vente_client existe déjà"'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Ajouter l'index sur client_id dans ventes_animaux
-- (Si l'index existe déjà, vous pouvez ignorer l'erreur)
CREATE INDEX idx_ventes_client ON ventes_animaux(client_id);

-- =============================================
-- INDEX SUPPLÉMENTAIRES POUR PERFORMANCE
-- =============================================
-- Index sur lots
CREATE INDEX idx_lots_date_arrivee ON lots(date_arrivee);
CREATE INDEX idx_lots_statut ON lots(statut);
CREATE INDEX idx_lots_type ON lots(type_animal);

-- =============================================
-- DONNÉES PAR DÉFAUT
-- =============================================

-- Soins préconfigurés pour poulets (cycle 47 jours)
INSERT INTO soins_preconfigures (type_animal, jour_application, type_soin, description, cout_estime) VALUES
('Poulet', 1, 'Vaccin Marek', 'Vaccination contre la maladie de Marek (si poussin)', 500),
('Poulet', 7, 'Vaccin Gumboro', 'Première vaccination contre la maladie de Gumboro', 800),
('Poulet', 14, 'Vaccin Newcastle', 'Vaccination contre la maladie de Newcastle', 1000),
('Poulet', 21, 'Rappel Gumboro', 'Rappel vaccination Gumboro', 800),
('Poulet', 28, 'Vermifuge', 'Traitement vermifuge', 600),
('Poulet', 35, 'Complément Vitamines', 'Complément vitaminique pour croissance', 400)
ON DUPLICATE KEY UPDATE type_soin=type_soin;

-- Soins préconfigurés pour porcs
INSERT INTO soins_preconfigures (type_animal, jour_application, type_soin, description, cout_estime) VALUES
('Porc', 0, 'Vaccin Circovirus', 'Vaccination contre le circovirus porcin à l''arrivée', 1500),
('Porc', 14, 'Vermifuge', 'Traitement vermifuge première fois', 800),
('Porc', 42, 'Vaccin Rouget', 'Vaccination contre le rouget', 1200),
('Porc', 70, 'Rappel Vaccins', 'Rappel des vaccinations principales', 1500)
ON DUPLICATE KEY UPDATE type_soin=type_soin;

-- Paramètres par défaut de l'application
INSERT INTO parametres (cle, valeur, description) VALUES
('seuil_mortalite', '3', 'Seuil d''alerte mortalité en pourcentage'),
('duree_cycle_poulets', '47', 'Durée maximale cycle poulets en jours'),
('devise', 'FCFA', 'Devise utilisée dans l''application'),
('format_date', 'DD/MM/YYYY', 'Format d''affichage des dates'),
('alerte_stock_jours', '7', 'Nombre de jours avant alerte fin de cycle'),
('seuil_mortalite_critique', '5', 'Seuil critique de mortalité en pourcentage')
ON DUPLICATE KEY UPDATE valeur=valeur;
