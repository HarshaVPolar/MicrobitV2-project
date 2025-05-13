.syntax unified
.global main
.type main, %function

// setup for LED matrix
.equ GPIO_PORT0_BASE,      0x50000000
.equ GPIO_PORT1_BASE,      0x50000300
.equ P0_OUT_OFFSET,        0x504
.equ P0_OUTSET_OFFSET,     0x508
.equ P0_OUTCLR_OFFSET,     0x50C
.equ P0_IN_OFFSET,         0x510
.equ P0_DIR_OFFSET,        0x514
.equ P0_DIRSET_OFFSET,     0x518
.equ P0_PINCNF_OFFSET,     0x700

.equ COL1_PIN, 28
.equ COL2_PIN, 11
.equ COL3_PIN, 31
.equ COL4_PIN, 5
.equ COL5_PIN, 30

// Pins for matrix

.equ ROW1_PIN, 21
.equ ROW2_PIN, 22
.equ ROW3_PIN, 15
.equ ROW4_PIN, 24
.equ ROW5_PIN, 19

.equ BUTTON_A_PIN, 14
.equ BUTTON_B_PIN, 23

.equ MAshape2S, 3

main:
    push {r4, r5, r6, r7, lr}
    
    // start device
    bl setup_gpio
    
    mov r4, #0
    
main_loop:
    // check button
    bl is_button_a_pressed
    cmp r0, #1
    bne continue_current_pattern
    
    add r4, r4, #1
    cmp r4, #MAshape2S
    blt continue_pattern_switch
    mov r4, #0

continue_pattern_switch:
    bl wait_for_button_release
    
continue_current_pattern:
    cmp r4, #0
    beq display_pattern0
    cmp r4, #1
    beq display_pattern1
    cmp r4, #2
    beq display_pattern2
    
    mov r4, #0
    
display_pattern0:
    bl shape1
    b main_loop
    
display_pattern1:
    bl shape2
    b main_loop
    
display_pattern2:
    bl shape3
    b main_loop

.size main, .-main

setup_gpio:
    push {r4, r5, lr}
    
    // setting pins as output
    ldr r4, =GPIO_PORT0_BASE
    
    mov r0, #1
    lsl r0, r0, #ROW1_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW2_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW3_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW4_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW5_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL1_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL5_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    ldr r4, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r4, #P0_DIRSET_OFFSET]
    
    ldr r4, =GPIO_PORT0_BASE
    mov r0, #BUTTON_A_PIN
    lsl r0, r0, #2
    add r0, r0, #P0_PINCNF_OFFSET
    mov r1, #0xC
    str r1, [r4, r0]
    
    mov r0, #BUTTON_B_PIN
    lsl r0, r0, #2
    add r0, r0, #P0_PINCNF_OFFSET
    mov r1, #0xC
    str r1, [r4, r0]
    
    bl clear_all_pixels
    pop {r4, r5, pc}

