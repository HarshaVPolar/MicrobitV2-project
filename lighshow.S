.syntax unified
.global main
.type main, %function

.equ GPIO_PORT0_BASE,      0x50000000
.equ GPIO_PORT1_BASE,      0x50000300
.equ P0_OUT_OFFSET,        0x504
.equ P0_OUTSET_OFFSET,     0x508
.equ P0_OUTCLR_OFFSET,     0x50C
.equ P0_IN_OFFSET,         0x510
.equ P0_DIR_OFFSET,        0x514
.equ P0_DIRSET_OFFSET,     0x518
.equ P0_PINCNF_OFFSET,     0x700

.equ COL1_PIN, 28  // P0.28
.equ COL2_PIN, 11  // P0.11
.equ COL3_PIN, 31  // P0.31
.equ COL4_PIN, 5   // Port 1, pin 5
.equ COL5_PIN, 30  // P0.30

.equ ROW1_PIN, 21  // P0.21
.equ ROW2_PIN, 22  // P0.22
.equ ROW3_PIN, 15  // P0.15
.equ ROW4_PIN, 24  // P0.24
.equ ROW5_PIN, 19  // P0.19

.equ BUTTON_A_PIN, 14 // P0.14

main:
    bl setup_gpio

main_loop:
    bl is_button_a_pressed
    cmp r0, #1
    beq button_pressed_mode
    
    bl sequence_1_b
    b main_loop

button_pressed_mode:
    bl sequence_2
    
    bl is_button_a_pressed
    cmp r0, #1
    beq button_pressed_mode
    
    bl clear_bit
    b main_loop

.size main, .-main

setup_gpio:
    push {lr}

    ldr r4, =GPIO_PORT0_BASE
    
    // Row 1
    mov r0, #1
    lsl r0, r0, #ROW1_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    // Row 2
    mov r0, #1
    lsl r0, r0, #ROW2_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    // Row 3
    mov r0, #1
    lsl r0, r0, #ROW3_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    // Row 4
    mov r0, #1
    lsl r0, r0, #ROW4_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    // Row 5
    mov r0, #1
    lsl r0, r0, #ROW5_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    // Col 1
    mov r0, #1
    lsl r0, r0, #COL1_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    // Col 2
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    // Col 3
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    // Col 5
    mov r0, #1
    lsl r0, r0, #COL5_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    ldr r4, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    // Configure Button A as input with pull-up
    ldr r4, =GPIO_PORT0_BASE
    mov r0, #BUTTON_A_PIN
    lsl r0, r0, #2
    add r0, r0, #P0_PINCNF_OFFSET
    mov r1, #0xC // Input, Pull-up
    str r1, [r4, r0]
    
    bl clear_bit
    pop {pc}

