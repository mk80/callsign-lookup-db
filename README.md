# callsign-lookup-db
fcc callsign lookup with database info collection...store name, date, band, and comments on each contact

# postgresql schema setup
create database callsign;

\c callsign

create schema callsign;

create user callsign password 'callsign';

grant all on schema callsign to callsign;

grant all on all tables in schema callsign to callsign;

# new features to add
show all callsign tables
