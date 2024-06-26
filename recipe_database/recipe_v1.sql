create database repdb;

use repdb;

-- fks for duration table aren't working, can use ALTER TABLE to add them later
create table recipe (
recipeID int auto_increment primary key,
recipeName varchar (250) not null,
recipeDescription text,
cuisineID int not null,
durationID int not null,
prepTime time not null,
cookTime time,
servingSize int not null,
Instructions text not null,
foreign key (cuisineID) references cuisine (cuisineID)
-- foreign key (durationID) references duration (durationID),
-- foreign key (prepTime) references duration (prepTime),
-- foreign key (cookTime) references duration (cookTime)
); 

create table ingredient (
ingredientID int auto_increment primary key,
ingredientName varchar(50) not null,
allergen boolean not null
);

create table unit (
unitID int auto_increment primary key,
unitName varchar(50) not null
);

create table quantity (
quantityID int auto_increment primary key,
quantityAmount float not null
);

create table cuisine (
cuisineID int auto_increment primary key,
cuisine_type varchar(100) not null
);

-- cookTime doesn't have [not null] in case some recipes don't require cooking
-- need to double check if time or varchar data type would be more suitable for this table
create table duration (
durationID int auto_increment primary key,
overallDuration time not null,
prepTime time not null,
cookTime time
);

create table recipeStep (
stepID int auto_increment primary key,
recipeID int not null,
stepNumber int not null,
stepDescription text not null,
foreign key (recipeID) references recipe (recipeID)
);

create table dietaryRequirement (
dietaryID int auto_increment primary key,
dietaryType varchar(50) not null
);

create table allergy (
allergyID int auto_increment primary key,
allergyType varchar(50) not null
);

create table tool (
toolID int auto_increment primary key,
toolName varchar(50) not null
);

create table recipeImage (
imageID int auto_increment primary key,
recipeID int not null,
imageSource varchar(100) not null,
foreign key (recipeID) references recipe (recipeID)
);



