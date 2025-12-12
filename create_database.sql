create table if not exists users (
	id bigserial primary key,
	full_name varchar(100),
	email varchar(100) unique,
	user_role varchar(20)
);

create table if not exists credentials (
    id bigint primary key references users(id) on delete cascade,
    username varchar(20) unique,
    pass varchar(100)
);

create table if not exists files (
	id bigserial primary key,
	name varchar(50),
	path varchar(255)
);

create table if not exists models (
	id bigserial primary key,
	name varchar(50),
	description varchar(200),
	model_type varchar(50),
	file_id bigint references files(id)
);

create table if not exists experiments (
	id bigserial primary key,
	name varchar(50),
	description varchar(200),
	model_id bigint references models(id)
);

create table if not exists experiment_parameters (
	id bigserial primary key,
	experiment_id bigint references experiments(id),
	name varchar(50),
	value varchar(50)
);

create table if not exists labs (
	id bigserial primary key references experiments(id),
	name varchar(50),
	instruction varchar(200),
	deadline date
);


create table if not exists experiment_results (
	id bigint primary key references experiments(id) on delete cascade,
	value_name varchar(50),
	value varchar(50)
);


create table if not exists lab_results (
	lab_id bigint references labs(id),
	student_id bigint references users(id),
	value varchar(50),
	submitted_at date,
	primary key (lab_id, student_id)
);


create table if not exists assigned_labs (
	lab_id bigint references labs(id),
	student_id bigint references users(id),
	grade float default null,
	primary key (lab_id, student_id)
);
