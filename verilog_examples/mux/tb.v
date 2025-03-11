`timescale 1ns/1ns

module mux_tb;

// 测试4选1 MUX
reg [1:0] sel_4to1;
reg [3:0] data_4to1;
wire out_4to1;
mux_4to1 dut1(.sel(sel_4to1), .data_in(data_4to1), .out(out_4to1));

// 测试参数化MUX（8选1）
reg [2:0] sel_param;
reg [7:0] data_param;
wire out_param;
mux #(.WIDTH(8), .SEL_BITS(3)) dut2(.sel(sel_param), .data_in(data_param), .out(out_param));

initial begin
    // 测试4选1 MUX
    $display("Testing 4-to-1 MUX:");
    data_4to1 = 4'b1010;
    for (int i=0; i<4; i++) begin
        sel_4to1 = i;
        #10;
        $display("sel=%b → out=%b", sel_4to1, out_4to1);
    end

    // 测试参数化MUX
    $display("\nTesting 8-to-1 parameterized MUX:");
    data_param = 8'b10000000;
    sel_param = 3'b111; #10;  // 选择最高位
    $display("sel=%b → out=%b", sel_param, out_param);
    
    data_param = 8'b00000001;
    sel_param = 3'b000; #10;  // 选择最低位
    $display("sel=%b → out=%b", sel_param, out_param);

    $finish;
end

endmodule