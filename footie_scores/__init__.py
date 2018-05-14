import os

PACKAGE_ROOT = os.path.split(__file__)[0]
REPO_ROOT = os.path.join(PACKAGE_ROOT, os.pardir)

if not os.path.exists(os.path.join(REPO_ROOT, 'logs')):
    os.mkdir(os.path.join(REPO_ROOT, 'logs'))
