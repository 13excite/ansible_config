#!/usr/bin/env python
import sys, os, urllib2, json, re, subprocess, yaml

HOSTS       = "/tmp/test.yml"
GPG         = "/usr/local/bin/gpg"
PASS        = "/path/pass.gpg"

class HostsFromYAML():
    def __init__(self, filename):
        self.filename = filename

    def get_hosts(self):
        try:
            with open(self.filename, 'r') as f:
                data = yaml.load(f)
            if data['hosts']:
                return list(data['hosts'])
        except:
            sys.stderr.write("No hosts file found")
            sys.exit(1)

class GPGPass():
    def __init__(self, *args, **kwargs):
        self.pwds = list()

        try:
            proc = os.popen(GPG + " -d " + PASS, 'r', 1)
            for line in proc:
                m = re.search('^(\S+)\t(.+)$', line)
                if m:
                    self.pwds.append({"re": m.group(1), "pass": m.group(2)})

        except:
           sys.stderr.write("can't decrypt\n")
           sys.exit(1)


    def getpass(self, host):
        for v in self.pwds:
            if v["re"] == host:
                return v["pass"]

            if re.match(v["re"], host):
                return v["pass"]

if len(sys.argv) < 2 or sys.argv[1] != "--list":
    print "{}"
    sys.exit(0)



hostvars = {}
hosts = list()

gpg = GPGPass()

hostmap = HostsFromYAML(HOSTS)

for host in hostmap.get_hosts():
    hosts.append(host)
    hostvars.update({host : {"ansible_become_pass": gpg.getpass(host)}})

inv = {
    "_meta": {
        "hostvars": hostvars
    },
    "all": {
        "hosts":    hosts,
        "vars":     {
            "ansible_become":           "true",
            "ansible_become_method":    "su",
            "ansible_become_user":      "root",
        }
    }
}

#print json.dumps(inv, indent=4)
