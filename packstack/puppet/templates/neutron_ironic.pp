
class { 'neutron::plugins::ml2':
  type_drivers  => 'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver',
}

