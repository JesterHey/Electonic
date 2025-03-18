`timescale 1ns/1ns

module decoder_tb;

// 测试2-4译码器
reg [1:0] in_2to4;
reg en_2to4;
wire [3:0] out_2to4;
decoder_2to4 dut1(.in(in_2to4), .en(en_2to4), .out(out_2to4));

// 测试参数化译码器（3-8）
reg [2:0] in_param;
reg en_param;
wire [7:0] out_param;
decoder #(.N(3)) dut2(.in(in_param), .en(en_param), .out(out_param));

initial begin
    // 测试2-4译码器
    $display("Testing 2-to-4 decoder:");
    en_2to4 = 1;
    for (int i=0; i<4; i++) begin
        in_2to4 = i;
        #10;
        $display("Input=%b, Output=%b", in_2to4, out_2to4);
    end
    en_2to4 = 0;
    #10;
    $display("Disable test: Output=%b", out_2to4);

    // 测试3-8参数化译码器
    $display("\nTesting parameterized 3-to-8 decoder:");
    en_param = 1;
    for (int j=0; j<8; j++) begin
        in_param = j;
        #10;
        $display("Input=%b, Output=%b", in_param, out_param);
    end

    $finish;
end

endmodule