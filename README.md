# restore-pv-state
Restoring k8s bounding states between  PVC and PV using NFS

### Prerequesties
kubectl installed.

### Backup PV/PVC states
````
$ export KUBECONFIG=backup-cluster-admin-kubeconfig.yaml
$ python pydef.py -b
````
### Restore PV/PVC states
````
$ export KUBECONFIG=restore-cluster-admin-kubeconfig.yaml
$ python pydef.py -r
````
