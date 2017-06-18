import os
import click
from app import create_app, db
from app.models import User, Role, Permission, Tool, Category
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or "default")
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role,
				Permission=Permission, Tool=Tool, Category=Category)


@app.cli.command()
@click.option('--length', default=25, help='Profile stack length')
@click.option('--profile-dir', default=None, help='Profile directory')
def profile(length=25, profile_dir=None):
	"""Start the application under the code profiler."""
	from werkzeug.contrib.profiler import ProfilerMiddleware
	app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
	app.run()


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='aaa')
def test():
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)


def deploy():
	"""Run deployment tasks."""
	from flask_migrate import upgrade
	from app.models import Role

	# migrate database to latest revision
	upgrade()

	# create user roles
	Role.insert_roles()


if __name__ == "__main__":
	app.run()