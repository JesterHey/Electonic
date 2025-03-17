module full_adder (
    input  A,    // 输入位 A
    input  B,    // 输入位 B
    input  Cin,  // 进位输入
    output S,    // 和输出
    output Cout  // 进位输出
);
    // 计算和：A、B、Cin 的异或
    assign S = A ^ B ^ Cin;
    
    // 计算进位：当至少两个输入为1时，进位为1
    assign Cout = (A & B) | (B & Cin) | (A & Cin);
endmodule