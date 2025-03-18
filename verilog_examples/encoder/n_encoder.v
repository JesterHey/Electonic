module priority_encoder #(
    parameter N = 8          // 输入位数（输出位数=log2(N)向上取整）
)(
    input wire [N-1:0] in,
    output reg [$clog2(N)-1:0] out,
    output reg valid
);

always @(*) begin
    valid = |in;
    out = 0;
    for (int i = N-1; i >= 0; i--) begin
        if (in[i]) begin
            out = i;
            break;
        end
    end
end

endmodule