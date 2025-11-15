-- Événements de lots: mortalités et ventes partielles
USE gestion_elevage;

CREATE TABLE IF NOT EXISTS mortalites (
	id INT AUTO_INCREMENT PRIMARY KEY,
	lot_id INT NOT NULL,
	date_event DATE NOT NULL,
	quantite INT NOT NULL,
	motif VARCHAR(255),
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ventes_animaux (
	id INT AUTO_INCREMENT PRIMARY KEY,
	lot_id INT NOT NULL,
	date_vente DATE NOT NULL,
	quantite INT NOT NULL,
	prix_unitaire FLOAT NOT NULL,
	client VARCHAR(100),
	FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE CASCADE
);


