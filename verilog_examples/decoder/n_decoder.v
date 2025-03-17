module decoder #(
    parameter N = 3          // 输入位数（默认3-8译码器）
)(
    input wire [N-1:0] in,
    input wire         en,
    output reg [(1<<N)-1:0] out // 输出位数=2^N
);

always @(*) begin
    if (!en) begin
        out = 0;
    end else begin
        out = 1 << in;      // 位移实现独热码输出
    end
end

endmodule