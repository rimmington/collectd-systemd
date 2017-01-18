import dbus
import collectd


class SystemD(object):
    def __init__(self):
        self.plugin_name = 'systemd'
        self.interval = 60.0
        self.verbose_logging = False
        self.unit_names = []
        self.units = {}

    def log_verbose(self, msg):
        if not self.verbose_logging:
            return
        collectd.info('{} plugin [verbose]: {}'.format(self.plugin_name, msg))

    def init_dbus(self):
        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object('org.freedesktop.systemd1',
                                                          '/org/freedesktop/systemd1'),
                                      'org.freedesktop.systemd1.Manager')

    def get_unit(self, name):
        if name not in self.units:
            try:
                unit = dbus.Interface(self.bus.get_object('org.freedesktop.systemd1',
                                                          self.manager.GetUnit(name)),
                                      'org.freedesktop.DBus.Properties')
            except dbus.exceptions.DBusException as e:
                collectd.warning('{} plugin: failed to monitor unit {}: {}'.format(
                    self.plugin_name, name, e))
                return
            self.units[name] = unit
        return self.units[name]

    def get_unit_state(self, name):
        unit = self.get_unit(name)
        if not unit:
            return 'broken'
        else:
            return unit.Get('org.freedesktop.systemd1.Unit', 'ActiveState')

    def configure_callback(self, conf):
        for node in conf.children:
            vals = [str(v) for v in node.values]
            if node.key == 'Unit':
                self.unit_names = vals
            elif node.key == 'Interval':
                self.interval = float(vals[0])
            elif node.key == 'Verbose':
                self.verbose_logging = (vals[0].lower() == 'true')
            else:
                raise ValueError('{} plugin: Unknown config key: {}'
                                 .format(self.plugin_name, node.key))
        if not self.unit_names:
            self.log_verbose('No units defined in configuration')
            return
        self.init_dbus()
        collectd.register_read(self.read_callback, self.interval)
        self.log_verbose('Configured with units={}, interval={}'
                         .format(self.unit_names, self.interval))

    def read_callback(self):
        self.log_verbose('Read callback called')
        for name in self.unit_names:
            state = self.get_unit_state(name)
            value = (1.0 if state == 'active' else 0.0)
            self.log_verbose('Sending value: {}.{}={} (state={})'
                             .format(self.plugin_name, name, value, state))
            val = collectd.Values(
                type='gauge',
                plugin=self.plugin_name,
                plugin_instance=name,
                type_instance='active',
                values=[value])
            val.dispatch()


mon = SystemD()
collectd.register_config(mon.configure_callback)
