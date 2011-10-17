CREATE TABLE rater_accuracy (
	id int(11) NOT NULL auto_increment, 
	user_id int(11) NOT NULL, 
	accuracy decimal(5,2) default null,
	PRIMARY KEY(`id`)
	)