is_button_a_pressed:
    //  checking button
    ldr r1, =GPIO_PORT0_BASE
    ldr r1, [r1, #P0_IN_OFFSET]
    mov r2, #1
    lsl r2, r2, #BUTTON_A_PIN
    tst r1, r2
    mov r0, #0
    it eq
    moveq r0, #1
    bx lr

wait_for_button_release:
    push {r4, lr}
    

    ldr r4, =100000
debounce_delay:
    subs r4, r4, #1
    bne debounce_delay
    
button_check_loop:
    bl is_button_a_pressed
    cmp r0, #1
    beq button_check_loop
    
    ldr r4, =100000
release_delay:
    subs r4, r4, #1
    bne release_delay
    
    pop {r4, pc}

shape1:
    push {r4, r5, r6, r7, lr}
    
    bl clear_all_pixels
    
    ldr r4, =GPIO_PORT0_BASE
    
    mov r0, #1
    lsl r0, r0, #ROW1_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    ldr r5, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r5, #P0_OUTSET_OFFSET]
    
    ldr r4, =GPIO_PORT0_BASE
    mov r0, #1
    lsl r0, r0, #ROW2_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL1_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    ldr r5, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r5, #P0_OUTSET_OFFSET]
    
    ldr r4, =GPIO_PORT0_BASE
    mov r0, #1
    lsl r0, r0, #COL5_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW3_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL1_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    ldr r5, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r5, #P0_OUTSET_OFFSET]
    
    ldr r4, =GPIO_PORT0_BASE
    mov r0, #1
    lsl r0, r0, #COL5_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW4_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    ldr r5, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r5, #P0_OUTSET_OFFSET]
    
    ldr r4, =GPIO_PORT0_BASE
    mov r0, #1
    lsl r0, r0, #ROW5_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    bl medium_delay
    
    pop {r4, r5, r6, r7, pc}

shape2:
    push {r4, r5, r6, r7, lr}
    
    // X pattern anim
    bl clear_all_pixels
    bl display_diagonal_1
    bl medium_delay
    
    bl clear_all_pixels
    bl display_diagonal_2
    bl medium_delay
    
    bl clear_all_pixels
    bl display_diagonal_1
    bl display_diagonal_2
    bl medium_delay
    
    bl clear_all_pixels
    bl medium_delay
    
    pop {r4, r5, r6, r7, pc}

display_diagonal_1:
    push {r4, r5, lr}
    ldr r4, =GPIO_PORT0_BASE
    
    mov r0, #1
    lsl r0, r0, #ROW1_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL1_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW2_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW3_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW4_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    ldr r5, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r5, #P0_OUTSET_OFFSET]
    
    ldr r4, =GPIO_PORT0_BASE
    mov r0, #1
    lsl r0, r0, #ROW5_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL5_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    pop {r4, r5, pc}

display_diagonal_2:
    push {r4, r5, lr}
    ldr r4, =GPIO_PORT0_BASE
    
    mov r0, #1
    lsl r0, r0, #ROW1_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL5_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW2_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    ldr r5, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r5, #P0_OUTSET_OFFSET]
    
    ldr r4, =GPIO_PORT0_BASE
    mov r0, #1
    lsl r0, r0, #ROW3_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW4_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW5_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL1_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    pop {r4, r5, pc}

shape3:
    push {r4, r5, r6, r7, lr}
    
    bl clear_all_pixels
    bl pos1
    bl short_delay
    
    bl clear_all_pixels
    bl pos2
    bl short_delay
    
    bl clear_all_pixels
    bl pos3
    bl short_delay
    
    pop {r4, r5, r6, r7, pc}

pos1:
    push {r4, r5, lr}
    ldr r4, =GPIO_PORT0_BASE
    
    mov r0, #1
    lsl r0, r0, #ROW3_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL1_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    pop {r4, r5, pc}

pos2:
    push {r4, r5, lr}
    ldr r4, =GPIO_PORT0_BASE
    
    mov r0, #1
    lsl r0, r0, #ROW3_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    ldr r5, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r5, #P0_OUTSET_OFFSET]
    
    pop {r4, r5, pc}

pos3:
    push {r4, r5, lr}
    ldr r4, =GPIO_PORT0_BASE
    
    mov r0, #1
    lsl r0, r0, #ROW3_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    ldr r5, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r5, #P0_OUTSET_OFFSET]
    
    ldr r4, =GPIO_PORT0_BASE
    mov r0, #1
    lsl r0, r0, #COL5_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    pop {r4, r5, pc}

medium_delay:
    push {r4, lr}
    ldr r4, =400000
    bl delay_loop
    pop {r4, pc}

short_delay:
    push {r4, lr}
    ldr r4, =200000
    bl delay_loop
    pop {r4, pc}

delay_loop:
    subs r4, r4, #1
    bne delay_loop
    bx lr

clear_all_pixels:
    push {r4, r5, lr}
    
    // offing leds by keeping high and lows of cols and rows
    ldr r4, =GPIO_PORT0_BASE
    
    mov r0, #1
    lsl r0, r0, #ROW1_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW2_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW3_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW4_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #ROW5_PIN
    str r0, [r4, #P0_OUTSET_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL1_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL2_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL3_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    mov r0, #1
    lsl r0, r0, #COL5_PIN
    str r0, [r4, #P0_OUTCLR_OFFSET]
    
    ldr r5, =GPIO_PORT1_BASE
    mov r0, #1
    lsl r0, r0, #COL4_PIN
    str r0, [r5, #P0_OUTCLR_OFFSET]
    
    pop {r4, r5, pc}
