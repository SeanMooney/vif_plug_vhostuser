#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from os_vif import objects
from os_vif import plugin

from vif_plug_vhostuser import linux_net
from vif_plug_vhostuser import processutils

PLUGIN_NAME = 'vhostuser'


class VhostuserPlugin(plugin.PluginBase):
    """An VIF type that plugs into an OVS port using the vhostuser device
    interface.
    """

    def __init__(self, **config):
        processutils.configure(**config)
        linux_net.configure(**config)
        self.ovs_vsctl_timeout = config.get('ovs_vsctl_timeout', 30)

    def get_supported_vifs(self):
        return set([objects.PluginVIFSupport(PLUGIN_NAME, '1.0', '1.0')])

    def plug(self, instance, vif):
        if vif.vhostuser_ovs_plug:
            iface_id = vif.ovs_interfaceid
            port_name = os.path.basename(vif.vhostuser_socket)
            linux_net.create_ovs_vif_port(vif.bridge_name,
                                          port_name, iface_id,
                                          vif.address, instance.uuid,
                                          timeout=self.ovs_vsctl_timeout,
                                          type="dpdkvhostuser")

    def unplug(self, vif):
        if vif.ovs_hybrid_plug:
            port_name = os.path.basename(vif.vhostuser_socket)
            linux_net.delete_ovs_vif_port(vif.bridge_name, port_name,
                                          timeout=self.ovs_vsctl_timeout)
