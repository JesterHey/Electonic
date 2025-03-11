module mux #(
    parameter WIDTH = 8,    // 数据位宽
    parameter SEL_BITS = 3  // 选择信号位数（2^SEL_BITS >= WIDTH）
)(
    input wire [SEL_BITS-1:0] sel,
    input wire [WIDTH-1:0] data_in,
    output reg out
);

always @(*) begin
    out = data_in[sel];  // 直接索引选择
end

endmodule