import os
import psycopg2
from psycopg2 import pool, extras
from telegram_bot.entities.db_entities import User, Cron
import logging
from telegram_bot import config
import contextlib
import abc
from telegram_bot.cache_.m_cache import CacheHandler
from telegram_bot.entities.domain_entities import ReportParams, Singleton

_logger = logging.getLogger(__name__)
cache = CacheHandler()

#__all__ = [ConnectionManager, CronsRepository, UserRepository]


class ConnectionManager(object):
    def __init__(self):
        self.url = config.global_config.db_url
        _logger.info('db url: %s', os.environ.get('DATABASE_URL'))
        self.pooling = True if config.global_config.uta.pooling == True else False
        self._connect()

    def __del__(self):
        self.close()

    def close(self):
        if self.pooling:
            _logger.warning("Closing pool; future mapping and validation will fail.")
            self._pool.closeall()
        else:
            _logger.warning("Closing connection; future mapping and validation will fail.")
            if self._conn is not None:
                self._conn.close()

    def _connect(self):
        conn_args = dict(
            host=self.url.hostname,
            port=self.url.port,
            database=self.url.database,
            user=self.url.username,
            password=self.url.password,
            )
        if self.pooling:
            _logger.info("Using UTA ThreadedConnectionPool")
            self._pool = psycopg2.pool.ThreadedConnectionPool(config.global_config.uta.pool_min, config.global_config.uta.pool_max, **conn_args)
        else:
            self._conn = psycopg2.connect(**conn_args)
            self._conn.autocommit = True

        self._ensure_schema_exists()

    def get_connection(self):
        return self._pool.getconn() if self._pool else self._conn

    def close_connection(self, connection):
        if self.pooling:
            self._pool.putconn(connection)

    def _ensure_schema_exists(self):
        _logger.info('exist? haha')


_connection_manager = ConnectionManager()


class AbstractRepository(object):

    def __init__(self, mapper):
        self._connection_manager = _connection_manager
        self._connection = _connection_manager.get_connection()
        self.mapper = mapper

    def __del__(self):
        self.close()

    def close(self):
        #self._connection_manager.close_connection(self._connection)
        pass

    @contextlib.contextmanager
    def _get_cursor(self, n_retries=1):
        n_tries_rem = n_retries + 1
        while n_tries_rem > 0:
            try:
                conn = self._connection
                conn.autocommit = True
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("set search_path = {self.url.schema};".format(self=self._connection_manager))

                yield cur

                # contextmanager executes these when context exits
                cur.close()
                #self._connection_manager.close_connection(self._connection)
                break

            except psycopg2.OperationalError:
                _logger.warning("Lost connection to {url}; attempting reconnect".format(url=self._connection_manager.url))
                self._connection = self._connection_manager.get_connection()
                _logger.warning("Reconnected to {url}".format(url=self._connection_manager.url))
            n_tries_rem -= 1
        else:
            # N.B. Probably never reached
            raise Exception("Permanently lost connection to {url} ({n} retries)".format(url=self._connection_manager.url, n=n_retries))

    def _fetchall(self, sql, *args):
        with self._get_cursor() as cur:
            cur.execute(sql, *args)
            return [self.mapper.to_(r) for r in cur.fetchall()]

    def _fetchone(self, sql, *args):
        with self._get_cursor() as cur:
            cur.execute(sql, *args)
            return self.mapper.to_(cur.fetchone())

    # def _update(self, sql, *args):
    #     with self._get_cursor() as cur:
    #         cur.execute(sql, *args)
    #         return cur.fetchall()

    def _create(self, sql, *args):
        with self._get_cursor() as cur:
            cur.execute(sql, *args)
            return cur.fetchone()[0]

    def _update(self, sql, *args):
        with self._get_cursor() as cur:
            cur.execute(sql, *args)
            return cur.rowcount


