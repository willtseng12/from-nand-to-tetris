@0
D=A
@SP
M=M+1
A=M-1
M=D
@0
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
(BasicLoop$LOOP_START)
@0
D=A
@ARG
A=M+D
D=M
@SP
M=M+1
A=M-1
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
@0
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
@0
D=A
@ARG
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
@1
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
D=D-M
@SP
M=M+1
A=M-1
M=D
@0
D=A
@ARG
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
@0
D=A
@ARG
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
@BasicLoop$LOOP_START
D;JNE
@0
D=A
@LCL
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D