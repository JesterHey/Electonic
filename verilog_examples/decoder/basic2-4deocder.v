module decoder_2to4 (
    input wire [1:0] in,    // 2位输入
    input wire       en,     // 使能信号
    output reg [3:0] out     // 4位输出
);

always @(*) begin
    if (!en) begin
        out = 4'b0000;      // 使能无效时输出全0
    end else begin
        case(in)
            2'b00: out = 4'b0001;
            2'b01: out = 4'b0010;
            2'b10: out = 4'b0100;
            2'b11: out = 4'b1000;
            default: out = 4'b0000; // 避免锁存器
        endcase
    end
end

endmodule