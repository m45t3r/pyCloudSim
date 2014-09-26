
#+----+-----------+-----------+------+-----------+---+-------+---+-------------+
#| ID | Name      | Memory_MB | Disk | Ephemeral | / | VCPUs | / | extra_specs |
#| 1  | m1.tiny   | 512       | 1    | 0         | / | 1     | / | {}          |
#| 2  | m1.small  | 2048      | 10   | 20        | \ | 1     | \ | {}          |
#| 3  | m1.medium | 4096      | 10   | 40        | / | 2     | / | {}          |
#| 4  | m1.large  | 8192      | 10   | 80        | \ | 4     | \ | {}          |
#| 5  | m1.xlarge | 16384     | 10   | 160       | / | 8     | / | {}          |
#+----+-----------+-----------+------+-----------+---+-------+---+-------------+


from collections import defaultdict


flavors = defaultdict(defaultdict)

flavors['tiny']['vcpus'] = 1
flavors['tiny']['mem'] = 512

flavors['small']['vcpus'] = 1
flavors['small']['mem'] = 2048

flavors['medium']['vcpus'] = 2
flavors['medium']['mem'] = 4096

flavors['large']['vcpus'] = 4
flavors['large']['mem'] = 8192

flavors['xlarge']['vcpus'] = 8
flavors['xlarge']['mem'] = 16384
