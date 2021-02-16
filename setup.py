import setuptools
import versioneer

setuptools.setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    name="miat",
    author="Philippe Desmarais",
    author_email="philippe.desmarais0trash@gmail.com",
    description="Basic python manual image analysis tool using matplotlib",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CephalonAhmes/miat",
    packages=setuptools.find_packages(),
    install_requires = [
    'matplotlib>=3.0.0',
    'numpy>=1.17.0'],
    license='MIT',
    python_requires='>=3.6',
    include_package_data=True,
)