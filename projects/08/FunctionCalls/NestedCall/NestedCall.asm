(Sys.init)
@4000
D=A
@SP
M=M+1
A=M-1
M=D
@R3
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@5000
D=A
@SP
M=M+1
A=M-1
M=D
@R4
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@Sys.mainRET0
D=A
@SP
M=M+1
A=M-1
M=D
@LCL
D=M
@SP
M=M+1
A=M-1
M=D
@ARG
D=M
@SP
M=M+1
A=M-1
M=D
@THIS
D=M
@SP
M=M+1
A=M-1
M=D
@THAT
D=M
@SP
M=M+1
A=M-1
M=D
@5
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.main
0;JMP
(Sys.mainRET0)
@R6
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
(NestedCall$LOOP)
@NestedCall$LOOP
0;JMP
(Sys.main)
D=0
@SP
M=M+1
A=M-1
M=D
D=0
@SP
M=M+1
A=M-1
M=D
D=0
@SP
M=M+1
A=M-1
M=D
D=0
@SP
M=M+1
A=M-1
M=D
D=0
@SP
M=M+1
A=M-1
M=D
@4001
D=A
@SP
M=M+1
A=M-1
M=D
@R3
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@5001
D=A
@SP
M=M+1
A=M-1
M=D
@R4
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@200
D=A
@SP
M=M+1
A=M-1
M=D
@1
D=A
@LCL
A=M+D
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@40
D=A
@SP
M=M+1
A=M-1
M=D
@2
D=A
@LCL
A=M+D
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@6
D=A
@SP
M=M+1
A=M-1
M=D
@3
D=A
@LCL
A=M+D
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@123
D=A
@SP
M=M+1
A=M-1
M=D
@Sys.add12RET1
D=A
@SP
M=M+1
A=M-1
M=D
@LCL
D=M
@SP
M=M+1
A=M-1
M=D
@ARG
D=M
@SP
M=M+1
A=M-1
M=D
@THIS
D=M
@SP
M=M+1
A=M-1
M=D
@THAT
D=M
@SP
M=M+1
A=M-1
M=D
@6
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.add12
0;JMP
(Sys.add12RET1)
@R5
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@0
D=A
@LCL
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
@1
D=A
@LCL
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
@2
D=A
@LCL
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
@3
D=A
@LCL
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
@4
D=A
@LCL
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
@SP
M=M-1
A=M
D=M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
D=D+M
@SP
M=M+1
A=M-1
M=D
@SP
M=M-1
A=M
D=M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
D=D+M
@SP
M=M+1
A=M-1
M=D
@SP
M=M-1
A=M
D=M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
D=D+M
@SP
M=M+1
A=M-1
M=D
@SP
M=M-1
A=M
D=M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
D=D+M
@SP
M=M+1
A=M-1
M=D
@LCL
D=M
@R13
M=D
@5
D=A
@R13
A=M-D
D=M
@R14
M=D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M
@SP
M=D+1
@1
D=A
@R13
A=M-D
D=M
@THAT
M=D
@2
D=A
@R13
A=M-D
D=M
@THIS
M=D
@3
D=A
@R13
A=M-D
D=M
@ARG
M=D
@4
D=A
@R13
A=M-D
D=M
@LCL
M=D
@R14
A=M
0;JMP
(Sys.add12)
@4002
D=A
@SP
M=M+1
A=M-1
M=D
@R3
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@5002
D=A
@SP
M=M+1
A=M-1
M=D
@R4
D=A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
@0
D=A
@ARG
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
@12
D=A
@SP
M=M+1
A=M-1
M=D
@SP
M=M-1
A=M
D=M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
D=D+M
@SP
M=M+1
A=M-1
M=D
@LCL
D=M
@R13
M=D
@5
D=A
@R13
A=M-D
D=M
@R14
M=D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M
@SP
M=D+1
@1
D=A
@R13
A=M-D
D=M
@THAT
M=D
@2
D=A
@R13
A=M-D
D=M
@THIS
M=D
@3
D=A
@R13
A=M-D
D=M
@ARG
M=D
@4
D=A
@R13
A=M-D
D=M
@LCL
M=D
@R14
A=M
0;JMP
