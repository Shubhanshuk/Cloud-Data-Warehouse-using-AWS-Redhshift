# Cloud-Data-Warehouse-using-AWS-Redhshift

## Project Scope
A music streaming startup, Sparkify, has grown their user base and song database and want to move their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

As their data engineer, you are tasked with building an ETL pipeline that extracts their data from S3, stages them in Redshift, and transforms data into a set of dimensional tables for their analytics team to continue finding insights in what songs their users are listening to. You'll be able to test your database and ETL pipeline by running queries given to you by the analytics team from Sparkify and compare your results with their expected results.

Their user activity and songs metadata data resides in json files in S3. The goal of the current project is to build an ETL pipeline that extracts their data from S3, stages them in Redshift, and transforms data into a set of dimensional tables for their analytics team to continue finding insights in what songs their users are listening to. 

## Steps to run the project

1. Fill the required infromation and save it as *dwh.cfg*  file. 

```
[AWS]
KEY=
SECRET=

[CLUSTER]
HOST=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_PORT=

[IAM_ROLE]
ARN=

[S3]
LOG_DATA='s3://udacity-dend/log_data'
LOG_JSONPATH='s3://udacity-dend/log_json_path.json'
SONG_DATA='s3://udacity-dend/song_data'


[DWH]
DWH_CLUSTER_IDENTIFIER=dwhCluster
DWH_CLUSTER_TYPE=multi-node
DWH_NUM_NODES=4
DWH_NODE_TYPE=dc2.large
DWH_IAM_ROLE_NAME=dwhRole


```


2. Run the *create_cluster* script. This script will create the AWS role and Redshift cluster. 

    `$ python create_cluster.py`

3. Run the *create_tables* script. This script will drop and create the staging tables as well as dimensional tables everytime this script is executed. 

    `$ python create_tables.py`

4. Run the *etl* script. this script extract data from the files in S3, stage it in redshift, and finally store it in the dimensional tables.

    `$ python etl.py`


## Project structure

This project includes five script files:

- analytics.py runs a few queries on the created star schema to validate that the project has been completed successfully.
- create_cluster.py is where the AWS components for this project are created programmatically
- create_table.py is where fact and dimension tables for the star schema in Redshift are created.
- etl.py is where data gets loaded from S3 into staging tables on Redshift and then processed into the analytics tables on Redshift.
- sql_queries.py where SQL statements are defined, which are then used by etl.py, create_table.py and analytics.py.
- README.md is current file.
- requirements.txt with python dependencies needed to run the project

## Database schema design
State and justify your database schema design and ETL pipeline.

#### Staging Tables
- staging_events
- staging_songs

####  Fact Table
- songplays - records in event data associated with song plays i.e. records with page NextSong - 
*songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent*

#### Dimension Tables
- users - users in the app - 
*user_id, first_name, last_name, gender, level*
- songs - songs in music database - 
*song_id, title, artist_id, year, duration*
- artists - artists in music database - 
*artist_id, name, location, lattitude, longitude*
- time - timestamps of records in songplays broken down into specific units - 
*start_time, hour, day, week, month, year, weekday*


### Steps followed on this project

1. Setup AWS Infrastructure using code.  

- Create AWS role that can access S3 and AWS redshift
- Add AWS ROLE IRN in dwh.cfg and attach the required policy
- Create the AWS reshift cluster based on the onfigurations set in .cfg file

2. Create Table Schemas
- Write a SQL CREATE statement for each of these tables in sql_queries.py. 
- Write the DROP table queries
- Write the Create table queries
- Write the COPY command to extarct the data from S3 to Redhsift staging tables
- Complete the logic in create_tables.py to connect to the database and create these tables
- Add redshift database and IAM role info to dwh.cfg.

3. Build ETL Pipeline
- Implement the logic in etl.py to load data from S3 to staging tables on Redshift.
- Implement the logic in etl.py to load data from staging tables to analytics tables on Redshift.
- Test by running etl.py after running create_tables.py and running the analytic queries on your Redshift database.
- Delete your redshift cluster when finished.
