# Utility Scripts

This folder has as set of utility scripts to use in the development.

## GDS XOR
To run XOR on 2 different layouts and see if there are any differences. The above script will exit 1 if there any differences.

- To test the script on similar layouts run this:
```bash
klayout -b -r xor.drc -rd gds1=a.gds -rd gds2=b.gds -rd report=xor_report.lyrdb
```

- To test the script on different layouts run this:
```bash
klayout -b -r xor.drc -rd gds1=a.gds -rd gds2=c.gds -rd report=xor_report.lyrdb
```

