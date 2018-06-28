use snapngo_db;

drop table if exists tasks;
drop table if exists users;

-- create a table for the users
create table users (
	id varchar(30),
	name varchar(50),
	primary key (id)
	)
	-- table constraint
	ENGINE = InnoDB;

-- create a table for the tasks
create table tasks (
	id int(4) unsigned auto_increment,
  location varchar(100),
  deadline datetime,
  compensation decimal(4,2),
  tweetSent bit default 0,
  tweetID varchar(30),
  tweetSentTime datetime,
  assignedTo varchar(30),
  taskSubmitted bit default 0,
  submissionPhotoLink varchar(100),
  submissionTime datetime,
	primary key (id),
	INDEX(assignedTo),
	foreign key (assignedTo) references users(id)
	)
	-- table constraint
	ENGINE = InnoDB;
