module m1 (
    input wire A,
    input wire B,
    output wire S1,
    output wire S2
);
    assign S1 = A & B;  // 非线性运算（逻辑与）
    assign S2 = (A + B) + A;  // 线性运算（加法）
endmodule