from setuptools import find_packages, setup

package_name = 'imu_driver'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[
        'setuptools',
        'numpy',
        'adafruit-circuitpython-bno055',
        'adafruit-blinka',
    ],
    zip_safe=True,
    maintainer='tianyi',
    maintainer_email='0.tianyi.lim@gmail.com',
    description='Read data from BNO055 IMU and publish it as ROS2 messages.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'imu_driver_node = imu_driver.imu_driver_node:main'
        ],
    },
)
