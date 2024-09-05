from setuptools import setup
import re

def get_version() -> str:
    version = ''

    with open('discord_tools/__init__.py') as file:
        match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', file.read(), re.MULTILINE)
        if not match:
            raise RuntimeError('version not found')

        version = match.group(1)

    if not version:
        raise RuntimeError('version is not found')

    if version.endswith(('a', 'b', 'rc')):
        try:
            import subprocess
            p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if out:
                version += out.decode('utf-8').strip()
            p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if out:
                version += '+g' + out.decode('utf-8').strip()
        except Exception:
            pass

    return version

if __name__ == "__main__":
    setup(version=get_version())
