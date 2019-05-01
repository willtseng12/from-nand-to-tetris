// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// Position starts at top left
@SCREEN
D=A

@Position
M=D

(CHECK)
	@KBD
	D=M

	@BLACKEN
	D;JGT

	@WHITEN
	D;JEQ

(WHITEN)
	// check if whitened all
	@Position
	D=M

	@SCREEN
	D=D-A

	@CHECK
	D+1;JEQ

	// get pointer from the position register
	@Position
	A=M
	M=0

	// decrement position
	@Position
	M=M-1

	// check before next iteration
	@CHECK
	0;JEQ

	@WHITEN
	0;JMP



(BLACKEN)
	// check if blackened all
	@Position
	D=M

	@KBD // KBD comes right after the last screen register
	D=A-D

	@CHECK
	D;JEQ

	// get pointer from the position register
	@Position
	A=M
	M=-1

	// increment position
	@Position
	M=M+1

	// check before next iteration
	@CHECK
	0;JEQ

	@BLACKEN
	0;JMP



