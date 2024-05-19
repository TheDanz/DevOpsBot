FROM postgres:latest

ARG REPLUSER
ARG REPLPASSWORD
ARG DBNAME

RUN apt update && apt install sed
COPY init.sql /init.sql
RUN sed -i 's/replaceREPLUSER/'"$REPLUSER"'/g' /init.sql
RUN sed -i 's/replaceREPLPASSWORD/'"$REPLPASSWORD"'/g' /init.sql
RUN sed -i 's/replaceREPLPASSWORD/'"$REPLPASSWORD"'/g' /init.sql
RUN sed -i 's/replaceDBNAME/'"$DBNAME"'/g' /init.sql
RUN mv /init.sql /docker-entrypoint-initdb.d/init.sql


RUN echo "wal_level=replica" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "hot_standby=on" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "max_wal_senders=10" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "max_replication_slots=10" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "hot_standby_feedback=on" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "log_replication_commands=on" >> /usr/share/postgresql/postgresql.conf.sample