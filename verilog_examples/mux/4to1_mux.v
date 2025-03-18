module mux_4to1 (
    input wire [1:0] sel, // 2位选择信号
    input wire [3:0] data_in,
    output reg out
);

always @(*) begin
    case(sel)
        2'b00: out = data_in[0];
        2'b01: out = data_in[1];
        2'b10: out = data_in[2];
        2'b11: out = data_in[3];
        default: out = 1'b0; // 避免锁存器
    endcase
end

endmodule