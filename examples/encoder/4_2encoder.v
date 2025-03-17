module priority_encoder_4to2 (
    input wire [3:0] in,    // 4位输入（优先级从高到低：in[3] > in[2] > ...）
    output reg [1:0] out,   // 2位二进制输出
    output reg valid        // 有效信号（至少一个输入为1）
);

always @(*) begin
    valid = |in;  // 当输入不全为0时有效
    casex(in)
        4'b1xxx: out = 2'b11;  // 最高优先级
        4'b01xx: out = 2'b10;
        4'b001x: out = 2'b01;
        4'b0001: out = 2'b00;
        default: out = 2'b00;  // 无输入时保持默认
    endcase
end

endmodule