FROM ankane/pgvector:latest

# Initialization scripts are usually mounted or copied to /docker-entrypoint-initdb.d/
COPY ./database/init.sql /docker-entrypoint-initdb.d/
