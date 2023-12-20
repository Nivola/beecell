# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

from functools import wraps
import logging
from sqlalchemy.exc import IntegrityError, DBAPIError

logger = logging.getLogger(__name__)


class TransactionError(Exception):
    pass


class QueryError(Exception):
    pass


def transaction(manager):
    """Use this decorator to transform a function that contains delete, insert and update statement in a transaction.

    :param manager: Object with method get_session(), release_session()
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            try:
                session = manager.get_session()
            except Exception as ex:
                raise TransactionError(ex)

            try:
                logger.debug("Transaction - start")
                res = fn(session, *args, **kwargs)
                session.commit()
                logger.debug("Transaction - stop")
                return res
            except IntegrityError as ex:
                session.rollback()
                logger.error("Transaction - error: %s" % ex)
                raise TransactionError(ex)
            except DBAPIError as ex:
                session.rollback()
                logger.error("Transaction - error: %s" % ex)
                raise TransactionError(ex)
            finally:
                manager.release_session(session)

        return decorated_view

    return wrapper


def query(manager):
    """Use this decorator to transform a function that contains delete, insert and update statement in a transaction.

    :param manager: Object with method get_session(), release_session()
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            try:
                session = manager.get_session()
            except Exception as ex:
                raise QueryError(ex)

            try:
                logger.debug("Query - start")
                res = fn(session, *args, **kwargs)
                logger.debug("Query - stop")
                return res
            except DBAPIError as ex:
                logger.error("Query - error: %s" % ex)
                raise QueryError(ex)
            finally:
                manager.release_session(session)

        return decorated_view

    return wrapper
