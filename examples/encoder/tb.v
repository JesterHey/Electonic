`timescale 1ns/1ns

module encoder_tb;

// 测试4-2优先级编码器
reg [3:0] in_4to2;
wire [1:0] out_4to2;
wire valid_4to2;
priority_encoder_4to2 dut1(.in(in_4to2), .out(out_4to2), .valid(valid_4to2));

// 测试参数化编码器（8-3）
reg [7:0] in_param;
wire [2:0] out_param;
wire valid_param;
priority_encoder #(.N(8)) dut2(.in(in_param), .out(out_param), .valid(valid_param));

initial begin
    // 测试优先级编码器
    $display("Testing 4-to-2 Priority Encoder:");
    in_4to2 = 4'b1000; #10;
    $display("Input=%b → Output=%b (Valid=%b)", in_4to2, out_4to2, valid_4to2);
    in_4to2 = 4'b0100; #10;
    $display("Input=%b → Output=%b (Valid=%b)", in_4to2, out_4to2, valid_4to2);
    in_4to2 = 4'b0000; #10;
    $display("Input=%b → Output=%b (Valid=%b)", in_4to2, out_4to2, valid_4to2);

    // 测试参数化编码器
    $display("\nTesting 8-to-3 Priority Encoder:");
    in_param = 8'b00100000; #10;
    $display("Input=%b → Output=%b (Valid=%b)", in_param, out_param, valid_param);
    in_param = 8'b00010000; #10;
    $display("Input=%b → Output=%b (Valid=%b)", in_param, out_param, valid_param);
    in_param = 8'b00000000; #10;
    $display("Input=%b → Output=%b (Valid=%b)", in_param, out_param, valid_param);

    $finish;
end

endmodule