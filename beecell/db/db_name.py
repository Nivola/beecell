#!/usr/bin/env python
# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte


class DatabaseConstants():
    DB_ENGINE_MARIADB = "mariadb"
    DB_ENGINE_MYSQL = "mysql"
    DB_ENGINE_ORACLE = "oracle"
    DB_ENGINE_POSTGRESQL = "postgresql"
    DB_ENGINE_SQLSERVER = "sqlserver"

    ENVIRONMENT_PRODUCTION = "prd"
    ENVIRONMENT_TEST = "tst"
    ENVIRONMENT_DEVELOPMENT = "dev"
    ENVIRONMENT_TESTING = "col"

    ENVIRONMENTS = [
        {
            "name": "Production",
            "prefix": ENVIRONMENT_PRODUCTION
        },
        {
            "name": "Test",
            "prefix": ENVIRONMENT_TEST
        },
        {
            "name": "Development",
            "prefix": ENVIRONMENT_DEVELOPMENT
        },
        {
            "name": "Testing",
            "prefix": ENVIRONMENT_TESTING
        },
    ]

def get_db_name(db_engine: str, db_acronym: str, environment_prefix: str, db_digit: str):
    engine_prefix = get_engine_prefix(db_engine)

    # db name es. dbs-gspte-col-000o
    db_name = "dbs-%s-%s-%s%s" % (db_acronym, environment_prefix, db_digit, engine_prefix)
    if db_engine == "sqlserver":
        #  es. dbs-acc-de-c102s
        db_name = "dbs-%s-%s%s%s" % (db_acronym, environment_prefix[0:1], db_digit, engine_prefix)

    return db_name

def get_engine_prefix(db_engine: str):
    engine_prefix = None
    if db_engine == DatabaseConstants.DB_ENGINE_MARIADB:
        engine_prefix = "r"
    elif db_engine == DatabaseConstants.DB_ENGINE_MYSQL:
        engine_prefix = "m"
    elif db_engine == DatabaseConstants.DB_ENGINE_ORACLE:
        engine_prefix = "o"
    elif db_engine == DatabaseConstants.DB_ENGINE_POSTGRESQL:
        engine_prefix = "p"
    elif db_engine == DatabaseConstants.DB_ENGINE_SQLSERVER:
        engine_prefix = "s"
    
    return engine_prefix
