from setuptools import setup, find_packages

setup(
    name="adaptive-eq",
    version="0.1.0",
    description="Automatically adjusts EasyEffects EQ based on Spotify music",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/adaptive-eq",
    packages=find_packages(),
    package_data={
        '': ['config/*.json', 'icon.png'],
    },
    entry_points={
        'console_scripts': [
            'adaptive-eq=main:main',
            'adaptive-eq-tray=ui.tray:main',
        ],
    },
    install_requires=[
        'spotipy>=2.19.0',
        'pygobject>=3.42.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
    python_requires='>=3.6',
)