is_button_a_pressed:
    push {r1-r2}
    ldr r1, =GPIO_PORT0_BASE
    ldr r1, [r1, #P0_IN_OFFSET]
    mov r2, #1
    lsl r2, r2, #BUTTON_A_PIN
    tst r1, r2
    mov r0, #0
    it eq
    moveq r0, #1
    pop {r1-r2}
    bx lr

sequence_1_b: // Full Board Slow Animation 2 triangle pattern 
    push {lr}

    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_1
    pop {lr}
    bx lr

continue_seq1_1:
    bl timer
    bl shape_1_col_5
    bl timer
    bl clear_bit
    
    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_2
    pop {lr}
    bx lr

continue_seq1_2:
    bl shape_1_col_4
    bl timer
    bl clear_bit
    
    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_3
    pop {lr}
    bx lr

continue_seq1_3:  
    bl shape_1_col_3
    bl timer
    bl clear_bit
    
    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_4
    pop {lr}
    bx lr

continue_seq1_4:
    bl shape_1_col_2
    bl timer
    bl clear_bit
    
    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_5
    pop {lr}
    bx lr

continue_seq1_5:
    bl shape_1_col_1
    bl timer
    bl clear_bit

    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_6
    pop {lr}
    bx lr

continue_seq1_6:
    bl timer
    bl shape_1_col_1
    bl timer
    bl clear_bit
    
    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_7
    pop {lr}
    bx lr

continue_seq1_7:
    bl shape_1_col_2
    bl timer
    bl clear_bit
   
    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_8
    pop {lr}
    bx lr

continue_seq1_8:  
    bl shape_1_col_3
    bl timer
    bl clear_bit
    
    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_9
    pop {lr}
    bx lr

continue_seq1_9:
    bl shape_1_col_4
    bl timer
    bl clear_bit
    
    bl is_button_a_pressed
    cmp r0, #1
    bne continue_seq1_10
    pop {lr}
    bx lr

continue_seq1_10:
    bl shape_1_col_5
    bl timer
    bl clear_bit

    pop {lr}
    bx lr

sequence_2:
    push {lr}

    bl is_button_a_pressed
    cmp r0, #0    
    beq button_released_during_seq2
    bl timer
    bl shape_2_col_1
    
    bl is_button_a_pressed
    cmp r0, #0    
    beq button_released_during_seq2
    bl timer
    bl shape_2_col_2
    
    bl is_button_a_pressed
    cmp r0, #0   
    beq button_released_during_seq2
    bl timer
    bl shape_2_col_3
    
    bl is_button_a_pressed
    cmp r0, #0   
    beq button_released_during_seq2
    bl timer
    bl shape_2_col_4
    
    
    bl is_button_a_pressed
    cmp r0, #0    
    beq button_released_during_seq2
    bl timer
    bl shape_2_col_5
    
    
    bl is_button_a_pressed
    cmp r0, #0   
    beq button_released_during_seq2
    bl timer
    bl clear_bit

    
    bl is_button_a_pressed
    cmp r0, #0  
    beq button_released_during_seq2
    bl timer 
    bl shape_3_col_5
    
    
    bl is_button_a_pressed
    cmp r0, #0    
    beq button_released_during_seq2
    bl timer
    bl shape_3_col_4
    
    bl is_button_a_pressed
    cmp r0, #0   
    beq button_released_during_seq2
    bl timer
    bl shape_3_col_3
    
    bl is_button_a_pressed
    cmp r0, #0  
    beq button_released_during_seq2
    bl timer
    bl shape_3_col_2
    
    bl is_button_a_pressed
    cmp r0, #0    
    beq button_released_during_seq2
    bl timer
    bl shape_3_col_1
    
    bl is_button_a_pressed
    cmp r0, #0 
    beq button_released_during_seq2
    bl timer
    bl clear_bit
    
    pop {lr}
    bx lr

button_released_during_seq2:
    bl clear_bit
    pop {lr}
    bx lr

    push {lr}
    ldr r9, =400000 
    bl delay_loop
    pop {lr}
    bx lr

// Delay loop
delay_loop:
    sub r9, r9, #1
    cmp r9, #0
    bne delay_loop
    bx lr

// Shape 1 Column 1 (Col1 / Row 1,2,3,4,5)
shape_1_col_1:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 28
    bl set_bit
    mov r1, 21
    bl set_bit
    mov r1, 22
    bl set_bit
    mov r1, 15
    bl set_bit
    mov r1, 24
    bl set_bit
    mov r1, 19
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 21
    bl set_bit
    mov r1, 22
    bl set_bit
    mov r1, 15
    bl set_bit
    mov r1, 24
    bl set_bit
    mov r1, 19
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 1 Column 2 (Col2 / Row 2,3,4)
shape_1_col_2:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 11
    bl set_bit 
    mov r1, 22
    bl set_bit
    mov r1, 15
    bl set_bit
    mov r1, 24
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 22
    bl set_bit
    mov r1, 15
    bl set_bit
    mov r1, 24
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 1 Column 3 (Col3 / Row 3)
shape_1_col_3:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 31
    bl set_bit 
    mov r1, 15
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 15
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 1 Column 4 (Col4 / Row 2,3,4)
shape_1_col_4:
    push {lr}
    ldr r4, = 0x50000300 @ 0x50000300 DIR 5
    mov r0, 0x514
    mov r1, 5
    bl set_bit
    
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 22
    bl set_bit
    mov r1, 15
    bl set_bit
    mov r1, 24
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 22
    bl set_bit
    mov r1, 15
    bl set_bit
    mov r1, 24
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 1 Column 5 (Col5 / Row 1,2,3,4,5)
shape_1_col_5:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 30
    bl set_bit 
    mov r1, 21
    bl set_bit
    mov r1, 22
    bl set_bit
    mov r1, 15
    bl set_bit
    mov r1, 24
    bl set_bit
    mov r1, 19
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 21
    bl set_bit
    mov r1, 22
    bl set_bit
    mov r1, 15
    bl set_bit
    mov r1, 24
    bl set_bit
    mov r1, 19
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 2 Column 1 (Col1 / Row 1,5)
shape_2_col_1:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 28
    bl set_bit 
    mov r1, 21
    bl set_bit
    mov r1, 19
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 21
    bl set_bit
    mov r1, 19
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 2 Column 2 (Col2 / Row 2,4)
shape_2_col_2:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 11
    bl set_bit 
    mov r1, 22
    bl set_bit
    mov r1, 24
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 22
    bl set_bit
    mov r1, 24
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 2 Column 3 (Col3 / Row 3)
shape_2_col_3:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 31
    bl set_bit 
    mov r1, 15
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 15
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 2 Column 4 (Col4 / Row 2,4)
shape_2_col_4:
    push {lr}
    ldr r4, = 0x50000300 @ 0x50000300 DIR 5
    mov r0, 0x514
    mov r1, 5
    bl set_bit
    
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 11
    bl set_bit 
    mov r1, 22
    bl set_bit
    mov r1, 24
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 22
    bl set_bit
    mov r1, 24
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 2 Column 5 (Col5 / Row 1,5)
shape_2_col_5:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 30
    bl set_bit 
    mov r1, 21
    bl set_bit
    mov r1, 19
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 21
    bl set_bit
    mov r1, 19
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 3 Column 1 (Col1 / Row 1,5)
shape_3_col_1:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 28
    bl set_bit 
    mov r1, 21
    bl set_bit
    mov r1, 19
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 21
    bl set_bit
    mov r1, 19
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 3 Column 2 (Col2 / Row 2,4)
shape_3_col_2:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 11
    bl set_bit 
    mov r1, 22
    bl set_bit
    mov r1, 24
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 22
    bl set_bit
    mov r1, 24
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 3 Column 3 (Col3 / Row 3)
shape_3_col_3:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 31
    bl set_bit 
    mov r1, 15
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 15
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 3 Column 4 (Col4 / Row 2,4)
shape_3_col_4:
    push {lr}
    ldr r4, = 0x50000300 @ 0x50000300 DIR 5
    mov r0, 0x514
    mov r1, 05
    bl set_bit
    
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 22
    bl set_bit
    mov r1, 24
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 22
    bl set_bit
    mov r1, 24
    bl set_bit
    
    pop {lr}
    bx lr

// Shape 3 Column 5 (Col5 / Row 1,5)
shape_3_col_5:
    push {lr}
    ldr r4, = 0x50000000
    mov r0, 0x514 @ 0x50000000 DIR ->
    mov r1, 30
    bl set_bit 
    mov r1, 21
    bl set_bit
    mov r1, 19
    bl set_bit
    
    mov r0, 0x504 @ 0x50000000 OUT -> 
    mov r1, 21
    bl set_bit
    mov r1, 19
    bl set_bit
    
    pop {lr}
    bx lr

set_bit:
    // r4: base address of pin
    // r0: offset of address
    // r1: the pin to set to high
    push {lr}
    ldr r3, [r4, r0]
    mov r5, 0b1
    lsl r5, r5, r1
    orr r3, r3, r5
    str r3, [r4, r0]
    pop {lr}
    bx lr

clear_bit:
    // Clears entire board by pushing 0 into registers
    push {lr}
    mov r10, 0
    ldr r4, =GPIO_PORT0_BASE
    str r10, [r4, P0_DIR_OFFSET]
    str r10, [r4, P0_OUT_OFFSET]
    ldr r4, =GPIO_PORT1_BASE
    str r10, [r4, P0_DIR_OFFSET]
    str r10, [r4, P0_OUT_OFFSET]
    pop {lr}
    bx lr
