================
collectd-systemd
================

.. image:: https://travis-ci.org/mbachry/collectd-systemd.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/mbachry/collectd-systemd

.. image:: https://coveralls.io/repos/github/mbachry/collectd-systemd/badge.svg?branch=master
    :alt: Coverage
    :target: https://coveralls.io/github/mbachry/collectd-systemd?branch=master

A `collectd`_ plugin which checks if given `systemd`_ units are in
"active" state and sends `graphite`_ metrics with ``1.0`` or ``0.0``
value.

The plugin is particularly useful together with `grafana's alerting`_.

.. _collectd: https://collectd.org/
.. _systemd: https://www.freedesktop.org/wiki/Software/systemd/
.. _graphite: https://graphite.readthedocs.io/en/latest/overview.html
.. _grafana's alerting: https://github.com/grafana/grafana/issues/2209

Quick start
-----------

Make sure Python dbus bindings are installed in your system:

* Debian/Ubuntu: ``sudo apt-get install python-dbus``

* Fedora/CentOS: ``sudo yum install dbus-python``

Copy ``collectd_systemd.py`` to collectd Python plugin directory
(usually ``/usr/lib64/collectd/python/`` or
``/usr/lib/collectd/python/``). Add following snippet do
``/etc/collectd.conf``::

    LoadPlugin python

    <Plugin python>
        ModulePath "/usr/lib64/collectd/python"
        Import "collectd_systemd"

        <Module collectd_systemd>
            Unit "nginx.service" "postgresql.service" "mnt-nfs.mount"
        </Module>
    </Plugin>

Restart collectd daemon and open grafana web ui. Add a new graph with
following query::

    aliasSub(collectd.*.systemd-*.gauge-active, '.+systemd-(.+)\..+', '\1')

You should see all configured systemd units in the graph. Now it's
enough to add an alert for values lower than ``1.0`` to be paged when
units are down.

Configuration
-------------

Following configuration options are supported:

* ``Unit``: one or more systemd units to monitor. Wrap unit names in quotes and
  separate multiple units with spaces.

* ``Interval``: check interval. It's ok to keep the default (60 seconds)

* ``Verbose``: enable verbose logging (off by default)

Running tests
-------------

Install tox using pip or Linux package manager.

Type ``tox`` to run tests.
