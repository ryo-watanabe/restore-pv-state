# restore-pv-state
Restoring k8s bounding states between  PVC and PV using NFS

# Backup PV/PVC states
````
export KUBECONFIG=backup-cluster-kubeconfig.yaml
python pydef.py -b
````
# Restore PV/PVC states
````
export KUBECONFIG=restore-cluster-kubeconfig.yaml
python pydef.py -r
````
