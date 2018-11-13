#!/usr/bin/python
# -*- coding: UTF-8 -*-

import commands
import json
import argparse
import time

def localCommand(com):
    ret_ch = commands.getstatusoutput(com)
    if ret_ch[0]:
        print(ret_ch[1])
        exit(1)
    return ret_ch[1]

def isPVBounded(pv_name):
    val = localCommand("kubectl get pv " + pv["metadata"]["name"] + " -o json") 
    return json.loads(val)["status"]["phase"] == "Bound"

# 引数処理

parser = argparse.ArgumentParser()
parser.add_argument("--file", "-f", type=str, help="Set backup file path (default:pv_backup.json)")
parser.add_argument("--backup", "-b", action="store_true", help="Do backup")
parser.add_argument("--restore", "-r", action="store_true", help="Do restore")
parser.add_argument("--verbose", "-v", action="store_true", help="Debug print")
args = parser.parse_args()
if args.verbose:
    print(args)
if not args.file:
    args.file = "pv_backup.json"

if args.backup:
    
    backup = {}
    print("Backing up PV/PVC resources.")

    val = localCommand("kubectl get pv -o json")
    data = json.loads(val)
    backup["pvs"] = data["items"]

    val = localCommand("kubectl get pvc --all-namespaces -o json")
    data = json.loads(val)
    backup["pvcs"] = data["items"]
    
    val = localCommand("kubectl get ns -o json")
    data = json.loads(val)
    backup["namespaces"] = data["items"]
    
    f = open(args.file, 'w')
    json.dump(backup, f)
    f.close()

elif args.restore:
    print("Restoring PV/PVC definitions and bounding status.")

    f = open(args.file, 'r')
    backup = json.load(f)
    f.close()

#    print("Restoring namespaces")

    # Get rancher project ids
#    val = localCommand("kubectl get ns kube-system -o json") 
#    data = json.loads(val)
#    system_annotation_prj = data["metadata"]["annotations"]["field.cattle.io/projectId"]
#    system_label_prj = data["metadata"]["labels"]["field.cattle.io/projectId"]
#    bk_system_annotation_prj = ""
#    bk_default_annotation_prj = ""
#    val = localCommand("kubectl get ns default -o json") 
#    data = json.loads(val)
#    default_annotation_prj = data["metadata"]["annotations"]["field.cattle.io/projectId"]
#    default_label_prj = data["metadata"]["labels"]["field.cattle.io/projectId"]
#    for ns in backup["namespaces"]:
#        if ns["metadata"]["name"] == "kube-system":
#            bk_system_annotation_prj = ns["metadata"]["annotations"]["field.cattle.io/projectId"]
#        if ns["metadata"]["name"] == "default":
#            bk_default_annotation_prj = ns["metadata"]["annotations"]["field.cattle.io/projectId"]
#        
#    for ns in backup["namespaces"]:
#
#        restore_ns = {}
#        restore_ns["apiVersion"] = ns["apiVersion"]
#        restore_ns["kind"] = ns["kind"]
#        restore_ns["metadata"] = {}
#        restore_ns["metadata"]["name"] = ns["metadata"]["name"]
#        restore_ns["metadata"]["annotations"] = {}
#        restore_ns["metadata"]["labels"] = {}
        
        # Set rancher project ids:
#        if ns["metadata"]["annotations"]["field.cattle.io/projectId"] == bk_system_annotation_prj:
#            restore_ns["metadata"]["annotations"]["field.cattle.io/projectId"] = system_annotation_prj
#            restore_ns["metadata"]["labels"]["field.cattle.io/projectId"] = system_label_prj
#        if ns["metadata"]["annotations"]["field.cattle.io/projectId"] == bk_default_annotation_prj:
#            restore_ns["metadata"]["annotations"]["field.cattle.io/projectId"] = default_annotation_prj
#            restore_ns["metadata"]["labels"]["field.cattle.io/projectId"] = default_label_prj#
#
#        val = localCommand("echo '" + json.dumps(restore_ns) + "' | kubectl apply -f -") 

    for pv in backup["pvs"]:

        if pv["status"]["phase"] == "Bound":
            pvc = {}
            for pvc_item in backup["pvcs"]:
                if pvc_item["metadata"]["namespace"] == pv["spec"]["claimRef"]["namespace"] and pvc_item["metadata"]["name"] == pv["spec"]["claimRef"]["name"]:
                    pvc = pvc_item
                    break
            if not pvc:
                print("PVC not found for PV:" + pv["metadata"]["name"])
                exit(1)

            print("Creating and bounding PV:" + pv["metadata"]["name"] + " <--> PVC:" + pvc["metadata"]["namespace"] + "/" + pvc["metadata"]["name"])
            
            restore_pv = {}
            restore_pv["apiVersion"] = pv["apiVersion"]
            restore_pv["kind"] = pv["kind"]
            restore_pv["spec"] = {}
            restore_pv["spec"]["storageClassName"] = pv["spec"]["storageClassName"]
            restore_pv["spec"]["capacity"] = pv["spec"]["capacity"]
            restore_pv["spec"]["persistentVolumeReclaimPolicy"] = pv["spec"]["persistentVolumeReclaimPolicy"]
            restore_pv["spec"]["accessModes"] = pv["spec"]["accessModes"]
            restore_pv["spec"]["nfs"] = pv["spec"]["nfs"]
            restore_pv["metadata"] = {}
            restore_pv["metadata"]["name"] = pv["metadata"]["name"]
            restore_pv["metadata"]["annotations"] = pv["metadata"]["annotations"]
            val = localCommand("echo '" + json.dumps(restore_pv) + "' | kubectl apply -f -") 

            restore_pvc = {}
            restore_pvc["apiVersion"] = pvc["apiVersion"]
            restore_pvc["kind"] = pvc["kind"]
            restore_pvc["spec"] = {}
            restore_pvc["spec"]["storageClassName"] = pvc["spec"]["storageClassName"]
            restore_pvc["spec"]["resources"] = pvc["spec"]["resources"]
            restore_pvc["spec"]["accessModes"] = pvc["spec"]["accessModes"]
            restore_pvc["metadata"] = {}
            restore_pvc["metadata"]["name"] = pvc["metadata"]["name"]
            restore_pvc["metadata"]["namespace"] = pvc["metadata"]["namespace"]
            restore_pvc["metadata"]["annotations"] = pv["metadata"]["annotations"]
            val = localCommand("echo '" + json.dumps(restore_pvc) + "' | kubectl apply -f -") 

            while not isPVBounded(pv["metadata"]["name"]):
                time.sleep(2)

else:
    print("Please set action --backup or --restore.")
    exit(1)

exit(0)
