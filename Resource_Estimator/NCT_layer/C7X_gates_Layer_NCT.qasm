OPENQASM 2.0;
include "qelib1.inc";
qreg q[9];

//--------------- Layer: 1, Toffoli-Layer: 1 ---------------//
ccx q[3],q[5],q[8];

//--------------- Layer: 2, Toffoli-Layer: 2 ---------------//
ccx q[4],q[2],q[5];

//--------------- Layer: 3, Toffoli-Layer: 3 ---------------//
ccx q[0],q[1],q[4];

//--------------- Layer: 4, Toffoli-Layer: 4 ---------------//
ccx q[4],q[2],q[5];

//--------------- Layer: 5, Toffoli-Layer: 5 ---------------//
ccx q[3],q[5],q[8];

//--------------- Layer: 6, Toffoli-Layer: 6 ---------------//
ccx q[4],q[2],q[5];
ccx q[6],q[3],q[7];

//--------------- Layer: 7, Toffoli-Layer: 7 ---------------//
ccx q[0],q[1],q[4];

//--------------- Layer: 8, Toffoli-Layer: 8 ---------------//
ccx q[4],q[2],q[5];

//--------------- Layer: 9, Toffoli-Layer: 9 ---------------//
ccx q[2],q[5],q[3];

//--------------- Layer: 10, Toffoli-Layer: 10 ---------------//
ccx q[8],q[4],q[2];

//--------------- Layer: 11, Toffoli-Layer: 11 ---------------//
ccx q[2],q[5],q[3];

//--------------- Layer: 12, Toffoli-Layer: 12 ---------------//
ccx q[6],q[3],q[7];

//--------------- Layer: 13, Toffoli-Layer: 13 ---------------//
ccx q[2],q[5],q[3];

//--------------- Layer: 14, Toffoli-Layer: 14 ---------------//
ccx q[8],q[4],q[2];

//--------------- Layer: 15, Toffoli-Layer: 15 ---------------//
ccx q[2],q[5],q[3];

//--------------- Layer: 16, Toffoli-Layer: 16 ---------------//
ccx q[3],q[5],q[8];

//--------------- Layer: 17, Toffoli-Layer: 17 ---------------//
ccx q[4],q[2],q[5];

//--------------- Layer: 18, Toffoli-Layer: 18 ---------------//
ccx q[0],q[1],q[4];

//--------------- Layer: 19, Toffoli-Layer: 19 ---------------//
ccx q[4],q[2],q[5];

//--------------- Layer: 20, Toffoli-Layer: 20 ---------------//
ccx q[3],q[5],q[8];

//--------------- Layer: 21, Toffoli-Layer: 21 ---------------//
ccx q[4],q[2],q[5];

//--------------- Layer: 22, Toffoli-Layer: 22 ---------------//
ccx q[0],q[1],q[4];

//--------------- Layer: 23, Toffoli-Layer: 23 ---------------//
ccx q[4],q[2],q[5];