class AbstractMapper(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def to_(self, *args):
        raise NotImplementedError('users must define to_ to use this base class')

    @abc.abstractmethod
    def from_(self, *args):
        raise NotImplementedError('users must define from_ to use this base class')


class _UserMapper(AbstractMapper):

    def to_(self, dict_row):
        if not dict_row:
            return None
        user = User(dict_row['telegram_id'], active=dict_row['active'], chat_id=dict_row['chat_id'])
        return user

    def from_(self, user):
        pass


class _CronsMapper(AbstractMapper):

    def to_(self, dict_row):
        if not dict_row:
            return None
        id = dict_row['id']
        name = dict_row['name']
        cron_string = dict_row['start_str']
        request_params = ReportParams.decode(dict_row['request_params'])
        active = dict_row['active']
        user_id = dict_row['user_id']
        cron = Cron(id=id, name=name, cron_string=cron_string, request_params=request_params, active=active, user_id=user_id)
        return cron

    def from_(self, cron):
        pass


class CronsRepository(AbstractRepository, metaclass=Singleton):
    _mapper = _CronsMapper()
    _queries = {
        "read_crons_by_user_id":
            """
            SELECT * 
            FROM crons
            WHERE user_id=%s
            """,
        "read_by_id":
            """
            SELECT * 
            FROM crons
            WHERE id=%s
            """,
        "update_cron":
            """
            UPDATE crons
            SET name=%s AND start_str=%s AND active=%s
            WHERE id=%s            
            """,
        "create_cron":
            """
            INSERT INTO crons(name, user_id, start_str, request_params)
            VALUES(%s, %s, %s, %s) RETURNING id;
            """,
        "remove_cron":
            """
            DELETE FROM
            crons
            WHERE id=%s
            """,
        "remove_all_crons":
            """
            DELETE FROM
            crons
            """,
        "read_all":
            """
            SELECT * 
            FROM crons
            """
    }

    def __init__(self):
        super().__init__(mapper=self._mapper)

    def create(self, cron, user_id):
        r = self._create(self._queries['create_cron'], [cron.name, user_id, cron.cron_string, psycopg2.Binary(cron.request_params.encode())])
        return r

    def read(self):
        pass

    def delete(self, id):
        r = self._update(self._queries['remove_cron'], [id])
        return r

    def delete_all(self):
        self._update(self._queries['remove_all_crons'], [])

    def update(self, cron):
        res = self._update(self._queries['update_cron'], [cron.name, cron.cron_string, cron.active, cron.id])
        return res

    def read_by_user_id(self, user_id):
        crons = self._fetchall(self._queries['read_crons_by_user_id'], [user_id])
        return crons if crons else None

    def read_by_id(self, id):
        crons = self._fetchall(self._queries['read_by_id'], [id])
        return crons[0]

    def read_all(self):
        crons = self._fetchall(self._queries['read_all'], [])
        return crons


class UserRepository(AbstractRepository, metaclass=Singleton):
    _mapper = _UserMapper()
    _queries = {
        "user_by_id":
            """
            SELECT * 
            FROM users 
            WHERE telegram_id=%s
            """,
        "all_users":
            """
            SELECT *
            FROM users
            """,
        "insert_user":
            """
            INSERT INTO
            users(telegram_id, active, chat_id)
            VALUES(%s, %s, %s) RETURNING telegram_id;
            """,
        "remove_user":
            """
            DELETE FROM
            users
            WHERE telegram_id=%s
            """,
        "update":
            """
            UPDATE users
            SET active=%s, chat_id=%s
            WHERE telegram_id=%s 
            """
    }

    def __init__(self):
        super().__init__(mapper=self._mapper)

    def create(self, user):
        r = self._create(self._queries['insert_user'], [user.id, user.active, user.chat_id])
        return r

    @cache.cache.cache('user_by_id', expire=600)
    def read_by_id_vs_cache(self, id):
        return self.read_by_id(id)

    def read_by_id(self, id):
        return self._fetchone(self._queries['user_by_id'], [id])

    def read_all(self):
        rows = self._fetchall(self._queries['all_users'], [])
        return rows

    def delete(self, id):
        rows = self._update(self._queries['remove_user'], [id])
        return rows

    def update(self, user):
        rows = self._update(self._queries['update'], [user.active, user.chat_id, user.id])
        return rows
