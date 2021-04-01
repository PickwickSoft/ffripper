#!/bin/bash
# ffripper uninstall script

for i in $(find /usr -path "*ffripper*"); do
	rm -rf $i
done
