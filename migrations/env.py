import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# C'est l'objet de configuration Alembic, qui permet
# d'accéder aux valeurs du fichier .ini utilisé.
config = context.config

# Interprétation du fichier de configuration pour le logging Python.
# Cette ligne initialise les loggers.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # Fonctionne avec Flask-SQLAlchemy<3 et Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # Fonctionne avec Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# Ajoutez l'objet MetaData de votre modèle ici
# pour le support de l''autogenerate'
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# D'autres valeurs de la configuration, définies par les besoins de env.py,
# peuvent être acquises :
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Exécute les migrations en mode 'offline'.

    Cela configure le contexte avec juste une URL
    et non un Engine, bien qu'un Engine soit acceptable
    ici aussi. En sautant la création de l'Engine
    nous n'avons même pas besoin qu'une DBAPI soit disponible.

    Les appels à context.execute() ici émettent la chaîne donnée vers
    la sortie du script.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Exécute les migrations en mode 'online'.

    Dans ce scénario, nous devons créer un Engine
    et associer une connexion au contexte.

    """

    # ce callback est utilisé pour empêcher une auto-migration d'être générée
    # quand il n'y a aucun changement dans le schéma
    # référence : http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
